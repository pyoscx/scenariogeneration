import xml.etree.ElementTree as ET

from .utils import DynamicsConstrains, DynamicsShape



class _Action():
    """ Private class used to define an action, should not be used by the user.
        Used as a wrapper to create the extra elements needed
        
        Parameters
        ----------
            name (str): name of the action

            action (*Action): any action

        Attributes
        ----------
            name (str): name of the action

            action (*Action): any action

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,action):
        """ initalize _Action

        Parameters
        ----------
            name (str): name of the action

            action (*Action): any action

        """
        self.name = name
        self.action = action
        
    def get_attributes(self):
        """ returns the attributes of the _Action as a dict

        """
        return {'name':self.name}
        
    def get_element(self):
        """ returns the elementTree of the _Action

        """
        element = ET.Element('Action',attrib=self.get_attributes())
        element.append(self.action.get_element())
        return element

#LongitudinalAction

class AbsoluteSpeedAction():
    """ The AbsoluteSpeedAction class specifies a LongitudinalAction of type SpeedAction with an abosulte target speed
        
        Parameters
        ----------
            speed (float): the speed wanted

            transition_dynamics (TransitionDynamics): how the change should be made

        Attributes
        ----------

            speed (float): the speed wanted

            transition_dynamics (TransitionDynamics): how the change should be made

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,speed,transition_dynamics):
        """ initalize the AbsoluteSpeedAction

        Parameters
        ----------
            speed (float): the speed wanted

            transition_dynamics (TransitionDynamics): how the change should be made

        """
        self.speed = speed
        self.transition_dynamics = transition_dynamics
    def get_attributes(self):
        """ returns the attributes of the AbsoluteSpeedAction as a dict

        """
        return {'value':str(self.speed)}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSpeedAction

        """
        element = ET.Element('PrivateAction')
        longaction = ET.SubElement(element,'LongitudinalAction')
        speedaction = ET.SubElement(longaction,'SpeedAction')

        speedaction.append(self.transition_dynamics.get_element('SpeedActionDynamics'))
        speedactiontarget = ET.SubElement(speedaction,'SpeedActionTarget')
        
        ET.SubElement(speedactiontarget,'AbsoluteTargetSpeed',self.get_attributes())
        
        return element

class RelativeSpeedAction():
    """ The RelativeSpeedAction creates a LongitudinalAction of type SpeedAction with a relative target
        
        Parameters
        ----------
            transition_dynamics (TransitionDynamics): how the change should be made

            speed (float): the speed wanted

            target (str): the name of the relative target (used for relative speed)

            valuetype (str): the type of relative speed wanted (used for relative speed)

            continious (bool): if the controller tries to keep the relative speed 

        Attributes
        ----------
            speed (float): the speed wanted

            target (str): the name of the relative target (used for relative speed)

            valuetype (str): the type of relative speed wanted (used for relative speed)

            continious (bool): if the controller tries to keep the relative speed 

            transition_dynamics (TransitionDynamics): how the change should be made

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,speed,entity,transition_dynamics,valuetype='delta',continious=True):
        """ initalizes RelativeSpeedAction

        Parameters
        ----------
            speed (float): the speed wanted

            target (str): the name of the relative target (used for relative speed)

            transition_dynamics (TransitionDynamics): how the change should be made

            valuetype (str): the type of relative speed wanted (used for relative speed)

            continious (bool): if the controller tries to keep the relative speed 

        """
        self.speed = speed
        self.target = entity
        self.valuetype = valuetype
        self.continious = continious
        self.transition_dynamics = transition_dynamics

    
    def get_attributes(self):
        """ returns the attributes of the RelativeSpeedAction as a dict

        """
        return {'entityRef':self.target,'value':str(self.speed),'speedTargetValueType':self.valuetype,'continious':str(self.continious)}

    def get_element(self):
        """ returns the elementTree of the RelativeSpeedAction

        """
        element = ET.Element('PrivateAction')
        longaction = ET.SubElement(element,'LongitudinalAction')
        speedaction = ET.SubElement(longaction,'SpeedAction')
        speedaction.append(self.transition_dynamics.get_element('SpeedActionDynamics'))
        speedactiontarget = ET.SubElement(speedaction,'SpeedActionTarget')
        
        ET.SubElement(speedactiontarget,'RelativeTargetSpeed',self.get_attributes())
        
        return element
            
