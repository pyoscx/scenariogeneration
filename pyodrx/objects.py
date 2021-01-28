import xml.etree.ElementTree as ET
from .helpers import enum2str
from .enumerations import ObjectType, Orientation, Dynamic 


class Object():
    """ creates an Object

        Parameters
        ----------
            marking_type (RoadMarkType): the type of marking

            width (float): with of the line

            length (float): length of the line
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

            color (RoadMarkColor): color of line (optional)

        Attributes
        ----------
            marking_type (str): the type of marking

            width (float): with of the line

            length (float): length of the line
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

            color (RoadMarkColor): color of line (optional)

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of FileHeader

            add_roadmark(roadmark)
                adds a new roadmark to the lane

    """
    def __init__(self,s,t,height,object_id,dynamic=Dynamic.no,name='defaultName',zOffset=0,Type=ObjectType.none,subtype=None,validLength=0,orientation=Orientation.none,hdg=0,pitch=0,roll=0,width=None,length=None,radius=None):
        """ initalizes the Object

        Parameters
        ----------
            marking_type (str): the type of marking

            width (float): with of the line

            length (float): length of the line
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

            color (RoadMarkColor): color of line
                Default: 'standard'

        """ 
        self.s = s
        self.t = t
        self.height = height
        self.object_id = object_id
        
        self.dynamic = dynamic
        self.name = name
        self.zOffset = zOffset
        self.Type = Type
        self.subtype = subtype
        self.validLength = validLength
        self.orientation = orientation
        self.hdg = hdg
        self.pitch = pitch
        self.roll = roll
        self.width = width
        self.length = length
        self.radius = radius
        
        self._repeats = []
        
        
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
        
        #ensuring that all attributes that are required according to OpenDRIVE 1.6 are filled - for convenience the ones of the parent object are used
        #if not provided specifically  
        
        if sStart == None:
            self._repeats[-1]['s']=str(self.s)
            print ("Info: no s-coordinate specified for repeating object with id",self.object_id ,", using s-coordinate of original object instead.")
        else:
            self._repeats[-1]['s']=str(sStart)           
        if tStart == None:
            self._repeats[-1]['tStart']=str(self.t)
            print ("Info: no starting t-coordinate specified for repeating object with id",self.object_id ,", using t-coordinate of original object instead.")
        else:
            self._repeats[-1]['tStart']=str(tStart)
        if tEnd == None:
            self._repeats[-1]['tEnd']=str(self.t)
            print ("Info: no ending t-coordinate specified for repeating object with id",self.object_id ,", using t-coordinate of original object instead.")
        else:
            self._repeats[-1]['tEnd']=str(tEnd)
        if heightStart == None:
            self._repeats[-1]['heightStart']=str(self.height)
            print ("Info: no starting height specified for repeating object with id",self.object_id ,", using height of original object instead.")
        else:
            self._repeats[-1]['heightStart']=str(heightStart)
        if heightEnd == None:
            self._repeats[-1]['heightEnd']=str(self.height)
            print ("Info: no ending height specified for repeating object with id",self.object_id ,", using height of original object instead.")
        else:
            self._repeats[-1]['heightEnd']=str(heightEnd)
        if zOffsetStart == None:
            self._repeats[-1]['zOffsetStart']=str(self.zOffset)
            print ("Info: no starting zOffset specified for repeating object with id",self.object_id ,", using zOffset of original object instead.")
        else:
            self._repeats[-1]['zOffsetStart']=str(zOffsetStart)
        if zOffsetEnd == None:
            self._repeats[-1]['zOffsetEnd']=str(self.zOffset)
            print ("Info: no ending zOffset specified for repeating object with id",self.object_id ,", using zOffset of original object instead.")
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
        retdict = {}
        retdict['type'] = enum2str(self.Type)
        retdict['id'] = str(self.object_id)
        retdict['s'] = str(self.s)
        retdict['t'] = str(self.t)
        retdict['height'] = str(self.height)
        retdict['subtype'] = str(self.subtype)
        retdict['dynamic'] = enum2str(self.dynamic)
        retdict['name'] = str(self.name)
        retdict['zOffset'] = str(self.zOffset)
        retdict['validLength'] = str(self.validLength)
        retdict['hdg'] = str(self.hdg)        
        retdict['pitch'] = str(self.pitch)
        retdict['roll'] = str(self.roll)
        
        if self.orientation == Orientation.positive:
            retdict['orientation'] = '+'    
        elif self.orientation == Orientation.negative:
            retdict['orientation'] = '-'        
        else:
            retdict['orientation'] = enum2str(self.orientation)    
        
        if self.radius is not None:
            retdict['radius'] = str(self.radius)                    
        else:
            retdict['width'] = str(self.width)
            retdict['length'] = str(self.length)
        
        return retdict

    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """
        element = ET.Element('object',attrib=self.get_attributes())
        for _repeat in self._repeats:
            ET.SubElement(element,'repeat', attrib=_repeat)

        return element
    
#TODO Adjust all comments
#TODO Allow repeated
#TODO Generate tests
