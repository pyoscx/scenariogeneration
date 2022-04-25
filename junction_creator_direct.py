# junction creator example 


from scenariogeneration import xodr
import numpy as np

junction_creator = xodr.DirectJunctionCreator(id = 100, name = 'my_junction')

road_case = 2
if road_case == 1:
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=2,right_lanes=2)
    road2 = xodr.create_road(xodr.Line(100),2, left_lanes=2, right_lanes=2)
    road3 = xodr.create_road(xodr.Arc(-0.001,100),3, left_lanes=0, right_lanes=1)


    road1.add_successor(xodr.ElementType.junction, 100)
    road2.add_predecessor(xodr.ElementType.junction, 100)
    road3.add_predecessor(xodr.ElementType.junction, 100)


    ### change the offset to be a dict with direct junction
    junction_creator.add_connection(road1, road2)
    junction_creator.add_connection(road1, road3, -3, -1)


    odr = xodr.OpenDrive('myroad')
    odr.add_road(road3)
    odr.add_road(road1)
    odr.add_road(road2)
else:
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=2,right_lanes=2)
    road2 = xodr.create_road(xodr.Line(100),2, left_lanes=3, right_lanes=2)
    road3 = xodr.create_road(xodr.Arc(-0.001,100),3, left_lanes=0, right_lanes=1)
    # road4 = xodr.create_road(xodr.Arc(0.001,100),4, left_lanes=0, right_lanes=1)


    road1.add_successor(xodr.ElementType.junction, 100)
    road2.add_predecessor(xodr.ElementType.junction, 100)
    road3.add_predecessor(xodr.ElementType.junction, 100)


    ### change the offset to be a dict with direct junction
    junction_creator.add_connection(road1, road2)
    junction_creator.add_connection(road2, road3, 3, -1)
    # junction_creator.add_connection(road2, road4, 3, 1)


    odr = xodr.OpenDrive('myroad')
    
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)
    # odr.add_road(road4)





### change the offset to be a dict with direct junction
junction_creator.add_connection(road1, road2, [-2,-1,1,2], [-2,-1,1,2])
junction_creator.add_connection(road1, road3, -3, -1)


odr = xodr.OpenDrive('myroad')
odr.add_road(road2)
odr.add_road(road1)
odr.add_road(road3)


odr.add_junction(junction_creator.junction)
odr.adjust_roads_and_lanes()


from scenariogeneration import esmini
<<<<<<< HEAD
esmini(odr,'../../esmini', window_size='2000 50 800 400')
=======
esmini(odr,'esmini', window_size='2000 50 800 400')
>>>>>>> typo fix
