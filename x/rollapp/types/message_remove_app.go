package types

import (
	"errors"

	errorsmod "cosmossdk.io/errors"
	sdk "github.com/cosmos/cosmos-sdk/types"
	"github.com/cosmos/cosmos-sdk/x/auth/migrations/legacytx"
)

const TypeMsgRemoveApp = "remove_app"

var (
	_ sdk.Msg            = &MsgRemoveApp{}
	_ legacytx.LegacyMsg = &MsgRemoveApp{}
)

func NewMsgRemoveApp(creator string, id uint64, rollappId string) *MsgRemoveApp {
	return &MsgRemoveApp{
		Creator:   creator,
		Id:        id,
		RollappId: rollappId,
	}
}

func (msg *MsgRemoveApp) Route() string {
	return RouterKey
}

func (msg *MsgRemoveApp) Type() string {
	return TypeMsgRemoveApp
}

func (msg *MsgRemoveApp) GetSigners() []sdk.AccAddress {
	creator, err := sdk.AccAddressFromBech32(msg.Creator)
	if err != nil {
		panic(err)
	}
	return []sdk.AccAddress{creator}
}

func (msg *MsgRemoveApp) GetSignBytes() []byte {
	bz := ModuleCdc.MustMarshalJSON(msg)
	return sdk.MustSortJSON(bz)
}

func (msg *MsgRemoveApp) GetApp() App {
	return NewApp(
		msg.Id,
		"",
		msg.RollappId,
		"",
		"",
		"",
		0,
	)
}

func (msg *MsgRemoveApp) ValidateBasic() error {
	_, err := sdk.AccAddressFromBech32(msg.Creator)
	if err != nil {
		return errors.Join(ErrInvalidCreatorAddress, err)
	}

	if msg.Id == 0 {
		return errorsmod.Wrap(ErrInvalidAppID, "App id cannot be zero")
	}

	if len(msg.RollappId) == 0 {
		return errorsmod.Wrap(ErrInvalidRollappID, "RollappId cannot be empty")
	}

	return nil
}