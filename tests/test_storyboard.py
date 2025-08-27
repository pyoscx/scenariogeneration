"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import datetime as dt
import os

import pytest

from scenariogeneration import prettyprint
from scenariogeneration import xosc as OSC
from scenariogeneration.xosc import (
    Trigger,
    ValueTrigger,
    ConditionEdge,
    SimulationTimeCondition,
    Rule,
)
from scenariogeneration.xosc.enumerations import _MINOR_VERSION
from .xml_validator import ValidationResponse, version_validation

EGO_NAME = "Ego"
TARGET_NAME = "target"


@pytest.fixture(autouse=True)
def reset_version():
    OSC.enumerations.VersionBase().setVersion(minor=_MINOR_VERSION)


@pytest.fixture(name="TD")
def transition_dynamics():
    td = OSC.TransitionDynamics(
        OSC.DynamicsShapes.step, OSC.DynamicsDimension.rate, 1
    )
    return td


@pytest.fixture(name="trigcond")
def trigger_condition():
    trigcond = OSC.TimeToCollisionCondition(
        10,
        OSC.Rule.equalTo,
        position=OSC.WorldPosition(),
        freespace=False,
    )
    return trigcond


@pytest.fixture(name="speedaction")
def speed_action(TD):
    return OSC.AbsoluteSpeedAction(50, TD)


@pytest.fixture(name="trigger", autouse=True)
def test_trigger(trigcond):
    return OSC.EntityTrigger(
        "mytesttrigger", 0.2, OSC.ConditionEdge.rising, trigcond, "Target_1"
    )


@pytest.fixture(autouse=True)
def init():
    init = OSC.Init()
    step_time = OSC.TransitionDynamics(
        OSC.DynamicsShapes.step, OSC.DynamicsDimension.time, 1
    )

    egospeed = OSC.AbsoluteSpeedAction(0, step_time)
    egostart = OSC.TeleportAction(OSC.LanePosition(25, 0, -3, 0))

    targetspeed = OSC.AbsoluteSpeedAction(0, step_time)
    targetstart = OSC.TeleportAction(OSC.LanePosition(15, 0, -2, 0))

    init.add_init_action(EGO_NAME, egospeed)
    init.add_init_action(EGO_NAME, egostart)
    init.add_init_action(TARGET_NAME, targetspeed)
    init.add_init_action(TARGET_NAME, targetstart)
    return init


@pytest.fixture(name="default_trigger", autouse=True)
def default_trigger():
    trigger = OSC.ValueTrigger(
        "starttrigger",
        0,
        OSC.ConditionEdge.rising,
        OSC.SimulationTimeCondition(3, OSC.Rule.greaterThan),
    )
    return trigger


@pytest.fixture()
def event(default_trigger):
    _event = OSC.Event("myfirstevent", OSC.Priority.overwrite)
    _event.add_trigger(default_trigger)
    action = OSC.LongitudinalDistanceAction(
        EGO_NAME, max_deceleration=3, max_speed=50, distance=-4
    )
    _event.add_action("newspeed", action)
    return _event


@pytest.fixture(name="man")
def maneuver(event):
    man = OSC.Maneuver("my_maneuver")
    man.add_event(event)
    return man


@pytest.fixture(name="maneuver_group")
def fixture_maneuver_group_ego(man):
    mangr = OSC.ManeuverGroup("mangroup")
    mangr.add_actor(EGO_NAME)
    mangr.add_maneuver(man)
    return mangr


@pytest.fixture(name="maneuver_group_target")
def fixture_maneuver_group_target(man):
    mangr = OSC.ManeuverGroup("mangroup")
    mangr.add_actor(TARGET_NAME)
    mangr.add_maneuver
    return mangr


@pytest.fixture(name="act")
def fixture_act(maneuver_group, default_trigger):
    act = OSC.Act("my act", default_trigger)
    act.add_maneuver_group(maneuver_group)
    return act


@pytest.fixture(name="story")
def fixture_story(act):
    story = OSC.Story("mystory")
    story.add_act(act)
    return story


