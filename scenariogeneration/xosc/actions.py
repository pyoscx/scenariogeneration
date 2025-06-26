"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
from typing import Any, Optional, Union

from .enumerations import (
    AutomaticGearType,
    CoordinateSystem,
    DynamicsShapes,
    FollowingMode,
    LateralDisplacement,
    LightMode,
    LongitudinalDisplacement,
    SpeedTargetValueType,
    VehicleComponentType,
    VehicleLightType,
    VersionBase,
)
from .exceptions import (
    NoActionsDefinedError,
    NotAValidElement,
    NotEnoughInputArguments,
    OpenSCENARIOVersionError,
    ToManyOptionalArguments,
)
from .parameters import Range
from .position import Route, Trajectory, _PositionFactory
from .utils import (
    AbsoluteSpeed,
    AnimationFile,
    CatalogReference,
    Color,
    Controller,
    DirectionOfTravelDistribution,
    DynamicsConstraints,
    Environment,
    PedestrianAnimation,
    RelativeSpeedToMaster,
    TimeReference,
    TrafficDefinition,
    TransitionDynamics,
    UserDefinedAnimation,
    UserDefinedComponent,
    UserDefinedLight,
    _AnimationTypeFactory,
    _ComponentAnimation,
    _LightState,
    _PositionType,
    _VehicleComponent,
    convert_bool,
    convert_enum,
    convert_float,
    convert_int,
    find_mandatory_field,
    get_bool_string,
)


class _GlobalActionFactory:
    @staticmethod
    def parse_globalaction(element: ET.Element) -> Any:
        if element.findall("EnvironmentAction"):
            return EnvironmentAction.parse(element)
        if element.findall("EntityAction/AddEntityAction"):
            return AddEntityAction.parse(element)
        if element.findall("EntityAction/DeleteEntityAction"):
            return DeleteEntityAction.parse(element)
        if element.findall("ParameterAction/ModifyAction/Rule/AddValue"):
            return ParameterAddAction.parse(element)
        if element.findall(
            "ParameterAction/ModifyAction/Rule/MultiplyByValue"
        ):
            return ParameterMultiplyAction.parse(element)
        if element.findall("ParameterAction/SetAction"):
            return ParameterSetAction.parse(element)
        if element.findall("VariableAction/ModifyAction/Rule/AddValue"):
            return VariableAddAction.parse(element)
        if element.findall("VariableAction/ModifyAction/Rule/MultiplyByValue"):
            return VariableMultiplyAction.parse(element)
        if element.findall("VariableAction/SetAction"):
            return VariableSetAction.parse(element)
        if element.findall(
            "InfrastructureAction/TrafficSignalAction/TrafficSignalStateAction"
        ):
            return TrafficSignalStateAction.parse(element)
        if element.findall(
            "InfrastructureAction/TrafficSignalAction/TrafficSignalControllerAction"
        ):
            return TrafficSignalControllerAction.parse(element)
        if element.findall("TrafficAction/TrafficSourceAction"):
            return TrafficSourceAction.parse(element)
        if element.findall("TrafficAction/TrafficSinkAction"):
            return TrafficSinkAction.parse(element)
        if element.findall("TrafficAction/TrafficSwarmAction"):
            return TrafficSwarmAction.parse(element)
        if element.findall("TrafficAction/TrafficStopAction"):
            return TrafficStopAction.parse(element)

        raise NotAValidElement(
            "element ", element, "is not a valid GlobalAction"
        )


class _PrivateActionFactory:
    @staticmethod
    def parse_privateaction(element: ET.Element) -> Any:
        if element.findall(
            "LongitudinalAction/SpeedAction/SpeedActionTarget/AbsoluteTargetSpeed"
        ):
            return AbsoluteSpeedAction.parse(element)
        if element.findall(
            "LongitudinalAction/SpeedAction/SpeedActionTarget/RelativeTargetSpeed"
        ):
            return RelativeSpeedAction.parse(element)
        if element.findall("LongitudinalAction/LongitudinalDistanceAction"):
            return LongitudinalDistanceAction.parse(element)
        if element.findall(
            "LateralAction/LaneChangeAction/LaneChangeTarget/AbsoluteTargetLane"
        ):
            return AbsoluteLaneChangeAction.parse(element)
        if element.findall(
            "LateralAction/LaneChangeAction/LaneChangeTarget/RelativeTargetLane"
        ):
            return RelativeLaneChangeAction.parse(element)
        if element.findall(
            "LateralAction/LaneOffsetAction/LaneOffsetTarget/AbsoluteTargetLaneOffset"
        ):
            return AbsoluteLaneOffsetAction.parse(element)
        if element.findall(
            "LateralAction/LaneOffsetAction/LaneOffsetTarget/RelativeTargetLaneOffset"
        ):
            return RelativeLaneOffsetAction.parse(element)
        if element.findall("LateralAction/LateralDistanceAction"):
            return LateralDistanceAction.parse(element)
        if element.findall("VisibilityAction"):
            return VisibilityAction.parse(element)
        if element.findall("SynchronizeAction"):
            return SynchronizeAction.parse(element)
        if element.findall("ActivateControllerAction"):
            return ActivateControllerAction.parse(element)
        if element.findall("ControllerAction"):
            return ControllerAction.parse(element)
        if element.findall("TeleportAction"):
            return TeleportAction.parse(element)
        if element.findall("RoutingAction/AssignRouteAction"):
            return AssignRouteAction.parse(element)
        if element.findall("RoutingAction/FollowTrajectoryAction"):
            return FollowTrajectoryAction.parse(element)
        if element.findall("RoutingAction/AcquirePositionAction"):
            return AcquirePositionAction.parse(element)
        if element.findall("AppearanceAction/AnimationAction"):
            return AnimationAction.parse(element)
        if element.findall("LongitudinalAction/SpeedProfileAction"):
            return SpeedProfileAction.parse(element)
        if element.findall("AppearanceAction/LightStateAction"):
            return LightStateAction.parse(element)

        raise NotAValidElement(
            "element ", element, "is not a valid PrivateAction"
        )


class _ActionType(VersionBase):
    """Helper class for typesetting."""


class _PrivateActionType(_ActionType):
    """Helper class for typesetting."""


class _Action(VersionBase):
    """Private class used to define an action, should not be used by the user.
    Used as a wrapper to create the extra elements needed.

    Parameters
    ----------
        name (str): name of the action

        action (_ActionType): any action

    Attributes
    ----------
        name (str): name of the action

        action (_ActionType): any action

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an
            instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, name: str, action: _ActionType) -> None:
        """Initalize _Action.

        Parameters
        ----------
            name (str): name of the action

            action (_ActionType): any action
        """
        self.name = name

        self.action = action

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Action):
            if (
                self.get_attributes() == other.get_attributes()
                and self.action == other.action
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "_Action":
        """Parses the xml element of _Action.

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A _Action element
            (same as generated by the class itself)

        Returns
        -------
            action (_Action): a _Action object
        """
        name = element.attrib["name"]
        if element.find("PrivateAction") is not None:
            action = _PrivateActionFactory.parse_privateaction(
                find_mandatory_field(element, "PrivateAction")
            )
        elif element.find("GlobalAction") is not None:
            action = _GlobalActionFactory.parse_globalaction(
                find_mandatory_field(element, "GlobalAction")
            )
        elif element.find("UserDefinedAction") is not None:
            action = UserDefinedAction.parse(
                find_mandatory_field(element, "UserDefinedAction")
            )
        else:
            raise NotAValidElement(element.tag, "is not a valid action")
        return _Action(name, action)

    def get_attributes(self) -> dict:
        """Returns the attributes of the _Action as a dict."""
        return {"name": self.name}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the _Action."""
        element = ET.Element("Action", attrib=self.get_attributes())
        element.append(self.action.get_element())
        return element


#### Private Actions ####

# LongitudinalAction


class AbsoluteSpeedAction(_PrivateActionType):
    """Specifies a LongitudinalAction of type SpeedAction with an absolute
    target speed.

    Parameters
    ----------
    speed : float
        The desired speed.
    transition_dynamics : TransitionDynamics
        How the change should be made.

    Attributes
    ----------
    speed : float
        The desired speed.
    transition_dynamics : TransitionDynamics
        How the change should be made.

    Methods
    -------
    parse(element)
        Parses an XML element and returns an instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, speed: float, transition_dynamics: TransitionDynamics):
        """Initialize the AbsoluteSpeedAction.

        Parameters
        ----------
        speed : float
            The desired speed.
        transition_dynamics : TransitionDynamics
            How the change should be made.
        """
        self.speed = convert_float(speed)
        if not isinstance(transition_dynamics, TransitionDynamics):
            raise TypeError(
                "transition_dynamics input not of type TransitionDynamics"
            )
        self.transition_dynamics = transition_dynamics

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AbsoluteSpeedAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.transition_dynamics == other.transition_dynamics
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "AbsoluteSpeedAction":
        """Parses the XML element of WorldPosition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        AbsoluteSpeedAction
            A world position object.
        """
        speed_element = find_mandatory_field(
            element,
            "LongitudinalAction/SpeedAction/SpeedActionTarget/AbsoluteTargetSpeed",
        )
        td_element = find_mandatory_field(
            element, "LongitudinalAction/SpeedAction/SpeedActionDynamics"
        )
        speed = speed_element.attrib["value"]
        transition_dynamics = TransitionDynamics.parse(td_element)
        return AbsoluteSpeedAction(speed, transition_dynamics)

    def get_attributes(self) -> dict:
        """Returns the attributes of the AbsoluteSpeedAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the AbsoluteSpeedAction.
        """
        return {"value": str(self.speed)}

    def get_element(self) -> ET.Element:
        """Returns the ElementTree of the AbsoluteSpeedAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the AbsoluteSpeedAction.
        """
        element = ET.Element("PrivateAction")
        longaction = ET.SubElement(element, "LongitudinalAction")
        speedaction = ET.SubElement(longaction, "SpeedAction")

        speedaction.append(
            self.transition_dynamics.get_element("SpeedActionDynamics")
        )
        speedactiontarget = ET.SubElement(speedaction, "SpeedActionTarget")

        ET.SubElement(
            speedactiontarget, "AbsoluteTargetSpeed", self.get_attributes()
        )

        return element


class RelativeSpeedAction(_PrivateActionType):
    """Creates a LongitudinalAction of type SpeedAction with a relative target.

    Parameters
    ----------
    speed : float
        The desired speed.
    entity : str
        The name of the relative target.
    valuetype : str
        The type of relative speed wanted (used for relative speed).
    continuous : bool
        Whether the controller tries to maintain the relative speed.

    Attributes
    ----------
    speed : float
        The desired speed.
    target : str
        The name of the relative target (used for relative speed).
    valuetype : str
        The type of relative speed wanted (used for relative speed).
    continuous : bool
        Whether the controller tries to maintain the relative speed.
    transition_dynamics : TransitionDynamics
        How the change should be made.

    Methods
    -------
    parse(element : ET.Element) -> "RelativeSpeedAction"
        Parses an ElementTree element and returns an instance of the class.
    get_element() -> ET.Element
        Returns the full ElementTree representation of the class.
    get_attributes() -> dict
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        speed: float,
        entity: str,
        transition_dynamics: TransitionDynamics,
        valuetype: SpeedTargetValueType = SpeedTargetValueType.delta,
        continuous: bool = True,
    ):
        """Initializes RelativeSpeedAction.

        Parameters
        ----------
        speed : float
            The speed wanted.
        entity : str
            The name of the relative target.
        transition_dynamics : TransitionDynamics
            How the change should be made.
        valuetype : SpeedTargetValueType
            The type of relative speed wanted.
        continuous : bool
            If the controller tries to keep the relative speed.
        """
        self.speed = convert_float(speed)
        self.entity = entity
        if not hasattr(SpeedTargetValueType, str(valuetype)):
            raise TypeError("valuetype input not of type SpeedTargetValueType")
        self.valuetype = valuetype

        if not isinstance(transition_dynamics, TransitionDynamics):
            raise TypeError(
                "transition_dynamics input not of type TransitionDynamics"
            )
        self.transition_dynamics = transition_dynamics
        self.continuous = convert_bool(continuous)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RelativeSpeedAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.transition_dynamics == other.transition_dynamics
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RelativeSpeedAction":
        """Parses the XML element of RelativeSpeedAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RelativeSpeedAction
            The RelativeSpeedAction object.
        """
        speed_element = find_mandatory_field(
            element,
            "LongitudinalAction/SpeedAction/SpeedActionTarget/RelativeTargetSpeed",
        )
        td_element = find_mandatory_field(
            element, "LongitudinalAction/SpeedAction/SpeedActionDynamics"
        )
        speed = speed_element.attrib["value"]
        entity = speed_element.attrib["entityRef"]
        continuous = convert_bool(speed_element.attrib["continuous"])
        valuetype = getattr(
            SpeedTargetValueType, speed_element.attrib["speedTargetValueType"]
        )
        transition_dynamics = TransitionDynamics.parse(td_element)
        return RelativeSpeedAction(
            speed, entity, transition_dynamics, valuetype, continuous
        )

    def get_attributes(self) -> dict:
        """Returns the attributes of the RelativeSpeedAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the keys related to the RelativeSpeedAction.
        """
        return {
            "entityRef": self.entity,
            "value": str(self.speed),
            "speedTargetValueType": self.valuetype.get_name(),
            "continuous": get_bool_string(self.continuous),
        }

    def get_element(self) -> ET.Element:
        """Returns the ElementTree of the RelativeSpeedAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The ElementTree representation of the RelativeSpeedAction.
        """
        element = ET.Element("PrivateAction")
        longaction = ET.SubElement(element, "LongitudinalAction")
        speedaction = ET.SubElement(longaction, "SpeedAction")
        speedaction.append(
            self.transition_dynamics.get_element("SpeedActionDynamics")
        )
        speedactiontarget = ET.SubElement(speedaction, "SpeedActionTarget")

        ET.SubElement(
            speedactiontarget, "RelativeTargetSpeed", self.get_attributes()
        )

        return element


