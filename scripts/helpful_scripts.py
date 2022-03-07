from brownie import network, accounts, config

LOCAL_BLOCKCHAIN_ENV = ["development", "test-ganache-local", "mainnet-fork", "ganache"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        return accounts[0]
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None
