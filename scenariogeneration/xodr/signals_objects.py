""" the signals_objects module contains the base classes relating signals (traffic signs and signals) and objects

"""
import xml.etree.ElementTree as ET
from .helpers import enum2str
from .enumerations import ObjectType, Orientation, Dynamic 

class _SignalObjectBase():
    """ creates a common basis for Signal and Object shall not be instantiated directly

        Attributes
        ----------
            s (float): s-coordinate of Signal / Object

            t (float): t-coordinate of Signal / Object

            id (string): id of Signal / Object

            Type (ObjectType or string): type of the Signal (typically string) / Object (typically enum ObjectType)

            subtype (string): subtype for further specification of Signal / Object
            
            dynamic (Dynamic): specifies if Signal / Object is static (road sign) or dynamic (traffic light)
            
            name (string): name for identification of Signal / Object
            
            zOffset (float): vertical offset of Signal / Object with respect to centerline
            
            orientation (Orientation): orientation of Signal / Object with respect to road
            
            pitch (float): pitch angle (rad) of Signal / Object relative to the inertial system (xy-plane)
            
            roll (float): roll angle (rad) of Signal / Object after applying pitch, relative to the inertial system (x’’y’’-plane) 
            
            width (float): width of the Signal / Object
            
            height (float): height of Signal / Object
            
            _usedIDs ({[str]}): dictionary with list of used IDs, keys are class names of child class (Object, Signal). 
            Shared among all instances of Signal/Object to auto-generate unique IDs.

            _IDCounter ({int}): dictionary with counter for auto-generation of IDs, keys are class names of child class (Object, Signal). 
            Shared among all instances of Signal/Object to auto-generate unique IDs.


        Methods
        -------
            get_common_attributes()
                Returns a dictionary of all attributes of FileHeader
                
            _update_id()
                Ensures that an ID is assigned if none was provided and that provided IDs are unique
                Should be called when adding an Object or signal to the road
        """
        
    _usedIDs = {}
    _IDCounter = {}

    def __init__(self,s,t,id,Type,subtype,dynamic,name,zOffset,orientation,pitch,roll,width,height):
        """ initalizes common attributes for Signal and Object

        Parameters
        ----------
            s (float): s-coordinate of Signal / Object

            t (float): t-coordinate of Signal / Object

            id (string): id of Signal / Object

            Type (ObjectType or string): type of the Signal (typically string) / Object (typically enum ObjectType)

            subtype (string): subtype for further specification of Signal / Object
            
            dynamic (Dynamic): specifies if Signal / Object is static (road sign) or dynamic (traffic light)
            
            name (string): name for identification of Signal / Object
            
            zOffset (float): vertical offset of Signal / Object with respect to centerline
            
            orientation (Orientation): orientation of Signal / Object with respect to road
            
            pitch (float): pitch angle (rad) of Signal / Object relative to the inertial system (xy-plane)
            
            roll (float): roll angle (rad) of Signal / Object after applying pitch, relative to the inertial system (x’’y’’-plane)
            
            width (float): width of the Signal / Object
            
            height (float): height of Signal / Object

        """ 
        self.s = s
        self.t = t
        self.height = height
        self.Type = Type       
        self.dynamic = dynamic
        self.name = name
        self.zOffset = zOffset
        self.subtype = subtype
        self.orientation = orientation
        self.pitch = pitch
        self.roll = roll
        self.width = width
        self.id = id
        
    
    def __eq__(self, other):
        if isinstance(other,_SignalObjectBase):
            if self.get_common_attributes() == other.get_common_attributes():
                return True
        return False

    def _update_id(self):
        #ensure unique IDs
        try:
            if str(self.id) in self._usedIDs[self.__class__.__name__]:
                print ("Warning: id",self.id,"has already been used for another",self.__class__.__name__,"...auto-generating unique id.")
                
        except KeyError:
            self._usedIDs[self.__class__.__name__]=[]
            self._IDCounter[self.__class__.__name__]=0
            
        
        if self.id == None or (str(self.id) in self._usedIDs[self.__class__.__name__]):
            while (str(self._IDCounter[self.__class__.__name__]) in self._usedIDs[self.__class__.__name__]):
                self._IDCounter[self.__class__.__name__]+=1
            self.id = str(self._IDCounter[self.__class__.__name__])             
    
        self._usedIDs[self.__class__.__name__].append(str(self.id))
        
        
        
    def get_common_attributes(self):
            """ returns common attributes of Signal and Object as a dict
    
            """
            retdict = {}
            retdict['id'] = str(self.id)
            retdict['s'] = str(self.s)
            retdict['t'] = str(self.t)
            retdict['subtype'] = str(self.subtype)
            retdict['dynamic'] = enum2str(self.dynamic)
            retdict['zOffset'] = str(self.zOffset)
            if self.pitch:
                retdict['pitch'] = str(self.pitch)
            if self.roll:
                retdict['roll'] = str(self.roll)
            if self.width is not None:
                retdict['width'] = str(self.width)
            if self.height is not None:
                retdict['height'] = str(self.height)            
            if self.name is not None:   
                retdict['name'] = str(self.name)            
            if (isinstance(self.Type, ObjectType)):
                retdict['type'] = enum2str(self.Type)
            else:
                retdict['type'] = str(self.Type)                        
            if self.orientation == Orientation.positive:
                retdict['orientation'] = '+'    
            elif self.orientation == Orientation.negative:
                retdict['orientation'] = '-'        
            else:
                retdict['orientation'] = enum2str(self.orientation)    
            
            return retdict