class LongitudinalDistanceAction(_PrivateActionType):
    """The LongitudinalAction creates a LongitudinalAction of type
    LongitudinalAction with a distance target.

    Parameters
    ----------
    entity : str
        The target name.
    freespace : bool, optional
        (True) distance between bounding boxes,
        (False) distance between ref point. Default is True.
    continuous : bool, optional
        If the controller tries to keep the relative speed.
        Default is True.
    max_acceleration : float, optional
        Maximum acceleration allowed. Default is None.
    max_deceleration : float, optional
        Maximum deceleration allowed. Default is None.
    max_speed : float, optional
        Maximum speed allowed. Default is None.
    distance : float
        Distance to the entity.
    timegap : float
        Time to the target.
    coordinate_system : CoordinateSystem, optional
        The coordinate system for the distance calculation.
        Default is CoordinateSystem.entity.
    displacement : LongitudinalDisplacement, optional
        Type of displacement wanted.
        Default is LongitudinalDisplacement.any.
    max_acceleration_rate : float, optional
        Max jerk in acceleration (Valid from OpenSCENARIO 1.2).
        Default is None.
    max_deceleration_rate : float, optional
        Max jerk in deceleration (Valid from OpenSCENARIO 1.2).
        Default is None.

    Attributes
    ----------
    entity : str
        The target name.
    freespace : bool
        (True) distance between bounding boxes,
        (False) distance between ref point.
    continuous : bool
        If the controller tries to keep the relative speed.
    distance : float
        The distance to the entity.
    dynamic_constraint : DynamicsConstraints
        Dynamics constraints of the action.
    coordinate_system : CoordinateSystem
        The coordinate system for the distance calculation.
    displacement : LongitudinalDisplacement
        Type of displacement wanted.
    max_acceleration_rate : float
        Max jerk in acceleration (Valid from OpenSCENARIO 1.2).
    max_deceleration_rate : float
        Max jerk in deceleration (Valid from OpenSCENARIO 1.2).

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        entity: str,
        freespace: bool = True,
        continuous: bool = True,
        max_acceleration=None,
        max_deceleration=None,
        max_speed: float = None,
        distance: float = None,
        timeGap: float = None,
        coordinate_system: CoordinateSystem = CoordinateSystem.entity,
        displacement: LongitudinalDisplacement = LongitudinalDisplacement.any,
        max_acceleration_rate: float = None,
        max_deceleration_rate: float = None,
    ):
        """Initialize the LongitudinalDistanceAction.

        Parameters
        ----------
        entity : str
            The target name.
        freespace : bool, optional
            (True) distance between bounding boxes,
            (False) distance between ref point. Default is True.
        continuous : bool, optional
            If the controller tries to keep the relative speed.
            Default is True.
        max_acceleration : float, optional
            Maximum acceleration allowed. Default is None.
        max_deceleration : float, optional
            Maximum deceleration allowed. Default is None.
        max_speed : float, optional
            Maximum speed allowed. Default is None.
        distance : float
            Distance to the entity.
        timegap : float
            Time to the target.
        coordinate_system : CoordinateSystem, optional
            The coordinate system for the distance calculation.
            Default is CoordinateSystem.entity.
        displacement : LongitudinalDisplacement, optional
            Type of displacement wanted.
            Default is LongitudinalDisplacement.any.
        max_acceleration_rate : float, optional
            Max jerk in acceleration (Valid from OpenSCENARIO 1.2).
            Default is None.
        max_deceleration_rate : float, optional
            Max jerk in deceleration (Valid from OpenSCENARIO 1.2).
            Default is None.
        """
        self.target = entity
        self.freespace = convert_bool(freespace)
        self.continuous = convert_bool(continuous)
        self.dynamic_constraint = DynamicsConstraints(
            max_acceleration,
            max_deceleration,
            max_speed,
            max_acceleration_rate,
            max_deceleration_rate,
        )

        if distance is not None and timeGap is not None:
            raise ToManyOptionalArguments(
                "Not both of distance and timeGap can be used."
            )
        if distance is None and timeGap is None:
            raise NotEnoughInputArguments(
                "Either ds or dsLane is needed as input."
            )
        self.distance = convert_float(distance)
        self.timeGap = convert_float(timeGap)

        self.coordinate_system = convert_enum(
            coordinate_system, CoordinateSystem
        )
        self.displacement = convert_enum(
            displacement, LongitudinalDisplacement
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LongitudinalDistanceAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.dynamic_constraint == other.dynamic_constraint
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "LongitudinalDistanceAction":
        """Parses the XML element of LongitudinalAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A LongitudinalDistanceAction element
            (same as generated by the class itself).

        Returns
        -------
        LongitudinalDistanceAction
            A LongitudinalDistanceAction object.
        """
        lda_element = find_mandatory_field(
            element, "LongitudinalAction/LongitudinalDistanceAction"
        )
        entity = lda_element.attrib["entityRef"]
        freespace = convert_bool(lda_element.attrib["freespace"])
        continuous = convert_bool(lda_element.attrib["continuous"])
        distance = None
        timeGap = None
        if "distance" in lda_element.attrib:
            distance = convert_float(lda_element.attrib["distance"])
        if "timeGap" in lda_element.attrib:
            timeGap = convert_float(lda_element.attrib["timeGap"])

        coordinate_system = CoordinateSystem.entity
        if "coordinateSystem" in lda_element.attrib:
            coordinate_system = convert_enum(
                lda_element.attrib["coordinateSystem"], CoordinateSystem, False
            )
        displacement = LongitudinalDisplacement.any
        if "displacement" in lda_element.attrib:
            displacement = convert_enum(
                lda_element.attrib["displacement"],
                LongitudinalDisplacement,
                False,
            )
        max_acceleration = None
        max_deceleration = None
        max_speed = None
        constraints = None
        if lda_element.find("DynamicConstraints") is not None:
            constraints = DynamicsConstraints.parse(
                find_mandatory_field(lda_element, "DynamicConstraints")
            )
            max_acceleration = constraints.max_acceleration
            max_deceleration = constraints.max_deceleration
            max_speed = constraints.max_speed

        return LongitudinalDistanceAction(
            entity,
            freespace,
            continuous,
            max_acceleration,
            max_deceleration,
            max_speed,
            distance,
            timeGap,
            coordinate_system,
            displacement,
        )

    def get_attributes(self) -> dict:
        """Returns the attributes of the LongitudinalDistanceAction as a
        dictionary.

        as a dictionary   Reas a dictionary   turns
        -------
        dict
            A dictionary containing the attributes of the
            LongitudinalDistanceAction
        """

        retdict = {}
        retdict["entityRef"] = self.target
        retdict["freespace"] = get_bool_string(self.freespace)
        retdict["continuous"] = get_bool_string(self.continuous)
        if self.distance is not None:
            retdict["distance"] = str(self.distance)
        if self.timeGap is not None:
            retdict["timeGap"] = str(self.timeGap)
        if not self.isVersion(minor=0):
            retdict["coordinateSystem"] = self.coordinate_system.get_name()
            retdict["displacement"] = self.displacement.get_name()
        return retdict

    def get_element(self) -> ET.Element:
        """Generates an XML element tree representation of the
        LongitudinalDistanceAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The root XML element representing the
            LongitudinalDistanceAction.
        """

        element = ET.Element("PrivateAction")
        longact = ET.SubElement(element, "LongitudinalAction")

        longdistaction = ET.SubElement(
            longact, "LongitudinalDistanceAction", attrib=self.get_attributes()
        )
        if self.dynamic_constraint.is_filled():
            longdistaction.append(self.dynamic_constraint.get_element())
        return element


class SpeedProfileAction(_PrivateActionType):
    """Specifies a LongitudinalAction of type SpeedProfileAction.

    Parameters
    ----------
    speeds : list of float
        The different speed entries wanted.
    following_mode : FollowingMode
        How to follow the speed changes.
    times : list of float, optional
        Time entries when the speed entries should be achieved.
        Default is None.
    dynamics_constraint : DynamicsConstraints, optional
        Constraints for the speed profile. Default is None.
    entity : str, optional
        Name of an entity. The speeds will then be interpreted as
        relative to that entity. Default is None.

    Attributes
    ----------
    speeds : list of float
        The different speed entries wanted.
    following_mode : FollowingMode
        How to follow the speed changes.
    times : list of float, optional
        Time entries when the speed entries should be achieved.
    dynamics_constraint : DynamicsConstraints, optional
        Constraints for the speed profile.
    entity : str, optional
        Name of an entity. The speeds will then be interpreted as
        relative to that entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        speeds: list[float],
        following_mode: FollowingMode,
        times: list[float] = None,
        dynamics_constraint: DynamicsConstraints = None,
        entity: str = None,
    ):
        """Initalize the SpeedProfileAction.

        Parameters
        ----------
            speeds (list of float): the different speed entries wanted

            following_mode (FollowingMode): how to follow the speed
            changes

            times (list of float): optional time entries when the speed
            entries should be achieved. Default is None

            dynamics_constraint (DynamicsConstraints): optional
            constraints for the speed profile. Default is None

            entity (str): name of an entity, the speeds will then be
            interpreted as relative to that entity. Default is None
        """
        if times and (len(times) != len(speeds)):
            raise ValueError("times and speeds are not the same lenght")
        self.speeds = [convert_float(x) for x in speeds]
        if dynamics_constraint and not isinstance(
            dynamics_constraint, DynamicsConstraints
        ):
            raise TypeError(
                "dynamics_constraint input not of type DynamicsConstraints"
            )
        self.dynamics_constraint = dynamics_constraint
        self.following_mode = convert_enum(following_mode, FollowingMode)
        if times:
            self.times = [convert_float(x) for x in times]
        else:
            self.times = times
        self.entity = entity

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SpeedProfileAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.dynamics_constraint == other.dynamics_constraint
                and self.entity == other.entity
                and self.speeds == other.speeds
                and self.times == other.times
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "SpeedProfileAction":
        """Parses the XML element of SpeedProfileAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A SpeedProfileAction element (same as generated by the class
              itself).

        Returns
        -------
        SpeedProfileAction
            A SpeedProfileAction object.
        """
        speed_profile_element = find_mandatory_field(
            element, "LongitudinalAction/SpeedProfileAction"
        )
        following_mode = convert_enum(
            speed_profile_element.attrib["followingMode"], FollowingMode
        )
        dynamics_constraint = None
        entity = None

        if "entityRef" in speed_profile_element.attrib:
            entity = speed_profile_element.attrib["entityRef"]
        if speed_profile_element.find("DynamicConstraints") is not None:
            dynamics_constraint = DynamicsConstraints.parse(
                find_mandatory_field(
                    speed_profile_element, "DynamicConstraints"
                )
            )

        entires = speed_profile_element.findall("SpeedProfileEntry")
        speeds = []
        times = []
        for i in entires:
            if "time" in i.attrib:
                times.append(convert_float(i.attrib["time"]))
            speeds.append(convert_float(i.attrib["speed"]))

        return SpeedProfileAction(
            speeds, following_mode, times, dynamics_constraint, entity
        )

    def get_attributes(self) -> dict:
        """Returns the attributes of the SpeedProfileAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            SpeedProfileAction.
        """
        retdict = {"followingMode": self.following_mode.get_name()}
        if self.entity:
            retdict["entityRef"] = self.entity
        return retdict

    def get_element(self) -> ET.Element:
        """Generates an XML element tree representation of the
        SpeedProfileAction.

        Returns
        -------
        ET.Element
            The root XML element representing the SpeedProfileAction.

        Raises
        ------
        OpenSCENARIOVersionError
            If the OpenSCENARIO version is less than 1.2.
        """
        if not self.isVersion(minor=2):
            raise OpenSCENARIOVersionError(
                "SpeedProfileAction was introduced in OpenSCENARIO V1.2"
            )
        element = ET.Element("PrivateAction")
        longaction = ET.SubElement(element, "LongitudinalAction")
        speedaction = ET.SubElement(
            longaction, "SpeedProfileAction", attrib=self.get_attributes()
        )
        if self.dynamics_constraint is not None:
            speedaction.append(self.dynamics_constraint.get_element())

        for i, speed in enumerate(self.speeds):
            tmp_dict = {"speed": str(speed)}
            if self.times:
                tmp_dict["time"] = str(self.times[i])
            ET.SubElement(speedaction, "SpeedProfileEntry", attrib=tmp_dict)

        return element


class AbsoluteLaneChangeAction(_PrivateActionType):
    """Creates a LateralAction of type LaneChangeAction with an absolute
    target.

    Parameters
    ----------
    lane : int
        Lane to change to.
    transition_dynamics : TransitionDynamics
        How the change should be made.
    target_lane_offset : float, optional
        Offset in the target lane, if desired. Default is None.

    Attributes
    ----------
    lane : int
        Lane to change to.
    target_lane_offset : float
        Offset in the target lane, if specified.
    transition_dynamics : TransitionDynamics
        How the change should be made.

    Methods
    -------
    parse(element)
        Parses an ElementTree element and returns an instance of the
        class.
    get_element()
        Returns the full ElementTree representation of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        lane: int,
        transition_dynamics: TransitionDynamics,
        target_lane_offset: float = None,
    ):
        """Initialize AbsoluteLaneChangeAction.

        Parameters
        ----------
        lane : int
            Lane to change to.
        transition_dynamics : TransitionDynamics
            How the change should be made.
        target_lane_offset : float, optional
            Offset in the target lane, if desired. Default is None.
        """

        self.lane = convert_int(lane)
        self.target_lane_offset = convert_float(target_lane_offset)
        if not isinstance(transition_dynamics, TransitionDynamics):
            raise TypeError(
                "transition_dynamics input not of type TransitionDynamics"
            )
        self.transition_dynamics = transition_dynamics

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AbsoluteLaneChangeAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.transition_dynamics == other.transition_dynamics
                and self.target_lane_offset == other.target_lane_offset
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "AbsoluteLaneChangeAction":
        """Parses the XML element of AbsoluteLaneChangeAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            An AbsoluteLaneChangeAction element (same as generated by
            the class itself).

        Returns
        -------
        AbsoluteLaneChangeAction
            An AbsoluteLaneChangeAction object.
        """
        lca_element = find_mandatory_field(
            element, "LateralAction/LaneChangeAction"
        )
        target_lane_offset = None
        if "targetLaneOffset" in lca_element.attrib:
            target_lane_offset = convert_float(
                lca_element.attrib["targetLaneOffset"]
            )
        dynamics = TransitionDynamics.parse(
            find_mandatory_field(lca_element, "LaneChangeActionDynamics")
        )
        targetlane_element = find_mandatory_field(
            lca_element, "LaneChangeTarget/AbsoluteTargetLane"
        )
        lane = convert_int(targetlane_element.attrib["value"])

        return AbsoluteLaneChangeAction(lane, dynamics, target_lane_offset)

    def get_attributes(self) -> dict:
        """Returns the attributes of the AbsoluteLaneChangeAction as a
        dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            AbsoluteLaneChangeAction.
        """
        retdict = {}
        retdict["value"] = str(self.lane)
        return retdict

    def get_element(self) -> ET.Element:
        """Generates an XML element tree representation of the
        AbsoluteLaneChangeAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The root XML element representing the
            AbsoluteLaneChangeAction.
        """
        element = ET.Element("PrivateAction")
        laneoffset = {}
        lataction = ET.SubElement(element, "LateralAction")
        if self.target_lane_offset:
            laneoffset = {"targetLaneOffset": str(self.target_lane_offset)}
        lanechangeaction = ET.SubElement(
            lataction, "LaneChangeAction", attrib=laneoffset
        )

        lanechangeaction.append(
            self.transition_dynamics.get_element("LaneChangeActionDynamics")
        )
        lanchangetarget = ET.SubElement(lanechangeaction, "LaneChangeTarget")

        ET.SubElement(
            lanchangetarget, "AbsoluteTargetLane", self.get_attributes()
        )
        return element


class RelativeLaneChangeAction(_PrivateActionType):
    """Creates a LateralAction of type LaneChangeAction with a relative target.

    Parameters
    ----------
    lane : int
        Relative lane number.
    entity : str
        The entity to run relative to.
    transition_dynamics : TransitionDynamics
        How the change should be made.
    target_lane_offset : float, optional
        Offset in the target lane, if desired (default is None).

    Attributes
    ----------
    lane : int
        Relative lane number.
    target : str
        Target for relative lane change.
    target_lane_offset : float
        Offset in the target lane, if specified.
    transition_dynamics : TransitionDynamics
        How the change should be made.

    Methods
    -------
    parse(element)
        Parses an XML element and returns an instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        lane: int,
        entity: str,
        transition_dynamics: TransitionDynamics,
        target_lane_offset: float = None,
    ):
        """Initialize RelativeLaneChangeAction.

        Parameters
        ----------
        lane : int
            Relative lane number.
        entity : str
            The entity to run relative to.
        transition_dynamics : TransitionDynamics
            How the change should be made.
        target_lane_offset : float, optional
            Offset in the target lane, if desired. Default is None.
        """
        self.lane = convert_int(lane)
        self.target = entity
        self.target_lane_offset = convert_float(target_lane_offset)
        if not isinstance(transition_dynamics, TransitionDynamics):
            raise TypeError(
                "transition_dynamics input not of type TransitionDynamics"
            )
        self.transition_dynamics = transition_dynamics

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RelativeLaneChangeAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.transition_dynamics == other.transition_dynamics
                and self.target_lane_offset == other.target_lane_offset
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RelativeLaneChangeAction":
        """Parses the XML element of AbsoluteLaneChangeAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            An AbsoluteLaneChangeAction element (same as generated by
            the class itself).

        Returns
        -------
        AbsoluteLaneChangeAction
            An AbsoluteLaneChangeAction object.
        """
        lca_element = find_mandatory_field(
            element, "LateralAction/LaneChangeAction"
        )
        target_lane_offset = None
        if "targetLaneOffset" in lca_element.attrib:
            target_lane_offset = convert_float(
                lca_element.attrib["targetLaneOffset"]
            )
        dynamics = TransitionDynamics.parse(
            find_mandatory_field(lca_element, "LaneChangeActionDynamics")
        )
        targetlane_element = find_mandatory_field(
            lca_element, "LaneChangeTarget/RelativeTargetLane"
        )
        lane = convert_int(targetlane_element.attrib["value"])
        target = targetlane_element.attrib["entityRef"]

        return RelativeLaneChangeAction(
            lane, target, dynamics, target_lane_offset
        )

    def get_attributes(self) -> dict:
        """Returns the attributes of the RelativeLaneChangeAction as a
        dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            RelativeLaneChangeAction.
        """
        retdict = {}
        retdict["value"] = str(self.lane)
        retdict["entityRef"] = self.target
        return retdict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the RelativeLaneChangeAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the RelativeLaneChangeAction.
        """
        element = ET.Element("PrivateAction")
        laneoffset = {}
        lataction = ET.SubElement(element, "LateralAction")
        if self.target_lane_offset is not None:
            laneoffset = {"targetLaneOffset": str(self.target_lane_offset)}
        lanechangeaction = ET.SubElement(
            lataction, "LaneChangeAction", attrib=laneoffset
        )

        lanechangeaction.append(
            self.transition_dynamics.get_element("LaneChangeActionDynamics")
        )
        lanchangetarget = ET.SubElement(lanechangeaction, "LaneChangeTarget")

        ET.SubElement(
            lanchangetarget, "RelativeTargetLane", self.get_attributes()
        )
        return element


class AbsoluteLaneOffsetAction(_PrivateActionType):
    """The AbsoluteLaneOffsetAction class creates a LateralAction of type
    LaneOffsetAction with an absolute target.

    Parameters
    ----------
    value : float
        Lateral offset of the lane.
    shape : DynamicsShapes
        Shape of the offset action.
    maxlatacc : float
        Maximum allowed lateral acceleration.
    continuous : bool, optional
        If the controller tries to keep the relative speed.
        Default is True.

    Attributes
    ----------
    continuous : bool
        If the controller tries to keep the relative speed.
    value : float
        Lateral offset of the lane.
    target : str
        The name of the entity (relative only).
    dynshape : DynamicsShapes
        The shape of the action.
    maxlatacc : float
        Maximum allowed lateral acceleration.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        value: float,
        shape: DynamicsShapes,
        maxlatacc: float = None,
        continuous: bool = True,
    ):
        """Initializes the AbsoluteLaneOffsetAction.

        Parameters
        ----------
        value : float
            Lateral offset of the lane.
        shape : DynamicsShapes
            Shape of the offset action.
        maxlatacc : float
            Maximum allowed lateral acceleration.
        continuous : bool, optional
            If the controller tries to keep the relative speed.
            Default is True.
        """
        self.continuous = convert_bool(continuous)
        self.value = convert_float(value)
        self.dynshape = convert_enum(shape, DynamicsShapes)
        self.maxlatacc = convert_float(maxlatacc)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AbsoluteLaneOffsetAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.dynshape == other.dynshape
                and self.maxlatacc == other.maxlatacc
                and self.continuous == other.continuous
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "AbsoluteLaneOffsetAction":
        """Parses the XML element of AbsoluteLaneOffsetAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            An AbsoluteLaneOffsetAction element (same as generated by
            the class itself).

        Returns
        -------
        AbsoluteLaneOffsetAction
            An AbsoluteLaneOffsetAction object.
        """
        loa_element = find_mandatory_field(
            element, "LateralAction/LaneOffsetAction"
        )

        continuous = convert_bool(loa_element.attrib["continuous"])
        load_element = find_mandatory_field(
            loa_element, "LaneOffsetActionDynamics"
        )
        maxacc = convert_float(load_element.attrib["maxLateralAcc"])
        dynamics = convert_enum(
            load_element.attrib["dynamicsShape"], DynamicsShapes
        )

        atlo_element = find_mandatory_field(
            loa_element, "LaneOffsetTarget/AbsoluteTargetLaneOffset"
        )
        value = atlo_element.attrib["value"]

        return AbsoluteLaneOffsetAction(value, dynamics, maxacc, continuous)

    def get_attributes(self) -> dict:
        """Returns the attributes of the AbsoluteLaneOffsetAction as a
        dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            AbsoluteLaneOffsetAction.
        """
        retdict = {}
        retdict["value"] = str(self.value)
        return retdict

    def get_element(self) -> ET.Element:
        """Generates an XML element tree representation of the
        AbsoluteLaneOffsetAction.

        Returns
        -------
        ET.Element
            The root XML element representing the
            AbsoluteLaneOffsetAction.
        """
        element = ET.Element("PrivateAction")
        lataction = ET.SubElement(element, "LateralAction")
        laneoffsetaction = ET.SubElement(
            lataction,
            "LaneOffsetAction",
            attrib={"continuous": get_bool_string(self.continuous)},
        )
        ET.SubElement(
            laneoffsetaction,
            "LaneOffsetActionDynamics",
            {
                "maxLateralAcc": str(self.maxlatacc),
                "dynamicsShape": self.dynshape.get_name(),
            },
        )
        laneoftarget = ET.SubElement(laneoffsetaction, "LaneOffsetTarget")
        ET.SubElement(
            laneoftarget, "AbsoluteTargetLaneOffset", self.get_attributes()
        )

        return element


