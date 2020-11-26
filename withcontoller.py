""" Notes:
    An example how to add a sumo controller to an object


    Some features used:
        Controller 
        Properties

"""


import pyoscx   

### create catalogs
catalog = pyoscx.Catalog()
catalog.add_catalog('VehicleCatalog','../xosc/Catalogs/Vehicles')



### create road
road = pyoscx.RoadNetwork(roadfile='../xodr/e6mini.xodr',scenegraph='../models/e6mini.osgb')


### create parameters
paramdec = pyoscx.ParameterDeclarations()

paramdec.add_parameter(pyoscx.Parameter('$HostVehicle',pyoscx.ParameterType.string,'car_white'))
paramdec.add_parameter(pyoscx.Parameter('$TargetVehicle',pyoscx.ParameterType.string,'car_red'))

### create vehicles

bb = pyoscx.BoundingBox(2,5,1.8,2.0,0,0.9)
fa = pyoscx.Axle(30,0.8,1.68,2.98,0.4, name='FrontAxle')
ba = pyoscx.Axle(30,0.8,1.68,0,0.4, name='RearAxle')
white_veh = pyoscx.Vehicle('car_white',pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)

white_veh.add_property_file('../models/car_white.osgb')
white_veh.add_property('model_id','0')


bb = pyoscx.BoundingBox(1.8,4.5,1.5,1.3,0,0.8)
fa = pyoscx.Axle(30,0.8,1.68,2.98,0.4, name='FrontAxle')
ba = pyoscx.Axle(30,0.8,1.68,0,0.4, name='RearAxle')
red_veh = pyoscx.Vehicle('car_red',pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)

red_veh.add_property_file('../models/car_red.osgb')
red_veh.add_property('model_id','2')


## create entities

egoname = 'Ego'
targetname = 'Target'
prop = pyoscx.Properties()
prop.add_property(name="esminiController", value="SumoController")
prop.add_file("../sumo_inputs/e6mini.sumocfg")
cont = pyoscx.Controller('mycontroler',prop)
cont.dump_to_catalog('Controller.xosx','Controller','controllers','Mandolin')
# pyoscx.prettyprint(cont.get_element())
pyoscx.prettyprint(cont.get_element())
entities = pyoscx.Entities()
entities.add_scenario_object(egoname,white_veh)
entities.add_scenario_object(targetname,red_veh,cont)


### create init

init = pyoscx.Init()
step_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)

egospeed = pyoscx.AbsoluteSpeedAction(10,step_time)
egostart = pyoscx.TeleportAction(pyoscx.LanePosition(25,0,-3,0))


init.add_init_action(egoname,egospeed)
init.add_init_action(egoname,egostart)



## create the story
storyparam = pyoscx.ParameterDeclarations()
storyparam.add_parameter(pyoscx.Parameter('$owner',pyoscx.ParameterType.string,targetname))
story = pyoscx.Story('mystory',storyparam)


## create the storyboard
sb = pyoscx.StoryBoard(init)

## create the scenario
sce = pyoscx.Scenario('adapt_speed_example','Mandolin',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)
# display the scenario
pyoscx.prettyprint(sce.get_element())

# if you want to save it
# sce.write_xml('exampel_with_controller.xml',True)

# if you have esmini downloaded and want to see the scenario (add path to esmini as second argument)
# pyoscx.esminiRunner(sce)
# pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')