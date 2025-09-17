"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import datetime as dt

import pytest

from scenariogeneration import prettyprint
from scenariogeneration import xosc as OSC
from scenariogeneration.xosc.enumerations import _MINOR_VERSION

from .xml_validator import ValidationResponse, version_validation


@pytest.fixture(autouse=True)
def reset_version():
    OSC.enumerations.VersionBase().setVersion(minor=_MINOR_VERSION)


def test_road():
    controller = OSC.TrafficSignalController(
        "controllerName", 11, "ReferenceID"
    )
    roadfile = "Databases/SampleDatabase.xodr"
    road = OSC.RoadNetwork(roadfile)
    prettyprint(road.get_element(), None)
    road2 = OSC.RoadNetwork(roadfile)
    road3 = OSC.RoadNetwork(roadfile, "a")
    assert road == road2
    assert road != road3
    road.add_traffic_signal_controller(controller)
    assert version_validation("RoadNetwork", road, 0) == ValidationResponse.OK
    assert version_validation("RoadNetwork", road, 1) == ValidationResponse.OK
    assert version_validation("RoadNetwork", road, 2) == ValidationResponse.OK

    road.add_used_area_position(OSC.WorldPosition())
    with pytest.raises(OSC.NotEnoughInputArguments):
        road.get_element()
    road.add_used_area_position(OSC.WorldPosition(1, 1, 1))

    prettyprint(road.get_element(), None)

    road4 = OSC.RoadNetwork.parse(road.get_element())
    prettyprint(road4.get_element(), None)
    assert road4 == road

    assert (
        version_validation("RoadNetwork", road, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("RoadNetwork", road, 1) == ValidationResponse.OK
    assert version_validation("RoadNetwork", road, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        road.add_traffic_signal_controller("dummy")
    with pytest.raises(TypeError):
        road.add_used_area_position("dummy")


def test_catalog():
    catalog = OSC.Catalog()
    catalog.add_catalog("VehicleCatalog", "Catalogs/VehicleCatalogs")
    catalog.add_catalog("ControllerCatalog", "Catalogs/ControllerCatalogs")
    prettyprint(catalog.get_element())

    catalog2 = OSC.Catalog()
    catalog2.add_catalog("VehicleCatalog", "Catalogs/VehicleCatalogs")
    catalog2.add_catalog("ControllerCatalog", "Catalogs/ControllerCatalogs")

    catalog3 = OSC.Catalog()
    catalog3.add_catalog("VehicleCatalog", "Catalogs/VehicleCatalogs")

    assert catalog == catalog2
    assert catalog != catalog3

    catalog4 = OSC.Catalog.parse(catalog.get_element())
    prettyprint(catalog4.get_element(), None)
    assert catalog == catalog4

    assert (
        version_validation("CatalogLocations", catalog, 0)
        == ValidationResponse.OK
    )
    assert (
        version_validation("CatalogLocations", catalog, 1)
        == ValidationResponse.OK
    )
    assert (
        version_validation("CatalogLocations", catalog, 2)
        == ValidationResponse.OK
    )


class TestScenario:
    @pytest.fixture()
    def catalog(self):
        catalog = OSC.Catalog()
        catalog.add_catalog("VehicleCatalog", "Catalogs/VehicleCatalogs")
        catalog.add_catalog("ControllerCatalog", "Catalogs/ControllerCatalogs")
        return catalog

    @pytest.fixture()
    def road(self):
        roadfile = "Databases/SampleDatabase.xodr"
        road = OSC.RoadNetwork(roadfile)
        return road

    @pytest.fixture(name="TD")
    def transition_dynamic(self):
        return OSC.TransitionDynamics(
            OSC.DynamicsShapes.step, OSC.DynamicsDimension.rate, 1
        )

    @pytest.fixture()
    def story(self, TD):
        trigcond = OSC.TimeToCollisionCondition(
            10,
            OSC.Rule.equalTo,
            True,
            freespace=False,
            position=OSC.WorldPosition(),
        )

        trigger = OSC.EntityTrigger(
            "mytesttrigger",
            0.2,
            OSC.ConditionEdge.rising,
            trigcond,
            "Target_1",
        )

        event = OSC.Event("myfirstevent", OSC.Priority.overwrite)
        event.add_trigger(trigger)

        speedaction = OSC.AbsoluteSpeedAction(50, TD)
        event.add_action("newspeed", speedaction)

        man = OSC.Maneuver("my maneuver")
        man.add_event(event)

        mangr = OSC.ManeuverGroup("mangroup")
        mangr.add_actor("Ego")
        mangr.add_maneuver(man)

        act = OSC.Act("my act", trigger)
        act.add_maneuver_group(mangr)

        story = OSC.Story("mystory")
        story.add_act(act)
        return story

    @pytest.fixture()
    def entities(self):
        bb = OSC.BoundingBox(2, 5, 1.5, 1.5, 0, 0.2)
        fa = OSC.Axle(2, 2, 2, 1, 1)
        ba = OSC.Axle(1, 1, 2, 1, 1)
        veh = OSC.Vehicle(
            "mycar", OSC.VehicleCategory.car, bb, fa, ba, 150, 10, 10
        )

        entities = OSC.Entities()
        entities.add_scenario_object("Ego", veh)
        entities.add_scenario_object("Target_1", veh)
        return entities

    @pytest.fixture()
    def story_board(self, TD, story):
        init = OSC.Init()
        egospeed = OSC.AbsoluteSpeedAction(10, TD)

        init.add_init_action("Ego", egospeed)
        init.add_init_action(
            "Ego", OSC.TeleportAction(OSC.WorldPosition(1, 2, 3, 0, 0, 0))
        )
        init.add_init_action("Target_1", egospeed)
        init.add_init_action(
            "Target_1", OSC.TeleportAction(OSC.WorldPosition(1, 5, 3, 0, 0, 0))
        )

        sb = OSC.StoryBoard(init)
        sb.add_story(story)
        return sb

    @pytest.fixture()
    def variables(self):
        variables = OSC.VariableDeclarations()
        variables.add_variable(
            OSC.Variable("my_var", OSC.ParameterType.string, "hej")
        )
        return variables

    @pytest.fixture(name="monitor_dec")
    def monitor(self):
        monitor_dec = OSC.MonitorDeclarations()
        monitor_dec.add_monitor(OSC.Monitor("myMonitor", True))

        return monitor_dec

    @pytest.fixture(name="sce")
    def scenario(self, catalog, road, entities, story_board):
        sce = OSC.Scenario(
            "myscenario",
            "Mandolin",
            OSC.ParameterDeclarations(),
            entities=entities,
            storyboard=story_board,
            roadnetwork=road,
            catalog=catalog,
        )
        return sce

    def test_scenario_prettyprint(self, sce):
        prettyprint(sce.get_element(), None)

    def test_scenario_equality(
        self, sce, story_board, entities, road, catalog
    ):
        sce2 = OSC.Scenario(
            "myscenario",
            "Mandolin",
            OSC.ParameterDeclarations(),
            entities=entities,
            storyboard=story_board,
            roadnetwork=road,
            catalog=catalog,
            creation_date=dt.datetime.now(),
        )

        assert sce == sce2

    def test_scenario_neq(
        self, sce, variables, story_board, entities, road, catalog, monitor_dec
    ):
        sce3 = OSC.Scenario(
            "2myscenario",
            "Mandolin",
            OSC.ParameterDeclarations(),
            entities=entities,
            storyboard=story_board,
            roadnetwork=road,
            catalog=catalog,
            variable_declaration=variables,
        )
        prettyprint(sce3)
        assert sce != sce3

        sce4 = OSC.Scenario(
            "2myscenario",
            "Mandolin",
            OSC.ParameterDeclarations(),
            entities=sce3.entities,
            storyboard=sce3.storyboard,
            roadnetwork=sce3.roadnetwork,
            catalog=sce3.catalog,
            variable_declaration=sce3.variable_declaration,
            monitor_declarations=monitor_dec,
        )
        assert sce3 != sce4

    def test_scenario_parse(self, sce):
        sce4 = OSC.Scenario.parse(sce.get_element())
        prettyprint(sce4.get_element(), None)
        assert sce == sce4

    def test_scenario_version_2(
        self, story_board, entities, road, catalog, variables, monitor_dec
    ):
        sce3 = OSC.Scenario(
            "2myscenario",
            "Mandolin",
            OSC.ParameterDeclarations(),
            osc_minor_version=2,
            entities=entities,
            storyboard=story_board,
            roadnetwork=road,
            catalog=catalog,
            variable_declaration=variables,
            monitor_declarations=monitor_dec,
        )
        element = sce3.get_element()
        assert element is not None

    def test_scenario_dummy_args(
        self, story_board, entities, road, catalog, monitor_dec
    ):
        with pytest.raises(TypeError):
            OSC.Scenario(
                "myscenario",
                "Mandolin",
                "dummy",
                entities=entities,
                storyboard=story_board,
                roadnetwork=road,
                catalog=catalog,
            )
        with pytest.raises(TypeError):
            OSC.Scenario(
                "myscenario",
                "Mandolin",
                OSC.ParameterDeclarations(),
                entities="dummy",
                storyboard=story_board,
                roadnetwork=road,
                catalog=catalog,
            )
        with pytest.raises(TypeError):
            OSC.Scenario(
                "myscenario",
                "Mandolin",
                OSC.ParameterDeclarations(),
                entities=entities,
                storyboard="dummy",
                roadnetwork=road,
                catalog=catalog,
            )
        with pytest.raises(TypeError):
            OSC.Scenario(
                "myscenario",
                "Mandolin",
                OSC.ParameterDeclarations(),
                entities=entities,
                storyboard=story_board,
                roadnetwork="dummy",
                catalog=catalog,
            )
        with pytest.raises(TypeError):
            OSC.Scenario(
                "myscenario",
                "Mandolin",
                OSC.ParameterDeclarations(),
                entities=entities,
                storyboard=story_board,
                roadnetwork=road,
                catalog="dummy",
            )
        with pytest.raises(TypeError):
            OSC.Scenario(
                "myscenario",
                "Mandolin",
                "dummy",
                entities=entities,
                storyboard=story_board,
                roadnetwork=road,
                catalog=catalog,
                monitor_declarations=monitor_dec,
                variable_declaration="dummy",
            )
        with pytest.raises(TypeError):
            OSC.Scenario(
                "myscenario",
                "Mandolin",
                OSC.ParameterDeclarations(),
                entities=entities,
                storyboard=story_board,
                roadnetwork=road,
                catalog=catalog,
                monitor_declarations="dummy",
            )

    def test_scenario_optional_args(
        self, sce, entities, road, catalog, story_board, variables, monitor_dec
    ):
        # Test with optional arguments
        sce_with_optional = OSC.Scenario(
            "myscenario",
            "Mandolin",
            OSC.ParameterDeclarations(),
            entities=entities,
            storyboard=story_board,
            roadnetwork=road,
            catalog=catalog,
            creation_date=dt.datetime.now(),
            variable_declaration=variables,
            monitor_declarations=monitor_dec,
        )
        prettyprint(sce_with_optional.get_element(), None)
        assert sce_with_optional.monitor_declarations == monitor_dec
        assert sce_with_optional.variable_declaration == variables
