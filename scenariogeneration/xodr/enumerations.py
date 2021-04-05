""" the enumerations module contains the enumerations of OpenDRIVE

"""
from enum import Enum, auto



class MarkRule(Enum):
    """ Enum for MarkRule
    """
    no_passing = auto()
    caution = auto()
    none = auto()
    
class LaneType(Enum):
    """ Enum for LaneType
    """
    none = auto()
    driving = auto()
    stop = auto()
    shoulder = auto()
    biking = auto()
    sidewalk = auto()
    border = auto()
    restricted = auto()
    parking = auto()
    bidirectional = auto()
    median = auto()
    special1 = auto()
    special2 = auto()
    special3 = auto()
    roadWorks = auto()
    tram = auto()
    rail = auto()
    entry = auto()
    exit = auto()
    offRamp = auto()
    onRamp = auto()
    connectingRamp = auto()
    bus = auto()
    taxi = auto()
    HOV = auto()
    mwyEntry = auto()
    mwyExit = auto()

class RoadMarkColor(Enum):
    """ Enum for RoadMarkColor
    """
    standard = auto()
    blue = auto()
    green = auto()
    red = auto()
    white = auto()
    yellow = auto()
    orange = auto()



class RoadMarkWeight(Enum):
    """ Enum for RoadMarkWeight
    """
    standard = auto()
    bold = auto()

class RoadMarkType(Enum):
    """ Enum for RoadMarkType
    """
    none = auto()
    solid = auto()
    broken = auto()
    solid_solid = auto()
    solid_broken = auto()
    broken_solid = auto()
    broken_broken = auto()
    botts_dots = auto()
    grass = auto()
    curb = auto()
    custom = auto()
    edge = auto()

class RoadType(Enum):
    """ Enum for RoadType
    """
    unknown = auto()
    rural = auto()
    motorway = auto()
    town = auto()
    lowSpeed = auto()
    pedestrian = auto()
    bicycle = auto()
    townExpressway = auto()
    townCollector = auto()
    townArterial = auto()
    townPrivate = auto()
    townLocal = auto()
    townPlayStreet = auto()


class LaneChange(Enum):
    """ Enum for LaneChange
    """
    increase = auto()
    decrease = auto()
    both = auto()
    none = auto()    

class ElementType(Enum):
    """ Enum for LaneChange
    """
    road = auto()
    junction = auto()

class ContactPoint(Enum):
    """ Enum for ContactPoint
    """
    start = auto()
    end = auto()

class Direction(Enum):
    """ Enum for Direction
    """
    same = auto()
    opposite = auto()
    
class Orientation(Enum):
    """ Enum for Orientation
    """
    positive = auto()
    negative = auto()
    none = auto()

class ObjectType(Enum):
    """ Enum for ObjectType taken from OpenDRIVE 1.6 without deprecated types
    """
    none = auto()
    obstacle = auto()
    pole = auto()
    tree = auto()
    vegetation = auto()
    barrier = auto()
    building = auto()
    parkingSpace = auto()
    patch = auto()
    railing = auto()
    trafficIsland = auto()
    crosswalk = auto()
    streetLamp = auto()
    gantry = auto()
    soundBarrier = auto()
    roadMark = auto()
    
class Dynamic(Enum):
    """ Enum for Dynamic
    """
    yes = auto()
    no = auto()
    
class RoadSide(Enum):
    """ Enum for RoadSide
    """
    both = auto()
    left = auto()
    right = auto()

class JunctionGroupType(Enum):
    """ Enum for JunctionGroup
    """
    roundabout = auto()
    unknown = auto()