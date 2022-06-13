"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
from scenariogeneration import xodr as pyodrx
from scenariogeneration import prettyprint


def test_signal_validity():

    signal = pyodrx.Signal(s=98.0, t=-4, country="USA", Type="R1", subtype="1")
    signal.add_validity(1, 1)
    road = pyodrx.create_straight_road(0)
    road.add_signal(signal)
    prettyprint(road.get_element())


def test_object_validity():

    guardrail = pyodrx.Object(
        0, 0, height=0.3, zOffset=0.4, Type=pyodrx.ObjectType.barrier, name="guardRail"
    )
    guardrail.add_validity(1, 1)
    road = pyodrx.create_straight_road(0)
    road.add_object(guardrail)
    prettyprint(road.get_element())


def test_signal():
    signal1 = pyodrx.Signal(
        s=10.0,
        t=-2,
        dynamic=pyodrx.Dynamic.no,
        orientation=pyodrx.Orientation.positive,
        zOffset=0.00,
        country="US",
        Type="R1",
        subtype="1",
    )

    signal2 = pyodrx.Signal(
        s=20.0,
        t=-2,
        dynamic=pyodrx.Dynamic.no,
        orientation=pyodrx.Orientation.positive,
        country="DEU",
        Type="274",
        subtype="120",
        value=120,
        unit="km/h",
    )

    road = pyodrx.create_straight_road(0)
    road.add_signal(signal1)
    road.add_signal(signal2)
    prettyprint(road.get_element())
    signal3 = pyodrx.Signal(
        s=10.0,
        t=-2,
        dynamic=pyodrx.Dynamic.no,
        orientation=pyodrx.Orientation.positive,
        zOffset=0.00,
        country="US",
        Type="R1",
        subtype="1",
    )
    # unique fixer
    signal3.id = signal1.id
    assert signal1 == signal3
    assert signal1 != signal2


def test_object():
    object1 = pyodrx.Object(
        s=10.0,
        t=-2,
        dynamic=pyodrx.Dynamic.no,
        orientation=pyodrx.Orientation.positive,
        zOffset=0.00,
        id="1",
        height=1.0,
        Type=pyodrx.ObjectType.pole,
    )

    # same chosen ID should cause warning and be resolved automatically
    object2 = pyodrx.Object(
        s=20.0,
        t=-2,
        dynamic=pyodrx.Dynamic.no,
        orientation=pyodrx.Orientation.positive,
        zOffset=0.00,
        height=10,
        id="1",
        Type=pyodrx.ObjectType.streetLamp,
    )

    road = pyodrx.create_straight_road(0)
    road.add_object([object1, object2])
    prettyprint(road.get_element())
    object3 = pyodrx.Object(
        s=10.0,
        t=-2,
        dynamic=pyodrx.Dynamic.no,
        orientation=pyodrx.Orientation.positive,
        zOffset=0.00,
        id="1",
        height=1.0,
        Type=pyodrx.ObjectType.pole,
    )

    outline = pyodrx.Outline()
    outline.add_corner(pyodrx.CornerLocal(1, 2, 3, 4))
    outline.add_corner(pyodrx.CornerLocal(1, 2, 3, 5))
    object2.add_outline(outline)
    prettyprint(object2)
    object3.id = object1.id
    assert object1 == object3
    assert object2 != object1


def test_repeated_object():
    object1 = pyodrx.Object(
        s=10.0,
        t=-2,
        dynamic=pyodrx.Dynamic.no,
        orientation=pyodrx.Orientation.positive,
        zOffset=0.00,
        height=1.0,
        Type=pyodrx.ObjectType.pole,
    )
    object1.repeat(100, 50)
    road = pyodrx.create_straight_road(0)
    road.add_object(object1)
    prettyprint(road.get_element())

    object2 = pyodrx.Object(
        s=10.0,
        t=-2,
        dynamic=pyodrx.Dynamic.no,
        orientation=pyodrx.Orientation.positive,
        zOffset=0.00,
        height=1.0,
        Type=pyodrx.ObjectType.pole,
    )
    object2.repeat(100, 50)

    object3 = pyodrx.Object(
        s=10.0,
        t=-2,
        dynamic=pyodrx.Dynamic.no,
        orientation=pyodrx.Orientation.positive,
        zOffset=0.00,
        height=1.0,
        Type=pyodrx.ObjectType.pole,
    )
    object3.repeat(100, 50)

    object3.id = object1.id
    assert object1 == object3
    assert object2 != object1


def test_object_roadside():
    road = pyodrx.create_straight_road(0)
    odr = pyodrx.OpenDrive("myroad")
    odr.add_road(road)
    odr.adjust_roads_and_lanes()
    object1 = pyodrx.Object(
        s=0,
        t=0,
        dynamic=pyodrx.Dynamic.no,
        orientation=pyodrx.Orientation.positive,
        zOffset=0.00,
        height=1.0,
        Type=pyodrx.ObjectType.pole,
    )
    road.add_object_roadside(object1, 50, tOffset=0.85)
    prettyprint(road.get_element())


def test_corner_local():
    cl = pyodrx.CornerLocal(1, 2, 3, 4)
    cl2 = pyodrx.CornerLocal(1, 2, 3, 4)
    cl3 = pyodrx.CornerLocal(1, 2, 3, 3)
    assert cl == cl2
    assert cl != cl3
    prettyprint(cl)


def test_corner_road():
    cr = pyodrx.CornerRoad(1, 2, 3, 4)
    cr2 = pyodrx.CornerRoad(1, 2, 3, 4)
    cr3 = pyodrx.CornerRoad(1, 2, 3, 3)
    assert cr == cr2
    assert cr != cr3
    prettyprint(cr)


def test_outline():
    cr = pyodrx.CornerRoad(1, 2, 3, 4)
    cr2 = pyodrx.CornerLocal(1, 2, 3, 4)

    outline = pyodrx.Outline()
    outline.add_corner(cr)
    outline2 = pyodrx.Outline()
    outline2.add_corner(cr)

    outline3 = pyodrx.Outline()
    outline3.add_corner(cr2)
    outline4 = pyodrx.Outline(
        True, pyodrx.FillType.asphalt, pyodrx.LaneType.bidirectional, False, 1
    )
    outline4.add_corner(cr2)
    prettyprint(outline)
    prettyprint(outline4)
    assert outline == outline2
    assert outline != outline3
    assert outline != outline4
