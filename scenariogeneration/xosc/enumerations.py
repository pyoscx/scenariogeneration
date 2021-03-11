""" Collection of the enumerations defined in OpenSCENARIO, and used in the xosc module

"""
XMLNS = 'http://www.w3.org/2001/XMLSchema-instance'
XSI = 'OpenSccenario.xsd'

from enum import Enum, auto

class CloudState(Enum):
    """ Enum for CloudState
    """
    skyOff = auto()
    free = auto()
    cloudy = auto()
    overcast = auto()
    rainy = auto()

class ConditionEdge(Enum):
    """ Enum for ConditionEdge
    """
    rising = auto()
    falling = auto()
    risingOrFalling = auto()
    none = auto()

class DynamicsDimension(Enum):
    """ Enum for DynamicsDimension
    """
    rate = auto()
    time = auto()
    distance = auto()

class DynamicsShapes(Enum):
    """ Enum for DynamicsShapes
    """
    linear = auto()
    cubic = auto() 
    sinusoidal = auto()
    step = auto()

class FollowMode(Enum):
    """ Enum for FollowMode
    """
    position = auto()
    follow = auto()

class MiscObjectCategory(Enum):
    """ Enum for MiscObjectCategory
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
    grafficIsland = auto()
    crosswalk = auto()
    streetLamp = auto()
    gantry = auto()
    soundBarrier = auto()
    wind = auto()
    roadMark = auto()

class ObjectType(Enum):
    """ Enum for ObjectType
    """
    pedestrian = auto()
    vehicle = auto()
    miscellaneous = auto()

class ParameterType(Enum):
    """ Enum for ParameterType
    """
    integer = auto()
    double = auto()
    string = auto()
    unsighedInt = auto()
    unsighedShort = auto()
    boolean = auto()
    dateTime = auto()

class PedestrianCategory(Enum):
    """ Enum for PedestrianCategory
    """
    pedestrian = auto()
    wheelchair = auto()
    animal = auto()

class PrecipitationType(Enum):
    """ Enum for PercipitationType
    """
    dry = auto()
    rain = auto()
    snow = auto()

class Priority(Enum):
    """ Enum for Priority
    """
    overwrite = auto()
    skip = auto()
    parallel = auto()

class ReferenceContext(Enum):
    """ Enum for ReferenceContext
    """
    relative = auto()
    absolute = auto()

class RelativeDistanceType(Enum):
    """ Enum for RelativeDistanceType
    """
    longitudinal = auto()
    lateral = auto()
    cartesianDistance = auto()

class RouteStrategy(Enum):
    """ Enum for RouteStrategy
    """
    fastest = auto()
    shortest = auto()
    leastIntersections = auto()
    random = auto()

class Rule(Enum):
    """ Enum for Rule
    """
    greaterThan = auto()
    lessThan = auto()
    equalTo = auto()

class SpeedTargetValueType(Enum):
    """ Enum for SpeedTargetValueType
    """
    delta = auto()
    factor = auto()

class StoryboardElementState(Enum):
    """ Enum for StoryboardElementState
    """
    startTransition = auto()
    endTransition = auto()
    stopTransition = auto()
    skipTransition = auto()
    completeState = auto()
    runningState = auto()
    standbyState = auto()

class StoryboardElementType(Enum):
    """ Enum for StoryboardElementType
    """
    story = auto()
    act = auto()
    maneuver = auto()
    event = auto()
    action = auto()
    maneuverGroup = auto()

class TriggeringEntitiesRule(Enum):
    """ Enum for TriggeringEntitiesRule
    """
    any = auto()
    all = auto()

class VehicleCategory(Enum):
    """ Enum for VehicleCategory
    """
    car = auto()
    van = auto()
    truck = auto()
    trailer = auto()
    semitrailer = auto()
    bus = auto()
    motorbike = auto()
    bicycle = auto()
    train = auto()
    tram = auto()

