import shelve


class Storage:
    def load(self, key):
        raise NotImplementedError

    def save(self, key, value):
        raise NotImplementedError


class MemoryStorage(Storage):
    def __init__(self):
        self._data = {}

    def load(self, key):
        return self._data.get(key)

    def save(self, key, value):
        self._data[key] = value


class FileStorage(Storage):
    def __init__(self, filepath='./conversation.db'):
        self.filepath = filepath

    def load(self, key):
        with shelve.open(self.filepath) as db:
            return db.get(key)

    def save(self, key, value):
        with shelve.open(self.filepath) as db:
            db[key] = value
