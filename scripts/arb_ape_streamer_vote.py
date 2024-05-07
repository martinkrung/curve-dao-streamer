# legacy script to create a vote in the Curve DAO with brownie
import json
import os
import warnings

import requests
from brownie import Contract, accounts, chain, web3
from eth_abi import encode_single

warnings.filterwarnings("ignore")

# this script is used to prepare, simulate and broadcast votes within Curve's DAO
# modify the constants below according the the comments, and then use `simulate` in
# a forked mainnet to verify the result of the vote prior to broadcasting on mainnet

# addresses related to the DAO - these should not need modification
CURVE_DAO_OWNERSHIP = {
    "agent": "0x40907540d8a6c65c637785e8f8b742ae6b0b9968",
    "voting": "0xe478de485ad2fe566d49342cbd03e49ed7db3356",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 30,
}

CURVE_DAO_PARAM = {
    "agent": "0x4eeb3ba4f221ca16ed4a0cc7254e2e32df948c5f",
    "voting": "0xbcff8b0b9419b9a88c44546519b1e909cf330399",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 15,
}

EMERGENCY_DAO = {
    "forwarder": "0xf409Ce40B5bb1e4Ef8e97b1979629859c6d5481f",
    "agent": "0x00669DF67E4827FCc0E48A1838a8d5AB79281909",
    "voting": "0x1115c9b3168563354137cdc60efb66552dd50678",
    "token": "0x4c0947B16FB1f755A2D32EC21A0c4181f711C500",
    "quorum": 51,
}

# the intended target of the vote, should be one of the above constant dicts
TARGET = CURVE_DAO_OWNERSHIP

# address to create the vote from - you will need to modify this prior to mainnet use
SENDER = accounts.at("0x34d6Dbd097f6b739C59D7467779549Aea60e1F84", force=True)

# a list of calls to perform in the vote, formatted as a lsit of tuples
# in the format (target, function name, *input args).
#
# for example, to call:
# GaugeController("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB").add_gauge("0xFA712...", 0, 0)
#
# use the following:
# [("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB", "add_gauge", "0xFA712...", 0, 0),]
#
# commonly used addresses:
# GaugeController - 0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB
# GaugeProxy - 0x519AFB566c05E00cfB9af73496D00217A630e4D5
# PoolProxy - 0xeCb456EA5365865EbAb8a2661B0c503410e9B347
# FactoryPoolProxy - 0x2EF1Bc1961d3209E5743C91cd3fBfa0d08656bC3

def encode(sig: str, *args):
    x = web3.keccak(text=sig)[:4] + encode_single(sig[sig.find("(") :], args)
    return x.hex()


OP_TOKEN = "0x4200000000000000000000000000000000000042"
STREAMER = "0x1C8f3D9Fc486e07e3c06e91a18825a344CeeFc54"
AGENT_PROXY = "0x28c4A1Fa47EEE9226F8dE7D6AF0a41C62Ca98267"
AMOUNT_TO_STREAM = 200_000 * 10**18

GAUGES = ["0x3050a62335948e008c6241b3ef9a81a8c0613b76", "0xb280fab4817c54796f9e6147aa1ad0198cfefb41"]  # up to 8 gauges

ACTIONS = [
    ("0x8e1e5001C7B8920196c7E3EdF2BCf47B2B6153ff", "broadcast", [ # accept transfer ownership
        ("0xabC000d88f23Bb45525E447528DBF656A9D55bf5", encode("accept_transfer_ownership()")),
    ]),
    ("0x8e1e5001C7B8920196c7E3EdF2BCf47B2B6153ff", "broadcast", [ # setup streamer
        ("0xD166EEdf272B860E991d331B71041799379185D5", encode("transfer(address,address,uint256)", OP_TOKEN, AGENT_PROXY, AMOUNT_TO_STREAM)), # transfer from vault to proxy
        (OP_TOKEN, encode("approve(address,uint256)", STREAMER, AMOUNT_TO_STREAM)),  # allow the gauge streamer to transferFrom proxy
        (STREAMER, encode("notify_reward_amount(uint256)", AMOUNT_TO_STREAM)),
    ]),
    ("0x8e1e5001C7B8920196c7E3EdF2BCf47B2B6153ff", "broadcast", [  # set gauges as receivers on the streamer
        (STREAMER, encode("add_receiver(address)", gauge)) 
        for gauge in GAUGES
    ]),
    ("0x8e1e5001C7B8920196c7E3EdF2BCf47B2B6153ff", "broadcast", [  # allow streamer to deposit in the gauges
        (gauge, encode("add_reward(address,address)", OP_TOKEN, STREAMER))
        for gauge in GAUGES
    ]),
]

# description of the vote, will be pinned to IPFS
DESCRIPTION = "Distribute 200k OP rewards over 8 weeks from the DAO vault on Optimism to the Tricrypto and TriCRV gauges on Optimism."


def prepare_evm_script():
    agent = Contract(TARGET["agent"])
    evm_script = "0x00000001"

    for address, fn_name, *args in ACTIONS:
        contract = Contract(address)
        fn = getattr(contract, fn_name)
        calldata = fn.encode_input(*args)
        agent_calldata = agent.execute.encode_input(address, 0, calldata)[2:]
        length = hex(len(agent_calldata) // 2)[2:].zfill(8)
        evm_script = f"{evm_script}{agent.address[2:]}{length}{agent_calldata}"

    return evm_script


def make_vote(sender=SENDER):
    text = json.dumps({"text": DESCRIPTION})
    # https://docs.infura.io/infura/networks/ipfs/how-to/authenticate-requests
    response = requests.post(
        "https://ipfs.infura.io:5001/api/v0/add",
        files={"file": text},
        auth=(os.getenv("IPFS_PROJECT_ID"), os.getenv("IPFS_PROJECT_SECRET")),
    )
    ipfs_hash = response.json()["Hash"]
    print(f"ipfs hash: {ipfs_hash}")

    aragon = Contract(TARGET["voting"])
    evm_script = prepare_evm_script()
    if TARGET.get("forwarder"):
        # the emergency DAO only allows new votes via a forwarder contract
        # so we have to wrap the call in another layer of evm script
        vote_calldata = aragon.newVote.encode_input(evm_script, DESCRIPTION, False, False)[2:]
        length = hex(len(vote_calldata) // 2)[2:].zfill(8)
        evm_script = f"0x00000001{aragon.address[2:]}{length}{vote_calldata}"
        print(f"Target: {TARGET['forwarder']}\nEVM script: {evm_script}")
        tx = Contract(TARGET["forwarder"]).forward(evm_script, {"from": sender})
    else:
        print(f"Target: {aragon.address}\nEVM script: {evm_script}")
        tx = aragon.newVote(
            evm_script,
            f"ipfs:{ipfs_hash}",
            False,
            False,
            # {"from": sender}
            {"from": sender, "priority_fee": "2 gwei"},
        )

    vote_id = tx.events["StartVote"]["voteId"]

    print(f"\nSuccess! Vote ID: {vote_id}")
    return vote_id


def simulate():
    # make the new vote
    convex = "0x989aeb4d175e16225e39e87d0d97a3360524ad80"
    vote_id = make_vote()

    # vote
    aragon = Contract(TARGET["voting"])
    aragon.vote(vote_id, True, False, {"from": convex})

    # sleep for a week so it has time to pass
    chain.sleep(86400 * 7)

    # moment of truth - execute the vote!
    aragon.executeVote(vote_id, {"from": accounts[0]})
