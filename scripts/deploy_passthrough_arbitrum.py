from pathlib import Path
from readline import append_history_file

import os
import click
from ape import accounts, project, chain, networks
from ape.cli import NetworkBoundCommand, network_option, account_option
from eth._utils.address import generate_contract_address
from eth_utils import to_checksum_address, to_canonical_address
from datetime import datetime

# some constants from .env if needed
# COLLECTOR_ADDRESS = os.getenv('COLLECTOR_ADDRESS')

# account = accounts.load(DEPLOY_NAME)

@click.group(short_help="Deploy the project")
def cli():
    pass


@cli.command(cls=NetworkBoundCommand)
#@network_option()
@account_option()
def deploy(network, account):
    # crvUSDARBCRV-gauge address
    reward_receiver = '0xB08FEf57bFcc5f7bF0EF69C0c090849d497C8F8A'
    # Existing Arbitrum Streamer: https://arbiscan.io/address/0xf968e2e28460a8f419877df2ec86574636e8262c
    # New Llama Risk Multisig for new ARB Grant: https://arbiscan.io/address/0xa6A7020B3276e86011a33638F3CD8fe02d5E4b61

    depositors = ['0xf968e2e28460a8f419877df2ec86574636e8262c', '0xa6A7020B3276e86011a33638F3CD8fe02d5E4b61']

    # deploy = account.deploy(project.RewardForwarderFromArbitrum, reward_receiver, depositors, publish=True)

    deploy = account.deploy(project.RewardForwarderFromArbitrum, reward_receiver, depositors, max_priority_fee="1000 wei", max_fee="1 gwei", gas_limit="100000")


@cli.command(cls=NetworkBoundCommand)
#@network_option()
@account_option()
def publish(network, account):
    print(account)
    print(network)

    networks.provider.network.explorer.publish_contract("")