class LongitudinalDistanceAction():
    """ The LongitudinalDistanceAction creates a LongitudinalAction of type LongitudinalDistanceAction with a distance target
        
        Parameters
        ----------
            distance (float): distance to the entity
            
            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None

        Attributes
        ----------
            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

            continious (bool): if the controller tries to keep the relative speed 

            distance (float): the distance to the entity

            dynamic_constraint (DynamicsConstrains): Dynamics constraints of the action

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,distance,entity,freespace=True,continious=True,max_acceleration = None,max_deceleration = None,max_speed = None):
        """ initalize the LongitudinalDistanceAction
        
        Parameters
        ----------
            distance (float): distance to the entity
            
            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None

        """
        self.target = entity
        self.freespace = freespace
        self.continious = continious
        self.dynamic_constraint = DynamicsConstrains(max_acceleration,max_deceleration,max_speed)
        self.distance = distance   
        

    def get_attributes(self):
        """ returns the attributes of the LongitudinalDistanceAction as a dict

        """
        retdict = {}
        retdict['entryRef'] = self.target
        retdict['freespace'] = str(self.freespace)
        retdict['continious'] = str(self.continious)
        retdict['distance'] = str(self.distance)
        return retdict

    def get_element(self):
        """ returns the elementTree of the LongitudinalDistanceAction

        """
        element = ET.Element('PrivateAction')
        longact = ET.SubElement(element,'LongitudinalAction')

        longdistaction = ET.SubElement(longact,'LongitudinalDistanceAction',attrib=self.get_attributes())
        if self.dynamic_constraint.is_filled():
            longdistaction.append(self.dynamic_constraint.get_element())
        return element

class LongitudinalTimegapAction():
    """ The LongitudinalTimegapAction creates a LongitudinalAction of type LongitudinalDistanceAction with the timegap option
        
        Parameters
        ----------
            timegap (float): time to the target 

            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None

        Attributes
        ----------
            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

            continious (bool): if the controller tries to keep the relative speed 

            timegap (float): timegap to the target

            dynamic_constraint (DynamicsConstrains): Dynamics constraints of the action

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,timegap,entity,freespace=True,continious=True,max_acceleration = None,max_deceleration = None,max_speed = None):
        """ initalize the LongitudinalTimegapAction
        
        Parameters
        ----------
            timegap (float): time to the target 

            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None

        """
        self.target = entity
        self.freespace = freespace
        self.continious = continious
        self.timegap = timegap
        self.dynamic_constraint = DynamicsConstrains(max_acceleration,max_deceleration,max_speed)
        
       

    def get_attributes(self):
        """ returns the attributes of the LongitudinalTimegapAction as a dict

        """
        retdict = {}
        retdict['entryRef'] = self.target
        retdict['freespace'] = str(self.freespace)
        retdict['continious'] = str(self.continious)
        retdict['timeGap'] = str(self.timegap)
        return retdict

    def get_element(self):
        """ returns the elementTree of the LongitudinalTimegapAction

        """
        element = ET.Element('PrivateAction')
        longact = ET.SubElement(element,'LongitudinalAction')

        longdistaction = ET.SubElement(longact,'LongitudinalDistanceAction',attrib=self.get_attributes())
        if self.dynamic_constraint.is_filled():
            longdistaction.append(self.dynamic_constraint.get_element())
        return element

# lateral actions



