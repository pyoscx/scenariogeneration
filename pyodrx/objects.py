import xml.etree.ElementTree as ET
from .helpers import enum2str
from .enumerations import ObjectType, Orientation, Dynamic 

class _SignalObjectCommon():
    """ creates a common basis for Signal and Object shall not be instantiated directly

        Attributes
        ----------
            s (float): s-coordinate of Signal / Object

            t (float): t-coordinate of Signal / Object

            height (float): height of Signal / Object

            object_id (string): id of Signal / Object

            type (ObjectType or string): type of the Signal (typically string) / Object (typically enum ObjectType)

            subtype (string): subtype for further specification of Signal / Object

            dynamic (Dynamic): specifies if Signal / Object is static (road sign) or dynamic (traffic light)
            
            name (string): name for identification of Signal / Object
            
            zOffset (float): vertical offset of Signal / Object with respect to centerline
            
            orientation (Orientation): orientation of Signal / Object with respect to road
            
            pitch (float): pitch angle (rad) of Signal / Object relative to the inertial system (xy-plane)
            
            roll (float): roll angle (rad) of Signal / Object after applying pitch, relative to the inertial system (x’’y’’-plane) 
            
            width (float): width of the Signal / Object


        Methods
        -------
            get_common_attributes()
                Returns a dictionary of all attributes of FileHeader
        """
        
    def __init__(self,s,t,height,object_id,Type,subtype,dynamic,name,zOffset,orientation,pitch,roll,width):
        """ initalizes common attributes for Signal and Object

        Parameters
        ----------
            s (float): s-coordinate of Signal / Object

            t (float): t-coordinate of Signal / Object

            height (float): height of Signal / Object

            object_id (string): id of Signal / Object

            type (ObjectType or string): type of the Signal (typically string) / Object (typically enum ObjectType)

            subtype (string): subtype for further specification of Signal / Object

            dynamic (Dynamic): specifies if Signal / Object is static (road sign) or dynamic (traffic light)
            
            name (string): name for identification of Signal / Object
            
            zOffset (float): vertical offset of Signal / Object with respect to centerline
            
            orientation (Orientation): orientation of Signal / Object with respect to road
            
            pitch (float): pitch angle (rad) of Signal / Object relative to the inertial system (xy-plane)
            
            roll (float): roll angle (rad) of Signal / Object after applying pitch, relative to the inertial system (x’’y’’-plane)
            
            width (float): width of the Signal / Object

        """ 
        self.s = s
        self.t = t
        self.height = height
        self.object_id = object_id
        self.Type = Type
        
        self.dynamic = dynamic
        self.name = name
        self.zOffset = zOffset
        self.subtype = subtype
        self.orientation = orientation
        self.pitch = pitch
        self.roll = roll
        self.width = width
        

        
    def get_common_attributes(self):
            """ returns common attributes of Signal and Object as a dict
    
            """
            retdict = {}
            retdict['id'] = str(self.object_id)
            retdict['s'] = str(self.s)
            retdict['t'] = str(self.t)
            retdict['height'] = str(self.height)
            retdict['subtype'] = str(self.subtype)
            retdict['dynamic'] = enum2str(self.dynamic)
            retdict['name'] = str(self.name)
            retdict['zOffset'] = str(self.zOffset)
            retdict['pitch'] = str(self.pitch)
            retdict['roll'] = str(self.roll)
            retdict['width'] = str(self.width)            
            
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

