import json
from collections.abc import MutableMapping


class MetaStorage(MutableMapping):
    @classmethod
    def to_str(cls, obj):
        if isinstance(obj, memoryview):
            obj = obj.tobytes()
        if isinstance(obj, bytes):
            obj = obj.decode("utf-8")
        return obj

    def __init__(self, path, fs_map: MutableMapping, meta_map: MutableMapping):
        self._fs_map = fs_map
        self._meta = meta_map
        self._path = path

    def __getitem__(self, k: str) -> bytes:
        if k.startswith("."):
            return bytes(
                json.dumps(
                    json.loads(self.to_str(self._meta[".hub.dataset"]))[k][self._path]
                ),
                "utf-8",
            )
        else:
            return self._fs_map[k]

    def get(self, k: str) -> bytes:
        if k.startswith("."):
            meta_ = self._meta.get(".hub.dataset")
            if not meta_:
                return None
            meta = json.loads(self.to_str(meta_))
            metak = meta.get(k)
            if not metak:
                return None
            item = metak.get(self._path)
            return bytes(json.dumps(item), "utf-8") if item else None
        else:
            return self._fs_map.get(k)

    def __setitem__(self, k: str, v: bytes):
        if k.startswith("."):
            meta = json.loads(self.to_str(self._meta[".hub.dataset"]))
            meta[k] = meta.get(k) or {}
            meta[k][self._path] = json.loads(self.to_str(v))
            self._meta[".hub.dataset"] = bytes(json.dumps(meta), "utf-8")
        else:
            self._fs_map[k] = v

    def __len__(self):
        return len(self._fs_map) + 1

    def __iter__(self):
        yield ".zarray"
        yield from self._fs_map

    def __delitem__(self, k: str):
        if k.startswith("."):
            meta = json.loads(self.to_str(self._meta[".hub.dataset"]))
            meta[k] = meta.get(k) or dict()
            meta[k][self._path] = None
            self._meta[".hub.dataset"] = bytes(json.dumps(meta), "utf-8")
        else:
            del self._fs_map[k]

    # def listdir(self):
    #     res = []
    #     for i in self:
    #         res += [i]
    #     return res

    # def rmdir(self):
    #     for i in self.listdir():
    #         del self[i]

    def commit(self):
        self._meta.commit()
        self._fs_map.commit()