def test_event(trigger, speedaction):
    event = OSC.Event("myfirstevent", OSC.Priority.overwrite)
    event.add_trigger(trigger)

    event.add_action("newspeed", speedaction)

    event2 = OSC.Event("myfirstevent", OSC.Priority.overwrite)
    event2.add_trigger(trigger)
    event2.add_action("newspeed", speedaction)
    event3 = OSC.Event("myfirstevent", OSC.Priority.overwrite)
    event3.add_trigger(trigger)
    event3.add_action("newspeed", speedaction)
    event3.add_action("newspeed2", speedaction)
    assert event == event2
    assert event != event3
    event5 = OSC.Event("myfirstevent", OSC.Priority.overwrite)
    event5.add_trigger(trigger)
    event5.add_action("newspeed", speedaction)
    event5.add_action("newspeed2", speedaction)
    assert event3 == event5
    prettyprint(event3, None)

    event4 = OSC.Event.parse(event3.get_element())
    prettyprint(event4, None)
    assert event3 == event4

    assert version_validation("Event", event, 0) == ValidationResponse.OK
    assert version_validation("Event", event, 1) == ValidationResponse.OK
    assert version_validation("Event", event, 2) == ValidationResponse.OK

    assert version_validation("Event", event5, 0) == ValidationResponse.OK
    assert version_validation("Event", event5, 1) == ValidationResponse.OK
    assert version_validation("Event", event5, 2) == ValidationResponse.OK

    with pytest.raises(ValueError):
        OSC.Event("name", "dummy")
    with pytest.raises(TypeError):
        event.add_action("dummy")
    with pytest.raises(TypeError):
        event.add_trigger("dummy")
    with pytest.raises(TypeError):
        event.add_trigger(OSC.SimulationTimeCondition(3, OSC.Rule.equalTo))
    with pytest.raises(TypeError):
        event.add_trigger(OSC.SpeedCondition(5, OSC.Rule.greaterOrEqual))


def test_maneuver(tmpdir, trigger, speedaction):
    event = OSC.Event("myfirstevent", OSC.Priority.overwrite)
    event.add_trigger(trigger)
    event.add_action("newspeed", speedaction)
    man = OSC.Maneuver("my maneuver")
    man.add_event(event)
    prettyprint(man.get_element())
    man2 = OSC.Maneuver("my maneuver")
    man2.add_event(event)
    man3 = OSC.Maneuver("my maneuver")
    man3.add_event(event)
    man3.add_event(event)
    assert man == man2
    assert man != man3

    man4 = OSC.Maneuver.parse(man3.get_element())
    assert man4 == man3

    assert version_validation("Maneuver", man3, 0) == ValidationResponse.OK
    assert version_validation("Maneuver", man3, 1) == ValidationResponse.OK
    assert version_validation("Maneuver", man3, 2) == ValidationResponse.OK
    man.dump_to_catalog(
        os.path.join(tmpdir, "my_catalog.xosc"),
        "ManeuverCatalog",
        "test catalog",
        "Mandolin",
        licence=OSC.License("my lic"),
        creation_date=dt.datetime.now(),
        properties=OSC.Properties(),
    )
    with pytest.raises(TypeError):
        OSC.Maneuver("my man", "dummy")
    with pytest.raises(TypeError):
        man.add_event("dummy")
    with pytest.raises(TypeError):
        man.add_parameter("dummy")


