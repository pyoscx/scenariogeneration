import xml.etree.ElementTree as ET

from .utils import DynamicsConstrains, TimeReference

from .enumerations import DynamicsShapes, SpeedTargetValueType, FollowMode


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


#### Private Actions ####

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
        retdict['entityRef'] = self.target
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
        retdict['entityRef'] = self.target
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
        return retdict
    
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
        retdict['value'] = str(self.lane)
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

            shape (DynamicsShapes): shape of the offset action

            maxlatacc (float): maximum allowed lateral acceleration

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

        Attributes
        ----------
            continious (bool): if the controller tries to keep the relative speed 

            value (float): lateral offset of the lane

            target (str): the name of the entity (relative only)

            dynshape (DynamicsShapes): the shape of the action

            maxlatacc (float): maximum allowed lateral acceleration

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,shape,maxlatacc,continious = True):
        """ initalizes the LaneOffsetAction
            Parameters
            ----------
                value (float): lateral offset of the lane

                shape (DynamicsShapes): shape of the offset action

                maxlatacc (float): maximum allowed lateral acceleration

                continious (bool): if the controller tries to keep the relative speed 
                    Default: True
        """
        self.continious = continious
        self.value = value
        if shape not in DynamicsShapes:
            raise ValueError(shape + '; is not a valid shape.')
        self.dynshape = shape
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
        laneoffsetaction = ET.SubElement(lataction,'LaneOffsetAction',attrib={'continious':str(self.continious)})
        ET.SubElement(laneoffsetaction,'LaneOffsetActionDynamics',{'maxLateralAcc':str(self.maxlatacc),'dynamicsShape':self.dynshape.name})
        laneoftarget = ET.SubElement(laneoffsetaction,'LaneOffsetTarget')
        ET.SubElement(laneoftarget,'AbsoluteTargetLaneOffset',self.get_attributes())

        return element

class RelativeLaneOffsetAction():
    """ the RelativeLaneOffsetAction class creates a LateralAction of type LaneOffsetAction with a relative target
        
        Parameters
        ----------
            value (float): relative lateral offset of the target

            entity (str): name of the entity

            shape (str): shape of the offset action

            maxlatacc (float): maximum allowed lateral acceleration

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

        Attributes
        ----------
            continious (bool): if the controller tries to keep the relative speed 

            value (float): relative lateral offset of the arget

            target (str): the name of the entity

            dynshape (str): the shape of the action

            maxlatacc (float): maximum allowed lateral acceleration

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,entity,shape,maxlatacc,continious = True):
        """ initalizes the LaneOffsetAction,

            Parameters
            ----------
                value (float): relative lateral offset of the target

                entity (str): name of the entity

                shape (str): shape of the offset action

                maxlatacc (float): maximum allowed lateral acceleration

                continious (bool): if the controller tries to keep the relative speed 
                    Default: True
        """
        self.continious = continious
        self.value = value
        self.target = entity
        if shape not in DynamicsShapes:
            raise ValueError(shape + '; is not a valid shape.')
        self.dynshape = shape
        self.maxlatacc = maxlatacc

    def get_attributes(self):
        """ returns the attributes of the LaneOffsetAction as a dict

        """
        retdict = {}
        retdict['value'] = str(self.value)
        retdict['entityRef'] = self.target
        return retdict
        
    def get_element(self):
        """ returns the elementTree of the LaneOffsetAction

        """
        element = ET.Element('PrivateAction')
        lataction = ET.SubElement(element,'LateralAction')
        laneoffsetaction = ET.SubElement(lataction,'LaneOffsetAction',attrib={'continious':str(self.continious)})
        ET.SubElement(laneoffsetaction,'LaneOffsetActionDynamics',{'maxLateralAcc':str(self.maxlatacc),'dynamicsShape':self.dynshape.name})
        laneoftarget = ET.SubElement(laneoffsetaction,'LaneOffsetTarget')
        ET.SubElement(laneoftarget,'RelativeTargetLaneOffset',attrib=self.get_attributes())

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



# Routing actions

class AssingRouteAction():
    """ AssingRouteAction creates a RouteAction of type AssingRouteAction

        Parameters
        ----------
            route (Route, or CatalogReference): the route to follow

        Attributes
        ----------
            route (Route, or CatalogReference): the route to follow


        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,route):
        """ initalizes the AssingRouteAction

            Parameters
            ----------
                route (Route, or CatalogReference): the route to follow

        """
        self.route = route

    def get_element(self):
        """ returns the elementTree of the AssingRouteAction

        """
        element = ET.Element('PrivateAction')
        routeaction = ET.SubElement(element,'RoutingAction')
        assignrouteaction = ET.SubElement(routeaction,'AssignRoutingAction')
        assignrouteaction.append(self.route.get_element())

        return element


