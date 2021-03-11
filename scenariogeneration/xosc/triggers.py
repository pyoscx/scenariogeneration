""" the trigger module contains the classes related to the triggers and conditions of OpenSCENARIO.

"""
import xml.etree.ElementTree as ET

from .utils import EntityRef, convert_bool, _PositionType, _ValueTriggerType, _EntityTriggerType, _TriggerType
from .enumerations import Rule, ConditionEdge, TriggeringEntitiesRule, RelativeDistanceType, StoryboardElementType, StoryboardElementState





class EmptyTrigger(_TriggerType):
    """ EmptyTrigger creates an empty trigger
        
        Parameters
        ----------
            triggeringpoint (str): start or stop 

        Attributes
        ----------
            
        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,triggeringpoint = 'start'):
        """ initalizes the emtpy trigger

        Parameters
        ----------
            triggeringpoint (str): start or stop 

        """
        if triggeringpoint not in ['start','stop']:
            raise ValueError('not a valid triggering point, valid start or stop')
        if triggeringpoint == 'start':
            self._triggerpoint = 'StartTrigger'
        else:
            self._triggerpoint = 'StopTrigger'

    def get_element(self):
        """ returns the elementTree of the Trigger

        """
        return ET.Element(self._triggerpoint)
        


class Trigger(_TriggerType):
    """ The Trigger class creates a Trigger that can be used if multiple ConditionGroups are wanted
        
        Parameters
        ----------
            triggeringpoint (str): start or stop 
                Default: start

        Attributes
        ----------
            triggeringpoint (str): start or stop 

            conditiongroups (list of ConditionGroup): a list of all conditiongroups

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            add_conditiongroup(conditiongroup)
                Adds a conditiongroup to the trigger 

    """
    def __init__(self,triggeringpoint = 'start'):
        """ initalize the Trigger

        Parameters
        ----------
            triggeringpoint (str): start or stop
         
        """
        if triggeringpoint not in ['start','stop']:
            raise ValueError('not a valid triggering point, valid start or stop')
        if triggeringpoint == 'start':
            self._triggerpoint = 'StartTrigger'
        else:
            self._triggerpoint = 'StopTrigger'
        self.conditiongroups = []

    def add_conditiongroup(self,conditiongroup):
        """ Adds a conditiongroup to the trigger

        Parameters
        ----------
            conditiongroup (ConditionGroup): a conditiongroup to add to the trigger
         
        """
        if not isinstance(conditiongroup,ConditionGroup):
            raise TypeError('conditiongroup input not of type ConditionGroup')   
        conditiongroup._set_used_by_parent()
        self.conditiongroups.append(conditiongroup)
    
    def get_element(self):
        """ returns the elementTree of the Trigger

        """
        element = ET.Element(self._triggerpoint)
        if not self.conditiongroups:
            ValueError('No conditiongroups were added to the trigger')
        for c in self.conditiongroups:
            element.append(c.get_element())
        return element

class ConditionGroup(_TriggerType):
    """ The ConditionGroup class creates a Trigger that can be used if multiple Conditions are wanted
        
        Parameters
        ----------
            triggeringpoint (str): start or stop (not needed if used with the Trigger class)
                Default: start

        Attributes
        ----------
            triggeringpoint (str): start or stop 

            conditions (list of EntityTriggers and Valuetriggers): a list of all conditions

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            add_condition(condition)
                Adds a condition to the ConditionGroup

    """
    def __init__(self,triggeringpoint = 'start'):
        """ initalize the ConditionGroup

        Parameters
        ----------
            triggeringpoint (str): start or stop
         
        """
        if triggeringpoint not in ['start','stop']:
            raise ValueError('not a valid triggering point, valid start or stop')
        if triggeringpoint == 'start':
            self._triggerpoint = 'StartTrigger'
        else:
            self._triggerpoint = 'StopTrigger'
        self.conditions = []

    def add_condition(self,condition):
        """ Adds a condition (EntityTrigger or ValueTrigger) to the ConditionGroup

            Parameters
            ----------
                condition (EntityTrigger, or ValueTrigger): a condition to add to the ConditionGroup
         
        """
        if not ( isinstance(condition,EntityTrigger) or isinstance(condition,ValueTrigger)):
            raise TypeError('condition input not of type EntityTrigger or ValueTrigger')   
        condition._set_used_by_parent()
        self.conditions.append(condition)
        self._used_by_parent = False
    
    def _set_used_by_parent(self):
        """ _set_used_by_parent is used internaly if the condition group is added to a Trigger

        """
        self._used_by_parent = True
    
    def get_element(self):
        """ returns the elementTree of the ConditionGroup

        """
        if not self.conditions:
            raise ValueError('No conditions were added to the ConditionGroup')
        condgroup = ET.Element('ConditionGroup')

        for c in self.conditions:
            condgroup.append(c.get_element())

        if self._used_by_parent:
            return condgroup
        else:
            # could create a new Trigger here, but went with this solution for now
            element = ET.Element(self._triggerpoint)
            element.append(condgroup)
            return element



class EntityTrigger(_TriggerType):
    """ the EntityTrigger creates an Trigger containing an EntityTrigger 
        
        Parameters
        ----------
            name (str): name of the trigger

            delay (float): the delay of the trigger

            conditionedge (ConditionEdge): on what conditionedge the trigger should act

            entitycondotion (*Condition): an entity condition

            triggeringentity (str): the entity of the trigger

            triggeringrule (TriggeringEntitiesRule): rule of the trigger
                Default: 'any'

            triggeringpoint (str): start or stop 
            
        Attributes
        ----------
            name (str): name of the trigger

            delay (float): the delay of the trigger

            conditionedge (ConditionEdge): the condition edge

            entitycondition (*EntityCondition): the entitycondition
        
            triggerentity (TriggeringEntities): the triggering entity

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,delay,conditionedge,entitycondition,triggerentity,triggeringrule=TriggeringEntitiesRule.any,triggeringpoint = 'start'):
        """ initalize the EntityTrigger

        Parameters
        ----------
            name (str): name of the trigger

            delay (float): the delay of the trigger

            conditionedge (ConditionEdge): on what conditionedge the trigger should act

            entitycondotion (*EntityCondition): an entity condition

            triggeringentity (str): the entity of the trigger 

            triggeringrule (TriggeringEntitiesRule): rule of the trigger
                Default: 'any'

            triggeringpoint (str): start or stop 
    
        """
        self.name = name
        if triggeringpoint not in ['start','stop']:
            raise ValueError('not a valid triggering point, valid start or stop')
        if triggeringpoint == 'start':
            self._triggerpoint = 'StartTrigger'
        else:
            self._triggerpoint = 'StopTrigger'
            
        self.delay = delay
        if conditionedge not in ConditionEdge:
            raise ValueError('not a valid condition edge')
        self.conditionedge = conditionedge
        if not isinstance(entitycondition,_EntityTriggerType):
            raise TypeError('entitycondition is not a valid EntityCondition')
        self.entitycondition = entitycondition
        self.triggerentity = TriggeringEntities(triggeringrule)
        self.triggerentity.add_entity(triggerentity)
        
        self._used_by_parent = False

    def _set_used_by_parent(self):
        """ _set_used_by_parent is used internaly if the condition is added to a ConditionGroup

        """
        self._used_by_parent = True

    def add_triggering_entity(self,triggerentity):
        """ adds additional triggering entities to a trigger

        Parameters
        ----------
            triggeringentity (str)
        """
        self.triggerentity.add_entity(triggerentity)
    def get_attributes(self):
        """ returns the attributes of the LaneOffsetAction as a dict

        """
        return {'name':self.name,'delay':str(self.delay),'conditionEdge':self.conditionedge.name}

    def get_element(self):
        """ returns the elementTree of the LaneOffsetAction

        """
        condition = ET.Element('Condition',attrib=self.get_attributes())
        byentity = ET.SubElement(condition,'ByEntityCondition')
        byentity.append(self.triggerentity.get_element())
        byentity.append(self.entitycondition.get_element())


        if self._used_by_parent:
            return condition
        else:
            # could create a new Trigger ConditionGroup here, but went with this solution for now
            element = ET.Element(self._triggerpoint)
            condgroup = ET.SubElement(element,'ConditionGroup')
            condgroup.append(condition)
            return element