def test_maneuvergroup(trigger, speedaction):
    event = OSC.Event("myfirstevent", OSC.Priority.overwrite)
    event.add_trigger(trigger)
    event.add_action("newspeed", speedaction)
    man = OSC.Maneuver("my maneuver")
    man.add_event(event)
    prettyprint(man.get_element())

    mangr = OSC.ManeuverGroup("mangroup")
    mangr.add_actor("Ego")
    mangr.add_maneuver(man)
    prettyprint(mangr.get_element())

    mangr2 = OSC.ManeuverGroup("mangroup")
    mangr2.add_actor("Ego")
    mangr2.add_maneuver(man)

    mangr3 = OSC.ManeuverGroup("mangroup")
    mangr3.add_actor("2Ego")
    mangr3.add_maneuver(man)
    mangr3.add_maneuver(man)
    assert mangr == mangr2
    assert mangr != mangr3

    mangr4 = OSC.ManeuverGroup.parse(mangr3.get_element())
    assert mangr4 == mangr3

    mangr5 = OSC.ManeuverGroup("with catalog")
    mangr5.add_maneuver(OSC.CatalogReference("my_catalog", "cut-in"))
    prettyprint(mangr5.get_element())
    assert (
        version_validation("ManeuverGroup", mangr3, 0) == ValidationResponse.OK
    )
    assert (
        version_validation("ManeuverGroup", mangr3, 1) == ValidationResponse.OK
    )
    assert (
        version_validation("ManeuverGroup", mangr3, 2) == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        mangr.add_maneuver("dummy")


class TestActAndStory:
    """Test Act and Story classes."""

    @pytest.fixture(name="default_act_trigger")
    def default_starttrigger(self):
        start_trigger = ValueTrigger(
            "act_start",
            0,
            ConditionEdge.none,
            SimulationTimeCondition(0, Rule.greaterThan),
        )
        return start_trigger

    @pytest.fixture(name="act3")
    def fixture_act3(self, maneuver_group, default_act_trigger):
        act3 = OSC.Act("my act", default_act_trigger)
        act3.add_maneuver_group(maneuver_group)
        act3.add_maneuver_group(maneuver_group)
        return act3

    def test_eq(self, act, maneuver_group, default_trigger):
        act2 = OSC.Act("my act", default_trigger)
        act2.add_maneuver_group(maneuver_group)
        assert act == act2

    def test_not_eq(self, act, act3):
        assert act != act3

    def test_parse(self, act):
        act4 = OSC.Act.parse(act.get_element())
        assert act4 == act
        for minor_version in range(4):
            assert (
                version_validation("Act", act, minor_version)
                == ValidationResponse.OK
            )

    def test_invalid_starttrigger(self, default_act_trigger):
        with pytest.raises(TypeError):
            OSC.Act("act", "dummy")
        with pytest.raises(TypeError):
            OSC.Act("act", default_act_trigger, "dummy")

    def test_add_invalid_maneuver_group(self, act):
        with pytest.raises(TypeError):
            act.add_maneuver_group("dummy")

    def test_optional_attr_v3(self):
        OSC.VersionBase().setVersion(minor=3)
        action = OSC.Act("my act")
        assert action.starttrigger is None
        assert action.stoptrigger == Trigger("stop")

    def test_optional_attr_v2(self, default_act_trigger):
        OSC.VersionBase().setVersion(minor=2)
        action = OSC.Act("my act")
        assert action.starttrigger == default_act_trigger
        assert action.stoptrigger == Trigger("stop")

    def test_default_triggers_v3(self, default_act_trigger):
        act5 = OSC.Act("my act", starttrigger=default_act_trigger)
        act6 = OSC.Act("my act")
        assert act6 != act5

    def test_default_starttrigger_v2(self, default_act_trigger):
        OSC.VersionBase().setVersion(minor=2)
        act5 = OSC.Act("my act", starttrigger=default_act_trigger)
        act6 = OSC.Act("my act")
        assert act6 == act5


class TestStory:
    def test_story_pretty_print(self, story):
        prettyprint(story.get_element())

    def test_story_eq(self, act, story):
        story2 = OSC.Story("mystory")
        story2.add_act(act)
        assert story == story2

    def test_story_not_eq(self, default_trigger, maneuver_group, story):
        act3 = OSC.Act("my act", default_trigger)
        act3.add_maneuver_group(maneuver_group)
        act3.add_maneuver_group(maneuver_group)

        story3 = OSC.Story("mystory")
        story3.add_act(act3)
        assert story != story3

    def test_story_parse(self, story):
        story4 = OSC.Story.parse(story.get_element())
        assert story == story4
        for minor_version in range(4):
            assert (
                version_validation("Story", story, minor_version)
                == ValidationResponse.OK
            )

    def test_invalid_story(self):
        with pytest.raises(TypeError):
            OSC.Story("name", "dummy")

    def test_add_invalid_act_to_add(self, story):
        with pytest.raises(TypeError):
            story.add_act("dummy")


def test_init():
    init = OSC.Init()
    TD = OSC.TransitionDynamics(
        OSC.DynamicsShapes.step, OSC.DynamicsDimension.rate, 1
    )
    egospeed = OSC.AbsoluteSpeedAction(10, TD)

    init.add_init_action("Ego", egospeed)
    init.add_init_action(
        "Ego", OSC.TeleportAction(OSC.WorldPosition(1, 2, 3, 0, 0, 0))
    )
    init.add_init_action("Target_1", egospeed)
    init.add_init_action(
        "Target_1", OSC.TeleportAction(OSC.WorldPosition(1, 5, 3, 0, 0, 0))
    )
    init.add_init_action("Target_2", egospeed)
    init.add_init_action(
        "Target_2", OSC.TeleportAction(OSC.WorldPosition(10, 2, 3, 0, 0, 0))
    )
    # prettyprint(init.get_element())

    init2 = OSC.Init()
    init2.add_init_action("Ego", egospeed)
    init2.add_init_action(
        "Ego", OSC.TeleportAction(OSC.WorldPosition(1, 2, 3, 0, 0, 0))
    )
    init2.add_init_action("Target_1", egospeed)
    init2.add_init_action(
        "Target_1", OSC.TeleportAction(OSC.WorldPosition(1, 5, 3, 0, 0, 0))
    )
    init2.add_init_action("Target_2", egospeed)
    init2.add_init_action(
        "Target_2", OSC.TeleportAction(OSC.WorldPosition(10, 2, 3, 0, 0, 0))
    )

    init3 = OSC.Init()
    init3.add_init_action(
        "Ego", OSC.TeleportAction(OSC.WorldPosition(1, 2, 3, 0, 0, 0))
    )
    init3.add_init_action("Target_1", egospeed)
    init3.add_init_action(
        "Target_1", OSC.TeleportAction(OSC.WorldPosition(1, 5, 3, 0, 0, 0))
    )
    init3.add_init_action("Target_2", egospeed)
    init3.add_init_action(
        "Target_2", OSC.TeleportAction(OSC.WorldPosition(10, 2, 3, 0, 0, 0))
    )
    init3.add_global_action(
        OSC.AddEntityAction("target", OSC.WorldPosition(0, 0, 0, 0))
    )
    prettyprint(init3.get_element(), None)

    assert init == init2
    assert init != init3

    init4 = OSC.Init.parse(init3.get_element())
    prettyprint(init4.get_element(), None)
    assert init3 == init4

    assert version_validation("Init", init, 0) == ValidationResponse.OK
    assert version_validation("Init", init, 1) == ValidationResponse.OK
    assert version_validation("Init", init, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        init.add_init_action("asdf", "dummy")
    with pytest.raises(TypeError):
        init.add_global_action("dummy")
    with pytest.raises(TypeError):
        init.add_user_defined_action("dummy")


class TestStoryBoardStory:
    @pytest.fixture()
    def init_story(self):
        init = OSC.Init()
        TD = OSC.TransitionDynamics(
            OSC.DynamicsShapes.step, OSC.DynamicsDimension.rate, 1
        )
        egospeed = OSC.AbsoluteSpeedAction(10, TD)

        init.add_init_action("Ego", egospeed)
        init.add_init_action(
            "Ego", OSC.TeleportAction(OSC.WorldPosition(1, 2, 3, 0, 0, 0))
        )
        init.add_init_action("Target_1", egospeed)
        init.add_init_action(
            "Target_1", OSC.TeleportAction(OSC.WorldPosition(1, 5, 3, 0, 0, 0))
        )
        init.add_init_action("Target_2", egospeed)
        init.add_init_action(
            "Target_2",
            OSC.TeleportAction(OSC.WorldPosition(10, 2, 3, 0, 0, 0)),
        )
        return init

    @pytest.fixture(name="act_story")
    def _act_story(self, trigger, speedaction):
        event = OSC.Event("myfirstevent", OSC.Priority.overwrite)
        event.add_trigger(trigger)
        event.add_action("newspeed", speedaction)
        man = OSC.Maneuver("my maneuver")
        man.add_event(event)

        mangr = OSC.ManeuverGroup("mangroup")
        mangr.add_actor("Ego")
        mangr.add_maneuver(man)

        act = OSC.Act("my act", trigger)
        act.add_maneuver_group(mangr)
        return act

    @pytest.fixture(name="story")
    def _story(self, act_story):
        story = OSC.Story("mystory")
        story.add_act(act_story)
        return story

    @pytest.fixture(name="storyboard_story")
    def _storyboard_story(self, init_story, story):
        sb = OSC.StoryBoard(init_story)
        sb.add_story(story)
        return sb

    def test_storyboard_story_prettyprint(self, storyboard_story):
        prettyprint(storyboard_story.get_element())

    def test_storyboard_story_eq(self, storyboard_story, init_story, story):
        sb2 = OSC.StoryBoard(init_story)
        sb2.add_story(story)
        assert sb2 == storyboard_story

    def test_storyboard_story_not_eq(
        self, storyboard_story, init_story, story
    ):
        sb3 = OSC.StoryBoard(init_story)
        sb3.add_story(story)
        sb3.add_story(story)
        assert storyboard_story != sb3

    def test_storyboard_story_parse(self, storyboard_story):
        sb4 = OSC.StoryBoard.parse(storyboard_story.get_element())
        assert storyboard_story == sb4

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OK),
            (1, ValidationResponse.OK),
            (2, ValidationResponse.OK),
            (3, ValidationResponse.OK),
        ],
    )
    def test_storyboard_story_version_validation(
        self, version, expected, storyboard_story
    ):
        assert (
            version_validation("Storyboard", storyboard_story, version)
            == expected
        )

    def test_storyboard_story_invalid(self, storyboard_story, story):
        with pytest.raises(TypeError):
            storyboard_story.add_story("dummy")


