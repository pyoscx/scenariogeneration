# junction creator example 



from scenariogeneration import xodr, prettyprint
import numpy as np


junction_creator = xodr.CommonJunctionCreator(id = 100, name = 'my_junction',startnum=100)

junction_creator = xodr.JunctionCreator(id = 100, name = 'my_junction',startnum=100)


road1 = xodr.create_road(xodr.Line(100),1,right_lanes=2)
road2 = xodr.create_road(xodr.Arc(0.01,100),2)
road3 = xodr.create_road(xodr.Line(100),3,right_lanes=1)




road_case = 1

road_case = 3

road_case = 6

# junction_creator.add_incoming_road_circular_geometry(road1, radius = 20, angle=0, road_connection = 'predecessor')
# junction_creator.add_incoming_road_circular_geometry(road2, radius = 30, angle=1*np.pi, road_connection = 'predecessor')
# junction_creator.add_incoming_road_circular_geometry(road3, radius = 20, angle=1*np.pi/2, road_connection = 'predecessor')




if road_case == 1:
    road1 = xodr.create_road(xodr.Line(100),1,right_lanes=2)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2)
    road3 = xodr.create_road(xodr.Line(100),3,right_lanes=2)

    junction_creator.add_incoming_road_cartesian_geometry(road1,x=0,y=-5,heading=0, road_connection = 'successor')
    junction_creator.add_incoming_road_cartesian_geometry(road2,x=104,y=0,heading=1.1*np.pi, road_connection = 'predecessor')
    junction_creator.add_incoming_road_cartesian_geometry(road3,x=40,y=-80,heading=1*np.pi/2, road_connection = 'predecessor')

    junction_creator.add_connection(road_one_id=1, road_two_id=2)
    
    junction_creator.add_connection(road_one_id=2, road_two_id=3)
    junction_creator.add_connection(road_one_id=1, road_two_id=3, lane_one_id=-2, lane_two_id=-2)


if road_case == 2:
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=2)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2)
    road3 = xodr.create_road(xodr.Line(100),3,right_lanes=2)

    junction_creator.add_incoming_road_cartesian_geometry(road1,x=0,y=-5,heading=0, road_connection = 'predecessor')
    junction_creator.add_incoming_road_cartesian_geometry(road2,x=104,y=0,heading=1.1*np.pi, road_connection = 'successor')
    junction_creator.add_incoming_road_cartesian_geometry(road3,x=40,y=-80,heading=1*np.pi/2, road_connection = 'predecessor')

    junction_creator.add_connection(road_one_id=1, road_two_id=2)
    
    junction_creator.add_connection(road_one_id=2, road_two_id=3)
    junction_creator.add_connection(road_one_id=3, road_two_id=1, lane_one_id=-2, lane_two_id=2)


if road_case == 3:
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=2)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2)
    road3 = xodr.create_road(xodr.Line(100),3,right_lanes=2)

    junction_creator.add_incoming_road_cartesian_geometry(road1,x=0,y=-5,heading=0, road_connection = 'predecessor')
    junction_creator.add_incoming_road_cartesian_geometry(road2,x=104,y=0,heading=1.1*np.pi, road_connection = 'successor')
    junction_creator.add_incoming_road_cartesian_geometry(road3,x=40,y=-80,heading=1*np.pi/2, road_connection = 'predecessor')

    junction_creator.add_connection(road_one_id=1, road_two_id=2)
    
    junction_creator.add_connection(road_one_id=2, road_two_id=3)
    junction_creator.add_connection(road_one_id=1, road_two_id=3, lane_one_id=2, lane_two_id=-2)
    junction_creator.add_connection(road_one_id=1, road_two_id=3, lane_one_id=-1, lane_two_id=1)


if road_case == 4:
    road1 = xodr.create_road(xodr.Line(100),1,right_lanes=2, left_lanes=2)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2, right_lanes=2, left_lanes=2)
    road3 = xodr.create_road(xodr.Line(100),3,right_lanes=2, left_lanes=2)

    junction_creator.add_incoming_road_cartesian_geometry(road1,x=0,y=0,heading=0, road_connection = 'predecessor')
    junction_creator.add_incoming_road_cartesian_geometry(road2,x=80,y=0,heading=1.0001*np.pi, road_connection = 'predecessor')
    junction_creator.add_incoming_road_cartesian_geometry(road3,x=40,y=-40,heading=np.pi/2, road_connection = 'predecessor')
    junction_creator.add_connection(road_one_id=1, road_two_id=2)
    # junction_creator.add_connection(road_one_id=1, road_two_id=2, lane_one_id = 1, lane_two_id = -1)
    # junction_creator.add_connection(road_one_id=2, road_two_id=1, lane_one_id = 2, lane_two_id = -2)
    junction_creator.add_connection(road_one_id=1, road_two_id=3, lane_one_id = 2, lane_two_id = -2)
    junction_creator.add_connection(road_one_id=3, road_two_id=1, lane_one_id = 1, lane_two_id = -1)
    junction_creator.add_connection(road_one_id=2, road_two_id=3, lane_one_id = 1, lane_two_id = -1)
    junction_creator.add_connection(road_one_id=3, road_two_id=2, lane_one_id = 2, lane_two_id = -2)

if road_case == 5:
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=2)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2)
    road3 = xodr.create_road(xodr.Line(100),3,right_lanes=2)

    junction_creator.add_incoming_road_circular_geometry(road1,20,0, road_connection = 'predecessor')
    junction_creator.add_incoming_road_circular_geometry(road2,20,np.pi, road_connection = 'successor')
    junction_creator.add_incoming_road_circular_geometry(road3,30,np.pi/2, road_connection = 'predecessor')

    junction_creator.add_connection(road_one_id=1, road_two_id=2)
    
    junction_creator.add_connection(road_one_id=2, road_two_id=3)
    junction_creator.add_connection(road_one_id=1, road_two_id=3, lane_one_id=2, lane_two_id=-2)
    junction_creator.add_connection(road_one_id=1, road_two_id=3, lane_one_id=-1, lane_two_id=1)

if road_case == 6:
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=0,right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2)
    
    junction_creator.add_incoming_road_circular_geometry(road1,20,0, road_connection = 'predecessor')
    junction_creator.add_incoming_road_circular_geometry(road2,20,np.pi/2, road_connection = 'predecessor')
    
    junction_creator.add_connection(road_one_id=2, road_two_id=1)
    prettyprint(junction_creator.junction)


    prettyprint(junction_creator.junction)


odr = xodr.OpenDrive('myroad')
odr.add_road(road1)
odr.add_road(road2)
odr.add_road(road3)



for r in junction_creator.get_connecting_roads():
    odr.add_road(r)

odr.add_junction(junction_creator.junction)
odr.adjust_roads_and_lanes()


from scenariogeneration import esmini
esmini(odr,'../../esmini',car_density=10, window_size= '2200 60 800 600')