class ValueTrigger(_TriggerType):
    """ the ValueTrigger creates a Trigger of the type ValueTrigger of openscenario
        
        Parameters
        ----------
            name (str): name of the trigger

            delay (float): the delay of the trigger

            conditionedge (ConditionEdge): on what conditionedge the trigger should act

            valuecondition (*ValueCondition): a value condition

            triggeringentity (str): the entity of the trigger 

            triggeringrule (str): rule of the trigger
                Default: 'any'

            triggeringpoint (str): start or stop 
            
        Attributes
        ----------
            name (str): name of the trigger

            delay (float): the delay of the trigger

            conditionedge (ConditionEdge): the condition edge

            valuecondition (*ValueCondition): the value condition
        
            triggerentity (TriggeringEntities): the triggering entity

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,delay,conditionedge,valuecondition,triggeringpoint='start'):
        """ initalize the ValueTrigger
        
        Parameters
        ----------
            name (str): name of the trigger

            delay (float): the delay of the trigger

            conditionedge (ConditionEdge): on what conditionedge the trigger should act

            valuecondition (*ValueCondition): a value condition

            triggeringentity (str): the entity of the trigger 

            triggeringrule (str): rule of the trigger
                Default: 'any'
            #TODO CHECK THIS
            triggeringpoint (str): start or stop 

        """
        self.name = name
        if triggeringpoint not in ['start','stop']:
            raise ValueError('not a valid triggering point, valid start or stop')
        if triggeringpoint == 'start':
            self._triggerpoint = 'StartTrigger'
        else:
            self._triggerpoint = 'StopTrigger'
            
        self.delay = delay
        if conditionedge not in ConditionEdge:
            raise ValueError('not a valid condition edge')
        self.conditionedge = conditionedge
        if not isinstance(valuecondition,_ValueTriggerType):
            raise TypeError('entitycondition is not a valid EntityCondition')
        self.valuecondition = valuecondition
        self._used_by_parent = False

    def _set_used_by_parent(self):
        """ _set_used_by_parent is used internaly if the condition is added to a ConditionGroup

        """
        self._used_by_parent = True

    def get_attributes(self):
        """ returns the attributes of the LaneOffsetAction as a dict

        """
        return {'name':self.name,'delay':str(self.delay),'conditionEdge':self.conditionedge.name}

    def get_element(self):
        """ returns the elementTree of the LaneOffsetAction

        """
        condition = ET.Element('Condition',attrib=self.get_attributes())
        byvalue = ET.SubElement(condition,'ByValueCondition')
        byvalue.append(self.valuecondition.get_element())
        if self._used_by_parent:
            return condition
        else:
            # could create a new Trigger ConditionGroup here, but went with this solution for now
            element = ET.Element(self._triggerpoint)
            condgroup = ET.SubElement(element,'ConditionGroup')
            condgroup.append(condition)
            return element


class TriggeringEntities():
    """ the TriggeringEntities class is used by Value and Entity Triggers to defined the trigger entity
        
        Parameters
        ----------
            triggeringrule (TriggeringEntitiesRule): all or any

        Attributes
        ----------
            entity (list of EntityRef): refernce to the entity

            triggeringrule (TriggeringEntitiesRule): all or any

        Methods
        -------
            add_entity(entity)
                adds a entityref to the triggering entities
                
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,triggeringrule):
        """ initalize the TriggeringEntities
        
        Parameters
        ----------
            entity (TriggeringEntitiesRule): name of the entity

            triggeringrule (str): all or any

        """
        if triggeringrule not in TriggeringEntitiesRule:
            raise ValueError('not a vaild triggering rule')
        self.entity = [] 
        self.triggeringrule = triggeringrule

    def add_entity(self,entity):
        """ add_entity adds an entity to the TriggeringEntities

        Parameters
        ----------
            entity (str): name of the entity to add
        
        """
        self.entity.append(EntityRef(entity))

    def get_attributes(self):
        """ returns the attributes of the LaneOffsetAction as a dict

        """
        return {'triggeringEntitiesRule':self.triggeringrule.name}

    def get_element(self):
        """ returns the elementTree of the LaneOffsetAction

        """
        element = ET.Element('TriggeringEntities',attrib=self.get_attributes())
        for ent in self.entity:
            element.append(ent.get_element())
        return element



