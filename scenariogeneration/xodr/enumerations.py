"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.
"""

from enum import Enum, auto
from typing import Type, Union


def enumchecker(
    value: Union[Enum, str, None], enum_type: Type[Enum], none_ok: bool = False
) -> Enum:
    """Check if an enum value is correct. If the input is a string, attempt to
    convert it to the enum.

    Parameters
    ----------
    value : Enum or str or None
        The value to check or convert.
    enum_type : Type[Enum]
        The enumeration type to validate against.
    none_ok : bool, optional
        Whether None is an acceptable value. Defaults to False.

    Returns
    -------
    Enum
        The validated or converted enum value.

    Raises
    ------
    TypeError
        If the value is invalid or cannot be converted to the enum type.
    """
    if value is None:
        if none_ok:
            return value
        else:
            raise TypeError("None is not a valid enumeration")
    if isinstance(value, Enum):
        if hasattr(enum_type, value.name):
            return value
        else:
            raise TypeError(
                value.get_name()
                + " is not of Enumeration type :"
                + str(enum_type)
            )

    elif isinstance(value, str):
        if hasattr(enum_type, value):
            return enum_type[value]
        else:
            raise TypeError(
                value
                + " is not a valid string input for Enumeration type "
                + str(enum_type)
            )
    else:
        raise TypeError(
            "Type: " + type(enum_type) + " is not a valid input for Enums."
        )


class TrafficRule(Enum):
    """Enum for TrafficRule."""

    RHT = auto()
    LHT = auto()
    none = auto()


class MarkRule(Enum):
    """Enum for MarkRule."""

    no_passing = auto()
    caution = auto()
    none = auto()


class LaneType(Enum):
    """Enum for LaneType."""

    none = auto()
    driving = auto()
    stop = auto()
    shoulder = auto()
    biking = auto()
    sidewalk = auto()
    curb = auto()
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
    """Enum for RoadMarkColor."""

    standard = auto()
    blue = auto()
    green = auto()
    red = auto()
    white = auto()
    yellow = auto()
    orange = auto()


class RoadMarkWeight(Enum):
    """Enum for RoadMarkWeight."""

    standard = auto()
    bold = auto()


class RoadMarkType(Enum):
    """Enum for RoadMarkType."""

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
    """Enum for RoadType."""

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
    """Enum for LaneChange."""

    increase = auto()
    decrease = auto()
    both = auto()
    none = auto()


class ElementType(Enum):
    """Enum for LaneChange."""

    road = auto()
    junction = auto()


class ContactPoint(Enum):
    """Enum for ContactPoint."""

    start = auto()
    end = auto()


class Direction(Enum):
    """Enum for Direction."""

    same = auto()
    opposite = auto()


class Orientation(Enum):
    """Enum for Orientation."""

    positive = auto()
    negative = auto()
    none = auto()


class ObjectType(Enum):
    """Enum for ObjectType taken from OpenDRIVE 1.6 without deprecated
    types."""

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


class TunnelType(Enum):
    """Enum for TunnelType."""

    standard = auto()
    underpass = auto()


class Dynamic(Enum):
    """Enum for Dynamic."""

    yes = auto()
    no = auto()


class RoadSide(Enum):
    """Enum for RoadSide."""

    both = auto()
    left = auto()
    right = auto()


class JunctionGroupType(Enum):
    """Enum for JunctionGroup."""

    roundabout = auto()
    unknown = auto()


class JunctionType(Enum):
    """Enum for JunctionType."""

    default = auto()
    virtual = auto()
    direct = auto()


class FillType(Enum):
    """Enum for FillType."""

    asphalt = auto()
    cobble = auto()
    concrete = auto()
    grass = auto()
    gravel = auto()
    pavement = auto()
    soil = auto()


class Access(Enum):
    """Enum for ParkingSpace Access."""

    all = auto()
    bus = auto()
    car = auto()
    electric = auto()
    handicapped = auto()
    residents = auto()
    truck = auto()
    woman = auto()


class RawDataPostProcessing(Enum):
    """Enum for dataQuality RawData PostProcessing."""

    cleaned = auto()
    fused = auto()
    property = auto()
    raw = auto()


class RawDataSource(Enum):
    """Enum for dataQuality RawData PostProcessing."""

    cadaster = auto()
    custom = auto()
    sensor = auto()
