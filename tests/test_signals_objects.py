"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

from scenariogeneration import xodr
from scenariogeneration import prettyprint, prettify

from .xml_validator import version_validation, ValidationResponse
import pytest


def test_signal_validity():
    signal = xodr.Signal(s=98.0, t=-4, country="USA", Type="R1", subtype="1")
    signal.add_validity(1, 1)
    road = xodr.create_road(xodr.Line(100), 0)
    road.add_signal(signal)
    prettyprint(road.get_element())
    assert (
        version_validation("t_road_signals_signal", signal, wanted_schema="xodr")
        == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        xodr.Signal(0, 0, "US", "R1", dynamic="dummy")
    with pytest.raises(TypeError):
        xodr.Signal(0, 0, "US", "R1", orientation="dummy")


def test_object_validity():
    guardrail = xodr.Object(
        s=0,
        t=0,
        height=0.3,
        zOffset=0.4,
        Type=xodr.ObjectType.barrier,
        name="guardRail",
    )
    guardrail.add_validity(1, 1)
    road = xodr.create_road(xodr.Line(100), 0)
    road.add_object(guardrail)
    prettyprint(road.get_element())
    assert (
        version_validation("t_road_objects_object", guardrail, wanted_schema="xodr")
        == ValidationResponse.OK
    )


def test_object_parking_space():
    parking_space_object = xodr.Object(
        s=0,
        t=0,
        length=5,
        width=3,
        height=0.0,
        Type=xodr.ObjectType.parkingSpace,
        name="parkingSpace",
    )
    parking_space = xodr.ParkingSpace(xodr.Access.all, "test string")
    parking_space_object.add_parking_space(parking_space)
    road = xodr.create_road(xodr.Line(100), 0)
    road.add_object(parking_space_object)
    prettyprint(road.get_element())
    assert (
        version_validation(
            "t_road_objects_object", parking_space_object, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )

    with pytest.raises(TypeError):
        xodr.ParkingSpace("dummy", "test")


def test_signal():
    signal1 = xodr.Signal(
        s=10.0,
        t=-2,
        dynamic=xodr.Dynamic.no,
        orientation=xodr.Orientation.positive,
        zOffset=0.00,
        country="US",
        Type="R1",
        subtype="1",
    )

    signal2 = xodr.Signal(
        s=20.0,
        t=-2,
        dynamic=xodr.Dynamic.no,
        orientation=xodr.Orientation.positive,
        country="DEU",
        Type="274",
        subtype="120",
        value=120,
        unit="km/h",
    )

    signal2_wRev = xodr.Signal(
        s=20.0,
        t=-2,
        dynamic=xodr.Dynamic.no,
        orientation=xodr.Orientation.positive,
        country="DEU",
        countryRevision="2017",
        Type="274",
        subtype="120",
        value=120,
        unit="km/h",
    )

    road = xodr.create_road(xodr.Line(100), 0)
    road.add_signal(signal1)
    road.add_signal(signal2)
    road.add_signal(signal2_wRev)
    prettyprint(road.get_element())
    signal3 = xodr.Signal(
        s=10.0,
        t=-2,
        dynamic=xodr.Dynamic.no,
        orientation=xodr.Orientation.positive,
        zOffset=0.00,
        country="US",
        Type="R1",
        subtype="1",
    )
    # unique fixer
    signal3.id = signal1.id
    assert signal1 == signal3
    assert signal1 != signal2
    assert signal2 != signal2_wRev
    road.planview.adjust_geometries()
    assert (
        version_validation("t_road", road, wanted_schema="xodr")
        == ValidationResponse.OK
    )
    with pytest.raises(xodr.NotEnoughInputArguments):
        sig = xodr.Signal(100, 2, "se", "c", "31", value="10")
        sig.get_attributes()


def test_signal_reference():
    signal1 = xodr.SignalReference(
        s=10.0,
        t=-2,
        orientation=xodr.Orientation.positive,
    )

    signal2 = xodr.SignalReference(
        s=20.0,
        t=-2,
        orientation=xodr.Orientation.positive,
    )

    signal2_wRev = xodr.SignalReference(
        s=20.0,
        t=-2,
        orientation=xodr.Orientation.positive,
    )

    road = xodr.create_road(xodr.Line(100), 0)
    road.add_signal(signal1)
    road.add_signal(signal2)
    road.add_signal(signal2_wRev)
    prettyprint(road.get_element())
    signal3 = xodr.SignalReference(
        s=10.0,
        t=-2,
        orientation=xodr.Orientation.positive,
    )
    # unique fixer
    signal3.id = signal1.id
    assert signal1 == signal3
    assert signal1 != signal2
    assert signal2 != signal2_wRev
    road.planview.adjust_geometries()
    assert (
        version_validation("t_road", road, wanted_schema="xodr")
        == ValidationResponse.OK
    )

    with pytest.raises(TypeError):
        xodr.SignalReference(1, 1, 1, "dummy")


def test_object():
    object1 = xodr.Object(
        s=10.0,
        t=-2,
        dynamic=xodr.Dynamic.no,
        orientation=xodr.Orientation.positive,
        zOffset=0.00,
        id="1",
        height=1.0,
        Type=xodr.ObjectType.pole,
    )

    # same chosen ID should cause warning and be resolved automatically
    object2 = xodr.Object(
        s=20.0,
        t=-2,
        dynamic=xodr.Dynamic.no,
        orientation=xodr.Orientation.positive,
        zOffset=0.00,
        height=10,
        id="1",
        Type=xodr.ObjectType.streetLamp,
    )

    road = xodr.create_road(xodr.Line(100), 0)
    road.add_object([object1, object2])
    prettyprint(road.get_element())
    object3 = xodr.Object(
        s=10.0,
        t=-2,
        dynamic=xodr.Dynamic.no,
        orientation=xodr.Orientation.positive,
        zOffset=0.00,
        id="1",
        height=1.0,
        Type=xodr.ObjectType.pole,
    )

    outline = xodr.Outline(id=1)
    outline.add_corner(xodr.CornerLocal(1, 2, 3, 4))
    outline.add_corner(xodr.CornerLocal(1, 2, 3, 5))
    object2.add_outline(outline)
    prettyprint(object2)
    object3.id = object1.id
    assert object1 == object3
    assert object2 != object1
    road.planview.adjust_geometries()
    assert (
        version_validation("t_road", road, wanted_schema="xodr")
        == ValidationResponse.OK
    )


def test_tunnel():
    tunnel1 = xodr.Tunnel(
        s=10.0,
        length=10.0,
        tunnel_type=xodr.TunnelType.standard,
        id="1",
        name="Tunnel 1",
        daylight=0.79,
        lighting=0.34,
    )
    prettyprint(tunnel1)

    tunnel1_copy = xodr.Tunnel(
        s=10.0,
        length=10.0,
        tunnel_type=xodr.TunnelType.standard,
        id="1",
        name="Tunnel 1",
        daylight=0.79,
        lighting=0.34,
    )
    assert tunnel1 == tunnel1_copy

    tunnel2 = xodr.Tunnel(
        s=50.0,
        length=20.0,
        tunnel_type=xodr.TunnelType.standard,
        id="2",
        name="Tunnel 2",
        daylight=0.79,
        lighting=0.34,
    )
    assert tunnel1 != tunnel2

    assert (
        version_validation("t_road_objects_tunnel", tunnel1, wanted_schema="xodr")
        == ValidationResponse.OK
    )

    road = xodr.create_road(xodr.Line(100), 0)
    road.add_tunnel([tunnel1, tunnel2])
    road.planview.adjust_geometries()
    prettyprint(road)
    assert (
        version_validation("t_road", road, wanted_schema="xodr")
        == ValidationResponse.OK
    )

    assert _is_sub_element_written(tunnel1, road)
    assert _is_sub_element_written(tunnel2, road)

    tunnel1.id = 999
    assert _is_sub_element_written(tunnel1, road)

    new_tunnel = xodr.Tunnel(
        s=1.0,
        length=19.0,
        tunnel_type=xodr.TunnelType.standard,
        id="777",
        name="Tunnel",
        daylight=0.79,
        lighting=0.34,
    )
    assert not _is_sub_element_written(new_tunnel, road)

    road.add_tunnel(new_tunnel)
    assert _is_sub_element_written(new_tunnel, road)

    with pytest.raises(TypeError):
        xodr.Tunnel(1, 1, 1, "", tunnel_type="dummy")


def _is_sub_element_written(sub_element, element):
    return prettify(sub_element.get_element(), xml_declaration=False) in prettify(
        element.get_element(), xml_declaration=True
    )


def test_repeated_object():
    object1 = xodr.Object(
        s=10.0,
        t=-2,
        dynamic=xodr.Dynamic.no,
        orientation=xodr.Orientation.positive,
        zOffset=0.00,
        height=1.0,
        Type=xodr.ObjectType.pole,
    )
    object1.repeat(100, 50)
    road = xodr.create_road(xodr.Line(100), 0)
    road.add_object(object1)
    prettyprint(road.get_element())

    object2 = xodr.Object(
        s=10.0,
        t=-2,
        dynamic=xodr.Dynamic.no,
        orientation=xodr.Orientation.positive,
        zOffset=0.00,
        height=1.0,
        Type=xodr.ObjectType.pole,
    )
    object2.repeat(100, 50)

    object3 = xodr.Object(
        s=10.0,
        t=-2,
        dynamic=xodr.Dynamic.no,
        orientation=xodr.Orientation.positive,
        zOffset=0.00,
        height=1.0,
        Type=xodr.ObjectType.pole,
    )
    object3.repeat(100, 50)

    object3.id = object1.id
    assert object1 == object3
    assert object2 != object1


def test_object_roadside():
    road = xodr.create_road(xodr.Line(100), 0)
    odr = xodr.OpenDrive("myroad")
    odr.add_road(road)
    odr.adjust_roads_and_lanes()
    object1 = xodr.Object(
        s=0,
        t=0,
        dynamic=xodr.Dynamic.no,
        orientation=xodr.Orientation.positive,
        zOffset=0.00,
        height=1.0,
        Type=xodr.ObjectType.pole,
    )
    road.add_object_roadside(object1, 50, tOffset=0.85)
    prettyprint(road.get_element())
    road.planview.adjust_geometries()
    assert (
        version_validation("t_road", road, wanted_schema="xodr")
        == ValidationResponse.OK
    )


def test_corner_local():
    cl = xodr.CornerLocal(1, 2, 3, 4)
    cl2 = xodr.CornerLocal(1, 2, 3, 4)
    cl3 = xodr.CornerLocal(1, 2, 3, 3)
    assert cl == cl2
    assert cl != cl3
    prettyprint(cl)
    assert (
        version_validation(
            "t_road_objects_object_outlines_outline_cornerLocal",
            cl,
            wanted_schema="xodr",
        )
        == ValidationResponse.OK
    )


def test_corner_road():
    cr = xodr.CornerRoad(1, 2, 3, 4)
    cr2 = xodr.CornerRoad(1, 2, 3, 4)
    cr3 = xodr.CornerRoad(1, 2, 3, 3)
    assert cr == cr2
    assert cr != cr3
    prettyprint(cr)
    assert (
        version_validation(
            "t_road_objects_object_outlines_outline_cornerRoad",
            cr,
            wanted_schema="xodr",
        )
        == ValidationResponse.OK
    )


def test_outline():
    cr = xodr.CornerRoad(1, 2, 3, 4)
    cr2 = xodr.CornerLocal(1, 2, 3, 4)

    outline = xodr.Outline()
    outline.add_corner(cr)
    outline2 = xodr.Outline()
    outline2.add_corner(cr)

    outline3 = xodr.Outline()
    outline3.add_corner(cr2)
    outline4 = xodr.Outline(
        True, xodr.FillType.asphalt, xodr.LaneType.bidirectional, False, 1
    )
    outline4.add_corner(cr2)
    prettyprint(outline)
    prettyprint(outline4)
    assert outline == outline2
    assert outline != outline3
    assert outline != outline4
    assert (
        version_validation(
            "t_road_objects_object_outlines_outline", outline, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )
