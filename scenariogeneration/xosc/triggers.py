"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
from typing import Union

from .enumerations import (
    ConditionEdge,
    CoordinateSystem,
    DirectionalDimension,
    ObjectType,
    RelativeDistanceType,
    RoutingAlgorithm,
    Rule,
    StoryboardElementState,
    StoryboardElementType,
    TriggeringEntitiesRule,
    VersionBase,
)
from .exceptions import (
    NotAValidElement,
    NotEnoughInputArguments,
    OpenSCENARIOVersionError,
    ToManyOptionalArguments,
)
from .position import _PositionFactory
from .utils import (
    EntityRef,
    _EntityTriggerType,
    _PositionType,
    _TriggerType,
    _ValueTriggerType,
    convert_bool,
    convert_enum,
    convert_float,
    convert_int,
    find_mandatory_field,
    get_bool_string,
)


class EmptyTrigger(_TriggerType):
    """EmptyTrigger creates an empty trigger.

    Parameters
    ----------
    triggeringpoint : str, optional
        Start or stop. Default is "start".

    Methods
    -------
    get_element()
        Returns the full ElementTree of the class.
    """

    def __init__(self, triggeringpoint: str = "start") -> None:
        """Initializes the empty trigger.

        Parameters
        ----------
        triggeringpoint : str, optional
            Start or stop. Default is "start".
        """
        if triggeringpoint not in ["start", "stop"]:
            raise ValueError(
                "not a valid triggering point, valid start or stop"
            )
        if triggeringpoint == "start":
            self._triggerpoint = "StartTrigger"
        else:
            self._triggerpoint = "StopTrigger"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EmptyTrigger):
            if self._triggerpoint == other._triggerpoint:
                return True
        elif isinstance(other, Trigger):
            if (
                len(other.conditiongroups) == 0
                and self._triggerpoint == other._triggerpoint
            ):
                return True
        return False

    def get_element(self) -> ET.Element:
        """Generate an XML element for the trigger point.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the trigger point.
        """
        return ET.Element(self._triggerpoint)


class _EntityConditionFactory:
    @staticmethod
    def parse_entity_condition(element: ET.Element) -> _EntityTriggerType:
        if element.find("EndOfRoadCondition") is not None:
            return EndOfRoadCondition.parse(element)
        if element.find("CollisionCondition") is not None:
            return CollisionCondition.parse(element)
        if element.find("OffroadCondition") is not None:
            return OffroadCondition.parse(element)
        if element.find("TimeHeadwayCondition") is not None:
            return TimeHeadwayCondition.parse(element)
        if element.find("TimeToCollisionCondition") is not None:
            return TimeToCollisionCondition.parse(element)
        if element.find("AccelerationCondition") is not None:
            return AccelerationCondition.parse(element)
        if element.find("StandStillCondition") is not None:
            return StandStillCondition.parse(element)
        if element.find("SpeedCondition") is not None:
            return SpeedCondition.parse(element)
        if element.find("RelativeSpeedCondition") is not None:
            return RelativeSpeedCondition.parse(element)
        if element.find("TraveledDistanceCondition") is not None:
            return TraveledDistanceCondition.parse(element)
        if element.find("ReachPositionCondition") is not None:
            return ReachPositionCondition.parse(element)
        if element.find("DistanceCondition") is not None:
            return DistanceCondition.parse(element)
        if element.find("RelativeDistanceCondition") is not None:
            return RelativeDistanceCondition.parse(element)
        raise NotAValidElement(
            "element ", element, "is not a valid entity condition"
        )


class _ValueConditionFactory:
    @staticmethod
    def parse_value_condition(element: ET.Element) -> _ValueTriggerType:
        if element.find("ParameterCondition") is not None:
            return ParameterCondition.parse(
                find_mandatory_field(element, "ParameterCondition")
            )
        if element.find("VariableCondition") is not None:
            return VariableCondition.parse(
                find_mandatory_field(element, "VariableCondition")
            )
        if element.find("TimeOfDayCondition") is not None:
            return TimeOfDayCondition.parse(
                find_mandatory_field(element, "TimeOfDayCondition")
            )
        if element.find("SimulationTimeCondition") is not None:
            return SimulationTimeCondition.parse(
                find_mandatory_field(element, "SimulationTimeCondition")
            )
        if element.find("StoryboardElementStateCondition") is not None:
            return StoryboardElementStateCondition.parse(
                find_mandatory_field(
                    element, "StoryboardElementStateCondition"
                )
            )
        if element.find("UserDefinedValueCondition") is not None:
            return UserDefinedValueCondition.parse(
                find_mandatory_field(element, "UserDefinedValueCondition")
            )
        if element.find("TrafficSignalCondition") is not None:
            return TrafficSignalCondition.parse(
                find_mandatory_field(element, "TrafficSignalCondition")
            )
        if element.find("TrafficSignalControllerCondition") is not None:
            return TrafficSignalControllerCondition.parse(
                find_mandatory_field(
                    element, "TrafficSignalControllerCondition"
                )
            )
        raise NotAValidElement(
            "element ", element, "is not a valid entity condition"
        )


class _ConditionFactory:
    @staticmethod
    def parse_condition(element: ET.Element) -> _TriggerType:
        if element.find("ByEntityCondition/EntityCondition") is not None:
            return EntityTrigger.parse(element)
        elif element.find("ByValueCondition") is not None:
            return ValueTrigger.parse(element)
        else:
            raise NotAValidElement(
                "element ", element, "is not a valid condition"
            )


class EntityTrigger(_TriggerType):
    """The EntityTrigger creates a Trigger containing an EntityTrigger.

    Parameters
    ----------
    name : str
        Name of the trigger.
    delay : float
        The delay of the trigger.
    conditionedge : ConditionEdge
        On what condition edge the trigger should act.
    entitycondition : *EntityCondition
        An entity condition.
    triggerentity : str
        The entity of the trigger.
    triggeringrule : TriggeringEntitiesRule, optional
        Rule of the trigger. Default is 'any'.
    triggeringpoint : str, optional
        Start or stop. Default is 'start'.

    Attributes
    ----------
    name : str
        Name of the trigger.
    delay : float
        The delay of the trigger.
    conditionedge : ConditionEdge
        The condition edge.
    entitycondition : *EntityCondition
        The entity condition.
    triggerentity : TriggeringEntities
        The triggering entity.

    Methods
    -------
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        name: str,
        delay: float,
        conditionedge: ConditionEdge,
        entitycondition: _EntityTriggerType,
        triggerentity: str,
        triggeringrule: TriggeringEntitiesRule = TriggeringEntitiesRule.any,
        triggeringpoint: str = "start",
    ) -> None:
        """Initialize the EntityTrigger.

        Parameters
        ----------
        name : str
            Name of the trigger.
        delay : float
            The delay of the trigger.
        conditionedge : ConditionEdge
            On what condition edge the trigger should act.
        entitycondition : *EntityCondition
            An entity condition.
        triggerentity : str
            The entity of the trigger.
        triggeringrule : TriggeringEntitiesRule, optional
            Rule of the trigger. Default is 'any'.
        triggeringpoint : str, optional
            Start or stop. Default is 'start'.
        """
        self.name = name
        if triggeringpoint not in ["start", "stop"]:
            raise ValueError(
                "not a valid triggering point, valid start or stop"
            )
        if triggeringpoint == "start":
            self._triggerpoint = "StartTrigger"
        else:
            self._triggerpoint = "StopTrigger"

        self.delay = convert_float(delay)
        self.conditionedge = convert_enum(conditionedge, ConditionEdge)
        if not isinstance(entitycondition, _EntityTriggerType):
            raise TypeError("entitycondition is not a valid EntityCondition")
        self.entitycondition = entitycondition
        self.triggerentity = TriggeringEntities(triggeringrule)
        self.triggerentity.add_entity(triggerentity)

        self._used_by_parent = False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EntityTrigger):
            if (
                self.get_attributes() == other.get_attributes()
                and self.triggerentity == other.triggerentity
                and self.entitycondition == other.entitycondition
                and self._triggerpoint == other._triggerpoint
            ):
                return True
        elif isinstance(other, Trigger):
            if (
                len(other.conditiongroups) == 1
                and len(other.conditiongroups[0].conditions) == 1
            ):
                if (
                    self._triggerpoint == other._triggerpoint
                    and other.conditiongroups[0].conditions[0] == self
                ):
                    return True
        elif isinstance(other, ConditionGroup):
            if len(other.conditions) == 1:
                if (
                    self._triggerpoint == other._triggerpoint
                    and other.conditions[0] == self
                ):
                    return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "EntityTrigger":
        """Parses the XML element of EntityTrigger.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        EntityTrigger
            An EntityTrigger object.

        Notes
        -----
        This parser will ONLY parse the Condition itself, not the
        ConditionGroup or Trigger that it can generate.
        """
        if element.tag != "Condition":
            raise NotAValidElement(
                "ValueTrigger only parses a Condition, not ", element
            )

        name = element.attrib["name"]
        delay = convert_float(element.attrib["delay"])
        conditionedge = convert_enum(
            element.attrib["conditionEdge"], ConditionEdge
        )
        entityconditionelement = find_mandatory_field(
            element, "ByEntityCondition"
        )
        triggering_entities = TriggeringEntities.parse(
            find_mandatory_field(entityconditionelement, "TriggeringEntities")
        )
        condition = _EntityConditionFactory.parse_entity_condition(
            find_mandatory_field(entityconditionelement, "EntityCondition")
        )
        enttrig = EntityTrigger(name, delay, conditionedge, condition, "")
        enttrig.triggerentity = triggering_entities

        return enttrig

    def _set_used_by_parent(self) -> None:
        """Used internally if the condition is added to a ConditionGroup."""
        self._used_by_parent = True

    def add_triggering_entity(self, triggerentity: str) -> "EntityTrigger":
        """Adds additional triggering entities to a trigger.

        Parameters
        ----------
        triggerentity : str
            Name of the triggering entity.

        Returns
        -------
        EntityTrigger
            The updated EntityTrigger object.
        """
        self.triggerentity.add_entity(triggerentity)
        return self

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the EntityTrigger as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary of all attributes of the class.
        """
        return {
            "name": self.name,
            "delay": str(self.delay),
            "conditionEdge": self.conditionedge.get_name(),
        }

    def get_element(self) -> ET.Element:
        """Returns the ElementTree representation of the EntityTrigger.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the EntityTrigger.
        """
        condition = ET.Element("Condition", attrib=self.get_attributes())
        byentity = ET.SubElement(condition, "ByEntityCondition")
        byentity.append(self.triggerentity.get_element())
        byentity.append(self.entitycondition.get_element())

        if self._used_by_parent:
            return condition
        # Could create a new Trigger ConditionGroup here, but went with
        # this solution for now.
        element = ET.Element(self._triggerpoint)
        condgroup = ET.SubElement(element, "ConditionGroup")
        condgroup.append(condition)
        return element
        condition = ET.Element("Condition", attrib=self.get_attributes())
        byentity = ET.SubElement(condition, "ByEntityCondition")
        byentity.append(self.triggerentity.get_element())
        byentity.append(self.entitycondition.get_element())

        if self._used_by_parent:
            return condition
        # could create a new Trigger ConditionGroup here, but went with this solution for now
        element = ET.Element(self._triggerpoint)
        condgroup = ET.SubElement(element, "ConditionGroup")
        condgroup.append(condition)
        return element