class AcquirePositionAction():
    """ AcquirePositionAction creates a RouteAction of type AcquirePositionAction
        
        Parameters
        ----------
            position (*Position): target position

        Attributes
        ----------
            position (*Position): target position

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,position):
        """ initalizes the AssingRouteAction

            Parameters
            ----------
                position (*Position): target position

        """
        self.position = position

    def get_element(self):
        """ returns the elementTree of the AssingRouteAction

        """
        element = ET.Element('PrivateAction')
        routeaction = ET.SubElement(element,'RoutingAction')
        posaction = ET.SubElement(routeaction,'AcquirePositionAction')
        posaction.append(self.position.get_element())

        return element



class FollowTrajectoryAction():
    """ FollowTrajectoryAction creates a RouteAction of type FollowTrajectoryAction

        Parameters
        ----------
            trajectory (Trajectory, or CatalogReference): the trajectory to follow

            following_mode (FollowMode): the following mode of the action

            referece_domain (ReferenceContext): how to follow
                Default: None
            scale (double): scalefactor of the timeings (must be combined with referece_domain and offset)
                Default: None
            offset (double): offset for time values (must be combined with referece_domain and scale)
                Default: None

        Attributes
        ----------
            trajectory (Trajectory, or CatalogReference): the trajectory to follow

            following_mode (str): the following mode of the action

            timeref (TimeReference): the time reference of the trajectory

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,trajectory,following_mode,referece_domain=None,scale=None,offset=None):
        """ initalize the FollowTrajectoryAction 

            Parameters
            ----------
                trajectory (Trajectory, or CatalogReference): the trajectory to follow

                following_mode (str): the following mode of the action

                referece_domain (str): absolute or relative time reference (must be combined with scale and offset)
                    Default: None
                scale (double): scalefactor of the timeings (must be combined with referece_domain and offset)
                    Default: None
                offset (double): offset for time values (must be combined with referece_domain and scale)
                    Default: None
        """
        if following_mode not in FollowMode:
            ValueError(str(following_mode) + ' is not a valied following mode.')
        self.trajectory = trajectory
        self.following_mode = following_mode

        self.timeref = TimeReference(referece_domain,scale,offset)

    def get_element(self):
        """ returns the elementTree of the AssingRouteAction

        """
        element = ET.Element('PrivateAction')
        routeaction = ET.SubElement(element,'RoutingAction')
        trajaction = ET.SubElement(routeaction,'FollowTrajectoryAction')
        trajaction.append(self.trajectory.get_element())
        trajaction.append(self.timeref.get_element())
        ET.SubElement(trajaction,'TrajectoryFollowingMode',attrib={'name':self.following_mode.name})

        return element





