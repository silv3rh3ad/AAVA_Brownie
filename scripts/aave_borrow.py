from os import access
from scripts.get_WETH import get_weth
from scripts.helpful_scripts import get_account
from brownie import config, network, interface
from web3 import Web3

# 0.1
amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()

    lending_pool = get_lending_pool()

    # Aprroving the sending out ERC20 tokens (EVERY ERC20 TOKEN HAS TO BE APPROVED )
    approve_erc20(amount, lending_pool.address, erc20address, account)

    # Deposit
    print("[+] Depositing !")
    tx = lending_pool.deposit(
        erc20address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("[+] Deposited !")

    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)

    # borrowing
    print("\n[+] Borrowing !")
    # DAI in terms of ETH
    dai_price_feed = get_assest_price(
        "DAI/ETH", config["networks"][network.show_active()]["dai_price_feed"]
    )
    amount_to_borrow = (1 / dai_price_feed) * (borrowable_eth * 0.90)
    print(f"[+] Borring {amount_to_borrow} DAI")

    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    print("\t[+]Borrowed some DAI ")
    get_borrowable_data(lending_pool, account)

    # Repay everything
    repay_all(amount, lending_pool, account)


def repay_all(_amount, _lending_pool, _account):
    approve_erc20(
        Web3.toWei(_amount, "ether"),
        _lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        _account,
    )

    repay_tx = _lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        _amount,
        1,
        _account.address,
        {"from": _account},
    )
    repay_tx.wait(1)
    print("[+] Repaid!")


def get_assest_price(_assest_code, _assests_price_feed_address):
    assests_eth_price_feed = interface.AggregatorV3Interface(
        _assests_price_feed_address
    )
    latest_price = assests_eth_price_feed.latestRoundData()[1]
    latest_price = Web3.fromWei(latest_price, "ether")
    print(f"[+] Latest Price of {_assest_code}: {latest_price}")
    return float(latest_price)


def get_borrowable_data(_lendingpool, _account):
    # This variables returns in terms of WEI
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = _lendingpool.getUserAccountData(_account.address)

    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    totalCollateralETH = Web3.fromWei(totalCollateralETH, "ether")
    totalDebtETH = Web3.fromWei(totalDebtETH, "ether")

    print(f"\n[+] You have {totalCollateralETH} worth of ETH deposited.")
    print(f"[+] You have {totalDebtETH} worth of ETH borrowed.")
    print(f"\t[+] You can borrow {availableBorrowsETH} worth of ETH.")

    return (float(availableBorrowsETH), float(totalDebtETH))


def approve_erc20(amount, spender, erc20_address, account):
    print("[+] Approving ERC20 Token ..!")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("[+] Approved !")
    return tx


def get_lending_pool():
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["landing_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_address_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool
