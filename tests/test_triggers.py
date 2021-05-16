import pytest

from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint


def test_endofroadcond():
    cond = OSC.EndOfRoadCondition(20)
    prettyprint(cond.get_element())

    cond2 = OSC.EndOfRoadCondition(20)
    cond3 = OSC.EndOfRoadCondition(23)
    assert cond == cond2
    assert cond != cond3

def test_collision_condition():
    cond = OSC.CollisionCondition('Ego')
    prettyprint(cond.get_element())
    cond1 = OSC.CollisionCondition(OSC.ObjectType.pedestrian)
    prettyprint(cond1.get_element())
    cond2 = OSC.CollisionCondition('Ego')
    assert cond == cond2
    assert cond != cond1

def test_offroadcondition():
    cond = OSC.OffroadCondition(20)
    prettyprint(cond.get_element())
    cond2 = OSC.OffroadCondition(20)
    cond3 = OSC.OffroadCondition(23)
    assert cond == cond2
    assert cond != cond3

def test_timeheadwaycondition():
    cond = OSC.TimeHeadwayCondition('Ego',20,OSC.Rule.equalTo,True,False)
    prettyprint(cond.get_element())
    cond2 = OSC.TimeHeadwayCondition('Ego',20,OSC.Rule.equalTo,True,False)
    cond3 = OSC.TimeHeadwayCondition('Ego',20,OSC.Rule.equalTo,True,True)
    assert cond == cond2
    assert cond != cond3

def test_timetocollisioncondition():
    cond = OSC.TimeToCollisionCondition(value=20,alongroute=True,rule=OSC.Rule.equalTo,entity='Ego')
    prettyprint(cond.get_element())
    cond2 = OSC.TimeToCollisionCondition(value=20,alongroute=True,rule=OSC.Rule.equalTo,entity='Ego')
    cond3 = OSC.TimeToCollisionCondition(value=20,alongroute=True,rule=OSC.Rule.equalTo,position=OSC.WorldPosition())
    prettyprint(cond3.get_element())
    assert cond == cond2
    assert cond != cond3

def test_accelerationcondition():
    cond = OSC.AccelerationCondition(1,OSC.Rule.greaterThan)
    prettyprint(cond.get_element())
    cond2 = OSC.AccelerationCondition(1,OSC.Rule.greaterThan)
    cond3 = OSC.AccelerationCondition(1,OSC.Rule.lessThan)
    assert cond == cond2
    assert cond != cond3

def test_standstillcondition():
    cond = OSC.StandStillCondition(1)
    prettyprint(cond.get_element())
    cond2 = OSC.StandStillCondition(1)
    cond3 = OSC.StandStillCondition(3)
    assert cond == cond2
    assert cond != cond3

def test_speedcondition():
    cond = OSC.SpeedCondition(1,OSC.Rule.lessThan)
    prettyprint(cond.get_element())
    cond2 = OSC.SpeedCondition(1,OSC.Rule.lessThan)
    cond3 = OSC.SpeedCondition(2,OSC.Rule.lessThan)
    assert cond == cond2
    assert cond != cond3

def test_relativespeedcondition():
    cond = OSC.RelativeSpeedCondition(1,OSC.Rule.lessThan,'Ego')
    prettyprint(cond.get_element())
    cond2 = OSC.RelativeSpeedCondition(1,OSC.Rule.lessThan,'Ego')
    cond3 = OSC.RelativeSpeedCondition(1,OSC.Rule.lessThan,'Ego2')
    assert cond == cond2
    assert cond != cond3

def test_traveleddistancecondition():
    cond = OSC.TraveledDistanceCondition(1)
    prettyprint(cond.get_element())
    cond2 = OSC.TraveledDistanceCondition(1)
    cond3 = OSC.TraveledDistanceCondition(3)
    assert cond == cond2
    assert cond != cond3

def test_reachpositioncondition():
    cond = OSC.ReachPositionCondition(OSC.WorldPosition(),0.01)
    prettyprint(cond.get_element())
    cond2 = OSC.ReachPositionCondition(OSC.WorldPosition(),0.01)
    cond3 = OSC.ReachPositionCondition(OSC.WorldPosition(),0.02)
    assert cond == cond2
    assert cond != cond3

def test_distancecondition():
    cond = OSC.DistanceCondition(1,OSC.Rule.lessThan,OSC.WorldPosition(),True,False)
    prettyprint(cond.get_element())
    cond2 = OSC.DistanceCondition(1,OSC.Rule.lessThan,OSC.WorldPosition(),True,False)
    cond3 = OSC.DistanceCondition(1,OSC.Rule.greaterThan,OSC.WorldPosition(),True,False)
    assert cond == cond2
    assert cond != cond3

def test_relativedistancecondition():
    cond = OSC.RelativeDistanceCondition(1,OSC.Rule.equalTo,OSC.RelativeDistanceType.longitudinal,'Ego',True,False)
    prettyprint(cond.get_element())
    cond2 = OSC.RelativeDistanceCondition(1,OSC.Rule.equalTo,OSC.RelativeDistanceType.longitudinal,'Ego',True,False)
    cond3 = OSC.RelativeDistanceCondition(1,OSC.Rule.equalTo,OSC.RelativeDistanceType.longitudinal,'Ego',True,True)
    assert cond == cond2
    assert cond != cond3

def test_parametercondition():
    cond = OSC.ParameterCondition('MyParam',1,OSC.Rule.equalTo)
    prettyprint(cond.get_element())
    cond2 = OSC.ParameterCondition('MyParam',1,OSC.Rule.equalTo)
    cond3 = OSC.ParameterCondition('MyParam',1,OSC.Rule.lessThan)
    assert cond == cond2
    assert cond != cond3