""" Entity conditions


""" 

class EndOfRoadCondition(_EntityTriggerType):
    """ the EndOfRoadCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            duration (float): the duration at the en of road

        Attributes
        ----------
            duration (float): the duration at the en of road

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,duration):
        """ initalize the EndOfRoadCondition
        
        Parameters
        ----------
            duration (float): the duration after the condition

        """
        self.duration = duration
    
    def get_attributes(self):
        """ returns the attributes of the EndOfRoadCondition as a dict

        """
        return {'duration':str(self.duration)}

    def get_element(self):
        """ returns the elementTree of the EndOfRoadCondition

        """
        element = ET.Element('EntityCondition')
        ET.SubElement(element,'EndOfRoadCondition',attrib=self.get_attributes())
        return element

class CollisionCondition(_EntityTriggerType):
    """ the CollisionCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            entity (str or ObjectType): name of the entity to collide with

        Attributes
        ----------
            entity (str or ObjectType): name of the entity to collide with

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,entity):
        """ the CollisionCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            entity (str or ObjectType): name of the entity to collide with

        """
        
        self.entity = entity

    def get_element(self):
        """ returns the elementTree of the CollisionCondition

        """
        element = ET.Element('EntityCondition')
        colcond = ET.SubElement(element,'CollisionCondition')
        if isinstance(self.entity,str):
            colcond.append(EntityRef(self.entity).get_element())
        else:
            ET.SubElement(colcond,'ByType',{'type':self.entity.name})
        return element

