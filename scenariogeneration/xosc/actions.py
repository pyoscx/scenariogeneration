"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
from os import get_terminal_size
import xml.etree.ElementTree as ET

from numpy.lib.function_base import disp


from .utils import (
    DynamicsConstraints,
    TimeReference,
    TrafficSignalController,
    convert_bool,
    TransitionDynamics,
    CatalogReference,
    TrafficDefinition,
    Environment,
    AbsoluteSpeed,
    RelativeSpeedToMaster,
    convert_float,
    convert_int,
)
from .utils import Controller, _PositionType

from .enumerations import (
    CoordinateSystem,
    DynamicsShapes,
    LateralDisplacement,
    SpeedTargetValueType,
    FollowMode,
    ReferenceContext,
    VersionBase,
    LongitudinalDisplacement,
    DynamicsShapes,
)
from .exceptions import (
    NoActionsDefinedError,
    NotAValidElement,
    OpenSCENARIOVersionError,
    NotEnoughInputArguments,
    ToManyOptionalArguments,
)
from .position import _PositionFactory, Route, Trajectory


class _GlobalActionFactory:
    @staticmethod
    def parse_globalaction(element):
        if element.findall("EnvironmentAction"):
            return EnvironmentAction.parse(element)
        elif element.findall("EntityAction/AddEntityAction"):
            return AddEntityAction.parse(element)
        elif element.findall("EntityAction/DeleteEntityAction"):
            return DeleteEntityAction.parse(element)
        elif element.findall("ParameterAction/ModifyAction"):
            return ParameterAddAction.parse(element)
        elif element.findall("ParameterAction/SetAction"):
            return ParameterSetAction.parse(element)
        elif element.findall(
            "InfrastructureAction/TrafficSignalAction/TrafficSignalStateAction"
        ):
            return TrafficSignalStateAction.parse(element)
        elif element.findall(
            "InfrastructureAction/TrafficSignalAction/TrafficSignalControllerAction"
        ):
            return TrafficSignalControllerAction.parse(element)
        elif element.findall("TrafficAction/TrafficSourceAction"):
            return TrafficSourceAction.parse(element)
        elif element.findall("TrafficAction/TrafficSinkAction"):
            return TrafficSinkAction.parse(element)
        elif element.findall("TrafficAction/TrafficSwarmAction"):
            return TrafficSwarmAction.parse(element)
        elif element.findall("TrafficAction/TrafficStopAction"):
            return TrafficStopAction.parse(element)
        else:
            raise NotAValidElement("element ", element, "is not a valid GlobalAction")


class _PrivateActionFactory:
    @staticmethod
    def parse_privateaction(element):
        if element.findall(
            "LongitudinalAction/SpeedAction/SpeedActionTarget/AbsoluteTargetSpeed"
        ):
            return AbsoluteSpeedAction.parse(element)
        elif element.findall(
            "LongitudinalAction/SpeedAction/SpeedActionTarget/RelativeTargetSpeed"
        ):
            return RelativeSpeedAction.parse(element)
        elif element.findall("LongitudinalAction/LongitudinalDistanceAction"):
            return LongitudinalDistanceAction.parse(element)
        elif element.findall(
            "LateralAction/LaneChangeAction/LaneChangeTarget/AbsoluteTargetLane"
        ):
            return AbsoluteLaneChangeAction.parse(element)
        elif element.findall(
            "LateralAction/LaneChangeAction/LaneChangeTarget/RelativeTargetLane"
        ):
            return RelativeLaneChangeAction.parse(element)
        elif element.findall(
            "LateralAction/LaneOffsetAction/LaneOffsetTarget/AbsoluteTargetLaneOffset"
        ):
            return AbsoluteLaneOffsetAction.parse(element)
        elif element.findall(
            "LateralAction/LaneOffsetAction/LaneOffsetTarget/RelativeTargetLaneOffset"
        ):
            return RelativeLaneOffsetAction.parse(element)
        elif element.findall("LateralAction/LateralDistanceAction"):
            return LateralDistanceAction.parse(element)
        elif element.findall("VisibilityAction"):
            return VisibilityAction.parse(element)
        elif element.findall("SynchronizeAction"):
            return SynchronizeAction.parse(element)
        elif element.findall("ActivateControllerAction"):
            return ActivateControllerAction.parse(element)
        elif element.findall("ControllerAction"):
            return ControllerAction.parse(element)
        elif element.findall("TeleportAction"):
            return TeleportAction.parse(element)
        elif element.findall("RoutingAction/AssignRouteAction"):
            return AssignRouteAction.parse(element)
        elif element.findall("RoutingAction/FollowTrajectoryAction"):
            return FollowTrajectoryAction.parse(element)
        elif element.findall("RoutingAction/AcquirePositionAction"):
            return AcquirePositionAction.parse(element)
        else:
            raise NotAValidElement("element ", element, "is not a valid PrivateAction")


class _ActionType(VersionBase):
    """helper class for typesetting"""

    pass


class _PrivateActionType(_ActionType):
    """helper class for typesetting"""

    pass


