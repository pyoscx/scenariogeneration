"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
XMLNS = "http://www.w3.org/2001/XMLSchema-instance"
XSI = "OpenScenario.xsd"

from .exceptions import OpenSCENARIOVersionError
from os import error

_MINOR_VERSION = 1


class VersionBase:
    """base class for checking different versions of OpenSCENARIO"""

    version_major = 1
    version_minor = _MINOR_VERSION

    def isVersion(self, major=1, minor=1):
        return major >= self.version_major and minor >= self.version_minor

    def setVersion(self, major=1, minor=0):
        VersionBase.version_major = major
        VersionBase.version_minor = minor


class _OscEnum(VersionBase):
    """custom "enum" class to be able to handle different versions of the enums in OpenSCENARIO

    Parameters
    ----------
        name (str): enum name

        classname (str): name of the enum class (only used for printouts to help debugging)

        min_minor_version (int): how the relative distance should be calculated
            Default: 0

        max_minor_version (int): the max "minor version" where the enum is valid
            Default: Current Supported Version

    Attributes
    ----------
        name (str): enum name

        classname (str): name of the enum class (only used for printouts to help debugging)

        min_minor_version (int): how the relative distance should be calculated

        max_minor_version (int): the max "minor version" where the enum is valid

    Methods
    -------
        get_name()
            Returns the correct string of the Enum, will take care of versions

    """

    def __init__(
        self, classname, name, min_minor_version=0, max_minor_version=_MINOR_VERSION
    ):
        """initalize the _OscEnum

        Parameters
        ----------
            name (str): enum name

            classname (str): name of the enum class (only used for printouts to help debugging)

            min_minor_version (int): how the relative distance should be calculated
                Default: 0

            max_minor_version (int): the max "minor version" where the enum is valid
                Default: Current Supported Version
        """

        self.name = name
        self.classname = classname
        self.min_minor_version = min_minor_version
        self.max_minor_version = max_minor_version

    def __eq__(self, other):
        if isinstance(other, _OscEnum):
            if self.name == other.name and self.classname == other.classname:
                return True
        return False

    def get_name(self):
        """method that should be used when using the _OscEnum to get the string, will check version of the enum to see if it is used correctly with the used version

        Returns
        -------
        name (str)
        """

        if self.min_minor_version > self.version_minor:
            raise OpenSCENARIOVersionError(
                self.classname
                + "."
                + self.name
                + " is not part of OpenSCENARIO V"
                + str(self.version_major)
                + "."
                + str(self.version_minor)
                + ", was introduced in V"
                + str(self.version_major)
                + "."
                + str(self.min_minor_version)
            )
        elif self.max_minor_version < self.version_minor:
            raise OpenSCENARIOVersionError(
                self.classname
                + "."
                + self.name
                + " is not part of OpenSCENARIO V"
                + str(self.version_major)
                + "."
                + str(self.version_minor)
                + ", was deprecated in V"
                + str(self.version_major)
                + "."
                + str(self.max_minor_version)
            )
        return self.name

    def __str__(self):
        return self.name


class CloudState:
    """Enum for CloudState"""

    skyOff = _OscEnum("CloudState", "skyOff")
    free = _OscEnum("CloudState", "free")
    cloudy = _OscEnum("CloudState", "cloudy")
    overcast = _OscEnum("CloudState", "overcast")
    rainy = _OscEnum("CloudState", "rainy")


class ConditionEdge:
    """Enum for ConditionEdge"""

    rising = _OscEnum("ConditionEdge", "rising")
    falling = _OscEnum("ConditionEdge", "falling")
    risingOrFalling = _OscEnum("ConditionEdge", "risingOrFalling")
    none = _OscEnum("ConditionEdge", "none")


class DynamicsDimension:
    """Enum for DynamicsDimension"""

    rate = _OscEnum("DynamicsDimension", "rate")
    time = _OscEnum("DynamicsDimension", "time")
    distance = _OscEnum("DynamicsDimension", "distance")