class OffroadCondition(_EntityTriggerType):
    """ the OffroadCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            duration (float): the duration of offroad

        Attributes
        ----------
            duration (float): the duration of offroad

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,duration):
        """ initalize the OffroadCondition 
        
        Parameters
        ----------
            duration (float): the duration of offroad

        """
        self.duration = duration

    def get_attributes(self):
        """ returns the attributes of the OffroadCondition as a dict

        """
        return {'duration':str(self.duration)}

    def get_element(self):
        """ returns the elementTree of the OffroadCondition

        """
        element = ET.Element('EntityCondition')
        ET.SubElement(element,'OffroadCondition',attrib=self.get_attributes())
        return element

class TimeHeadwayCondition(_EntityTriggerType):
    """ the TimeHeadwayCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            entity (str): name of the entity for the headway

            value (float): time of headway

            rule (Rule): condition rule of triggering 

            alongroute (bool): if the route should count
                Default: True

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

        Attributes
        ----------
            entity (str): name of the entity for the headway

            value (float): time of headway

            rule (Rule): condition rule of triggering 

            alongroute (bool): if the route should count

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,entity,value,rule,alongroute=True,freespace=True):
        """ initalize the TimeHeadwayCondition
        
        Parameters
        ----------
            entity (str): name of the entity for the headway

            value (float): time of headway

            rule (Rule): condition rule of triggering 

            alongroute (bool): if the route should count
                Default: True
                
            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

        """
        self.entity = entity
        self.value = value
        if not isinstance(alongroute,bool):
            raise TypeError('alongroute input not of type bool')
        if not isinstance(freespace,bool):
            raise TypeError('freespace input not of type bool')
        self.alongroute = alongroute
        self.freespace = freespace
        if rule not in Rule:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule

    def get_attributes(self):
        """ returns the attributes of the TimeHeadwayCondition as a dict

        """
        basedict = {}
        basedict['entityRef'] = self.entity
        basedict['value'] = str(self.value)
        basedict['alongRoute'] = convert_bool(self.alongroute)
        basedict['freespace'] = convert_bool(self.freespace)
        basedict['rule'] = self.rule.name
        return basedict

    def get_element(self):
        """ returns the elementTree of the TimeHeadwayCondition

        """
        element = ET.Element('EntityCondition')
        ET.SubElement(element,'TimeHeadwayCondition',attrib=self.get_attributes())
        return element