class _Action(VersionBase):
    """Private class used to define an action, should not be used by the user.
    Used as a wrapper to create the extra elements needed

    Parameters
    ----------
        name (str): name of the action

        action (*Action): any action

    Attributes
    ----------
        name (str): name of the action

        action (*Action): any action

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

    """

    def __init__(self, name, action):
        """initalize _Action

        Parameters
        ----------
            name (str): name of the action

            action (*Action): any action

        """
        self.name = name

        self.action = action

    def __eq__(self, other):
        if isinstance(other, _Action):
            if (
                self.get_attributes() == other.get_attributes()
                and self.action == other.action
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of _Action

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A _Action element (same as generated by the class itself)

        Returns
        -------
            action (_Action): a _Action object

        """
        name = element.attrib["name"]
        if element.find("PrivateAction") is not None:
            action = _PrivateActionFactory.parse_privateaction(
                element.find("PrivateAction")
            )
        elif element.find("GlobalAction") is not None:
            action = _GlobalActionFactory.parse_globalaction(
                element.find("GlobalAction")
            )
        elif element.find("UserDefinedAction") is not None:
            action = UserDefinedAction.parse(element)
        else:
            raise NotAValidElement(element.tag, "is not a valid action")
        return _Action(name, action)

    def get_attributes(self):
        """returns the attributes of the _Action as a dict"""
        return {"name": self.name}

    def get_element(self):
        """returns the elementTree of the _Action"""
        element = ET.Element("Action", attrib=self.get_attributes())
        element.append(self.action.get_element())
        return element


#### Private Actions ####

# LongitudinalAction


class AbsoluteSpeedAction(_PrivateActionType):
    """The AbsoluteSpeedAction class specifies a LongitudinalAction of type SpeedAction with an abosulte target speed

    Parameters
    ----------
        speed (float): the speed wanted

        transition_dynamics (TransitionDynamics): how the change should be made

    Attributes
    ----------

        speed (float): the speed wanted

        transition_dynamics (TransitionDynamics): how the change should be made

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, speed: float, transition_dynamics):
        """initalize the AbsoluteSpeedAction

        Parameters
        ----------
            speed (float): the speed wanted

            transition_dynamics (TransitionDynamics): how the change should be made

        """
        self.speed = convert_float(speed)
        if not isinstance(transition_dynamics, TransitionDynamics):
            raise TypeError("transition_dynamics input not of type TransitionDynamics")
        self.transition_dynamics = transition_dynamics

    def __eq__(self, other):
        if isinstance(other, AbsoluteSpeedAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.transition_dynamics == other.transition_dynamics
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of WorldPosition

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A position element (same as generated by the class itself)

        Returns
        -------
            position (WorldPosition): a world position object

        """
        speed_element = element.find(
            "LongitudinalAction/SpeedAction/SpeedActionTarget/AbsoluteTargetSpeed"
        )
        td_element = element.find("LongitudinalAction/SpeedAction/SpeedActionDynamics")
        speed = speed_element.attrib["value"]
        transition_dynamics = TransitionDynamics.parse(td_element)
        return AbsoluteSpeedAction(speed, transition_dynamics)

    def get_attributes(self):
        """returns the attributes of the AbsoluteSpeedAction as a dict"""
        return {"value": str(self.speed)}

    def get_element(self):
        """returns the elementTree of the AbsoluteSpeedAction"""
        element = ET.Element("PrivateAction")
        longaction = ET.SubElement(element, "LongitudinalAction")
        speedaction = ET.SubElement(longaction, "SpeedAction")

        speedaction.append(self.transition_dynamics.get_element("SpeedActionDynamics"))
        speedactiontarget = ET.SubElement(speedaction, "SpeedActionTarget")

        ET.SubElement(speedactiontarget, "AbsoluteTargetSpeed", self.get_attributes())

        return element


class RelativeSpeedAction(_PrivateActionType):
    """The RelativeSpeedAction creates a LongitudinalAction of type SpeedAction with a relative target

    Parameters
    ----------
        speed (float): the speed wanted

        target (str): the name of the relative target (used for relative speed)

        transition_dynamics (TransitionDynamics): how the change should be made

        valuetype (str): the type of relative speed wanted (used for relative speed)

        continuous (bool): if the controller tries to keep the relative speed

    Attributes
    ----------
        speed (float): the speed wanted

        target (str): the name of the relative target (used for relative speed)

        valuetype (str): the type of relative speed wanted (used for relative speed)

        continuous (bool): if the controller tries to keep the relative speed

        transition_dynamics (TransitionDynamics): how the change should be made

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

    """

    def __init__(
        self,
        speed,
        entity,
        transition_dynamics,
        valuetype=SpeedTargetValueType.delta,
        continuous=True,
    ):
        """initalizes RelativeSpeedAction

        Parameters
        ----------
            speed (float): the speed wanted

            target (str): the name of the relative target

            transition_dynamics (TransitionDynamics): how the change should be made

            valuetype (SpeedTargetValueType): the type of relative speed wanted

            continuous (bool): if the controller tries to keep the relative speed

        """
        self.speed = convert_float(speed)
        self.target = entity
        if not hasattr(SpeedTargetValueType, str(valuetype)):
            raise TypeError("valuetype input not of type SpeedTargetValueType")
        self.valuetype = valuetype
        if not isinstance(continuous, bool):
            raise TypeError("continuous input not of type bool")

        if not isinstance(transition_dynamics, TransitionDynamics):
            raise TypeError("transition_dynamics input not of type TransitionDynamics")
        self.transition_dynamics = transition_dynamics
        self.continuous = continuous

    def __eq__(self, other):
        if isinstance(other, RelativeSpeedAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.transition_dynamics == other.transition_dynamics
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of RelativeSpeedAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A position element (same as generated by the class itself)

        Returns
        -------
            action (RelativeSpeedAction): the RelativeSpeedAction

        """
        speed_element = element.find(
            "LongitudinalAction/SpeedAction/SpeedActionTarget/RelativeTargetSpeed"
        )
        td_element = element.find("LongitudinalAction/SpeedAction/SpeedActionDynamics")
        speed = speed_element.attrib["value"]
        entity = speed_element.attrib["entityRef"]
        continuous = bool(speed_element.attrib["continuous"])
        valuetype = getattr(
            SpeedTargetValueType, speed_element.attrib["speedTargetValueType"]
        )
        transition_dynamics = TransitionDynamics.parse(td_element)
        return RelativeSpeedAction(
            speed, entity, transition_dynamics, valuetype, continuous
        )

    def get_attributes(self):
        """returns the attributes of the RelativeSpeedAction as a dict"""
        return {
            "entityRef": self.target,
            "value": str(self.speed),
            "speedTargetValueType": self.valuetype.get_name(),
            "continuous": convert_bool(self.continuous),
        }

    def get_element(self):
        """returns the elementTree of the RelativeSpeedAction"""
        element = ET.Element("PrivateAction")
        longaction = ET.SubElement(element, "LongitudinalAction")
        speedaction = ET.SubElement(longaction, "SpeedAction")
        speedaction.append(self.transition_dynamics.get_element("SpeedActionDynamics"))
        speedactiontarget = ET.SubElement(speedaction, "SpeedActionTarget")

        ET.SubElement(speedactiontarget, "RelativeTargetSpeed", self.get_attributes())

        return element


class LongitudinalDistanceAction(_PrivateActionType):
    """The LongitudinalAction creates a LongitudinalAction of type LongitudinalAction with a distance target

    Parameters
    ----------
        distance (float): distance to the entity

        entity (str): the target name

        freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
            Default: True

        continuous (bool): if the controller tries to keep the relative speed
            Default: True

        max_acceleration (float): maximum acceleration allowed
            Default: None

        max_deceleration (float): maximum deceleration allowed
            Default: None

        max_speed (float): maximum speed allowed
            Default: None

        coordinate_system (CoordinateSystem): the coordinate system for the distance calculation
            Default CoordinateSystem.entity

        displacement (LongitudinalDisplacement): type of displacement wanted
            Default LongitudinalDisplacement.any

    Attributes
    ----------
        entity (str): the target name

        freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

        continuous (bool): if the controller tries to keep the relative speed

        distance (float): the distance to the entity

        dynamic_constraint (DynamicsConstraints): Dynamics constraints of the action

        coordinate_system (CoordinateSystem): the coordinate system for the distance calculation

        displacement (LongitudinalDisplacement): type of displacement wanted

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

    """

    def __init__(
        self,
        entity,
        freespace=True,
        continuous=True,
        max_acceleration=None,
        max_deceleration=None,
        max_speed=None,
        distance=None,
        timeGap=None,
        coordinate_system=CoordinateSystem.entity,
        displacement=LongitudinalDisplacement.any,
    ):
        """initalize the LongitudinalDistanceAction

        Parameters
        ----------
            distance (float): distance to the entity

            timegap (float): time to the target

            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continuous (bool): if the controller tries to keep the relative speed
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None

            coordinate_system (CoordinateSystem): the coordinate system for the distance calculation
                Default CoordinateSystem.entity

            displacement (LongitudinalDisplacement): type of displacement wanted
                Default LongitudinalDisplacement.any
        """
        self.target = entity
        if not isinstance(continuous, bool):
            raise TypeError("continuous input not of type bool")

        if not isinstance(freespace, bool):
            raise TypeError("freespace input not of type bool")

        self.freespace = convert_bool(freespace)
        self.continuous = convert_bool(continuous)
        self.dynamic_constraint = DynamicsConstraints(
            max_acceleration, max_deceleration, max_speed
        )

        if distance is not None and timeGap is not None:
            raise ToManyOptionalArguments(
                "Not both of distance and timeGap can be used."
            )
        if distance is None and timeGap is None:
            raise NotEnoughInputArguments("Either ds or dsLane is needed as input.")
        self.distance = convert_float(distance)
        self.timeGap = convert_float(timeGap)

        if not hasattr(CoordinateSystem, str(coordinate_system)):
            raise ValueError(coordinate_system + "; is not a valid CoordinateSystem.")
        if not hasattr(LongitudinalDisplacement, str(displacement)):
            raise ValueError(
                displacement + "; is not a valid LongitudinalDisplacement."
            )
        self.coordinate_system = coordinate_system
        self.displacement = displacement

    def __eq__(self, other):
        if isinstance(other, LongitudinalDistanceAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.dynamic_constraint == other.dynamic_constraint
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of LongitudinalAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A LongitudinalDistanceAction element (same as generated by the class itself)

        Returns
        -------
            ld_action (LongitudinalDistanceAction): a LongitudinalDistanceAction object

        """
        lda_element = element.find("LongitudinalAction/LongitudinalDistanceAction")
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
            coordinate_system = getattr(
                CoordinateSystem, lda_element.attrib["coordinateSystem"]
            )
        displacement = LongitudinalDisplacement.any
        if "displacement" in lda_element.attrib:
            displcement = getattr(
                LongitudinalDisplacement, lda_element.attrib["displacement"]
            )
        max_acceleration = None
        max_deceleration = None
        max_speed = None
        constraints = None
        if lda_element.find("DynamicConstraints") != None:
            constraints = DynamicsConstraints.parse(
                lda_element.find("DynamicConstraints")
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

    def get_attributes(self):
        """returns the attributes of the LongitudinalDistanceAction as a dict"""
        retdict = {}
        retdict["entityRef"] = self.target
        retdict["freespace"] = str(self.freespace)
        retdict["continuous"] = str(self.continuous)
        if self.distance != None:
            retdict["distance"] = str(self.distance)
        if self.timeGap != None:
            retdict["timeGap"] = str(self.timeGap)
        if not self.isVersion(minor=0):
            retdict["coordinateSystem"] = self.coordinate_system.get_name()
            retdict["displacement"] = self.displacement.get_name()
        return retdict

    def get_element(self):
        """returns the elementTree of the LongitudinalDistanceAction"""
        element = ET.Element("PrivateAction")
        longact = ET.SubElement(element, "LongitudinalAction")

        longdistaction = ET.SubElement(
            longact, "LongitudinalDistanceAction", attrib=self.get_attributes()
        )
        if self.dynamic_constraint.is_filled():
            longdistaction.append(self.dynamic_constraint.get_element())
        return element


class AbsoluteLaneChangeAction(_PrivateActionType):
    """the AbsoluteLaneChangeAction creates a LateralAction of type LaneChangeAction with an absolute target

    Parameters
    ----------
        lane (int): lane to change to

        transition_dynamics (TransitionDynamics): how the change should be made

        target_lane_offset (float): if a offset in the target lane is wanted
            Default: None

    Attributes
    ----------
        lane (int): lane to change to

        target_lane_offset (float): offset in the target lane is wanted

        transition_dynamics (TransitionDynamics): how the change should be made

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

    """

    def __init__(self, lane, transition_dynamics, target_lane_offset=None):
        """initalize AbsoluteLaneChangeAction

        Parameters
        ----------
            lane (int): lane to change to

            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        """

        self.lane = convert_int(lane)
        self.target_lane_offset = convert_float(target_lane_offset)
        if not isinstance(transition_dynamics, TransitionDynamics):
            raise TypeError("transition_dynamics input not of type TransitionDynamics")
        self.transition_dynamics = transition_dynamics

    def __eq__(self, other):
        if isinstance(other, AbsoluteLaneChangeAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.transition_dynamics == other.transition_dynamics
                and self.target_lane_offset == other.target_lane_offset
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of AbsoluteLaneChangeAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A AbsoluteLaneChangeAction element (same as generated by the class itself)

        Returns
        -------
            alc_action (AbsoluteLaneChangeAction): a AbsoluteLaneChangeAction object

        """
        lca_element = element.find("LateralAction/LaneChangeAction")
        target_lane_offset = None
        if "targetLaneOffset" in lca_element.attrib:
            target_lane_offset = convert_float(lca_element.attrib["targetLaneOffset"])
        dynamics = TransitionDynamics.parse(
            lca_element.find("LaneChangeActionDynamics")
        )
        targetlane_element = lca_element.find("LaneChangeTarget/AbsoluteTargetLane")
        lane = convert_int(targetlane_element.attrib["value"])

        return AbsoluteLaneChangeAction(lane, dynamics, target_lane_offset)

    def get_attributes(self):
        """returns the attributes of the AbsoluteLaneChangeAction as a dict"""
        retdict = {}
        retdict["value"] = str(self.lane)
        return retdict

    def get_element(self):
        """returns the elementTree of the AbsoluteLaneChangeAction"""
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

        ET.SubElement(lanchangetarget, "AbsoluteTargetLane", self.get_attributes())
        return element


class RelativeLaneChangeAction(_PrivateActionType):
    """the RelativeLaneChangeAction creates a LateralAction of type LaneChangeAction with a relative target

    Parameters
    ----------
        lane (int): relative lane number

        entity (str): the entity to run relative to

        transition_dynamics (TransitionDynamics): how the change should be made

        target_lane_offset (float): if a offset in the target lane is wanted
            Default: None

    Attributes
    ----------
        value (int): lane to change to

        target (str): target for relative lane change

        target_lane_offset (float): offset in the target lane is wanted

        transition_dynamics (TransitionDynamics): how the change should be made

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

    """

    def __init__(self, lane, entity, transition_dynamics, target_lane_offset=None):
        """initalize RelativeLaneChangeAction

        Parameters
        ----------
            lane (int): relative lane number

            entity (str): the entity to run relative to

            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        """

        self.lane = convert_int(lane)
        self.target = entity
        self.target_lane_offset = convert_float(target_lane_offset)
        if not isinstance(transition_dynamics, TransitionDynamics):
            raise TypeError("transition_dynamics input not of type TransitionDynamics")
        self.transition_dynamics = transition_dynamics

    def __eq__(self, other):
        if isinstance(other, RelativeLaneChangeAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.transition_dynamics == other.transition_dynamics
                and self.target_lane_offset == other.target_lane_offset
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of AbsoluteLaneChangeAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A AbsoluteLaneChangeAction element (same as generated by the class itself)

        Returns
        -------
            alc_action (AbsoluteLaneChangeAction): a AbsoluteLaneChangeAction object

        """
        lca_element = element.find("LateralAction/LaneChangeAction")
        target_lane_offset = None
        if "targetLaneOffset" in lca_element.attrib:
            target_lane_offset = convert_float(lca_element.attrib["targetLaneOffset"])
        dynamics = TransitionDynamics.parse(
            lca_element.find("LaneChangeActionDynamics")
        )
        targetlane_element = lca_element.find("LaneChangeTarget/RelativeTargetLane")
        lane = convert_int(targetlane_element.attrib["value"])
        target = targetlane_element.attrib["entityRef"]

        return RelativeLaneChangeAction(lane, target, dynamics, target_lane_offset)

    def get_attributes(self):
        """returns the attributes of the RelativeLaneChangeAction as a dict"""
        retdict = {}
        retdict["value"] = str(self.lane)
        retdict["entityRef"] = self.target
        return retdict

    def get_element(self):
        """returns the elementTree of the RelativeLaneChangeAction"""
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

        ET.SubElement(lanchangetarget, "RelativeTargetLane", self.get_attributes())
        return element


class AbsoluteLaneOffsetAction(_PrivateActionType):
    """the AbsoluteLaneOffsetAction class creates a LateralAction of type LaneOffsetAction with an absolute target

    Parameters
    ----------
        value (float): lateral offset of the lane

        shape (DynamicsShapes): shape of the offset action

        maxlatacc (float): maximum allowed lateral acceleration

        continuous (bool): if the controller tries to keep the relative speed
            Default: True

    Attributes
    ----------
        continuous (bool): if the controller tries to keep the relative speed

        value (float): lateral offset of the lane

        target (str): the name of the entity (relative only)

        dynshape (DynamicsShapes): the shape of the action

        maxlatacc (float): maximum allowed lateral acceleration

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

    """

    def __init__(self, value, shape, maxlatacc=None, continuous=True):
        """initalizes the AbsoluteLaneOffsetAction
        Parameters
        ----------
            value (float): lateral offset of the lane

            shape (DynamicsShapes): shape of the offset action

            maxlatacc (float): maximum allowed lateral acceleration

            continuous (bool): if the controller tries to keep the relative speed
                Default: True
        """
        if not isinstance(continuous, bool):
            raise TypeError("continuous input not of type bool")

        self.continuous = continuous
        self.value = value
        if not hasattr(DynamicsShapes, str(shape)):
            raise ValueError(shape + "; is not a valid shape.")
        self.dynshape = shape
        self.maxlatacc = maxlatacc

    def __eq__(self, other):
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
    def parse(element):
        """Parses the xml element of AbsoluteLaneOffsetAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A AbsoluteLaneOffsetAction element (same as generated by the class itself)

        Returns
        -------
            alco_action (AbsoluteLaneOffsetAction): a AbsoluteLaneOffsetAction object

        """
        loa_element = element.find("LateralAction/LaneOffsetAction")

        contiuous = convert_bool(loa_element.attrib["continuous"])
        load_element = loa_element.find("LaneOffsetActionDynamics")
        maxacc = convert_float(load_element.attrib["maxLateralAcc"])
        dynamics = getattr(DynamicsShapes, load_element.attrib["dynamicsShape"])

        atlo_element = loa_element.find("LaneOffsetTarget/AbsoluteTargetLaneOffset")
        value = atlo_element.attrib["value"]

        return AbsoluteLaneOffsetAction(value, dynamics, maxacc, contiuous)

    def get_attributes(self):
        """returns the attributes of the AbsoluteLaneOffsetAction as a dict"""
        retdict = {}
        retdict["value"] = str(self.value)
        return retdict

    def get_element(self):
        """returns the elementTree of the AbsoluteLaneOffsetAction"""
        element = ET.Element("PrivateAction")
        lataction = ET.SubElement(element, "LateralAction")
        laneoffsetaction = ET.SubElement(
            lataction,
            "LaneOffsetAction",
            attrib={"continuous": convert_bool(self.continuous)},
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
        ET.SubElement(laneoftarget, "AbsoluteTargetLaneOffset", self.get_attributes())

        return element


class RelativeLaneOffsetAction(_PrivateActionType):
    """the RelativeLaneOffsetAction class creates a LateralAction of type LaneOffsetAction with a relative target

    Parameters
    ----------
        value (float): relative lateral offset of the target

        entity (str): name of the entity

        shape (str): shape of the offset action

        maxlatacc (float): maximum allowed lateral acceleration

        continuous (bool): if the controller tries to keep the relative speed
            Default: True

    Attributes
    ----------
        continuous (bool): if the controller tries to keep the relative speed

        value (float): relative lateral offset of the arget

        target (str): the name of the entity

        dynshape (str): the shape of the action

        maxlatacc (float): maximum allowed lateral acceleration

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

    """

    def __init__(self, value, entity, shape, maxlatacc, continuous=True):
        """initalizes the RelativeLaneOffsetAction,

        Parameters
        ----------
            value (float): relative lateral offset of the target

            entity (str): name of the entity

            shape (str): shape of the offset action

            maxlatacc (float): maximum allowed lateral acceleration

            continuous (bool): if the controller tries to keep the relative speed
                Default: True
        """
        if not isinstance(continuous, bool):
            raise TypeError("continuous input not of type bool")

        self.continuous = continuous
        self.value = value
        self.target = entity
        if not hasattr(DynamicsShapes, str(shape)):
            raise ValueError(shape + "; is not a valid shape.")
        self.dynshape = shape
        self.maxlatacc = maxlatacc

    def __eq__(self, other):
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
    def parse(element):
        """Parses the xml element of AbsoluteLaneOffsetAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A AbsoluteLaneOffsetAction element (same as generated by the class itself)

        Returns
        -------
            alco_action (AbsoluteLaneOffsetAction): a AbsoluteLaneOffsetAction object

        """
        loa_element = element.find("LateralAction/LaneOffsetAction")

        contiuous = convert_bool(loa_element.attrib["continuous"])
        load_element = loa_element.find("LaneOffsetActionDynamics")
        maxacc = convert_float(load_element.attrib["maxLateralAcc"])
        dynamics = getattr(DynamicsShapes, load_element.attrib["dynamicsShape"])

        rtlo_element = loa_element.find("LaneOffsetTarget/RelativeTargetLaneOffset")
        value = rtlo_element.attrib["value"]
        entity = rtlo_element.attrib["entityRef"]

        return RelativeLaneOffsetAction(value, entity, dynamics, maxacc, contiuous)

    def get_attributes(self):
        """returns the attributes of the RelativeLaneOffsetAction as a dict"""
        retdict = {}
        retdict["value"] = str(self.value)
        retdict["entityRef"] = self.target
        return retdict

    def get_element(self):
        """returns the elementTree of the RelativeLaneOffsetAction"""
        element = ET.Element("PrivateAction")
        lataction = ET.SubElement(element, "LateralAction")
        laneoffsetaction = ET.SubElement(
            lataction,
            "LaneOffsetAction",
            attrib={"continuous": convert_bool(self.continuous)},
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
            laneoftarget, "RelativeTargetLaneOffset", attrib=self.get_attributes()
        )

        return element


class LateralDistanceAction(_PrivateActionType):
    """

    Parameters
    ----------
        entity (str): the target name

        distance (float): the lateral distance to the entity

        freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
            Default: True

        continuous (bool): if the controller tries to keep the relative speed
            Default: True

        max_acceleration (float): maximum acceleration allowed
            Default: None

        max_deceleration (float): maximum deceleration allowed
            Default: None

        max_speed (float): maximum speed allowed
            Default: None

        coordinate_system (CoordinateSystem): the coordinate system for the distance calculation
            Default CoordinateSystem.entity

        displacement (LateralDisplacement): type of displacement wanted
            Default LateralDisplacement.any
    Attributes
    ----------
        entity (str): the target name

        distance (float): the lateral distance to the entity

        freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

        continuous (bool): if the controller tries to keep the relative speed

        distance (float): if the distance metric is used

        timegap (float): if timegap metric is used

        dynamic_constraint (DynamicsConstraints): Dynamics constraints of the action

        coordinate_system (CoordinateSystem): the coordinate system for the distance calculation

        displacement (LateralDisplacement): type of displacement wanted

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

    """

    def __init__(
        self,
        entity,
        distance=None,
        freespace=True,
        continuous=True,
        max_acceleration=None,
        max_deceleration=None,
        max_speed=None,
        coordinate_system=CoordinateSystem.entity,
        displacement=LateralDisplacement.any,
    ):
        """initalizes the LateralDistanceAction

        Parameters
        ----------
            entity (str): the target name

            distance (float): the lateral distance to the entity

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continuous (bool): if the controller tries to keep the relative speed
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None

            coordinate_system (CoordinateSystem): the coordinate system for the distance calculation
                Default CoordinateSystem.entity

            displacement (LateralDisplacement): type of displacement wanted
                Default LateralDisplacement.any
        """
        self.distance = distance
        self.target = entity
        if not isinstance(continuous, bool):
            raise TypeError("continuous input not of type bool")

        if not isinstance(freespace, bool):
            raise TypeError("freespace input not of type bool")

        self.freespace = freespace
        self.continuous = continuous
        self.dynamic_constraint = DynamicsConstraints(
            max_acceleration, max_deceleration, max_speed
        )
        if not hasattr(CoordinateSystem, str(coordinate_system)):
            raise ValueError(coordinate_system + "; is not a valid CoordinateSystem.")
        if not hasattr(LateralDisplacement, str(displacement)):
            raise ValueError(displacement + "; is not a valid LateralDisplacement.")
        self.coordinate_system = coordinate_system
        self.displacement = displacement

    def __eq__(self, other):
        if isinstance(other, LateralDistanceAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.dynamic_constraint == other.dynamic_constraint
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of LateralDistanceAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A LateralDistanceAction element (same as generated by the class itself)

        Returns
        -------
            ld_action (LateralDistanceAction): a LateralDistanceActionobject

        """
        lda_element = element.find("LateralAction/LateralDistanceAction")
        continuous = convert_bool(lda_element.attrib["continuous"])
        freespace = convert_bool(lda_element.attrib["freespace"])
        entity = lda_element.attrib["entityRef"]
        distance = None
        if "distance" in lda_element.attrib:
            distance = lda_element.attrib["distance"]
        coordinate = None
        if "coordinateSystem" in lda_element.attrib:
            coordinate = getattr(
                CoordinateSystem, lda_element.attrib["coordinateSystem"]
            )
        displacement = None
        if "displacement" in lda_element.attrib:
            displacement = getattr(
                LateralDisplacement, lda_element.attrib["displacement"]
            )
        constraints = None
        max_acc = None
        max_dec = None
        max_speed = None
        if lda_element.find("DynamicConstraints") != None:
            constraints = DynamicsConstraints.parse(
                lda_element.find("DynamicConstraints")
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

    def get_attributes(self):
        """returns the attributes of the LateralDistanceAction as a dict"""
        retdict = {}
        retdict["entityRef"] = self.target
        retdict["freespace"] = convert_bool(self.freespace)
        retdict["continuous"] = convert_bool(self.continuous)
        if self.distance != None:
            retdict["distance"] = str(self.distance)
        if not self.isVersion(minor=0):
            retdict["coordinateSystem"] = self.coordinate_system.get_name()
            retdict["displacement"] = self.displacement.get_name()
        return retdict

    def get_element(self):
        """returns the elementTree of the LateralDistanceAction"""
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
    """the TeleportAction creates the Teleport action of OpenScenario

    Parameters
    ----------
        position (*Position): any position object

    Attributes
    ----------
        position (*Position): any position object


    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

    """

    def __init__(self, position):
        """initalizes the TeleportAction

        Parameters
        ----------
            position (*Position): any position object

        """
        if not isinstance(position, _PositionType):
            raise TypeError("position input not a valid Position type")

        self.position = position

    def __eq__(self, other):
        if isinstance(other, TeleportAction):
            if self.position == other.position:
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of WorldPosition

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A position element (same as generated by the class itself)

        Returns
        -------
            position (WorldPosition): a world position object

        """
        position_element = element.find("TeleportAction/Position")

        position = _PositionFactory.parse_position(position_element)
        return TeleportAction(position)

    def get_element(self):
        """returns the elementTree of the TeleportAction"""
        element = ET.Element("PrivateAction")
        telact = ET.SubElement(element, "TeleportAction")
        telact.append(self.position.get_element())
        return element


# Routing actions


class AssignRouteAction(_PrivateActionType):
    """AssignRouteAction creates a RouteAction of type AssignRouteAction

    Parameters
    ----------
        route (Route, or CatalogReference): the route to follow

    Attributes
    ----------
        route (Route, or CatalogReference): the route to follow


    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

    """

    def __init__(self, route):
        """initalizes the AssignRouteAction

        Parameters
        ----------
            route (Route, or CatalogReference): the route to follow

        """
        if not (isinstance(route, Route) or isinstance(route, CatalogReference)):
            raise TypeError("route input not of type Route or CatalogReference")

        self.route = route

    def __eq__(self, other):
        if isinstance(other, AssignRouteAction):
            if self.route == other.route:
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of AssignRouteAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A AssignRouteAction element (same as generated by the class itself)

        Returns
        -------
            ar_action (AssignRouteAction): a AssignRouteAction object

        """
        ara_element = element.find("RoutingAction/AssignRouteAction")
        route = None
        if ara_element.find("Route") != None:
            route = Route.parse(ara_element.find("Route"))
        elif ara_element.find("CatalogReference") != None:
            route = CatalogReference.parse(ara_element.find("CatalogReference"))

        return AssignRouteAction(route)

    def get_element(self):
        """returns the elementTree of the AssignRouteAction"""
        element = ET.Element("PrivateAction")
        routeaction = ET.SubElement(element, "RoutingAction")
        assignrouteaction = ET.SubElement(routeaction, "AssignRouteAction")
        assignrouteaction.append(self.route.get_element())

        return element


class AcquirePositionAction(_PrivateActionType):
    """AcquirePositionAction creates a RouteAction of type AcquirePositionAction

    Parameters
    ----------
        position (*Position): target position

    Attributes
    ----------
        position (*Position): target position

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

    """

    def __init__(self, position):
        """initalizes the AcquirePositionAction

        Parameters
        ----------
            position (*Position): target position

        """
        if not isinstance(position, _PositionType):
            raise TypeError("position input not a valid Position type")

        self.position = position

    def __eq__(self, other):
        if isinstance(other, AcquirePositionAction):
            if self.position == other.position:
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of AcquirePositionAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A AcquirePositionAction element (same as generated by the class itself)

        Returns
        -------
            ap_action (AcquirePositionAction): a AcquirePositionAction object

        """
        pos_element = element.find("RoutingAction/AcquirePositionAction/Position")

        position = _PositionFactory.parse_position(pos_element)

        return AcquirePositionAction(position)

    def get_element(self):
        """returns the elementTree of the AcquirePositionAction"""
        element = ET.Element("PrivateAction")
        routeaction = ET.SubElement(element, "RoutingAction")
        posaction = ET.SubElement(routeaction, "AcquirePositionAction")
        posaction.append(self.position.get_element())

        return element


class FollowTrajectoryAction(_PrivateActionType):
    """FollowTrajectoryAction creates a RouteAction of type FollowTrajectoryAction

    Parameters
    ----------
        trajectory (Trajectory, or CatalogReference): the trajectory to follow

        following_mode (FollowMode): the following mode of the action

        reference_domain (ReferenceContext): how to follow
            Default: None
        scale (float): scalefactor of the timeings (must be combined with reference_domain and offset)
            Default: None
        offset (float): offset for time values (must be combined with reference_domain and scale)
            Default: None
        initialDistanceOffset (float): start at this offset into the trajectory (v1.1)
            Default: None

    Attributes
    ----------
        trajectory (Trajectory, or CatalogReference): the trajectory to follow

        following_mode (str): the following mode of the action

        timeref (TimeReference): the time reference of the trajectory

        initialDistanceOffset (float): start at this offset into the trajectory (v1.1)

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

    """

    def __init__(
        self,
        trajectory,
        following_mode,
        reference_domain=None,
        scale=None,
        offset=None,
        initialDistanceOffset=None,
    ):
        """initalize the FollowTrajectoryAction

        Parameters
        ----------
            trajectory (Trajectory, or CatalogReference): the trajectory to follow

            following_mode (FollowMode): the following mode of the action

            reference_domain (str): absolute or relative time reference (must be combined with scale and offset)
                Default: None
            scale (float): scalefactor of the timings (must be combined with reference_domain and offset)
                Default: None
            offset (float): offset for time values (must be combined with reference_domain and scale)
                Default: None
            initialDistanceOffset (float): start at this offset into the trajectory (v1.1)
                Default: None

        """
        # if following_mode not in FollowMode:
        #     ValueError(str(following_mode) + ' is not a valied following mode.')
        if not (
            isinstance(trajectory, Trajectory)
            or isinstance(trajectory, CatalogReference)
        ):
            raise TypeError("route input not of type Route or CatalogReference")
        self.trajectory = trajectory
        self.following_mode = following_mode
        # TODO: check reference_domain
        self.timeref = TimeReference(reference_domain, scale, offset)
        self.initialDistanceOffset = convert_float(initialDistanceOffset)

    def __eq__(self, other):
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
    def parse(element):
        """Parses the xml element of FollowTrajectoryAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A FollowTrajectoryAction element (same as generated by the class itself)

        Returns
        -------
            ft_action (FollowTrajectoryAction): a FollowTrajectoryAction object

        """
        fta_element = element.find("RoutingAction/FollowTrajectoryAction")
        initial_distance_offset = None
        if "initialDistanceOffset" in fta_element.attrib:
            initial_distance_offset = convert_float(
                fta_element.attrib["initialDistanceOffset"]
            )

        timeref = TimeReference.parse(fta_element.find("TimeReference"))
        reference_domain = timeref.reference_domain
        offset = timeref.offset
        scale = timeref.scale

        tfm_element = fta_element.find("TrajectoryFollowingMode")
        following_mode = getattr(FollowMode, tfm_element.attrib["followingMode"])

        if fta_element.find("TrajectoryRef") != None:
            fta_element = fta_element.find("TrajectoryRef")
        trajectory = None
        if fta_element.find("Trajectory") != None:
            trajectory = Trajectory.parse(fta_element.find("Trajectory"))
        if fta_element.find("CatalogReference") != None:
            trajectory = CatalogReference.parse(fta_element.find("CatalogReference"))

        return FollowTrajectoryAction(
            trajectory,
            following_mode,
            reference_domain,
            scale,
            offset,
            initial_distance_offset,
        )

    def get_attributes(self):
        """returns the attributes of the FollowTrajectoryAction as a dict"""
        if self.initialDistanceOffset:
            return {"initialDistanceOffset": str(self.initialDistanceOffset)}
        else:
            # If initialDistanceOffset is not set, return empty to stay backward compatible with v1.0
            return {}

    def get_element(self):
        """returns the elementTree of the FollowTrajectoryAction"""
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
    """ControllerAction creates a ControllerAction of open scenario

    Parameters
    ----------
        assignControllerAction (AssignControllerAction): assign a controller to an entity

        overrideControllerValueAction (OverrideControllerValueAction): values for brake, clutch, parking brake, steering wheel or gear

        activateControllerAction (ActivateControllerAction): activate/deactivate a controller on the reference entity/entities. Replaces the depreciated
                                                                element in PrivateAction in 1.1


    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class


    """

    def __init__(
        self,
        assignControllerAction=None,
        overrideControllerValueAction=None,
        activateControllerAction=None,
    ):

        """initalizes the ControllerAction

        Parameters
        ----------
            assignControllerAction (AssignControllerAction): assign a controller to an entity

            overrideControllerValueAction (OverrideControllerValueAction): values for brake, clutch, parking brake, steering wheel or gear

            activateControllerAction (ActivateControllerAction): activate/deactivate a controller on the reference entity/entities. Replaces the depreciated
                                                                element in PrivateAction in 1.1

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

    def __eq__(self, other):
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
    def parse(element):
        """Parses the xml element of ControllerAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A ControllerAction element (same as generated by the class itself)

        Returns
        -------
            (ControllerAction): a ActivateControllerAction object

        """

        activateControllerAction = None
        overrideControllerValueAction = None
        assignControllerAction = None

        ca_element = element.find("ControllerAction")

        if ca_element.find("ActivateControllerAction") != None:
            activateControllerAction = ActivateControllerAction.parse(element)
        if ca_element.find("OverrideControllerValueAction") != None:
            overrideControllerValueAction = OverrideControllerValueAction.parse(element)
        if ca_element.find("AssignControllerAction") != None:
            assignControllerAction = AssignControllerAction.parse(element)

        return ControllerAction(
            assignControllerAction,
            overrideControllerValueAction,
            activateControllerAction,
        )

    def get_element(self):
        """returns the elementTree of the ControllerAction"""
        if self.isVersion(minor=0):
            if (
                self.assignControllerAction is None
                or self.overrideControllerValueAction is None
            ):
                raise NotEnoughInputArguments(
                    "Both assignControllerAction and overrideControllerValueAction are required in version 1.0."
                )
            if self.activateControllerAction is not None:
                raise OpenSCENARIOVersionError(
                    "activateControllerAction is not parameter in version 1.0."
                )

        element = ET.Element("PrivateAction")
        controlleraction = ET.SubElement(element, "ControllerAction")

        if self.activateControllerAction != None:
            pa_element = self.activateControllerAction.get_element()
            aca_element = pa_element.find("ControllerAction/ActivateControllerAction")
            controlleraction.append(aca_element)

        if self.overrideControllerValueAction != None:
            pa_element = self.overrideControllerValueAction.get_element()
            ocva_element = pa_element.find(
                "ControllerAction/OverrideControllerValueAction"
            )
            controlleraction.append(ocva_element)

        if self.assignControllerAction != None:
            pa_element = self.assignControllerAction.get_element()
            aca_element = pa_element.find("ControllerAction/AssignControllerAction")
            controlleraction.append(aca_element)

        return element


class ActivateControllerAction(_PrivateActionType):
    """ActivateControllerAction creates a ActivateControllerAction of open scenario

    Parameters
    ----------
        lateral (boolean): activate or deactivate the controller

        longitudinal (boolean): activate or deactivate the controller

    Attributes
    ----------
        lateral (boolean): activate or deactivate the controller

        longitudinal (boolean): activate or deactivate the controller

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns the the attributes of the class

    """

    def __init__(self, lateral=None, longitudinal=None):
        """initalizes the ActivateControllerAction

        Parameters
        ----------
            lateral (boolean): activate or deactivate the controller
                Default: None

            longitudinal (boolean): activate or deactivate the controller
                Default: None
        """

        if lateral is not None and not isinstance(lateral, bool):
            raise TypeError("lateral input is not of type bool")

        if longitudinal is not None and not isinstance(longitudinal, bool):
            raise TypeError("longitudinal input is not of type bool")
        self.lateral = lateral
        self.longitudinal = longitudinal

    def __eq__(self, other):
        if isinstance(other, ActivateControllerAction):
            if self.get_attributes() == other.get_attributes():
                return True
        elif isinstance(other, ControllerAction):
            if self.get_attributes() == other.activateControllerAction.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of ActivateControllerAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A ActivateControllerAction element (same as generated by the class itself)

        Returns
        -------
            ac_action (ActivateControllerAction): a ActivateControllerAction object

        """
        aca_element = element.find("ControllerAction/ActivateControllerAction")
        lateral = None
        longitudinal = None
        if "lateral" in aca_element.attrib:
            lateral = convert_bool(aca_element.attrib["lateral"])
        if "longitudinal" in aca_element.attrib:
            longitudinal = convert_bool(aca_element.attrib["longitudinal"])

        return ActivateControllerAction(lateral, longitudinal)

    def get_attributes(self):
        """returns the attributes of the ActivateControllerAction as a dict"""
        return {
            "lateral": convert_bool(self.lateral),
            "longitudinal": convert_bool(self.longitudinal),
        }

    def get_element(self):
        """returns the elementTree of the ActivateControllerAction"""
        element = ET.Element("PrivateAction")
        if self.isVersion(minor=0):
            ET.SubElement(
                element, "ActivateControllerAction", attrib=self.get_attributes()
            )
        else:
            subelem = ET.SubElement(element, "ControllerAction")
            ET.SubElement(
                subelem, "ActivateControllerAction", attrib=self.get_attributes()
            )
        return element


class AssignControllerAction(_PrivateActionType):
    """AssignControllerAction creates a ControllerAction of type AssignControllerAction

    Parameters
    ----------
        controller (Controller or Catalogreference): a controller to assign

        activateLateral (bool): if the lateral control should be activated (valid from V1.1)
            Default: True

        activateLongitudinal (bool): if the longitudinal control should be activated (valid from V1.1)
            Default: True
    Attributes
    ----------
        controller (boolController or Catalogreferenceean): a controller to assign

        activateLateral (bool): if the lateral control should be activated (valid from V1.1)

        activateLongitudinal (bool): if the longitudinal control should be activated (valid from V1.1)

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

    """

    def __init__(self, controller, activateLateral=True, activateLongitudinal=True):
        """initalizes the AssignControllerAction

        Parameters
        ----------
            controller (Controller or Catalogreference): a controller to assign

            activateLateral (bool): if the lateral control should be activated (valid from V1.1)
                Default: True

            activateLongitudinal (bool): if the longitudinal control should be activated (valid from V1.1)
                Default: True
        """
        if not (
            isinstance(controller, Controller)
            or isinstance(controller, CatalogReference)
        ):
            raise TypeError("route input not of type Route or CatalogReference")
        self.controller = controller
        self.activateLateral = activateLateral
        self.activateLongitudinal = activateLongitudinal

    def __eq__(self, other):
        if isinstance(other, AssignControllerAction):
            if self.controller == other.controller:
                return True
        elif isinstance(other, ControllerAction):
            if self.controller == other.assignControllerAction.controller:
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of AssignControllerAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A AssignControllerAction element (same as generated by the class itself)

        Returns
        -------
            ac_action (AssignControllerAction): a AssignControllerAction object

        """
        ca_element = element.find("ControllerAction")
        aca_element = ca_element.find("AssignControllerAction")
        activate_lateral = True
        if "activateLateral" in aca_element.attrib:
            activate_lateral = convert_bool(aca_element.attrib["activateLateral"])

        activate_longitudinal = True
        if "activateLongitudinal" in aca_element.attrib:
            activate_longitudinal = convert_bool(
                aca_element.attrib["activateLongitudinal"]
            )

        controller = None
        if aca_element.find("Controller") != None:
            controller = Controller.parse(aca_element.find("Controller"))
        elif aca_element.find("CatalogReference") != None:
            controller = CatalogReference.parse(aca_element.find("CatalogReference"))
        else:
            raise NotAValidElement("No Controller found for AssignControllerAction")

        return AssignControllerAction(
            controller, activate_lateral, activate_longitudinal
        )

    def get_attributes(self):
        """returns the attributes of the VisibilityAction as a dict"""
        if self.isVersion(minor=0):
            return {}
        else:
            return {
                "activateLateral": convert_bool(self.activateLateral),
                "activateLongitudinal": convert_bool(self.activateLongitudinal),
            }

    def get_element(self):
        """returns the elementTree of the AssignControllerAction"""
        element = ET.Element("PrivateAction")
        controlleraction = ET.SubElement(element, "ControllerAction")
        assigncontrolleraction = ET.SubElement(
            controlleraction, "AssignControllerAction", self.get_attributes()
        )
        assigncontrolleraction.append(self.controller.get_element())

        return element


class OverrideControllerValueAction(_PrivateActionType):
    """OverrideControllerValueAction creates a OverrideControllerValueAction action of openscenario which can include, throttle, brake, clutch, steeringwheel, gear, parkingbrake
    NOTE: this implementation is compatible with osc v.1.1 where all attributes don't have to be set.

    Attributes
    ----------
        throttle_active (bool): if the throttle is active
            Default: None (will not be written)

        throttle_value (float): value of the throttle

        brake_active (bool): if the brake is active
            Default: None (will not be written)

        brake_value (float): value of the brake

        clutch_active (bool): if the clutch is active
            Default: None (will not be written)

        clutch_value (float): value of the clutch

        steeringwheel_active (bool): if the steeringwheel is active
            Default: None (will not be written)

        steeringwheel_value (float): value of the steeringwheel

        gear_active (bool): if the gear is active
            Default: None (will not be written)

        gear_value (float): value of the gear

        parkingbrake_active (bool): if the parkingbrake is active
            Default: None (will not be written)

        parkingbrake_value (float): value of the parkingbrake

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns the the attributes of the class

        set_throttle(active,value)
            sets the throttle value

        set_brake(active,value)
            sets the brake value

        set_steeringwheel(active,value)
            sets the steeringwheel value

        set_clutch(active,value)
            sets the clutch value

        set_gear(active,value)
            sets the gear value

        set_parkingbrake(active,value)
            sets the parkingbrake value

    """

    def __init__(self):
        self.throttle_active = None
        self.throttle_value = convert_float(0)
        self.brake_active = None
        self.brake_value = convert_float(0)
        self.clutch_active = None
        self.clutch_value = convert_float(0)
        self.steeringwheel_active = None
        self.steeringwheel_value = convert_float(0)
        self.gear_active = None
        self.gear_value = convert_float(0)
        self.parkingbrake_active = None
        self.parkingbrake_value = convert_float(0)

    def __eq__(self, other):
        if isinstance(other, OverrideControllerValueAction):
            if (
                self.throttle_value == other.throttle_value
                and self.throttle_value == other.throttle_value
                and self.brake_active == other.brake_active
                and self.brake_value == other.brake_value
                and self.clutch_active == other.clutch_active
                and self.clutch_value == other.clutch_value
                and self.steeringwheel_active == other.steeringwheel_active
                and self.steeringwheel_value == other.steeringwheel_value
                and self.gear_active == other.gear_active
                and self.gear_value == other.gear_value
                and self.parkingbrake_active == other.parkingbrake_active
                and self.parkingbrake_value == other.parkingbrake_value
            ):
                return True
        elif isinstance(other, ControllerAction):
            if (
                self.throttle_value
                == other.overrideControllerValueAction.throttle_value
                and self.throttle_value
                == other.overrideControllerValueAction.throttle_value
                and self.brake_active
                == other.overrideControllerValueAction.brake_active
                and self.brake_value == other.overrideControllerValueAction.brake_value
                and self.clutch_active
                == other.overrideControllerValueAction.clutch_active
                and self.clutch_value
                == other.overrideControllerValueAction.clutch_value
                and self.steeringwheel_active
                == other.overrideControllerValueAction.steeringwheel_active
                and self.steeringwheel_value
                == other.overrideControllerValueAction.steeringwheel_value
                and self.gear_active == other.overrideControllerValueAction.gear_active
                and self.gear_value == other.overrideControllerValueAction.gear_value
                and self.parkingbrake_active
                == other.overrideControllerValueAction.parkingbrake_active
                and self.parkingbrake_value
                == other.overrideControllerValueAction.parkingbrake_value
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of OverrideControllerValueAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A OverrideControllerValueAction element (same as generated by the class itself)

        Returns
        -------
            ocv_action (OverrideControllerValueAction): a OverrideControllerValueAction object

        """
        ocv_action = OverrideControllerValueAction()
        ocva_element = element.find("ControllerAction/OverrideControllerValueAction")

        ocv_action.throttle_active = None
        ocv_action.throttle_value = convert_float(0)
        if ocva_element.find("Throttle") != None:
            throttle_element = ocva_element.find("Throttle")
            ocv_action.throttle_active = convert_bool(throttle_element.attrib["active"])
            ocv_action.throttle_value = convert_float(throttle_element.attrib["value"])

        ocv_action.brake_active = None
        ocv_action.brake_value = convert_float(0)
        if ocva_element.find("Brake") != None:
            brake_element = ocva_element.find("Brake")
            ocv_action.brake_active = convert_bool(brake_element.attrib["active"])
            ocv_action.brake_value = convert_float(brake_element.attrib["value"])

        ocv_action.clutch_active = None
        ocv_action.clutch_value = convert_float(0)
        if ocva_element.find("Clutch") != None:
            cluth_element = ocva_element.find("Clutch")
            ocv_action.clutch_active = convert_bool(cluth_element.attrib["active"])
            ocv_action.clutch_value = convert_float(cluth_element.attrib["value"])

        ocv_action.parkingbrake_active = None
        ocv_action.parkingbrake_value = convert_float(0)
        if ocva_element.find("ParkingBrake") != None:
            parkingbrake_element = ocva_element.find("ParkingBrake")
            ocv_action.parkingbrake_active = convert_bool(
                parkingbrake_element.attrib["active"]
            )
            ocv_action.parkingbrake_value = convert_float(
                parkingbrake_element.attrib["value"]
            )

        ocv_action.steeringwheel_active = None
        ocv_action.steeringwheel_value = convert_float(0)
        if ocva_element.find("SteeringWheel") != None:
            steeringwheel_element = ocva_element.find("SteeringWheel")
            ocv_action.steeringwheel_active = convert_bool(
                steeringwheel_element.attrib["active"]
            )
            ocv_action.steeringwheel_value = convert_float(
                steeringwheel_element.attrib["value"]
            )

        ocv_action.gear_active = None
        ocv_action.gear_value = convert_float(0)
        if ocva_element.find("Gear") != None:
            gear_element = ocva_element.find("Gear")
            ocv_action.gear_active = convert_bool(gear_element.attrib["active"])
            ocv_action.gear_value = convert_float(gear_element.attrib["number"])

        return ocv_action

    def set_clutch(self, active, value=0):
        """Sets the clutch value

        Parameters
        ----------
            active (bool): if the clutch should be overridden

            value (float): value of the clutch
                Default: 0
        """
        self.clutch_active = active
        self.clutch_value = convert_float(value)

    def set_brake(self, active, value=0):
        """Sets the brake value

        Parameters
        ----------
            active (bool): if the brake should be overridden

            value (float): value of the brake
                Default: 0
        """
        self.brake_active = active
        self.brake_value = convert_float(value)

    def set_throttle(self, active, value=0):
        """Sets the throttle value

        Parameters
        ----------
            active (bool): if the throttle should be overridden

            value (float): value of the throttle
                Default: 0
        """
        self.throttle_active = active
        self.throttle_value = convert_float(value)

    def set_steeringwheel(self, active, value=0):
        """Sets the steeringwheel value

        Parameters
        ----------
            active (bool): if the steeringwheel should be overridden

            value (float): value of the steeringwheel
                Default: 0

        """
        self.steeringwheel_active = active
        self.steeringwheel_value = convert_float(value)

    def set_parkingbrake(self, active, value=0):
        """Sets the parkingbrake value

        Parameters
        ----------
            active (bool): if the parkingbrake should be overridden

            value (float): value of the parkingbrake
                Default: 0

        """
        self.parkingbrake_active = active
        self.parkingbrake_value = convert_float(value)

    def set_gear(self, active, value=0):
        """Sets the gear value

        Parameters
        ----------
            active (bool): if the gear should be overridden

            value (float): value of the gear
                Default: 0
        """
        self.gear_active = active
        self.gear_value = convert_float(value)

    def get_element(self):
        """returns the elementTree of the OverrideControllerValueAction"""
        element = ET.Element("PrivateAction")
        controlleraction = ET.SubElement(element, "ControllerAction")
        overrideaction = ET.SubElement(
            controlleraction, "OverrideControllerValueAction"
        )

        if (
            self.throttle_active == None
            and self.brake_active == None
            and self.clutch_active == None
            and self.parkingbrake_active == None
            and self.steeringwheel_active == None
            and self.gear_active == None
        ):
            raise NoActionsDefinedError(
                "No actions were added to the OverrideControllerValueAction"
            )
        if self.throttle_active != None:
            ET.SubElement(
                overrideaction,
                "Throttle",
                {
                    "active": convert_bool(self.throttle_active),
                    "value": str(self.throttle_value),
                },
            )
        if self.brake_active != None:
            ET.SubElement(
                overrideaction,
                "Brake",
                {
                    "active": convert_bool(self.brake_active),
                    "value": str(self.brake_value),
                },
            )
        if self.clutch_active != None:
            ET.SubElement(
                overrideaction,
                "Clutch",
                {
                    "active": convert_bool(self.clutch_active),
                    "value": str(self.clutch_value),
                },
            )
        if self.parkingbrake_active != None:
            ET.SubElement(
                overrideaction,
                "ParkingBrake",
                {
                    "active": convert_bool(self.parkingbrake_active),
                    "value": str(self.parkingbrake_value),
                },
            )
        if self.steeringwheel_active != None:
            ET.SubElement(
                overrideaction,
                "SteeringWheel",
                {
                    "active": convert_bool(self.steeringwheel_active),
                    "value": str(self.steeringwheel_value),
                },
            )
        if self.gear_active != None:
            ET.SubElement(
                overrideaction,
                "Gear",
                {
                    "active": convert_bool(self.gear_active),
                    "number": str(self.gear_value),
                },
            )

        return element


class VisibilityAction(_PrivateActionType):
    """creates a VisibilityAction

    Parameters
    ----------
        graphics (boolean): visible for graphics or not

        traffic (boolean): visible for traffic

        sensors (boolean): visible to sensors or not

    Attributes
    ----------
        graphics (boolean): visible for graphics or not

        traffic (boolean): visible for traffic

        sensors (boolean): visible to sensors or not

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns the the attributes of the class

    """

    def __init__(self, graphics, traffic, sensors):
        """initalizes the VisibilityAction

        Parameters
        ----------
        graphics (boolean): visible for graphics or not

        traffic (boolean): visible for traffic

        sensors (boolean): visible to sensors or not

        """
        if not isinstance(graphics, bool):
            raise TypeError("graphics input is not of type bool")
        if not isinstance(traffic, bool):
            raise TypeError("traffic input is not of type bool")
        if not isinstance(sensors, bool):
            raise TypeError("sensors input is not of type bool")
        self.graphics = graphics
        self.traffic = traffic
        self.sensors = sensors

    def __eq__(self, other):
        if isinstance(other, VisibilityAction):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of VisibilityAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A VisibilityAction element (same as generated by the class itself)

        Returns
        -------
            v_action (VisibilityAction): a VisibilityAction object

        """
        va_element = element.find("VisibilityAction")
        graphics = convert_bool(va_element.attrib["graphics"])
        traffic = convert_bool(va_element.attrib["traffic"])
        sensors = convert_bool(va_element.attrib["sensors"])

        return VisibilityAction(graphics, traffic, sensors)

    def get_attributes(self):
        """returns the attributes of the VisibilityAction as a dict"""
        return {
            "graphics": convert_bool(self.graphics),
            "traffic": convert_bool(self.traffic),
            "sensors": convert_bool(self.sensors),
        }

    def get_element(self):
        """returns the elementTree of the VisibilityAction"""
        element = ET.Element("PrivateAction")
        ET.SubElement(element, "VisibilityAction", self.get_attributes())
        return element


class SynchronizeAction(_PrivateActionType):
    """Synchronizes an entity's arrival at a destination with a master entity. Both entities are provided with their own reference position which shall be reached at the same time. Final speed can be specified. Note that the reference positions can be different or identical.

    Parameters
    ----------
        entity (str): entity to syncronize with

        entity_PositionType (*Position): the position of the entity to syncronize to

        target_PositionType (*Position): the position of the target that should syncronize

        speed (float): the absolute speed of the target that should syncronize

        target_tolerance_master (optional) (float): tolerance offset of the master's position [m]. (Valid from OpenSCENARIO V1.1)

        target_tolerance (optional) (float): tolerance offset of the target's position [m]. (Valid from OpenSCENARIO V1.1)

        final_speed (AbsoluteSpeed or RelativeSpeedToMaster): The speed that the synchronized entity should have at its target position. (Valid from OpenSCENARIO V1.1)
            Default: None
    Attributes
    ----------
        entity (str): entity to syncronize with

        entity_PositionType (*Position): the position of the entity to syncronize to

        target_PositionType (*Position): the position of the target that should syncronize

        speed (float): the absolute speed of the target that should syncronize

        target_tolerance_master (optional) (float): tolerance offset of the master's position [m]. (Valid from OpenSCENARIO V1.1)

        target_tolerance (optional) (float): tolerance offset of the target's position [m]. (Valid from OpenSCENARIO V1.1)

        final_speed (AbsoluteSpeed or RelativeSpeedToMaster): The speed that the synchronized entity should have at its target position. (Valid from OpenSCENARIO V1.1)

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns the the attributes of the class

    """

    def __init__(
        self,
        entity,
        entity_PositionType: _PositionType,
        target_PositionType: _PositionType,
        target_tolerance_master=None,
        target_tolerance=None,
        final_speed=None,
    ):
        """initalize the SynchronizeAction

        Parameters
        ----------
            entity (str): entity to syncronize with

            entity_PositionType (*Position): the position of the entity to syncronize to

            target_PositionType (*Position): the position of the target that should syncronize

            speed (float): the absolute speed of the target that should syncronize

            target_tolerance_master (optional) (float): tolerance offset of the master's position [m]. (Valid from OpenSCENARIO V1.1)

            target_tolerance (optional) (float): tolerance offset of the target's position [m]. (Valid from OpenSCENARIO V1.1)

            final_speed (AbsoluteSpeed or RelativeSpeedToMaster): The speed that the synchronized entity should have at its target position. (Valid from OpenSCENARIO V1.1)
            Default: None
        """

        self.entity = entity
        if not isinstance(entity_PositionType, _PositionType):
            raise TypeError("entity_PositionType input is not a valid Position")

        if not isinstance(target_PositionType, _PositionType):
            raise TypeError("target_PositionType input is not a valid Position")
        self.entity_PositionType = entity_PositionType
        self.target_PositionType = target_PositionType
        self.target_tolerance_master = convert_float(target_tolerance_master)
        self.target_tolerance = convert_float(target_tolerance)
        if final_speed and not (
            isinstance(final_speed, AbsoluteSpeed)
            or isinstance(final_speed, RelativeSpeedToMaster)
        ):
            raise TypeError(
                "final_speed input is not AbsoluteSpeed or RelativeSpeedToMaster type"
            )
        else:
            self.final_speed = final_speed

    def __eq__(self, other):
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
    def parse(element):
        """Parses the xml element of SynchronizeAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A SynchronizeAction element (same as generated by the class itself)

        Returns
        -------
            sync_action (SynchronizeAction): a SynchronizeAction object

        """
        sa_element = element.find("SynchronizeAction")
        entity = sa_element.attrib["masterEntityRef"]

        target_tolerance = None
        if "targetTolerance" in sa_element.attrib:
            target_tolerance = convert_float(sa_element.attrib["targetTolerance"])

        target_tolerance_master = None
        if "targetToleranceMaster" in sa_element.attrib:
            target_tolerance_master = convert_float(
                sa_element.attrib["targetToleranceMaster"]
            )

        targetPositionMaster = _PositionFactory.parse_position(
            sa_element.find("TargetPositionMaster")
        )
        targetPosition = _PositionFactory.parse_position(
            sa_element.find("TargetPosition")
        )

        finalSpeed = None
        if sa_element.find("FinalSpeed") != None:
            sa_element = sa_element.find("FinalSpeed")
            if sa_element.find("AbsoluteSpeed") != None:
                finalSpeed = AbsoluteSpeed.parse(sa_element)
            if sa_element.find("RelativeSpeedToMaster") != None:
                finalSpeed = RelativeSpeedToMaster.parse(sa_element)

        return SynchronizeAction(
            entity,
            targetPositionMaster,
            targetPosition,
            target_tolerance_master,
            target_tolerance,
            finalSpeed,
        )
        _

    def get_attributes(self):
        """returns the attributes of the AbsoluteSynchronizeAction as a dict"""
        attr = {"masterEntityRef": self.entity}
        if self.isVersion(1, 0):
            return attr
        if self.target_tolerance_master is not None:
            attr.update({"targetToleranceMaster": str(self.target_tolerance_master)})
        if self.target_tolerance is not None:
            attr.update({"targetTolerance": str(self.target_tolerance)})
        return attr

    def get_element(self):
        """returns the elementTree of the AbsoluteSynchronizeAction"""
        element = ET.Element("PrivateAction")
        syncaction = ET.SubElement(element, "SynchronizeAction", self.get_attributes())
        syncaction.append(self.entity_PositionType.get_element("TargetPositionMaster"))
        syncaction.append(self.target_PositionType.get_element("TargetPosition"))
        if self.final_speed is not None:
            syncaction.append(self.final_speed.get_element())
        return element


#### Global Actions ####
class ParameterAddAction(_ActionType):
    """The ParameterAddAction class creates a ParameterAction of type ParameterModifyAction which adds a value to an existing Parameter

    Parameters
    ----------
        parameter_ref (str): name of the parameter

        value (float): the value that should be added to the parameter

    Attributes
    ----------

        parameter_ref (str): name of the parameter

        value (float): the value that should be added to the parameter

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, parameter_ref, value):
        """initalize the ParameterAddAction

        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (float): the value that should be added to the parameter

        """
        self.parameter_ref = parameter_ref
        self.value = value

    def __eq__(self, other):
        if isinstance(other, ParameterAddAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.parameter_ref == other.parameter_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of ParameterAddAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A ParameterAddAction element (same as generated by the class itself)

        Returns
        -------
            paa_action (ParameterAddAction): a ParameterAddAction object

        """
        pa_element = element.find("ParameterAction")
        parameterRef = pa_element.attrib["parameterRef"]

        ma_element = pa_element.find("ModifyAction")
        rule_element = ma_element.find("Rule")
        mbv_element = rule_element.find("AddValue")
        value = mbv_element.attrib["value"]

        return ParameterAddAction(parameterRef, value)

    def get_attributes(self):
        """returns the attributes of the AbsoluteSpeedAction as a dict"""
        return {"value": str(self.value)}

    def get_element(self):
        """returns the elementTree of the AbsoluteSpeedAction"""
        element = ET.Element("GlobalAction")
        paramaction = ET.SubElement(
            element, "ParameterAction", {"parameterRef": self.parameter_ref}
        )
        modifaction = ET.SubElement(paramaction, "ModifyAction")
        rule = ET.SubElement(modifaction, "Rule")
        ET.SubElement(rule, "AddValue", self.get_attributes())

        return element


class ParameterMultiplyAction(_ActionType):
    """The ParameterMultiplyAction class creates a ParameterAction of tyoe ParameterModifyAction which adds a value to an existing Parameter

    Parameters
    ----------
        parameter_ref (str): name of the parameter

        value (float): the value that should be multiplied to the parameter

    Attributes
    ----------

        parameter_ref (str): name of the parameter

        value (float): the value that should be multiplied to the parameter

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, parameter_ref, value):
        """initalize the ParameterMultiplyAction

        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (float): the value that should be added to the parameter

        """
        self.parameter_ref = parameter_ref
        self.value = value

    def __eq__(self, other):
        if isinstance(other, ParameterMultiplyAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.parameter_ref == other.parameter_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of ParameterMultiplyAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A ParameterMultiplyAction element (same as generated by the class itself)

        Returns
        -------
            pma_action (ParameterMultiplyAction): a ParameterMultiplyAction object

        """
        pa_element = element.find("ParameterAction")
        parameterRef = pa_element.attrib["parameterRef"]

        ma_element = pa_element.find("ModifyAction")
        rule_element = ma_element.find("Rule")
        mbv_element = rule_element.find("MultiplyByValue")
        value = mbv_element.attrib["value"]

        return ParameterMultiplyAction(parameterRef, value)

    def get_attributes(self):
        """returns the attributes of the ParameterMultiplyAction as a dict"""
        return {"value": str(self.value)}

    def get_element(self):
        """returns the elementTree of the ParameterMultiplyAction"""
        element = ET.Element("GlobalAction")
        paramaction = ET.SubElement(
            element, "ParameterAction", {"parameterRef": self.parameter_ref}
        )
        modifaction = ET.SubElement(paramaction, "ModifyAction")
        rule = ET.SubElement(modifaction, "Rule")
        ET.SubElement(rule, "MultiplyByValue", self.get_attributes())

        return element


class ParameterSetAction(_ActionType):
    """The ParameterSetAction class creates a ParameterAction which adds a value to an existing Parameter

    Parameters
    ----------
        parameter_ref (str): name of the parameter

        value (float): the value that should be set to the parameter

    Attributes
    ----------

        parameter_ref (str): name of the parameter

        value (float): the value that should be set to the parameter

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, parameter_ref, value):
        """initalize the ParameterSetAction

        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (float): the value that should be added to the parameter

        """
        self.parameter_ref = parameter_ref
        self.value = value

    def __eq__(self, other):
        if isinstance(other, ParameterSetAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.parameter_ref == other.parameter_ref
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of ParameterSetAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A ParameterSetAction element (same as generated by the class itself)

        Returns
        -------
            psa_action (ParameterSetAction): a ParameterSetAction object

        """
        pa_element = element.find("ParameterAction")
        parameterRef = pa_element.attrib["parameterRef"]
        psa_element = pa_element.find("SetAction")
        value = psa_element.attrib["value"]
        return ParameterSetAction(parameterRef, value)

    def get_attributes(self):
        """returns the attributes of the ParameterSetAction as a dict"""
        return {"value": str(self.value)}

    def get_element(self):
        """returns the elementTree of the ParameterSetAction"""
        element = ET.Element("GlobalAction")
        paramaction = ET.SubElement(
            element, "ParameterAction", {"parameterRef": self.parameter_ref}
        )
        ET.SubElement(paramaction, "SetAction", self.get_attributes())

        return element


class TrafficSignalStateAction(_ActionType):
    """The TrafficSignalStateAction class creates a Infrastructure action which controls the state of a traffic signal

    Parameters
    ----------
        name (str): id of the signal in the road network

        state (str): the state to set to the traffic light

    Attributes
    ----------

        name (str): id of the signal in the road network

        state (str): the state to set to the traffic light

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, name, state):
        """initalize the TrafficSignalStateAction

        Parameters
        ----------
            name (str): id of the signal in the road network

            state (str): the state to set to the traffic light

        """
        self.name = name
        self.state = state

    def __eq__(self, other):
        if isinstance(other, TrafficSignalStateAction):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of TrafficSignalStateAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A TrafficSignalStateAction element (same as generated by the class itself)

        Returns
        -------
            tss_action (TrafficSignalStateAction): a TrafficSignalStateAction object

        """
        isa_element = element.find("InfrastructureAction")
        tsa_element = isa_element.find("TrafficSignalAction")
        tss_element = tsa_element.find("TrafficSignalStateAction")
        name = tss_element.attrib["name"]
        state = tss_element.attrib["state"]
        return TrafficSignalStateAction(name, state)

    def get_attributes(self):
        """returns the attributes of the TrafficSignalStateAction as a dict"""
        return {"name": self.name, "state": self.state}

    def get_element(self):
        """returns the elementTree of the TrafficSignalStateAction"""
        element = ET.Element("GlobalAction")
        infra = ET.SubElement(element, "InfrastructureAction")
        tsa = ET.SubElement(infra, "TrafficSignalAction")
        ET.SubElement(tsa, "TrafficSignalStateAction", self.get_attributes())

        return element


class AddEntityAction(_ActionType):
    """The AddEntityAction class creates a EntityAction which adds a entity to the scenario

    Parameters
    ----------
        entityref (str): reference name of the newly added vehicle

        position (*Position): position where the vehicle should be added

    Attributes
    ----------

        entityref (str): reference name of the newly added vehicle

        position (*Position): position where the vehicle should be added

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, entityref, position):
        """initalize the AddEntityAction

        Parameters
        ----------
            entityref (str): reference name of the newly added vehicle

            position (*Position): position where the vehicle should be added

        """

        self.entityref = entityref
        self.position = position

    def __eq__(self, other):
        if isinstance(other, AddEntityAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.position == other.position
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of AddEntityAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A AddEntityAction element (same as generated by the class itself)

        Returns
        -------
            ae_action (AddEntityAction): a AddEntityAction object

        """
        ea_element = element.find("EntityAction")
        entityref = ea_element.attrib["entityRef"]
        aea_element = ea_element.find("AddEntityAction")
        position = _PositionFactory.parse_position(aea_element.find("Position"))
        return AddEntityAction(entityref, position)

    def get_attributes(self):
        """returns the attributes of the AddEntityAction as a dict"""
        return {"entityRef": self.entityref}

    def get_element(self):
        """returns the elementTree of the AddEntityAction"""
        element = ET.Element("GlobalAction")
        entityact = ET.SubElement(element, "EntityAction", attrib=self.get_attributes())
        addentity = ET.SubElement(entityact, "AddEntityAction")
        addentity.append(self.position.get_element())

        return element


class DeleteEntityAction(_ActionType):
    """The DeleteEntityAction class creates a EntityAction which removes an entity to the scenario

    Parameters
    ----------
        entityref (str): reference name of the vehicle to remove

    Attributes
    ----------

        entityref (str): reference name of the vehicle to remove


    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, entityref):
        """initalize the DeleteEntityAction

        Parameters
        ----------
            entityref (str): reference name of the vehicle to remove

        """

        self.entityref = entityref

    def __eq__(self, other):
        if isinstance(other, DeleteEntityAction):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of DeleteEntityAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A DeleteEntityAction element (same as generated by the class itself)

        Returns
        -------
            de_action (DeleteEntityAction): a DeleteEntityAction object

        """
        ea_element = element.find("EntityAction")
        entityref = ea_element.attrib["entityRef"]
        return DeleteEntityAction(entityref)

    def get_attributes(self):
        """returns the attributes of the DeleteEntityAction as a dict"""
        return {"entityRef": self.entityref}

    def get_element(self):
        """returns the elementTree of the DeleteEntityAction"""
        element = ET.Element("GlobalAction")
        entityact = ET.SubElement(element, "EntityAction", attrib=self.get_attributes())
        ET.SubElement(entityact, "DeleteEntityAction")

        return element


class TrafficSignalControllerAction(_ActionType):
    """The TrafficSignalControllerAction class creates a Infrastructure action which activates a controller of a traffic signal

    Parameters
    ----------
        phase (str): phase of the signal

        traffic_signalcontroller_ref (str): reference to traffic signal controller

    Attributes
    ----------

        phase (str): phase of the signal

        traffic_signalcontroller_ref (str): reference to traffic signal controller

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, phase, traffic_signalcontroller_ref):
        """initalize the TrafficSignalControllerAction

        Parameters
        ----------
            phase (str): phase of the signal

            traffic_signalcontroller_ref (str): reference to traffic signal controller

        """
        self.phase = phase
        self.traffic_signalcontroller_ref = traffic_signalcontroller_ref

    def __eq__(self, other):
        if isinstance(other, TrafficSignalControllerAction):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of TrafficSignalControllerAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A TrafficSignalControllerAction element (same as generated by the class itself)

        Returns
        -------
            tsc_action (TrafficSignalControllerAction): a TrafficSignalControllerAction object

        """
        isa_element = element.find("InfrastructureAction")
        tsa_element = isa_element.find("TrafficSignalAction")
        tsc_element = tsa_element.find("TrafficSignalControllerAction")

        phase = tsc_element.attrib["phase"]
        tsc_ref = tsc_element.attrib["trafficSignalControllerRef"]

        return TrafficSignalControllerAction(phase, tsc_ref)

    def get_attributes(self):
        """returns the attributes of the TrafficSignalControllerAction as a dict"""
        return {
            "phase": self.phase,
            "trafficSignalControllerRef": self.traffic_signalcontroller_ref,
        }

    def get_element(self):
        """returns the elementTree of the TrafficSignalControllerAction"""
        element = ET.Element("GlobalAction")
        infra = ET.SubElement(element, "InfrastructureAction")
        tsa = ET.SubElement(infra, "TrafficSignalAction")
        ET.SubElement(tsa, "TrafficSignalControllerAction", self.get_attributes())

        return element


class TrafficSourceAction(_ActionType):
    """The TrafficSourceAction class creates a TrafficAction of the typ TrafficSourceAction

    Parameters
    ----------
        rate (float): rate of appearing traffic

        radius (float): the radius of the source around the position

        position (*Position): any Position to define the source

        trafficdefinition (TrafficDefinition): definition of the traffic

        velocity (float): optional starting velocity of the traffic
            Default: None

        name (str): name of the TrafficAction, can be used to stop the TrafficAction, (valid from V1.1)
            Default: None

    Attributes
    ----------

        rate (float): rate of appearing traffic

        radius (float): the radius of the source around the position

        position (*Position): any Position to define the source

        trafficdefinition (TrafficDefinition): definition of the traffic

        velocity (float): optional starting velocity of the traffic
            Default: None

        name (str): name of the TrafficAction, can be used to stop the TrafficAction, (valid from V1.1)

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(
        self, rate, radius, position, trafficdefinition, velocity=None, name=None
    ):
        """initalize the TrafficSourceAction

        Parameters
        ----------
            rate (float): rate of appearing traffic

            radius (float): the radius of the source around the position

            position (*Position): any Position to define the source

            trafficdefinition (TrafficDefinition): definition of the traffic

            velocity (float): optional starting velocity of the traffic
                Default: None

            name (str): name of the TrafficAction, can be used to stop the TrafficAction, (valid from V1.1)
                Default: None
        """
        self.rate = rate
        self.radius = radius
        if not isinstance(position, _PositionType):
            raise TypeError("position input is not a valid Position")

        if not isinstance(trafficdefinition, TrafficDefinition):
            raise TypeError("trafficdefinition input is not of type TrafficDefinition")
        self.position = position
        self.trafficdefinition = trafficdefinition
        self.velocity = velocity
        self.name = name

    def __eq__(self, other):
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
    def parse(element):
        """Parses the xml element of TrafficSourceAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A TrafficSourceAction element (same as generated by the class itself)

        Returns
        -------
            tsa_action (TrafficSourceAction): a TrafficSourceAction object

        """
        ta_element = element.find("TrafficAction")
        name = None
        if "trafficName" in ta_element.attrib:
            name = ta_element.attrib["trafficName"]
        tsa_element = ta_element.find("TrafficSourceAction")

        radius = tsa_element.attrib["radius"]
        rate = tsa_element.attrib["rate"]
        velocity = None
        if "velocity" in tsa_element.attrib:
            velocity = tsa_element.attrib["velocity"]

        position = _PositionFactory.parse_position(tsa_element.find("Position"))
        trafficdefinition = TrafficDefinition.parse(
            tsa_element.find("TrafficDefinition")
        )

        return TrafficSourceAction(
            rate, radius, position, trafficdefinition, velocity, name
        )

    def get_attributes(self):
        """returns the attributes of the TrafficSourceAction as a dict"""
        retdict = {}
        retdict["rate"] = str(self.rate)
        retdict["radius"] = str(self.radius)
        if self.velocity is not None:
            retdict["velocity"] = str(self.velocity)

        return retdict

    def get_element(self):
        """returns the elementTree of the TrafficSourceAction"""
        element = ET.Element("GlobalAction")
        traffic_attrib = {}
        if self.name and not self.isVersion(minor=0):
            traffic_attrib = {"trafficName": self.name}

        trafficaction = ET.SubElement(element, "TrafficAction", attrib=traffic_attrib)
        sourceaction = ET.SubElement(
            trafficaction, "TrafficSourceAction", attrib=self.get_attributes()
        )
        sourceaction.append(self.position.get_element())
        sourceaction.append(self.trafficdefinition.get_element())

        return element


class TrafficSinkAction(_ActionType):
    """The TrafficSinkAction class creates a TrafficAction of the typ TrafficSinkAction

    Parameters
    ----------
        rate (float): rate of appearing traffic

        radius (float): the radius of the sink around the position

        position (*Position): any Position to define the sink

        trafficdefinition (TrafficDefinition): definition of the traffic

        name (str): name of the TrafficAction, can be used to stop the TrafficAction, (valid from V1.1)
            Default: None

    Attributes
    ----------

        rate (float): rate of appearing traffic

        radius (float): the radius of the source around the position

        position (*Position): any Position to define the source

        trafficdefinition (TrafficDefinition): definition of the traffic

        name (str): name of the TrafficAction, can be used to stop the TrafficAction, (valid from V1.1)

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, radius, position, trafficdefinition, rate=None, name=None):
        """initalize the TrafficSinkAction

        Parameters
        ----------
            rate (float): rate of appearing traffic

            radius (float): the radius of the source around the position

            position (*Position): any Position to define the source

            trafficdefinition (TrafficDefinition): definition of the traffic

            name (str): name of the TrafficAction, can be used to stop the TrafficAction, (valid from V1.1)

        """
        self.rate = rate
        self.radius = radius
        if not isinstance(position, _PositionType):
            raise TypeError("position input is not a valid Position")

        if not isinstance(trafficdefinition, TrafficDefinition):
            raise TypeError("trafficdefinition input is not of type TrafficDefinition")
        self.position = position
        self.trafficdefinition = trafficdefinition
        self.name = name

    def __eq__(self, other):
        if isinstance(other, TrafficSinkAction):
            if (
                self.get_attributes() == other.get_attributes()
                and self.position == other.position
                and self.trafficdefinition == other.trafficdefinition
            ):
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of TrafficSinkAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A TrafficSinkAction element (same as generated by the class itself)

        Returns
        -------
            ts_action (TrafficSinkAction): a TrafficSinkAction object

        """
        ta_element = element.find("TrafficAction")
        name = None
        if "trafficName" in ta_element.attrib:
            name = ta_element.attrib["trafficName"]

        tsa_element = ta_element.find("TrafficSinkAction")
        radius = tsa_element.attrib["radius"]
        rate = None
        if "rate" in tsa_element.attrib:
            rate = tsa_element.attrib["rate"]

        if tsa_element.find("TrafficDefinition") != None:
            trafficdefinition = TrafficDefinition.parse(
                tsa_element.find("TrafficDefinition")
            )

        position = _PositionFactory.parse_position(tsa_element.find("Position"))

        return TrafficSinkAction(radius, position, trafficdefinition, rate, name)

    def get_attributes(self):
        """returns the attributes of the TrafficSinkAction as a dict"""
        retdict = {}

        retdict["rate"] = str(self.rate)
        retdict["radius"] = str(self.radius)
        return retdict

    def get_element(self):
        """returns the elementTree of the TrafficSinkAction"""

        element = ET.Element("GlobalAction")
        traffic_attrib = {}
        if self.name and not self.isVersion(minor=0):
            traffic_attrib = {"trafficName": self.name}
        trafficaction = ET.SubElement(element, "TrafficAction", attrib=traffic_attrib)
        sinkaction = ET.SubElement(
            trafficaction, "TrafficSinkAction", attrib=self.get_attributes()
        )
        sinkaction.append(self.position.get_element())
        sinkaction.append(self.trafficdefinition.get_element())

        return element


class TrafficSwarmAction(_ActionType):
    """The TrafficSwarmAction class creates a TrafficAction of the typ TrafficSwarmAction

    Parameters
    ----------
        semimajoraxis (float): half length of major axis of ellipsis around target

        semiminoraxis (float): half length of minor axis of ellipsis around target

        innerradius (float): radius of inner cirvle

        offset (float): longitudinal offset from central entity

        numberofvehicles (int): maximum number of vehicles around entity

        centralobject (str): entity to swarm around

        trafficdefinition (TrafficDefinition): definition of the traffic

        velocity (float): optional starting velocity
            Default: None

        name (str): name of the TrafficAction, can be used to stop the TrafficAction, (valid from V1.1)
            Default: None
    Attributes
    ----------

        semimajoraxis (float): half length of major axis of ellipsis around target

        semiminoraxis (float): half length of minor axis of ellipsis around target

        innerradius (float): radius of inner cirvle

        offset (float): longitudinal offset from central entity

        numberofvehicles (int): maximum number of vehicles around entity

        centralobject (str): entity to swarm around

        trafficdefinition (TrafficDefinition): definition of the traffic

        velocity (float): optional starting velocity
            Default: None

        name (str): name of the TrafficAction, can be used to stop the TrafficAction, (valid from V1.1)

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(
        self,
        semimajoraxis,
        semiminoraxis,
        innerradius,
        offset,
        numberofvehicles,
        centralobject,
        trafficdefinition,
        velocity=None,
        name=None,
    ):
        """initalize the TrafficSwarmAction

        Parameters
        ----------
            semimajoraxis (float): half length of major axis of ellipsis around target

            semiminoraxis (float): half length of minor axis of ellipsis around target

            innerradius (float): radius of inner circle

            offset (float): longitudinal offset from central entity

            numberofvehicles (int): maximum number of vehicles around entity

            centralobject (str): entity to swarm around

            trafficdefinition (TrafficDefinition): definition of the traffic

            velocity (float): optional starting velocity
                Default: None

            name (str): name of the TrafficAction, can be used to stop the TrafficAction, (valid from V1.1)
                Default: None
        """
        self.semimajoraxis = semimajoraxis
        self.semiminoraxis = semiminoraxis
        self.innerradius = innerradius
        self.offset = offset
        self.numberofvehicles = numberofvehicles
        self.centralobject = centralobject
        if not isinstance(trafficdefinition, TrafficDefinition):
            raise TypeError("trafficdefinition input is not of type TrafficDefinition")
        self.trafficdefinition = trafficdefinition
        self.velocity = velocity
        self.name = name

    def __eq__(self, other):
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
    def parse(element):
        """Parses the xml element of TrafficSwarmAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A TrafficSwarmAction element (same as generated by the class itself)

        Returns
        -------
            ts_action (TrafficSwarmAction): a TrafficSwarmAction object

        """
        ta_element = element.find("TrafficAction")
        name = None
        if "trafficName" in ta_element.attrib:
            name = ta_element.attrib["trafficName"]

        tsa_element = ta_element.find("TrafficSwarmAction")

        innerradius = tsa_element.attrib["innerRadius"]
        numberofvehicles = tsa_element.attrib["numberOfVehicles"]
        offset = tsa_element.attrib["offset"]
        semimajoraxis = tsa_element.attrib["semiMajorAxis"]
        semiminoraxis = tsa_element.attrib["semiMinorAxis"]
        velocity = None
        if "velocity" in tsa_element.attrib:
            velocity = tsa_element.attrib["velocity"]

        trafficdefinition = TrafficDefinition.parse(
            tsa_element.find("TrafficDefinition")
        )

        central_element = tsa_element.find("CentralSwarmObject")
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
        )
        return tsa_object

    def get_attributes(self):
        """returns the attributes of the TrafficSwarmAction as a dict"""
        retdict = {}
        retdict["semiMajorAxis"] = str(self.semimajoraxis)
        retdict["semiMinorAxis"] = str(self.semiminoraxis)
        retdict["innerRadius"] = str(self.innerradius)
        retdict["offset"] = str(self.offset)
        retdict["numberOfVehicles"] = str(self.numberofvehicles)
        if self.velocity is not None:
            retdict["velocity"] = str(self.velocity)
        return retdict

    def get_element(self):
        """returns the elementTree of the TrafficSwarmAction"""
        element = ET.Element("GlobalAction")
        traffic_attrib = {}
        if self.name and not self.isVersion(minor=0):
            traffic_attrib = {"trafficName": self.name}
        trafficaction = ET.SubElement(element, "TrafficAction", attrib=traffic_attrib)

        swarmaction = ET.SubElement(
            trafficaction, "TrafficSwarmAction", attrib=self.get_attributes()
        )
        swarmaction.append(self.trafficdefinition.get_element())
        ET.SubElement(
            swarmaction, "CentralSwarmObject", attrib={"entityRef": self.centralobject}
        )

        return element


class TrafficStopAction(_ActionType):
    """The TrafficStopAction class creates a TrafficAction of the typ TrafficStopAction

    Parameters
    ----------
        name (str): name of the Traffic to stop
            Default: None

    Attributes
    ----------

        name (str): name of the Traffic to stop

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, name=None):
        """initalize the TrafficSwarmAction

        Parameters
        ----------
            name (str): name of the Traffic to stop
                Default: None
        """
        self.name = name

    def __eq__(self, other):
        if isinstance(other, TrafficStopAction):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of TrafficStopAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A TrafficStopAction element (same as generated by the class itself)

        Returns
        -------
            ts_action (TrafficStopAction): a TrafficStopAction object

        """
        trafficaction_element = element.find("TrafficAction")
        name = trafficaction_element.attrib["trafficName"]
        return TrafficStopAction(name)

    def get_attributes(self):
        """returns the attributes of the TrafficStopAction as a dict"""
        retdict = {}
        if self.name and not self.isVersion(minor=0):
            retdict["trafficName"] = str(self.name)
        elif self.isVersion(minor=0):
            raise OpenSCENARIOVersionError(
                "TrafficStopAction was introduced in OpenSCENARIO V1.1"
            )

        return retdict

    def get_element(self):
        """returns the elementTree of the TrafficStopAction"""
        element = ET.Element("GlobalAction")
        trafficaction = ET.SubElement(
            element, "TrafficAction", attrib=self.get_attributes()
        )
        ET.SubElement(trafficaction, "TrafficStopAction")

        return element


class EnvironmentAction(_ActionType):
    """The EnvironmentAction class creates a GlobalAction of the typ EnvironmentAction

    Parameters
    ----------
        environment (Environment or CatalogReference): the environment to change to

    Attributes
    ----------

        environment (Environment or CatalogReference): the environment to change to

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class itself

        get_element()
            Returns the full ElementTree of the class

    """

    def __init__(self, environment):
        """initalize the EnvironmentAction

        Parameters
        ----------
            name (str): name of the action

            environment (Environment or CatalogReference): the environment to change to

        """
        if not (
            isinstance(environment, Environment)
            or isinstance(environment, CatalogReference)
        ):
            raise TypeError(
                "environment input not of type Environment or CatalogReference"
            )
        self.environment = environment

    def __eq__(self, other):
        if isinstance(other, EnvironmentAction):
            if self.environment == other.environment:
                return True
        return False

    @staticmethod
    def parse(element):
        """Parses the xml element of BoundingBox

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A orientation element (same as generated by the class itself)

        Returns
        -------
            boundingBox (BoundingBox): a BoundingBox object

        """
        action_element = element.find("EnvironmentAction")
        if action_element.find("Environment") != None:
            environment = Environment.parse(action_element.find("Environment"))
        elif action_element.find("CatalogReference") != None:
            environment = CatalogReference.parse(
                action_element.find("CatalogReference")
            )

        return EnvironmentAction(environment)

    def get_element(self):
        """returns the elementTree of the EnvironmentAction"""
        element = ET.Element("GlobalAction")
        envaction = ET.SubElement(element, "EnvironmentAction")
        envaction.append(self.environment.get_element())

        return element


class UserDefinedAction(_ActionType):
    """The UserDefinedAction enables adding simulator-specific CustomCommandActions.

    Parameters
    ----------

    Attributes
    ----------

    Methods
    -------
        add_custom_command_action(custom_command_action)
            Adds a CustomCommandAction to the UserDefinedAction

        get_element()
            Returns the full ElementTree of the class
    """

    def __init__(self):
        """initalize the UserDefinedAction

        Parameters
        ----------

        """
        self.custom_command_actions = []

    def add_custom_command_action(self, custom_command_action):
        """add a CustomCommandAction

        Parameters
        ----------
            custom_command_action (CustomCommandAction): A CustomCommandAction element

        """
        self.custom_command_actions.append(custom_command_action)
        return self

    def __eq__(self, other):
        if isinstance(other, UserDefinedAction):
            if len(self.custom_command_actions) == len(other.custom_command_actions):
                if all(
                    [
                        self.custom_command_actions[i]
                        == other.custom_command_actions[i]
                        for i in range(len(self.custom_command_actions))
                    ]
                ):
                    return True
        return False

    @staticmethod
    def parse(element):
        """Parsese the xml element of a UserDefinedAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): a UserDefinedAction element

        Returns
        -------
            userDefinedAction (UserDefinedAction): a UserDefinedAction object

        """
        user_defined_action = UserDefinedAction()
        for custom_command_element in element.findall("CustomCommandAction"):
            custom_command_action = CustomCommandAction.parse(custom_command_element)
            user_defined_action.add_custom_command_action(custom_command_action)
        return user_defined_action

    def get_element(self):
        """returns the elementTree of the UserDefinedAction"""
        element = ET.Element("UserDefinedAction")
        for custom_command_action in self.custom_command_actions:
            element.append(custom_command_action.get_element())
        return element


class CustomCommandAction(_ActionType):
    """The CustomCommandAction creates a simulator defined action


    Parameters
    ----------

    Attributes
    ----------

        type (str): type of the custom command

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

    """

    def __init__(self, type):
        """initalize the CustomCommandAction

        Parameters
        ----------
            type (str): type of the custom command

        """
        self.type = type

    def __eq__(self, other):
        if isinstance(other, CustomCommandAction):
            if other.type == self.type:
                return True
        return False

    @staticmethod
    def parse(element):
        """Parsese the xml element of a CustomCommandAction

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): a CustomCommandAction element

        Returns
        -------
            customCommandAction (CustomCommandAction): a CustomCommandAction object

        """
        if element.tag != "CustomCommandAction":
            raise NotAValidElement(
                f'Expected "CustomCommandAction" element, received "{element.tag}".'
            )
        action_type = element.attrib.get("type", None)
        if action_type == None:
            raise NotAValidElement(
                'CustomCommandAction is missing required argument "type".'
            )
        return CustomCommandAction(action_type)

    def get_element(self):
        """returns the elementTree of the CustomCommandAction"""
        element = ET.Element("CustomCommandAction", attrib={"type": self.type})
        return element