class DynamicsShapes:
    """Enum for DynamicsShapes"""

    linear = _OscEnum("DynamicsShapes", "linear")
    cubic = _OscEnum("DynamicsShapes", "cubic")
    sinusoidal = _OscEnum("DynamicsShapes", "sinusoidal")
    step = _OscEnum("DynamicsShapes", "step")


class FollowMode:
    """Enum for FollowMode"""

    position = _OscEnum("FollowMode", "position")
    follow = _OscEnum("FollowMode", "follow")


class MiscObjectCategory:
    """Enum for MiscObjectCategory"""

    none = _OscEnum("MiscObjectCategory", "none")
    obstacle = _OscEnum("MiscObjectCategory", "obstacle")
    pole = _OscEnum("MiscObjectCategory", "pole")
    tree = _OscEnum("MiscObjectCategory", "tree")
    vegetation = _OscEnum("MiscObjectCategory", "vegetation")
    barrier = _OscEnum("MiscObjectCategory", "barrier")
    building = _OscEnum("MiscObjectCategory", "building")
    parkingSpace = _OscEnum("MiscObjectCategory", "parkingSpace")
    patch = _OscEnum("MiscObjectCategory", "patch")
    railing = _OscEnum("MiscObjectCategory", "railing")
    grafficIsland = _OscEnum("MiscObjectCategory", "grafficIsland")
    crosswalk = _OscEnum("MiscObjectCategory", "crosswalk")
    streetLamp = _OscEnum("MiscObjectCategory", "streetLamp")
    gantry = _OscEnum("MiscObjectCategory", "gantry")
    soundBarrier = _OscEnum("MiscObjectCategory", "soundBarrier")
    wind = _OscEnum("MiscObjectCategory", "wind", max_minor_version=0)
    roadMark = _OscEnum("MiscObjectCategory", "roadMark")


class ObjectType:
    """Enum for ObjectType"""

    pedestrian = _OscEnum("ObjectType", "pedestrian")
    vehicle = _OscEnum("ObjectType", "vehicle")
    miscellaneous = _OscEnum("ObjectType", "miscellaneous")
    external = _OscEnum("ObjectType", "external", min_minor_version=1)


class ParameterType:
    """Enum for ParameterType"""

    integer = _OscEnum("ParameterType", "integer")
    double = _OscEnum("ParameterType", "double")
    string = _OscEnum("ParameterType", "string")
    unsighedInt = _OscEnum("ParameterType", "unsighedInt")
    unsighedShort = _OscEnum("ParameterType", "unsighedShort")
    boolean = _OscEnum("ParameterType", "boolean")
    dateTime = _OscEnum("ParameterType", "dateTime")


class PedestrianCategory:
    """Enum for PedestrianCategory"""

    pedestrian = _OscEnum("PedestrianCategory", "pedestrian")
    wheelchair = _OscEnum("PedestrianCategory", "wheelchair")
    animal = _OscEnum("PedestrianCategory", "animal")


class PrecipitationType:
    """Enum for PercipitationType"""

    dry = _OscEnum("PrecipitationType", "dry")
    rain = _OscEnum("PrecipitationType", "rain")
    snow = _OscEnum("PrecipitationType", "snow")


class Priority:
    """Enum for Priority"""

    overwrite = _OscEnum("Priority", "overwrite")
    skip = _OscEnum("Priority", "skip")
    parallel = _OscEnum("Priority", "parallel")


class ReferenceContext:
    """Enum for ReferenceContext"""

    relative = _OscEnum("ReferenceContext", "relative")
    absolute = _OscEnum("ReferenceContext", "absolute")


class RelativeDistanceType:
    """Enum for RelativeDistanceType"""

    longitudinal = _OscEnum("RelativeDistanceType", "longitudinal")
    lateral = _OscEnum("RelativeDistanceType", "lateral")
    cartesianDistance = _OscEnum(
        "RelativeDistanceType", "cartesianDistance", max_minor_version=0
    )
    euclidianDistance = _OscEnum(
        "RelativeDistanceType", "euclidianDistance", min_minor_version=1
    )