class TimeToCollisionCondition(_EntityTriggerType):
    """ the TimeToCollisionCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------

            value (float): time to collision

            rule (Rule): condition rule of triggering 

            alongroute (bool): if the route should count
                Default: True

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            optionals:
                entity (str): the entity to trigger collision on

                position (*Position): a position for collision

        Attributes
        ----------
            value (float): time before collision

            rule (Rule): condition rule of triggering 

            alongroute (bool): if the route should count
            Default: True

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
            Default: True
            optionals:
                entity (EntityRef):  entity for the collision

                position (*Position): a position for collision

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,rule,alongroute=True,freespace=True,entity=None,position=None):
        """ initalize the TimeToCollisionCondition
        
        Parameters
        ----------

            value (float): time to collision

            rule (Rule): condition rule of triggering 

            alongroute (bool): if the route should count
                Default: True

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            optionals:
                entity (str): the entity to trigger collision on

                position (*Position): a position for collision
        
        """
        self.value = value
        if not isinstance(alongroute,bool):
            raise TypeError('alongroute input not of type bool')
        if not isinstance(freespace,bool):
            raise TypeError('freespace input not of type bool')
        self.freespace = freespace
        self.alongroute = alongroute
        if rule not in Rule:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
        self.use_entity = None
        if (entity !=None) and (position !=None):
            raise ValueError('Can only have either entity of position, not both')
        if entity:
            self.entity = EntityRef(entity)
            self.use_entity = True
        if position:
            if not isinstance(position,_PositionType):
                raise TypeError('input position is not a valid Position')
            self.position = position
            self.use_entity = False

    def get_attributes(self):
        """ returns the attributes of the TimeToCollisionCondition as a dict

        """
        basedict = {}
        basedict['value'] = str(self.value)
        basedict['alongRoute'] = convert_bool(self.alongroute)
        basedict['freespace'] = convert_bool(self.freespace)
        basedict['rule'] = self.rule.name
        return basedict
        

    def get_element(self):
        """ returns the elementTree of the TimeToCollisionCondition

        """
        element = ET.Element('EntityCondition')
        collisionevent = ET.SubElement(element,'TimeToCollisionCondition',attrib=self.get_attributes())
        
        targetelement = ET.SubElement(collisionevent,'TimeToCollisionConditionTarget')
        if self.use_entity == None:
            raise ValueError('neither position or entity was set.')
        elif self.use_entity:
            targetelement.append(self.entity.get_element())
        else: 
            targetelement.append(self.position.get_element())
        
        
        return element
        



class AccelerationCondition(_EntityTriggerType):
    """ the AccelerationCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            value (float): acceleration

            rule (Rule): condition rule of triggering 

        Attributes
        ----------
            value (float): acceleration

            rule (Rule): condition rule of triggering 

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,rule):
        """ the AccelerationCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            value (float): acceleration

            rule (Rule): condition rule of triggering 
        """
        self.value = value
        if rule not in Rule:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
        
    def get_attributes(self):
        """ returns the attributes of the AccelerationCondition as a dict

        """
        return {'value':str(self.value),'rule':self.rule.name}

    def get_element(self):
        """ returns the elementTree of the AccelerationCondition

        """
        element = ET.Element('EntityCondition')
        ET.SubElement(element,'AccelerationCondition',attrib=self.get_attributes())
        return element

class StandStillCondition(_EntityTriggerType):
    """ the StandStillCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            duration (float): time of standstill

        Attributes
        ----------
            duration (float): time of standstill

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,duration):
        """ the StandStillCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            duration (float): time of standstill
        """
        self.duration = duration

    def get_attributes(self):
        """ returns the attributes of the StandStillCondition as a dict

        """
        return {'duration':str(self.duration)}

    def get_element(self):
        """ returns the elementTree of the StandStillCondition

        """
        element = ET.Element('EntityCondition')
        ET.SubElement(element,'StandStillCondition',attrib=self.get_attributes())
        return element

class SpeedCondition(_EntityTriggerType):
    """ the SpeedCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            value (float): speed to trigger on

            rule (Rule): condition rule of triggering 

        Attributes
        ----------
            value (float): speed to trigger on

            rule (Rule): condition rule of triggering 

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,rule):
        """ initalize the SpeedCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            value (float): speed to trigger on

            rule (Rule): condition rule of triggering 
        """
        self.value = value
        if rule not in Rule:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
        
    def get_attributes(self):
        """ returns the attributes of the SpeedCondition as a dict

        """
        basedict = {}
        basedict['value'] = str(self.value)
        basedict['rule'] = self.rule.name
        return basedict
        # return merge_dicts({'value':str(self.value)},self.rule.get_attributes())

    def get_element(self):
        """ returns the elementTree of the SpeedCondition

        """
        element = ET.Element('EntityCondition')
        ET.SubElement(element,'SpeedCondition',attrib=self.get_attributes())
        return element

