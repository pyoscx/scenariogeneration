""" Notes:
    Example of a synchronizing two vehicles at one point

    Some features used:
        AbsoluteSynchronizeAction

        
"""

import pyoscx


### create catalogs
catalog = pyoscx.Catalog()
catalog.add_catalog('VehicleCatalog','../xosc/Catalogs/Vehicles')

### create road
road = pyoscx.RoadNetwork(roadfile="../xodr/e6mini.xodr",scenegraph="../models/e6mini.osgb")

### create parameters
paramdec = pyoscx.ParameterDeclarations()

## create entities

egoname = 'Ego'
targetname = 'Target'

entities = pyoscx.Entities()
entities.add_scenario_object(egoname,pyoscx.CatalogReference('VehicleCatalog','car_red'))
entities.add_scenario_object(targetname,pyoscx.CatalogReference('VehicleCatalog','car_blue'))

### create init

init = pyoscx.Init()

init.add_init_action(egoname,pyoscx.TeleportAction(pyoscx.LanePosition(50,0,-2,0)))
init.add_init_action(egoname,pyoscx.AbsoluteSpeedAction(10,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))

init.add_init_action(targetname,pyoscx.TeleportAction(pyoscx.LanePosition(30,0,-3,0)))
init.add_init_action(targetname,pyoscx.AbsoluteSpeedAction(20,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))


## target action

tar_action = pyoscx.AbsoluteSynchronizeAction(egoname,pyoscx.LanePosition(200,0,-1,0),pyoscx.LanePosition(200,0,-2,0),10)

tar_event = pyoscx.Event('target_event',pyoscx.Priority.overwrite)
tar_event.add_trigger(pyoscx.ValueTrigger('ego_start',0,pyoscx.ConditionEdge.none,pyoscx.SimulationTimeCondition(3,pyoscx.Rule.greaterThan)))
tar_event.add_action('tar_action',tar_action)

tar_man = pyoscx.Maneuver('target_man')
tar_man.add_event(tar_event)

tar_man_gr = pyoscx.ManeuverGroup('target_man_gr')
tar_man_gr.add_maneuver(tar_man)
tar_man_gr.add_actor(targetname)


## act
act = pyoscx.Act('myact',pyoscx.ValueTrigger('start',0,pyoscx.ConditionEdge.none,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan)))

act.add_maneuver_group(tar_man_gr)
## create the storyboard
sb = pyoscx.StoryBoard(init,pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(20,pyoscx.Rule.greaterThan),'stop'))
sb.add_act(act)



## create the scenario
sce = pyoscx.Scenario('adaptspeed_example','User',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

# display the scenario
pyoscx.prettyprint(sce.get_element())

# if you want to save it
# sce.write_xml('myfirstscenario.xml',True)

# if you have esmini downloaded and want to see the scenario

# pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')
