package types

import (
	sdk "github.com/cosmos/cosmos-sdk/types"
	"github.com/cosmos/cosmos-sdk/x/auth/types"

	rollapptypes "github.com/dymensionxyz/dymension/v3/x/rollapp/types"
)

// RollappKeeper defines the expected rollapp keeper used for retrieve rollapp.
type RollappKeeper interface {
	GetRollapp(ctx sdk.Context, rollappId string) (val rollapptypes.Rollapp, found bool)
	MinBond(ctx sdk.Context, rollappID string) sdk.Coin
	MustGetRollapp(ctx sdk.Context, rollappId string) rollapptypes.Rollapp
	GetAllRollapps(ctx sdk.Context) (list []rollapptypes.Rollapp)
	SetRollappAsLaunched(ctx sdk.Context, rollapp *rollapptypes.Rollapp) error
	HardForkToLatest(ctx sdk.Context, rollappId string) error
	ForkLatestAllowed(ctx sdk.Context, rollappId string) bool
}

// AccountKeeper defines the expected account keeper used for simulations (noalias)
type AccountKeeper interface {
	GetModuleAccount(ctx sdk.Context, moduleName string) types.ModuleAccountI
}

// BankKeeper defines the expected interface needed to retrieve account balances.
type BankKeeper interface {
	SpendableCoins(ctx sdk.Context, addr sdk.AccAddress) sdk.Coins
	SendCoinsFromAccountToModule(ctx sdk.Context, senderAddr sdk.AccAddress, recipientModule string, amt sdk.Coins) error
	SendCoinsFromModuleToAccount(ctx sdk.Context, senderModule string, recipientAddr sdk.AccAddress, amt sdk.Coins) error
	GetAllBalances(ctx sdk.Context, addr sdk.AccAddress) sdk.Coins
	BurnCoins(ctx sdk.Context, name string, amt sdk.Coins) error
}
