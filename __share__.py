from . import __path__ as _dir_nspath
from pathlib import Path

__all__ = []
qu_path = Path(list(_dir_nspath)[0])

# used for prefix dicts
class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()
