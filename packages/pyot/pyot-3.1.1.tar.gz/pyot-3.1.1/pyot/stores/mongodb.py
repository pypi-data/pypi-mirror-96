import datetime
from typing import Any
from logging import getLogger
import asyncio
import pytz

import motor.motor_asyncio as mongo
from pyot.core.exceptions import NotFound
from pyot.pipeline.token import PipelineToken
from pyot.pipeline.objects import StoreObject
from pyot.pipeline.expiration import ExpirationManager
from pyot.utils import bytify, pytify

LOGGER = getLogger(__name__)


class MongoDB(StoreObject):
    unique = False
    store_type = "CACHE"

    def __init__(self, game: str, db: str, expirations: Any = None, log_level: int = 10, host='127.0.0.1', port=27017, **kwargs) -> None:
        self._game = game
        kwargs = {key.lower():val for (key, val) in kwargs.items()}
        if 'connect' not in kwargs:
            kwargs['connect'] = False
        if 'w' not in kwargs:
            kwargs['w'] = 0
        self._client = mongo.AsyncIOMotorClient(host=host, port=port, **kwargs)
        self._cache = None
        self._db_name = db
        self._alias = f"{host}:{port}:{db}"
        self._manager = ExpirationManager(game, expirations)
        self._log_level = log_level

    async def connect(self):
        if self._cache is None:
            LOGGER.warning(f'[Trace: {self._game.upper()} > MongoDB > {self._alias}] Connecting to MongoDB at {self._alias} ...')
            self._client.io_loop = asyncio.get_event_loop()
            self._cache = self._client[self._db_name]
            for method in self._manager:
                indexes = await self._cache[method].index_information()
                if 'setAt_1' in indexes:
                    if self._manager.get_timeout(method) >= 0:
                        await self._cache.command('collMod', method, index={'keyPattern': {'setAt': 1}, 'expireAfterSeconds': self._manager.get_timeout(method)})
                    else:
                        await self._cache[method].drop_index('setAt')
                elif self._manager.get_timeout(method) > 0:
                    await self._cache[method].create_index('token')
                    await self._cache[method].create_index('setAt', expireAfterSeconds=self._manager.get_timeout(method))
                else:
                    await self._cache[method].create_index('token')
        else:
            self._client.io_loop = asyncio.get_event_loop()

    async def set(self, token: PipelineToken, value: Any) -> None:
        timeout = self._manager.get_timeout(token.method)
        if timeout != 0:
            await self.connect()
            await self._cache[token.method].insert_one(
                {
                    'token': token.stringify,
                    'data': value,
                    'dataType': "bson",
                    'setAt': datetime.datetime.now(pytz.utc)
                }
            )
            LOGGER.log(self._log_level, f"[Trace: {self._game.upper()} > MongoDB > {self._alias}] SET: {self._log_template(token)}")

    async def get(self, token: PipelineToken, session=None) -> Any:
        timeout = self._manager.get_timeout(token.method)
        if timeout == 0:
            raise NotFound
        await self.connect()
        item = await self._cache[token.method].find_one({'token': token.stringify})
        if item is None:
            raise NotFound
        LOGGER.log(self._log_level, f"[Trace: {self._game.upper()} > MongoDB > {self._alias}] GET: {self._log_template(token)}")
        if item.get("dataType", None) is None:
            await self._cache[token.method].delete_many({'token': token.stringify})
            raise NotFound
        return item["data"]

    async def delete(self, token: PipelineToken) -> None:
        await self.connect()
        await self._cache[token.method].delete_many({'token': token.stringify})
        LOGGER.log(self._log_level, f"[Trace: {self._game.upper()} > MongoDB > {self._alias}] DELETE: {self._log_template(token)}")

    async def contains(self, token: PipelineToken) -> bool:
        await self.connect()
        item = await self._cache[token.method].find_one({'token': token.stringify})
        if item is None:
            return False
        return True

    async def clear(self):
        collections = await self._cache.list_collection_names()
        for name in collections:
            await self.connect()
            await self._cache.drop_collection(name)
        LOGGER.log(self._log_level, f"[Trace: {self._game.upper()} > MongoDB > {self._alias}] CLEAR: Store has been cleared successfully")


class MongoDBSerializer:

    _enums = {
        "pickle": 0,
        "bson": 1,
    }

    _serializers = {
        "pickle": bytify,
        "bson": lambda x: x,
    }

    _deserializers = {
        "pickle": pytify,
        "bson": lambda x: x,
    }

    def __init__(self, serialization: str):
        serialization = serialization.lower()
        try:
            self.serialization = serialization
            self.type_enum = self._enums[serialization]
            self.serializer = self._serializers[serialization]
            self.deserializer = self._deserializers[serialization]
        except KeyError as e:
            raise ValueError(f"MongoDB invalid serialization type '{e}'")

    def same_type(self, type_):
        if self._enums.get(type_, -1) == self.type_enum:
            return True
        return False

    def serialize(self, data, type_=None):
        if type_ is None:
            return self.serializer(data)
        return self._serializers[type_](data)

    def deserialize(self, data, type_=None):
        if type_ is None:
            return self.deserializer(data)
        return self._deserializers[type_](data)

    def transerialize(self, data, from_, to_=None):
        deserialized = self._deserializers[from_](data)
        if to_ is None:
            return self.serialize(deserialized)
        return self._serializers[to_](deserialized)

    def valid_type(self, type_, throw=False):
        try:
            _ = self._enums[type_]
            return True
        except KeyError as e:
            if throw:
                raise ValueError(f"MongoDB invalid serialization type '{e}'")
            return False