class Object(_SignalObjectCommon):
    """ creates an Object

        Parameters
        ----------
            _SignalObjectCommon: super-class with common attributes of Signal / Object

        Attributes
        ----------
            s (float): s-coordinate of Object (init in super-class)

            t (float): t-coordinate of Object (init in super-class)

            height (float): height of Object (init in super-class)

            object_id (string): id of Object (init in super-class)

            type (ObjectType or string): type of Object (typically enum ObjectType) (init in super-class)

            subtype (string): subtype for further specification of Object (init in super-class)

            dynamic (Dynamic): specifies if Object is static or dynamic (init in super-class)
            
            name (string): name for identification of Object (init in super-class)
            
            zOffset (float): vertical offset of Object with respect to centerline (init in super-class)
            
            orientation (Orientation): orientation of Object with respect to road (init in super-class)
            
            pitch (float): pitch angle (rad) of Object relative to the inertial system (xy-plane) (init in super-class)
            
            roll (float): roll angle (rad) of Object after applying pitch, relative to the inertial system (x’’y’’-plane) (init in super-class)
            
            width (float): width of the Object (init in super-class)
        
            validLength (float): validLength
            
            length (float): width of the Object (shall not be used with radius)
            
            hdg (float): heading angle (rad) of the Object relative to road direction
            
            radius (float): radius of the Object (shall not be used with width/length)
            
            _repeats ([dict]): list of dictionary containing attributes for optional subelement for repeating Objects to be filled by repeat method
            
            _usedIDs ([str]): list of used IDs shared among all instances of Object to throw warning when ID is not unique 

        Methods
        -------
            repeat()
                adds a dictionary to _repeats[] list to create a subelement for repeating the Object
                
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of FileHeader

    """
    
    _usedIDs = []
    
    def __init__(self,s,t,height,object_id,dynamic=Dynamic.no,name='defaultName',zOffset=0,Type=ObjectType.none,subtype=None,validLength=0,orientation=Orientation.none,hdg=0,pitch=0,roll=0,width=None,length=None,radius=None):
        """ initalizes the Object

        Parameters
        ----------
            s (float): s-coordinate of Object (init in super-class)

            t (float): t-coordinate of Object (init in super-class)

            height (float): height of Object (init in super-class)

            object_id (string): id of Object (init in super-class)

            type (ObjectType or string): type of Object (typically enum ObjectType) (init in super-class)
                Default: ObjectType.none
            subtype (string): subtype for further specification of Object (init in super-class)
                Default: None
            dynamic (Dynamic): specifies if Object is static or dynamic (init in super-class)
                Default: Dynamic.no            
            name (string): name for identification of Object (init in super-class)
                Default: 'defaultName'                   
            zOffset (float): vertical offset of Object with respect to centerline (init in super-class)
                Default: 0                        
            orientation (Orientation): orientation of Object with respect to road (init in super-class)
                Default: Orientation.none                                    
            pitch (float): pitch angle (rad) of Object relative to the inertial system (xy-plane) (init in super-class)
                Default: 0                                 
            roll (float): roll angle (rad) of Object after applying pitch, relative to the inertial system (x’’y’’-plane) (init in super-class)
                Default: 0                                             
            width (float): width of the Object (init in super-class)
                Default: None                                         
            validLength (float): validLength
                Default: 0                                             
            length (float): width of the Object (shall not be used with radius)
                Default: None                                            
            hdg (float): heading angle (rad) of the Object relative to road direction
                Default: 0
            radius (float): radius of the Object (shall not be used with width/length)
                Default: None

        """
        #get attributes that are common with signals
        super().__init__(s,t,height,object_id,Type,subtype,dynamic,name,zOffset,orientation,pitch,roll,width)
                
        #attributes that differ from signals
        self.validLength = validLength
        self.length = length
        self.hdg = hdg
        self.radius = radius
        
        #list for repeat entries
        self._repeats = []
        
        if self.object_id in self._usedIDs:
            print ("Warning: id",self.object_id,"has already been used for another object and is not unique.")
        self._usedIDs.append(object_id)
    
        #check if width/length combination or radius was provided and ensure working defaults 
        if radius is not None and (width is not None or length is not None):
            print ("Object with id",self.object_id,"was provided with radius, width and/or length. Provide either radius or width and length. Using radius as fallback.")
            self.width = None
            self.length = None
        elif width is not None and length is None:
            print ("Object with id",self.object_id,"was provided with width, but length is missing. Using 0 as fallback.")
            self.length = 0
        elif length is not None and width is None:
            print ("Object with id",self.object_id,"was provided with length, but width is missing. Using 0 as fallback.")
            self.width = 0
        elif radius is None and width is None and length is None:
            print ("Object with id",self.object_id,"was provided with no radius, width or length. Provide either radius or width and length. Using radius=0 as fallback.")
            self.radius = 0
        else:
            pass
        
    def repeat(self,repeatLength,repeatDistance,sStart=None,tStart=None,tEnd=None,heightStart=None,heightEnd=None,zOffsetStart=None,zOffsetEnd=None,widthStart=None,widthEnd=None,lengthStart=None,lengthEnd=None,radiusStart=None,radiusEnd=None):
        
        self._repeats.append({})

        self._repeats[-1]['length']=str(repeatLength)
        self._repeats[-1]['distance']=str(repeatDistance)
        
        def infoFallback(object_id, attributeName):
            print ("Info: Using data of parent object with id",object_id,"as attribute",attributeName,"was not specified for repeat entry.")
                  
        #ensuring that all attributes that are required according to OpenDRIVE 1.6 are filled - for convenience the ones of the parent object are used
        #if not provided specifically          
        if sStart == None:
            self._repeats[-1]['s']=str(self.s)
            infoFallback(self.object_id, 's')
        else:
            self._repeats[-1]['s']=str(sStart)           
        if tStart == None:
            self._repeats[-1]['tStart']=str(self.t)
            infoFallback(self.object_id, 'tStart')
        else:
            self._repeats[-1]['tStart']=str(tStart)
        if tEnd == None:
            self._repeats[-1]['tEnd']=str(self.t)
            infoFallback(self.object_id, 'tEnd')
        else:
            self._repeats[-1]['tEnd']=str(tEnd)
        if heightStart == None:
            self._repeats[-1]['heightStart']=str(self.height)
            infoFallback(self.object_id, 'heightStart')
        else:
            self._repeats[-1]['heightStart']=str(heightStart)
        if heightEnd == None:
            self._repeats[-1]['heightEnd']=str(self.height)
            infoFallback(self.object_id, 'heightEnd')
        else:
            self._repeats[-1]['heightEnd']=str(heightEnd)
        if zOffsetStart == None:
            self._repeats[-1]['zOffsetStart']=str(self.zOffset)
            infoFallback(self.object_id, 'zOffsetStart')
        else:
            self._repeats[-1]['zOffsetStart']=str(zOffsetStart)
        if zOffsetEnd == None:
            self._repeats[-1]['zOffsetEnd']=str(self.zOffset)
            infoFallback(self.object_id, 'zOffsetEnd')
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
            
    def get_attributes(self):
        """ returns the attributes of the Object as a dict

        """
        retdict = super().get_common_attributes()
        retdict['type'] = enum2str(self.Type)
        retdict['validLength'] = str(self.validLength)
        retdict['hdg'] = str(self.hdg)        
            
        
        if self.radius is not None:
            retdict['radius'] = str(self.radius)
            #remove width entry that comes per default from super-class      
            retdict.pop('width')               
        else:
            retdict['length'] = str(self.length)
        
        return retdict

    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """
        element = ET.Element('object',attrib=self.get_attributes())
        for _repeat in self._repeats:
            ET.SubElement(element,'repeat', attrib=_repeat)

        return element
    
#TODO Adapt examples