class RelativeLaneOffsetAction(_PrivateActionType):
    """Creates a LateralAction of type LaneOffsetAction with a relative target.

    Parameters
    ----------
    value : float
        Relative lateral offset of the target.
    entity : str
        Name of the entity.
    shape : str
        Shape of the offset action.
    maxlatacc : float
        Maximum allowed lateral acceleration.
    continuous : bool, optional
        If the controller tries to keep the relative speed.
        Default is True.

    Attributes
    ----------
    continuous : bool
        If the controller tries to keep the relative speed.
    value : float
        Relative lateral offset of the target.
    target : str
        The name of the entity.
    dynshape : str
        The shape of the action.
    maxlatacc : float
        Maximum allowed lateral acceleration.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        value: float,
        entity: str,
        shape: DynamicsShapes,
        maxlatacc: float,
        continuous: bool = True,
    ):
        """Initializes the RelativeLaneOffsetAction.

        Parameters
        ----------
        value : float
            Relative lateral offset of the target.
        entity : str
            Name of the entity.
        shape : DynamicsShapes
            Shape of the offset action.
        maxlatacc : float
            Maximum allowed lateral acceleration.
        continuous : bool, optional
            If the controller tries to keep the relative speed.
            Default is True.
        """
        self.continuous = convert_bool(continuous)
        self.value = convert_float(value)
        self.target = entity
        if not hasattr(DynamicsShapes, str(shape)):
            raise ValueError(shape + "; is not a valid shape.")
        self.dynshape = shape
        self.maxlatacc = convert_float(maxlatacc)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RelativeLaneOffsetAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.dynshape == other.dynshape
                and self.maxlatacc == other.maxlatacc
                and self.continuous == other.continuous
                and self.target == other.target
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RelativeLaneOffsetAction":
        """Parses the XML element of AbsoluteLaneOffsetAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            An AbsoluteLaneOffsetAction element (same as generated by
            the class itself).

        Returns
        -------
        AbsoluteLaneOffsetAction
            An AbsoluteLaneOffsetAction object.
        """
        loa_element = find_mandatory_field(
            element, "LateralAction/LaneOffsetAction"
        )

        contiuous = convert_bool(loa_element.attrib["continuous"])
        load_element = find_mandatory_field(
            loa_element, "LaneOffsetActionDynamics"
        )
        maxacc = convert_float(load_element.attrib["maxLateralAcc"])
        dynamics = getattr(
            DynamicsShapes, load_element.attrib["dynamicsShape"]
        )

        rtlo_element = find_mandatory_field(
            loa_element, "LaneOffsetTarget/RelativeTargetLaneOffset"
        )
        value = convert_float(rtlo_element.attrib["value"])
        entity = rtlo_element.attrib["entityRef"]

        return RelativeLaneOffsetAction(
            value, entity, dynamics, maxacc, contiuous
        )

    def get_attributes(self) -> dict:
        """Returns the attributes of the RelativeLaneOffsetAction as a
        dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            RelativeLaneOffsetAction.
        """
        retdict = {}
        retdict["value"] = str(self.value)
        retdict["entityRef"] = self.target
        return retdict

    def get_element(self) -> ET.Element:
        """Generates an XML element tree representation of the
        RelativeLaneOffsetAction.

        Returns
        -------
        ET.Element
            The root XML element representing the
            RelativeLaneOffsetAction.
        """
        element = ET.Element("PrivateAction")
        lataction = ET.SubElement(element, "LateralAction")
        laneoffsetaction = ET.SubElement(
            lataction,
            "LaneOffsetAction",
            attrib={"continuous": get_bool_string(self.continuous)},
        )
        ET.SubElement(
            laneoffsetaction,
            "LaneOffsetActionDynamics",
            {
                "maxLateralAcc": str(self.maxlatacc),
                "dynamicsShape": self.dynshape.get_name(),
            },
        )
        laneoftarget = ET.SubElement(laneoffsetaction, "LaneOffsetTarget")
        ET.SubElement(
            laneoftarget,
            "RelativeTargetLaneOffset",
            attrib=self.get_attributes(),
        )

        return element


class LateralDistanceAction(_PrivateActionType):
    """
    Parameters
    ----------
    entity : str
        The target name.
    distance : float
        The lateral distance to the entity.
    freespace : bool, optional
        (True) distance between bounding boxes,
        (False) distance between ref point. Default is True.
    continuous : bool, optional
        If the controller tries to keep the relative speed. Default is True.
    max_acceleration : float, optional
        Maximum acceleration allowed. Default is None.
    max_deceleration : float, optional
        Maximum deceleration allowed. Default is None.
    max_speed : float, optional
        Maximum speed allowed. Default is None.
    coordinate_system : CoordinateSystem, optional
        The coordinate system for the distance calculation.
        Default is CoordinateSystem.entity.
    displacement : LateralDisplacement, optional
        Type of displacement wanted. Default is LateralDisplacement.any.

    Attributes
    ----------
    entity : str
        The target name.
    distance : float
        The lateral distance to the entity.
    freespace : bool
        (True) distance between bounding boxes,
        (False) distance between ref point.
    continuous : bool
        If the controller tries to keep the relative speed.
    distance : float
        If the distance metric is used.
    timegap : float
        If timegap metric is used.
    dynamic_constraint : DynamicsConstraints
        Dynamics constraints of the action.
    coordinate_system : CoordinateSystem
        The coordinate system for the distance calculation.
    displacement : LateralDisplacement
        Type of displacement wanted.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        entity: str,
        distance: Optional[float] = None,
        freespace: bool = True,
        continuous: bool = True,
        max_acceleration: Optional[float] = None,
        max_deceleration: Optional[float] = None,
        max_speed: Optional[float] = None,
        coordinate_system: CoordinateSystem = CoordinateSystem.entity,
        displacement: LateralDisplacement = LateralDisplacement.any,
    ):
        """Initializes the LateralDistanceAction.

        Parameters
        ----------
        entity : str
            The target name.
        distance : float, optional
            The lateral distance to the entity. Default is None.
        freespace : bool, optional
            If True, distance is measured between bounding boxes;
            if False, distance is measured between reference points.
            Default is True.
        continuous : bool, optional
            If True, the controller tries to maintain the relative speed
            Default is True.
        max_acceleration : float, optional
            Maximum acceleration allowed. Default is None.
        max_deceleration : float, optional
            Maximum deceleration allowed. Default is None.
        max_speed : float, optional
            Maximum speed allowed. Default is None.
        coordinate_system : CoordinateSystem, optional
            The coordinate system for the distance calculation.
            Default is CoordinateSystem.entity.
        displacement : LateralDisplacement, optional
            Type of displacement wanted.
            Default is LateralDisplacement.any.
        """
        self.distance = distance
        self.target = entity

        self.freespace = convert_bool(freespace)
        self.continuous = convert_bool(continuous)
        self.dynamic_constraint = DynamicsConstraints(
            max_acceleration, max_deceleration, max_speed
        )
        self.coordinate_system = convert_enum(
            coordinate_system, CoordinateSystem
        )
        self.displacement = convert_enum(displacement, LateralDisplacement)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LateralDistanceAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.dynamic_constraint == other.dynamic_constraint
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "LateralDistanceAction":
        """Parses the XML element of LateralDistanceAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A LateralDistanceAction element (same as generated by the
            class itself).

        Returns
        -------
        LateralDistanceAction
            A LateralDistanceAction object.
        """
        lda_element = find_mandatory_field(
            element, "LateralAction/LateralDistanceAction"
        )
        continuous = convert_bool(lda_element.attrib["continuous"])
        freespace = convert_bool(lda_element.attrib["freespace"])
        entity = lda_element.attrib["entityRef"]
        distance = None
        if "distance" in lda_element.attrib:
            distance = lda_element.attrib["distance"]
        coordinate = None
        if "coordinateSystem" in lda_element.attrib:
            coordinate = convert_enum(
                lda_element.attrib["coordinateSystem"], CoordinateSystem
            )
        displacement = None
        if "displacement" in lda_element.attrib:
            displacement = convert_enum(
                lda_element.attrib["displacement"], LateralDisplacement
            )
        constraints = None
        max_acc = None
        max_dec = None
        max_speed = None
        if lda_element.find("DynamicConstraints") is not None:
            constraints = DynamicsConstraints.parse(
                find_mandatory_field(lda_element, "DynamicConstraints")
            )
            max_acc = constraints.max_acceleration
            max_dec = constraints.max_deceleration
            max_speed = constraints.max_speed

        return LateralDistanceAction(
            entity,
            distance,
            freespace,
            continuous,
            max_acc,
            max_dec,
            max_speed,
            coordinate,
            displacement,
        )

    def get_attributes(self) -> dict:
        """Returns the attributes of the LateralDistanceAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            LateralDistanceAction.
        """
        retdict = {}
        retdict["entityRef"] = self.target
        retdict["freespace"] = get_bool_string(self.freespace)
        retdict["continuous"] = get_bool_string(self.continuous)
        if self.distance is not None:
            retdict["distance"] = str(self.distance)
        if not self.isVersion(minor=0):
            retdict["coordinateSystem"] = self.coordinate_system.get_name()
            retdict["displacement"] = self.displacement.get_name()
        return retdict

    def get_element(self) -> ET.Element:
        """Constructs and returns an XML element tree representation of the
        LateralDistanceAction.

        Returns
        -------
        ET.Element
            The root XML element representing the LateralDistanceAction.
        """
        element = ET.Element("PrivateAction")
        lataction = ET.SubElement(element, "LateralAction")
        lateraldistanceaction = ET.SubElement(
            lataction, "LateralDistanceAction", attrib=self.get_attributes()
        )
        if self.dynamic_constraint.is_filled():
            lateraldistanceaction.append(self.dynamic_constraint.get_element())

        return element


# teleport
class TeleportAction(_PrivateActionType):
    """The TeleportAction creates the Teleport action of OpenScenario.

    Parameters
    ----------
    position : _PositionType
        Any position object.

    Attributes
    ----------
    position : _PositionType
        Any position object.

    Methods
    -------
    parse(element : xml.etree.ElementTree.Element) -> TeleportAction
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element() -> xml.etree.ElementTree.Element
        Returns the full ElementTree of the class.
    """

    def __init__(self, position: _PositionType):
        """Initializes the TeleportAction.

        Parameters
        ----------
        position : _PositionType
            Any position object.
        """
        if not isinstance(position, _PositionType):
            raise TypeError("position input not a valid Position type")

        self.position = position

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TeleportAction):
            if self.position == other.position:
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TeleportAction":
        """Parses the XML element of TeleportAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        TeleportAction
            A TeleportAction object.
        """
        position_element = find_mandatory_field(
            element, "TeleportAction/Position"
        )

        position = _PositionFactory.parse_position(position_element)
        return TeleportAction(position)

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the TeleportAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the TeleportAction.
        """
        element = ET.Element("PrivateAction")
        telact = ET.SubElement(element, "TeleportAction")
        telact.append(self.position.get_element())
        return element


# Routing actions


class AssignRouteAction(_PrivateActionType):
    """AssignRouteAction creates a RouteAction of type AssignRouteAction.

    Parameters
    ----------
    route : Route or CatalogReference
        The route to follow.

    Attributes
    ----------
    route : Route or CatalogReference
        The route to follow.

    Methods
    -------
    parse(element : ET.Element) -> AssignRouteAction
        Parses an ElementTree element and returns an instance of the
        class.
    get_element() -> ET.Element
        Returns the full ElementTree representation of the class.
    """

    def __init__(self, route: Union[Route, CatalogReference]):
        """Initializes the AssignRouteAction.

        Parameters
        ----------
        route : Route or CatalogReference
            The route to follow.
        """
        if not isinstance(route, (Route, CatalogReference)):
            raise TypeError(
                "route input not of type Route or CatalogReference"
            )

        self.route = route

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AssignRouteAction):
            if self.route == other.route:
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "AssignRouteAction":
        """Parses the XML element of AssignRouteAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A AssignRouteAction element (same as generated by the class
            itself).

        Returns
        -------
        AssignRouteAction
            A AssignRouteAction object.
        """
        ara_element = find_mandatory_field(
            element, "RoutingAction/AssignRouteAction"
        )
        route = None
        if ara_element.find("Route") is not None:
            route = Route.parse(find_mandatory_field(ara_element, "Route"))
        elif ara_element.find("CatalogReference") is not None:
            route = CatalogReference.parse(
                find_mandatory_field(ara_element, "CatalogReference")
            )

        return AssignRouteAction(route)

    def get_element(self) -> ET.Element:
        """Generates an XML element tree representation of the
        AssignRouteAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The root XML element representing the AssignRouteAction.
        """
        element = ET.Element("PrivateAction")
        routeaction = ET.SubElement(element, "RoutingAction")
        assignrouteaction = ET.SubElement(routeaction, "AssignRouteAction")
        assignrouteaction.append(self.route.get_element())

        return element


class AcquirePositionAction(_PrivateActionType):
    """AcquirePositionAction creates a RouteAction of type
    AcquirePositionAction.

    Parameters
    ----------
    position : _PositionType
        Target position.

    Attributes
    ----------
    position : _PositionType
        Target position.

    Methods
    -------
    parse(element : ET.Element) -> AcquirePositionAction
        Parses an ElementTree element and returns an instance of the
        class.
    get_element() -> ET.Element
        Returns the full ElementTree representation of the class.
    """

    def __init__(self, position: _PositionType):
        """Initializes the AcquirePositionAction.

        Parameters
        ----------
        position : _PositionType
            Target position.
        """
        if not isinstance(position, _PositionType):
            raise TypeError("position input not a valid Position type")

        self.position = position

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AcquirePositionAction):
            if self.position == other.position:
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "AcquirePositionAction":
        """Parses the XML element of AcquirePositionAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A AcquirePositionAction element (same as generated by the
            class itself).

        Returns
        -------
        AcquirePositionAction
            An AcquirePositionAction object.
        """
        pos_element = find_mandatory_field(
            element, "RoutingAction/AcquirePositionAction/Position"
        )

        position = _PositionFactory.parse_position(pos_element)

        return AcquirePositionAction(position)

    def get_element(self) -> ET.Element:
        """Generates an XML element tree representation of the
        AcquirePositionAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The root XML element representing the PrivateAction with
            nested RoutingAction and AcquirePositionAction elements.
        """

        element = ET.Element("PrivateAction")
        routeaction = ET.SubElement(element, "RoutingAction")
        posaction = ET.SubElement(routeaction, "AcquirePositionAction")
        posaction.append(self.position.get_element())

        return element


class FollowTrajectoryAction(_PrivateActionType):
    """FollowTrajectoryAction creates a RouteAction of type
    FollowTrajectoryAction.

    Parameters
    ----------
    trajectory : Trajectory or CatalogReference
        The trajectory to follow.
    following_mode : FollowingMode
        The following mode of the action.
    reference_domain : ReferenceContext, optional
        How to follow. Default is None.
    scale : float, optional
        Scale factor of the timings (must be combined with
        reference_domain and offset). Default is None.
    offset : float, optional
        Offset for time values (must be combined with reference_domain
        and scale). Default is None.
    initialDistanceOffset : float, optional
        Start at this offset into the trajectory (valid from v1.1).
        Default is None.

    Attributes
    ----------
    trajectory : Trajectory or CatalogReference
        The trajectory to follow.
    following_mode : str
        The following mode of the action.
    timeref : TimeReference
        The time reference of the trajectory.
    initialDistanceOffset : float
        Start at this offset into the trajectory (valid from v1.1).

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    """

    def __init__(
        self,
        trajectory: Union[Trajectory, CatalogReference],
        following_mode: FollowingMode,
        reference_domain: str = None,
        scale: float = None,
        offset: float = None,
        initialDistanceOffset: float = None,
    ):
        """Initialize the FollowTrajectoryAction.

        Parameters
        ----------
        trajectory : Trajectory or CatalogReference
            The trajectory to follow.
        following_mode : FollowingMode
            The following mode of the action.
        reference_domain : str, optional
            Absolute or relative time reference (must be combined with
            scale and offset). Default is None.
        scale : float, optional
            Scale factor of the timings (must be combined with
            reference_domain and offset). Default is None.
        offset : float, optional
            Offset for time values (must be combined with r
            eference_domain and scale). Default is None.
        initialDistanceOffset : float, optional
            Start at this offset into the trajectory (valid from v1.1).
            Default is None.
        """
        if not isinstance(trajectory, (Trajectory, CatalogReference)):
            raise TypeError(
                "route input not of type Route or CatalogReference"
            )
        self.trajectory = trajectory
        self.following_mode = convert_enum(following_mode, FollowingMode)
        # TODO: check reference_domain
        self.timeref = TimeReference(reference_domain, scale, offset)
        self.initialDistanceOffset = convert_float(initialDistanceOffset)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FollowTrajectoryAction):
            if (
                self.timeref == other.timeref
                and self.get_attributes() == other.get_attributes()
                and self.trajectory == other.trajectory
                and self.following_mode == other.following_mode
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "FollowTrajectoryAction":
        """Parses the XML element of FollowTrajectoryAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A FollowTrajectoryAction element (same as generated by the
            class itself).

        Returns
        -------
        FollowTrajectoryAction
            A FollowTrajectoryAction object.
        """
        fta_element = find_mandatory_field(
            element, "RoutingAction/FollowTrajectoryAction"
        )
        initial_distance_offset = None
        if "initialDistanceOffset" in fta_element.attrib:
            initial_distance_offset = convert_float(
                fta_element.attrib["initialDistanceOffset"]
            )

        timeref = TimeReference.parse(
            find_mandatory_field(fta_element, "TimeReference")
        )
        reference_domain = timeref.reference_domain
        offset = timeref.offset
        scale = timeref.scale

        tfm_element = find_mandatory_field(
            fta_element, "TrajectoryFollowingMode"
        )
        following_mode = convert_enum(
            tfm_element.attrib["followingMode"], FollowingMode
        )

        if fta_element.find("TrajectoryRef") is not None:
            fta_element = find_mandatory_field(fta_element, "TrajectoryRef")
        trajectory = None
        if fta_element.find("Trajectory") is not None:
            trajectory = Trajectory.parse(
                find_mandatory_field(fta_element, "Trajectory")
            )
        if fta_element.find("CatalogReference") is not None:
            trajectory = CatalogReference.parse(
                find_mandatory_field(fta_element, "CatalogReference")
            )

        return FollowTrajectoryAction(
            trajectory,
            following_mode,
            reference_domain,
            scale,
            offset,
            initial_distance_offset,
        )

    def get_attributes(self) -> dict:
        """Returns the attributes of the FollowTrajectoryAction as a
        dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            FollowTrajectoryAction.
        """

        if self.initialDistanceOffset:
            return {"initialDistanceOffset": str(self.initialDistanceOffset)}
        else:
            # If initialDistanceOffset is not set,
            # return empty to stay backward compatible with v1.0
            return {}

    def get_element(self) -> ET.Element:
        """Generates an XML element tree representation of the
        FollowTrajectoryAction.

        Returns
        -------
        ET.Element
            The root XML element representing the FollowTrajectoryAction
        """
        element = ET.Element("PrivateAction")
        routeaction = ET.SubElement(element, "RoutingAction")
        trajaction = ET.SubElement(
            routeaction, "FollowTrajectoryAction", attrib=self.get_attributes()
        )
        if self.isVersion(minor=0):
            trajaction.append(self.trajectory.get_element())
        else:
            trajref = ET.SubElement(trajaction, "TrajectoryRef")
            trajref.append(self.trajectory.get_element())
        trajaction.append(self.timeref.get_element())
        ET.SubElement(
            trajaction,
            "TrajectoryFollowingMode",
            attrib={"followingMode": self.following_mode.get_name()},
        )

        return element


class ControllerAction(_PrivateActionType):
    """ControllerAction creates a ControllerAction of OpenSCENARIO.

    Parameters
    ----------
    assignControllerAction : AssignControllerAction, optional
        Assign a controller to an entity.
    overrideControllerValueAction : OverrideControllerValueAction,
        optional. Values for brake, clutch, parking brake, steering
        wheel, or gear.
    activateControllerAction : ActivateControllerAction, optional
        Activate/deactivate a controller on the reference
        entity/entities.
        Replaces the deprecated element in PrivateAction in version 1.1.

    Methods
    -------
    parse : ElementTree.Element -> ControllerAction
        Parses an ElementTree element and returns an instance of the
        class.
    get_element : None -> ElementTree.Element
        Returns the full ElementTree representation of the class.
    """

    def __init__(
        self,
        assignControllerAction: Optional["AssignControllerAction"] = None,
        overrideControllerValueAction: Optional[
            "OverrideControllerValueAction"
        ] = None,
        activateControllerAction: Optional["ActivateControllerAction"] = None,
    ):
        """Initializes the ControllerAction.

        Parameters
        ----------
        assignControllerAction : AssignControllerAction, optional
            Assign a controller to an entity.
        overrideControllerValueAction : OverrideControllerValueAction,
            optional. Values for brake, clutch, parking brake, steering
            wheel, or gear.
        activateControllerAction : ActivateControllerAction, optional
            Activate/deactivate a controller on the reference entity/entities.
            Replaces the deprecated element in PrivateAction in version 1.1.
        """
        if assignControllerAction is not None and not isinstance(
            assignControllerAction, AssignControllerAction
        ):
            raise TypeError(
                "assignControllerAction is not of type AssignControllerAction"
            )
        if overrideControllerValueAction is not None and not isinstance(
            overrideControllerValueAction, OverrideControllerValueAction
        ):
            raise TypeError(
                "overrideControllerValueAction is not of type OverrideControllerValueAction"
            )
        if activateControllerAction is not None and not isinstance(
            activateControllerAction, ActivateControllerAction
        ):
            raise TypeError(
                "activateControllerAction is not of type ActivateControllerAction"
            )
        self.assignControllerAction = assignControllerAction
        self.overrideControllerValueAction = overrideControllerValueAction
        self.activateControllerAction = activateControllerAction
        if self.assignControllerAction is not None:
            self.assignControllerAction._used_by_parent = True
        if self.overrideControllerValueAction is not None:
            self.overrideControllerValueAction._used_by_parent = True

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ControllerAction):
            if (
                self.activateControllerAction == other.activateControllerAction
                and self.overrideControllerValueAction
                == other.overrideControllerValueAction
                and self.assignControllerAction == other.assignControllerAction
            ):
                return True
        if isinstance(other, AssignControllerAction):
            if self.assignControllerAction == other:
                return True
        if isinstance(other, OverrideControllerValueAction):
            if self.overrideControllerValueAction == other:
                return True
        if isinstance(other, ActivateControllerAction):
            if self.activateControllerAction == other:
                return True

        return False

    @staticmethod
    def parse(element: ET.Element) -> "ControllerAction":
        """Parses the XML element of ControllerAction.

        element : xml.etree.ElementTree.Element
            A ControllerAction element (same as generated by the class
            itself).

        ControllerAction
            A ControllerAction object containing one of the following:
            - ActivateControllerAction
            - OverrideControllerValueAction
            - AssignControllerAction
        """

        activateControllerAction = None
        overrideControllerValueAction = None
        assignControllerAction = None

        ca_element = find_mandatory_field(element, "ControllerAction")

        if ca_element.find("ActivateControllerAction") is not None:
            activateControllerAction = ActivateControllerAction.parse(element)
        if ca_element.find("OverrideControllerValueAction") is not None:
            overrideControllerValueAction = (
                OverrideControllerValueAction.parse(element)
            )
        if ca_element.find("AssignControllerAction") is not None:
            assignControllerAction = AssignControllerAction.parse(element)

        return ControllerAction(
            assignControllerAction,
            overrideControllerValueAction,
            activateControllerAction,
        )

    def get_element(self) -> ET.Element:
        """Generates and returns an XML element tree representation of the
        ControllerAction.

        Returns
        -------
        ET.Element
            The root XML element representing the ControllerAction.

        Raises
        ------
        NotEnoughInputArguments
            If both `assignControllerAction` and
            `overrideControllerValueAction` are not provided
            in version 1.0.
        OpenSCENARIOVersionError
            If `activateControllerAction` is provided in version 1.0.
        """

        if self.isVersion(minor=0):
            if (
                self.assignControllerAction is None
                or self.overrideControllerValueAction is None
            ):
                raise NotEnoughInputArguments(
                    "Both assignControllerAction and "
                    "overrideControllerValueAction are required in version 1.0."
                )
            if self.activateControllerAction is not None:
                raise OpenSCENARIOVersionError(
                    "activateControllerAction is not parameter in version 1.0."
                )

        element = ET.Element("PrivateAction")
        controlleraction = ET.SubElement(element, "ControllerAction")

        if self.activateControllerAction is not None:
            pa_element = self.activateControllerAction.get_element()
            aca_element = find_mandatory_field(
                pa_element, "ControllerAction/ActivateControllerAction"
            )
            controlleraction.append(aca_element)

        if self.overrideControllerValueAction is not None:
            pa_element = self.overrideControllerValueAction.get_element()
            ocva_element = find_mandatory_field(
                pa_element, "ControllerAction/OverrideControllerValueAction"
            )
            controlleraction.append(ocva_element)

        if self.assignControllerAction is not None:
            pa_element = self.assignControllerAction.get_element()
            aca_element = find_mandatory_field(
                pa_element, "ControllerAction/AssignControllerAction"
            )
            controlleraction.append(aca_element)

        return element


class ActivateControllerAction(_PrivateActionType):
    """ActivateControllerAction creates an ActivateControllerAction of
    OpenSCENARIO.

    Parameters
    ----------
    lateral : bool
        Activate or deactivate the lateral controller.
    longitudinal : bool
        Activate or deactivate the longitudinal controller.
    animation : bool
        Activate or deactivate an animation.
    lighting : bool
        Activate or deactivate lights.
    controllerRef : Controller
        Reference to a controller assigned to the entity.

    Attributes
    ----------
    lateral : bool
        Activate or deactivate the lateral controller.
    longitudinal : bool
        Activate or deactivate the longitudinal controller.
    animation : bool
        Activate or deactivate an animation.
    lighting : bool
        Activate or deactivate lights.
    controllerRef : Controller
        Reference to a controller assigned to the entity.

    Methods
    -------
    parse(element)
        Parses an ElementTree element and returns an instance of the
        class.
    get_element()
        Returns the full ElementTree representation of the class.
    get_attributes()
        Returns the attributes of the class as a dictionary.
    """

    def __init__(
        self,
        lateral: Optional[bool] = None,
        longitudinal: Optional[bool] = None,
        animation: Optional[bool] = None,
        lighting: Optional[bool] = None,
        controllerRef: Optional[Controller] = None,
    ):
        """Initializes the ActivateControllerAction.

        Parameters
        ----------
        lateral : bool
            Activate or deactivate the lateral controller.
        longitudinal : bool
            Activate or deactivate the longitudinal controller.
        animation : bool
            Activate or deactivate an animation.
        lighting : bool
            Activate or deactivate lights.
        controllerRef : Controller
            Reference to a controller assigned to the entity.
        """
        self.lateral = convert_bool(lateral)
        self.longitudinal = convert_bool(longitudinal)
        self.animation = convert_bool(animation)
        self.lighting = convert_bool(lighting)
        self.controllerRef = controllerRef

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ActivateControllerAction):
            if self.get_attributes() == other.get_attributes():
                return True
        elif isinstance(other, ControllerAction):
            if (
                self.get_attributes()
                == other.activateControllerAction.get_attributes()
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "ActivateControllerAction":
        """Parses the XML element of ActivateControllerAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A ActivateControllerAction element (same as generated by
            the class itself).

        Returns
        -------
        ActivateControllerAction
            A ActivateControllerAction object.
        """
        lateral = None
        longitudinal = None
        animation = None
        lighting = None
        controllerRef = None
        if element.find("ControllerAction") is not None:
            aca_element = find_mandatory_field(
                element, "ControllerAction/ActivateControllerAction"
            )
        else:
            aca_element = find_mandatory_field(
                element, "ActivateControllerAction"
            )

        if "lateral" in aca_element.attrib:
            lateral = convert_bool(aca_element.attrib["lateral"])
        if "longitudinal" in aca_element.attrib:
            longitudinal = convert_bool(aca_element.attrib["longitudinal"])
        if "animation" in aca_element.attrib:
            animation = convert_bool(aca_element.attrib["animation"])
        if "lighting" in aca_element.attrib:
            lighting = convert_bool(aca_element.attrib["lighting"])
        if "controllerRef" in aca_element.attrib:
            controllerRef = aca_element.attrib["controllerRef"]

        return ActivateControllerAction(
            lateral, longitudinal, animation, lighting, controllerRef
        )

    def get_attributes(self) -> dict:
        """Returns the attributes of the ActivateControllerAction as a
        dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            ActivateControllerAction.
        """
        retdict = {}
        if self.lateral is not None:
            retdict["lateral"] = get_bool_string(self.lateral)
        if self.longitudinal is not None:
            retdict["longitudinal"] = get_bool_string(self.longitudinal)
        if self.animation is not None and self.isVersion(minor=2):
            retdict["animation"] = get_bool_string(self.animation)
        if self.lighting is not None and self.isVersion(minor=2):
            retdict["lighting"] = get_bool_string(self.lighting)
        if self.controllerRef is not None and self.isVersion(minor=2):
            retdict["controllerRef"] = self.controllerRef
        return retdict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the ActivateControllerAction.

        Returns
        -------
        ET.Element
            The XML element representing the ActivateControllerAction.
        """
        element = ET.Element("PrivateAction")
        if self.isVersion(minor=0):
            ET.SubElement(
                element,
                "ActivateControllerAction",
                attrib=self.get_attributes(),
            )
        else:
            subelem = ET.SubElement(element, "ControllerAction")
            ET.SubElement(
                subelem,
                "ActivateControllerAction",
                attrib=self.get_attributes(),
            )
        return element