class RelativeSpeedCondition(_EntityTriggerType):
    """ the RelativeSpeedCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            value (float): acceleration

            rule (Rule): condition rule of triggering 

            entity (str): name of the entity to be relative to

        Attributes
        ----------
            value (float): acceleration

            rule (Rule): condition rule of triggering 

            entity (str): name of the entity to be relative to

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,rule,entity):
        """ initalize the RelativeSpeedCondition
        
        Parameters
        ----------
            value (float): acceleration

            rule (Rule): condition rule of triggering 

            entity (str): name of the entity to be relative to
            
        """
        self.value = value
        if rule not in Rule:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
        self.entity = entity

    def get_attributes(self):
        """ returns the attributes of the RelativeSpeedCondition as a dict

        """
        basedict = {}
        basedict['value'] = str(self.value)
        basedict['rule'] = self.rule.name
        basedict['entityRef'] = self.entity
        return basedict
        # return merge_dicts({'value':str(self.value),'entityRef':self.entity},self.rule.get_attributes())

    def get_element(self):
        """ returns the elementTree of the RelativeSpeedCondition

        """
        element = ET.Element('EntityCondition')
        ET.SubElement(element,'RelativeSpeedCondition',attrib=self.get_attributes())
        return element

class TraveledDistanceCondition(_EntityTriggerType):
    """ the TraveledDistanceCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            value (float): how far it has traveled

        Attributes
        ----------
            value (float): how far it has traveled

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value):
        """ the TraveledDistanceCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            value (float): how far it has traveled
        
        """
        self.value = value

    def get_attributes(self):
        """ returns the attributes of the TraveledDistanceCondition as a dict

        """
        return {'value':str(self.value)}

    def get_element(self):
        """ returns the elementTree of the TraveledDistanceCondition

        """
        element = ET.Element('EntityCondition')
        ET.SubElement(element,'TraveledDistanceCondition',attrib=self.get_attributes())
        return element 
    
class ReachPositionCondition(_EntityTriggerType):
    """ the ReachPositionCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            position (*Position): any position to reach

            tolerance (float): tolerance of the position

        Attributes
        ----------
            position (*Position): any position to reach

            tolerance (float): tolerance of the position

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,position,tolerance):
        """ initalize the ReachPositionCondition
        
        Parameters
        ----------
            position (*Position): any position to reach

            tolerance (float): tolerance of the position

        """
        if not (isinstance(position,_PositionType)):
            raise TypeError('position input is not a valid Position')
        self.position = position
        self.tolerance = tolerance

    def get_attributes(self):
        """ returns the attributes of the ReachPositionCondition as a dict

        """
        return {'tolerance':str(self.tolerance)}
        

    def get_element(self):
        """ returns the elementTree of the ReachPositionCondition

        """
        element = ET.Element('EntityCondition')
        reachposcond = ET.SubElement(element,'ReachPositionCondition',attrib=self.get_attributes())
        reachposcond.append(self.position.get_element())
        return element

class DistanceCondition(_EntityTriggerType):
    """ the DistanceCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            value (float): distance to position

            rule (Rule): condition rule of triggering 

            position (*Position): any position to reach

            alongroute (bool): if the route should count
                Default: True

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

        Attributes
        ----------
            value (float): distance to position

            rule (Rule): condition rule of triggering 

            position (*Position): any position to reach

            alongroute (bool): if the route should count

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,rule,position,alongroute=True,freespace=True):
        self.value = value
        self.alongroute = alongroute
        self.freespace = freespace
        if rule not in Rule:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
        if not (isinstance(position,_PositionType)):
            raise TypeError('position input is not a valid Position')
        self.position = position

    def get_attributes(self):
        """ returns the attributes of the DistanceCondition as a dict

        """
        basedict = {}
        basedict['value'] = str(self.value)
        basedict['alongRoute'] = convert_bool(self.alongroute)
        basedict['freespace'] = convert_bool(self.freespace)
        basedict['rule'] = self.rule.name
        return basedict

    def get_element(self):
        """ returns the elementTree of the DistanceCondition

        """
        element = ET.Element('EntityCondition')
        distancecond = ET.SubElement(element,'DistanceCondition',attrib=self.get_attributes())
        distancecond.append(self.position.get_element())
        return element

