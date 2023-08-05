import asyncio
from pyot.models import riot
from .__core__ import SyotBaseObject

class SyotBase(SyotBaseObject):
    pass

# from .account import Account, ActivePlatform

class Account(SyotBase, riot.Account):
    def get(self, **kwargs):
        return asyncio.run(super().get(**kwargs))

class ActiveShard(SyotBase, riot.ActiveShard):
    def get(self, **kwargs):
        return asyncio.run(super().get(**kwargs))

SyotBase._bridges, SyotBaseObject._bridges = {
    "Account": Account,
    "ActiveShard": ActiveShard,
}