class ValueTrigger(_TriggerType):
    """The ValueTrigger creates a Trigger of the type ValueTrigger of
    openscenario.

    Parameters
    ----------
    name : str
        Name of the trigger.
    delay : float
        The delay of the trigger.
    conditionedge : ConditionEdge
        On what condition edge the trigger should act.
    valuecondition : _ValueTriggerType
        A value condition.
    triggeringentity : str
        The entity of the trigger.
    triggeringrule : str, optional
        Rule of the trigger. Default is 'any'.
    triggeringpoint : str, optional
        Start or stop. Default is 'start'.

    Attributes
    ----------
    name : str
        Name of the trigger.
    delay : float
        The delay of the trigger.
    conditionedge : ConditionEdge
        The condition edge.
    valuecondition : _ValueTriggerType
        The value condition.
    triggerentity : TriggeringEntities
        The triggering entity.

    Methods
    -------
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        name: str,
        delay: float,
        conditionedge: ConditionEdge,
        valuecondition: _ValueTriggerType,
        triggeringpoint: str = "start",
    ) -> None:
        """Initialize the ValueTrigger.

        Parameters
        ----------
        name : str
            Name of the trigger.
        delay : float
            The delay of the trigger.
        conditionedge : ConditionEdge
            On what condition edge the trigger should act.
        valuecondition : _ValueTriggerType
            A value condition.
        triggeringentity : str
            The entity of the trigger.
        triggeringrule : str, optional
            Rule of the trigger. Default is 'any'.
        triggeringpoint : str, optional
            Start or stop. Default is 'start'.
        """
        self.name = name
        if triggeringpoint not in ["start", "stop"]:
            raise ValueError(
                "not a valid triggering point, valid start or stop"
            )
        if triggeringpoint == "start":
            self._triggerpoint = "StartTrigger"
        else:
            self._triggerpoint = "StopTrigger"

        self.delay = convert_float(delay)
        self.conditionedge = convert_enum(conditionedge, ConditionEdge)
        if not isinstance(valuecondition, _ValueTriggerType):
            raise TypeError("entitycondition is not a valid EntityCondition")
        self.valuecondition = valuecondition
        self._used_by_parent = False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ValueTrigger):
            if (
                self.get_attributes() == other.get_attributes()
                and self.valuecondition == other.valuecondition
                and self._triggerpoint == other._triggerpoint
            ):
                return True
        elif isinstance(other, Trigger):
            if (
                len(other.conditiongroups) == 1
                and len(other.conditiongroups[0].conditions) == 1
            ):
                if (
                    self._triggerpoint == other._triggerpoint
                    and other.conditiongroups[0].conditions[0] == self
                ):
                    return True
        elif isinstance(other, ConditionGroup):
            if len(other.conditions) == 1:
                if (
                    self._triggerpoint == other._triggerpoint
                    and other.conditions[0] == self
                ):
                    return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "ValueTrigger":
        """Parses the XML element of ValueTrigger.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        ValueTrigger
            A ValueTrigger object.

        Notes
        -----
        This parser will ONLY parse the Condition itself, not the
        ConditionGroup or Trigger that it can generate.

        Raises
        ------
        NotAValidElement
        """
        if element.tag != "Condition":
            raise NotAValidElement(
                "ValueTrigger only parses a Condition, not ", element
            )

        name = element.attrib["name"]
        delay = convert_float(element.attrib["delay"])
        conditionedge = convert_enum(
            element.attrib["conditionEdge"], ConditionEdge
        )
        condition = _ValueConditionFactory.parse_value_condition(
            find_mandatory_field(element, "ByValueCondition")
        )
        return ValueTrigger(name, delay, conditionedge, condition)

    def _set_used_by_parent(self) -> None:
        """Set the condition as used by a parent ConditionGroup.

        This method is used internally when the condition is added to a
        ConditionGroup.
        """
        self._used_by_parent = True

    def get_attributes(self) -> dict[str, str]:
        """Get the attributes of the LaneOffsetAction as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the LaneOffsetAction.
        """
        return {
            "name": self.name,
            "delay": str(self.delay),
            "conditionEdge": self.conditionedge.get_name(),
        }

    def get_element(self) -> ET.Element:
        """Get the ElementTree representation of the LaneOffsetAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the LaneOffsetAction.
        """
        condition = ET.Element("Condition", attrib=self.get_attributes())
        byvalue = ET.SubElement(condition, "ByValueCondition")
        byvalue.append(self.valuecondition.get_element())
        if self._used_by_parent:
            return condition
        # could create a new Trigger ConditionGroup here, but went with this solution for now
        element = ET.Element(self._triggerpoint)
        condgroup = ET.SubElement(element, "ConditionGroup")
        condgroup.append(condition)
        return element


class ConditionGroup(_TriggerType):
    """The ConditionGroup class creates a Trigger that can be used if multiple
    Conditions are wanted. The ConditionGroups act like an "AND" logic for all
    added conditions.

    Parameters
    ----------
    triggeringpoint : str, optional
        Start or stop (not needed if used with the Trigger class).
        Default is 'start'.

    Attributes
    ----------
    triggeringpoint : str
        Start or stop.
    conditions : list of EntityTriggers and ValueTriggers
        A list of all conditions.

    Methods
    -------
    get_element()
        Returns the full ElementTree of the class.
    add_condition(condition)
        Adds a condition to the ConditionGroup.
    """

    def __init__(self, triggeringpoint: str = "start") -> None:
        """Initialize the ConditionGroup.

        Parameters
        ----------
        triggeringpoint : str
            Start or stop.
        """
        if triggeringpoint not in ["start", "stop"]:
            raise ValueError(
                "not a valid triggering point, valid start or stop"
            )
        if triggeringpoint == "start":
            self._triggerpoint = "StartTrigger"
        else:
            self._triggerpoint = "StopTrigger"
        self.conditions = []
        self._used_by_parent = False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ConditionGroup):
            if (
                self.conditions == other.conditions
                and self._triggerpoint == other._triggerpoint
            ):
                return True
        elif isinstance(other, Trigger):
            if len(other.conditiongroups) == 1:
                if (
                    self._triggerpoint == other._triggerpoint
                    and other.conditiongroups[0] == self
                ):
                    return True
        elif isinstance(other, (EntityTrigger, ValueTrigger)):
            if len(self.conditions) == 1:
                if (
                    self._triggerpoint == other._triggerpoint
                    and self.conditions[0] == other
                ):
                    return True

        return False

    @staticmethod
    def parse(element: ET.Element) -> "ConditionGroup":
        """Parse the XML element of ConditionGroup.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        ConditionGroup
            A ConditionGroup object.
        """

        condgr = ConditionGroup()
        conditions = element.findall("Condition")
        for cond in conditions:
            condgr.add_condition(_ConditionFactory().parse_condition(cond))

        return condgr

    def add_condition(
        self, condition: Union[EntityTrigger, ValueTrigger]
    ) -> "ConditionGroup":
        """Adds a condition (EntityTrigger or ValueTrigger) to the
        ConditionGroup.

        Parameters
        ----------
        condition : Union[EntityTrigger, ValueTrigger]
            A condition to add to the ConditionGroup.
        """
        if not isinstance(condition, (EntityTrigger, ValueTrigger)):
            raise TypeError(
                "condition input not of type EntityTrigger or ValueTrigger"
            )
        condition._set_used_by_parent()
        condition._triggerpoint = self._triggerpoint
        self.conditions.append(condition)
        self._used_by_parent = False
        return self

    def _set_used_by_parent(self) -> None:
        """Set the condition group as used by a parent Trigger.

        This method is used internally when the condition group is added
        to a Trigger.
        """
        self._used_by_parent = True
        for cond in self.conditions:
            cond._triggerpoint = self._triggerpoint

    def get_element(self) -> ET.Element:
        """Constructs and returns an XML element representation of the
        ConditionGroup.

        Returns
        -------
        ET.Element
            An XML element representing the ConditionGroup. If the
            ConditionGroup is used by a parent, it directly returns
            the ConditionGroup element. Otherwise, it wraps the
            ConditionGroup in a parent trigger element.

        Raises
        ------
        ValueError
            If no conditions were added to the ConditionGroup.
        """

        if not self.conditions:
            raise ValueError("No conditions were added to the ConditionGroup")
        condgroup = ET.Element("ConditionGroup")

        for c in self.conditions:
            condgroup.append(c.get_element())

        if self._used_by_parent:
            return condgroup
        # could create a new Trigger here, but went with this solution for now
        element = ET.Element(self._triggerpoint)
        element.append(condgroup)
        return element


class Trigger(_TriggerType):
    """The Trigger class creates a Trigger that can be used if multiple
    ConditionGroups are wanted. The Trigger acts like an "OR" logic for all
    added ConditionGroups.

    Parameters
    ----------
    triggeringpoint : str, optional
        Start or stop. Default is "start".

    Attributes
    ----------
    triggeringpoint : str
        Start or stop.
    conditiongroups : list of ConditionGroup
        A list of all conditiongroups.

    Methods
    -------
    get_element()
        Returns the full ElementTree of the class.
    add_conditiongroup(conditiongroup)
        Adds a conditiongroup to the trigger.
    """

    def __init__(self, triggeringpoint: str = "start") -> None:
        """Initialize the Trigger.

        Parameters
        ----------
        triggeringpoint : str, optional
            Start or stop. Default is "start".
        """
        if triggeringpoint not in ["start", "stop"]:
            raise ValueError(
                "not a valid triggering point, valid start or stop"
            )
        if triggeringpoint == "start":
            self._triggerpoint = "StartTrigger"
        else:
            self._triggerpoint = "StopTrigger"
        self.conditiongroups = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Trigger):
            if (
                self.conditiongroups == other.conditiongroups
                and self._triggerpoint == other._triggerpoint
            ):
                return True
        elif isinstance(other, (EntityTrigger, ValueTrigger)):
            if (
                len(self.conditiongroups) == 1
                and len(self.conditiongroups[0].conditions) == 1
            ):
                if (
                    self._triggerpoint == other._triggerpoint
                    and self.conditiongroups[0].conditions[0] == other
                ):
                    return True
        elif isinstance(other, ConditionGroup):
            if len(self.conditiongroups) == 1:
                if (
                    self._triggerpoint == other._triggerpoint
                    and self.conditiongroups[0] == other
                ):
                    return True
        elif isinstance(other, EmptyTrigger):
            if (
                len(self.conditiongroups) == 0
                and self._triggerpoint == other._triggerpoint
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "Trigger":
        """Parse the XML element of ConditionGroup.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        ConditionGroup
            A ConditionGroup object.
        """

        trigger = Trigger()
        trigger._triggerpoint = element.tag

        conditiongroups = element.findall("ConditionGroup")
        for condgr in conditiongroups:
            tmp_condgr = ConditionGroup.parse(condgr)
            tmp_condgr._triggerpoint = trigger._triggerpoint
            for cond in tmp_condgr.conditions:
                cond._triggerpoint = trigger._triggerpoint
            trigger.add_conditiongroup(tmp_condgr)

        return trigger

    def add_conditiongroup(self, conditiongroup: ConditionGroup) -> "Trigger":
        """Add a condition group to the trigger.

        Parameters
        ----------
        conditiongroup : ConditionGroup
            A condition group to add to the trigger.

        Returns
        -------
        Trigger
            The updated Trigger object.
        """
        if not isinstance(conditiongroup, ConditionGroup):
            raise TypeError("conditiongroup input not of type ConditionGroup")
        conditiongroup._triggerpoint = self._triggerpoint
        conditiongroup._set_used_by_parent()

        self.conditiongroups.append(conditiongroup)
        return self

    def get_element(self) -> ET.Element:
        """Generate an XML element representation of the Trigger.

        Returns
        -------
        ET.Element
            An XML element containing the trigger point and its associated
            condition groups.
        """
        """Returns the elementTree of the Trigger."""
        element = ET.Element(self._triggerpoint)
        for c in self.conditiongroups:
            element.append(c.get_element())
        return element


class TriggeringEntities(VersionBase):
    """The TriggeringEntities class is used by Value and Entity Triggers to
    define the trigger entity.

    Parameters
    ----------
    triggeringrule : TriggeringEntitiesRule
        Rule specifying 'all' or 'any'.

    Attributes
    ----------
    entity : list of EntityRef
        Reference to the entity.
    triggeringrule : TriggeringEntitiesRule
        Rule specifying 'all' or 'any'.

    Methods
    -------
    add_entity(entity)
        Adds an EntityRef to the triggering entities.
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, triggeringrule: TriggeringEntitiesRule) -> None:
        """Initialize the TriggeringEntities.

        Parameters
        ----------
        entity : TriggeringEntitiesRule
            Name of the entity.
        triggeringrule : str
            Specifies 'all' or 'any'.
        """
        self.entity = []
        self.triggeringrule = convert_enum(
            triggeringrule, TriggeringEntitiesRule
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TriggeringEntities):
            if (
                self.get_attributes() == other.get_attributes()
                and self.entity == other.entity
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TriggeringEntities":
        """Parse the XML element of TriggeringEntities.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        TriggeringEntities
            A TriggeringEntities object.
        """

        rule = convert_enum(
            element.attrib["triggeringEntitiesRule"], TriggeringEntitiesRule
        )
        triggeringentities = TriggeringEntities(rule)
        entrefs = element.findall("EntityRef")
        for ent in entrefs:
            entityref = EntityRef.parse(ent)
            triggeringentities.add_entity(entityref.entity)
        return triggeringentities

    def add_entity(self, entity: str) -> "TriggeringEntities":
        """Add an entity to the TriggeringEntities.

        Parameters
        ----------
        entity : str
            Name of the entity to add.
        """
        self.entity.append(EntityRef(entity))
        return self

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the LaneOffsetAction as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the LaneOffsetAction.
        """
        return {"triggeringEntitiesRule": self.triggeringrule.get_name()}

    def get_element(self) -> ET.Element:
        """Constructs and returns an XML element representation of the
        LaneOffsetAction.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the LaneOffsetAction.
        """
        element = ET.Element(
            "TriggeringEntities", attrib=self.get_attributes()
        )
        if len(self.entity) == 0:
            raise NotEnoughInputArguments(
                "No TriggereingEntities has been added"
            )

        for ent in self.entity:
            element.append(ent.get_element())
        return element


""" Entity conditions


"""


class EndOfRoadCondition(_EntityTriggerType):
    """The EndOfRoadCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    duration : float
        The duration at the end of the road.

    Attributes
    ----------
    duration : float
        The duration at the end of the road.

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

    def __init__(self, duration: float) -> None:
        """Initialize the EndOfRoadCondition.

        Parameters
        ----------
        duration : float
            The duration after the condition.
        """
        self.duration = convert_float(duration)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EndOfRoadCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "EndOfRoadCondition":
        """Parses the xml element of EndOfRoadCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        EndOfRoadCondition
            An EndOfRoadCondition object.
        """
        condition = find_mandatory_field(element, "EndOfRoadCondition")
        duration = convert_float(condition.attrib["duration"])
        return EndOfRoadCondition(duration)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the EndOfRoadCondition as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the EndOfRoadCondition.
        """
        return {"duration": str(self.duration)}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the EndOfRoadCondition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the EndOfRoadCondition.
        """
        element = ET.Element("EntityCondition")
        ET.SubElement(
            element, "EndOfRoadCondition", attrib=self.get_attributes()
        )
        return element


class CollisionCondition(_EntityTriggerType):
    """The CollisionCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    entity : Union[str, ObjectType]
        Name of the entity to collide with.

    Attributes
    ----------
    entity : Union[str, ObjectType]
        Name of the entity to collide with.

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

    def __init__(self, entity: Union[str, ObjectType]) -> None:
        """The CollisionCondition class is an Entity Condition used by the
        EntityTrigger.

        Parameters
        ----------
        entity : Union[str, ObjectType]
            Name of the entity to collide with.
        """
        self.entity = entity
        if not isinstance(self.entity, str):
            self.entity = convert_enum(self.entity, ObjectType)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CollisionCondition):
            if self.entity == other.entity:
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "CollisionCondition":
        """Parses the xml element of CollisionCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        CollisionCondition
            A CollisionCondition object.
        """
        condition = find_mandatory_field(element, "CollisionCondition")
        bytype = condition.find("ByType")
        if bytype is not None:
            entity = convert_enum(bytype.attrib["type"], ObjectType)
        else:
            entityref = EntityRef.parse(
                find_mandatory_field(condition, "EntityRef")
            )
            entity = entityref.entity
        return CollisionCondition(entity)

    def get_element(self) -> ET.Element:
        """Generate an XML element representing a CollisionCondition.

        Returns
        -------
        ET.Element
            The root XML element for the CollisionCondition.
        """
        element = ET.Element("EntityCondition")
        colcond = ET.SubElement(element, "CollisionCondition")
        if isinstance(self.entity, str):
            colcond.append(EntityRef(self.entity).get_element())
        else:
            ET.SubElement(colcond, "ByType", {"type": self.entity.get_name()})
        return element


class OffroadCondition(_EntityTriggerType):
    """The OffroadCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    duration : float
        The duration of offroad.

    Attributes
    ----------
    duration : float
        The duration of offroad.

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

    def __init__(self, duration: float) -> None:
        """Initialize the OffroadCondition.

        Parameters
        ----------
        duration : float
            The duration of offroad.
        """
        self.duration = convert_float(duration)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, OffroadCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "OffroadCondition":
        """Parses the xml element of OffroadCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        OffroadCondition
            An OffroadCondition object.
        """
        condition = find_mandatory_field(element, "OffroadCondition")
        duration = convert_float(condition.attrib["duration"])
        return OffroadCondition(duration)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the OffroadCondition as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the OffroadCondition.
        """
        return {"duration": str(self.duration)}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the OffroadCondition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the OffroadCondition.
        """
        element = ET.Element("EntityCondition")
        ET.SubElement(
            element, "OffroadCondition", attrib=self.get_attributes()
        )
        return element


class TimeHeadwayCondition(_EntityTriggerType):
    """The TimeHeadwayCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
        entity (str): name of the entity for the headway

        value (float): time of headway

        rule (Rule): condition rule of triggering

        alongroute (bool): if the route should count
            Default: True

        freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
            Default: True

        distance_type (RelativeDistanceType): how the relative distance should be calculated (valid from V1.1)
            Default: RelativeDistanceType.longitudinal

        coordinate_system (CoordinateSystem): what coordinate system to use for the relative distance (valid from V1.1)
            Default: CoordinateSystem.road

        routing_algorithm (RoutingAlgorithm): the routing algorithm for the condition (valid from V1.2)
            Default: None

    Attributes
    ----------
        entity (str): name of the entity for the headway

        value (float): time of headway

        rule (Rule): condition rule of triggering

        alongroute (bool): if the route should count

        freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

        distance_type (RelativeDistanceType): how the relative distance should be calculated (valid from V1.1)

        coordinate_system (CoordinateSystem): what coordinate system to use for the relative distance (valid from V1.1)

        routing_algorithm (RoutingAlgorithm): the routing algorithm for the condition (valid from V1.2)

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
        entity: str,
        value: float,
        rule: Rule,
        alongroute: bool = True,
        freespace: bool = True,
        distance_type: RelativeDistanceType = RelativeDistanceType.longitudinal,
        coordinate_system: CoordinateSystem = CoordinateSystem.road,
        routing_algorithm: Union[RoutingAlgorithm, None] = None,
    ) -> None:
        """Initalize the TimeHeadwayCondition.

        Parameters
        ----------
            entity (str): name of the entity for the headway

            value (float): time of headway

            rule (Rule): condition rule of triggering

            alongroute (bool): if the route should count
                Default: True

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            distance_type (RelativeDistanceType): how the relative distance should be calculated (valid from V1.1)
                Default: RelativeDistanceType.longitudinal

            coordinate_system (CoordinateSystem): what coordinate system to use for the relative distance (valid from V1.1)
                Default: CoordinateSystem.road

            routing_algorithm (RoutingAlgorithm): the routing algorithm for the condition (valid from V1.2)
                Default: None
        """
        self.entity = entity
        self.value = convert_float(value)
        self.alongroute = convert_bool(alongroute)
        self.freespace = convert_bool(freespace)
        self.rule = convert_enum(rule, Rule)
        self.relative_distance_type = convert_enum(
            distance_type, RelativeDistanceType
        )
        self.coordinate_system = convert_enum(
            coordinate_system, CoordinateSystem
        )
        self.routing_algorithm = convert_enum(
            routing_algorithm, RoutingAlgorithm, True
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TimeHeadwayCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TimeHeadwayCondition":
        """Parses the xml element of TimeHeadwayCondition.

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A position element (same as generated by the class itself)

        Returns
        -------
            condition (TimeHeadwayCondition): a TimeHeadwayCondition object
        """
        condition = find_mandatory_field(element, "TimeHeadwayCondition")
        entity = condition.attrib["entityRef"]
        value = condition.attrib["value"]
        rule = getattr(Rule, condition.attrib["rule"])
        routing_algorithm = None
        if "alongRoute" in condition.attrib:
            alongroute = convert_bool(condition.attrib["alongRoute"])
        else:
            alongroute = True

        if "relativeDistanceType" in condition.attrib:
            reldisttype = convert_enum(
                condition.attrib["relativeDistanceType"], RelativeDistanceType
            )
        else:
            reldisttype = RelativeDistanceType.longitudinal

        if "coordinateSystem" in condition.attrib:
            coordsystem = convert_enum(
                condition.attrib["coordinateSystem"], CoordinateSystem
            )
        else:
            coordsystem = CoordinateSystem.road
        freespace = convert_bool(condition.attrib["freespace"])

        if "routingAlgorithm" in condition.attrib:
            routing_algorithm = convert_enum(
                condition.attrib["routingAlgorithm"], RoutingAlgorithm
            )
        return TimeHeadwayCondition(
            entity,
            value,
            rule,
            alongroute,
            freespace,
            reldisttype,
            coordsystem,
            routing_algorithm,
        )

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the TimeHeadwayCondition as a dict."""
        basedict = {}
        basedict["entityRef"] = self.entity
        basedict["value"] = str(self.value)
        if self.isVersion(minor=0):
            basedict["alongRoute"] = get_bool_string(self.alongroute)
        else:
            basedict["relativeDistanceType"] = (
                self.relative_distance_type.get_name()
            )
            basedict["coordinateSystem"] = self.coordinate_system.get_name()
        basedict["freespace"] = get_bool_string(self.freespace)
        basedict["rule"] = self.rule.get_name()
        if self.routing_algorithm:
            if self.version_minor < 2:
                raise OpenSCENARIOVersionError(
                    "RoutingAlgorithm in TimeHeadwayCondition was added in OSC V1.2"
                )
            basedict["routingAlgorithm"] = self.routing_algorithm.get_name()
        return basedict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the TimeHeadwayCondition."""
        element = ET.Element("EntityCondition")
        ET.SubElement(
            element, "TimeHeadwayCondition", attrib=self.get_attributes()
        )
        return element


class TimeToCollisionCondition(_EntityTriggerType):
    """The TimeToCollisionCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    value : float
        Time to collision.
    rule : Rule
        Condition rule of triggering.
    alongroute : bool, optional
        If the route should count. Default is True.
    freespace : bool, optional
        If True, distance between bounding boxes is used. If False,
        distance between reference points is used. Default is True.
    entity : str, optional
        The entity to trigger collision on.
    position : *Position, optional
        A position for collision.
    distance_type : RelativeDistanceType, optional
        How the relative distance should be calculated (valid from
        V1.1). Default is RelativeDistanceType.longitudinal.
    coordinate_system : CoordinateSystem, optional
        What coordinate system to use for the relative distance
        (valid from V1.1). Default is CoordinateSystem.road.
    routing_algorithm : RoutingAlgorithm, optional
        The routing algorithm for the condition (valid from V1.2).
        Default is None.

    Attributes
    ----------
    value : float
        Time before collision.
    rule : Rule
        Condition rule of triggering.
    alongroute : bool
        If the route should count. Default is True.
    freespace : bool
        If True, distance between bounding boxes is used. If False,
        distance between reference points is used. Default is True.
    entity : EntityRef, optional
        Entity for the collision.
    position : *Position, optional
        A position for collision.
    distance_type : RelativeDistanceType
        How the relative distance should be calculated (valid from
        V1.1).
    coordinate_system : CoordinateSystem
        What coordinate system to use for the relative distance
        (valid from V1.1).
    routing_algorithm : RoutingAlgorithm, optional
        The routing algorithm for the condition (valid from V1.2).

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
        rule: Rule,
        alongroute: bool = True,
        freespace: bool = True,
        entity: Union[str, None] = None,
        position: Union[_PositionType, None] = None,
        distance_type: RelativeDistanceType = RelativeDistanceType.longitudinal,
        coordinate_system: CoordinateSystem = CoordinateSystem.road,
        routing_algorithm: Union[RoutingAlgorithm, None] = None,
    ) -> None:
        """Initialize the TimeToCollisionCondition.

        Parameters
        ----------
        value : float
            Time to collision.
        rule : Rule
            Condition rule of triggering.
        alongroute : bool, optional
            If the route should count. Default is True.
        freespace : bool, optional
            If True, distance between bounding boxes is used. If False,
            distance between reference points is used. Default is True.
        entity : str, optional
            The entity to trigger collision on.
        position : *Position, optional
            A position for collision.
        distance_type : RelativeDistanceType, optional
            How the relative distance should be calculated (valid from
            V1.1). Default is RelativeDistanceType.longitudinal.
        coordinate_system : CoordinateSystem, optional
            What coordinate system to use for the relative distance
            (valid from V1.1). Default is CoordinateSystem.road.
        routing_algorithm : RoutingAlgorithm, optional
            The routing algorithm for the condition (valid from V1.2).
            Default is None.
        """
        self.value = convert_float(value)
        self.freespace = convert_bool(freespace)
        self.alongroute = convert_bool(alongroute)
        self.rule = convert_enum(rule, Rule)
        self.use_entity = None
        if (entity is not None) and (position is not None):
            raise ToManyOptionalArguments(
                "Can only have either entity of position, not both"
            )
        if entity:
            self.entity = EntityRef(entity)
            self.use_entity = True
        if position:
            if not isinstance(position, _PositionType):
                raise TypeError("input position is not a valid Position")
            self.position = position
            self.use_entity = False

        if self.use_entity is None:
            raise ValueError("neither position or entity was set.")

        self.relative_distance_type = convert_enum(
            distance_type, RelativeDistanceType
        )
        self.coordinate_system = convert_enum(
            coordinate_system, CoordinateSystem
        )
        self.routing_algorithm = convert_enum(
            routing_algorithm, RoutingAlgorithm, True
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TimeToCollisionCondition):
            if self.get_attributes() == other.get_attributes():
                if (
                    self.use_entity
                    and other.use_entity
                    and self.entity
                    and other.entity
                ) or (
                    not self.use_entity
                    and not other.use_entity
                    and self.position
                    and other.position
                ):
                    return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TimeToCollisionCondition":
        """Parse the XML element of TimeToCollisionCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        TimeToCollisionCondition
            A TimeToCollisionCondition object.
        """
        condition = find_mandatory_field(element, "TimeToCollisionCondition")
        value = condition.attrib["value"]
        rule = convert_enum(condition.attrib["rule"], Rule)
        freespace = convert_bool(condition.attrib["freespace"])
        routing_algorithm = None
        if "alongRoute" in condition.attrib:
            alongroute = convert_bool(condition.attrib["alongRoute"])
        else:
            alongroute = True

        if "relativeDistanceType" in condition.attrib:
            reldisttype = convert_enum(
                condition.attrib["relativeDistanceType"], RelativeDistanceType
            )
        else:
            reldisttype = RelativeDistanceType.longitudinal

        if "coordinateSystem" in condition.attrib:
            coordsystem = convert_enum(
                condition.attrib["coordinateSystem"], CoordinateSystem
            )
        else:
            coordsystem = CoordinateSystem.road
        entity = None
        position = None
        if (
            condition.find("TimeToCollisionConditionTarget/EntityRef")
            is not None
        ):
            entityref = EntityRef.parse(
                find_mandatory_field(
                    condition, "TimeToCollisionConditionTarget/EntityRef"
                )
            )
            entity = entityref.entity
        elif (
            condition.find("TimeToCollisionConditionTarget/Position")
            is not None
        ):
            position = _PositionFactory.parse_position(
                find_mandatory_field(
                    condition, "TimeToCollisionConditionTarget/Position"
                )
            )
        else:
            raise ValueError(
                "No TimeToCollisionConditionTarget found while parsing TimeToCollisionCondition."
            )
        if "routingAlgorithm" in condition.attrib:
            routing_algorithm = convert_enum(
                condition.attrib["routingAlgorithm"], RoutingAlgorithm
            )
        return TimeToCollisionCondition(
            value,
            rule,
            alongroute,
            freespace,
            entity,
            position,
            reldisttype,
            coordsystem,
            routing_algorithm,
        )

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the TimeToCollisionCondition as a dict.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the
            TimeToCollisionCondition.
        """
        basedict = {}
        basedict["value"] = str(self.value)
        if self.isVersion(minor=0):
            basedict["alongRoute"] = get_bool_string(self.alongroute)
        else:
            basedict["relativeDistanceType"] = self.relative_distance_type.name
            basedict["coordinateSystem"] = self.coordinate_system.name
        basedict["freespace"] = get_bool_string(self.freespace)
        basedict["rule"] = self.rule.get_name()
        if self.routing_algorithm:
            if self.version_minor < 2:
                raise OpenSCENARIOVersionError(
                    "RoutingAlgorithm in TimeHeadwayCondition was added in OSC V1.2"
                )
            basedict["routingAlgorithm"] = self.routing_algorithm.get_name()
        return basedict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the TimeToCollisionCondition.

        Returns
        -------
        ET.Element
            The XML element representing the TimeToCollisionCondition.
        """
        element = ET.Element("EntityCondition")
        collisionevent = ET.SubElement(
            element, "TimeToCollisionCondition", attrib=self.get_attributes()
        )

        targetelement = ET.SubElement(
            collisionevent, "TimeToCollisionConditionTarget"
        )

        if self.use_entity:
            targetelement.append(self.entity.get_element())
        else:
            targetelement.append(self.position.get_element())

        return element


