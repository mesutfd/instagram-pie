from typing import Generator

from storages import ClientStorage, UserBankStorage


def get_clients() -> Generator:
    try:
        clients = ClientStorage()
        yield clients
    finally:
        clients.close()


def get_agents():
    try:
        agents = UserBankStorage()
        yield agents
    finally:
        agents.close()