class AssignControllerAction(_PrivateActionType):
    """AssignControllerAction creates a ControllerAction of type
    AssignControllerAction.

    Parameters
    ----------
    controller : Controller or CatalogReference
        A controller to assign.
    activateLateral : bool, optional
        If the lateral control should be activated (valid from V1.1).
        Default is True.
    activateLongitudinal : bool, optional
        If the longitudinal control should be activated
        (valid from V1.1). Default is True.
    activateLighting : bool, optional
        If the lighting control should be activated (valid from V1.2).
        Default is False.
    activateAnimation : bool, optional
        If the animation control should be activated (valid from V1.2).
        Default is False.

    Attributes
    ----------
    controller : Controller or CatalogReference
        A controller to assign.
    activateLateral : bool
        Indicates if the lateral control is activated (valid from V1.1).
    activateLongitudinal : bool
        Indicates if the longitudinal control is activated
        (valid from V1.1).
    activateLighting : bool
        Indicates if the lighting control is activated
        (valid from V1.2).
    activateAnimation : bool
        Indicates if the animation control is activated
        (valid from V1.2).

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns the attributes of the AssignControllerAction as a
        dictionary.
    """

    def __init__(
        self,
        controller: Union[Controller, CatalogReference],
        activateLateral: bool = True,
        activateLongitudinal: bool = True,
        activateLighting: bool = False,
        activateAnimation: bool = False,
    ):
        """Initializes the AssignControllerAction.

        Parameters
        ----------
        controller : Controller or CatalogReference
            A controller to assign.
        activateLateral : bool, optional
            If the lateral control should be activated
            (valid from V1.1). Default is True.
        activateLongitudinal : bool, optional
            If the longitudinal control should be activated
            (valid from V1.1). Default is True.
        """
        if not isinstance(controller, (Controller, CatalogReference)):
            raise TypeError(
                "route input not of type Route or CatalogReference"
            )
        self.controller = controller
        self.activateLateral = convert_bool(activateLateral)
        self.activateLongitudinal = convert_bool(activateLongitudinal)
        self.activateLighting = convert_bool(activateLighting)
        self.activateAnimation = convert_bool(activateAnimation)
        self._used_by_parent = False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AssignControllerAction):
            if self.controller == other.controller:
                return True
        elif isinstance(other, ControllerAction):
            if self.controller == other.assignControllerAction.controller:
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "AssignControllerAction":
        """Parses the XML element of AssignControllerAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A AssignControllerAction element (same as generated by the
            class itself).

        Returns
        -------
        AssignControllerAction
            An AssignControllerAction object.
        """
        ca_element = find_mandatory_field(element, "ControllerAction")
        aca_element = find_mandatory_field(
            ca_element, "AssignControllerAction"
        )
        activate_lateral = True
        if "activateLateral" in aca_element.attrib:
            activate_lateral = convert_bool(
                aca_element.attrib["activateLateral"]
            )

        activate_longitudinal = True
        if "activateLongitudinal" in aca_element.attrib:
            activate_longitudinal = convert_bool(
                aca_element.attrib["activateLongitudinal"]
            )
        activate_lighting = False
        if "activateLighting" in aca_element.attrib:
            activate_lighting = convert_bool(
                aca_element.attrib["activateLighting"]
            )
        activate_animation = False
        if "activateAnimation" in aca_element.attrib:
            activate_animation = convert_bool(
                aca_element.attrib["activateAnimation"]
            )
        controller = None
        if aca_element.find("Controller") is not None:
            controller = Controller.parse(
                find_mandatory_field(aca_element, "Controller")
            )
        elif aca_element.find("CatalogReference") is not None:
            controller = CatalogReference.parse(
                find_mandatory_field(aca_element, "CatalogReference")
            )
        else:
            raise NotAValidElement(
                "No Controller found for AssignControllerAction"
            )

        return AssignControllerAction(
            controller,
            activate_lateral,
            activate_longitudinal,
            activate_lighting,
            activate_animation,
        )

    def get_attributes(self) -> dict:
        """Returns the attributes of the AssignControllerAction as a
        dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            AssignControllerAction.
        """
        retdict = {}

        if self.isVersionEqLarger(minor=1):
            retdict = {
                "activateLateral": get_bool_string(self.activateLateral),
                "activateLongitudinal": get_bool_string(
                    self.activateLongitudinal
                ),
            }
        if self.isVersionEqLarger(minor=2):
            retdict["activateLighting"] = get_bool_string(
                self.activateLighting
            )
            retdict["activateAnimation"] = get_bool_string(
                self.activateAnimation
            )
        return retdict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the AssignControllerAction.

        Returns
        -------
        ET.Element
            The XML element representing the AssignControllerAction.

        Raises
        ------
        OpenSCENARIOVersionError
            If the AssignControllerAction is used alone in OSC 1.0.
        """
        if self.isVersion(minor=0) and not self._used_by_parent:
            raise OpenSCENARIOVersionError(
                "AssignControllerAction cannot be used alone in OSC 1.0, "
                "please add it to a ControllerAction."
            )
        element = ET.Element("PrivateAction")
        controlleraction = ET.SubElement(element, "ControllerAction")
        assigncontrolleraction = ET.SubElement(
            controlleraction, "AssignControllerAction", self.get_attributes()
        )
        assigncontrolleraction.append(self.controller.get_element())

        return element


class OverrideControllerValueAction(_PrivateActionType):
    """
    OverrideControllerValueAction creates a
    OverrideControllerValueAction action of OpenSCENARIO which can
    include throttle, brake, clutch, steering wheel, gear, and
    parking brake.
    NOTE: This implementation is compatible with OSC v1.1 where all
    attributes don't have to be set.

    Attributes
    ----------
    throttle_active : bool, optional
        If the throttle is active. Default is None (not written).
    throttle_value : float
        Value of the throttle.
    brake_active : bool, optional
        If the brake is active. Default is None (not written).
    brake_value : float
        Value of the brake.
    clutch_active : bool, optional
        If the clutch is active. Default is None (not written).
    clutch_value : float
        Value of the clutch.
    steeringwheel_active : bool, optional
        If the steering wheel is active. Default is None (not written).
    steeringwheel_value : float
        Value of the steering wheel.
    gear_active : bool, optional
        If the gear is active. Default is None (not written).
    gear_value : float
        Value of the gear.
    parkingbrake_active : bool, optional
        If the parking brake is active. Default is None (not written).
    parkingbrake_value : float
        Value of the parking brake.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns the attributes of the class.
    set_throttle(active, value)
        Sets the throttle value.
    set_brake(active, value)
        Sets the brake value.
    set_steeringwheel(active, value)
        Sets the steering wheel value.
    set_clutch(active, value)
        Sets the clutch value.
    set_gear(active, value)
        Sets the gear value.
    set_parkingbrake(active, value)
        Sets the parking brake value.
    """

    def __init__(self):
        self.throttle_active = None
        self.throttle_value = convert_float(0)
        self.throttle_rate = None
        self.brake_active = None
        self.brake_value = convert_float(0)
        self.brake_rate = None
        self.brake_force = False
        self.clutch_active = None
        self.clutch_value = convert_float(0)
        self.clutch_rate = None
        self.steeringwheel_active = None
        self.steeringwheel_value = convert_float(0)
        self.steeringwheel_rate = None
        self.steeringwheel_torque = None
        self.gear_active = None
        self.gear_value = convert_float(0)
        self._gear_maunal = True
        self.parkingbrake_active = None
        self.parkingbrake_value = convert_float(0)
        self.parkingbrake_rate = None
        self.parkingbrake_force = False

        self._used_by_parent = False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, OverrideControllerValueAction):
            if (
                self.throttle_value == other.throttle_value
                and self.throttle_value == other.throttle_value
                and self.throttle_rate == other.throttle_rate
                and self.brake_active == other.brake_active
                and self.brake_value == other.brake_value
                and self.brake_rate == other.brake_rate
                and self.brake_force == other.brake_force
                and self.clutch_active == other.clutch_active
                and self.clutch_value == other.clutch_value
                and self.clutch_rate == other.clutch_rate
                and self.steeringwheel_active == other.steeringwheel_active
                and self.steeringwheel_value == other.steeringwheel_value
                and self.steeringwheel_rate == other.steeringwheel_rate
                and self.steeringwheel_torque == other.steeringwheel_torque
                and self.gear_active == other.gear_active
                and self.gear_value == other.gear_value
                and self.parkingbrake_active == other.parkingbrake_active
                and self.parkingbrake_value == other.parkingbrake_value
                and self.parkingbrake_force == other.parkingbrake_force
                and self.parkingbrake_rate == other.parkingbrake_rate
            ):
                return True
        elif isinstance(other, ControllerAction):
            if (
                self.throttle_value
                == other.overrideControllerValueAction.throttle_value
                and self.throttle_value
                == other.overrideControllerValueAction.throttle_value
                and self.throttle_rate
                == other.overrideControllerValueAction.throttle_rate
                and self.brake_active
                == other.overrideControllerValueAction.brake_active
                and self.brake_value
                == other.overrideControllerValueAction.brake_value
                and self.brake_rate
                == other.overrideControllerValueAction.brake_rate
                and self.brake_force
                == other.overrideControllerValueAction.brake_force
                and self.clutch_active
                == other.overrideControllerValueAction.clutch_active
                and self.clutch_value
                == other.overrideControllerValueAction.clutch_value
                and self.clutch_rate
                == other.overrideControllerValueAction.clutch_rate
                and self.steeringwheel_active
                == other.overrideControllerValueAction.steeringwheel_active
                and self.steeringwheel_value
                == other.overrideControllerValueAction.steeringwheel_value
                and self.steeringwheel_rate
                == other.overrideControllerValueAction.steeringwheel_rate
                and self.steeringwheel_torque
                == other.overrideControllerValueAction.steeringwheel_torque
                and self.gear_active
                == other.overrideControllerValueAction.gear_active
                and self.gear_value
                == other.overrideControllerValueAction.gear_value
                and self.parkingbrake_active
                == other.overrideControllerValueAction.parkingbrake_active
                and self.parkingbrake_value
                == other.overrideControllerValueAction.parkingbrake_value
                and self.parkingbrake_force
                == other.overrideControllerValueAction.parkingbrake_force
                and self.parkingbrake_rate
                == other.overrideControllerValueAction.parkingbrake_rate
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "OverrideControllerValueAction":
        """Parses the XML element of OverrideControllerValueAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A OverrideControllerValueAction element (same as generated
            by the class itself).

        Returns
        -------
        OverrideControllerValueAction
            A OverrideControllerValueAction object.
        """
        ocv_action = OverrideControllerValueAction()
        ocva_element = find_mandatory_field(
            element, "ControllerAction/OverrideControllerValueAction"
        )

        ocv_action.throttle_active = None
        ocv_action.throttle_value = convert_float(0)
        if ocva_element.find("Throttle") is not None:
            throttle_element = find_mandatory_field(ocva_element, "Throttle")
            ocv_action.throttle_active = convert_bool(
                throttle_element.attrib["active"]
            )
            ocv_action.throttle_value = convert_float(
                throttle_element.attrib["value"]
            )
            if "maxRate" in throttle_element.attrib:
                ocv_action.throttle_rate = convert_float(
                    throttle_element.attrib["maxRate"]
                )

        ocv_action.brake_active = None
        ocv_action.brake_value = convert_float(0)
        if ocva_element.find("Brake") is not None:
            brake_element = find_mandatory_field(ocva_element, "Brake")
            ocv_action.brake_active = convert_bool(
                brake_element.attrib["active"]
            )
            if "value" in brake_element.attrib:
                ocv_action.brake_value = convert_float(
                    brake_element.attrib["value"]
                )
            else:
                if brake_element.find("BrakePercent") is not None:
                    brake_input_element = find_mandatory_field(
                        brake_element, "BrakePercent"
                    )
                    ocv_action.brake_force = False

                elif brake_element.find("BrakeForce") is not None:
                    brake_input_element = find_mandatory_field(
                        brake_element, "BrakeForce"
                    )
                    ocv_action.brake_force = True
                else:
                    raise ValueError("No value found while parsing brake.")
                ocv_action.brake_value = convert_float(
                    brake_input_element.attrib["value"]
                )
                if "maxRate" in brake_input_element.attrib:
                    ocv_action.brake_rate = brake_input_element.attrib[
                        "maxRate"
                    ]

        ocv_action.clutch_active = None
        ocv_action.clutch_value = convert_float(0)
        if ocva_element.find("Clutch") is not None:
            cluth_element = find_mandatory_field(ocva_element, "Clutch")
            ocv_action.clutch_active = convert_bool(
                cluth_element.attrib["active"]
            )
            ocv_action.clutch_value = convert_float(
                cluth_element.attrib["value"]
            )
            if "maxRate" in cluth_element.attrib:
                ocv_action.clutch_rate = convert_float(
                    cluth_element.attrib["maxRate"]
                )

        ocv_action.parkingbrake_active = None
        ocv_action.parkingbrake_value = convert_float(0)
        if ocva_element.find("ParkingBrake") is not None:
            parkingbrake_element = find_mandatory_field(
                ocva_element, "ParkingBrake"
            )
            ocv_action.parkingbrake_active = convert_bool(
                parkingbrake_element.attrib["active"]
            )

            if "value" in parkingbrake_element.attrib:
                ocv_action.parkingbrake_value = convert_float(
                    parkingbrake_element.attrib["value"]
                )
            else:
                if parkingbrake_element.find("BrakePercent") is not None:
                    parkingbrake_input_element = find_mandatory_field(
                        parkingbrake_element, "BrakePercent"
                    )
                    ocv_action.parkingbrake_force = False

                elif parkingbrake_element.find("BrakeForce") is not None:
                    parkingbrake_input_element = find_mandatory_field(
                        parkingbrake_element, "BrakeForce"
                    )
                    ocv_action.parkingbrake_force = True
                else:
                    raise ValueError("No value found while parsing brake.")
                ocv_action.parkingbrake_value = convert_float(
                    parkingbrake_input_element.attrib["value"]
                )
                if "maxRate" in parkingbrake_input_element.attrib:
                    ocv_action.parkingbrake_rate = convert_float(
                        parkingbrake_input_element.attrib["maxRate"]
                    )

        ocv_action.steeringwheel_active = None
        ocv_action.steeringwheel_value = convert_float(0)
        if ocva_element.find("SteeringWheel") is not None:
            steeringwheel_element = find_mandatory_field(
                ocva_element, "SteeringWheel"
            )
            ocv_action.steeringwheel_active = convert_bool(
                steeringwheel_element.attrib["active"]
            )
            ocv_action.steeringwheel_value = convert_float(
                steeringwheel_element.attrib["value"]
            )
            if "maxRate" in steeringwheel_element.attrib:
                ocv_action.steeringwheel_rate = convert_float(
                    steeringwheel_element.attrib["maxRate"]
                )
            if "maxTorque" in steeringwheel_element.attrib:
                ocv_action.steeringwheel_torque = convert_float(
                    steeringwheel_element.attrib["maxTorque"]
                )

        ocv_action.gear_active = None
        ocv_action.gear_value = convert_float(0)
        if ocva_element.find("Gear") is not None:
            gear_element = find_mandatory_field(ocva_element, "Gear")
            ocv_action.gear_active = convert_bool(
                gear_element.attrib["active"]
            )
            if "number" in gear_element.attrib:
                ocv_action.gear_value = convert_float(
                    gear_element.attrib["number"]
                )
            elif gear_element.find("AutomaticGear") is not None:
                ocv_action.gear_value = getattr(
                    AutomaticGearType,
                    find_mandatory_field(gear_element, "AutomaticGear").attrib[
                        "gear"
                    ],
                )

            elif gear_element.find("ManualGear") is not None:
                ocv_action.gear_value = convert_float(
                    find_mandatory_field(gear_element, "ManualGear").attrib[
                        "number"
                    ]
                )
            else:
                raise ValueError("no gear number found in OverrideGearAction")

        return ocv_action

    def set_clutch(
        self, active: bool, value: float = 0, rate: Optional[float] = None
    ) -> None:
        """Sets the clutch value.

        Parameters
        ----------
        active : bool
            If the clutch should be overridden.
        value : float, optional
            Value of the clutch. Default is 0.
        rate : float, optional
            Rate of the change (Valid from OpenSCENARIO V1.2).
            Default is None.
        """
        self.clutch_active = convert_bool(active)
        self.clutch_value = convert_float(value)
        self.clutch_rate = rate

    def set_brake(
        self,
        active: bool,
        value: float = 0,
        rate: Optional[float] = None,
        interpret_as_force: bool = False,
    ) -> None:
        """Sets the brake value.

        Parameters
        ----------
        active : bool
            If the brake should be overridden.
        value : float, optional
            Value of the brake. Default is 0.
        rate : float, optional
            The rate of the change (Valid from OpenSCENARIO V1.2).
            Default is None.
        interpret_as_force : bool, optional
            Interpret the value as force instead of percent
            (Valid from OpenSCENARIO V1.2). Default is None.
        """
        self.brake_active = convert_bool(active)
        self.brake_value = convert_float(value)
        self.brake_rate = rate
        self.brake_force = interpret_as_force

    def set_throttle(
        self, active: bool, value: float = 0, rate: Optional[float] = None
    ) -> None:
        """Sets the throttle value.

        Parameters
        ----------
        active : bool
            If the throttle should be overridden.
        value : float, optional
            Value of the throttle. Default is 0.
        rate : float, optional
            Rate of the change (Valid from OpenSCENARIO V1.2).
            Default is None.
        """
        self.throttle_active = convert_bool(active)
        self.throttle_value = convert_float(value)
        self.throttle_rate = rate

    def set_steeringwheel(
        self,
        active: bool,
        value: float = 0,
        rate: Optional[float] = None,
        torque: Optional[float] = None,
    ) -> None:
        """Sets the steeringwheel value.

        Parameters
        ----------
        active : bool
            If the steeringwheel should be overridden.
        value : float, optional
            Value of the steeringwheel. Default is 0.
        rate : float, optional
            The Max Rate of the change (Valid from OpenSCENARIO V1.2).
            Default is None.
        torque : float, optional
            The Max Torque of the change (Valid from OpenSCENARIO V1.2).
            Default is None.
        """
        self.steeringwheel_active = convert_bool(active)
        self.steeringwheel_value = convert_float(value)
        self.steeringwheel_rate = convert_float(rate)
        self.steeringwheel_torque = convert_float(torque)

    def set_parkingbrake(
        self,
        active: bool,
        value: float = 0,
        rate: Optional[float] = None,
        interpret_as_force: bool = False,
    ) -> None:
        """Sets the parkingbrake value.

        Parameters
        ----------
        active : bool
            If the parkingbrake should be overridden.
        value : float, optional
            Value of the parkingbrake. Default is 0.
        rate : float, optional
            The rate of the change (Valid from OpenSCENARIO V1.2).
            Default is None.
        interpret_as_force : bool, optional
            Interpret the value as force instead of percent
            (Valid from OpenSCENARIO V1.2). Default is None.
        """
        self.parkingbrake_active = convert_bool(active)
        self.parkingbrake_value = convert_float(value)
        self.parkingbrake_rate = rate
        self.parkingbrake_force = interpret_as_force

    def set_gear(
        self, active: bool, value: Union[float, AutomaticGearType] = 0
    ) -> None:
        """Sets the gear value.

        Parameters
        ----------
        active : bool
            If the gear should be overridden.
        value : float or AutomaticGearType
            Value of the gear. Default is 0.
        """
        self.gear_active = convert_bool(active)
        if hasattr(AutomaticGearType, str(value)):
            self.gear_value = value
            self._gear_maunal = False
        else:
            self.gear_value = convert_float(value)
            self._gear_maunal = True

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the OverrideControllerValueAction.

        Returns
        -------
        ET.Element
            The XML element representing the
            OverrideControllerValueAction.

        Raises
        ------
        OpenSCENARIOVersionError
            If the OverrideControllerValueAction is used alone in
            OSC 1.0.
        """
        if self.isVersion(minor=0) and not self._used_by_parent:
            raise OpenSCENARIOVersionError(
                "OverrideControllerValueAction cannot be used alone in "
                "OSC 1.0, please add it to a ControllerAction"
            )
        element = ET.Element("PrivateAction")
        controlleraction = ET.SubElement(element, "ControllerAction")
        overrideaction = ET.SubElement(
            controlleraction, "OverrideControllerValueAction"
        )

        if (
            self.throttle_active is None
            and self.brake_active is None
            and self.clutch_active is None
            and self.parkingbrake_active is None
            and self.steeringwheel_active is None
            and self.gear_active is None
        ):
            raise NoActionsDefinedError(
                "No actions were added to the OverrideControllerValueAction"
            )
        if self.throttle_active is not None:
            throttle_dict = {
                "active": get_bool_string(self.throttle_active),
                "value": str(self.throttle_value),
            }
            if self.throttle_rate is not None and self.isVersion(minor=2):
                throttle_dict["maxRate"] = str(self.throttle_rate)
            elif self.throttle_rate is not None and not self.isVersion(
                minor=2
            ):
                raise OpenSCENARIOVersionError(
                    "maxRate was introduced in OpenSCENARIO v1.2"
                )
            ET.SubElement(
                overrideaction,
                "Throttle",
                throttle_dict,
            )
        if self.brake_active is not None:
            if not self.isVersion(minor=2):
                ET.SubElement(
                    overrideaction,
                    "Brake",
                    {
                        "active": get_bool_string(self.brake_active),
                        "value": str(self.brake_value),
                    },
                )
            else:
                override_brake = ET.SubElement(
                    overrideaction,
                    "Brake",
                    {"active": get_bool_string(self.brake_active)},
                )
                brake_dict = {"value": str(self.brake_value)}
                if self.brake_rate is not None:
                    brake_dict["maxRate"] = str(self.brake_rate)
                if self.brake_force:
                    ET.SubElement(
                        override_brake, "BrakeForce", attrib=brake_dict
                    )
                else:
                    ET.SubElement(
                        override_brake, "BrakePercent", attrib=brake_dict
                    )

        if self.clutch_active is not None:
            if self.throttle_rate is not None and self.isVersion(minor=2):
                throttle_dict["maxRate"] = str(self.throttle_rate)
            elif self.throttle_rate is not None and not self.isVersion(
                minor=2
            ):
                raise OpenSCENARIOVersionError(
                    "maxRate was introduced in OpenSCENARIO v1.2"
                )
            clutch_dict = {
                "active": get_bool_string(self.clutch_active),
                "value": str(self.clutch_value),
            }
            if self.clutch_rate is not None and self.isVersion(minor=2):
                clutch_dict["maxRate"] = str(self.clutch_rate)
            elif self.clutch_rate is not None and not self.isVersion(minor=2):
                raise OpenSCENARIOVersionError(
                    "maxRate was introduced in OpenSCENARIO v1.2"
                )
            ET.SubElement(
                overrideaction,
                "Clutch",
                clutch_dict,
            )
        if self.parkingbrake_active is not None:
            if not self.isVersion(minor=2):
                ET.SubElement(
                    overrideaction,
                    "ParkingBrake",
                    {
                        "active": get_bool_string(self.parkingbrake_active),
                        "value": str(self.parkingbrake_value),
                    },
                )
            else:
                override_parking = ET.SubElement(
                    overrideaction,
                    "ParkingBrake",
                    {"active": get_bool_string(self.parkingbrake_active)},
                )
                parkingbrake_dict = {"value": str(self.parkingbrake_value)}
                if self.parkingbrake_rate is not None:
                    parkingbrake_dict["maxRate"] = str(self.parkingbrake_rate)
                if self.parkingbrake_force:
                    ET.SubElement(
                        override_parking,
                        "BrakeForce",
                        attrib=parkingbrake_dict,
                    )
                else:
                    ET.SubElement(
                        override_parking,
                        "BrakePercent",
                        attrib=parkingbrake_dict,
                    )
        if self.steeringwheel_active is not None:
            steering_dict = {
                "active": get_bool_string(self.steeringwheel_active),
                "value": str(self.steeringwheel_value),
            }
            if self.steeringwheel_torque is not None:
                if self.isVersion(minor=2):
                    steering_dict["maxTorque"] = str(self.steeringwheel_torque)
                else:
                    raise OpenSCENARIOVersionError(
                        "maxTorque was introduced in OpenSCENARIO v1.2"
                    )
            if self.steeringwheel_rate is not None:
                if self.isVersion(minor=2):
                    steering_dict["maxRate"] = str(self.steeringwheel_rate)
                else:
                    raise OpenSCENARIOVersionError(
                        "maxRate was introduced in OpenSCENARIO v1.2"
                    )
            ET.SubElement(
                overrideaction,
                "SteeringWheel",
                steering_dict,
            )

        if self.gear_active is not None:
            if not self.isVersion(minor=2):
                ET.SubElement(
                    overrideaction,
                    "Gear",
                    {
                        "active": get_bool_string(self.gear_active),
                        "number": str(self.gear_value),
                    },
                )
            else:
                override_gear_action = ET.SubElement(
                    overrideaction,
                    "Gear",
                    {
                        "active": get_bool_string(self.gear_active),
                    },
                )
                if self._gear_maunal:
                    ET.SubElement(
                        override_gear_action,
                        "ManualGear",
                        {"number": str(int(self.gear_value))},
                    )
                else:
                    ET.SubElement(
                        override_gear_action,
                        "AutomaticGear",
                        {"gear": self.gear_value.get_name()},
                    )

        return element