class AccelerationCondition(_EntityTriggerType):
    """The AccelerationCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    value : float
        Acceleration value.
    rule : Rule
        Condition rule of triggering.
    direction : DirectionalDimension, optional
        Direction of the acceleration. If not given, the total
        acceleration is considered. Default is None.

    Attributes
    ----------
    value : float
        Acceleration value.
    rule : Rule
        Condition rule of triggering.
    direction : DirectionalDimension, optional
        Direction of the acceleration. If not given, the total
        acceleration is considered.

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
        rule: Rule,
        direction: Union[DirectionalDimension, None] = None,
    ) -> None:
        """The AccelerationCondition class is an Entity Condition used by the
        EntityTrigger.

        Parameters
        ----------
        value : float
            Acceleration value.
        rule : Rule
            Condition rule of triggering.
        direction : DirectionalDimension, optional
            Direction of the acceleration. If not given, the total
            acceleration is considered. Valid since OSC 1.2.
        """
        self.value = convert_float(value)
        self.rule = convert_enum(rule, Rule)
        self.direction = convert_enum(direction, DirectionalDimension, True)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AccelerationCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "AccelerationCondition":
        """Parse the XML element of AccelerationCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        AccelerationCondition
            An AccelerationCondition object.
        """
        direction = None
        condition = find_mandatory_field(element, "AccelerationCondition")
        value = convert_float(condition.attrib["value"])
        rule = convert_enum(condition.attrib["rule"], Rule)
        if "direction" in condition.attrib:
            direction = convert_enum(
                condition.attrib["direction"], DirectionalDimension
            )
        return AccelerationCondition(value, rule, direction)

    def get_attributes(self) -> dict[str, str]:
        """Retrieves the attributes of the AccelerationCondition as a
        dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the AccelerationCondition.
            Keys include 'value', 'rule', and optionally 'direction' if the
            version supports it.

        Raises
        ------
        OpenSCENARIOVersionError
            If the 'direction' attribute is accessed in a version earlier
            than OpenSCENARIO 1.2.
        """
        retdict = {}
        retdict["value"] = str(self.value)
        retdict["rule"] = self.rule.get_name()
        if self.direction is not None:
            if self.isVersionEqLess(minor=1):
                raise OpenSCENARIOVersionError(
                    "Direction was introduced in OSC 1.2"
                )
            retdict["direction"] = self.direction.get_name()
        return retdict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the AccelerationCondition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the AccelerationCondition.
        """
        element = ET.Element("EntityCondition")
        ET.SubElement(
            element, "AccelerationCondition", attrib=self.get_attributes()
        )
        return element