class RelativeDistanceCondition(_EntityTriggerType):
    """ the RelativeDistanceCondition class is an Entity Condition used by the EntityTrigger
        
        Parameters
        ----------
            value (float): distance to position

            rule (Rule): condition rule of triggering 

            dist_type (RelativeDistanceType): type of relative distance

            entity (str): name of the entity fore relative distance     

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

        Attributes
        ----------
            value (float): distance to position

            rule (Rule): condition rule of triggering 

            entity (str): name of the entity fore relative distance

            dist_type (RelativeDistanceType): type of relative distance

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,rule,dist_type,entity,alongroute=True,freespace=True):
        """ initalize the RelativeDistanceCondition
        
        Parameters
        ----------
            value (float): distance to position

            rule (Rule): condition rule of triggering 

            dist_type (RelativeDistanceType): type of relative distance

            entity (str): name of the entity fore relative distance           

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

        """
        self.value = value
        if not isinstance(freespace,bool):
            raise TypeError('freespace input not of type bool')
        self.alongroute = alongroute
        self.freespace = freespace
        if dist_type not in RelativeDistanceType:
            raise TypeError('dist_type is not of type RelativeDistanceType')
        self.dist_type = dist_type
        if rule not in Rule:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
        self.entity = entity

    def get_attributes(self):
        """ returns the attributes of the RelativeDistanceCondition as a dict

        """
        basedict = {}
        basedict['value'] = str(self.value)
        basedict['freespace'] = convert_bool(self.freespace)
        basedict['entityRef'] = self.entity
        basedict['rule'] = self.rule.name
        basedict['relativeDistanceType'] = self.dist_type.name
        return basedict

    def get_element(self):
        """ returns the elementTree of the RelativeDistanceCondition

        """
        element = ET.Element('EntityCondition')
        ET.SubElement(element,'RelativeDistanceCondition',attrib=self.get_attributes())
        return element
        


""" Value Conditions

"""


class ParameterCondition(_ValueTriggerType):
    """ the ParameterCondition class is an Value Condition used by the ValueTrigger
        
        Parameters
        ----------
            parameter (str): the parameter to trigger on

            value (int): value to trigger on 

            rule (Rule): condition rule of triggering 

        Attributes
        ----------
            parameter (str): the parameter to trigger on

            value (int): value to trigger on 

            rule (Rule): condition rule of triggering 

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,parameter,value,rule):
        """ initalize the ParameterCondition

            Parameters
            ----------
                parameter (str): the parameter to trigger on

                value (int): value to trigger on 

                rule (Rule): condition rule of triggering 

        """
        self.parameter = parameter
        self.value = value
        if rule not in Rule:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
        
    def get_attributes(self):
        """ returns the attributes of the ParameterCondition as a dict

        """
        basedict = {'parameterRef':self.parameter,'value':str(self.value)}
        basedict['rule'] = self.rule.name
        return basedict

    def get_element(self):
        """ returns the elementTree of the ParameterCondition

        """
        return ET.Element('ParameterCondition',attrib=self.get_attributes())

class TimeOfDayCondition(_ValueTriggerType):
    """ the TimeOfDayCondition class is an Value Condition used by the ValueTrigger
        
        Parameters
        ----------
            rule (Rule): condition rule of triggering 

            time of day (str): datetime ??? format unknown
            
        Attributes
        ----------
            rule (Rule): condition rule of triggering 

            time of day (str): datetime ??? format unknown

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,rule,datetime):
        """ initalize the TimeOfDayCondition
            Parameters
            ----------
                rule (Rule): condition rule of triggering 

                time of day (str): datetime ??? format unknown
            
        """
        if rule not in Rule:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
        self.datetime = datetime
    
    def get_attributes(self):
        """ returns the attributes of the TimeOfDayCondition as a dict

        """
        basedict = {}
        basedict['datetime'] = self.datetime
        basedict['rule'] = self.rule.name
        return basedict

    def get_element(self):
        """ returns the elementTree of the TimeOfDayCondition

        """
        return ET.Element('TimeOfDayCondition',attrib=self.get_attributes())


class SimulationTimeCondition(_ValueTriggerType):
    """ the SimulationTimeCondition class is an Value Condition used by the ValueTrigger
        
        Parameters
        ----------
            value (int): simulation time 

            rule (Rule): condition rule of triggering 

        Attributes
        ----------
            value (int): simulation time 

            rule (Rule): condition rule of triggering 

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,rule):
        """ initalize the SimulationTimeCondition

            Parameters
            ----------
                value (int): simulation time 

                rule (Rule): condition rule of triggering 
        """
        self.value = value
        if rule not in Rule:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
    
    def get_attributes(self):
        """ returns the attributes of the SimulationTimeCondition as a dict

        """
        basedict = {}
        basedict['value'] = str(self.value)
        basedict['rule'] = self.rule.name
        return basedict
    def get_element(self):
        """ returns the elementTree of the SimulationTimeCondition

        """
        return ET.Element('SimulationTimeCondition',attrib=self.get_attributes())