class VisibilityAction(_PrivateActionType):
    """Creates a VisibilityAction.

    Parameters
    ----------
    graphics : bool
        Visible for graphics or not.
    traffic : bool
        Visible for traffic.
    sensors : bool
        Visible to sensors or not.

    Attributes
    ----------
    graphics : bool
        Visible for graphics or not.
    traffic : bool
        Visible for traffic.
    sensors : bool
        Visible to sensors or not.
    sensor_refs : list of str
        All sensor references.

    Methods
    -------
    parse(element : xml.etree.ElementTree.Element) -> VisibilityAction
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element() -> xml.etree.ElementTree.Element
        Returns the full ElementTree of the class.
    get_attributes() -> dict
        Returns the attributes of the class.
    """

    def __init__(self, graphics: bool, traffic: bool, sensors: bool):
        """Initializes the VisibilityAction.

        Parameters
        ----------
        graphics : bool
            Visible for graphics or not.
        traffic : bool
            Visible for traffic.
        sensors : bool
            Visible to sensors or not.
        """
        self.graphics = convert_bool(graphics)
        self.traffic = convert_bool(traffic)
        self.sensors = convert_bool(sensors)
        self.sensor_refs = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, VisibilityAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.sensor_refs == other.sensor_refs
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "VisibilityAction":
        """Parses the XML element of VisibilityAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A VisibilityAction element (same as generated by the
            class itself).

        Returns
        -------
        VisibilityAction
            A VisibilityAction object.
        """
        va_element = find_mandatory_field(element, "VisibilityAction")
        graphics = convert_bool(va_element.attrib["graphics"])
        traffic = convert_bool(va_element.attrib["traffic"])
        sensors = convert_bool(va_element.attrib["sensors"])
        visibility_action = VisibilityAction(graphics, traffic, sensors)
        sensor_ref_element = va_element.find("SensorReferenceSet")
        if sensor_ref_element is not None:
            for sensor_element in sensor_ref_element.findall(
                "SensorReference"
            ):
                visibility_action.add_sensor_reference(
                    sensor_element.attrib["name"]
                )
        return visibility_action

    def add_sensor_reference(self, sensor_ref: str):
        """Adds a sensor reference to the visibility action.

        Parameters
        ----------
        sensor_ref : str
            Name of a sensor.

        Returns
        -------
        VisibilityAction
            The updated VisibilityAction instance.
        """
        self.sensor_refs.append(sensor_ref)
        return self

    def get_attributes(self) -> dict:
        """Returns the attributes of the VisibilityAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            VisibilityAction.
        """
        return {
            "graphics": get_bool_string(self.graphics),
            "traffic": get_bool_string(self.traffic),
            "sensors": get_bool_string(self.sensors),
        }

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the VisibilityAction.

        Returns
        -------
        ET.Element
            The XML element representing the VisibilityAction.
        """
        element = ET.Element("PrivateAction")
        visibility_element = ET.SubElement(
            element, "VisibilityAction", self.get_attributes()
        )
        if self.sensor_refs:
            if self.isVersionEqLess(minor=1):
                raise OpenSCENARIOVersionError(
                    "SensorReference was added in OSC V1.2"
                )
            sensor_ref_element = ET.SubElement(
                visibility_element, "SensorReferenceSet"
            )
            for sensor in self.sensor_refs:
                ET.SubElement(
                    sensor_ref_element,
                    "SensorReference",
                    {"name": str(sensor)},
                )
        return element


class SynchronizeAction(_PrivateActionType):
    """Synchronizes an entity's arrival at a destination with a master entity.
    Both entities are provided with their own reference position which shall be
    reached at the same time. Final speed can be specified. Note that the
    reference positions can be different or identical.

    Parameters
    ----------
    entity : str
        Entity to synchronize with.
    entity_PositionType : _PositionType
        The position of the entity to synchronize to.
    target_PositionType : _PositionType
        The position of the target that should synchronize.
    speed : float
        The absolute speed of the target that should synchronize.
    target_tolerance_master : float, optional
        Tolerance offset of the master's position [m]. (Valid from
        OpenSCENARIO V1.1)
    target_tolerance : float, optional
        Tolerance offset of the target's position [m]. (Valid from
        OpenSCENARIO V1.1)
    final_speed : AbsoluteSpeed or RelativeSpeedToMaster, optional
        The speed that the synchronized entity should have at its
        target position. (Valid from OpenSCENARIO V1.1)

    Attributes
    ----------
    entity : str
        Entity to synchronize with.
    entity_PositionType : _PositionType
        The position of the entity to synchronize to.
    target_PositionType : _PositionType
        The position of the target that should synchronize.
    speed : float
        The absolute speed of the target that should synchronize.
    target_tolerance_master : float, optional
        Tolerance offset of the master's position [m]. (Valid from
        OpenSCENARIO V1.1)
    target_tolerance : float, optional
        Tolerance offset of the target's position [m]. (Valid from
        OpenSCENARIO V1.1)
    final_speed : AbsoluteSpeed or RelativeSpeedToMaster, optional
        The speed that the synchronized entity should have at its
        target position. (Valid from OpenSCENARIO V1.1)

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns the attributes of the class.
    """

    def __init__(
        self,
        entity: str,
        entity_PositionType: _PositionType,
        target_PositionType: _PositionType,
        target_tolerance_master: Optional[float] = None,
        target_tolerance: Optional[float] = None,
        final_speed: Optional[
            Union[AbsoluteSpeed, RelativeSpeedToMaster]
        ] = None,
    ):
        """Initialize the SynchronizeAction.

        Parameters
        ----------
        entity : str
            Entity to synchronize with.
        entity_PositionType : _PositionType
            The position of the entity to synchronize to.
        target_PositionType : _PositionType
            The position of the target that should synchronize.
        target_tolerance_master : float, optional
            Tolerance offset of the master's position [m].
            Valid from OpenSCENARIO V1.1.
        target_tolerance : float, optional
            Tolerance offset of the target's position [m].
            Valid from OpenSCENARIO V1.1.
        final_speed : AbsoluteSpeed or RelativeSpeedToMaster, optional
            The speed that the synchronized entity should have at its
            target position. Valid from OpenSCENARIO V1.1.
        """

        self.entity = entity
        if not isinstance(entity_PositionType, _PositionType):
            raise TypeError(
                "entity_PositionType input is not a valid Position"
            )

        if not isinstance(target_PositionType, _PositionType):
            raise TypeError(
                "target_PositionType input is not a valid Position"
            )
        self.entity_PositionType = entity_PositionType
        self.target_PositionType = target_PositionType
        self.target_tolerance_master = convert_float(target_tolerance_master)
        self.target_tolerance = convert_float(target_tolerance)
        if final_speed and not (
            isinstance(final_speed, (AbsoluteSpeed, RelativeSpeedToMaster))
        ):
            raise TypeError(
                "final_speed input is not AbsoluteSpeed or RelativeSpeedToMaster type"
            )

        self.final_speed = final_speed

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SynchronizeAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.entity_PositionType == other.entity_PositionType
                and self.target_PositionType == other.target_PositionType
                and self.final_speed == other.final_speed
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "SynchronizeAction":
        """Parses the XML element of SynchronizeAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A SynchronizeAction element (same as generated by the class
            itself).

        Returns
        -------
        SynchronizeAction
            A SynchronizeAction object.
        """
        sa_element = find_mandatory_field(element, "SynchronizeAction")
        entity = sa_element.attrib["masterEntityRef"]

        target_tolerance = None
        if "targetTolerance" in sa_element.attrib:
            target_tolerance = convert_float(
                sa_element.attrib["targetTolerance"]
            )

        target_tolerance_master = None
        if "targetToleranceMaster" in sa_element.attrib:
            target_tolerance_master = convert_float(
                sa_element.attrib["targetToleranceMaster"]
            )

        targetPositionMaster = _PositionFactory.parse_position(
            find_mandatory_field(sa_element, "TargetPositionMaster")
        )
        targetPosition = _PositionFactory.parse_position(
            find_mandatory_field(sa_element, "TargetPosition")
        )

        finalSpeed = None
        if sa_element.find("FinalSpeed") is not None:
            sa_element = find_mandatory_field(sa_element, "FinalSpeed")
            if sa_element.find("AbsoluteSpeed") is not None:
                finalSpeed = AbsoluteSpeed.parse(sa_element)
            if sa_element.find("RelativeSpeedToMaster") is not None:
                finalSpeed = RelativeSpeedToMaster.parse(sa_element)

        return SynchronizeAction(
            entity,
            targetPositionMaster,
            targetPosition,
            target_tolerance_master,
            target_tolerance,
            finalSpeed,
        )

    def get_attributes(self) -> dict:
        """Returns the attributes of the AbsoluteSynchronizeAction as a dict.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            AbsoluteSynchronizeAction.
        """
        attr = {"masterEntityRef": self.entity}
        if self.isVersion(1, 0):
            return attr
        if self.target_tolerance_master is not None:
            attr.update(
                {"targetToleranceMaster": str(self.target_tolerance_master)}
            )
        if self.target_tolerance is not None:
            attr.update({"targetTolerance": str(self.target_tolerance)})
        return attr

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the AbsoluteSynchronizeAction.

        Returns
        -------
        ET.Element
            The XML element representing the AbsoluteSynchronizeAction.
        """
        element = ET.Element("PrivateAction")
        syncaction = ET.SubElement(
            element, "SynchronizeAction", self.get_attributes()
        )
        syncaction.append(
            self.entity_PositionType.get_element("TargetPositionMaster")
        )
        syncaction.append(
            self.target_PositionType.get_element("TargetPosition")
        )
        if self.final_speed is not None:
            syncaction.append(self.final_speed.get_element())
        return element