class RouteStrategy:
    """Enum for RouteStrategy"""

    fastest = _OscEnum("RouteStrategy", "fastest")
    shortest = _OscEnum("RouteStrategy", "shortest")
    leastIntersections = _OscEnum("RouteStrategy", "leastIntersections")
    random = _OscEnum("RouteStrategy", "random")


class Rule:
    """Enum for Rule"""

    greaterThan = _OscEnum("Rule", "greaterThan")
    lessThan = _OscEnum("Rule", "lessThan")
    equalTo = _OscEnum("Rule", "equalTo")
    greaterOrEqual = _OscEnum("Rule", "greaterOrEqual", min_minor_version=1)
    lessOrEqual = _OscEnum("Rule", "lessOrEqual", min_minor_version=1)
    notEqualTo = _OscEnum("Rule", "notEqualTo", min_minor_version=1)


class SpeedTargetValueType:
    """Enum for SpeedTargetValueType"""

    delta = _OscEnum("SpeedTargetValueType", "delta")
    factor = _OscEnum("SpeedTargetValueType", "factor")


class StoryboardElementState:
    """Enum for StoryboardElementState"""

    startTransition = _OscEnum("StoryboardElementState", "startTransition")
    endTransition = _OscEnum("StoryboardElementState", "endTransition")
    stopTransition = _OscEnum("StoryboardElementState", "stopTransition")
    skipTransition = _OscEnum("StoryboardElementState", "skipTransition")
    completeState = _OscEnum("StoryboardElementState", "completeState")
    runningState = _OscEnum("StoryboardElementState", "runningState")
    standbyState = _OscEnum("StoryboardElementState", "standbyState")


class StoryboardElementType:
    """Enum for StoryboardElementType"""

    story = _OscEnum("StoryboardElementType", "story")
    act = _OscEnum("StoryboardElementType", "act")
    maneuver = _OscEnum("StoryboardElementType", "maneuver")
    event = _OscEnum("StoryboardElementType", "event")
    action = _OscEnum("StoryboardElementType", "action")
    maneuverGroup = _OscEnum("StoryboardElementType", "maneuverGroup")


class TriggeringEntitiesRule:
    """Enum for TriggeringEntitiesRule"""

    any = _OscEnum("TriggeringEntitiesRule", "any")
    all = _OscEnum("TriggeringEntitiesRule", "all")


class VehicleCategory:
    """Enum for VehicleCategory"""

    car = _OscEnum("VehicleCategory", "car")
    van = _OscEnum("VehicleCategory", "van")
    truck = _OscEnum("VehicleCategory", "truck")
    trailer = _OscEnum("VehicleCategory", "trailer")
    semitrailer = _OscEnum("VehicleCategory", "semitrailer")
    bus = _OscEnum("VehicleCategory", "bus")
    motorbike = _OscEnum("VehicleCategory", "motorbike")
    bicycle = _OscEnum("VehicleCategory", "bicycle")
    train = _OscEnum("VehicleCategory", "train")
    tram = _OscEnum("VehicleCategory", "tram")


class CoordinateSystem:
    """Enum for CoordinateSystem"""

    entity = _OscEnum("CoordinateSystem", "entity", min_minor_version=1)
    lane = _OscEnum("CoordinateSystem", "lane", min_minor_version=1)
    road = _OscEnum("CoordinateSystem", "road", min_minor_version=1)
    trajectory = _OscEnum("CoordinateSystem", "trajectory", min_minor_version=1)


class LateralDisplacement:
    any = _OscEnum("LateralDisplacement", "any", min_minor_version=1)
    leftToReferencedEntity = _OscEnum(
        "LateralDisplacement", "leftToReferencedEntity", min_minor_version=1
    )
    rightToReferencedEntity = _OscEnum(
        "LateralDisplacement", "rightToReferencedEntity", min_minor_version=1
    )


class LongitudinalDisplacement:
    any = _OscEnum("LongitudinalDisplacement", "any", min_minor_version=1)
    trailingReferencedEntity = _OscEnum(
        "LongitudinalDisplacement", "trailingReferencedEntity", min_minor_version=1
    )
    leadingReferencedEntity = _OscEnum(
        "LongitudinalDisplacement", "leadingReferencedEntity", min_minor_version=1
    )
