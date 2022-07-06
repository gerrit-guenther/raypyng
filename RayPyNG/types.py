from collections import UserDict

class TypeMap(UserDict):
    def __init__(self, default=None, map=None) -> None:
        if map is None:
            self.__known_types = {}
        else:
            self.__known_types = map
        self.__default_type = default

    def __getitem__(self, key):
        if key not in self.__known_types.keys():
            self.__known_types[key] = self.__default_type
        return self.__known_types[key]


class Counter(int):
    counter = 0
    def __new__(cls, *args, **kwargs):
        cls.counter += 1
        return  super().__new__(cls, cls.counter)

def MappedFactory(*args):
    pass

class TestMe:
    def __init__(self, test_map,name, vals) -> None:
        self.element_factory = MappedFactory(test_map)

    def add(self,name,value):
        xx = self.element_factory[name](name,value)