all:

start_env:
	# source will not work, but this is for cmd documentation
	source .env
	source .venv/bin/activate


deploy_passthrough_local:
	ape run scripts/deploy_passthrough_arbitrum.py deploy --network arbitrum:mainnet-fork:foundry maxFeePerGas=1100000000

deploy_passthrough_arbitrum_sepolia:
	ape run scripts/deploy_passthrough_arbitrum.py deploy --network arbitrum:sepolia:infura

deploy_passthrough_arbitrum:
	ape run scripts/deploy_passthrough_arbitrum.py deploy --network arbitrum:mainnet:infura

import_pvk:
	ape accounts import arbdeploy

networks_list:
	ape networks list