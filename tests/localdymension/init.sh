#!/bin/bash
set -xeu
rm -rf v1
rm -rf v2
rm -rf v3
rm -rf v4

MNE1="amused rural desk trick safe whip first menu worth swap enhance punch spin figure elevator abandon camera idea peace nurse coyote adjust modify produce"
MNE2="relax output math high normal adapt include audit spend leader perfect husband nominee service federal neutral occur spider luxury mesh emerge head cabbage abuse"
MNE3="predict alter night ugly venue speed labor exhibit embrace combine acquire ivory canal solar salad mirror invest life chapter decorate manage despair load pear"
MNE4="rule jealous step victory tiny taste nose list field hawk various copy interest grass maximum puppy airport tree between popular deny cram cover under"

mkdir v1 v2 v3 v4
dymd init v1 --chain-id local_3300-1 --home v1 2> output1
dymd init v2 --chain-id local_3300-1 --home v2 2> output2
dymd init v3 --chain-id local_3300-1 --home v3 2> output3
dymd init v4 --chain-id local_3300-1 --home v4 2> output4

node1=$(cat output1 | jq -r '.node_id')
node2=$(cat output2 | jq -r '.node_id')
node3=$(cat output3 | jq -r '.node_id')
node4=$(cat output4 | jq -r '.node_id')

echo $MNE1 | dymd keys add v1 --recover --keyring-backend test --home v1
echo $MNE2 | dymd keys add v2 --recover --keyring-backend test --home v2
echo $MNE3 | dymd keys add v3 --recover --keyring-backend test --home v3
echo $MNE4 | dymd keys add v4 --recover --keyring-backend test --home v4

python3 -u transform.py export.json genesis.json v1 v2 v3 v4

cp genesis.json v1/config/genesis.json
cp genesis.json v2/config/genesis.json
cp genesis.json v3/config/genesis.json
cp genesis.json v4/config/genesis.json

PEERS="$node1@dymension1:26656,$node2@dymension2:26656,$node3@dymension3:26656,$node4@dymension4:26656"
echo $PEERS
sed -i.bak -e "s/^persistent_peers *=.*/persistent_peers = \"$PEERS\"/" v1/config/config.toml
sed -i.bak -e "s/^persistent_peers *=.*/persistent_peers = \"$PEERS\"/" v2/config/config.toml
sed -i.bak -e "s/^persistent_peers *=.*/persistent_peers = \"$PEERS\"/" v3/config/config.toml
sed -i.bak -e "s/^persistent_peers *=.*/persistent_peers = \"$PEERS\"/" v4/config/config.toml