class StandStillCondition(_EntityTriggerType):
    """The StandStillCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    duration : float
        Time of standstill.

    Attributes
    ----------
    duration : float
        Time of standstill.

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

    def __init__(self, duration: float):
        """The StandStillCondition class is an Entity Condition used by the
        EntityTrigger.

        Parameters
        ----------
        duration : float
            Time of standstill.
        """
        self.duration = convert_float(duration)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, StandStillCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "StandStillCondition":
        """Parse the XML element of StandStillCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        StandStillCondition
            A StandStillCondition object.
        """
        condition = find_mandatory_field(element, "StandStillCondition")
        duration = convert_float(condition.attrib["duration"])
        return StandStillCondition(duration)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the StandStillCondition as a dict.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the
            StandStillCondition.
        """
        return {"duration": str(self.duration)}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the StandStillCondition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the StandStillCondition.
        """
        element = ET.Element("EntityCondition")
        ET.SubElement(
            element, "StandStillCondition", attrib=self.get_attributes()
        )
        return element


class SpeedCondition(_EntityTriggerType):
    """The SpeedCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    value : float
        Speed to trigger on.
    rule : Rule
        Condition rule of triggering.
    directional_dimension : DirectionalDimension, optional
        Direction of the speed to compare. If not used, total speed
        is considered. Default is None.

    Attributes
    ----------
    value : float
        Speed to trigger on.
    rule : Rule
        Condition rule of triggering.
    directional_dimension : DirectionalDimension, optional
        Direction of the speed to compare. If not used, total speed
        is considered.

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
        rule: Rule,
        directional_dimension: Union[DirectionalDimension, None] = None,
    ) -> None:
        """Initialize the SpeedCondition class.

        Parameters
        ----------
        value : float
            Speed to trigger on.
        rule : Rule
            Condition rule of triggering.
        directional_dimension : DirectionalDimension, optional
            Direction of the speed to compare. If not used, total speed
            is considered. Default is None.
        """
        self.value = convert_float(value)
        self.rule = convert_enum(rule, Rule)
        self.directional_dimension = convert_enum(
            directional_dimension, DirectionalDimension, True
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SpeedCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "SpeedCondition":
        """Parse the XML element of SpeedCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        SpeedCondition
            A SpeedCondition object.
        """
        condition = find_mandatory_field(element, "SpeedCondition")
        value = convert_float(condition.attrib["value"])
        rule = convert_enum(condition.attrib["rule"], Rule)
        direction = None
        if "direction" in condition.attrib:
            direction = convert_enum(
                condition.attrib["direction"], DirectionalDimension
            )
        return SpeedCondition(value, rule, direction)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the SpeedCondition as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the SpeedCondition.
        """
        basedict = {}
        basedict["value"] = str(self.value)
        basedict["rule"] = self.rule.get_name()
        if self.directional_dimension is not None:
            if self.isVersionEqLess(minor=1):
                raise OpenSCENARIOVersionError(
                    "Direction was introduced in OSC 1.2"
                )
            basedict["direction"] = self.directional_dimension.get_name()
        return basedict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the SpeedCondition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the SpeedCondition.
        """
        element = ET.Element("EntityCondition")
        ET.SubElement(element, "SpeedCondition", attrib=self.get_attributes())
        return element


class RelativeSpeedCondition(_EntityTriggerType):
    """The RelativeSpeedCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    value : float
        Acceleration value.
    rule : Rule
        Condition rule of triggering.
    entity : str
        Name of the entity to be relative to.
    directional_dimension : DirectionalDimension, optional
        Direction of the speed to compare. If not used, total speed is
        considered. Default is None.

    Attributes
    ----------
    value : float
        Acceleration value.
    rule : Rule
        Condition rule of triggering.
    entity : str
        Name of the entity to be relative to.
    directional_dimension : DirectionalDimension, optional
        Direction of the speed to compare. If not used, total speed is
        considered.

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
        rule: Rule,
        entity: str,
        directional_dimension: Union[DirectionalDimension, None] = None,
    ) -> None:
        """Initialize the RelativeSpeedCondition.

        Parameters
        ----------
        value : float
            Acceleration value.
        rule : Rule
            Condition rule of triggering.
        entity : str
            Name of the entity to be relative to.
        directional_dimension : DirectionalDimension, optional
            Direction of the speed to compare. If not used, total speed
            is considered. Default is None.
        """
        self.value = convert_float(value)
        self.rule = convert_enum(rule, Rule)
        self.entity = entity
        self.directional_dimension = convert_enum(
            directional_dimension, DirectionalDimension, True
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RelativeSpeedCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RelativeSpeedCondition":
        """Parse the XML element of RelativeSpeedCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RelativeSpeedCondition
            A RelativeSpeedCondition object.
        """
        condition = find_mandatory_field(element, "RelativeSpeedCondition")
        value = convert_float(condition.attrib["value"])
        entity = condition.attrib["entityRef"]
        rule = convert_enum(condition.attrib["rule"], Rule)
        direction = None
        if "direction" in condition.attrib:
            direction = convert_enum(
                condition.attrib["direction"], DirectionalDimension
            )
        return RelativeSpeedCondition(value, rule, entity, direction)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the RelativeSpeedCondition as a
        dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the
            RelativeSpeedCondition.

        Raises
        ------
        OpenSCENARIOVersionError
            If the OSC version is less than 1.2 and the
            directional dimension is specified.
        """

        basedict = {}
        basedict["value"] = str(self.value)
        basedict["rule"] = self.rule.get_name()
        basedict["entityRef"] = self.entity
        if self.directional_dimension is not None:
            if self.isVersionEqLess(minor=1):
                raise OpenSCENARIOVersionError(
                    "Direction was introduced in OSC 1.2"
                )
            basedict["direction"] = self.directional_dimension.get_name()
        return basedict

    def get_element(self) -> ET.Element:
        """Generate an XML element representing a RelativeSpeedCondition.

        Returns
        -------
        ET.Element
            An XML element tree with the structure:
            <EntityCondition>
                <RelativeSpeedCondition ... />
            </EntityCondition>
        """
        """Returns the elementTree of the RelativeSpeedCondition."""
        element = ET.Element("EntityCondition")
        ET.SubElement(
            element, "RelativeSpeedCondition", attrib=self.get_attributes()
        )
        return element


class TraveledDistanceCondition(_EntityTriggerType):
    """The TraveledDistanceCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    value : float
        How far it has traveled.

    Attributes
    ----------
    value : float
        How far it has traveled.

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

    def __init__(self, value: float):
        """The TraveledDistanceCondition class is an Entity Condition used by
        the EntityTrigger.

        Parameters
        ----------
        value : float
            How far it has traveled.
        """
        self.value = convert_float(value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TraveledDistanceCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TraveledDistanceCondition":
        """Parse the XML element of TraveledDistanceCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        TraveledDistanceCondition
            A TraveledDistanceCondition object.
        """
        condition = find_mandatory_field(element, "TraveledDistanceCondition")
        value = convert_float(condition.attrib["value"])
        return TraveledDistanceCondition(value)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the TraveledDistanceCondition as a
        dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the
            TraveledDistanceCondition.
        """
        return {"value": str(self.value)}

    def get_element(self) -> ET.Element:
        """Generate an XML element representing a TraveledDistanceCondition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The root XML element for the EntityCondition, containing
            a TraveledDistanceCondition as a child element.
        """
        """Returns the elementTree of the TraveledDistanceCondition."""
        element = ET.Element("EntityCondition")
        ET.SubElement(
            element, "TraveledDistanceCondition", attrib=self.get_attributes()
        )
        return element


class ReachPositionCondition(_EntityTriggerType):
    """The ReachPositionCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    position : *Position
        Any position to reach.
    tolerance : float
        Tolerance of the position.

    Attributes
    ----------
    position : *Position
        Any position to reach.
    tolerance : float
        Tolerance of the position.

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

    def __init__(self, position: _PositionType, tolerance: float) -> None:
        """Initialize the ReachPositionCondition.

        Parameters
        ----------
        position : *Position
            Any position to reach.
        tolerance : float
            Tolerance of the position.
        """
        if not isinstance(position, _PositionType):
            raise TypeError("position input is not a valid Position")
        self.position = position
        self.tolerance = convert_float(tolerance)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ReachPositionCondition):
            if (
                self.get_attributes() == other.get_attributes()
                and self.position == other.position
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "ReachPositionCondition":
        """Parse the XML element of ReachPositionCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        ReachPositionCondition
            A ReachPositionCondition object.
        """
        condition = find_mandatory_field(element, "ReachPositionCondition")
        tolerance = convert_float(condition.attrib["tolerance"])
        position = _PositionFactory.parse_position(
            find_mandatory_field(condition, "Position")
        )
        return ReachPositionCondition(position, tolerance)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the ReachPositionCondition as a dict.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the
            ReachPositionCondition.
        """
        return {"tolerance": str(self.tolerance)}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the ReachPositionCondition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the ReachPositionCondition.
        """
        element = ET.Element("EntityCondition")
        reachposcond = ET.SubElement(
            element, "ReachPositionCondition", attrib=self.get_attributes()
        )
        reachposcond.append(self.position.get_element())
        if self.isVersionEqLarger(minor=2):
            raise OpenSCENARIOVersionError(
                "ReachPositionCondition is deprecrated, please use DistanceCondition instead"
            )
        return element


class DistanceCondition(_EntityTriggerType):
    """The DistanceCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    value : float
        Distance to position.
    rule : Rule
        Condition rule of triggering.
    position : *Position
        Any position to reach.
    alongroute : bool, optional
        If the route should count (deprecated in V.1.0). Default is True.
    freespace : bool, optional
        If True, distance between bounding boxes is used. If False,
        distance between reference points is used. Default is True.
    distance_type : RelativeDistanceType, optional
        How the relative distance should be calculated (valid from
        V1.1). Default is RelativeDistanceType.longitudinal.
    coordinate_system : CoordinateSystem, optional
        What coordinate system to use for the relative distance (valid
        from V1.1). Default is CoordinateSystem.road.
    routing_algorithm : RoutingAlgorithm, optional
        The routing algorithm to use if a relevant coordinate system is
        used (road/lane). Default is RoutingAlgorithm.undefined.

    Attributes
    ----------
    value : float
        Distance to position.
    rule : Rule
        Condition rule of triggering.
    position : *Position
        Any position to reach.
    alongroute : bool
        If the route should count.
    freespace : bool
        If True, distance between bounding boxes is used. If False,
        distance between reference points is used.
    distance_type : RelativeDistanceType
        How the relative distance should be calculated.
    coordinate_system : CoordinateSystem
        What coordinate system to use for the relative distance.
    routing_algorithm : RoutingAlgorithm
        The routing algorithm to use if a relevant coordinate system is
        used (road/lane).

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
        rule: Rule,
        position: _PositionType,
        alongroute: bool = True,
        freespace: bool = True,
        distance_type: RelativeDistanceType = RelativeDistanceType.longitudinal,
        coordinate_system: CoordinateSystem = CoordinateSystem.road,
        routing_algorithm: Union[RoutingAlgorithm, None] = None,
    ) -> None:
        """Initialize the DistanceCondition.

        Parameters
        ----------
        value : float
            Distance to position.
        rule : Rule
            Condition rule of triggering.
        position : *Position
            Any position to reach.
        alongroute : bool, optional
            If the route should count (deprecated in V.1.0). Default is
            True.
        freespace : bool, optional
            If True, distance between bounding boxes is used. If False,
            distance between reference points is used. Default is True.
        distance_type : RelativeDistanceType, optional
            How the relative distance should be calculated (valid from
            V1.1). Default is RelativeDistanceType.longitudinal.
        coordinate_system : CoordinateSystem, optional
            What coordinate system to use for the relative distance
            (valid from V1.1). Default is CoordinateSystem.road.
        routing_algorithm : RoutingAlgorithm, optional
            The routing algorithm to use if a relevant coordinate system
            is used (road/lane). Default is RoutingAlgorithm.undefined.
        """
        self.value = value
        self.alongroute = convert_bool(alongroute)
        self.freespace = convert_bool(freespace)
        self.rule = convert_enum(rule, Rule)
        if not isinstance(position, _PositionType):
            raise TypeError("position input is not a valid Position")
        self.position = position
        self.relative_distance_type = convert_enum(
            distance_type, RelativeDistanceType
        )
        self.coordinate_system = convert_enum(
            coordinate_system, CoordinateSystem
        )
        self.routing_algorithm = convert_enum(
            routing_algorithm, RoutingAlgorithm, True
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DistanceCondition):
            if (
                self.get_attributes() == other.get_attributes()
                and self.position == other.position
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "DistanceCondition":
        """Parse the XML element of DistanceCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        DistanceCondition
            A DistanceCondition object.
        """
        condition = find_mandatory_field(element, "DistanceCondition")
        value = condition.attrib["value"]
        rule = convert_enum(condition.attrib["rule"], Rule)
        freespace = convert_bool(condition.attrib["freespace"])
        if "alongRoute" in condition.attrib:
            alongroute = convert_bool(condition.attrib["alongRoute"])
        else:
            alongroute = True

        if "relativeDistanceType" in condition.attrib:
            reldisttype = convert_enum(
                condition.attrib["relativeDistanceType"], RelativeDistanceType
            )
        else:
            reldisttype = RelativeDistanceType.longitudinal

        if "coordinateSystem" in condition.attrib:
            coordsystem = convert_enum(
                condition.attrib["coordinateSystem"], CoordinateSystem
            )
        else:
            coordsystem = CoordinateSystem.road

        if "routingAlgorithm" in condition.attrib:
            routing_algorithm = convert_enum(
                condition.attrib["routingAlgorithm"], RoutingAlgorithm
            )
        else:
            routing_algorithm = None
        position = None

        position = _PositionFactory.parse_position(
            find_mandatory_field(condition, "Position")
        )
        return DistanceCondition(
            value,
            rule,
            position,
            alongroute,
            freespace,
            reldisttype,
            coordsystem,
            routing_algorithm,
        )

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the DistanceCondition as a dict.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            DistanceCondition.
        """
        basedict = {}
        basedict["value"] = str(self.value)

        basedict["freespace"] = get_bool_string(self.freespace)
        basedict["rule"] = self.rule.get_name()
        if self.isVersion(minor=0):
            basedict["alongRoute"] = get_bool_string(self.alongroute)
        else:
            basedict["relativeDistanceType"] = (
                self.relative_distance_type.get_name()
            )
            basedict["coordinateSystem"] = self.coordinate_system.get_name()
        if self.routing_algorithm is not None:
            if self.isVersionEqLess(minor=1):
                raise OpenSCENARIOVersionError(
                    "routing algorithm was introduced in OSC 1.2"
                )
            basedict["routingAlgorithm"] = self.routing_algorithm.get_name()

        return basedict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the DistanceCondition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the DistanceCondition.
        """

        element = ET.Element("EntityCondition")
        distancecond = ET.SubElement(
            element, "DistanceCondition", attrib=self.get_attributes()
        )
        distancecond.append(self.position.get_element())
        return element


class RelativeDistanceCondition(_EntityTriggerType):
    """The RelativeDistanceCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    value : float
        Distance to position.
    rule : Rule
        Condition rule of triggering.
    dist_type : RelativeDistanceType
        Type of relative distance.
    entity : str
        Name of the entity for relative distance.
    freespace : bool, optional
        If True, distance between bounding boxes is used. If False,
        distance between reference points is used. Default is True.
    coordinate_system : CoordinateSystem, optional
        Coordinate system to use (valid from V1.1). Default is
        CoordinateSystem.entity.
    routing_algorithm : RoutingAlgorithm, optional
        If coordinate_system is road/lane, this can be set (valid
        from V1.2). Default is None.

    Attributes
    ----------
    value : float
        Distance to position.
    rule : Rule
        Condition rule of triggering.
    entity : str
        Name of the entity for relative distance.
    dist_type : RelativeDistanceType
        Type of relative distance.
    freespace : bool
        If True, distance between bounding boxes is used. If False,
        distance between reference points is used.
    coordinate_system : CoordinateSystem
        Coordinate system to use (valid from V1.1).
    routing_algorithm : RoutingAlgorithm, optional
        If coordinate_system is road/lane, this can be set (valid
        from V1.2). Default is None.

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
        rule: Rule,
        dist_type: RelativeDistanceType,
        entity: str,
        alongroute: bool = True,
        freespace: bool = True,
        coordinate_system: CoordinateSystem = CoordinateSystem.entity,
        routing_algorithm: Union[RoutingAlgorithm, None] = None,
    ) -> None:
        """Initialize the RelativeDistanceCondition.

        Parameters
        ----------
        value : float
            Distance to position.
        rule : Rule
            Condition rule of triggering.
        dist_type : RelativeDistanceType
            Type of relative distance.
        entity : str
            Name of the entity for relative distance.
        freespace : bool, optional
            If True, distance between bounding boxes is used. If False,
            distance between reference points is used. Default is True.
        coordinate_system : CoordinateSystem, optional
            Coordinate system to use (valid from V1.1). Default is
            CoordinateSystem.entity.
        routing_algorithm : RoutingAlgorithm, optional
            If coordinate_system is road/lane, this can be set (valid
            from V1.2). Default is None.
        """
        self.value = value
        self.alongroute = convert_bool(alongroute)
        self.freespace = convert_bool(freespace)
        self.dist_type = convert_enum(dist_type, RelativeDistanceType)
        self.rule = convert_enum(rule, Rule)
        self.entity = entity
        self.coordinate_system = convert_enum(
            coordinate_system, CoordinateSystem
        )
        self.routing_algorithm = convert_enum(
            routing_algorithm, RoutingAlgorithm, True
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RelativeDistanceCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RelativeDistanceCondition":
        """Parse the XML element of RelativeDistanceCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RelativeDistanceCondition
            A RelativeDistanceCondition object.
        """
        condition = find_mandatory_field(element, "RelativeDistanceCondition")
        # value = convert_float(condition.attrib["value"])
        value = condition.attrib["value"]
        rule = convert_enum(condition.attrib["rule"], Rule)
        freespace = convert_bool(condition.attrib["freespace"])
        entity = condition.attrib["entityRef"]
        if "alongRoute" in condition.attrib:
            alongroute = convert_bool(condition.attrib["alongRoute"])
        else:
            alongroute = True

        if "relativeDistanceType" in condition.attrib:
            reldisttype = convert_enum(
                condition.attrib["relativeDistanceType"], RelativeDistanceType
            )
        else:
            reldisttype = RelativeDistanceType.longitudinal

        if "coordinateSystem" in condition.attrib:
            coordsystem = convert_enum(
                condition.attrib["coordinateSystem"], CoordinateSystem
            )
        else:
            coordsystem = CoordinateSystem.road
        if "routingAlgorithm" in condition.attrib:
            routing_algorithm = convert_enum(
                condition.attrib["routingAlgorithm"], RoutingAlgorithm
            )
        else:
            routing_algorithm = None

        return RelativeDistanceCondition(
            value,
            rule,
            reldisttype,
            entity,
            alongroute,
            freespace,
            coordsystem,
            routing_algorithm,
        )

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the RelativeDistanceCondition as a
        dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the
            RelativeDistanceCondition.
        """
        basedict = {}
        basedict["value"] = str(self.value)
        basedict["freespace"] = get_bool_string(self.freespace)
        basedict["entityRef"] = self.entity
        basedict["rule"] = self.rule.get_name()
        basedict["relativeDistanceType"] = self.dist_type.get_name()
        if not self.isVersion(minor=0):
            basedict["coordinateSystem"] = self.coordinate_system.get_name()
        if self.routing_algorithm:
            if self.isVersionEqLarger(minor=2):
                basedict["routingAlgorithm"] = (
                    self.routing_algorithm.get_name()
                )
            else:
                raise OpenSCENARIOVersionError(
                    "RoutingAlgorithm was introduced in V1.2"
                )

        return basedict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the RelativeDistanceCondition.

        Returns
        -------
        ET.Element
            The XML element representing the RelativeDistanceCondition.
        """
        element = ET.Element("EntityCondition")
        ET.SubElement(
            element, "RelativeDistanceCondition", attrib=self.get_attributes()
        )
        return element


class RelativeClearanceCondition(_EntityTriggerType):
    """The RelativeClearanceCondition class is an Entity Condition used by the
    EntityTrigger.

    Parameters
    ----------
    distance_backward : float
        Distance backwards.
    distance_forward : float
        Distance forward.
    freespace : bool
        True for distance between bounding boxes, False for distance
        between reference points.
    opposite_lanes : bool
        If lanes in opposite direction are considered.

    Attributes
    ----------
    distance_backward : float
        Distance backwards.
    distance_forward : float
        Distance forward.
    freespace : bool
        True for distance between bounding boxes, False for distance
        between reference points.
    opposite_lanes : bool
        If lanes in opposite direction are considered.
    entities : list of EntityRef
        Specific entities to look for.
    lane_ranges : list of tuple
        Lanes to be checked.

    Methods
    -------
    add_entity(entity)
        Adds an entity to the RelativeClearanceCondition.
    add_relative_lane_range(from, to)
        Adds a RelativeLaneRange to the RelativeClearanceCondition.
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
        opposite_lanes: bool,
        distance_backward: float = 0,
        distance_forward: float = 0,
        freespace: bool = True,
    ) -> None:
        """Initialize the RelativeDistanceCondition.

        Parameters
        ----------
        distance_backward : float
            Distance backwards.
        distance_forward : float
            Distance forward.
        freespace : bool
            True for distance between bounding boxes, False for distance
            between reference points.
        opposite_lanes : bool
            If lanes in opposite direction are considered.
        """

        self.freespace = convert_bool(freespace)
        self.opposite_lanes = convert_bool(opposite_lanes)
        self.distance_backward = convert_float(distance_backward)
        self.distance_forward = convert_float(distance_forward)

        self.entities = []
        self.lane_ranges = []

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RelativeClearanceCondition):
            if (
                self.get_attributes() == other.get_attributes()
                and self.entities == other.entities
                and self.lane_ranges == other.lane_ranges
            ):
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "RelativeClearanceCondition":
        """Parse the XML element of RelativeClearanceCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        RelativeClearanceCondition
            A RelativeClearanceCondition object.
        """
        condition = find_mandatory_field(element, "RelativeClearanceCondition")
        if "freespace" in condition.attrib:
            freespace = convert_bool(condition.attrib["freespace"])
        else:
            freespace = convert_bool(condition.attrib["freeSpace"])

        opposite_lanes = convert_bool(condition.attrib["oppositeLanes"])

        if "distanceBackward" in condition.attrib:
            back_dist = convert_float(condition.attrib["distanceBackward"])
        else:
            back_dist = None

        if "distanceForward" in condition.attrib:
            fwd_dist = convert_float(condition.attrib["distanceForward"])
        else:
            fwd_dist = None
        retval = RelativeClearanceCondition(
            opposite_lanes, back_dist, fwd_dist, freespace
        )
        for er in condition.findall("EntityRef"):
            retval.add_entity(er.attrib["entityRef"])

        for r in condition.findall("RelativeLaneRange"):
            retval.add_relative_lane_range(
                convert_int(r.attrib["from"]), convert_int(r.attrib["to"])
            )

        return retval

    def add_entity(self, entity: str) -> None:
        """Add an entity to the RelativeClearanceCondition.

        Parameters
        ----------
        entity : str
            Name of the entity.
        """
        self.entities.append(EntityRef(entity))

    def add_relative_lane_range(self, from_lane: int, to_lane: int) -> None:
        """Add a RelativeLaneRange to the RelativeClearanceCondition.

        Parameters
        ----------
        from_lane : int
            Start lane.
        to_lane : int
            End lane.
        """
        self.lane_ranges.append((from_lane, to_lane))

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the RelativeClearanceCondition as a
        dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the
            RelativeClearanceCondition.
        """
        basedict = {}
        basedict["oppositeLanes"] = get_bool_string(self.opposite_lanes)
        # TODO: wrong in the spec, should be lower case s
        basedict["freeSpace"] = get_bool_string(self.freespace)

        if self.distance_backward is not None:
            basedict["distanceBackward"] = str(self.distance_backward)
        if self.distance_forward is not None:
            basedict["distanceForward"] = str(self.distance_forward)
        return basedict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the RelativeClearanceCondition.

        Returns
        -------
        ET.Element
            The XML element representing the RelativeClearanceCondition.
        """
        if self.isVersionEqLess(minor=1):
            raise OpenSCENARIOVersionError(
                "RelativeClearanceCondition was added in OSC 1.2"
            )
        element = ET.Element("EntityCondition")
        relative_clearence_element = ET.SubElement(
            element, "RelativeClearanceCondition", attrib=self.get_attributes()
        )
        for r in self.lane_ranges:
            ET.SubElement(
                relative_clearence_element,
                "RelativeLaneRange",
                {"from": str(r[0]), "to": str(r[1])},
            )
        for e in self.entities:
            relative_clearence_element.append(e.get_element())

        return element


