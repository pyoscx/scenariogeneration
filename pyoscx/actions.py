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
        """ returns the atributes of the _Action as a dict

        """
        return {'name':self.name}
        
    def get_element(self):
        """ returns the elementTree of the _Action

        """
        element = ET.Element('Action',attrib=self.get_attributes())
        element.append(self.action.get_element())
        return element

#LongitudinalAction
class SpeedAction():
    """ The SpeedAction class a SpeedAction of OpenScenario
        
        Parameters
        ----------
            transition_dynamics (TransitionDynamics): how the change should be made

        Attributes
        ----------
            abs_target (bool): if the speed action is absolute (True) or relative (False)

            speed (float): the speed wanted

            target (str): the name of the relative target (used for relative speed)

            valuetype (str): the type of relative speed wanted (used for relative speed)

            continious (bool): if the controller tries to keep the relative speed 

            transition_dynamics (TransitionDynamics): how the change should be made

        Methods
        -------
            set_absolute_target_speed(speed)
                sets the absolute speed target 
            
            set_relative_target_speed(speed,entity,valuetype,continious)
                sets the relative speed target

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,transition_dynamics):
        """ initalizes SpeedAction

        Parameters
        ----------
            transition_dynamics (TransitionDynamics): how the change should be made

        """
        self.abs_target = None
        self.speed = None
        self.target = None
        self.valuetype = None
        self.continious = None
        self.transition_dynamics = transition_dynamics
        self._actionname = ''
    def set_absolute_target_speed(self,speed):
        """ sets the absolute speed target 
            
        Parameters
        ----------
            speed (float): the wanted speed

        """

        if self.abs_target == False:
            raise(ValueError('Relative target already set'))
        self.abs_target = True
        self.speed = speed
        self._actionname = 'AbsoluteTargetSpeed'

    def set_relative_target_speed(self,speed,entity,valuetype='delta',continious=True):
        """ sets the relative speed target

        Parameters
        ----------
            speed (float): the wanted relative speed

            target (str): the name of the relative target (used for relative speed)

            valuetype (str): the type of relative speed wanted (used for relative speed)
                Default: 'delta'

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

        """
        if self.abs_target == True:
            raise(ValueError('Absolute target already set'))
        self.abs_target = False
        self.speed = speed
        self.target = entity
        self.valuetype = valuetype
        self.continious = continious
        self._actionname = 'RelativeTargetSpeed'
    
    def get_attributes(self):
        """ returns the atributes of the SpeedAction as a dict

        """
        if self.abs_target:
            return {'value':str(self.speed)}
        else:
            return {'entityRef':self.target,'value':str(self.speed),'speedTargetValueType':self.valuetype,'continious':str(self.continious)}

    def get_element(self):
        """ returns the elementTree of the SpeedAction

        """
        element = ET.Element('PrivateAction')
        longaction = ET.SubElement(element,'LongitudinalAction')
        speedaction = ET.SubElement(longaction,'SpeedAction')

        speedaction.append(self.transition_dynamics.get_element('SpeedActionDynamics'))
        speedactiontarget = ET.SubElement(speedaction,'SpeedActionTarget')
        
        ET.SubElement(speedactiontarget,self._actionname,self.get_attributes())
        
        return element
            


class LongitudinalDistanceAction():
    """ The LongitudinalDistanceAction creates the LongitudinalDistanceAction of openScenario
        
        Parameters
        ----------
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

            distance (float): if the distance metric is used

            timegap (float): if timegap metric is used

            dynamic_constraint (DynamicsConstrains): Dynamics constraints of the action

        Methods
        -------
            set_distance(distance)
                sets the distance metric

            set_timegap(timegap)
                sets the timecap metric

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,entity,freespace=True,continious=True,max_acceleration = None,max_deceleration = None,max_speed = None):
        """ initalize the LongitudinalDistanceAction
        
        Parameters
        ----------
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
        self.distance = None
        self.timegap = None
        self.dynamic_constraint = DynamicsConstrains(max_acceleration,max_deceleration,max_speed)
        
    def set_distance(self,distance):
        """ sets the distance metric

        Parameters
        ----------
            distance (float): distance to the entity

        """
        if self.timegap:
            raise ValueError('Already have timegap setting')
        self.distance = distance

    def set_timegap(self,timegap):
        """ sets the timegap metric

        Parameters
        ----------
            timegap (float): time to the target

        """
        if self.distance:
            raise ValueError('Already have distance setting')
        self.timegap = timegap
    
        

    def get_attributes(self):
        """ returns the atributes of the LongitudinalDistanceAction as a dict

        """
        retdict = {}
        retdict['entryRef'] = self.target
        retdict['freespace'] = str(self.freespace)
        retdict['continious'] = str(self.continious)
        if self.timegap:
            retdict['timeGap'] = str(self.timegap)
        elif self.distance:
            retdict['distance'] = str(self.distance)
        else:
            ValueError('No value added for either timegap or distance')
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

# lateral actions

class LaneChangeAction():
    """ 
        
        Parameters
        ----------
            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        Attributes
        ----------
            abs_target (bool): if the action should be absolute (True), or relative (False)

            value (int): lane to change to

            target (str): target for relative lane change

            target_lane_offset (float): offset in the target lane is wanted
                
            transition_dynamics (TransitionDynamics): how the change should be made

        Methods
        -------
            set_absolute_target_lane(value)
                sets an absolut lane target

            set_relative_target_lane(value,entity)
                sets a relative lane target

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,transition_dynamics,target_lane_offset=None):
        """ initalize LaneChangeAction

        Parameters
        ----------
            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        """

        self.abs_target = None
        self.value = None
        self.target = None
        self.target_lane_offset = target_lane_offset
        self._lanechangename = None
        self.transition_dynamics = transition_dynamics

    def set_absolute_target_lane(self,value):
        """ sets an absolut lane target

        Parameters
        ----------
            value (int): number of the lane that should be changed to

        """
        if self.abs_target == False:
            raise ValueError('already a relative target')
        self.abs_target = True
        self.value = value
        self._lanechangename = 'RelativeTargetLane'

    def set_relative_target_lane(self,value,entity):
        """ sets a relative lane target

        Parameters
        ----------
            value (int): number of relative lane that should be changed to

            entity (str): the entity to run relative to

        """
        if self.abs_target == True:
            raise ValueError('already an abosulte target')
        self.abs_target = False
        self.value = value
        self.target = entity
        self._lanechangename = 'AbsoluteTargetLane'

    def get_attributes(self):
        """ returns the atributes of the LaneChangeAction as a dict

        """
        retdict = {}
        if self.abs_target == None:
            raise ValueError('no target type set')
        retdict['value'] = str(self.value)
        if not self.abs_target:
            retdict['entityRef'] = self.target
        return retdict
    
    def get_element(self):
        """ returns the elementTree of the LaneChangeAction

        """
        element = ET.Element('PrivateAction')
        laneoffset = {}
        lataction = ET.SubElement(element,'LateralAction')
        if self.target_lane_offset:
            laneoffset = {'targetLaneOffset':str(self.target_lane_offset)}
        lanechangeaction = ET.SubElement(lataction,'LaneChangeAction',attrib=laneoffset)
        
        lanechangeaction.append(self.transition_dynamics.get_element('LaneChangeActionDynamics'))
        lanchangetarget = ET.SubElement(lanechangeaction,'LaneChangeTarget')
        
        ET.SubElement(lanchangetarget,self._lanechangename,self.get_attributes())
        return element


