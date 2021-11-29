cd IBFT-Network
besu operator generate-blockchain-config --config-file=ibftConfigFile.json --to=networkFiles --private-key-file-name=key
cd networkFiles/keys
find  -type d -printf '%P\n' | grep 0x > ../../validator_node_addresses.txt
cd ../../

while ((i++)); read p; do
  mkdir -p ValNode-$i/data
  cp "networkFiles/keys/$p/key" ValNode-$i/data
done <validator_node_addresses.txt

cd ValNode-1
besu --data-path=data --genesis-file=../networkFiles/genesis.json --rpc-http-enabled --rpc-http-api=ETH,NET,IBFT --host-allowlist="*" --rpc-http-cors-origins="all" >/dev/null &

echo Sleeping 15 seconds
sleep 15

cd ..
echo Getting enode URL
curl -X POST --data '{"jsonrpc":"2.0","method":"net_enode","params":[],"id":1}' http://127.0.0.1:8545 | python3 -c "import sys, json; print(json.load(sys.stdin)['result'])" > boot_enode.txt

kill %1

enode_url=$(<boot_enode.txt)
i=0
while ((i++)); read p; do
    if [[ "$i" == '1' ]]; then
        printf "cd ValNode-$i\nbesu --data-path=data --genesis-file=../networkFiles/genesis.json --min-gas-price=1 --rpc-http-enabled --rpc-http-api=ETH,NET,IBFT --host-allowlist="*" --rpc-http-cors-origins="all"\ncd ..\n" > start_validator_node_$i.sh
    else
        printf "cd ValNode-$i\nbesu --data-path=data --genesis-file=../networkFiles/genesis.json --min-gas-price=1 --bootnodes=$enode_url --p2p-port=$((30302+i)) --rpc-http-enabled --rpc-http-api=ETH,NET,IBFT --host-allowlist="*" --rpc-http-cors-origins="all" --rpc-http-port=$((8544+i))\ncd ..\n" > start_validator_node_$i.sh
    fi
    chmod +x start_validator_node_$i.sh
    echo "Writing script to launch ValNode-$i with JSON-RPC on port $((8544+i)) and p2p on port $((30302+i))"
done <validator_node_addresses.txt

j=0
num_non_validator_nodes=2
while [ $j -lt $num_non_validator_nodes ]; do
    i=$[$j+1]
    printf "cd RNode-$i\nbesu --data-path=data --genesis-file=../networkFiles/genesis.json --min-gas-price=1 --bootnodes=$enode_url --p2p-port=$((30306+i)) --rpc-http-enabled --rpc-http-api=ETH,NET,IBFT,WEB3 --host-allowlist="*" --rpc-http-cors-origins="all" --rpc-http-port=$((8548+i)) --graphql-http-enabled --graphql-http-port=$((8569+i))\ncd ..\n" > start_regular_node_$i.sh
    chmod +x start_regular_node_$i.sh
    echo "Writing script to launch RNode-$i with JSON-RPC on port $((8548+i)) and p2p on port $((30306+i))"
    j=$[$j+1]
done

printf "cd RNode-1\nethsigner --logging=ALL --chain-id=1337 --downstream-http-port=8549 --http-listen-port=8590 --http-cors-origins="*" file-based-signer --key-file=keyFile --password-file=passwordFile\ncd ..\n" > start_ethsigner_regular_node_1.sh
chmod +x start_ethsigner_regular_node_1.sh
echo "Writing script to launch EthSigner for RNode-1 with JSON-RPC on port 8590"

printf "cd RNode-2\nethsigner --logging=ALL --chain-id=1337 --downstream-http-port=8550 --http-listen-port=8591 --http-cors-origins="*" file-based-signer --key-file=keyFile --password-file=passwordFile\ncd ..\n" > start_ethsigner_regular_node_2.sh
chmod +x start_ethsigner_regular_node_2.sh
echo "Writing script to launch EthSigner for RNode-2 with JSON-RPC on port 8591"
