from enum import Enum

class ModelCompatibleEnum(Enum):
    @classmethod
    def as_list(cls):
        return [entry.name for entry in cls]

    @classmethod
    def as_tuples(cls):
        return tuple(((entry.name, entry.value) for entry in cls))