class LaneOffsetAction():
    """ the LaneOffsetAction class creates a LaneOffsetAction of openScenario
        
        Parameters
        ----------
            shape (str): shape of the offset action

            constants (list of floats): the constants of the shape

            maxlatacc (float): maximum allowed lateral acceleration

            continious (bool): if the controller tries to keep the relative speed 
                Default: True

        Attributes
        ----------
            continious (bool): if the controller tries to keep the relative speed 

            abs_target (bool): if an absolute (True), or relative (False) target is used.

            value (float): lateral offset of the lane or target

            target (str): the name of the entity (relative only)

            dynshape (DynamicsShape): the shape of the action

            maxlatacc (float): maximum allowed lateral acceleration

        Methods
        -------
            set_absolute_target_lane(value)
                sets a absolute lane offset target

            set_relative_target_lane(value,entity)
                sets a relative lane offset target

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,shape,constants,maxlatacc,continious = True):
        """ initalizes the LaneOffsetAction
            Parameters
            ----------
            shape (str): shape of the offset action

            constants (list of floats): the constants of the shape

            maxlatacc (float): maximum allowed lateral acceleration

            continious (bool): if the controller tries to keep the relative speed 
                Default: True
        """
        self.continious = continious
        self.abs_target = None
        self.value = None
        self.target = None
        self._laneoffsettarget = None
        self.dynshape = DynamicsShape(shape,constants)
        self.maxlatacc = maxlatacc

    def set_absolute_target_lane(self,value):
        """ sets a absolute lane offset target

        Parameters
        ----------
            value (float): lateral offset of the lane

        """
        if self.abs_target == False:
            raise ValueError('already a relative target')
        self.abs_target = True
        self.value = value
        
        self._laneoffsettarget = 'AbsoluteTargetLaneOffset'

    def set_relative_target_lane(self,value,entity):
        """ sets a relative lane offset target

        Parameters
        ----------
            value (float): lateral offset of the entity

            entity (str): name of the entity

        """
        if self.abs_target == True:
            raise ValueError('already an abosulte target')
        self.abs_target = False
        self.value = value
        self.target = entity
        self._laneoffsettarget ='RelativeTargetLaneOffset'       
        
    def get_attributes(self):
        """ returns the atributes of the LaneOffsetAction as a dict

        """
        retdict = {}
        retdict['value'] = str(self.value)
        if not self.abs_target:
            retdict['entryRef'] = self.target
        return retdict
        
    def get_element(self):
        """ returns the elementTree of the LaneOffsetAction

        """
        element = ET.Element('PrivateAction')
        lataction = ET.SubElement(element,'LateralAction')
        laneoffsetaction = ET.SubElement(lataction,'LaneChangeAction',attrib={'continious':str(self.continious)})
        ET.SubElement(laneoffsetaction,'LaneOffsetActionDynamics',{'maxLateralAcc':str(self.maxlatacc),'dynamicsShape':self.dynshape.shape})
        ET.SubElement(laneoffsetaction,self._laneoffsettarget,self.get_attributes())

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
        """ returns the atributes of the LateralDistanceAction as a dict

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