class Signal(_SignalObjectBase):
    """ Signal defines the signal element in Opendrive

        Attributes
        ----------
            s (float): s-coordinate of Signal (init in base class)

            t (float): t-coordinate of Signal (init in base class)

            country (str): country code according to ISO 3166-1 (alpha-2 with two letters for OpenDRIVE 1.6, alpha-3 with three letters for OpenDRIVE 1.4)        
            
            Type (SignalType or str): type of Signal (str) (init in base class)
            
            subtype (string): subtype for further specification of Signal (init in base class)
            
            id (string): id of Signal (init in base class)
            
            name (string): name for identification of Signal (init in base class)
            
            dynamic (Dynamic): specifies if Signal is static or dynamic (init in base class)
            
            value (double): value for further specification of the signal
            
            unit (str): unit, needs to be provided when value is given
            
            zOffset (float): vertical offset of Signal with respect to centerline (init in base class)
            
            orientation (Orientation): orientation of Signal with respect to road (init in base class)
            
            hOffset (float): heading offset of the signal relative to orientation
            
            pitch (float): pitch angle (rad) of Signal relative to the inertial system (xy-plane) (init in base class)
            
            roll (float): roll angle (rad) of Signal after applying pitch, relative to the inertial system (x’’y’’-plane) (init in base class)
            
            width (float): width of the Signal (init in base class)
            
            height (float): height of Signal (init in base class)
            
            validity (Validity): explicit validity information for a signal (optional)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
                
    """

    def __init__(self, s, t, country, Type, subtype="-1", id=None, name=None, dynamic=Dynamic.no, value=None, unit=None, zOffset=1.5, orientation=Orientation.positive, 
                 hOffset=0, pitch=0, roll=0, height=None, width=None):
        """ initalizes the Signal

        Parameters
        ----------
            s (float): s-coordinate of Signal (init in base class)

            t (float): t-coordinate of Signal (init in base class)
            
            country (str): country code according to ISO 3166-1 (alpha-2 with two letters for OpenDRIVE 1.6, alpha-3 with three letters for OpenDRIVE 1.4)
            
            Type (SignalType or str): type of Signal (str) (init in base class)

            subtype (string): subtype for further specification of Signal (init in base class)
                Default: "-1"
            id (string): id of Signal (init in base class)
                Default: None
            name (string): name for identification of Signal (init in base class)
                Default: None 
            dynamic (Dynamic): specifies if Signal is static or dynamic (init in base class)
                Default: Dynamic.no 
            value (double): value for further specification of the signal
                Default: None
            unit (str): unit, needs to be provided when value is given
                Default: None                                  
            zOffset (float): vertical offset of Signal with respect to centerline (init in base class)
                Default: 0                        
            orientation (Orientation): orientation of Signal with respect to road (init in base class)
                Default: Orientation.none                                    
            hOffset (float): heading offset of the signal relative to orientation
                Default: 0
            pitch (float): pitch angle (rad) of Signal relative to the inertial system (xy-plane) (init in base class)
                Default: 0                                 
            roll (float): roll angle (rad) of Signal after applying pitch, relative to the inertial system (x’’y’’-plane) (init in base class)
                Default: 0                                             
            width (float): width of the Signal (init in base class)
                Default: None     
            height (float): height of Signal (init in base class)
                Default: None                                       

        """        
        
        
        #get attributes that are common with signals
        super().__init__(s,t,id,Type,subtype,dynamic,name,zOffset,orientation,pitch,roll,width,height)
        self.s = s
        self.t = t
        self.dynamic = dynamic
        self.orientation = orientation
        self.zOffset = zOffset
        self.country = country
        self.type = Type
        self.subtype = subtype
        self.value = value
        self.unit = unit
        self.hOffset = hOffset
        self.validity = None
        
        
    def __eq__(self, other):
        if isinstance(other,Signal):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self):
        retdict = super().get_common_attributes()
        retdict["country"] = str(self.country).upper()
        retdict["type"] = str(self.type)
        retdict["subtype"] = str(self.subtype)
        if self.hOffset:
            retdict["hOffset"] = str(self.hOffset)    
        #TODO check if value is supplied --> unit is mandatory in that case   
        if self.value is not None:
            retdict["value"] = str(self.value)
            retdict["unit"] = str(self.unit)
        return retdict

    def add_validity(self, fromLane, toLane): 
        if self.validity: 
            raise ValueError('only one validity is allowed')
        self.validity = Validity(fromLane, toLane)

    def get_element(self):
        element = ET.Element('signal', attrib=self.get_attributes())
        if self.validity: 
            element.append(self.validity.get_element())
        return element

