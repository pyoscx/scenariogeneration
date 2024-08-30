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

import re
from .exceptions import OpenSCENARIOVersionError
from os import error
import warnings

_MINOR_VERSION = 2


class VersionBase:
    """base class for checking different versions of OpenSCENARIO"""

    version_major = 1
    version_minor = _MINOR_VERSION

    def isVersion(self, major=1, minor=_MINOR_VERSION):
        return major == self.version_major and minor == self.version_minor

    def isVersionEqLess(self, major=1, minor=_MINOR_VERSION):
        return major >= self.version_major and minor >= self.version_minor

    def isVersionEqLarger(self, major=1, minor=_MINOR_VERSION):
        return major <= self.version_major and minor <= self.version_minor

    def setVersion(self, major=1, minor=_MINOR_VERSION):
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
        self,
        classname,
        name,
        min_minor_version=0,
        max_minor_version=_MINOR_VERSION,
        replacement=None,
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

            replacement (str): can be used is the enum has been replaced to make transitions go easier
        """

        self.name = name
        self.classname = classname
        self.min_minor_version = min_minor_version
        self.max_minor_version = max_minor_version
        self.replacement = replacement

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
            if self.replacement:
                warnings.warn(
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
                    + " and replaced with: "
                    + self.replacement
                )
                return self.name

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


class _EnumMeta(type):
    """This class is used to add functionality to the Enum classes in the xosc module
    Note: this class should only be inherited

    """

    def __getitem__(self, name):
        return self.__dict__[name]


class CloudState(metaclass=_EnumMeta):
    """Enum for CloudState"""

    skyOff = _OscEnum("CloudState", "skyOff")
    free = _OscEnum("CloudState", "free")
    cloudy = _OscEnum("CloudState", "cloudy")
    overcast = _OscEnum("CloudState", "overcast")
    rainy = _OscEnum("CloudState", "rainy")


class ConditionEdge(metaclass=_EnumMeta):
    """Enum for ConditionEdge"""

    rising = _OscEnum("ConditionEdge", "rising")
    falling = _OscEnum("ConditionEdge", "falling")
    risingOrFalling = _OscEnum("ConditionEdge", "risingOrFalling")
    none = _OscEnum("ConditionEdge", "none")


class DynamicsDimension(metaclass=_EnumMeta):
    """Enum for DynamicsDimension"""

    rate = _OscEnum("DynamicsDimension", "rate")
    time = _OscEnum("DynamicsDimension", "time")
    distance = _OscEnum("DynamicsDimension", "distance")


class DynamicsShapes(metaclass=_EnumMeta):
    """Enum for DynamicsShapes"""

    linear = _OscEnum("DynamicsShapes", "linear")
    cubic = _OscEnum("DynamicsShapes", "cubic")
    sinusoidal = _OscEnum("DynamicsShapes", "sinusoidal")
    step = _OscEnum("DynamicsShapes", "step")


class FollowingMode(metaclass=_EnumMeta):
    """Enum for FollowingMode"""

    position = _OscEnum("FollowingMode", "position")
    follow = _OscEnum("FollowingMode", "follow")


class MiscObjectCategory(metaclass=_EnumMeta):
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


class ObjectType(metaclass=_EnumMeta):
    """Enum for ObjectType"""

    pedestrian = _OscEnum("ObjectType", "pedestrian")
    vehicle = _OscEnum("ObjectType", "vehicle")
    miscellaneous = _OscEnum("ObjectType", "miscellaneous")
    external = _OscEnum("ObjectType", "external", min_minor_version=1)


class ParameterType(metaclass=_EnumMeta):
    """Enum for ParameterType"""

    integer = _OscEnum(
        "ParameterType", "integer", max_minor_version=1, replacement="int"
    )
    int = _OscEnum("ParameterType", "int", min_minor_version=2)
    double = _OscEnum("ParameterType", "double")
    string = _OscEnum("ParameterType", "string")
    unsignedInt = _OscEnum("ParameterType", "unsignedInt")
    unsignedShort = _OscEnum("ParameterType", "unsignedShort")
    boolean = _OscEnum("ParameterType", "boolean")
    dateTime = _OscEnum("ParameterType", "dateTime")


class PedestrianCategory(metaclass=_EnumMeta):
    """Enum for PedestrianCategory"""

    pedestrian = _OscEnum("PedestrianCategory", "pedestrian")
    wheelchair = _OscEnum("PedestrianCategory", "wheelchair")
    animal = _OscEnum("PedestrianCategory", "animal")


class PrecipitationType(metaclass=_EnumMeta):
    """Enum for PercipitationType"""

    dry = _OscEnum("PrecipitationType", "dry")
    rain = _OscEnum("PrecipitationType", "rain")
    snow = _OscEnum("PrecipitationType", "snow")


class Priority(metaclass=_EnumMeta):
    """Enum for Priority"""

    overwrite = _OscEnum(
        "Priority", "overwrite", max_minor_version=1, replacement="override"
    )
    override = _OscEnum("Priority", "override", min_minor_version=2)
    skip = _OscEnum("Priority", "skip")
    parallel = _OscEnum("Priority", "parallel")


class ReferenceContext(metaclass=_EnumMeta):
    """Enum for ReferenceContext"""

    relative = _OscEnum("ReferenceContext", "relative")
    absolute = _OscEnum("ReferenceContext", "absolute")


class RelativeDistanceType(metaclass=_EnumMeta):
    """Enum for RelativeDistanceType"""

    longitudinal = _OscEnum("RelativeDistanceType", "longitudinal")
    lateral = _OscEnum("RelativeDistanceType", "lateral")
    cartesianDistance = _OscEnum(
        "RelativeDistanceType", "cartesianDistance", max_minor_version=0
    )
    euclidianDistance = _OscEnum(
        "RelativeDistanceType", "euclidianDistance", min_minor_version=1
    )


class RouteStrategy(metaclass=_EnumMeta):
    """Enum for RouteStrategy"""

    fastest = _OscEnum("RouteStrategy", "fastest")
    shortest = _OscEnum("RouteStrategy", "shortest")
    leastIntersections = _OscEnum("RouteStrategy", "leastIntersections")
    random = _OscEnum("RouteStrategy", "random")


class Rule(metaclass=_EnumMeta):
    """Enum for Rule"""

    greaterThan = _OscEnum("Rule", "greaterThan")
    lessThan = _OscEnum("Rule", "lessThan")
    equalTo = _OscEnum("Rule", "equalTo")
    greaterOrEqual = _OscEnum("Rule", "greaterOrEqual", min_minor_version=1)
    lessOrEqual = _OscEnum("Rule", "lessOrEqual", min_minor_version=1)
    notEqualTo = _OscEnum("Rule", "notEqualTo", min_minor_version=1)


class SpeedTargetValueType(metaclass=_EnumMeta):
    """Enum for SpeedTargetValueType"""

    delta = _OscEnum("SpeedTargetValueType", "delta")
    factor = _OscEnum("SpeedTargetValueType", "factor")


class StoryboardElementState(metaclass=_EnumMeta):
    """Enum for StoryboardElementState"""

    startTransition = _OscEnum("StoryboardElementState", "startTransition")
    endTransition = _OscEnum("StoryboardElementState", "endTransition")
    stopTransition = _OscEnum("StoryboardElementState", "stopTransition")
    skipTransition = _OscEnum("StoryboardElementState", "skipTransition")
    completeState = _OscEnum("StoryboardElementState", "completeState")
    runningState = _OscEnum("StoryboardElementState", "runningState")
    standbyState = _OscEnum("StoryboardElementState", "standbyState")


class StoryboardElementType(metaclass=_EnumMeta):
    """Enum for StoryboardElementType"""

    story = _OscEnum("StoryboardElementType", "story")
    act = _OscEnum("StoryboardElementType", "act")
    maneuver = _OscEnum("StoryboardElementType", "maneuver")
    event = _OscEnum("StoryboardElementType", "event")
    action = _OscEnum("StoryboardElementType", "action")
    maneuverGroup = _OscEnum("StoryboardElementType", "maneuverGroup")


class TriggeringEntitiesRule(metaclass=_EnumMeta):
    """Enum for TriggeringEntitiesRule"""

    any = _OscEnum("TriggeringEntitiesRule", "any")
    all = _OscEnum("TriggeringEntitiesRule", "all")


class VehicleCategory(metaclass=_EnumMeta):
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


class CoordinateSystem(metaclass=_EnumMeta):
    """Enum for CoordinateSystem"""

    entity = _OscEnum("CoordinateSystem", "entity", min_minor_version=1)
    lane = _OscEnum("CoordinateSystem", "lane", min_minor_version=1)
    road = _OscEnum("CoordinateSystem", "road", min_minor_version=1)
    trajectory = _OscEnum("CoordinateSystem", "trajectory", min_minor_version=1)


class LateralDisplacement(metaclass=_EnumMeta):
    any = _OscEnum("LateralDisplacement", "any", min_minor_version=1)
    leftToReferencedEntity = _OscEnum(
        "LateralDisplacement", "leftToReferencedEntity", min_minor_version=1
    )
    rightToReferencedEntity = _OscEnum(
        "LateralDisplacement", "rightToReferencedEntity", min_minor_version=1
    )


class LongitudinalDisplacement(metaclass=_EnumMeta):
    any = _OscEnum("LongitudinalDisplacement", "any", min_minor_version=1)
    trailingReferencedEntity = _OscEnum(
        "LongitudinalDisplacement", "trailingReferencedEntity", min_minor_version=1
    )
    leadingReferencedEntity = _OscEnum(
        "LongitudinalDisplacement", "leadingReferencedEntity", min_minor_version=1
    )


class AutomaticGearType(metaclass=_EnumMeta):
    n = _OscEnum("AutomaticGearType", "n", min_minor_version=2)
    p = _OscEnum("AutomaticGearType", "p", min_minor_version=2)
    r = _OscEnum("AutomaticGearType", "r", min_minor_version=2)
    d = _OscEnum("AutomaticGearType", "d", min_minor_version=2)


class ControllerType(metaclass=_EnumMeta):
    lateral = _OscEnum("ControllerType", "lateral", min_minor_version=2)
    longitudinal = _OscEnum("ControllerType", "longitudinal", min_minor_version=2)
    lighting = _OscEnum("ControllerType", "lighting", min_minor_version=2)
    animation = _OscEnum("ControllerType", "animation", min_minor_version=2)
    movement = _OscEnum("ControllerType", "movement", min_minor_version=2)
    appearance = _OscEnum("ControllerType", "appearance", min_minor_version=2)
    all = _OscEnum("ControllerType", "all", min_minor_version=2)


class DirectionalDimension(metaclass=_EnumMeta):
    longitudinal = _OscEnum("DirectionalDimension", "longitudinal", min_minor_version=2)
    lateral = _OscEnum("DirectionalDimension", "lateral", min_minor_version=2)
    vertical = _OscEnum("DirectionalDimension", "vertical", min_minor_version=2)


class FractionalCloudCover(metaclass=_EnumMeta):
    zeroOktas = _OscEnum("FractionalCloudCover", "zeroOktas", min_minor_version=2)
    oneOktas = _OscEnum("FractionalCloudCover", "oneOktas", min_minor_version=2)
    twoOktas = _OscEnum("FractionalCloudCover", "twoOktas", min_minor_version=2)
    threeOktas = _OscEnum("FractionalCloudCover", "threeOktas", min_minor_version=2)
    fourOktas = _OscEnum("FractionalCloudCover", "fourOktas", min_minor_version=2)
    fiveOktas = _OscEnum("FractionalCloudCover", "fiveOktas", min_minor_version=2)
    sixOktas = _OscEnum("FractionalCloudCover", "sixOktas", min_minor_version=2)
    sevenOktas = _OscEnum("FractionalCloudCover", "sevenOktas", min_minor_version=2)
    eightOktas = _OscEnum("FractionalCloudCover", "eightOktas", min_minor_version=2)
    nineOktas = _OscEnum("FractionalCloudCover", "nineOktas", min_minor_version=2)


class LightMode(metaclass=_EnumMeta):
    on = _OscEnum("LightMode", "on", min_minor_version=2)
    off = _OscEnum("LightMode", "off", min_minor_version=2)
    flashing = _OscEnum("LightMode", "flashing", min_minor_version=2)


class PedestrianGestureType(metaclass=_EnumMeta):
    phoneCallRightHand = _OscEnum(
        "PedestrianGestureType", "phoneCallRightHand", min_minor_version=2
    )
    phoneCallLeftHand = _OscEnum(
        "PedestrianGestureType", "phoneCallLeftHand", min_minor_version=2
    )
    phoneTextRightHand = _OscEnum(
        "PedestrianGestureType", "phoneTextRightHand", min_minor_version=2
    )
    phoneTextLeftHand = _OscEnum(
        "PedestrianGestureType", "phoneTextLeftHand", min_minor_version=2
    )
    wavingRightArm = _OscEnum(
        "PedestrianGestureType", "wavingRightArm", min_minor_version=2
    )
    wavingLeftArm = _OscEnum(
        "PedestrianGestureType", "wavingLeftArm", min_minor_version=2
    )
    umbrellaRightHand = _OscEnum(
        "PedestrianGestureType", "umbrellaRightHand", min_minor_version=2
    )
    umbrellaLeftHand = _OscEnum(
        "PedestrianGestureType", "umbrellaLeftHand", min_minor_version=2
    )
    crossArms = _OscEnum("PedestrianGestureType", "crossArms", min_minor_version=2)
    coffeeRightHand = _OscEnum(
        "PedestrianGestureType", "coffeeRightHand", min_minor_version=2
    )
    coffeeLeftHand = _OscEnum(
        "PedestrianGestureType", "coffeeLeftHand", min_minor_version=2
    )
    sandwichRightHand = _OscEnum(
        "PedestrianGestureType", "sandwichRightHand", min_minor_version=2
    )
    sandwichLeftHand = _OscEnum(
        "PedestrianGestureType", "sandwichLeftHand", min_minor_version=2
    )


class PedestrianMotionType(metaclass=_EnumMeta):
    standing = _OscEnum("PedestrianMotionType", "standing", min_minor_version=2)
    sitting = _OscEnum("PedestrianMotionType", "sitting", min_minor_version=2)
    lying = _OscEnum("PedestrianMotionType", "lying", min_minor_version=2)
    squatting = _OscEnum("PedestrianMotionType", "squatting", min_minor_version=2)
    walking = _OscEnum("PedestrianMotionType", "walking", min_minor_version=2)
    running = _OscEnum("PedestrianMotionType", "running", min_minor_version=2)
    reeling = _OscEnum("PedestrianMotionType", "reeling", min_minor_version=2)
    crawling = _OscEnum("PedestrianMotionType", "crawling", min_minor_version=2)
    cycling = _OscEnum("PedestrianMotionType", "cycling", min_minor_version=2)
    jumping = _OscEnum("PedestrianMotionType", "jumping", min_minor_version=2)
    ducking = _OscEnum("PedestrianMotionType", "ducking", min_minor_version=2)
    bendingDown = _OscEnum("PedestrianMotionType", "bendingDown", min_minor_version=2)


class RoutingAlgorithm(metaclass=_EnumMeta):
    assignedRoute = _OscEnum("RoutingAlgorithm", "assignedRoute", min_minor_version=2)
    fastest = _OscEnum("RoutingAlgorithm", "fastest", min_minor_version=2)
    leastIntersections = _OscEnum(
        "RoutingAlgorithm", "leastIntersections", min_minor_version=2
    )
    shortest = _OscEnum("RoutingAlgorithm", "shortest", min_minor_version=2)
    undefined = _OscEnum("RoutingAlgorithm", "undefined", min_minor_version=2)


class VehicleComponentType(metaclass=_EnumMeta):
    hood = _OscEnum("VehicleComponentType", "hood", min_minor_version=2)
    trunk = _OscEnum("VehicleComponentType", "trunk", min_minor_version=2)
    doorFrontRight = _OscEnum(
        "VehicleComponentType", "doorFrontRight", min_minor_version=2
    )
    doorFrontLeft = _OscEnum(
        "VehicleComponentType", "doorFrontLeft", min_minor_version=2
    )
    doorRearRight = _OscEnum(
        "VehicleComponentType", "doorRearRight", min_minor_version=2
    )
    doorRearLeft = _OscEnum("VehicleComponentType", "doorRearLeft", min_minor_version=2)
    windowFrontRight = _OscEnum(
        "VehicleComponentType", "windowFrontRight", min_minor_version=2
    )
    windowFrontLeft = _OscEnum(
        "VehicleComponentType", "windowFrontLeft", min_minor_version=2
    )
    windowRearRight = _OscEnum(
        "VehicleComponentType", "windowRearRight", min_minor_version=2
    )
    windowRearLeft = _OscEnum(
        "VehicleComponentType", "windowRearLeft", min_minor_version=2
    )
    sideMirrors = _OscEnum("VehicleComponentType", "sideMirrors", min_minor_version=2)
    sideMirrorRight = _OscEnum(
        "VehicleComponentType", "sideMirrorRight", min_minor_version=2
    )
    sideMirrorLeft = _OscEnum(
        "VehicleComponentType", "sideMirrorLeft", min_minor_version=2
    )


class VehicleLightType(metaclass=_EnumMeta):
    daytimeRunningLights = _OscEnum(
        "VehicleLightType", "daytimeRunningLights", min_minor_version=2
    )
    lowBeam = _OscEnum("VehicleLightType", "lowBeam", min_minor_version=2)
    highBeam = _OscEnum("VehicleLightType", "highBeam", min_minor_version=2)
    fogLights = _OscEnum("VehicleLightType", "fogLights", min_minor_version=2)
    fogLightsFront = _OscEnum("VehicleLightType", "fogLightsFront", min_minor_version=2)
    fogLightsRear = _OscEnum("VehicleLightType", "fogLightsRear", min_minor_version=2)
    brakeLights = _OscEnum("VehicleLightType", "brakeLights", min_minor_version=2)
    warningLights = _OscEnum("VehicleLightType", "warningLights", min_minor_version=2)
    indicatorLeft = _OscEnum("VehicleLightType", "indicatorLeft", min_minor_version=2)
    indicatorRight = _OscEnum("VehicleLightType", "indicatorRight", min_minor_version=2)
    reversingLights = _OscEnum(
        "VehicleLightType", "reversingLights", min_minor_version=2
    )
    licensePlateIllumination = _OscEnum(
        "VehicleLightType", "licensePlateIllumination", min_minor_version=2
    )
    specialPurposeLights = _OscEnum(
        "VehicleLightType", "specialPurposeLights", min_minor_version=2
    )


class Role(metaclass=_EnumMeta):
    none = _OscEnum("Role", "none", min_minor_version=2)
    ambulance = _OscEnum("Role", "ambulance", min_minor_version=2)
    civil = _OscEnum("Role", "civil", min_minor_version=2)
    fire = _OscEnum("Role", "fire", min_minor_version=2)
    military = _OscEnum("Role", "military", min_minor_version=2)
    police = _OscEnum("Role", "police", min_minor_version=2)
    publicTransport = _OscEnum("Role", "publicTransport", min_minor_version=2)
    roadAssistance = _OscEnum("Role", "roadAssistance", min_minor_version=2)


class Wetness(metaclass=_EnumMeta):
    dry = _OscEnum("Wetness", "dry", min_minor_version=2)
    moist = _OscEnum("Wetness", "moist", min_minor_version=2)
    wetWithPuddles = _OscEnum("Wetness", "wetWithPuddles", min_minor_version=2)
    lowFlooded = _OscEnum("Wetness", "lowFlooded", min_minor_version=2)
    highFlooded = _OscEnum("Wetness", "highFlooded", min_minor_version=2)


class ColorType:
    other = _OscEnum("ColorType", "other", min_minor_version=2)
    red = _OscEnum("ColorType", "red", min_minor_version=2)
    yellow = _OscEnum("ColorType", "yellow", min_minor_version=2)
    green = _OscEnum("ColorType", "green", min_minor_version=2)
    blue = _OscEnum("ColorType", "blue", min_minor_version=2)
    violet = _OscEnum("ColorType", "violet", min_minor_version=2)
    orange = _OscEnum("ColorType", "orange", min_minor_version=2)
    brown = _OscEnum("ColorType", "brown", min_minor_version=2)
    black = _OscEnum("ColorType", "black", min_minor_version=2)
    grey = _OscEnum("ColorType", "grey", min_minor_version=2)
    white = _OscEnum("ColorType", "white", min_minor_version=2)