""" Value Conditions

"""


class ParameterCondition(_ValueTriggerType):
    """The ParameterCondition class is a Value Condition used by the
    ValueTrigger.

    Parameters
    ----------
    parameter : str
        The parameter to trigger on.
    value : int
        Value to trigger on.
    rule : Rule
        Condition rule of triggering.

    Attributes
    ----------
    parameter : str
        The parameter to trigger on.
    value : int
        Value to trigger on.
    rule : Rule
        Condition rule of triggering.

    Methods
    -------
    parse
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element
        Returns the full ElementTree of the class.
    get_attributes
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, parameter: str, value: int, rule: Rule) -> None:
        """Initialize the ParameterCondition.

        Parameters
        ----------
        parameter : str
            The parameter to trigger on.
        value : int
            Value to trigger on.
        rule : Rule
            Condition rule of triggering.
        """
        self.parameter = parameter
        self.value = value
        self.rule = convert_enum(rule, Rule)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ParameterCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "ParameterCondition":
        """Parse the XML element of ParameterCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        ParameterCondition
            A ParameterCondition object.
        """
        parameter = element.attrib["parameterRef"]
        value = element.attrib["value"]
        rule = convert_enum(element.attrib["rule"], Rule)
        return ParameterCondition(parameter, value, rule)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the ParameterCondition as a dict.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            ParameterCondition.
        """
        basedict = {"parameterRef": self.parameter, "value": str(self.value)}
        basedict["rule"] = self.rule.get_name()
        return basedict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the ParameterCondition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the ParameterCondition.
        """
        return ET.Element("ParameterCondition", attrib=self.get_attributes())


class VariableCondition(_ValueTriggerType):
    """The VariableCondition class is a Value Condition used by the
    ValueTrigger (valid from V1.2).

    Parameters
    ----------
    variable : str
        The variable to trigger on.
    value : int
        Value to trigger on.
    rule : Rule
        Condition rule of triggering.

    Attributes
    ----------
    variable : str
        The variable to trigger on.
    value : int
        Value to trigger on.
    rule : Rule
        Condition rule of triggering.

    Methods
    -------
    parse
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element
        Returns the full ElementTree of the class.
    get_attributes
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, variable: str, value: int, rule: Rule) -> None:
        """Initialize the VariableCondition.

        Parameters
        ----------
        variable : str
            The variable to trigger on.
        value : int
            Value to trigger on.
        rule : Rule
            Condition rule of triggering.
        """
        self.variable = variable
        self.value = value
        self.rule = convert_enum(rule, Rule)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, VariableCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "VariableCondition":
        """Parse the XML element of VariableCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        VariableCondition
            A VariableCondition object.
        """
        variable = element.attrib["variableRef"]
        value = element.attrib["value"]
        rule = convert_enum(element.attrib["rule"], Rule)
        return VariableCondition(variable, value, rule)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the VariableCondition as a dict.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            VariableCondition.
        """
        basedict = {"variableRef": self.variable, "value": str(self.value)}
        basedict["rule"] = self.rule.get_name()
        return basedict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the VariableCondition.

        Returns
        -------
        xml.etree.ElementTree.Element
            The XML element representing the VariableCondition.
        """
        if self.isVersionEqLess(minor=1):
            raise OpenSCENARIOVersionError(
                "VariableCondition was added in OSC 1.2"
            )
        return ET.Element("VariableCondition", attrib=self.get_attributes())


