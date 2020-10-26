""" Notes:

    Example showing how to create "repeating traffic" if a car goes to the end of the road
    Some features used:
        multiple execusions 
        End of road
        Teleport
        LanePosition
        
"""

import pyoscx

### create catalogs
catalog = pyoscx.Catalog()
catalog.add_catalog('VehicleCatalog','../xosc/Catalogs/Vehicles')

### create road
road = pyoscx.RoadNetwork(roadfile='../xodr/straight_500m.xodr',scenegraph='../models/straight_500m.osgb')

### create parameters
paramdec = pyoscx.ParameterDeclarations()

## loop to create cars, init and their reset actions

egoname = 'Ego'

targetname = 'Target'
entities = pyoscx.Entities()
init = pyoscx.Init()
act = pyoscx.Act('indef traffic')

for i in range(20):
    entities.add_scenario_object(targetname+str(i),pyoscx.CatalogReference('VehicleCatalog','car_yellow'))

    init.add_init_action(targetname+str(i),pyoscx.TeleportAction(pyoscx.LanePosition(100+i*20,0,-1,1)))
    init.add_init_action(targetname+str(i),pyoscx.AbsoluteSpeedAction(60,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))

    event = pyoscx.Event('speedchange',pyoscx.Priority.overwrite,maxexecution=10)
    event.add_action('restart',pyoscx.TeleportAction(pyoscx.LanePosition(0,0,-1,1)))
    
    trig_cond = pyoscx.EndOfRoadCondition(0)

    event.add_trigger(pyoscx.EntityTrigger('trigger',0,pyoscx.ConditionEdge.rising,trig_cond,targetname+str(i)))

    man = pyoscx.Maneuver('mymaneuver')
    man.add_event(event)


    mangr = pyoscx.ManeuverGroup('mangr',maxexecution=3)
    mangr.add_maneuver(man)
    mangr.add_actor(targetname+str(i))
    act.add_maneuver_group(mangr)
    

## create the storyboard
sb = pyoscx.StoryBoard(init,pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(100,pyoscx.Rule.greaterThan),'stop'))

sb.add_act(act)
## create the scenario
sce = pyoscx.Scenario('adaptspeed_example','User',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

# display the scenario
pyoscx.prettyprint(sce.get_element())


# pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')