class StoryboardElementStateCondition(_ValueTriggerType):
    """ the StoryboardElementStateCondition class is an Value Condition used by the ValueTrigger
        
        Parameters
        ----------
            element (StoryboardElementType): the element to trigger on

            reference (str): reference of the parameter

            state (StoryboardElementState): state to trigger on

        Attributes
        ----------
            element (StoryboardElementType): the element to trigger on

            reference (str): reference of the parameter

            state (StoryboardElementState): state to trigger on

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,element,reference,state):
        """ initalize the StoryboardElementStateCondition

            Parameters
            ----------
                element (StoryboardElementType): the element to trigger on

                reference (str): reference of the parameter

                state (StoryboardElementType): state to trigger on
        """
        if element not in StoryboardElementType:
            raise TypeError('element input is not of type StoryBoardElementType')
        if state not in StoryboardElementState:
            raise TypeError('state input is not of type StoryBoardElementState')
        self.element = element
        self.reference = reference
        self.state = state
    
    def get_attributes(self):
        """ returns the attributes of the StoryboardElementStateCondition as a dict

        """
        return {'storyboardElementType':self.element.name,'storyboardElementRef':self.reference,'state':self.state.name}

    def get_element(self):
        """ returns the elementTree of the StoryboardElementStateCondition

        """
        return ET.Element('StoryboardElementStateCondition',attrib=self.get_attributes())

class UserDefinedValueCondition(_ValueTriggerType):
    """ the UserDefinedValueCondition class is an Value Condition used by the ValueTrigger
        
        Parameters
        ----------
            name (str): name of the parameter

            value (int): value to trigger on

            rule (Rule): condition rule of triggering 
            
        Attributes
        ----------
            name (str): name of the parameter

            value (int): value to trigger on

            rule (Rule): condition rule of triggering 

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,value,rule):
        """ initalize the UserDefinedValueCondition
        
            Parameters
            ----------
                name (str): name of the parameter

                value (int): value to trigger on

                rule (Rule): condition rule of triggering 
        """
        self.name = name
        self.value = value
        if rule not in Rule:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
    
    def get_attributes(self):
        """ returns the attributes of the UserDefinedValueCondition as a dict

        """
        basedict = {'name':self.name,'value':str(self.value)}
        basedict['rule'] = self.rule.name
        return basedict
    def get_element(self):
        """ returns the elementTree of the UserDefinedValueCondition

        """
        return ET.Element('UserDefinedValueCondition',attrib=self.get_attributes())

class TrafficSignalCondition(_ValueTriggerType):
    """ the TrafficSignalCondition class is an Value Condition used by the ValueTrigger
        
        Parameters
        ----------
            name (str): name of the traficsignal ???

            state (str): state of the signal

        Attributes
        ----------
            name (str): name of the traficsignal ???

            state (str): state of the signal

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,state):
        """ initalize the TrafficSignalCondition

            Parameters
            ----------
                name (str): name of the traficsignal ???

                state (str): state of the signal

        """
        self.name = name
        self.state = state
    
    def get_attributes(self):
        """ returns the attributes of the TrafficSignalCondition as a dict

        """
        return {'name':self.name,'state':self.state}

    def get_element(self):
        """ returns the elementTree of the TrafficSignalCondition

        """
        return ET.Element('TrafficSignalCondition',attrib=self.get_attributes())


class TrafficSignalControllerCondition(_ValueTriggerType):
    """ the TrafficSignalControllerCondition class is an Value Condition used by the ValueTrigger
        
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
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,trafficsignalref,phase):
        """ initalize the TrafficSignalControllerCondition
        
            Parameters
            ----------
                trafficsignalref (str): ???

                phase (str): ???

        """
        self.trafficsignalref = trafficsignalref
        self.phase = phase
    
    def get_attributes(self):
        """ returns the attributes of the TrafficSignalControllerCondition as a dict

        """
        return {'trafficSignalControllerRef':self.trafficsignalref,'phase':self.phase}

    def get_element(self):
        """ returns the elementTree of the TrafficSignalControllerCondition

        """
        return ET.Element('TrafficSignalControllerCondition',attrib=self.get_attributes())