class LightStateAction(_PrivateActionType):
    """LightStateAction creates an AppearanceAction of the Type
    LightStateAction.

    Parameters
    ----------
    light_type : VehicleLightType or UserDefinedLight
        The type of the light.
    mode : LightMode
        The new mode of the light.
    transition_time : float, optional
        The transition time of the light. Default is 0.
    flashing_off_duration : float, optional
        How long the light should be off when LightMode is set to
        "flashing".
    flashing_on_duration : float, optional
        How long the light should be on when LightMode is set to
        "flashing".
    intensity : float, optional
        The luminous intensity of the light.
    color : Color, optional
        The color of the light.

    Attributes
    ----------
    lightstate : _LightState
        The type of light.
    light_type : VehicleLightType or UserDefinedLight
        The state of the light.
    transition_time : float, optional
        The transition time of the light. Default is 0.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns the attributes of the class.
    """

    def __init__(
        self,
        light_type: Union[VehicleLightType, UserDefinedLight],
        mode: LightMode,
        transition_time: float = 0,
        flashing_off_duration: Optional[float] = None,
        flashing_on_duration: Optional[float] = None,
        intensity: Optional[float] = None,
        color: Optional[Color] = None,
    ):
        """Initialize the LightStateAction.

        Parameters
        ----------
        light_type : VehicleLightType or UserDefinedLight
            The type of the light.
        mode : LightMode
            The new mode of the light.
        transition_time : float, optional
            The transition time of the light. Default is 0.
        flashing_off_duration : float, optional
            Duration the light should be off when LightMode is set to
            "flashing".
        flashing_on_duration : float, optional
            Duration the light should be on when LightMode is set to
            "flashing".
        intensity : float, optional
            The luminous intensity of the light.
        color : Color, optional
            The color of the light.
        """
        try:
            self.light_type = convert_enum(light_type, VehicleLightType)
        except Exception:
            if not isinstance(light_type, UserDefinedLight):
                raise TypeError(
                    "light_type input is not of type VehicleLightType or UserDefinedLight"
                )

            self.light_type = light_type

        self.lightstate = _LightState(
            mode, color, intensity, flashing_off_duration, flashing_on_duration
        )

        self.transition_time = convert_float(transition_time)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LightStateAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.light_type == other.light_type
                and self.lightstate == other.lightstate
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "LightStateAction":
        """Parses the XML element of LightStateAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A LightStateAction element (same as generated by the class
            itself).

        Returns
        -------
        LightStateAction
            A LightStateAction object.
        """
        light_element = find_mandatory_field(
            element, "AppearanceAction/LightStateAction"
        )
        transition_time = None
        if "transitionTime" in light_element.attrib:
            transition_time = convert_float(
                light_element.attrib["transitionTime"]
            )
        light_state = _LightState.parse(
            find_mandatory_field(light_element, "LightState")
        )
        type_element = find_mandatory_field(light_element, "LightType")
        if type_element.find("UserDefinedLight") is not None:
            light_type = UserDefinedLight.parse(
                find_mandatory_field(type_element, "UserDefinedLight")
            )
        else:
            light_type = convert_enum(
                find_mandatory_field(type_element, "VehicleLight").attrib[
                    "vehicleLightType"
                ],
                VehicleLightType,
            )
        # create with dummy mode
        light_state_action = LightStateAction(
            light_type, LightMode.on, transition_time
        )
        light_state_action.lightstate = light_state
        return light_state_action

    def get_attributes(self) -> dict:
        """Returns the attributes of the LightStateAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the LightStateAction.
        """
        attr = {"transitionTime": str(self.transition_time)}
        return attr

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the LightStateAction."""
        element = ET.Element("PrivateAction")
        appear_element = ET.SubElement(element, "AppearanceAction")
        light_element = ET.SubElement(
            appear_element, "LightStateAction", self.get_attributes()
        )
        light_element.append(self.lightstate.get_element())

        light_type_element = ET.SubElement(light_element, "LightType")
        if hasattr(VehicleLightType, str(self.light_type)):
            ET.SubElement(
                light_type_element,
                "VehicleLight",
                attrib={"vehicleLightType": self.light_type.get_name()},
            )
        else:
            light_type_element.append(self.light_type.get_element())

        return element


class AnimationAction(_PrivateActionType):
    """AnimationAction creates an AppearanceAction of the Type AnimationAction.

    Parameters
    ----------
    animation_type : VehicleComponentType, UserDefinedComponent,
        PedestrianAnimation, AnimationFile or UserDefinedAnimation
        The animation to be taken place.
    duration : float, optional
        The duration of the animation. Default is None.
    loop : bool, optional
        If the animation should be looped. Default is None.
    state : float, optional
        The state the animation should be put to. Default is None.

    Attributes
    ----------
    animation_type : _ComponentAnimation, PedestrianAnimation,
        AnimationFile or UserDefinedAnimation
        The animation to be taken place.
    duration : float
        The duration of the animation.
    loop : bool
        If the animation should be looped.
    state : float
        The state the animation should be put to.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns the attributes of the class.
    """

    def __init__(
        self,
        animation_type: Union[
            VehicleComponentType,
            UserDefinedComponent,
            PedestrianAnimation,
            AnimationFile,
            UserDefinedAnimation,
            _ComponentAnimation,
        ],
        duration: Optional[float] = None,
        loop: Optional[bool] = None,
        state: Optional[float] = None,
    ):
        """Initialize the AnimationAction.

        Parameters
        ----------
        animation_type : VehicleComponentType, UserDefinedComponent,
            PedestrianAnimation, AnimationFile or UserDefinedAnimation
            The animation to be taken place.
        duration : float, optional
            The duration of the animation. Default is None.
        loop : bool, optional
            If the animation should be looped. Default is None.
        state : float, optional
            The state the animation should be put to. Default is None.
        """
        if isinstance(animation_type, UserDefinedComponent):
            self.animation_type = _ComponentAnimation(animation_type)
        elif isinstance(
            animation_type,
            (
                PedestrianAnimation,
                AnimationFile,
                UserDefinedAnimation,
                _ComponentAnimation,
            ),
        ):
            self.animation_type = animation_type
        else:
            self.animation_type = _ComponentAnimation(
                _VehicleComponent(animation_type)
            )

        self.duration = convert_float(duration)
        if loop is not None and not isinstance(loop, bool):
            raise TypeError("loop input is not of type bool")
        self.loop = loop
        self.state = convert_float(state)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AnimationAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.animation_type == other.animation_type
                and self.state == other.state
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "AnimationAction":
        """Parses the XML element of AnimationAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A AnimationAction element (same as generated by the class
            itself).

        Returns
        -------
        AnimationAction
            A AnimationAction object.
        """
        animation_element = find_mandatory_field(
            element, "AppearanceAction/AnimationAction"
        )
        duration = None
        if "animationDuration" in animation_element.attrib:
            duration = convert_float(
                animation_element.attrib["animationDuration"]
            )
        loop = None
        if "loop" in animation_element.attrib:
            loop = convert_bool(animation_element.attrib["loop"])
        animation_state = find_mandatory_field(
            animation_element, "AnimationState"
        )
        state = None
        if animation_state is not None:
            state = convert_float(animation_state.attrib["state"])
        animation_type = _AnimationTypeFactory.parse_animationtype(
            find_mandatory_field(animation_element, "AnimationType")
        )
        return AnimationAction(animation_type, duration, loop, state)

    def get_attributes(self) -> dict:
        """Retrieve the attributes of the AnimationAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the AnimationAction.
        """

        retdict = {}

        if self.duration is not None:
            retdict["animationDuration"] = str(self.duration)
        if self.loop is not None:
            retdict["loop"] = get_bool_string(self.loop)

        return retdict

    def get_element(self) -> ET.Element:
        """Constructs and returns an ElementTree representation of the
        AnimationAction.

        Returns
        -------
        ET.Element
            The root XML element representing the AnimationAction.
        """

        element = ET.Element("PrivateAction")
        appear_element = ET.SubElement(element, "AppearanceAction")
        animation_element = ET.SubElement(
            appear_element, "AnimationAction", self.get_attributes()
        )

        animation_type_element = ET.SubElement(
            animation_element, "AnimationType"
        )
        animation_type_element.append(self.animation_type.get_element())
        if self.state is not None:
            ET.SubElement(
                animation_element,
                "AnimationState",
                attrib={"state": str(self.state)},
            )

        return element


#### Global Actions ####
class ParameterAddAction(_ActionType):
    """The ParameterAddAction class creates a ParameterAction of type
    ParameterModifyAction which adds a value to an existing Parameter (valid to
    V1.1, deprecated since V1.2).

    Parameters
    ----------
    parameter_ref : str
        Name of the parameter.
    value : float
        The value that should be added to the parameter.

    Attributes
    ----------
    parameter_ref : str
        Name of the parameter.
    value : float
        The value that should be added to the parameter.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, parameter_ref: str, value: float):
        """Initialize the ParameterAddAction.

        Parameters
        ----------
        parameter_ref : str
            Name of the parameter.
        value : float
            The value that should be added to the parameter.
        """
        self.parameter_ref = parameter_ref
        self.value = convert_float(value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ParameterAddAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.parameter_ref == other.parameter_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "ParameterAddAction":
        """Parses the XML element of ParameterAddAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A ParameterAddAction element (same as generated by the
            class itself).

        Returns
        -------
        ParameterAddAction
            A ParameterAddAction object.
        """
        pa_element = find_mandatory_field(element, "ParameterAction")
        parameterRef = pa_element.attrib["parameterRef"]

        ma_element = find_mandatory_field(pa_element, "ModifyAction")
        rule_element = find_mandatory_field(ma_element, "Rule")
        mbv_element = find_mandatory_field(rule_element, "AddValue")
        value = convert_float(mbv_element.attrib["value"])

        return ParameterAddAction(parameterRef, value)

    def get_attributes(self) -> dict:
        """Returns the attributes of the ParameterAddAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            ParameterAddAction.
        """
        return {"value": str(self.value)}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the ParameterAddAction.

        Returns
        -------
        ET.Element
            The XML element representing the ParameterAddAction.
        """
        if self.version_minor > 1:
            raise OpenSCENARIOVersionError(
                "ParameterAddAction was deprecated in OSC 1.2, please use VariableAddAction instead"
            )
        element = ET.Element("GlobalAction")
        paramaction = ET.SubElement(
            element, "ParameterAction", {"parameterRef": self.parameter_ref}
        )
        modifaction = ET.SubElement(paramaction, "ModifyAction")
        rule = ET.SubElement(modifaction, "Rule")
        ET.SubElement(rule, "AddValue", self.get_attributes())

        return element


class ParameterMultiplyAction(_ActionType):
    """The ParameterMultiplyAction class creates a ParameterAction of type
    ParameterModifyAction which multiplies a value to an existing Parameter
    (valid to V1.1, deprecated since V1.2).

    Parameters
    ----------
    parameter_ref : str
        Name of the parameter.
    value : float
        The value that should be multiplied to the parameter.

    Attributes
    ----------
    parameter_ref : str
        Name of the parameter.
    value : float
        The value that should be multiplied to the parameter.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, parameter_ref: str, value: float):
        """Initialize the ParameterMultiplyAction.

        Parameters
        ----------
        parameter_ref : str
            Name of the parameter.
        value : float
            The value that should be added to the parameter.
        """
        self.parameter_ref = parameter_ref
        self.value = convert_float(value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ParameterMultiplyAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.parameter_ref == other.parameter_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "ParameterMultiplyAction":
        """Parses the XML element of ParameterMultiplyAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A ParameterMultiplyAction element (same as generated by the
            class itself).

        Returns
        -------
        ParameterMultiplyAction
            A ParameterMultiplyAction object.
        """
        pa_element = find_mandatory_field(element, "ParameterAction")
        parameterRef = pa_element.attrib["parameterRef"]

        ma_element = find_mandatory_field(pa_element, "ModifyAction")
        rule_element = find_mandatory_field(ma_element, "Rule")
        mbv_element = find_mandatory_field(rule_element, "MultiplyByValue")
        value = convert_float(mbv_element.attrib["value"])

        return ParameterMultiplyAction(parameterRef, value)

    def get_attributes(self) -> dict:
        """Returns the attributes of the ParameterMultiplyAction as a dict.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            ParameterMultiplyAction.
        """
        return {"value": str(self.value)}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the ParameterMultiplyAction.

        Returns
        -------
        ET.Element
            The XML element representing the ParameterMultiplyAction.
        """
        if self.version_minor > 1:
            raise OpenSCENARIOVersionError(
                "ParameterMultiplyAction was deprecated in OSC 1.2, "
                "please use VariableMultiplyAction instead"
            )
        element = ET.Element("GlobalAction")
        paramaction = ET.SubElement(
            element, "ParameterAction", {"parameterRef": self.parameter_ref}
        )
        modifaction = ET.SubElement(paramaction, "ModifyAction")
        rule = ET.SubElement(modifaction, "Rule")
        ET.SubElement(rule, "MultiplyByValue", self.get_attributes())

        return element


class ParameterSetAction(_ActionType):
    """The ParameterSetAction class creates a ParameterAction which adds a
    value to an existing Parameter (valid to V1.1, deprecated since V1.2).

    Parameters
    ----------
    parameter_ref : str
        Name of the parameter.
    value : float
        The value that should be set to the parameter.

    Attributes
    ----------
    parameter_ref : str
        Name of the parameter.
    value : float
        The value that should be set to the parameter.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an instance
        of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, parameter_ref: str, value: float):
        """Initialize the ParameterSetAction.

        Parameters
        ----------
        parameter_ref : str
            Name of the parameter.
        value : float
            The value that should be added to the parameter.
        """
        self.parameter_ref = parameter_ref
        self.value = value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ParameterSetAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.parameter_ref == other.parameter_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "ParameterSetAction":
        """Parses the XML element of ParameterSetAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A ParameterSetAction element (same as generated by the class
            itself).

        Returns
        -------
        ParameterSetAction
            A ParameterSetAction object.
        """
        pa_element = find_mandatory_field(element, "ParameterAction")
        parameterRef = pa_element.attrib["parameterRef"]
        psa_element = find_mandatory_field(pa_element, "SetAction")
        value = psa_element.attrib["value"]
        psa = ParameterSetAction(parameterRef, value)
        psa.setVersion(minor=1)
        return psa  # ParameterSetAction(parameterRef, value)

    def get_attributes(self) -> dict:
        """Returns the attributes of the ParameterSetAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            ParameterSetAction.
        """
        return {"value": str(self.value)}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the ParameterSetAction.

        Returns
        -------
        ET.Element
            The XML element representing the ParameterSetAction.
        """
        if self.version_minor > 1:
            raise OpenSCENARIOVersionError(
                "ParameterSetAction was deprecated in OSC 1.2, please use VariableSetAction instead"
            )
        element = ET.Element("GlobalAction")
        paramaction = ET.SubElement(
            element, "ParameterAction", {"parameterRef": self.parameter_ref}
        )
        ET.SubElement(paramaction, "SetAction", self.get_attributes())

        return element


class VariableAddAction(_ActionType):
    """The VariableAddAction class creates a VariableAction of type
    VariableModifyAction which adds a value to an existing Variable (valid from
    V1.2).

    Parameters
    ----------
    variable_ref : str
        Name of the variable.
    value : float
        The value that should be added to the variable.

    Attributes
    ----------
    variable_ref : str
        Name of the variable.
    value : float
        The value that should be added to the variable.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, variable_ref: str, value: float):
        """Initialize the VariableAddAction.

        Parameters
        ----------
        variable_ref : str
            Name of the variable.
        value : float
            The value that should be added to the variable.
        """
        self.variable_ref = variable_ref
        self.value = value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, VariableAddAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.variable_ref == other.variable_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "VariableAddAction":
        """Parses the XML element of VariableAddAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A VariableAddAction element (same as generated by the class
            itself).

        Returns
        -------
        VariableAddAction
            A VariableAddAction object.
        """
        pa_element = find_mandatory_field(element, "VariableAction")
        variableRef = pa_element.attrib["variableRef"]

        ma_element = find_mandatory_field(pa_element, "ModifyAction")
        rule_element = find_mandatory_field(ma_element, "Rule")
        mbv_element = find_mandatory_field(rule_element, "AddValue")
        value = mbv_element.attrib["value"]

        return VariableAddAction(variableRef, value)

    def get_attributes(self) -> dict:
        """Returns the attributes of the AbsoluteSpeedAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            AbsoluteSpeedAction.
        """
        return {"value": str(self.value)}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the AbsoluteSpeedAction.

        Returns
        -------
        ET.Element
            The XML element representing the AbsoluteSpeedAction.
        """
        if self.version_minor < 2:
            raise OpenSCENARIOVersionError(
                "VariableActions were added in OSC 1.2"
            )
        element = ET.Element("GlobalAction")
        paramaction = ET.SubElement(
            element, "VariableAction", {"variableRef": self.variable_ref}
        )
        modifaction = ET.SubElement(paramaction, "ModifyAction")
        rule = ET.SubElement(modifaction, "Rule")
        ET.SubElement(rule, "AddValue", self.get_attributes())

        return element


class VariableMultiplyAction(_ActionType):
    """The VariableMultiplyAction class creates a VariableAction of type
    VariableModifyAction which multiplies a value to an existing Variable
    (valid from V1.2).

    Parameters
    ----------
    variable_ref : str
        Name of the variable.
    value : float
        The value that should be multiplied to the variable.

    Attributes
    ----------
    variable_ref : str
        Name of the variable.
    value : float
        The value that should be multiplied to the variable.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, variable_ref: str, value: float):
        """Initialize the VariableMultiplyAction.

        Parameters
        ----------
        variable_ref : str
            Name of the variable.
        value : float
            The value that should be added to the variable.
        """
        self.variable_ref = variable_ref
        self.value = value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, VariableMultiplyAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.variable_ref == other.variable_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "VariableMultiplyAction":
        """Parses the XML element of VariableMultiplyAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A VariableMultiplyAction element (same as generated by the
            class itself).

        Returns
        -------
        VariableMultiplyAction
            A VariableMultiplyAction object.
        """
        pa_element = find_mandatory_field(element, "VariableAction")
        variableRef = pa_element.attrib["variableRef"]

        ma_element = find_mandatory_field(pa_element, "ModifyAction")
        rule_element = find_mandatory_field(ma_element, "Rule")
        mbv_element = find_mandatory_field(rule_element, "MultiplyByValue")
        value = mbv_element.attrib["value"]

        return VariableMultiplyAction(variableRef, value)

    def get_attributes(self) -> dict:
        """Returns the attributes of the VariableMultiplyAction as a dict.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            VariableMultiplyAction.
        """
        return {"value": str(self.value)}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the VariableMultiplyAction."""
        if self.version_minor < 2:
            raise OpenSCENARIOVersionError(
                "VariableActions were added in OSC 1.2"
            )
        element = ET.Element("GlobalAction")
        paramaction = ET.SubElement(
            element, "VariableAction", {"variableRef": self.variable_ref}
        )
        modifaction = ET.SubElement(paramaction, "ModifyAction")
        rule = ET.SubElement(modifaction, "Rule")
        ET.SubElement(rule, "MultiplyByValue", self.get_attributes())

        return element


class VariableSetAction(_ActionType):
    """The VariableSetAction class creates a VariableAction which sets a value
    to an existing Variable (valid from V1.2).

    Parameters
    ----------
    variable_ref : str
        Name of the variable.
    value : float
        The value that should be set to the variable.

    Attributes
    ----------
    variable_ref : str
        Name of the variable.
    value : float
        The value that should be set to the variable.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, variable_ref: str, value: float):
        """Initialize the VariableSetAction.

        Parameters
        ----------
        variable_ref : str
            Name of the variable.
        value : float
            The value that should be added to the variable.
        """
        self.variable_ref = variable_ref
        self.value = value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, VariableSetAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.variable_ref == other.variable_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "VariableSetAction":
        """Parses the XML element of VariableSetAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A VariableSetAction element (same as generated by the class
            itself).

        Returns
        -------
        VariableSetAction
            A VariableSetAction object.
        """
        pa_element = find_mandatory_field(element, "VariableAction")
        variableRef = pa_element.attrib["variableRef"]
        psa_element = find_mandatory_field(pa_element, "SetAction")
        value = psa_element.attrib["value"]
        return VariableSetAction(variableRef, value)

    def get_attributes(self) -> dict:
        """Returns the attributes of the VariableSetAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            VariableSetAction.
        """
        return {"value": str(self.value)}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the VariableSetAction.

        Returns
        -------
        ET.Element
            The XML element representing the VariableSetAction.
        """
        if self.version_minor < 2:
            raise OpenSCENARIOVersionError(
                "VariableActions were added in OSC 1.2"
            )
        element = ET.Element("GlobalAction")
        paramaction = ET.SubElement(
            element, "VariableAction", {"variableRef": self.variable_ref}
        )
        ET.SubElement(paramaction, "SetAction", self.get_attributes())

        return element


class TrafficSignalStateAction(_ActionType):
    """The TrafficSignalStateAction class creates an Infrastructure action
    which controls the state of a traffic signal.

    Parameters
    ----------
    name : str
        ID of the signal in the road network.
    state : str
        The state to set to the traffic light.

    Attributes
    ----------
    name : str
        ID of the signal in the road network.
    state : str
        The state to set to the traffic light.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, name: str, state: str):
        """Initialize the TrafficSignalStateAction.

        Parameters
        ----------
        name : str
            ID of the signal in the road network.
        state : str
            The state to set to the traffic light.
        """
        self.name = name
        self.state = state

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TrafficSignalStateAction):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TrafficSignalStateAction":
        """Parses the XML element of TrafficSignalStateAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A TrafficSignalStateAction element (same as generated by the
            class itself).

        Returns
        -------
        TrafficSignalStateAction
            A TrafficSignalStateAction object.
        """
        isa_element = find_mandatory_field(element, "InfrastructureAction")
        tsa_element = find_mandatory_field(isa_element, "TrafficSignalAction")
        tss_element = find_mandatory_field(
            tsa_element, "TrafficSignalStateAction"
        )
        name = tss_element.attrib["name"]
        state = tss_element.attrib["state"]
        return TrafficSignalStateAction(name, state)

    def get_attributes(self) -> dict:
        """Returns the attributes of the TrafficSignalStateAction as a dict.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            TrafficSignalStateAction.
        """
        return {"name": self.name, "state": self.state}

    def get_element(self) -> ET.Element:
        """Generates an XML element tree representation of a
        TrafficSignalStateAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The root XML element representing the GlobalAction
            with nested InfrastructureAction and TrafficSignalAction.
        """

        element = ET.Element("GlobalAction")
        infra = ET.SubElement(element, "InfrastructureAction")
        tsa = ET.SubElement(infra, "TrafficSignalAction")
        ET.SubElement(tsa, "TrafficSignalStateAction", self.get_attributes())

        return element


