from scripts.helpful_scripts import get_account
from brownie import accounts, network, config, interface


def get_weth():
    # Getting WETH from ETH in our wallet

    account = get_account()
    weth = interface.WethInterface(
        config["networks"][network.show_active()]["weth_token"]
    )
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    print("[+] Received 0.1 WETH")
    return tx


def main():
    get_weth()