def test_timeofdaycondition():
    cond = OSC.TimeOfDayCondition(OSC.Rule.equalTo,'12')
    prettyprint(cond.get_element())
    cond2 = OSC.TimeOfDayCondition(OSC.Rule.equalTo,'12')
    cond3 = OSC.TimeOfDayCondition(OSC.Rule.equalTo,'13')
    assert cond == cond2
    assert cond != cond3

def test_simulationtimecondition():
    cond = OSC.SimulationTimeCondition(1.2,OSC.Rule.greaterThan)
    prettyprint(cond.get_element())
    cond2 = OSC.SimulationTimeCondition(1.2,OSC.Rule.greaterThan)
    cond3 = OSC.SimulationTimeCondition(1.3,OSC.Rule.greaterThan)
    assert cond == cond2
    assert cond != cond3

def test_storyboardelementstatecondition():
    cond = OSC.StoryboardElementStateCondition(OSC.StoryboardElementType.action,'hej',OSC.StoryboardElementState.endTransition)
    cond2 = OSC.StoryboardElementStateCondition(OSC.StoryboardElementType.action,'hej',OSC.StoryboardElementState.endTransition)
    cond3 = OSC.StoryboardElementStateCondition(OSC.StoryboardElementType.action,'hej',OSC.StoryboardElementState.startTransition)
    prettyprint(cond.get_element())
    assert cond == cond2
    assert cond != cond3

def test_userdefinedcondition():
    cond = OSC.UserDefinedValueCondition('mytrigger',10,OSC.Rule.equalTo)
    prettyprint(cond.get_element())
    cond2 = OSC.UserDefinedValueCondition('mytrigger',10,OSC.Rule.equalTo)
    cond3 = OSC.UserDefinedValueCondition('mytrigger',12,OSC.Rule.equalTo)
    assert cond == cond2
    assert cond != cond3

def test_trafficsignalcondition():
    cond = OSC.TrafficSignalCondition('traflight','green')
    prettyprint(cond.get_element())
    cond2 = OSC.TrafficSignalCondition('traflight','green')
    cond3 = OSC.TrafficSignalCondition('traflight','red')
    assert cond == cond2
    assert cond != cond3
    
def test_trafficsignalconditioncontroller():
    cond = OSC.TrafficSignalControllerCondition('somereferens','yellow')
    prettyprint(cond.get_element())
    cond2 = OSC.TrafficSignalControllerCondition('somereferens','yellow')
    cond3 = OSC.TrafficSignalControllerCondition('somereferens','green')
    assert cond == cond2
    assert cond != cond3

def test_triggeringentities():
    cond =OSC.TriggeringEntities(OSC.TriggeringEntitiesRule.all)
    prettyprint(cond.get_element())
    cond2 =OSC.TriggeringEntities(OSC.TriggeringEntitiesRule.all)
    cond3 =OSC.TriggeringEntities(OSC.TriggeringEntitiesRule.any)

    assert cond == cond2
    assert cond != cond3

def test_entitytrigger():
    trigcond = OSC.TimeToCollisionCondition(10,OSC.Rule.equalTo,True,freespace=False,position=OSC.WorldPosition())
    trigger = OSC.EntityTrigger('mytesttrigger',0.2,OSC.ConditionEdge.rising,trigcond,'Target_1')
    prettyprint(trigger.get_element())
    trigger2 = OSC.EntityTrigger('mytesttrigger',0.2,OSC.ConditionEdge.rising,trigcond,'Target_1')
    trigger3 = OSC.EntityTrigger('mytesttrigger',0.3,OSC.ConditionEdge.rising,trigcond,'Target_1')

    assert trigger == trigger2
    assert trigger != trigger3

def test_valuetrigger():
    trigcond = OSC.ParameterCondition('something',2,OSC.Rule.equalTo)
    trigger = OSC.ValueTrigger('myvaluetrigger',0.2,OSC.ConditionEdge.rising,trigcond,triggeringpoint='stop')
    prettyprint(trigger.get_element())
    trigger2 = OSC.ValueTrigger('myvaluetrigger',0.2,OSC.ConditionEdge.rising,trigcond,triggeringpoint='stop')
    trigger3 = OSC.ValueTrigger('myvaluetrigger',0.3,OSC.ConditionEdge.rising,trigcond,triggeringpoint='stop')
    assert trigger == trigger2
    assert trigger != trigger3

def test_conditiongroup():
    condgr = OSC.ConditionGroup()

    trig1 = OSC.EntityTrigger('firsttrigger',1,OSC.ConditionEdge.rising,OSC.RelativeDistanceCondition(10,OSC.Rule.greaterThan,OSC.RelativeDistanceType.longitudinal,'Ego'),'Target')
    trig2 = OSC.EntityTrigger('secondtrigger',2,OSC.ConditionEdge.rising,OSC.SpeedCondition(2,OSC.Rule.equalTo),'Target')
    condgr.add_condition(trig1)
    condgr.add_condition(trig2)

    prettyprint(condgr.get_element())

    condgr2 = OSC.ConditionGroup()
    condgr3 = OSC.ConditionGroup()
    condgr2.add_condition(trig1)
    condgr2.add_condition(trig2)
    condgr3.add_condition(trig2)
    assert condgr == condgr2
    assert condgr != condgr3

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
    prettyprint(trig.get_element())
    
    trig2 = OSC.Trigger()
    trig3 = OSC.Trigger()
    trig2.add_conditiongroup(condgr)
    trig2.add_conditiongroup(condgr2)
    trig3.add_conditiongroup(condgr2)

    assert trig == trig2
    assert trig != trig3