class AbsoluteLaneChangeAction():
    """ the AbsoluteLaneChangeAction creates a LateralAction of type LaneChangeAction with an absolute target
        
        Parameters
        ----------
            lane (int): lane to change to

            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        Attributes
        ----------
            lane (int): lane to change to

            target_lane_offset (float): offset in the target lane is wanted
                
            transition_dynamics (TransitionDynamics): how the change should be made

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,lane,transition_dynamics,target_lane_offset=None):
        """ initalize AbsoluteLaneChangeAction

        Parameters
        ----------
            lane (int): lane to change to

            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        """

        self.lane = lane
        self.target_lane_offset = target_lane_offset
        self.transition_dynamics = transition_dynamics

    def get_attributes(self):
        """ returns the attributes of the AbsoluteLaneChangeAction as a dict

        """
        retdict = {}
        retdict['value'] = str(self.lane)

    
    def get_element(self):
        """ returns the elementTree of the AbsoluteLaneChangeAction

        """
        element = ET.Element('PrivateAction')
        laneoffset = {}
        lataction = ET.SubElement(element,'LateralAction')
        if self.target_lane_offset:
            laneoffset = {'targetLaneOffset':str(self.target_lane_offset)}
        lanechangeaction = ET.SubElement(lataction,'LaneChangeAction',attrib=laneoffset)
        
        lanechangeaction.append(self.transition_dynamics.get_element('LaneChangeActionDynamics'))
        lanchangetarget = ET.SubElement(lanechangeaction,'LaneChangeTarget')
        
        ET.SubElement(lanchangetarget,'AbsoluteTargetLane',self.get_attributes())
        return element


class RelativeLaneChangeAction():
    """ the RelativeLaneChangeAction creates a LateralAction of type LaneChangeAction with a relative target
        
        Parameters
        ----------
            lane (int): relative lane number

            entity (str): the entity to run relative to
            
            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        Attributes
        ----------
            value (int): lane to change to

            target (str): target for relative lane change

            target_lane_offset (float): offset in the target lane is wanted
                
            transition_dynamics (TransitionDynamics): how the change should be made

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,lane,entity,transition_dynamics,target_lane_offset=None):
        """ initalize RelativeLaneChangeAction

        Parameters
        ----------
            lane (int): relative lane number

            entity (str): the entity to run relative to
            
            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        """

        self.lane = lane
        self.target = entity
        self.target_lane_offset = target_lane_offset
        self.transition_dynamics = transition_dynamics


    def get_attributes(self):
        """ returns the attributes of the RelativeLaneChangeAction as a dict

        """
        retdict = {}
        retdict['lane'] = str(self.lane)
        retdict['entityRef'] = self.target
        return retdict
    
    def get_element(self):
        """ returns the elementTree of the RelativeLaneChangeAction

        """
        element = ET.Element('PrivateAction')
        laneoffset = {}
        lataction = ET.SubElement(element,'LateralAction')
        if self.target_lane_offset:
            laneoffset = {'targetLaneOffset':str(self.target_lane_offset)}
        lanechangeaction = ET.SubElement(lataction,'LaneChangeAction',attrib=laneoffset)
        
        lanechangeaction.append(self.transition_dynamics.get_element('LaneChangeActionDynamics'))
        lanchangetarget = ET.SubElement(lanechangeaction,'LaneChangeTarget')
        
        ET.SubElement(lanchangetarget,'RelativeTargetLane',self.get_attributes())
        return element



class AbsoluteLaneOffsetAction():
    """ the AbsoluteLaneOffsetAction class creates a LateralAction of type LaneOffsetAction with an absolute target
        
        Parameters
        ----------
            value (float): lateral offset of the lane

            shape (str): shape of the offset action

            constants (list of floats): the constants of the shape

            maxlatacc (float): maximum allowed lateral acceleration

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

        Attributes
        ----------
            continious (bool): if the controller tries to keep the relative speed 

            value (float): lateral offset of the lane

            target (str): the name of the entity (relative only)

            dynshape (DynamicsShape): the shape of the action

            maxlatacc (float): maximum allowed lateral acceleration

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,shape,constants,maxlatacc,continious = True):
        """ initalizes the LaneOffsetAction
            Parameters
            ----------
                value (float): lateral offset of the lane

                shape (str): shape of the offset action

                constants (list of floats): the constants of the shape

                maxlatacc (float): maximum allowed lateral acceleration

                continious (bool): if the controller tries to keep the relative speed 
                    Default: True
        """
        self.continious = continious
        self.value = value
        self.dynshape = DynamicsShape(shape,constants)
        self.maxlatacc = maxlatacc

    def get_attributes(self):
        """ returns the attributes of the LaneOffsetAction as a dict

        """
        retdict = {}
        retdict['value'] = str(self.value)
        return retdict
        
    def get_element(self):
        """ returns the elementTree of the LaneOffsetAction

        """
        element = ET.Element('PrivateAction')
        lataction = ET.SubElement(element,'LateralAction')
        laneoffsetaction = ET.SubElement(lataction,'LaneChangeAction',attrib={'continious':str(self.continious)})
        ET.SubElement(laneoffsetaction,'LaneOffsetActionDynamics',{'maxLateralAcc':str(self.maxlatacc),'dynamicsShape':self.dynshape.shape})
        ET.SubElement(laneoffsetaction,'AbsoluteTargetLaneOffset',self.get_attributes())

        return element

class RelativeLaneOffsetAction():
    """ the RelativeLaneOffsetAction class creates a LateralAction of type LaneOffsetAction with a relative target
        
        Parameters
        ----------
            value (float): relative lateral offset of the target

            entity (str): name of the entity

            shape (str): shape of the offset action

            constants (list of floats): the constants of the shape

            maxlatacc (float): maximum allowed lateral acceleration

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

        Attributes
        ----------
            continious (bool): if the controller tries to keep the relative speed 

            value (float): relative lateral offset of the arget

            target (str): the name of the entity

            dynshape (DynamicsShape): the shape of the action

            maxlatacc (float): maximum allowed lateral acceleration

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,entity,shape,constants,maxlatacc,continious = True):
        """ initalizes the LaneOffsetAction,

            Parameters
            ----------
                value (float): relative lateral offset of the target

                entity (str): name of the entity

                shape (str): shape of the offset action

                constants (list of floats): the constants of the shape

                maxlatacc (float): maximum allowed lateral acceleration

                continious (bool): if the controller tries to keep the relative speed 
                    Default: True
        """
        self.continious = continious
        self.value = value
        self.target = entity
        self.dynshape = DynamicsShape(shape,constants)
        self.maxlatacc = maxlatacc

    def get_attributes(self):
        """ returns the attributes of the LaneOffsetAction as a dict

        """
        retdict = {}
        retdict['value'] = str(self.value)
        retdict['entryRef'] = self.target
        return retdict
        
    def get_element(self):
        """ returns the elementTree of the LaneOffsetAction

        """
        element = ET.Element('PrivateAction')
        lataction = ET.SubElement(element,'LateralAction')
        laneoffsetaction = ET.SubElement(lataction,'LaneChangeAction',attrib={'continious':str(self.continious)})
        ET.SubElement(laneoffsetaction,'LaneOffsetActionDynamics',{'maxLateralAcc':str(self.maxlatacc),'dynamicsShape':self.dynshape.shape})
        ET.SubElement(laneoffsetaction,'RelativeTargetLaneOffset',self.get_attributes())

        return element