class TestStoryboardAct:
    @pytest.fixture()
    def _act(self, man):
        mangr = OSC.ManeuverGroup("mangroup")
        mangr.add_actor(TARGET_NAME)
        mangr.add_maneuver(man)
        starttrigger = OSC.ValueTrigger(
            "starttrigger",
            0,
            OSC.ConditionEdge.rising,
            OSC.SimulationTimeCondition(0, OSC.Rule.greaterThan),
        )
        act = OSC.Act("my_act", starttrigger)
        act.add_maneuver_group(mangr)
        return act

    @pytest.fixture(name="sb_act")
    def _story_board_act(self, init, _act):
        sb = OSC.StoryBoard(init)
        sb.add_act(_act)
        return sb

    def test_storyboard_act_prettyprint(self, sb_act):
        prettyprint(sb_act.get_element())

    def test_storyboard_act_eq(self, sb_act, init, _act):
        sb2 = OSC.StoryBoard(init)
        sb2.add_act(_act)
        assert sb2 == sb_act

    def test_storyboard_act_not_eq(self, sb_act, init, _act):
        sb3 = OSC.StoryBoard(init)
        sb3.add_act(_act)
        sb3.add_act(_act)

        assert sb_act != sb3

    def test_storyboard_act_parse(self, sb_act):
        sb4 = OSC.StoryBoard.parse(sb_act.get_element())
        assert sb_act == sb4

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OK),
            (1, ValidationResponse.OK),
            (2, ValidationResponse.OK),
            (3, ValidationResponse.OK),
        ],
    )
    def test_storyboard_act_version_validation(
        self, version, expected, sb_act
    ):
        assert version_validation("Storyboard", sb_act, version) == expected

    def test_storyboard_act_invalid(self, sb_act, _act):
        with pytest.raises(TypeError):
            sb_act.add_act("dummy")
        with pytest.raises(TypeError):
            sb_act.add_act(_act, "dummy")


