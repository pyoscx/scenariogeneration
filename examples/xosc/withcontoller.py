"""
    An example how to add a sumo controller to an object


    Some features used:

    - Controller

    - Properties

"""

import os
from scenariogeneration import xosc, prettyprint

### create catalogs
catalog = xosc.Catalog()
catalog.add_catalog('VehicleCatalog','../xosc/Catalogs/Vehicles')



### create road
road = xosc.RoadNetwork(roadfile='../xodr/e6mini.xodr',scenegraph='../models/e6mini.osgb')


### create parameters
paramdec = xosc.ParameterDeclarations()

paramdec.add_parameter(xosc.Parameter('$HostVehicle',xosc.ParameterType.string,'car_white'))
paramdec.add_parameter(xosc.Parameter('$TargetVehicle',xosc.ParameterType.string,'car_red'))

### create vehicles

bb = xosc.BoundingBox(2,5,1.8,2.0,0,0.9)
fa = xosc.Axle(0.523598775598,0.8,1.68,2.98,0.4)
ba = xosc.Axle(0.523598775598,0.8,1.68,0,0.4)
white_veh = xosc.Vehicle('car_white',xosc.VehicleCategory.car,bb,fa,ba,69,10,10)

white_veh.add_property_file('../models/car_white.osgb')
white_veh.add_property('model_id','0')


bb = xosc.BoundingBox(1.8,4.5,1.5,1.3,0,0.8)
fa = xosc.Axle(0.523598775598,0.8,1.68,2.98,0.4)
ba = xosc.Axle(0.523598775598,0.8,1.68,0,0.4)
red_veh = xosc.Vehicle('car_red',xosc.VehicleCategory.car,bb,fa,ba,69,10,10)

red_veh.add_property_file('../models/car_red.osgb')
red_veh.add_property('model_id','2')


## create entities

egoname = 'Ego'
targetname = 'Target'
prop = xosc.Properties()
prop.add_property(name="esminiController", value="SumoController")
prop.add_file("../sumo_inputs/e6mini.sumocfg")
cont = xosc.Controller('mycontroler',prop)
# cont.dump_to_catalog('Controller.xosc','Controller','controllers','Mandolin')


entities = xosc.Entities()
entities.add_scenario_object(egoname,white_veh)
entities.add_scenario_object(targetname,red_veh,cont)


### create init

init = xosc.Init()
step_time = xosc.TransitionDynamics(xosc.DynamicsShapes.step,xosc.DynamicsDimension.time,1)

egospeed = xosc.AbsoluteSpeedAction(10,step_time)
egostart = xosc.TeleportAction(xosc.LanePosition(25,0,-3,0))


init.add_init_action(egoname,egospeed)
init.add_init_action(egoname,egostart)



## create the story
storyparam = xosc.ParameterDeclarations()
storyparam.add_parameter(xosc.Parameter('$owner',xosc.ParameterType.string,targetname))
story = xosc.Story('mystory',storyparam)


## create the storyboard
sb = xosc.StoryBoard(init)

## create the scenario
sce = xosc.Scenario('adapt_speed_example','Mandolin',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

# Print the resulting xml
prettyprint(sce.get_element())

# write the OpenSCENARIO file as xosc using current script name
sce.write_xml(os.path.basename(__file__).replace('.py','.xosc'))

# uncomment the following lines to display the scenario using esmini
# from scenariogeneration import esmini
# esmini(sce,os.path.join('esmini'))
