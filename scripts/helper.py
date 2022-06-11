from brownie import network, accounts, config, interface, Contract

FORKED_LOCAL_ENV = ["mainnet-fork"]
LOCAL_CHAIN_ENV = ["development", "ganache-local", "mainnet-fork"]


def get_account(index=None, id=None):
    """Sets the default account for transactions.
    If on development network will grab the one at `index`.
    If specifying the id, will load from brownie's keystore.
    If on a local development network or forked network, it will add an account from the .env
        file.


    Args:
        index (int)
        id (string)

    Returns:
        brownie.accounts.Account: Specified account object.
    """
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_CHAIN_ENV
        or network.show_active() in FORKED_LOCAL_ENV
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


# contract_to_mock = {
#     "eth_usd_price_feed": MockV3Aggregator,
#     "vrf_coordinator": VRFCoordinatorMock,
#     "link_token": LinkToken,
# }


# def get_contract(contract_name):
#     """Grabs the contract addresses from the brownie config if defined, otherwise,
#     it will deploy a mock version of that contract and return that mock contract.

#     Args:
#         contract_name (string)

#     Returns:
#         brownie.network.contract.ProjectContract: The most recently deployed version of this contract.
#     """

#     # we can get the compiled contract
#     contract_type = contract_to_mock[contract_name]

#     if network.show_active() in LOCAL_CHAIN_ENV:
#         if len(contract_type) <= 0:
#             # MockV3Aggregator.length
#             deploy_mocks()
#         contract = contract_type[-1]
#         # MockV3Aggregator[-1]
#     else:
#         contract_address = config["networks"][network.show_active()][contract_name]
#         # address
#         # ABI

#         # we have the ABI from the build and the address from the config
#         contract = Contract.from_abi(
#             contract_type._name, contract_address, contract_type.abi
#         )
#     return contract


# DECIMALS = 8
# INITIAL_VALUE = 200000000000


# def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):

#     account = get_account()
#     MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
#     link_token = LinkToken.deploy({"from": account})
#     VRFCoordinatorMock.deploy(link_token.address, {"from": account})
#     print("Deployed mocks!")


# def fund_w_link(
#     contract_address, account=None, link_token=None, amount=100000000000000000
# ):
#     account = account if account else get_account()
#     link_token = link_token if link_token else get_contract("link_token")

#     # # if you have the interface you don't need the abi (brownie will know to do it)
#     # link_token_contract = interface.LinkTokenInterface(link_token.address)
#     # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
#     tx = link_token.transfer(contract_address, amount, {"from": account})
#     tx.wait(1)
