#!/bin/bash
set -xeu

MNE1="amused rural desk trick safe whip first menu worth swap enhance punch spin figure elevator abandon camera idea peace nurse coyote adjust modify produce"
MNE2="relax output math high normal adapt include audit spend leader perfect husband nominee service federal neutral occur spider luxury mesh emerge head cabbage abuse"
MNE3="predict alter night ugly venue speed labor exhibit embrace combine acquire ivory canal solar salad mirror invest life chapter decorate manage despair load pear"

mkdir v1 v2 v3
dymd init v1 --chain-id d_3300-1 --home v1
dymd init v2 --chain-id d_3300-1 --home v2
dymd init v3 --chain-id d_3300-1 --home v3

echo $MNE1 | dymd keys add v1 --recover --keyring-backend test --home v1
echo $MNE2 | dymd keys add v2 --recover --keyring-backend test --home v2
echo $MNE3 | dymd keys add v3 --recover --keyring-backend test --home v3


python3 -u transform.py export.json genesis.json v1 v2 v3