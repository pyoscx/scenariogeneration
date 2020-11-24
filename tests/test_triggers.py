import pytest

import pyoscx as OSC



def test_endofroadcond():
    cond = OSC.EndOfRoadCondition(20)
    OSC.prettyprint(cond.get_element())

def test_collision_condition():
    cond = OSC.CollisionCondition('Ego')
    OSC.prettyprint(cond.get_element())
    cond1 = OSC.CollisionCondition(OSC.ObjectType.pedestrian)
    OSC.prettyprint(cond1.get_element())

def test_offroadcondition():
    cond = OSC.OffroadCondition(20)
    OSC.prettyprint(cond.get_element())

def test_timeheadwaycondition():
    cond = OSC.TimeHeadwayCondition('Ego',20,OSC.Rule.equalTo,True,False)
    OSC.prettyprint(cond.get_element())

def test_timetocollisioncondition():
    cond = OSC.TimeToCollisionCondition(value=20,alongroute=True,rule=OSC.Rule.equalTo,entity='Ego')
    OSC.prettyprint(cond.get_element())

    cond = OSC.TimeToCollisionCondition(value=20,alongroute=True,rule=OSC.Rule.equalTo,position=OSC.WorldPosition())
    OSC.prettyprint(cond.get_element())

def test_accelerationcondition():
    cond = OSC.AccelerationCondition(1,OSC.Rule.greaterThan)
    OSC.prettyprint(cond.get_element())

def test_standstillcondition():
    cond = OSC.StandStillCondition(1)
    OSC.prettyprint(cond.get_element())

def test_speedcondition():
    cond = OSC.SpeedCondition(1,OSC.Rule.lessThan)
    OSC.prettyprint(cond.get_element())

def test_relativespeedcondition():
    cond = OSC.RelativeSpeedCondition(1,OSC.Rule.lessThan,'Ego')
    OSC.prettyprint(cond.get_element())

def test_traveleddistancecondition():
    cond = OSC.TraveledDistanceCondition(1)
    OSC.prettyprint(cond.get_element())

def test_reachpositioncondition():
    cond = OSC.ReachPositionCondition(OSC.WorldPosition(),0.01)
    OSC.prettyprint(cond.get_element())

def test_distancecondition():
    cond = OSC.DistanceCondition(1,OSC.Rule.lessThan,OSC.WorldPosition(),True,False)
    OSC.prettyprint(cond.get_element())

def test_relativedistancecondition():
    cond = OSC.RelativeDistanceCondition(1,OSC.Rule.equalTo,OSC.RelativeDistanceType.longitudinal,'Ego',True,False)
    OSC.prettyprint(cond.get_element())

def test_parametercondition():
    cond = OSC.ParameterCondition('MyParam',1,OSC.Rule.equalTo)
    OSC.prettyprint(cond.get_element())

def test_timeofdaycondition():
    cond = OSC.TimeOfDayCondition(OSC.Rule.equalTo,'12')
    OSC.prettyprint(cond.get_element())

def test_simulationtimecondition():
    cond = OSC.SimulationTimeCondition(1.2,OSC.Rule.greaterThan)
    OSC.prettyprint(cond.get_element())

def test_storyboardelementstatecondition():
    cond = OSC.StoryboardElementStateCondition(OSC.StoryboardElementType.action,'hej',OSC.StoryboardElementState.endTransition)
    OSC.prettyprint(cond.get_element())

def test_userdefinedcondition():
    cond = OSC.UserDefinedValueCondition('mytrigger',10,OSC.Rule.equalTo)
    OSC.prettyprint(cond.get_element())

def test_trafficsignalcondition():
    cond = OSC.TrafficSignalCondition('traflight','green')
    OSC.prettyprint(cond.get_element())

def test_trafficsignalconditioncontroller():
    cond = OSC.TrafficSignalControllerCondition('somereferens','yellow')
    OSC.prettyprint(cond.get_element())

def test_triggeringentities():
    cond =OSC.TriggeringEntities(OSC.TriggeringEntitiesRule.all)
    OSC.prettyprint(cond.get_element())

def test_entitytrigger():
    trigcond = OSC.TimeToCollisionCondition(10,OSC.Rule.equalTo,True,freespace=False,position=OSC.WorldPosition())
    trigger = OSC.EntityTrigger('mytesttrigger',0.2,OSC.ConditionEdge.rising,trigcond,'Target_1')
    OSC.prettyprint(trigger.get_element())

def test_valuetrigger():
    trigcond = OSC.ParameterCondition('something',2,OSC.Rule.equalTo)
    trigger = OSC.ValueTrigger('myvaluetrigger',0.2,OSC.ConditionEdge.rising,trigcond,triggeringpoint='stop')
    OSC.prettyprint(trigger.get_element())

def test_conditiongroup():
    condgr = OSC.ConditionGroup()

    trig1 = OSC.EntityTrigger('firsttrigger',1,OSC.ConditionEdge.rising,OSC.RelativeDistanceCondition(10,OSC.Rule.greaterThan,OSC.RelativeDistanceType.longitudinal,'Ego'),'Target')
    trig2 = OSC.EntityTrigger('secondtrigger',2,OSC.ConditionEdge.rising,OSC.SpeedCondition(2,OSC.Rule.equalTo),'Target')
    condgr.add_condition(trig1)
    condgr.add_condition(trig2)

    OSC.prettyprint(condgr.get_element())

def test_trigger():
    
    condgr = OSC.ConditionGroup()

    trig1 = OSC.EntityTrigger('firsttrigger',1,OSC.ConditionEdge.rising,OSC.RelativeDistanceCondition(10,OSC.Rule.greaterThan,OSC.RelativeDistanceType.longitudinal,'Ego'),'Target')
    trig2 = OSC.EntityTrigger('secondtrigger',2,OSC.ConditionEdge.rising,OSC.SpeedCondition(2,OSC.Rule.equalTo),'Target')

    condgr.add_condition(trig1)
    condgr.add_condition(trig2)

    condgr2 = OSC.ConditionGroup()

    trig3 = OSC.EntityTrigger('thirdtrigger',1,OSC.ConditionEdge.rising,OSC.RelativeDistanceCondition(10,OSC.Rule.greaterThan,OSC.RelativeDistanceType.longitudinal,'Ego'),'Target')
    trig4 = OSC.EntityTrigger('forthtrigger',2,OSC.ConditionEdge.rising,OSC.SpeedCondition(2,OSC.Rule.equalTo),'Target')

    condgr2.add_condition(trig3)
    condgr2.add_condition(trig4)

    trig = OSC.Trigger()

    trig.add_conditiongroup(condgr)
    trig.add_conditiongroup(condgr2)
    OSC.prettyprint(trig.get_element())