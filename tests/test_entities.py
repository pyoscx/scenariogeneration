"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
import pytest

from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint
from scenariogeneration.xosc.utils import CatalogReference, EntityRef


def test_properties():
    prop = OSC.Properties()
    prop.add_file("myprops.xml")
    prettyprint(prop.get_element())
    prop.add_property("mything", "2")
    prettyprint(prop.get_element())
    prop.add_property("theotherthing", "true")

    prop2 = OSC.Properties()
    prop2.add_file("myprops.xml")
    prop2.add_property("mything", "2")
    prop2.add_property("theotherthing", "true")

    prop3 = OSC.Properties()
    prop3.add_file("myprops.xml")

    assert prop == prop2
    assert prop != prop3


def test_axle():
    ba = OSC.Axle(1, 1, 2, 1, 1)
    prettyprint(ba.get_element())
    ba2 = OSC.Axle(1, 1, 2, 1, 1)
    ba3 = OSC.Axle(1, 1, 2, 1, 12)
    assert ba == ba2
    assert ba != ba3
    ba4 = OSC.Axle.parse(ba.get_element())
    assert ba == ba4


def test_axles():
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ra = OSC.Axle(1, 1, 2, 1, 1)
    aa = OSC.Axle(1, 1, 2, 1, 1)
    aa2 = OSC.Axle(2, 3, 1, 3, 2)
    axles = OSC.Axles(fa, ra)
    axles.add_axle(aa)
    axles.add_axle(aa2)
    prettyprint(axles.get_element())
    axles2 = OSC.Axles(fa, ra)
    axles2.add_axle(aa)
    axles2.add_axle(aa2)
    axles3 = OSC.Axles(fa, ra)
    assert axles == axles2
    assert axles != axles3
    axles4 = OSC.Axles.parse(axles.get_element())
    assert axles == axles4


def test_vehicle():
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)

    veh = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)

    prettyprint(veh.get_element())
    veh.add_property_file("propfile.xml")
    veh.add_property("myprop", "12")
    veh.add_axle(ba)
    param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
    veh.add_parameter(param)

    prettyprint(veh.get_element())

    veh2 = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)
    veh2.add_property_file("propfile.xml")
    veh2.add_property("myprop", "12")
    veh2.add_axle(ba)
    veh2.add_parameter(param)

    veh3 = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)
    assert veh == veh2
    assert veh != veh3

    veh4 = OSC.Vehicle.parse(veh.get_element())
    prettyprint(veh4.get_element())
    assert veh4 == veh


def test_pedestrian():
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    ped = OSC.Pedestrian("myped", 100, OSC.PedestrianCategory.pedestrian, bb, "ped")

    prettyprint(ped.get_element())
    ped.add_property_file("propfile.xml")
    ped.add_property("myprop", "12")
    param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
    ped.add_parameter(param)

    prettyprint(ped.get_element())

    ped2 = OSC.Pedestrian("myped", 100, OSC.PedestrianCategory.pedestrian, bb, "ped")
    ped2.add_property_file("propfile.xml")
    ped2.add_property("myprop", "12")
    ped2.add_parameter(param)
    ped3 = OSC.Pedestrian("myped", 100, OSC.PedestrianCategory.pedestrian, bb)

    assert ped == ped2
    assert ped != ped3

    ped4 = OSC.Pedestrian.parse(ped.get_element())
    assert ped4 == ped


def test_miscobj():
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    veh = OSC.MiscObject("mycar", 100, OSC.MiscObjectCategory.obstacle, bb)

    prettyprint(veh.get_element())
    veh.add_property_file("propfile.xml")
    veh.add_property_file("propfile2.xml")
    veh.add_property("myprop", "12")
    param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
    param2 = OSC.Parameter("myparam1", OSC.ParameterType.double, "0.01")
    veh.add_parameter(param)
    veh.add_parameter(param2)
    prettyprint(veh.get_element())

    veh2 = OSC.MiscObject("mycar", 100, OSC.MiscObjectCategory.obstacle, bb)
    veh2.add_property_file("propfile.xml")
    veh2.add_property_file("propfile2.xml")
    veh2.add_property("myprop", "12")
    veh2.add_parameter(param)
    veh2.add_parameter(param2)

    veh3 = OSC.MiscObject("mycar", 100, OSC.MiscObjectCategory.obstacle, bb)
    veh4 = OSC.MiscObject.parse(veh3.get_element())
    assert veh3 == veh4
    assert veh == veh2
    assert veh != veh3
    veh5 = OSC.MiscObject.parse(veh.get_element())
    prettyprint(veh5.get_element())
    assert veh5 == veh


