###############################################################################
# Reading/Writing/Modifying RML files
from lxml import etree # ???
import xml.etree.ElementTree as ET # ???

###############################################################################
class BeamlineObject:
    """ magic wrapper between xml and python objects
    """
    def __init__(self,name:str,type:str) -> None:
        self.name = name
        self.type = type

###############################################################################
class RMLFile:
    """Read/Write wrapper for the Ray RML files
    """
    def __init__(self,filename:str=None,/,template:str=None) -> None:
        self._filename=filename
        self._template = template if template is not None else filename
        pass

    def _read(self,file:str=None):
        """read rml file

        Args:
            file (str, optional): file name to read. If set to None will use template file name defined during initilizatino of the class. Defaults to None.
        """
        if file is None:
            file = self._template
        self._tree = ET.parse(file)