class TestStoryboardManeuverGroup:
    @pytest.fixture(name="sb_mangr")
    def storyboard_maneuver_group(self, init, maneuver_group_target):
        sb = OSC.StoryBoard(init)
        sb.add_maneuver_group(maneuver_group_target)
        return sb

    def test_storyboard_maneuver_group_prettyprint(self, sb_mangr):
        prettyprint(sb_mangr.get_element())

    def test_storyboard_maneuver_group_eq(
        self, sb_mangr, init, maneuver_group_target
    ):
        sb2 = OSC.StoryBoard(init)
        sb2.add_maneuver_group(maneuver_group_target)
        assert sb_mangr == sb2

    def test_storyboard_maneuver_group_not_eq(
        self, sb_mangr, init, maneuver_group_target
    ):
        sb3 = OSC.StoryBoard(init)
        sb3.add_maneuver_group(maneuver_group_target)
        sb3.add_maneuver_group(maneuver_group_target)
        assert sb_mangr != sb3

    def test_storyboard_maneuver_group_parse(self, sb_mangr):
        sb4 = OSC.StoryBoard.parse(sb_mangr.get_element())
        assert sb_mangr == sb4

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OK),
            (1, ValidationResponse.OK),
            (2, ValidationResponse.OK),
            (3, ValidationResponse.OK),
        ],
    )
    def test_storyboard_maneuver_group_version_validation(
        self, version, expected, sb_mangr
    ):
        assert version_validation("Storyboard", sb_mangr, version) == expected

    def test_storyboard_maneuver_group_invalid(
        self, sb_mangr, maneuver_group_target
    ):
        with pytest.raises(TypeError):
            sb_mangr.add_maneuver_group("dummy")
        with pytest.raises(TypeError):
            sb_mangr.add_maneuver_group(maneuver_group_target, "dummy")
        with pytest.raises(TypeError):
            sb_mangr.add_maneuver_group(
                maneuver_group_target, stoptrigger="dummy"
            )
        with pytest.raises(TypeError):
            sb_mangr.add_maneuver_group(
                maneuver_group_target, parameters="dummy"
            )