class TimeOfDayCondition(_ValueTriggerType):
    """The TimeOfDayCondition class is a Value Condition used by the
    ValueTrigger.

    Parameters
    ----------
    rule : Rule
        Condition rule of triggering.
    year : int
        Year of the date-time.
    month : int
        Month of the date-time.
    day : int
        Day of the date-time.
    hour : int
        Hour of the date-time.
    minute : int
        Minute of the date-time.
    second : int
        Second of the date-time.

    Attributes
    ----------
    rule : Rule
        Condition rule of triggering.
    year : int
        Year of the date-time.
    month : int
        Month of the date-time.
    day : int
        Day of the date-time.
    hour : int
        Hour of the date-time.
    minute : int
        Minute of the date-time.
    second : int
        Second of the date-time.

    Methods
    -------
    get_element()
        Returns the full ElementTree of the class.
    get_attributes()
        Returns a dictionary of all attributes of the class.
    """

    def __init__(
        self,
        rule: Rule,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
    ) -> None:
        """Initialize the TimeOfDayCondition.

        Parameters
        ----------
        rule : Rule
            Condition rule of triggering.
        year : int
            Year of the date-time.
        month : int
            Month of the date-time.
        day : int
            Day of the date-time.
        hour : int
            Hour of the date-time.
        minute : int
            Minute of the date-time.
        second : int
            Second of the date-time.
        """
        self.rule = convert_enum(rule, Rule)
        self.year = convert_int(year)
        self.month = convert_int(month)
        self.day = convert_int(day)
        self.hour = convert_int(hour)
        self.minute = convert_int(minute)
        self.second = convert_int(second)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TimeOfDayCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TimeOfDayCondition":
        """Parse the XML element of TimeOfDayCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        TimeOfDayCondition
            A TimeOfDayCondition object.
        """
        var = element.attrib["dateTime"]
        year = convert_int(var[0:4])
        month = convert_int(var[5:7])
        day = convert_int(var[8:10])

        hour = convert_int(var[11:13])
        minute = convert_int(var[14:16])
        second = convert_int(var[17:19])
        rule = convert_enum(element.attrib["rule"], Rule)
        return TimeOfDayCondition(rule, year, month, day, hour, minute, second)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the TimeOfDayCondition as a dict.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            TimeOfDayCondition.
        """
        basedict = {}
        dt = (
            str(self.year)
            + "-"
            + "{:0>2}".format(self.month)
            + "-"
            + "{:0>2}".format(self.day)
            + "T"
            + "{:0>2}".format(self.hour)
            + ":"
            + "{:0>2}".format(self.minute)
            + ":"
            + "{:0>2}".format(self.second)
        )
        basedict["dateTime"] = dt
        basedict["rule"] = self.rule.get_name()
        return basedict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the TimeOfDayCondition.

        Returns
        -------
        ET.Element
            The XML element representing the TimeOfDayCondition.
        """
        return ET.Element("TimeOfDayCondition", attrib=self.get_attributes())