def test_entity():
    object_type_list = [OSC.ObjectType.vehicle, OSC.ObjectType.pedestrian]
    ent = OSC.Entity("ego", object_type=object_type_list)
    prettyprint(ent.get_element())
    ent3 = OSC.Entity("ego", entityref=["Ego", "Ego2", "Ego3"])
    prettyprint(ent3.get_element())
    ent2 = OSC.Entity("ego", object_type=OSC.ObjectType.vehicle)
    ent4 = OSC.Entity("ego", object_type=object_type_list)
    assert ent != ent2
    assert ent == ent4

    ent5 = OSC.Entity.parse(ent.get_element())
    assert ent5 == ent

    ent6 = OSC.Entity.parse(ent3.get_element())
    prettyprint(ent6.get_element())
    assert ent6 == ent3


def test_scenarioobject():
    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")
    cnt = OSC.Controller("mycontroler", prop)

    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)
    veh = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)
    veh.add_property_file("propfile.xml")
    veh.add_property("myprop", "12")
    veh.add_axle(ba)
    param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
    veh.add_parameter(param)

    so = OSC.ScenarioObject("name", veh, cnt)
    so2 = OSC.ScenarioObject("name", veh, cnt)
    prettyprint(so.get_element())
    assert so == so2

    so4 = OSC.ScenarioObject.parse(so.get_element())
    prettyprint(so4.get_element())
    assert so4 == so


def test_entities():
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)
    veh = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)
    param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
    veh.add_parameter(param)

    entities = OSC.Entities()
    entities.add_scenario_object("Ego", veh)
    entities.add_scenario_object("Target_1", veh)
    entities.add_entity_bytype("Target_2", OSC.ObjectType.vehicle)
    entities.add_entity_byref("Target_3", "something")
    prettyprint(entities.get_element())

    entities2 = OSC.Entities()
    entities2.add_scenario_object("Ego", veh)
    entities2.add_scenario_object("Target_1", veh)
    entities2.add_entity_bytype("Target_2", OSC.ObjectType.vehicle)
    entities2.add_entity_byref("Target_3", "something")

    entities3 = OSC.Entities()
    entities3.add_scenario_object("Ego", veh)
    entities3.add_scenario_object("Target_1", veh)
    entities3.add_entity_bytype("Target_2", OSC.ObjectType.vehicle)

    assert entities == entities2
    assert entities != entities3

    entities4 = OSC.Entities.parse(entities2.get_element())
    prettyprint(entities4.get_element())
    assert entities == entities4


def test_controller():
    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")

    cnt = OSC.Controller("mycontroler", prop)
    prettyprint(cnt.get_element())
    cnt2 = OSC.Controller("mycontroler", prop)
    cnt3 = OSC.Controller("mycontroler2", prop)
    assert cnt == cnt2
    assert cnt != cnt3


def test_controller_in_Entities():
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)
    veh = OSC.Vehicle("mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10)

    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")

    cnt = OSC.Controller("mycontroler", prop)

    entities = OSC.Entities()
    entities.add_scenario_object("Target_1", veh, cnt)

    prettyprint(entities.get_element())

    entities2 = OSC.Entities()
    entities2.add_scenario_object("Target_1", veh, cnt)

    entities3 = OSC.Entities()
    entities3.add_scenario_object("Target_2", veh, cnt)
    assert entities == entities2
    assert entities != entities3


def test_external_object():
    ext_obj = OSC.ExternalObjectReference("my object")
    ext_obj2 = OSC.ExternalObjectReference("my object")
    ext_obj3 = OSC.ExternalObjectReference("my object 2")

    assert ext_obj == ext_obj2
    assert ext_obj != ext_obj3

    ext_obj4 = OSC.ExternalObjectReference.parse(ext_obj.get_element())
    assert ext_obj == ext_obj4