class Validity():
    """ Validity is the explicit validity information for a signal

        Attributes
        ----------
            fromLane (int): minimum id of the lanes for which the object is valid

            toLane (int): maximum id of the lanes for which the object is valid

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
                
    """

    def __init__(self, fromLane, toLane):
        """ initalize the Validity

            Parameters
            ----------
                fromLane (int): minimum id of the lanes for which the object is valid

                toLane (int): maximum id of the lanes for which the object is valid

        """
        self.fromLane = fromLane
        self.toLane = toLane

    def __eq__(self, other):
        if isinstance(other,Validity):
            if self.fromLane == other.fromLane and self.toLane == other.toLane:
                return True
        return False

    def get_attributes(self):
        """ returns the attributes of Validity as a dict 

        """
        retdict = {}
        retdict['fromLane'] = str(self.fromLane)
        retdict['toLane'] = str(self.toLane)
        return retdict

    def get_element(self):
        """ returns the elementTree of Validity

        """
        element = ET.Element('validity',attrib=self.get_attributes())

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

    def __eq__(self, other):
        if isinstance(other,Dependency):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self):
        retdict = {"id": str(self.id), "type": str(self.type)}
        return retdict

    def get_element(self):
        element = ET.Element('dependency', attrib=self.get_attributes())
        return element




