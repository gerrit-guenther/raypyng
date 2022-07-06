
###############################################################################
class XmlAttribute:
    def __init__(self,xmlvalue=None) -> None:
        if xmlvalue is not None:
            self.__value=xmlvalue

    def set(self,value):
        self.__value = value

    def get(self):
        return self.__value

    def __str__(self):
        return str(self.__value)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self}')"

###############################################################################
class XmlMappedAttribute(XmlAttribute):
    def __init__(self,xmlvalue=None,map=None) -> None:
        if map is None:
            raise ValueError(f"map parameter is required and can not be 'None'")
        self.__map = map
        super().__init__(xmlvalue)

        if xmlvalue in self.__map:
            self.set(self.__map[xmlvalue] )
        else:
            raise ValueError(f"Invalid value for the XmlAttribute: {xmlvalue}")


    def __str__(self):
        for k,v in self.__map.items():
            if v==self.get():
                return k
        raise ValueError(f"Can not map to bool: {self.get()}")

    def __repr__(self):
        return f"{self.__class__.__name__}('{self}',map={self.__map})"


###############################################################################
class XmlBoolAttribute(XmlMappedAttribute):
    def __init__(self,xmlvalue=None,true='True',false='False') -> None:
        m = {true:True,false:False}
        super().__init__(xmlvalue,m)



###############################################################################
class XmlAttributeBase:
    """Base class for Xml Attribute, including nessesary linking and etc
    """
    def __init__(self,*args,**kwargs) -> None:
        self.test_param = 42
    

###############################################################################
def XmlAttributeTypeFactory(*args,**kwargs):
    """Generates dynamically a new type which inherits from the supplied type and
    from the XmlAttributeBase

    Raises:
        TypeError: when no value or no wish type was supplied

    Returns:
        _type_: _description_
    """
    if not args:
        raise TypeError("value or type is needed for creating AttributeFactory object")
    type_or_value, *args = args
    if isinstance(type_or_value,type):
        _type = type_or_value
    else:
        _type = type(type_or_value)
        args = (type_or_value, *args)
    _sclass = type(f"XmlAttributeType<{_type}>", (XmlAttributeBase, _type, ), {
        "__new__" : lambda __name, __bases, *args, **kwargs : _type.__new__(__name, __bases, *args, **kwargs)
    })
    return _sclass(*args,**kwargs)

###############################################################################
def XmlAttributeFactory(*args,**kwargs):
    """Returns an instance of the dynamically created typed XmlAttribute class

    Returns:
        _type_: _description_
    """
    return XmlAttributeTypeFactory(*args,**kwargs)

