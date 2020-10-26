""" Notes:
    Simple example showing how to pick a route in a junction

    Some features used:
        Route
        AssingRouteAction
        LanePosition
"""

import pyoscx

### create catalogs
catalog = pyoscx.Catalog()
catalog.add_catalog('VehicleCatalog','../xosc/Catalogs/Vehicles')


### create road
road = pyoscx.RoadNetwork(roadfile="../xodr/fabriksgatan.xodr",scenegraph="../models/fabriksgatan.osgb")

### create parameters
paramdec = pyoscx.ParameterDeclarations()

## create entities

egoname = 'Ego'
targetname = 'Target'

entities = pyoscx.Entities()
entities.add_scenario_object(egoname,pyoscx.CatalogReference('VehicleCatalog','car_red'))

### create init

init = pyoscx.Init()

init.add_init_action(egoname,pyoscx.TeleportAction(pyoscx.LanePosition(50,0,1,0)))
init.add_init_action(egoname,pyoscx.AbsoluteSpeedAction(10,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)))

# create a router

ego_route = pyoscx.Route('ego_route')
ego_route.add_waypoint(pyoscx.LanePosition(30,0,1,0),pyoscx.RouteStrategy.fastest)
ego_route.add_waypoint(pyoscx.LanePosition(10,0,-1,1),pyoscx.RouteStrategy.fastest)


# create action
ego_action = pyoscx.AssingRouteAction(ego_route)


ego_event = pyoscx.Event('ego_event',pyoscx.Priority.overwrite)
ego_event.add_action('ego_route',ego_action)
ego_event.add_trigger(pyoscx.ValueTrigger('target_start',0,pyoscx.ConditionEdge.none,pyoscx.SimulationTimeCondition(1,pyoscx.Rule.greaterThan)))


## create the storyboard
ego_man = pyoscx.Maneuver('ego_man')
ego_man.add_event(ego_event)

sb = pyoscx.StoryBoard(init,pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(10,pyoscx.Rule.greaterThan),'stop'))
sb.add_maneuver(ego_man,egoname)

## create the scenario
sce = pyoscx.Scenario('adaptspeed_example','User',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

# display the scenario
pyoscx.prettyprint(sce.get_element())

# pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')