class TestStoryboardEmpty:
    """Test StoryBoard with no elements."""

    @pytest.fixture(name="empty_storyboard")
    def storyboard_empty(self):
        return OSC.StoryBoard(OSC.Init())

    def test_empty_storyboard_prettyprint(self, empty_storyboard):
        prettyprint(empty_storyboard.get_element())

    @pytest.mark.parametrize("version", [2, 3])
    def test_empty_storyboard_eq(self, version):
        OSC.VersionBase().setVersion(minor=version)
        sb1 = OSC.StoryBoard()
        sb2 = OSC.StoryBoard()
        assert sb1 == sb2

    def test_empty_storyboard_not_eq(self, empty_storyboard):
        sb3 = OSC.StoryBoard()
        sb3.add_maneuver_group(OSC.ManeuverGroup("dummy"))
        assert empty_storyboard != sb3

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OK),
            (1, ValidationResponse.OK),
            (2, ValidationResponse.OK),
            (3, ValidationResponse.OK),
        ],
    )
    def test_empty_version_validation(
        self, version, expected, empty_storyboard
    ):
        assert (
            version_validation("Storyboard", empty_storyboard, version)
            == expected
        )

    def test_empty_storyboard_stoptrigger_v2(self, empty_storyboard):
        OSC.VersionBase().setVersion(minor=2)
        assert empty_storyboard.stoptrigger == Trigger("stop")
        sb = OSC.StoryBoard(OSC.Init(), stoptrigger=Trigger("stop"))
        assert sb == empty_storyboard

    def test_empty_storyboard_stoptrigger_v3(self, empty_storyboard):
        OSC.VersionBase().setVersion(minor=3)
        assert empty_storyboard.stoptrigger == None


class TestStoryBoardManeuver:
    def setup_method(self):
        self.egoname = "Ego"
        self.targetname = "target"

    @pytest.fixture(name="sb_mng")
    def storyboard_manuver_group(self, init, man):
        sb = OSC.StoryBoard(init)
        sb.add_maneuver(man, self.targetname)
        return sb

    def test_storyboard_maneuver_prettyprint(self, sb_mng):
        prettyprint(sb_mng.get_element())

    def test_storyboard_maneuver_eq(self, sb_mng, init, man):
        sb2 = OSC.StoryBoard(init)
        sb2.add_maneuver(man, self.targetname)
        assert sb_mng == sb2

    def test_storyboard_maneuver_not_eq(self, init, man, sb_mng):
        sb3 = OSC.StoryBoard(init)
        sb3.add_maneuver(man, self.targetname)
        sb3.add_maneuver(
            OSC.CatalogReference("mancatalog", "my_maneuver"), self.targetname
        )
        assert sb_mng != sb3

    def test_storyboard_maneuver_parse(self, sb_mng):
        sb4 = OSC.StoryBoard.parse(sb_mng.get_element())
        assert sb_mng == sb4

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OK),
            (1, ValidationResponse.OK),
            (2, ValidationResponse.OK),
            (3, ValidationResponse.OK),
        ],
    )
    def test_storyboard_maneuver_validation(self, version, expected, sb_mng):
        assert version_validation("Storyboard", sb_mng, 0) == expected

    def test_storyboard_maneuver_invalid(self, sb_mng):
        with pytest.raises(TypeError):
            sb_mng.add_maneuver("dummy", "actor")


def test_actors():
    actors = OSC.storyboard._Actors(False)
    actors.add_actor("ego")
    actors2 = OSC.storyboard._Actors(False)
    actors2.add_actor("ego")
    actors3 = OSC.storyboard._Actors(False)
    actors3.add_actor("ego")
    actors3.add_actor("target")

    prettyprint(actors)
    prettyprint(actors3, None)

    assert actors == actors2
    assert actors != actors3

    actors4 = OSC.storyboard._Actors.parse(actors3.get_element())
    prettyprint(actors4, None)
    assert actors4 == actors3
    assert version_validation("Actors", actors3, 0) == ValidationResponse.OK
    assert version_validation("Actors", actors3, 1) == ValidationResponse.OK
    assert version_validation("Actors", actors3, 2) == ValidationResponse.OK
