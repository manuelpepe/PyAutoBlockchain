#!/bin/bash

if [[ -z "$(which ganache-cli)" ]]; then
    echo "ganache-cli not found"
    exit 1
fi

if [[ -z "$(which truffle)" ]]; then
    echo "truffle not found"
    exit 1
fi

if [[ ! -d integration-tests ]]; then
    echo "Subdirectory 'integration-tests/' not found."
    echo "Make sure to run the script from PAB's root."
    exit 2
fi

echo "[i] Starting ganache"
ganache-cli &
GANACHE_PID=$!

echo "[i] Setting up contracts"
cd integration-tests/contracts || exit 3

echo "[i] Building contracts"
truffle build

echo "[i] Testing contracts"
truffle test

echo "[i] Deploying contracts"
truffle migrate --network development > deploy.log 2>&1
echo Deploy Log:
cat deploy.log

echo "[i] Writing contract addresses mapping to integration-tests/.contracts.map"
temp_file=$(mktemp)
grep -E "Deploying|Replacing|contract address" deploy.log > "$temp_file"
sed -n -i '$!N;s/.*\(Deploying\|Replacing\) '\''\(.*\)'\''.*\n.*contract address:\s*\(.*\)/\2:\3/p' "$temp_file"
cp "$temp_file" ../.contracts.map
cat ../.contracts.map

echo "[i] Running tests"
cd ../..
pytest integration-tests/ --cov=pab --cov-report xml --cov-report term
tests_result=$?

echo "[i] Stopping ganache"
kill $GANACHE_PID

exit $tests_result