class ActivateControllerAction():
    """ ActivateControllerAction creates a ActivateControllerAction of open scenario
        
        Parameters
        ----------
            lateral (boolean): activate or deactivate the controller

            longitudinal (boolean): activate or deactivate the controller

        Attributes
        ----------
            lateral (boolean): activate or deactivate the controller
            
            longitudinal (boolean): activate or deactivate the controller

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,lateral, longitudinal):
        """ initalizes the ActivateControllerAction

            Parameters
            ----------
                lateral (boolean): activate or deactivate the controller
            
                longitudinal (boolean): activate or deactivate the controller

        """
        self.lateral = lateral
        self.longitudinal = longitudinal

    def get_attributes(self):
        """ returns the attributes of the ActivateControllerAction as a dict

        """
        return {'lateral':str(self.lateral),'longitudinal':str(self.longitudinal)}

    def get_element(self):
        """ returns the elementTree of the ActivateControllerAction

        """
        element = ET.Element('PrivateAction')
        routeaction = ET.SubElement(element,'ActivateControllerAction',attrib=self.get_attributes())

        return element


class AssignControllerAction():
    """ AssignControllerAction creates a ControllerAction of type AssignControllerAction
        
        Parameters
        ----------
            controller (Controller or Catalogreference): a controller to assign

        Attributes
        ----------
            controller (boolController or Catalogreferenceean): a controller to assign

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,controller):
        """ initalizes the AssignControllerAction

            Parameters
            ----------
                controller (Controller or Catalogreference): a controller to assign

        """
        self.controller = controller

    def get_element(self):
        """ returns the elementTree of the AssignControllerAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerActiton')
        controlleraction.append(self.controller.get_element())

        return element


class OverrideThrottleAction():
    """ OverrideThrottleAction creates a ControllerAction of type OverrideControllerValueAction and OverrideThrottleAction 
        
        Parameters
        ----------
            value (double): 0...1 throttle pedal

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 throttle pedal

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideThrottleAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideThrottleAction as a dict

        """
        return {'value':str(self.value),'active':str(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideThrottleAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideThrottleAction',self.get_attributes())
        return element


class OverrideBrakeAction():
    """ OverrideBrakeAction creates a ControllerAction of type OverrideControllerValueAction and OverrideBrakeAction 
        
        Parameters
        ----------
            value (double): 0...1 throttle pedal

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 brake pedal value

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideBrakeAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideBrakeAction as a dict

        """
        return {'value':str(self.value),'active':str(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideBrakeAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideBrakeAction',self.get_attributes())
        return element


class OverrideClutchAction():
    """ OverrideClutchAction creates a ControllerAction of type OverrideControllerValueAction and OverrideClutchAction
        
        Parameters
        ----------
            value (double): 0...1 clutch pedal value

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 brake pedal value

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideClutchAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideClutchAction as a dict

        """
        return {'value':str(self.value),'active':str(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideClutchAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideClutchAction',self.get_attributes())
        return element



class OverrideParkingBrakeAction():
    """ OverrideParkingBrakeAction creates a ControllerAction of type OverrideControllerValueAction and OverrideParkingBrakeAction 
        
        Parameters
        ----------
            value (double): 0...1 clutch pedal value

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 brake pedal value

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideParkingBrakeAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideParkingBrakeAction as a dict

        """
        return {'value':str(self.value),'active':str(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideParkingBrakeAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideParkingBrakeAction',self.get_attributes())
        return element




class OverrideSteeringWheelAction():
    """ OverrideSteeringWheelAction creates a ControllerAction of type OverrideControllerValueAction and OverrideSteeringWheelAction 
        
        Parameters
        ----------
            value (double): 0...1 clutch pedal value

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 brake pedal value

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideSteeringWheelAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideSteeringWheelAction as a dict

        """
        return {'value':str(self.value),'active':str(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideSteeringWheelAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideSteeringWheelAction',self.get_attributes())
        return element



class OverrideGearAction():
    """ OverrideGearAction creates a ControllerAction of type OverrideControllerValueAction and OverrideGearAction 
        
        Parameters
        ----------
            value (double): 0...1 clutch pedal value

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 brake pedal value

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideGearAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideGearAction as a dict

        """
        return {'value':str(self.value),'active':str(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideGearAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideGearAction',self.get_attributes())
        return element



class VisibilityAction():
    """ creates a VisibilityAction
        
        Parameters
        ----------
            graphics (boolean): visible for graphics or not

            traffic (boolean): visible for traffic

            sensors (boolean): visible to sensors or not

        Attributes
        ----------
            graphics (boolean): visible for graphics or not

            traffic (boolean): visible for traffic

            sensors (boolean): visible to sensors or not

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,graphics, traffic, sensors):
        """ initalizes the VisibilityAction

            Parameters
            ----------
            graphics (boolean): visible for graphics or not

            traffic (boolean): visible for traffic

            sensors (boolean): visible to sensors or not

        """
        self.graphics = graphics
        self.traffic = traffic
        self.sensors = sensors

    def get_attributes(self):
        """ returns the attributes of the VisibilityAction as a dict

        """
        return {'graphics':str(self.graphics),'active':str(self.traffic),'sensors':str(self.sensors)}

    def get_element(self):
        """ returns the elementTree of the VisibilityAction

        """
        element = ET.Element('PrivateAction')
        ET.SubElement(element,'VisibilityAction',self.get_attributes())
        return element

