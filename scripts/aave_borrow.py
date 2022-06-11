from eth_typing import Address
from web3 import Web3
from scripts.get_weth import get_weth
from scripts.helper import get_account
from brownie import network, config, interface

AMOUNT = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    # Approve sending out ERC20 tokens
    # approve_erc20()

    approve_erc20(AMOUNT, lending_pool.address, erc20_address, account)

    print(f"Depositing....{AMOUNT}")
    tx = lending_pool.deposit(
        erc20_address, AMOUNT, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited!")
    # How much to borrow?

    available_borrow, total_debt = get_borrowable_data(lending_pool, account)

    # borrow DAI in terms of Eth

    dai_to_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )

    amount_dai_to_borrow = (1 / dai_to_eth_price) * (available_borrow * 0.95)
    # borrowable_eth -> borrowable_dai * 0.95
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)

    print("Borrowed some dai!")

    get_borrowable_data(lending_pool, account)

    repay_all(amount_dai_to_borrow, lending_pool, account)

    print("YOu just deposited, borrowed, and repayed with Aave")


def get_asset_price(price_feed_address):
    # ABI
    # Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH price is {converted_price}")
    return float(converted_price)


def repay_all(amount, lending_pool, account):
    dai_address = config["networks"][network.show_active()]["dai_token"]
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        dai_address,
        account,
    )

    repay_tx = lending_pool.repay(
        dai_address, amount, 1, account.address, {"from": account}
    )

    repay_tx.wait(1)


def get_borrowable_data(lending_pool, account):
    # tuple
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liq_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)

    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")

    print(f"You have {total_collateral_eth} worth of Eth deposited")
    print(f"You have {total_debt_eth} worth of Eth borrowed")
    print(f"You can borrow {available_borrow_eth} worth of Eth")

    return (float(available_borrow_eth), float(total_debt_eth))


# approves any ERC20 token
def approve_erc20(amount, spender, erc20_address, account):
    # ABI
    # Address
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    print(f"Amount available: {erc20.balanceOf(account.address)}")
    tx = erc20.approve(spender, amount, {"from": account})
    print("Approved!")
    return tx


def get_lending_pool():
    # ABI
    # Address

    address_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )

    lending_pool_address = address_provider.getLendingPool()  # address
    # ABI
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool
