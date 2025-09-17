"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import copy
import os

import pytest

from scenariogeneration import prettyprint
from scenariogeneration import xosc as OSC
from scenariogeneration.xosc.enumerations import _MINOR_VERSION
from .xml_validator import ValidationResponse, version_validation


@pytest.fixture(autouse=True)
def reset_version():
    OSC.enumerations.VersionBase().setVersion(minor=_MINOR_VERSION)


@pytest.fixture(name="bb", autouse=True)
def bounding_box():
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    return bb


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

    assert version_validation("Properties", prop2, 0) == ValidationResponse.OK
    assert version_validation("Properties", prop2, 1) == ValidationResponse.OK
    assert version_validation("Properties", prop2, 2) == ValidationResponse.OK


def test_axle():
    ba = OSC.Axle(1, 1, 2, 1, 1)
    prettyprint(ba.get_element())
    ba2 = OSC.Axle(1, 1, 2, 1, 1)
    ba3 = OSC.Axle(1, 1, 2, 1, 12)
    assert ba == ba2
    assert ba != ba3
    ba4 = OSC.Axle.parse(ba.get_element())
    assert ba == ba4
    assert version_validation("Axle", ba2, 0) == ValidationResponse.OK
    assert version_validation("Axle", ba, 1) == ValidationResponse.OK
    assert version_validation("Axle", ba, 2) == ValidationResponse.OK


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
    assert version_validation("Axles", axles, 0) == ValidationResponse.OK
    assert version_validation("Axles", axles, 1) == ValidationResponse.OK
    assert version_validation("Axles", axles, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        OSC.Axles("dummy", ra)
    with pytest.raises(TypeError):
        OSC.Axles(fa, "dummy")
    with pytest.raises(TypeError):
        axles.add_axle("dummy")


class TestVehicle:
    @pytest.fixture(name="bb")
    def fix_bb(self):
        return OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)

    @pytest.fixture(name="fa")
    def fix_fa(self):
        return OSC.Axle(2, 2, 2, 1, 1)

    @pytest.fixture(name="ba")
    def fix_ba(self):
        return OSC.Axle(1, 1, 2, 1, 1)

    @pytest.fixture(name="simple_veh")
    def fix_simple_veh(self, bb, fa, ba):
        return OSC.Vehicle(
            "mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10
        )

    @pytest.fixture(name="simple_veh_mass")
    def fix_simple_veh_mass(self, bb, fa, ba):
        return OSC.Vehicle(
            "mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10, 2000
        )

    @pytest.fixture(name="extended_veh")
    def fix_extended_veh(self, bb, fa, ba):
        return OSC.Vehicle(
            "mycar",
            OSC.VehicleCategory.car,
            bb,
            fa,
            ba,
            150,
            10,
            10,
            2000,
            "model",
            1,
            1,
            OSC.Role.police,
        )

    @pytest.fixture(name="trailer_veh")
    def fix_trailer_veh(self, bb, fa, ba):
        return OSC.Vehicle(
            "mycar",
            OSC.VehicleCategory.car,
            bb,
            fa,
            ba,
            150,
            10,
            10,
            2000,
            "model",
            1,
            1,
            OSC.Role.police,
            trailer_hitch=OSC.HitchCoupler(1),
            trailer_coupler=OSC.HitchCoupler(2),
            trailer="my_trailer",
        )

    @pytest.fixture(name="trailer_veh_sceobj")
    def fix_trailer_veh_sceobj(self, bb, fa, ba):
        sceobj = OSC.ScenarioObject(
            "my_trailer",
            OSC.CatalogReference("VehcileCatalog", "some_trailer"),
        )
        return OSC.Vehicle(
            "mycar",
            OSC.VehicleCategory.car,
            bb,
            fa,
            ba,
            150,
            10,
            10,
            2000,
            "model",
            1,
            1,
            OSC.Role.police,
            trailer_hitch=OSC.HitchCoupler(1),
            trailer_coupler=OSC.HitchCoupler(2),
            trailer=sceobj,
        )

    @pytest.mark.parametrize(
        "vehicle_to_parse",
        [
            "simple_veh",
            "simple_veh_mass",
            "extended_veh",
            "trailer_veh",
            "trailer_veh_sceobj",
        ],
    )
    def test_base(self, vehicle_to_parse, request):
        vehicle = request.getfixturevalue(vehicle_to_parse)
        prettyprint(vehicle.get_element())

    def test_base_property(self, simple_veh, ba):
        simple_veh.add_property_file("propfile.xml")
        simple_veh.add_property("myprop", "12")
        simple_veh.add_axle(ba)
        param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
        simple_veh.add_parameter(param)

        prettyprint(simple_veh.get_element())

    @pytest.mark.parametrize(
        "vehicle_to_parse",
        [
            "simple_veh",
            "simple_veh_mass",
            "extended_veh",
            "trailer_veh",
            "trailer_veh_sceobj",
        ],
    )
    def test_eq_copy(self, vehicle_to_parse, request):
        vehicle = request.getfixturevalue(vehicle_to_parse)
        veh_copy = copy.deepcopy(vehicle)
        assert vehicle == veh_copy

    def test_eq(self, bb, ba, fa):
        veh1 = OSC.Vehicle(
            "mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10
        )
        veh2 = OSC.Vehicle(
            "mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10
        )
        assert veh1 == veh2

    def test_neq(self, bb, ba, fa):
        veh1 = OSC.Vehicle(
            "mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 11
        )
        veh2 = OSC.Vehicle(
            "mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10
        )
        assert veh1 != veh2

    def test_neq_extended(self, simple_veh, extended_veh):
        assert simple_veh != extended_veh

    def test_neq_trailer(self, trailer_veh, extended_veh):
        assert trailer_veh != extended_veh

    def test_type_error_bb(self, fa, ba):
        with pytest.raises(TypeError):
            OSC.Vehicle(
                "car",
                OSC.VehicleCategory.bicycle,
                "dummy",
                fa,
                ba,
                150,
                10,
                10,
            )

    def test_type_error_ba(self, bb, ba):
        with pytest.raises(TypeError):
            OSC.Vehicle(
                "car",
                OSC.VehicleCategory.bicycle,
                bb,
                "dummy",
                ba,
                150,
                10,
                10,
            )

    def test_type_error_fa(self, fa, bb):
        with pytest.raises(TypeError):
            OSC.Vehicle(
                "car",
                OSC.VehicleCategory.bicycle,
                bb,
                fa,
                "dummy",
                150,
                10,
                10,
            )

    def test_value_error_type(self, bb, fa, ba):
        with pytest.raises(ValueError):
            OSC.Vehicle("car", "dummy", bb, fa, ba, 150, 10, 10)

    def test_wrong_param_addition(self, simple_veh):
        with pytest.raises(TypeError):
            simple_veh.add_parameter("dummy")

    def test_wrong_axle_addition(self, simple_veh):
        with pytest.raises(TypeError):
            simple_veh.add_axle("dummy")

    def test_role_error(self, bb, fa, ba):
        with pytest.raises(ValueError):
            OSC.Vehicle(
                "car",
                OSC.VehicleCategory.bicycle,
                bb,
                fa,
                ba,
                150,
                10,
                10,
                role="dummy",
            )

    @pytest.mark.parametrize(
        "vehicle_to_parse",
        [
            "simple_veh",
            "simple_veh_mass",
            "extended_veh",
            "trailer_veh",
            "trailer_veh_sceobj",
        ],
    )
    def test_parse(self, vehicle_to_parse, request):
        vehicle = request.getfixturevalue(vehicle_to_parse)
        parsed_vehicle = OSC.Vehicle.parse(vehicle.get_element())
        assert vehicle == parsed_vehicle

    @pytest.mark.parametrize(
        ["vehicle_to_validate", "version", "expected"],
        [
            ("simple_veh", 0, ValidationResponse.OK),
            ("simple_veh", 1, ValidationResponse.OK),
            ("simple_veh", 2, ValidationResponse.OK),
            ("simple_veh", 3, ValidationResponse.OK),
            ("simple_veh_mass", 0, ValidationResponse.OSC_VERSION),
            ("simple_veh_mass", 1, ValidationResponse.OK),
            ("simple_veh_mass", 2, ValidationResponse.OK),
            ("simple_veh_mass", 3, ValidationResponse.OK),
            ("extended_veh", 0, ValidationResponse.OSC_VERSION),
            ("extended_veh", 1, ValidationResponse.OSC_VERSION),
            ("extended_veh", 2, ValidationResponse.OK),
            ("extended_veh", 3, ValidationResponse.OK),
            ("trailer_veh", 0, ValidationResponse.OSC_VERSION),
            ("trailer_veh", 1, ValidationResponse.OSC_VERSION),
            ("trailer_veh", 2, ValidationResponse.OSC_VERSION),
            ("trailer_veh", 3, ValidationResponse.OK),
            ("trailer_veh_sceobj", 0, ValidationResponse.OSC_VERSION),
            ("trailer_veh_sceobj", 1, ValidationResponse.OSC_VERSION),
            ("trailer_veh_sceobj", 2, ValidationResponse.OSC_VERSION),
            ("trailer_veh_sceobj", 3, ValidationResponse.OK),
        ],
    )
    def test_xml_validation(
        self, vehicle_to_validate, version, expected, request
    ):
        veh = request.getfixturevalue(vehicle_to_validate)
        assert version_validation("Vehicle", veh, version) == expected


class TestPedestrian:

    @pytest.fixture()
    def ped(self, bb):
        ped = OSC.Pedestrian(
            "myped",
            100,
            OSC.PedestrianCategory.pedestrian,
            bb,
            "ped",
            OSC.Role.police,
        )
        return ped

    @pytest.fixture(name="ped3")
    def pedestrian_3(self, bb):
        ped3 = OSC.Pedestrian(
            "myped", 100, OSC.PedestrianCategory.pedestrian, bb, "test_model"
        )
        return ped3

    def test_prettyprint(self, ped):
        prettyprint(ped.get_element())

    def test_add_property_file(self, ped):
        ped.add_property_file("propfile.xml")
        prettyprint(ped.get_element())
        assert ped.properties is not None

    def test_add_property(self, ped):
        ped.add_property("myprop", "12")
        prettyprint(ped.get_element())
        assert ped.properties is not None

    def test_add_parameter(self, ped):
        param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
        ped.add_parameter(param)
        prettyprint(ped.get_element())
        assert ped.parameters is not None

    def test_eq(self, ped, bb):
        param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
        ped2 = OSC.Pedestrian(
            "myped",
            100,
            OSC.PedestrianCategory.pedestrian,
            bb,
            "ped",
            OSC.Role.police,
        )
        ped2.add_property_file("propfile.xml")
        ped2.add_property("myprop", "12")
        ped2.add_parameter(param)

        ped.add_property_file("propfile.xml")
        ped.add_property("myprop", "12")
        ped.add_parameter(param)
        assert ped == ped2

    def test_neq(self, ped3, ped):
        assert ped != ped3

    def test_parse(self, ped):
        ped4 = OSC.Pedestrian.parse(ped.get_element())
        assert ped4 == ped

    def test_dump_to_catalog(self, ped, tmpdir):
        ped.dump_to_catalog(
            os.path.join(tmpdir, "my_catalog.xosc"),
            "PedestrianCatalog",
            "test catalog",
            "Mandolin",
        )

    def version_validation(self, ped, ped3):
        assert (
            version_validation("Pedestrian", ped, 0)
            == ValidationResponse.OSC_VERSION
        )
        assert (
            version_validation("Pedestrian", ped, 1)
            == ValidationResponse.OSC_VERSION
        )
        assert (
            version_validation("Pedestrian", ped, 2) == ValidationResponse.OK
        )

        assert (
            version_validation("Pedestrian", ped3, 0) == ValidationResponse.OK
        )
        assert (
            version_validation("Pedestrian", ped3, 1) == ValidationResponse.OK
        )
        assert (
            version_validation("Pedestrian", ped3, 2) == ValidationResponse.OK
        )

    def test_invalid_input(self, bb, ped):
        with pytest.raises(ValueError):
            OSC.Pedestrian("myped", 100, "dummy", bb, "ped", OSC.Role.police)
        with pytest.raises(TypeError):
            OSC.Pedestrian(
                "myped",
                100,
                OSC.PedestrianCategory.pedestrian,
                "dummy",
                "ped",
                OSC.Role.police,
            )
        with pytest.raises(ValueError):
            OSC.Pedestrian(
                "myped",
                100,
                OSC.PedestrianCategory.pedestrian,
                bb,
                "ped",
                "dummy",
            )
        with pytest.raises(TypeError):
            ped.add_parameter("dummy")


class TestMiscObject:
    @pytest.fixture()
    def misc_obj(self, bb):
        obs = OSC.MiscObject(
            "myobstacle", 100, OSC.MiscObjectCategory.obstacle, bb
        )
        return obs

    @pytest.fixture()
    def param(self):
        param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
        return param

    @pytest.fixture()
    def param2(self):
        param2 = OSC.Parameter("myparam1", OSC.ParameterType.double, "0.01")
        return param2

    def test_prettyprint(self, misc_obj):
        prettyprint(misc_obj.get_element())

    def test_add_property_file(self, misc_obj):
        misc_obj.add_property_file("propfile.xml")
        misc_obj.add_property_file("propfile2.xml")
        prettyprint(misc_obj.get_element())
        assert misc_obj.properties is not None
        misc_obj.add_property("myprop", "12")
        assert len(misc_obj.properties.properties) == 1
        assert len(misc_obj.properties.files) == 2

    def test_add_parameter(self, misc_obj, param):
        param2 = OSC.Parameter("myparam1", OSC.ParameterType.double, "0.01")
        misc_obj.add_parameter(param)
        misc_obj.add_parameter(param2)
        prettyprint(misc_obj.get_element())
        assert misc_obj.parameters is not None
        assert len(misc_obj.parameters.parameters) == 2

    def test_eq(self, misc_obj, param, param2, bb):
        misc_obj2 = OSC.MiscObject(
            "myobstacle", 100, OSC.MiscObjectCategory.obstacle, bb
        )
        misc_obj2.add_property_file("propfile.xml")
        misc_obj2.add_property_file("propfile2.xml")
        misc_obj2.add_property("myprop", "12")
        misc_obj2.add_parameter(param)
        misc_obj2.add_parameter(param2)

        misc_obj.add_property_file("propfile.xml")
        misc_obj.add_property_file("propfile2.xml")
        misc_obj.add_property("myprop", "12")
        misc_obj.add_parameter(param)
        misc_obj.add_parameter(param2)
        assert misc_obj == misc_obj2

    def test_parse(self, misc_obj, bb):
        misc_obj3 = OSC.MiscObject(
            "myobstacle", 100, OSC.MiscObjectCategory.tree, bb
        )
        misc_obj4 = OSC.MiscObject.parse(misc_obj3.get_element())
        assert misc_obj3 == misc_obj4
        misc_obj5 = OSC.MiscObject.parse(misc_obj.get_element())
        prettyprint(misc_obj5.get_element())
        assert misc_obj5 == misc_obj

    def test_neq(self, misc_obj, bb):
        misc_obj3 = OSC.MiscObject(
            "myobstacle", 100, OSC.MiscObjectCategory.building, bb
        )
        assert misc_obj != misc_obj3
        misc_obj4 = OSC.MiscObject(
            "myobstacle", 200, OSC.MiscObjectCategory.obstacle, bb
        )
        assert misc_obj != misc_obj4
        bb2 = OSC.BoundingBox(3, 5, 1.5, 1.5, 0, 0.2)
        misc_obj5 = OSC.MiscObject(
            "myobstacle", 100, OSC.MiscObjectCategory.obstacle, bb2
        )
        assert misc_obj != misc_obj5

    def test_dump_to_catalog(self, misc_obj, tmpdir):
        misc_obj.dump_to_catalog(
            os.path.join(tmpdir, "my_catalog.xosc"),
            "MiscObjectCatalog",
            "test catalog",
            "Mandolin",
        )

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OK),
            (1, ValidationResponse.OK),
            (2, ValidationResponse.OK),
            (3, ValidationResponse.OK),
        ],
    )
    def test_version_validation(self, version, expected, misc_obj):
        assert version_validation("MiscObject", misc_obj, version) == expected

    def test_invalid_input(self, bb):
        with pytest.raises(ValueError):
            OSC.MiscObject("mycar", 100, "dummy", bb)
        with pytest.raises(TypeError):
            OSC.MiscObject(
                "mycar", 100, OSC.MiscObjectCategory.obstacle, "dummy"
            )

    def test_optionals(self, bb):
        misc_obj6 = OSC.MiscObject(
            "myobstacle", 100, OSC.MiscObjectCategory.obstacle, bb
        )
        parsed_obj = OSC.MiscObject.parse(misc_obj6.get_element())
        assert parsed_obj.properties == OSC.Properties()
        OSC.VersionBase().setVersion(minor=2)
        parsed_obj2 = OSC.MiscObject.parse(misc_obj6.get_element())
        assert len(parsed_obj2.properties.properties) == 0


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

    assert (
        version_validation("EntitySelection", ent, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("EntitySelection", ent, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("EntitySelection", ent, 2) == ValidationResponse.OK
    )

    with pytest.raises(ValueError):
        OSC.Entity("ego", object_type="dummy")
    with pytest.raises(ValueError):
        OSC.Entity("ego", object_type=["dummy", OSC.ObjectType.pedestrian])


def test_scenarioobject():
    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")
    cnt = OSC.Controller("mycontroller", prop)

    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)
    veh = OSC.Vehicle(
        "mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10
    )
    veh.add_property_file("propfile.xml")
    veh.add_property("myprop", "12")
    veh.add_axle(ba)
    param = OSC.Parameter("mypar", OSC.ParameterType.integer, "1")
    veh.add_parameter(param)
    cnt2 = [
        OSC.Controller("mycontroller", prop),
        OSC.Controller("mycontroller_2", prop),
    ]
    so = OSC.ScenarioObject("name", veh, cnt)
    so2 = OSC.ScenarioObject("name", veh, cnt)
    so3 = OSC.ScenarioObject("name", veh, cnt2)
    prettyprint(so.get_element())
    assert so == so2
    assert so != so3
    prettyprint(so3.get_element())
    so4 = OSC.ScenarioObject.parse(so.get_element())

    assert so4 == so
    so5 = OSC.ScenarioObject.parse(so3.get_element())
    assert so5 == so3
    assert version_validation("ScenarioObject", so, 0) == ValidationResponse.OK
    assert version_validation("ScenarioObject", so, 1) == ValidationResponse.OK
    assert version_validation("ScenarioObject", so, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.ScenarioObject("my car", "dummy")
    with pytest.raises(TypeError):
        OSC.ScenarioObject("my car", veh, "dummy")


def test_entities():
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)
    veh = OSC.Vehicle(
        "mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10
    )
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

    assert version_validation("Entities", entities, 0) == ValidationResponse.OK
    assert version_validation("Entities", entities, 1) == ValidationResponse.OK
    assert version_validation("Entities", entities, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        entities.add_scenario_object("asdf", "dummy")
    with pytest.raises(TypeError):
        entities.add_scenario_object("asdf", veh, "dummy")
    with pytest.raises(ValueError):
        entities.add_entity_bytype("qwer", "dummy")


def test_controller(tmpdir):
    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")

    cnt = OSC.Controller("mycontroler", prop)
    prettyprint(cnt.get_element())
    cnt2 = OSC.Controller("mycontroler", prop)
    cnt3 = OSC.Controller("mycontroler2", prop)
    assert cnt == cnt2
    assert cnt != cnt3

    assert version_validation("Controller", cnt, 0) == ValidationResponse.OK
    assert version_validation("Controller", cnt, 1) == ValidationResponse.OK
    assert version_validation("Controller", cnt, 2) == ValidationResponse.OK

    cnt.dump_to_catalog(
        os.path.join(tmpdir, "my_catalog.xosc"),
        "ControllerCatalog",
        "test catalog",
        "Mandolin",
    )

    with pytest.raises(TypeError):
        OSC.Controller("my cnt", "dummy")
    with pytest.raises(TypeError):
        cnt.add_parameter("dummy")


def test_controller_in_Entities():
    bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
    fa = OSC.Axle(2, 2, 2, 1, 1)
    ba = OSC.Axle(1, 1, 2, 1, 1)
    veh = OSC.Vehicle(
        "mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10
    )

    prop = OSC.Properties()
    prop.add_property("mything", "2")
    prop.add_property("theotherthing", "true")

    cnt = OSC.Controller("mycontroler", prop)
    cnt2 = OSC.Controller("mycontroler", prop)

    entities = OSC.Entities()
    entities.add_scenario_object("Target_1", veh, cnt)

    prettyprint(entities.get_element())

    entities2 = OSC.Entities()
    entities2.add_scenario_object("Target_1", veh, cnt)

    entities3 = OSC.Entities()
    entities3.add_scenario_object("Target_2", veh, cnt)
    assert entities == entities2
    assert entities != entities3

    entities_multi_cnt = OSC.Entities()
    entities_multi_cnt.add_scenario_object("Target_2", veh, [cnt, cnt2])
    prettyprint(entities_multi_cnt.get_element())
    assert entities3 != entities_multi_cnt

    assert version_validation("Entities", entities, 0) == ValidationResponse.OK
    assert version_validation("Entities", entities, 1) == ValidationResponse.OK
    assert version_validation("Entities", entities, 2) == ValidationResponse.OK

    assert (
        version_validation("Entities", entities_multi_cnt, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("Entities", entities_multi_cnt, 1)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("Entities", entities_multi_cnt, 2)
        == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        entities_multi_cnt.add_scenario_object("tar", veh, [cnt, "dummy"])


def test_external_object():
    ext_obj = OSC.ExternalObjectReference("my object")
    ext_obj2 = OSC.ExternalObjectReference("my object")
    ext_obj3 = OSC.ExternalObjectReference("my object 2")

    assert ext_obj == ext_obj2
    assert ext_obj != ext_obj3

    ext_obj4 = OSC.ExternalObjectReference.parse(ext_obj.get_element())
    assert ext_obj == ext_obj4
    assert (
        version_validation("ExternalObjectReference", ext_obj, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert (
        version_validation("ExternalObjectReference", ext_obj, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("ExternalObjectReference", ext_obj, 2)
        == ValidationResponse.OK
    )


class TestEntityDistribution:
    def setup_method(self):
        self.empty_input = None
        self.catalog_ref = OSC.CatalogReference("VehicleCatalog", "Vehicle")

        bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
        fa = OSC.Axle(2, 2, 2, 1, 1)
        ra = OSC.Axle(1, 1, 2, 1, 1)
        self.vehicle = OSC.Vehicle(
            name="mycar",
            vehicle_type=OSC.VehicleCategory.car,
            boundingbox=bb,
            frontaxle=fa,
            rearaxle=ra,
            max_speed=150,
            max_acceleration=10,
            max_deceleration=10,
        )
        bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
        self.pedestrian = OSC.Pedestrian(
            name="mypedestrian",
            mass=70,
            category=OSC.PedestrianCategory.pedestrian,
            boundingbox=bb,
        )
        prop_1 = OSC.Properties()
        prop_1.add_property("myprop1", "1")
        prop_2 = OSC.Properties()
        prop_2.add_property("myprop2", "2")
        self.controller_1 = OSC.Controller("MyController1", prop_1)
        self.controller_2 = OSC.Controller("MyController2", prop_2)
        self.controller_catalog_1 = OSC.CatalogReference(
            "ControllerCatalog", "MyControllerCatalog1"
        )
        self.controller_catalog_2 = OSC.CatalogReference(
            "ControllerCatalog", "MyControllerCatalog2"
        )
        self.catalog_ref_list = [
            self.controller_catalog_1,
            self.controller_catalog_2,
        ]
        self.controller_list = [self.controller_1, self.controller_2]

        self.entity_distribution = OSC.EntityDistribution()
        self.entity_distribution.setVersion(1, 3)

    @pytest.mark.parametrize(
        ["weight", "entityobject_key", "controller_key", "expected"],
        [
            (
                -1,
                "empty_input",
                "empty_input",
                (True, ValueError, "Weight must be a non-negative value"),
            ),
            (
                0.5,
                "empty_input",
                "empty_input",
                (
                    True,
                    TypeError,
                    "entityobject must be of type CatalogReference, Vehicle, or Pedestrian",
                ),
            ),
            (0.5, "catalog_ref", "empty_input", (False, None, None)),
            (0.5, "vehicle", "empty_input", (False, None, None)),
            (0.5, "pedestrian", "empty_input", (False, None, None)),
            (
                0.5,
                "catalog_ref",
                "vehicle",
                (
                    True,
                    TypeError,
                    "controller input is not of type CatalogReference or Controller",
                ),
            ),
            (0.5, "catalog_ref", "controller_catalog_1", (False, None, None)),
            (0.5, "catalog_ref", "controller_1", (False, None, None)),
            (0.5, "catalog_ref", "catalog_ref_list", (False, None, None)),
            (0.5, "catalog_ref", "controller_list", (False, None, None)),
        ],
    )
    def test_add_entity_distribution(
        self, weight, entityobject_key, controller_key, expected
    ):
        entityobject = getattr(self, entityobject_key)
        controller = getattr(self, controller_key)
        expect_throw, expected_exception, expected_message = expected

        if expect_throw:
            with pytest.raises(expected_exception) as excinfo:
                self.entity_distribution.add_entity_distribution_entry(
                    weight, entityobject, controller
                )
            assert str(excinfo.value) == expected_message

    def test_add_entity_distribution_valid(self):
        self.entity_distribution.add_entity_distribution_entry(
            0.5, self.catalog_ref, self.controller_catalog_1
        )
        prettyprint(self.entity_distribution.get_element())

    def test_eq(self):
        entity_distribution_1 = OSC.EntityDistribution()
        entity_distribution_1.setVersion(1, 3)
        entity_distribution_1.add_entity_distribution_entry(
            0.5, self.catalog_ref, self.controller_catalog_1
        )

        entity_distribution_2 = OSC.EntityDistribution()
        entity_distribution_2.setVersion(1, 3)
        entity_distribution_2.add_entity_distribution_entry(
            0.5, self.catalog_ref, self.controller_catalog_1
        )

        assert entity_distribution_1 == entity_distribution_2

    def test_neq(self):
        entity_distribution_1 = OSC.EntityDistribution()
        entity_distribution_1.setVersion(1, 3)
        entity_distribution_1.add_entity_distribution_entry(
            0.5, self.catalog_ref, self.controller_catalog_1
        )

        entity_distribution_2 = OSC.EntityDistribution()
        entity_distribution_2.setVersion(1, 3)
        entity_distribution_2.add_entity_distribution_entry(
            0.5, self.catalog_ref, self.controller_catalog_2
        )

        assert entity_distribution_1 != entity_distribution_2

    def test_parse(self):
        self.entity_distribution.add_entity_distribution_entry(
            0.5, self.catalog_ref, self.controller_catalog_1
        )
        parsed_entity_distribution = OSC.EntityDistribution.parse(
            self.entity_distribution.get_element()
        )
        assert self.entity_distribution == parsed_entity_distribution

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OSC_VERSION),
            (1, ValidationResponse.OSC_VERSION),
            (2, ValidationResponse.OSC_VERSION),
            (3, ValidationResponse.OK),
        ],
    )
    def test_validate_xml(self, version, expected):
        self.entity_distribution.add_entity_distribution_entry(
            0.5, self.catalog_ref, self.controller_catalog_1
        )
        assert (
            version_validation(
                "EntityDistribution", self.entity_distribution, version
            )
            == expected
        )


class TestTrafficDistribution:
    def setup_method(self):
        self.entity_distribution = OSC.EntityDistribution()
        self.entity_distribution.setVersion(1, 3)
        self.catalog_ref = OSC.CatalogReference("VehicleCatalog", "Vehicle")
        self.entity_distribution.add_entity_distribution_entry(
            0.5, self.catalog_ref
        )

        self.traffic_distribution = OSC.TrafficDistribution()
        self.traffic_distribution.setVersion(1, 3)
        self.invalid_entity_distribution = "invalid_entity_distribution"
        self.properties = None
        self.invalid_properties = "invalid_properties"

    @pytest.mark.parametrize(
        "weight, entity_distribution, properties, expected_exception, expected_message",
        [
            (
                -0.5,
                "entity_distribution",
                "properties",
                ValueError,
                "Weight must be a non-negative value",
            ),
            (
                0.5,
                "invalid_entity_distribution",
                "properties",
                TypeError,
                "entity_distribution must be of type EntityDistribution",
            ),
            (
                0.5,
                "entity_distribution",
                "invalid_properties",
                TypeError,
                "properties must be of type Properties or None",
            ),
        ],
    )
    def test_add_traffic_distribution_entry_param(
        self,
        weight,
        entity_distribution,
        properties,
        expected_exception,
        expected_message,
    ):
        # Setup valid and invalid objects
        entity_distribution = getattr(self, entity_distribution)
        properties = getattr(self, properties)

        with pytest.raises(expected_exception) as excinfo:
            self.traffic_distribution.add_traffic_distribution_entry(
                weight, entity_distribution, properties
            )
        assert str(excinfo.value) == expected_message

    def test_add_traffic_distribution_entry_valid(self):
        self.traffic_distribution.add_traffic_distribution_entry(
            0.5, self.entity_distribution
        )
        prettyprint(self.entity_distribution.get_element())

    def test_eq(self):
        traffic_distribution_1 = OSC.TrafficDistribution()
        traffic_distribution_1.setVersion(1, 3)
        traffic_distribution_1.add_traffic_distribution_entry(
            0.5, self.entity_distribution
        )

        traffic_distribution_2 = OSC.TrafficDistribution()
        traffic_distribution_2.setVersion(1, 3)
        traffic_distribution_2.add_traffic_distribution_entry(
            0.5, self.entity_distribution
        )

        assert traffic_distribution_1 == traffic_distribution_2

    def test_neq(self):
        traffic_distribution_1 = OSC.TrafficDistribution()
        traffic_distribution_1.setVersion(1, 3)
        traffic_distribution_1.add_traffic_distribution_entry(
            0.5, self.entity_distribution
        )

        traffic_distribution_2 = OSC.TrafficDistribution()
        traffic_distribution_2.setVersion(1, 3)
        traffic_distribution_2.add_traffic_distribution_entry(
            1, self.entity_distribution
        )

        assert traffic_distribution_1 != traffic_distribution_2

    def test_parse(self):
        self.traffic_distribution.add_traffic_distribution_entry(
            0.5, self.entity_distribution
        )
        parsed_traffic_distribution = OSC.TrafficDistribution.parse(
            self.traffic_distribution.get_element()
        )
        assert self.traffic_distribution == parsed_traffic_distribution

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OSC_VERSION),
            (1, ValidationResponse.OSC_VERSION),
            (2, ValidationResponse.OSC_VERSION),
            (3, ValidationResponse.OK),
        ],
    )
    def test_validate_xml(self, version, expected):
        self.traffic_distribution.add_traffic_distribution_entry(
            0.5, self.entity_distribution
        )
        assert (
            version_validation(
                "TrafficDistribution", self.traffic_distribution, version
            )
            == expected
        )