class LateralDistanceAction():
    """ 
        
        Parameters
        ----------
            entity (str): the target name

            distance (float): the lateral distance to the entity

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None
            
        Attributes
        ----------
            entity (str): the target name

            distance (float): the lateral distance to the entity

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

            continious (bool): if the controller tries to keep the relative speed 

            distance (float): if the distance metric is used

            timegap (float): if timegap metric is used

            dynamic_constraint (DynamicsConstrains): Dynamics constraints of the action


        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,entity,distance=None,freespace=True,continious=True,max_acceleration = None,max_deceleration = None,max_speed = None):
        """ initalizes the LateralDistanceAction

        Parameters
        ----------
            entity (str): the target name

            distance (float): the lateral distance to the entity

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None
        """
        self.distance = distance
        self.target = entity
        self.freespace = freespace
        self.continious = continious
        self.dynamic_constraint = DynamicsConstrains(max_acceleration,max_deceleration,max_speed)

    def get_attributes(self):
        """ returns the attributes of the LateralDistanceAction as a dict

        """
        retdict = {}
        retdict['entityRef'] = self.target
        retdict['freespace'] = str(self.freespace)
        retdict['continious'] = str(self.continious)
        if self.distance:
            retdict['distance'] = str(self.distance)
        return retdict

    def get_element(self):
        """ returns the elementTree of the LateralDistanceAction

        """
        element = ET.Element('PrivateAction')
        lataction = ET.SubElement(element,'LateralAction')
        lateraldistanceaction = ET.SubElement(lataction,'LateralDistanceAction',attrib=self.get_attributes())
        if self.dynamic_constraint.is_filled():
            lateraldistanceaction.append(self.dynamic_constraint.get_element())

        return element



# teleport
class TeleportAction():
    """ the TeleportAction creates the Teleport action of OpenScenario
        
        Parameters
        ----------
            position (*Position): any position object

        Attributes
        ----------
            position (*Position): any position object


        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,position):
        """ initalizes the TeleportAction

        Parameters
        ----------
            position (*Position): any position object

        """
        self.position = position

    def get_element(self):
        """ returns the elementTree of the TeleportAction

        """
        element = ET.Element('PrivateAction')
        telact = ET.SubElement(element,'TeleportAction')
        telact.append(self.position.get_element())
        return element
        
# not worked on yet
""" 
        
        Parameters
        ----------
            
        Attributes
        ----------

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
""" 
    class RoutingAction():,
    
        def __init__(self):
            pass


    # Visibility
    class VisibilityAction():
        def __init__(self,traffic = True,sensors = True,graphics = True):
            self.traffic = traffic
            self.sensors = sensors
            self.graphics = graphics

        def get_element(self):
            pass

    # syncronization
    class SynchronizeAction():
        def __init__(self,entity,entity_target,target,speed):
            self.target = entity
            self.target_pos = entity_target
            self.position = target
            self.speed = speed

        def get_element(self):
            pass
            
    # controller
    class ActivateControllerAction():
        def __init__(self):
            pass

    class ControllerAction():
        def __init__(self):
            pass
"""

