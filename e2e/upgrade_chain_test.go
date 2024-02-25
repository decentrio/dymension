package e2e

import (
	"context"
	"crypto/sha256"
	"fmt"
	"os"
	"path"
	"path/filepath"
	"testing"
	"time"

	test "github.com/decentrio/rollup-e2e-testing"
	"github.com/decentrio/rollup-e2e-testing/cosmos"
	"github.com/decentrio/rollup-e2e-testing/ibc"
	"github.com/decentrio/rollup-e2e-testing/testutil"

	"github.com/stretchr/testify/require"
	"go.uber.org/zap/zaptest"
)

const (
	haltHeightDelta    = uint64(20)
	blocksAfterUpgrade = uint64(10)
	votingPeriod       = "30s"
	maxDepositPeriod   = "10s"
)

func TestDymensionHubChainUpgrade(t *testing.T) {
	if testing.Short() {
		t.Skip()
	}

	ctx := context.Background()
	// Create chain factory with dymension
	numHubVals := 3
	numHubFullNodes := 3

	dymensionConfig.ModifyGenesis = modifyGenesisShortProposals(votingPeriod, maxDepositPeriod)
	dymensionConfig.Images = []ibc.DockerImage{prevVersionDymensionImage}
	cf := cosmos.NewBuiltinChainFactory(zaptest.NewLogger(t), []*cosmos.ChainSpec{
		{
			Name:          "dymension-hub",
			ChainConfig:   dymensionConfig,
			NumValidators: &numHubVals,
			NumFullNodes:  &numHubFullNodes,
		},
	})

	chains, err := cf.Chains(t.Name())
	require.NoError(t, err)

	dymension := chains[0].(*cosmos.CosmosChain)
	ic := test.NewSetup().
		AddChain(dymension)

	client, network := test.DockerSetup(t)

	require.NoError(t, ic.Build(ctx, nil, test.InterchainBuildOptions{
		TestName:         t.Name(),
		Client:           client,
		NetworkID:        network,
		SkipPathCreation: true,
		// BlockDatabaseFile: interchaintest.DefaultBlockDatabaseFilepath(),
	}))
	t.Cleanup(func() {
		_ = ic.Close()
	})

	// Make sure gov params has changed
	dymNode := dymension.FullNodes[0]
	votingParams, err := dymNode.QueryParam(ctx, "gov", "voting_params")
	require.NoError(t, err)
	fmt.Println("gov voting params: ", votingParams.Value)

	// Create some user accounts on both chains
	user := test.GetAndFundTestUsers(t, ctx, t.Name(), walletAmount, dymension)[0]

	// Copy file to node
	fileName := "bytecode/dymd.tar"
	_, file := filepath.Split(fileName)
	err = dymNode.CopyFile(ctx, fileName, file)
	require.NoError(t, err, "err writing binary file to docker volume")

	// Get the file's checksum
	fileContent, err := os.ReadFile(fileName)
	require.NoError(t, err, "err reading binary file")
	sum := sha256.Sum256(fileContent)

	height, err := dymension.Height(ctx)
	require.NoError(t, err, "error fetching height before submit upgrade proposal")

	haltHeight := height + haltHeightDelta

	proposal := cosmos.SoftwareUpgradeProposal{
		Deposit:     "500000000000" + dymension.Config().Denom, // greater than min deposit
		Title:       "Chain Upgrade 1",
		Name:        "v3",
		Description: "First chain software upgrade",
		Height:      haltHeight,
		Info:        fmt.Sprintf("{ \"binaries\": { \"linux/amd64\":\"file://%s?checksum=sha256:%x\" } }", path.Join(dymNode.HomeDir(), file), sum),
	}

	upgradeTx, err := dymension.UpgradeLegacyProposal(ctx, user.KeyName(), proposal)
	require.NoError(t, err, "error submitting software upgrade proposal tx")
	fmt.Println("upgradeTx", upgradeTx)

	err = dymension.VoteOnProposalAllValidators(ctx, upgradeTx.ProposalID, cosmos.ProposalVoteYes)
	require.NoError(t, err, "failed to submit votes")

	_, err = cosmos.PollForProposalStatus(ctx, dymension, height, haltHeight, upgradeTx.ProposalID, cosmos.ProposalStatusPassed)
	prop, _ := dymension.QueryProposal(ctx, upgradeTx.ProposalID)
	fmt.Println("prop: ", prop)
	require.Equal(t, prop.Status, cosmos.ProposalStatusPassed)
	require.NoError(t, err, "proposal status did not change to passed in expected number of blocks")

	timeoutCtx, timeoutCtxCancel := context.WithTimeout(ctx, time.Second*45)
	defer timeoutCtxCancel()

	height, err = dymension.Height(ctx)
	require.NoError(t, err, "error fetching height before upgrade")

	// this should timeout due to chain halt at upgrade height.
	_ = testutil.WaitForBlocks(timeoutCtx, int(haltHeight-height)+1, dymension)

	height, err = dymension.Height(ctx)
	require.NoError(t, err, "error fetching height after chain should have halted")

	// make sure that chain is halted
	require.Equal(t, haltHeight, height, "height is not equal to halt height")

	// bring down nodes to prepare for upgrade
	err = dymension.StopAllNodes(ctx)
	require.NoError(t, err, "error stopping node(s)")

	// upgrade version on all nodes
	dymension.UpgradeVersion(ctx, client, repo, version)

	// start all nodes back up.
	// validators reach consensus on first block after upgrade height
	// and chain block production resumes.
	err = dymension.StartAllNodes(ctx)
	require.NoError(t, err, "error starting upgraded node(s)")

	timeoutCtx, timeoutCtxCancel = context.WithTimeout(ctx, time.Second*45)
	defer timeoutCtxCancel()

	err = testutil.WaitForBlocks(timeoutCtx, int(blocksAfterUpgrade), dymension)
	require.NoError(t, err, "chain did not produce blocks after upgrade")

	height, err = dymension.Height(ctx)
	require.NoError(t, err, "error fetching height after upgrade")

	require.GreaterOrEqual(t, height, haltHeight+blocksAfterUpgrade, "height did not increment enough after upgrade")
}
