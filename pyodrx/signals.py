# Class that adds Opendrive signal elements
# <Signals> is a container for <signal>. <signals> is a subelement of the <road> element.
# Current subelements include:
# <validity> to restrict validity to specific lanes

import xml.etree.ElementTree as ET


class Signals:
    """ Signals defines the signals element in Opendrive
        
        Parameters
        ----------

        Attributes
        ----------
           signals (list): list of signal elements in this element

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
                
    """

    def __init__(self):
        self.signalList = []

    def get_element(self):
        element = ET.Element('signals')
        for signal in self.signalList:
            element.append(signal.get_element())
        return element


class Signal:
    """ Signal defines the signal element in Opendrive
        
        Parameters
        ----------
            s (int): the s-coordinate of the signal.
            t (double): the t-coordinate of the signal.
            dynamic (bool): static/dynamic definition of the signal.
            orientation (str): The orientation of the signal wrt the road. "+" means valid in positive s.
            z-offset (double): offset between the road to the bottom edge of the signal.
            country (str): country code used to read signal type and subtype
            type (str): code for the signal (stop sign for example is 206 in Germany)
            subtype (str): code for values in the signal
            value (double):
            unit (str):
            width (int):
            text (str)
            h-offset (double):
            pitch (double) :
            roll (double):

        Attributes
        ----------
           

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
                
    """

    def __init__(self, s, t, dynamic="no", orientation="+", zOffset=0.00, country="US", Type="R1", subtype="1",
                 value=0.00):
        self.s = s
        self.t = t
        self.dynamic = dynamic
        self.orientation = orientation
        self.zOffset = zOffset
        self.country = country
        self.type = Type
        self.subtype = subtype
        self.value = value

    def get_attributes(self):
        retdict = {"s": str(self.s), "t": str(self.t), "dynamic": self.dynamic, "orientation": self.orientation,
                   "zOffset": str(self.zOffset), "country": str(self.country), "type": str(self.type),
                   "subtype": str(self.subtype), "value": str(self.value)}
        return retdict

    def get_element(self):
        element = ET.Element('signal', attrib=self.get_attributes())
        return element


class Dependency:
    """
    Dependency defines the dependency element in Opendrive. It is placed within the signal element.
    Parameters
        ----------
            id (str): id of the controlled signal
            type (str): type of dependency

        Attributes
        ----------
            id (str): id of the controlled signal
            type (str): type of dependency

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self, id, type):
        self.id = id
        self.type = type

    def get_attributes(self):
        retdict = {"id": str(self.id), "type": str(self.type)}
        return retdict

    def get_element(self):
        element = ET.Element('dependency', attrib=self.get_attributes())
        return element