class AbsoluteSynchronizeAction():
    """ creates a SynchronizeAction with an absolute speed as target speed
        
        Parameters
        ----------
            entity (str): entity to syncronize with

            entity_position (*Position): the position of the entity to syncronize to

            target_position (*Position): the position of the target that should syncronize

            speed (double): the absolute speed of the target that should syncronize

        Attributes
        ----------
            entity (str): entity to syncronize with

            entity_position (*Position): the position of the entity to syncronize to

            target_position (*Position): the position of the target that should syncronize

            speed (double): the absolute speed of the target that should syncronize

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,entity,entity_position,target_position,speed):
        """ initalize the AbsoluteSynchronizeAction
    
            Parameters
            ----------
                entity (str): entity to syncronize with

                entity_position (*Position): the position of the entity to syncronize to

                target_position (*Position): the position of the target that should syncronize

                speed (double): the absolute speed of the target that should syncronize
        """

        self.entity = entity
        self.entity_position = entity_position
        self.target_position = target_position
        self.speed = speed

    def get_attributes(self):
        """ returns the attributes of the AbsoluteSynchronizeAction as a dict

        """
        return {'masterEntityRef':self.entity}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSynchronizeAction

        """
        element = ET.Element('PrivateAction')
        syncaction = ET.SubElement(element,'SyncronizeAction',self.get_attributes())
        syncaction.append(self.entity_position.get_element('TargetPositionMaster'))
        syncaction.append(self.target_position.get_element('TargetPosition'))
        finalspeed = ET.SubElement(syncaction,'FinalSpeed')
        ET.SubElement(finalspeed,'AbsoluteSpeed',attrib={'value':str(self.speed)})
        
        return element