class SimulationTimeCondition(_ValueTriggerType):
    """The SimulationTimeCondition class is a Value Condition used by the
    ValueTrigger.

    Parameters
    ----------
    value : float
        Simulation time.
    rule : Rule
        Condition rule of triggering.

    Attributes
    ----------
    value : float
        Simulation time.
    rule : Rule
        Condition rule of triggering.

    Methods
    -------
    parse
        Parses an ElementTree created by the class and returns an
        instance of the class.
    get_element
        Returns the full ElementTree of the class.
    get_attributes
        Returns a dictionary of all attributes of the class.
    """

    def __init__(self, value: float, rule: Rule) -> None:
        """Initialize the SimulationTimeCondition.

        Parameters
        ----------
        value : float
            Simulation time.
        rule : Rule
            Condition rule of triggering.
        """
        self.value = convert_float(value)
        self.rule = convert_enum(rule, Rule)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SimulationTimeCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "SimulationTimeCondition":
        """Parse the XML element of SimulationTimeCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        SimulationTimeCondition
            A SimulationTimeCondition object.
        """
        value = convert_float(element.attrib["value"])
        rule = convert_enum(element.attrib["rule"], Rule)
        return SimulationTimeCondition(value, rule)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the SimulationTimeCondition as a dict.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            SimulationTimeCondition.
        """
        basedict = {}
        basedict["value"] = str(self.value)
        basedict["rule"] = self.rule.get_name()
        return basedict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the SimulationTimeCondition.

        Returns
        -------
        ET.Element
            The XML element representing the SimulationTimeCondition.
        """
        return ET.Element(
            "SimulationTimeCondition", attrib=self.get_attributes()
        )


