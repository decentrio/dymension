package types

// DONTCOVER

import (
	errorsmod "cosmossdk.io/errors"
)

// x/eibc module sentinel errors
var (
	ErrInvalidOrderID                 = errorsmod.Register(ModuleName, 3, "Invalid order ID")
	ErrDemandOrderAlreadyExist        = errorsmod.Register(ModuleName, 4, "Demand order already exists")
	ErrDemandOrderDoesNotExist        = errorsmod.Register(ModuleName, 5, "Demand order does not exist")
	ErrDemandOrderInactive            = errorsmod.Register(ModuleName, 6, "Demand order inactive")
	ErrFulfillerAddressDoesNotExist   = errorsmod.Register(ModuleName, 7, "Fulfiller address does not exist")
	ErrInvalidRecipientAddress        = errorsmod.Register(ModuleName, 8, "Invalid recipient address")
	ErrBlockedAddress                 = errorsmod.Register(ModuleName, 9, "Can't purchase demand order for recipient with blocked address")
	ErrDemandAlreadyFulfilled         = errorsmod.Register(ModuleName, 10, "Demand order already fulfilled")
	ErrFeeTooHigh                     = errorsmod.Register(ModuleName, 11, "Fee must be less than or equal to the total amount")
	ErrExpectedFeeNotMet              = errorsmod.Register(ModuleName, 12, "Expected fee not met")
	ErrNegativeFee                    = errorsmod.Register(ModuleName, 13, "Fee must be greater than or equal to 0")
	ErrMultipleDenoms                 = errorsmod.Register(ModuleName, 15, "Multiple denoms not allowed")
	ErrEmptyPrice                     = errorsmod.Register(ModuleName, 16, "Price must be greater than 0")
	ErrOperatorFeeAccountDoesNotExist = errorsmod.Register(ModuleName, 17, "Operator fee account does not exist")
	ErrLPAccountDoesNotExist          = errorsmod.Register(ModuleName, 18, "LP account does not exist")
	ErrRollappStateInfoNotFound       = errorsmod.Register(ModuleName, 19, "Rollapp state info not found")
	ErrOrderNotSettlementValidated    = errorsmod.Register(ModuleName, 20, "Demand order not settlement validated")
	ErrRollappIdMismatch              = errorsmod.Register(ModuleName, 21, "Rollapp ID mismatch")
	ErrPriceMismatch                  = errorsmod.Register(ModuleName, 22, "Price mismatch")
	ErrInvalidCreationHeight          = errorsmod.Register(ModuleName, 23, "Invalid creation height")
)