class AddEntityAction(_ActionType):
    """AddEntityAction class creates an EntityAction to add an entity to the
    scenario.

    Parameters
    ----------
    entityref : str
        Reference name of the newly added vehicle.
    position : _PositionType
        Position where the vehicle should be added.

    Attributes
    ----------
    entityref : str
        Reference name of the newly added vehicle.
    position : _PositionType
        Position where the vehicle should be added.

    Methods
    -------
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, entityref: str, position: _PositionType):
        """Initialize the AddEntityAction.

        Parameters
        ----------
        entityref : str
            Reference name of the newly added vehicle.
        position : _PositionType
            Position where the vehicle should be added.
        """

        self.entityref = entityref
        if not isinstance(position, _PositionType):
            raise TypeError("position input is not of a known _PositionType")
        self.position = position

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AddEntityAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.position == other.position
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "AddEntityAction":
        """Parses the XML element of AddEntityAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A AddEntityAction element (same as generated by the class
            itself).

        Returns
        -------
        AddEntityAction
            A AddEntityAction object.
        """
        ea_element = find_mandatory_field(element, "EntityAction")
        entityref = ea_element.attrib["entityRef"]
        aea_element = find_mandatory_field(ea_element, "AddEntityAction")
        position = _PositionFactory.parse_position(
            find_mandatory_field(aea_element, "Position")
        )
        return AddEntityAction(entityref, position)

    def get_attributes(self) -> dict:
        """Returns the attributes of the AddEntityAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the AddEntityAction.
        """
        return {"entityRef": self.entityref}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the AddEntityAction.

        Returns
        -------
        ET.Element
            The XML element representing the AddEntityAction.
        """
        element = ET.Element("GlobalAction")
        entityact = ET.SubElement(
            element, "EntityAction", attrib=self.get_attributes()
        )
        addentity = ET.SubElement(entityact, "AddEntityAction")
        addentity.append(self.position.get_element())

        return element


class DeleteEntityAction(_ActionType):
    """The DeleteEntityAction class creates an EntityAction that removes an
    entity from the scenario.

    Parameters
    ----------
    entityref : str
        Reference name of the vehicle to remove.

    Attributes
    ----------
    entityref : str
        Reference name of the vehicle to remove.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, entityref: str):
        """Initialize the DeleteEntityAction.

        Parameters
        ----------
        entityref : str
            Reference name of the vehicle to remove.
        """

        self.entityref = entityref

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DeleteEntityAction):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "DeleteEntityAction":
        """Parses the XML element of DeleteEntityAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A DeleteEntityAction element (same as generated by the class
            itself).

        Returns
        -------
        DeleteEntityAction
            A DeleteEntityAction object.
        """
        ea_element = find_mandatory_field(element, "EntityAction")
        entityref = ea_element.attrib["entityRef"]
        return DeleteEntityAction(entityref)

    def get_attributes(self) -> dict:
        """Returns the attributes of the DeleteEntityAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            DeleteEntityAction.
        """
        return {"entityRef": self.entityref}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the DeleteEntityAction.

        Returns
        -------
        ET.Element
            The XML element representing the DeleteEntityAction.
        """
        element = ET.Element("GlobalAction")
        entityact = ET.SubElement(
            element, "EntityAction", attrib=self.get_attributes()
        )
        ET.SubElement(entityact, "DeleteEntityAction")

        return element


class TrafficSignalControllerAction(_ActionType):
    """The TrafficSignalControllerAction class creates an Infrastructure action
    which activates a controller of a traffic signal.

    Parameters
    ----------
    phase : str
        Phase of the signal.
    traffic_signalcontroller_ref : str
        Reference to the traffic signal controller.

    Attributes
    ----------
    phase : str
        Phase of the signal.
    traffic_signalcontroller_ref : str
        Reference to the traffic signal controller.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, phase: str, traffic_signalcontroller_ref: str):
        """Initialize the TrafficSignalControllerAction.

        Parameters
        ----------
        phase : str
            Phase of the signal.
        traffic_signalcontroller_ref : str
            Reference to the traffic signal controller.
        """
        self.phase = phase
        self.traffic_signalcontroller_ref = traffic_signalcontroller_ref

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TrafficSignalControllerAction):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TrafficSignalControllerAction":
        """Parses the XML element of TrafficSignalControllerAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A TrafficSignalControllerAction element (same as generated
            by the class itself).

        Returns
        -------
        TrafficSignalControllerAction
            A TrafficSignalControllerAction object.
        """
        isa_element = find_mandatory_field(element, "InfrastructureAction")
        tsa_element = find_mandatory_field(isa_element, "TrafficSignalAction")
        tsc_element = find_mandatory_field(
            tsa_element, "TrafficSignalControllerAction"
        )

        phase = tsc_element.attrib["phase"]
        tsc_ref = tsc_element.attrib["trafficSignalControllerRef"]

        return TrafficSignalControllerAction(phase, tsc_ref)

    def get_attributes(self) -> dict:
        """Returns the attributes of the TrafficSignalControllerAction as a
        dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            TrafficSignalControllerAction.
        """
        return {
            "phase": self.phase,
            "trafficSignalControllerRef": self.traffic_signalcontroller_ref,
        }

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the TrafficSignalControllerAction.

        Returns
        -------
        ET.Element
            The XML element representing the TrafficSignalControllerAction.
        """
        element = ET.Element("GlobalAction")
        infra = ET.SubElement(element, "InfrastructureAction")
        tsa = ET.SubElement(infra, "TrafficSignalAction")
        ET.SubElement(
            tsa, "TrafficSignalControllerAction", self.get_attributes()
        )

        return element


class TrafficSourceAction(_ActionType):
    """The TrafficSourceAction class creates a TrafficAction of the type
    TrafficSourceAction.

    Parameters
    ----------
    rate : float
        Rate of appearing traffic.
    radius : float
        The radius of the source around the position.
    position : _PositionType
        Any Position to define the source.
    trafficdefinition : TrafficDefinition
        Definition of the traffic.
    velocity : float, optional
        Starting velocity of the traffic. Default is None.
    name : str, optional
        Name of the TrafficAction, can be used to stop the TrafficAction
        (valid from V1.1). Default is None.

    Attributes
    ----------
    rate : float
        Rate of appearing traffic.
    radius : float
        The radius of the source around the position.
    position : _PositionType
        Any Position to define the source.
    trafficdefinition : TrafficDefinition
        Definition of the traffic.
    velocity : float, optional
        Starting velocity of the traffic. Default is None.
    name : str, optional
        Name of the TrafficAction, can be used to stop the TrafficAction
        (valid from V1.1).

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        rate: float,
        radius: float,
        position: _PositionType,
        trafficdefinition: TrafficDefinition,
        velocity: Optional[float] = None,
        name: Optional[str] = None,
    ):
        """Initialize the TrafficSourceAction.

        Parameters
        ----------
        rate : float
            Rate of appearing traffic.
        radius : float
            The radius of the source around the position.
        position : _PositionType
            Any Position to define the source.
        trafficdefinition : TrafficDefinition
            Definition of the traffic.
        velocity : float, optional
            Starting velocity of the traffic. Default is None.
        name : str, optional
            Name of the TrafficAction, can be used to stop the
            TrafficAction (valid from V1.1). Default is None.
        """
        self.rate = convert_float(rate)
        self.radius = convert_float(radius)
        if not isinstance(position, _PositionType):
            raise TypeError("position input is not a valid Position")

        if not isinstance(trafficdefinition, TrafficDefinition):
            raise TypeError(
                "trafficdefinition input is not of type TrafficDefinition"
            )
        self.position = position
        self.trafficdefinition = trafficdefinition
        self.velocity = convert_float(velocity)
        self.name = name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TrafficSourceAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.position == other.position
                and self.trafficdefinition == other.trafficdefinition
                and self.name == other.name
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TrafficSourceAction":
        """Parses the XML element of TrafficSourceAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A TrafficSourceAction element (same as generated by the
            class itself).

        Returns
        -------
        TrafficSourceAction
            A TrafficSourceAction object.
        """
        ta_element = find_mandatory_field(element, "TrafficAction")
        name = None
        if "trafficName" in ta_element.attrib:
            name = ta_element.attrib["trafficName"]
        tsa_element = find_mandatory_field(ta_element, "TrafficSourceAction")

        radius = convert_float(tsa_element.attrib["radius"])
        rate = convert_float(tsa_element.attrib["rate"])
        velocity = None
        if "velocity" in tsa_element.attrib:
            velocity = convert_float(tsa_element.attrib["velocity"])
        elif "speed" in tsa_element.attrib:
            velocity = tsa_element.attrib["speed"]
        position = _PositionFactory.parse_position(
            find_mandatory_field(tsa_element, "Position")
        )
        trafficdefinition = TrafficDefinition.parse(
            find_mandatory_field(tsa_element, "TrafficDefinition")
        )

        return TrafficSourceAction(
            rate, radius, position, trafficdefinition, velocity, name
        )

    def get_attributes(self) -> dict:
        """Retrieve the attributes of the TrafficSourceAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the TrafficSourceAction.
        """
        retdict = {}
        retdict["rate"] = str(self.rate)
        retdict["radius"] = str(self.radius)
        if self.velocity is not None:
            if self.version_minor < 2:
                retdict["velocity"] = str(self.velocity)
            else:
                retdict["speed"] = str(self.velocity)
        return retdict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the TrafficSourceAction."""
        element = ET.Element("GlobalAction")
        traffic_attrib = {}
        if self.name and not self.isVersion(minor=0):
            traffic_attrib = {"trafficName": self.name}

        trafficaction = ET.SubElement(
            element, "TrafficAction", attrib=traffic_attrib
        )
        sourceaction = ET.SubElement(
            trafficaction, "TrafficSourceAction", attrib=self.get_attributes()
        )
        sourceaction.append(self.position.get_element())
        sourceaction.append(self.trafficdefinition.get_element())

        return element


