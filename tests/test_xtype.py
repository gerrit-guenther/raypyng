

#from types import NoneType


class ValueTree:
    def __init__(self,xtype=None,*args,**kwargs) -> None:
        if xtype is not None and xtype is not type(None):
            self.__value = xtype(*args,**kwargs)
        else:
            self.__value = None
        self.__leafs = {}


    def __setattr__(self, name: str, value) -> None:
        #if __name in self.__leafs:
        if name is None:
            return 
        if name.startswith("_"):
            super().__setattr__(name,value)
        else:
            self.__leafs[name] = ValueTree(type(value),value) 
        #pass

    def __getattr__(self, name: str) -> None:
        if name.startswith("_"):
            super().__getattr__(name)
        else:
            if isinstance(self.__leafs[name],ValueTree):
                return self.__leafs[name].__value
            else:
                return self.__leafs[name]


# creating class dynamically

class AttributeBase:
    def __init__(self,*args,**kwargs) -> None:
        self.param = 42
    

def AttributeFactory(*args,**kwargs):
    if not args:
        raise TypeError("value or type is needed for creating AttributeFactory object")
    type_or_value, *args = args
    if isinstance(type_or_value,type):
        _type = type_or_value
    else:
        _type = type(type_or_value)
        args = (type_or_value, *args)
    _sclass = type(f"Attribute<{_type}>", (AttributeBase, _type, ), {
        "__new__" : lambda __name, __bases, *args, **kwargs : _type.__new__(__name, __bases, *args, **kwargs)
    })
    return _sclass(*args,**kwargs)
  