class StoryboardElementStateCondition(_ValueTriggerType):
    """The StoryboardElementStateCondition class is a Value Condition used by
    the ValueTrigger.

    Parameters
    ----------
    element : StoryboardElementType
        The element to trigger on.
    reference : str
        Reference of the parameter.
    state : StoryboardElementState
        State to trigger on.

    Attributes
    ----------
    element : StoryboardElementType
        The element to trigger on.
    reference : str
        Reference of the parameter.
    state : StoryboardElementState
        State to trigger on.

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
        element: StoryboardElementType,
        reference: str,
        state: StoryboardElementState,
    ) -> None:
        """Initialize the StoryboardElementStateCondition.

        Parameters
        ----------
        element : StoryboardElementType
            The element to trigger on.
        reference : str
            Reference of the parameter.
        state : StoryboardElementState
            State to trigger on.
        """
        self.element = convert_enum(element, StoryboardElementType)
        self.reference = reference
        self.state = convert_enum(state, StoryboardElementState)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, StoryboardElementStateCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "StoryboardElementStateCondition":
        """Parse the XML element of StoryboardElementStateCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        StoryboardElementStateCondition
            A StoryboardElementStateCondition object.
        """
        ref = element.attrib["storyboardElementRef"]
        sbet = convert_enum(
            element.attrib["storyboardElementType"], StoryboardElementType
        )
        state = convert_enum(element.attrib["state"], StoryboardElementState)
        return StoryboardElementStateCondition(sbet, ref, state)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the StoryboardElementStateCondition as a
        dictionary.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            StoryboardElementStateCondition.
        """
        return {
            "storyboardElementType": self.element.get_name(),
            "storyboardElementRef": self.reference,
            "state": self.state.get_name(),
        }

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the StoryboardElementStateCondition.

        Returns
        -------
        ET.Element
            The XML element representing the StoryboardElementStateCondition.
        """
        return ET.Element(
            "StoryboardElementStateCondition", attrib=self.get_attributes()
        )


class UserDefinedValueCondition(_ValueTriggerType):
    """UserDefinedValueCondition is a Value Condition used by the ValueTrigger.

    Parameters
    ----------
    name : str
        Name of the parameter.
    value : int
        Value to trigger on.
    rule : Rule
        Condition rule of triggering.

    Attributes
    ----------
    name : str
        Name of the parameter.
    value : int
        Value to trigger on.
    rule : Rule
        Condition rule of triggering.

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

    def __init__(self, name: str, value: int, rule: Rule) -> None:
        """Initialize the UserDefinedValueCondition.

        Parameters
        ----------
        name : str
            Name of the parameter.
        value : int
            Value to trigger on.
        rule : Rule
            Condition rule of triggering.
        """
        self.name = name
        self.value = value
        self.rule = convert_enum(rule, Rule)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UserDefinedValueCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "UserDefinedValueCondition":
        """Parse the XML element of UserDefinedValueCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        UserDefinedValueCondition
            A UserDefinedValueCondition object.
        """
        name = element.attrib["name"]
        value = convert_int(element.attrib["value"])
        rule = convert_enum(element.attrib["rule"], Rule)
        return UserDefinedValueCondition(name, value, rule)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the UserDefinedValueCondition as a
        dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the
            UserDefinedValueCondition.
        """
        basedict = {"name": self.name, "value": str(self.value)}
        basedict["rule"] = self.rule.get_name()
        return basedict

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the UserDefinedValueCondition.

        Returns
        -------
        ET.Element
            The XML element representing the UserDefinedValueCondition.
        """
        return ET.Element(
            "UserDefinedValueCondition", attrib=self.get_attributes()
        )


class TrafficSignalCondition(_ValueTriggerType):
    """TrafficSignalCondition is a Value Condition used by the ValueTrigger.

    Parameters
    ----------
    name : str
        Name of the traffic signal.
    state : str
        State of the signal.

    Attributes
    ----------
    name : str
        Name of the traffic signal.
    state : str
        State of the signal.

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

    def __init__(self, name: str, state: str) -> None:
        """Initialize the TrafficSignalCondition.

        Parameters
        ----------
        name : str
            Name of the traffic signal.
        state : str
            State of the signal.
        """
        self.name = name
        self.state = state

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TrafficSignalCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TrafficSignalCondition":
        """Parse the XML element of TrafficSignalCondition.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element
            A position element (same as generated by the class itself).

        Returns
        -------
        TrafficSignalCondition
            A TrafficSignalCondition object.
        """
        name = element.attrib["name"]
        state = element.attrib["state"]

        return TrafficSignalCondition(name, state)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the TrafficSignalCondition as a dict.

        Returns
        -------
        dict
            A dictionary containing the attributes of the
            TrafficSignalCondition.
        """
        return {"name": self.name, "state": self.state}

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the TrafficSignalCondition.

        Returns
        -------
        ET.Element
            The XML element representing the TrafficSignalCondition.
        """
        return ET.Element(
            "TrafficSignalCondition", attrib=self.get_attributes()
        )


class TrafficSignalControllerCondition(_ValueTriggerType):
    """The TrafficSignalControllerCondition class is an Value Condition used by
    the ValueTrigger.

    Parameters
    ----------
        trafficsignalref (str): ???

        phase (str): ???

    Attributes
    ----------
        trafficsignalref (str): ???

        phase (str): ???

    Methods
    -------
        parse(element)
            parses a ElementTree created by the class and returns an instance of the class

        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class
    """

    def __init__(self, trafficsignalref: str, phase: str) -> None:
        """Initalize the TrafficSignalControllerCondition.

        Parameters
        ----------
            trafficsignalref (str): ???

            phase (str): ???
        """
        self.trafficsignalref = trafficsignalref
        self.phase = phase

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TrafficSignalControllerCondition):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    @staticmethod
    def parse(element: ET.Element) -> "TrafficSignalControllerCondition":
        """Parses the xml element of TrafficSignalControllerCondition.

        Parameters
        ----------
            element (xml.etree.ElementTree.Element): A position element (same as generated by the class itself)

        Returns
        -------
            condition (TrafficSignalControllerCondition): a TrafficSignalControllerCondition object
        """
        trafficsignalref = element.attrib["trafficSignalControllerRef"]
        phase = element.attrib["phase"]

        return TrafficSignalControllerCondition(trafficsignalref, phase)

    def get_attributes(self) -> dict[str, str]:
        """Returns the attributes of the TrafficSignalControllerCondition as a
        dict."""
        return {
            "trafficSignalControllerRef": self.trafficsignalref,
            "phase": self.phase,
        }

    def get_element(self) -> ET.Element:
        """Returns the elementTree of the TrafficSignalControllerCondition."""
        return ET.Element(
            "TrafficSignalControllerCondition", attrib=self.get_attributes()
        )