class RelativeSynchronizeAction():
    """ creates a SynchronizeAction with a relative speed target
        
        Parameters
        ----------
            entity (str): entity to syncronize with

            entity_position (*Position): the position of the entity to syncronize to

            target_position (*Position): the position of the target that should syncronize

            speed (double): the relative speed of the target that should syncronize

            speed_target_type (str): the semantics of the value (delta, factor)

        Attributes
        ----------
            entity (str): entity to syncronize with

            entity_position (*Position): the position of the entity to syncronize to

            target_position (*Position): the position of the target that should syncronize

            speed (double): the relative speed of the target that should syncronize

            speed_target_type (str): the semantics of the value (delta, factor)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,entity,entity_position,target_position,speed,speed_target_type):
        """ initalize the RelativeSynchronizeAction
    
            Parameters
            ----------
                entity (str): entity to syncronize with

                entity_position (*Position): the position of the entity to syncronize to

                target_position (*Position): the position of the target that should syncronize

                speed (double): the absolute speed of the target that should syncronize

                speed_target_type (str): the semantics of the value (delta, factor)
        """

        self.entity = entity
        self.entity_position = entity_position
        self.target_position = target_position
        self.speed = speed
        if speed_target_type not in SpeedTargetValueType:
            ValueError(speed_target_type + ' is not a valid speed_target_type')
        self.speed_target_type = speed_target_type

    def get_attributes(self):
        """ returns the attributes of the VisibilityAction as a dict

        """
        return {'masterEntityRef':self.entity}

    def get_element(self):
        """ returns the elementTree of the VisibilityAction

        """
        element = ET.Element('PrivateAction')
        syncaction = ET.SubElement(element,'SyncronizeAction',self.get_attributes())
        syncaction.append(self.entity_position.get_element('TargetPositionMaster'))
        syncaction.append(self.target_position.get_element('TargetPosition'))
        finalspeed = ET.SubElement(syncaction,'FinalSpeed')
        ET.SubElement(finalspeed,'RelativeSpeedToMaster',attrib={'value':str(self.speed),'speedTargetValueType':self.speed_target_type})
        
        return element


#### Global Actions ####


class ParameterAddAction():
    """ The ParameterAddAction class creates a ParameterAction of tyoe ParameterModifyAction which adds a value to an existing Parameter
        
        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be added to the parameter

        Attributes
        ----------

            parameter_ref (str): name of the parameter

            value (double): the value that should be added to the parameter

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,parameter_ref,value):
        """ initalize the ParameterAddAction

        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be added to the parameter

        """
        self.parameter_ref = parameter_ref
        self.value = value
    def get_attributes(self):
        """ returns the attributes of the AbsoluteSpeedAction as a dict

        """
        return {'value':str(self.value)}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSpeedAction

        """
        element = ET.Element('GlobalAction')
        paramaction = ET.SubElement(element,'ParameterAction',{'parameterRef':self.parameter_ref})
        modifaction = ET.SubElement(paramaction,'ModifyAction')
        rule = ET.SubElement(modifaction,'Rule')
        ET.SubElement(rule,'AddValue',self.get_attributes())

        
        return element


class ParameterMultiplyAction():
    """ The ParameterMultiplyAction class creates a ParameterAction of tyoe ParameterModifyAction which adds a value to an existing Parameter
        
        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be multiplied to the parameter

        Attributes
        ----------

            parameter_ref (str): name of the parameter

            value (double): the value that should be multiplied to the parameter

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,parameter_ref,value):
        """ initalize the ParameterMultiplyAction

        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be added to the parameter

        """
        self.parameter_ref = parameter_ref
        self.value = value
    def get_attributes(self):
        """ returns the attributes of the AbsoluteSpeedAction as a dict

        """
        return {'value':str(self.value)}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSpeedAction

        """
        element = ET.Element('GlobalAction')
        paramaction = ET.SubElement(element,'ParameterAction',{'parameterRef':self.parameter_ref})
        modifaction = ET.SubElement(paramaction,'ModifyAction')
        rule = ET.SubElement(modifaction,'Rule')
        ET.SubElement(rule,'MultiplyByValue',self.get_attributes())

        return element


class ParameterSetAction():
    """ The ParameterSetAction class creates a ParameterAction which adds a value to an existing Parameter
        
        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be set to the parameter

        Attributes
        ----------

            parameter_ref (str): name of the parameter

            value (double): the value that should be set to the parameter

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,parameter_ref,value):
        """ initalize the ParameterSetAction

        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be added to the parameter

        """
        self.parameter_ref = parameter_ref
        self.value = value
    def get_attributes(self):
        """ returns the attributes of the AbsoluteSpeedAction as a dict

        """
        return {'value':str(self.value)}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSpeedAction

        """
        element = ET.Element('GlobalAction')
        paramaction = ET.SubElement(element,'ParameterAction',{'parameterRef':self.parameter_ref})
        ET.SubElement(paramaction,'SetAction',self.get_attributes())
        
        return element


class TrafficSignalStateAction():
    """ The TrafficSignalStateAction class creates a Infrastructure action which controls the state of a traffic signal
        
        Parameters
        ----------
            name (str): id of the signal in the road network

            state (str): the state to set to the traffic light

        Attributes
        ----------

            name (str): id of the signal in the road network

            state (str): the state to set to the traffic light

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,name,state):
        """ initalize the TrafficSignalStateAction

        Parameters
        ----------
            name (str): id of the signal in the road network

            state (str): the state to set to the traffic light

        """
        self.name = name
        self.state = state

    def get_attributes(self):
        """ returns the attributes of the AbsoluteSpeedAction as a dict

        """
        return {'name':self.name,'state':self.state}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSpeedAction

        """
        element = ET.Element('GlobalAction')
        infra = ET.SubElement(element,'InfrastructureAction')
        tsa = ET.SubElement(infra,'TrafficSignalAction')
        ET.SubElement(tsa,'TrafficSignalStateAction',self.get_attributes())
        
        return element