class TrafficSinkAction(_ActionType):
    """The TrafficSinkAction class creates a TrafficAction of the type
    TrafficSinkAction.

    Parameters
    ----------
    rate : float
        Rate of appearing traffic.
    radius : float
        The radius of the sink around the position.
    position : _PositionType
        Any Position to define the sink.
    trafficdefinition : TrafficDefinition
        Definition of the traffic.
    name : str, optional
        Name of the TrafficAction, can be used to stop the TrafficAction
        (valid from V1.1). Default is None.

    Attributes
    ----------
    rate : float
        Rate of appearing traffic.
    radius : float
        The radius of the sink around the position.
    position : _PositionType
        Any Position to define the sink.
    trafficdefinition : TrafficDefinition
        Definition of the traffic.
    name : str
        Name of the TrafficAction, can be used to stop the TrafficAction
        (valid from V1.1).

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an instance
        of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        radius: float,
        position: _PositionType,
        trafficdefinition: TrafficDefinition,
        rate: Optional[float] = None,
        name: Optional[str] = None,
    ):
        """Initialize the TrafficSinkAction.

        Parameters
        ----------
        rate : float
            Rate of appearing traffic.
        radius : float
            The radius of the source around the position.
        position : _PositionType
            Any Position to define the source.
        trafficdefinition : TrafficDefinition
            Definition of the traffic.
        name : str
            Name of the TrafficAction, can be used to stop the
            TrafficAction (valid from V1.1).
        """
        self.rate = convert_float(rate)
        self.radius = convert_float(radius)
        if not isinstance(position, _PositionType):
            raise TypeError("position input is not a valid Position")

        if not isinstance(trafficdefinition, TrafficDefinition):
            raise TypeError(
                "trafficdefinition input is not of type TrafficDefinition"
            )
        self.position = position
        self.trafficdefinition = trafficdefinition
        self.name = name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TrafficSinkAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.position == other.position
                and self.trafficdefinition == other.trafficdefinition
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TrafficSinkAction":
        """Parses the XML element of TrafficSinkAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A TrafficSinkAction element (same as generated by the class
            itself).

        Returns
        -------
        TrafficSinkAction
            A TrafficSinkAction object.
        """
        ta_element = find_mandatory_field(element, "TrafficAction")
        name = None
        if "trafficName" in ta_element.attrib:
            name = ta_element.attrib["trafficName"]

        tsa_element = find_mandatory_field(ta_element, "TrafficSinkAction")
        radius = convert_float(tsa_element.attrib["radius"])
        rate = None
        if "rate" in tsa_element.attrib:
            rate = convert_float(tsa_element.attrib["rate"])

        if tsa_element.find("TrafficDefinition") is not None:
            trafficdefinition = TrafficDefinition.parse(
                find_mandatory_field(tsa_element, "TrafficDefinition")
            )

        position = _PositionFactory.parse_position(
            find_mandatory_field(tsa_element, "Position")
        )

        return TrafficSinkAction(
            radius, position, trafficdefinition, rate, name
        )

    def get_attributes(self) -> dict:
        """Retrieve the attributes of the TrafficSinkAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the TrafficSinkAction.
        """
        retdict = {}

        retdict["rate"] = str(self.rate)
        retdict["radius"] = str(self.radius)
        return retdict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the TrafficSinkAction.

        Returns
        -------
        ET.Element
            The XML element representing the TrafficSinkAction.
        """

        element = ET.Element("GlobalAction")
        traffic_attrib = {}
        if self.name and not self.isVersion(minor=0):
            traffic_attrib = {"trafficName": self.name}
        trafficaction = ET.SubElement(
            element, "TrafficAction", attrib=traffic_attrib
        )
        sinkaction = ET.SubElement(
            trafficaction, "TrafficSinkAction", attrib=self.get_attributes()
        )
        sinkaction.append(self.position.get_element())
        sinkaction.append(self.trafficdefinition.get_element())

        return element


class TrafficSwarmAction(_ActionType):
    """The TrafficSwarmAction class creates a TrafficAction of the type
    TrafficSwarmAction.

    Parameters
    ----------
    semimajoraxis : float
        Half length of the major axis of the ellipse around the target.
    semiminoraxis : float
        Half length of the minor axis of the ellipse around the target.
    innerradius : float
        Radius of the inner circle.
    offset : float
        Longitudinal offset from the central entity.
    numberofvehicles : int
        Maximum number of vehicles around the entity.
    centralobject : str
        Entity to swarm around.
    trafficdefinition : TrafficDefinition
        Definition of the traffic.
    velocity : float or Range, optional
        Starting velocity (Range replaces velocity in OSC V1.2).
        Default is None.
    name : str, optional
        Name of the TrafficAction, can be used to stop the TrafficAction
        (valid from V1.1). Default is None.
    direction_of_travel : DirectionOfTravelDistribution, optional
        Adds the DirectionOfTravelDistribution to the action (valid from
        OSC V1.2). Default is None.

    Attributes
    ----------
    semimajoraxis : float
        Half length of the major axis of the ellipse around the target.
    semiminoraxis : float
        Half length of the minor axis of the ellipse around the target.
    innerradius : float
        Radius of the inner circle.
    offset : float
        Longitudinal offset from the central entity.
    numberofvehicles : int
        Maximum number of vehicles around the entity.
    centralobject : str
        Entity to swarm around.
    trafficdefinition : TrafficDefinition
        Definition of the traffic.
    velocity : float or Range, optional
        Starting velocity. Default is None.
    name : str, optional
        Name of the TrafficAction, can be used to stop the TrafficAction
        (valid from V1.1).
    direction_of_travel : DirectionOfTravelDistribution, optional
        Adds the DirectionOfTravelDistribution to the action (valid from
        OSC V1.2).

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        semimajoraxis: float,
        semiminoraxis: float,
        innerradius: float,
        offset: float,
        numberofvehicles: int,
        centralobject: str,
        trafficdefinition: TrafficDefinition,
        velocity: Optional[Union[float, Range]] = None,
        name: Optional[str] = None,
        direction_of_travel: Optional[DirectionOfTravelDistribution] = None,
    ):
        """Initialize the TrafficSwarmAction.

        Parameters
        ----------
        semimajoraxis : float
            Half length of the major axis of the ellipse around the target.
        semiminoraxis : float
            Half length of the minor axis of the ellipse around the target.
        innerradius : float
            Radius of the inner circle.
        offset : float
            Longitudinal offset from the central entity.
        numberofvehicles : int
            Maximum number of vehicles around the entity.
        centralobject : str
            Entity to swarm around.
        trafficdefinition : TrafficDefinition
            Definition of the traffic.
        velocity : float, optional
            Starting velocity. Default is None.
        name : str, optional
            Name of the TrafficAction, can be used to stop the TrafficAction
            (valid from V1.1). Default is None.
        direction_of_travel : DirectionOfTravelDistribution, optional
            Adds the DirectionOfTravelDistribution to the action (valid from
            OSC V1.2). Default is None.
        """
        self.semimajoraxis = convert_float(semimajoraxis)
        self.semiminoraxis = convert_float(semiminoraxis)
        self.innerradius = convert_float(innerradius)
        self.offset = convert_float(offset)
        self.numberofvehicles = convert_int(numberofvehicles)
        self.centralobject = centralobject
        if not isinstance(trafficdefinition, TrafficDefinition):
            raise TypeError(
                "trafficdefinition input is not of type TrafficDefinition"
            )
        self.trafficdefinition = trafficdefinition
        if velocity is not None:
            if isinstance(velocity, Range):
                self.velocity = velocity
            else:
                self.velocity = convert_float(velocity)
        else:
            self.velocity = None
        self.name = name
        if direction_of_travel is not None and not isinstance(
            direction_of_travel, DirectionOfTravelDistribution
        ):
            raise TypeError(
                "direction_of_travel is not of type DirectionOfTravelDistribution"
            )
        self.direction_of_travel = direction_of_travel

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TrafficSwarmAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.centralobject == other.centralobject
                and self.trafficdefinition == other.trafficdefinition
                and self.name == other.name
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TrafficSwarmAction":
        """Parse the XML element of TrafficSwarmAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A TrafficSwarmAction element (same as generated by the class
            itself).

        Returns
        -------
        TrafficSwarmAction
            A TrafficSwarmAction object.
        """
        ta_element = find_mandatory_field(element, "TrafficAction")
        name = None
        if "trafficName" in ta_element.attrib:
            name = ta_element.attrib["trafficName"]

        tsa_element = find_mandatory_field(ta_element, "TrafficSwarmAction")

        innerradius = convert_float(tsa_element.attrib["innerRadius"])
        numberofvehicles = convert_int(tsa_element.attrib["numberOfVehicles"])
        offset = convert_float(tsa_element.attrib["offset"])
        semimajoraxis = convert_float(tsa_element.attrib["semiMajorAxis"])
        semiminoraxis = convert_float(tsa_element.attrib["semiMinorAxis"])
        velocity = None
        if "velocity" in tsa_element.attrib:
            velocity = convert_float(tsa_element.attrib["velocity"])
        elif tsa_element.find("InitalSpeedRange") is not None:
            velocity = Range.parse(
                find_mandatory_field(tsa_element, "InitalSpeedRange")
            )

        trafficdefinition = TrafficDefinition.parse(
            find_mandatory_field(tsa_element, "TrafficDefinition")
        )
        dot = None
        if tsa_element.find("DirectionOfTravelDistribution") is not None:
            dot = DirectionOfTravelDistribution.parse(
                find_mandatory_field(
                    tsa_element, "DirectionOfTravelDistribution"
                )
            )
        central_element = find_mandatory_field(tsa_element, "CentralObject")
        centralobject = central_element.attrib["entityRef"]

        tsa_object = TrafficSwarmAction(
            semimajoraxis,
            semiminoraxis,
            innerradius,
            offset,
            numberofvehicles,
            centralobject,
            trafficdefinition,
            velocity,
            name,
            dot,
        )
        return tsa_object

    def get_attributes(self) -> dict:
        """Returns the attributes of the TrafficSwarmAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            TrafficSwarmAction.
        """
        retdict = {}
        retdict["semiMajorAxis"] = str(self.semimajoraxis)
        retdict["semiMinorAxis"] = str(self.semiminoraxis)
        retdict["innerRadius"] = str(self.innerradius)
        retdict["offset"] = str(self.offset)
        retdict["numberOfVehicles"] = str(self.numberofvehicles)
        if self.velocity is not None and not isinstance(self.velocity, Range):
            retdict["velocity"] = str(self.velocity)
        return retdict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the TrafficSwarmAction.

        Returns
        -------
        ET.Element
            The XML element representing the TrafficSwarmAction.
        """
        element = ET.Element("GlobalAction")
        traffic_attrib = {}
        if self.name and not self.isVersion(minor=0):
            traffic_attrib = {"trafficName": self.name}
        trafficaction = ET.SubElement(
            element, "TrafficAction", attrib=traffic_attrib
        )

        swarmaction = ET.SubElement(
            trafficaction, "TrafficSwarmAction", attrib=self.get_attributes()
        )
        swarmaction.append(self.trafficdefinition.get_element())
        ET.SubElement(
            swarmaction,
            "CentralObject",
            attrib={"entityRef": self.centralobject},
        )
        if self.velocity is not None:
            if self.version_minor > 1:
                if isinstance(self.velocity, Range):
                    swarmaction.append(
                        self.velocity.get_element("InitialSpeedRange")
                    )
                else:
                    raise OpenSCENARIOVersionError(
                        "Range for TrafficSwarmAction was introduced in "
                        "OSC V1.2, velocity should not be used anymore."
                    )

        if self.direction_of_travel is not None:
            if self.version_minor < 2:
                raise OpenSCENARIOVersionError(
                    "DirectionOfTravelDistribution was added in OSC V1.2"
                )
            swarmaction.append(self.direction_of_travel.get_element())

        return element


class TrafficStopAction(_ActionType):
    """The TrafficStopAction class creates a TrafficAction of the type
    TrafficStopAction.

    Parameters
    ----------
    name : str, optional
        Name of the Traffic to stop. Default is None.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, name: str = None):
        """Initialize the TrafficSwarmAction.

        Parameters
        ----------
        name : str, optional
            Name of the Traffic to stop. Default is None.
        """
        self.name = name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TrafficStopAction):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TrafficStopAction":
        """Parses the XML element of TrafficStopAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A TrafficStopAction element (same as generated by the class
            itself).

        Returns
        -------
        TrafficStopAction
            A TrafficStopAction object.
        """
        trafficaction_element = find_mandatory_field(element, "TrafficAction")
        name = trafficaction_element.attrib["trafficName"]
        return TrafficStopAction(name)

    def get_attributes(self) -> dict:
        """Returns the attributes of the TrafficStopAction as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the TrafficStopAction.
        """
        retdict = {}
        if self.name and not self.isVersion(minor=0):
            retdict["trafficName"] = str(self.name)
        elif self.isVersion(minor=0):
            raise OpenSCENARIOVersionError(
                "TrafficStopAction was introduced in OpenSCENARIO V1.1"
            )

        return retdict

    def get_element(self) -> ET.Element:
        """Generates an XML element tree representation of the
        TrafficStopAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The root XML element representing the GlobalAction
            with a nested TrafficAction and TrafficStopAction.
        """
        element = ET.Element("GlobalAction")
        trafficaction = ET.SubElement(
            element, "TrafficAction", attrib=self.get_attributes()
        )
        ET.SubElement(trafficaction, "TrafficStopAction")

        return element


class EnvironmentAction(_ActionType):
    """The EnvironmentAction class creates a GlobalAction of the type
    EnvironmentAction.

    Parameters
    ----------
    environment : Environment or CatalogReference
        The environment to change to.

    Attributes
    ----------
    environment : Environment or CatalogReference
        The environment to change to.

    Methods
    -------
    parse(element)
        Parses an ElementTree created by the class and returns an
        instance of the class itself.
    get_element()
        Returns the full ElementTree of the class.
    """

    def __init__(self, environment: Union[Environment, CatalogReference]):
        """Initialize the EnvironmentAction.

        Parameters
        ----------
        environment : Environment or CatalogReference
            The environment to change to.
        """
        if not isinstance(environment, (Environment, CatalogReference)):
            raise TypeError(
                "environment input not of type Environment or CatalogReference"
            )
        self.environment = environment

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EnvironmentAction):
            if self.environment == other.environment:
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "EnvironmentAction":
        """Parse the XML element of BoundingBox.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A orientation element (same as generated by the class itself).

        Returns
        -------
        BoundingBox
            A BoundingBox object.
        """
        action_element = find_mandatory_field(element, "EnvironmentAction")
        if action_element.find("Environment") is not None:
            environment = Environment.parse(
                find_mandatory_field(action_element, "Environment")
            )
        elif action_element.find("CatalogReference") is not None:
            environment = CatalogReference.parse(
                find_mandatory_field(action_element, "CatalogReference")
            )

        return EnvironmentAction(environment)

    def get_element(self) -> ET.Element:
        """Generate an XML element representing a global action.

        Returns
        -------
        xml.etree.ElementTree.Element
            The root XML element for the global action, containing an
            "EnvironmentAction" sub-element with the environment details.
        """

        element = ET.Element("GlobalAction")
        envaction = ET.SubElement(element, "EnvironmentAction")
        envaction.append(self.environment.get_element())

        return element


class CustomCommandAction(_ActionType):
    """The CustomCommandAction creates a simulator-defined action.

    Parameters
    ----------
    type : str
        Type of the custom command.
    content : str
        Content of the custom command.

    Methods
    -------
    parse(element : xml.etree.ElementTree.Element) -> CustomCommandAction
        Parses the XML element of a CustomCommandAction and returns an
        instance of the class.
    get_element() -> xml.etree.ElementTree.Element
        Returns the full ElementTree of the class.
    """

    def __init__(self, type: str, content: str):
        """Initialize the CustomCommandAction.

        Parameters
        ----------
        type : str
            Type of the custom command.
        content : str
            Content of the custom command.
        """
        self.type = type
        self.content = content

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CustomCommandAction):
            if other.type == self.type:
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "CustomCommandAction":
        """Parse the XML element of a CustomCommandAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A CustomCommandAction element.

        Returns
        -------
        CustomCommandAction
            A CustomCommandAction object.

        Raises
        ------
        NotAValidElement
            If the element is not a valid CustomCommandAction or is
            missing required attributes.
        """
        if element.tag != "CustomCommandAction":
            raise NotAValidElement(
                f'Expected "CustomCommandAction" element, received "{element.tag}".'
            )
        action_type = element.attrib.get("type", None)
        if action_type is None:
            raise NotAValidElement(
                'CustomCommandAction is missing required argument "type".'
            )

        return CustomCommandAction(action_type, element.text)

    def get_element(self) -> ET.Element:
        """Generate an ElementTree element for the CustomCommandAction.

        Returns
        -------
        ET.Element
            An XML element representing the CustomCommandAction.
        """
        element = ET.Element("CustomCommandAction", attrib={"type": self.type})
        element.text = self.content
        return element


class UserDefinedAction(_ActionType):
    """The UserDefinedAction enables adding simulator-specific
    CustomCommandActions.

    Methods
    -------
    add_custom_command_action(custom_command_action)
        Adds a CustomCommandAction to the UserDefinedAction.
    get_element()
        Returns the full ElementTree of the class.
    """

    def __init__(self, custom_command_action: CustomCommandAction):
        """Initialize the UserDefinedAction.

        Parameters
        ----------
        custom_command_action : CustomCommandAction
            The custom command action to be added.
        """
        self.custom_command_action = custom_command_action

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UserDefinedAction):
            if self.custom_command_action == other.custom_command_action:
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "UserDefinedAction":
        """Parses the XML element of a UserDefinedAction.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A UserDefinedAction element.

        Returns
        -------
        UserDefinedAction
            A UserDefinedAction object.
        """
        custom_command_action = CustomCommandAction.parse(
            find_mandatory_field(element, "CustomCommandAction")
        )
        user_defined_action = UserDefinedAction(custom_command_action)
        return user_defined_action

    def get_element(self) -> ET.Element:
        """Generate an ElementTree representation of the UserDefinedAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The root XML element representing the UserDefinedAction.
        """
        element = ET.Element("UserDefinedAction")
        element.append(self.custom_command_action.get_element())
        return element
