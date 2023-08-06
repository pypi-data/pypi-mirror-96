#  Copyright (c) 2020. Davi Pereira dos Santos
#  This file is part of the kururu project.
#  Please respect the license - more about this in the section (*) below.
#
#  kururu is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  kururu is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with kururu.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is a crime and is unethical regarding the effort and
#  time spent here.
#  Relevant employers or funding agencies will be notified accordingly.

from aiuna.content.data import Data
from akangatu.distep import DIStep
from akangatu.transf.mixin.noop import asNoOp
from tatu import Tatu
from tatu.abs.storage import Storage
from tatu.amnesia import Amnesia
from tatu.pickle_ import Pickle
from tatu.sql.sqlite import SQLite


def setcache(storage, eager_store=True):
    from akangatu.transf.config import CACHE
    CACHE["cache"] = Cache(storage, eager_store=eager_store)


def closecache():
    from akangatu.transf.config import CACHE
    CACHE["cache"].storage.close()


class Cache(asNoOp, DIStep):
    # storages = {}

    #     ???? ver se vai haver cache-container.
    #     o único motivo seria caso a montagem dos campos lazy tenha muito overhead
    def __init__(self, storage="sqlite", eager_store=True, ignorelock=True, seed=0, _setcache=False):  # TODO: what todo with seed here?
        DIStep.__init__(self, storage=storage, eager_store=eager_store, ignorelock=ignorelock, seed=seed)
        if storage == "pickle":
            storage = Pickle(close_when_idle=True)
        elif storage == "sqlite":
            storage = SQLite(close_when_idle=True)
        elif storage == "amnesia":
            storage = Amnesia(close_when_idle=True)
        elif isinstance(storage, Storage):
            pass
        elif "://" in storage:
            storage = Tatu(url=storage, close_when_idle=True)
        else:
            print("Unknown storage:", type(storage))
            print("Unknown storage:", storage)
            exit()
        # if storage.id not in self.storages:
        #     self.storages[storage.id] = storage
        # self.storage: Storage = self.storages[storage.id]
        self.storage: Storage = storage
        self.eager_store = eager_store
        self.ignorelock = ignorelock
        if _setcache:
            setcache(self.storage)

    def _process_(self, data: Data):
        fetched = self.storage.fetch(data, lock=True, ignorelock=self.ignorelock)
        if fetched:
            return fetched
        self.storage.store(data, unlock=True, lazy=not self.eager_store, ignoredup=True)  # TODO: ignoredup?
        return data

    # TODO dar tatu.unlock() dentro do data.getitem se ocorrer alguma exception que interrompa o cacheamento

# c = 0
