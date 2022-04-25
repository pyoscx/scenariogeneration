# junction creator example 


from scenariogeneration import xodr, prettyprint
import numpy as np

radius = 100

junction_creator1 = xodr.JunctionCreator(id = 100, name = 'my_junction')
junction_creator2 = xodr.JunctionCreator(id = 200, name = 'my_junction2', startnum = 200)
junction_creator3 = xodr.JunctionCreator(id = 300, name = 'my_junction3', startnum = 300)
junction_creator4 = xodr.JunctionCreator(id = 400, name = 'my_junction4', startnum = 400)

road1 = xodr.create_road(xodr.Line(100),1)
road2 = xodr.create_road(xodr.Line(100),2)
road3 = xodr.create_road(xodr.Line(100),3)
road4 = xodr.create_road([xodr.Line(100),xodr.Arc(1/radius,angle=np.pi/2),xodr.Line(200+2*radius), xodr.Arc(1/radius,angle=np.pi/2), xodr.Line(100) ],4)
road5 = xodr.create_road([xodr.Line(100),xodr.Arc(-1/radius,angle=np.pi/2),xodr.Line(100)],5)
road6 = xodr.create_road([xodr.Line(100),xodr.Arc(-1/radius,angle=np.pi/2),xodr.Line(100)] ,6)


road1.add_predecessor(xodr.ElementType.junction, 100)
road1.add_successor(xodr.ElementType.junction,400)

road2.add_predecessor(xodr.ElementType.junction, 100)
road2.add_successor(xodr.ElementType.junction,200)

road3.add_predecessor(xodr.ElementType.junction, 100)
road3.add_successor(xodr.ElementType.junction, 300)


road4.add_predecessor(xodr.ElementType.junction, 200)
road4.add_successor(xodr.ElementType.junction,400)

road5.add_predecessor(xodr.ElementType.junction, 200)
road5.add_successor(xodr.ElementType.junction,300)

road6.add_predecessor(xodr.ElementType.junction, 300)
road6.add_successor(xodr.ElementType.junction,400)

junction_creator1.add_incoming_road_circular_junction(road1, radius = radius, angle=0)
junction_creator1.add_incoming_road_circular_junction(road2, radius = radius, angle=np.pi)
junction_creator1.add_incoming_road_circular_junction(road3, radius = radius, angle=np.pi/2)

junction_creator2.add_incoming_road_circular_junction(road2, radius = radius, angle=0)
junction_creator2.add_incoming_road_circular_junction(road4, radius = radius, angle=3*np.pi/2)
junction_creator2.add_incoming_road_circular_junction(road5, radius = radius, angle=np.pi/2)

junction_creator3.add_incoming_road_circular_junction(road3, radius = radius, angle=0)
junction_creator3.add_incoming_road_circular_junction(road5, radius = radius, angle=-np.pi/2)
junction_creator3.add_incoming_road_circular_junction(road6, radius = radius, angle=np.pi/2)

junction_creator4.add_incoming_road_circular_junction(road1, radius = radius, angle=0)
junction_creator4.add_incoming_road_circular_junction(road4, radius = radius, angle=np.pi/2)
junction_creator4.add_incoming_road_circular_junction(road6, radius = radius, angle=-np.pi/2)

junction_creator1.add_connection(road_one_id=1, road_two_id=2)
junction_creator1.add_connection(road_one_id=1, road_two_id=2)
junction_creator1.add_connection(road_one_id=1, road_two_id=3)
junction_creator1.add_connection(road_one_id=2, road_two_id=3)

junction_creator2.add_connection(2,4)
junction_creator2.add_connection(2,5)
junction_creator2.add_connection(4,5)

junction_creator3.add_connection(3,5)
junction_creator3.add_connection(5,6)
junction_creator3.add_connection(3,6)

junction_creator4.add_connection(1,6)
junction_creator4.add_connection(4,6)
junction_creator4.add_connection(4,1)

junction1 = xodr.create_junction(junction_creator1.get_connecting_roads(), 100, [road1, road2, road3])


junction2 = xodr.create_junction(junction_creator2.get_connecting_roads(), 200, [road2, road4, road5])
junction3 = xodr.create_junction(junction_creator3.get_connecting_roads(), 300, [road3,  road5, road6])
junction4 = xodr.create_junction(junction_creator4.get_connecting_roads(), 400, [road1,  road4, road6])

odr = xodr.OpenDrive('myroad')
odr.add_road(road1)
odr.add_road(road2)
odr.add_road(road3)
odr.add_road(road4)
odr.add_road(road5)
odr.add_road(road6)

for r in junction_creator1.get_connecting_roads():
    odr.add_road(r)

for r in junction_creator2.get_connecting_roads():
    odr.add_road(r)

for r in junction_creator3.get_connecting_roads():
    odr.add_road(r)

for r in junction_creator4.get_connecting_roads():
    odr.add_road(r)

# odr.add_junction(junction1)
# odr.add_junction(junction2)
# odr.add_junction(junction3)
# odr.add_junction(junction4)
odr.add_junction(junction_creator1.junction)
odr.add_junction(junction_creator2.junction)
odr.add_junction(junction_creator3.junction)
odr.add_junction(junction_creator4.junction)
odr.adjust_roads_and_lanes()
prettyprint(junction4)
prettyprint(junction_creator4.junction)


from scenariogeneration import esmini
esmini(odr,'esmini', window_size='2000 50 800 400')