class Object(_SignalObjectBase):
    """ creates an Object

        Parameters
        ----------
            _SignalObjectBase: base class with common attributes of Signal / Object

        Attributes
        ----------
            s (float): s-coordinate of Object (init in base class)

            t (float): t-coordinate of Object (init in base class)

            type (ObjectType or string): type of Object (typically enum ObjectType) (init in base class)

            subtype (string): subtype for further specification of Object (init in base class)
            
            id (string): id of Object (init in base class)
            
            name (string): name for identification of Object (init in base class)
            
            dynamic (Dynamic): specifies if Object is static or dynamic (init in base class)

            zOffset (float): vertical offset of Object with respect to centerline (init in base class)

            orientation (Orientation): orientation of Object with respect to road (init in base class)
            
            hdg (float): heading angle (rad) of the Object relative to road direction
            
            pitch (float): pitch angle (rad) of Object relative to the inertial system (xy-plane) (init in base class)
            
            roll (float): roll angle (rad) of Object after applying pitch, relative to the inertial system (x’’y’’-plane) (init in base class)            

            width (float): width of the Object (init in base class)

            length (float): width of the Object (shall not be used with radius)

            height (float): height of Object (init in base class)            
            
            radius (float): radius of the Object (shall not be used with width/length)
        
            validLength (float): validLength
            
            _repeats ([dict]): list of dictionary containing attributes for optional subelement for repeating Objects to be filled by repeat method

            validity (Validity): explicit validity information for a signal (optional)
            
        Methods
        -------
            repeat()
                adds a dictionary to _repeats[] list to create a subelement for repeating the Object
                
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of FileHeader

    """
        
    def __init__(self,s,t,Type=ObjectType.none,subtype=None,id=None,name=None,dynamic=Dynamic.no,zOffset=0,orientation=Orientation.none,hdg=0,pitch=0,roll=0,width=None,length=None,height=None,radius=None,validLength=None):
        """ initalizes the Object

        Parameters
        ----------
            s (float): s-coordinate of Object (init in base class)

            t (float): t-coordinate of Object (init in base class)
            
            Type (ObjectType or string): type of Object (typically enum ObjectType) (init in base class)
                Default: ObjectType.none
            subtype (string): subtype for further specification of Object (init in base class)
                Default: None
            id (string): id of Object (init in base class)
                Default: None
            name (string): name for identification of Object (init in base class)
                Default: None 
            dynamic (Dynamic): specifies if Object is static or dynamic (init in base class)
                Default: Dynamic.no                            
            zOffset (float): vertical offset of Object with respect to centerline (init in base class)
                Default: 0                        
            orientation (Orientation): orientation of Object with respect to road (init in base class)
                Default: Orientation.none                                    
            hdg (float): heading angle (rad) of the Object relative to road direction
                Default: 0
            pitch (float): pitch angle (rad) of Object relative to the inertial system (xy-plane) (init in base class)
                Default: 0                                 
            roll (float): roll angle (rad) of Object after applying pitch, relative to the inertial system (x’’y’’-plane) (init in base class)
                Default: 0                                             
            width (float): width of the Object (init in base class)
                Default: None     
            length (float): length of the Object (shall not be used with radius)
                Default: None  
            height (float): height of Object (init in base class)
                Default: None
            radius (float): radius of the Object (shall not be used with width/length)
                Default: None                               
            validLength (float): validity of object along s-coordinate
                Default: None                                             

        """
        #get attributes that are common with signals
        super().__init__(s,t,id,Type,subtype,dynamic,name,zOffset,orientation,pitch,roll,width,height)
                
        #attributes that differ from signals
        self.validLength = validLength
        self.length = length
        self.hdg = hdg
        self.radius = radius
        
        #list for repeat entries
        self._repeats = []

        self.validity = None
    
        #check if width/length combination or radius was provided and ensure working defaults 
        if radius is not None and (width is not None or length is not None):
            print ("Object with id",self.id,"was provided with radius, width and/or length. Provide either radius or width and length. Using radius as fallback.")
            self.width = None
            self.length = None
        elif width is not None and length is None:
            print ("Object with id",self.id,"was provided with width, but length is missing. Using 0 as fallback.")
            self.length = 0
        elif length is not None and width is None:
            print ("Object with id",self.id,"was provided with length, but width is missing. Using 0 as fallback.")
            self.width = 0
        else:
            pass

    def __eq__(self, other):
        if isinstance(other,Object):
            if self.get_attributes() == other.get_attributes() and \
            self._repeats == other._repeats:
                return True
        return False

    def repeat(self,repeatLength,repeatDistance,sStart=None,tStart=None,tEnd=None,heightStart=None,heightEnd=None,zOffsetStart=None,zOffsetEnd=None,widthStart=None,widthEnd=None,lengthStart=None,lengthEnd=None,radiusStart=None,radiusEnd=None):
        
        self._repeats.append({})

        self._repeats[-1]['length']=str(repeatLength)
        self._repeats[-1]['distance']=str(repeatDistance)
        
        def infoFallback(id, attributeName):
            pass
            #print ("Info: Using data of parent object with id",id,"as attribute",attributeName,"was not specified for repeat entry.")
                  
        #ensuring that all attributes that are required according to OpenDRIVE 1.6 are filled - for convenience the ones of the parent object are used
        #if not provided specifically          
        if sStart == None:
            self._repeats[-1]['s']=str(self.s)
            infoFallback(self.id, 's')
        else:
            self._repeats[-1]['s']=str(sStart)           
        if tStart == None:
            self._repeats[-1]['tStart']=str(self.t)
            infoFallback(self.id, 'tStart')
        else:
            self._repeats[-1]['tStart']=str(tStart)
        if tEnd == None:
            self._repeats[-1]['tEnd']=str(self.t)
            infoFallback(self.id, 'tEnd')
        else:
            self._repeats[-1]['tEnd']=str(tEnd)
        if heightStart == None and self.height != None:
            self._repeats[-1]['heightStart']=str(self.height)
            infoFallback(self.id, 'heightStart')
        else:
            self._repeats[-1]['heightStart']=str(heightStart)
        if heightEnd == None and self.height != None:
            self._repeats[-1]['heightEnd']=str(self.height)
            infoFallback(self.id, 'heightEnd')
        else:
            self._repeats[-1]['heightEnd']=str(heightEnd)
        if zOffsetStart == None:
            self._repeats[-1]['zOffsetStart']=str(self.zOffset)
            infoFallback(self.id, 'zOffsetStart')
        else:
            self._repeats[-1]['zOffsetStart']=str(zOffsetStart)
        if zOffsetEnd == None:
            self._repeats[-1]['zOffsetEnd']=str(self.zOffset)
            infoFallback(self.id, 'zOffsetEnd')
        else:
            self._repeats[-1]['zOffsetEnd']=str(zOffsetEnd)
        
        #attributes below are optional according to OpenDRIVE 1.6 - no further checks as these values overrule the ones of parent object
        #and fallbacks might be implemented differently by different simulators
        if widthStart is not None:
             self._repeats[-1]['widthStart']=str(widthStart)
        if widthEnd is not None:
             self._repeats[-1]['widthEnd']=str(widthEnd)
        if lengthStart is not None:
             self._repeats[-1]['lengthStart']=str(lengthStart)
        if lengthEnd is not None:
             self._repeats[-1]['lengthEnd']=str(lengthEnd)
        if radiusStart is not None:
             self._repeats[-1]['radiusStart']=str(radiusStart)
        if radiusEnd is not None:
             self._repeats[-1]['radiusEnd']=str(radiusEnd)   

    def add_validity(self, fromLane, toLane): 
        if self.validity: 
            raise ValueError('only one validity is allowed')
        self.validity = Validity(fromLane, toLane)        
            
    def get_attributes(self):
        """ returns the attributes of the Object as a dict

        """
        retdict = super().get_common_attributes()
        if self.validLength is not None:
            retdict['validLength'] = str(self.validLength)
        retdict['hdg'] = str(self.hdg)
        
        if self.radius is not None:
            retdict['radius'] = str(self.radius)
        elif self.length is not None and self.width is not None:
            retdict['length'] = str(self.length)
            retdict['width'] = str(self.width)
        
        return retdict

    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """
        element = ET.Element('object',attrib=self.get_attributes())
        for _repeat in self._repeats:
            ET.SubElement(element,'repeat', attrib=_repeat)
        if self.validity: 
            element.append(self.validity.get_element())

        return element
    
