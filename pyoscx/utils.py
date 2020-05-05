
import xml.etree.ElementTree as ET

def merge_dicts(*dict_args):
    """ Funciton to merge dicts 
    
    """
    retdict = {}
    for d in dict_args:
        retdict.update(d)

    return retdict

    
class ConditionEdge():
    """ ConditionEdge is used to determine how to trigger on a valuechange
        
        Parameters
        ----------
            condition (str): what valuechange to use rising, falling, risingorFalling or none

        Attributes
        ----------
            condition (str): what valuechange to use rising, falling, risingorFalling or none

        Methods
        -------

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,condition):
        """ initalize the ConditionEdge

            Parameters
            ----------
                condition (str): what valuechange to use rising, falling, risingorFalling or none

        """
        if condition not in ['rising','falling','risingorFalling','none']:
            raise ValueError('not a valid condition edge')
        self.condition = condition

    def get_attributes(self):
        """ returns the atributes of the ConditionEdge as a dict

        """
        return {'conditionEdge':self.condition}


class EntityRef():
    """ EntityRef creates an EntityRef element of openscenario
        
        Parameters
        ----------
            entity (str): name of the entity

        Attributes
        ----------
            entity (str): name of the entity

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,entity):
        """ initalize the EntityRef

            Parameters
            ----------
                entity (str): name of the entity
                
        """
        self.entity = entity

    def get_attributes(self):
        """ returns the atributes of the EntityRef as a dict

        """
        return {'entryRef':self.entity}

    def get_element(self):
        """ returns the elementTree of the EntityRef

        """
        return ET.Element('EntityRef',attrib=self.get_attributes())

class ObjectType():
    """ creates an objecttype of openscenario
        
        Parameters
        ----------
            obj_type (str): the typ of object, vehicle, pedestrian or miscellaneous
            
        Attributes
        ----------
            type (str): the typ of object

        Methods
        -------

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,obj_type):
        """ initalize the ObjectType

            Parameters
            ----------
                obj_type (str): the typ of object, vehicle, pedestrian or miscellaneous

        """
        if obj_type not in ['pedestrian','vehicle','miscellaneous']:
            raise ValueError('not a valid object type')

        self.type = obj_type

    def get_attributes(self):
        """ returns the atributes of the Parameter as a dict

        """
        return {'value':self.type}


class Parameter():
    """ Parameter is a declaration of a ParameterDeclaration for declarations
        
        Parameters
        ----------
            name (str): name of parameter

            parameter_type (str): type of the parameter

            value (str): value of the parameter

        Attributes
        ----------
            name (str): name of parameter

            parameter_type (str): type of the parameter

            value (str): value of the parameter

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    _PARAMETERS = [\
        'integer',
        'double',
        'string',
        'unsighedInt',
        'unsighedShort',
        'boolean',
        'dateTime']
    def __init__(self,name,parameter_type,value):
        """ initalize the Parameter 

            Parameters
            ----------
                name (str): name of parameter

                parameter_type (str): type of the parameter

                value (str): value of the parameter

        """
        self.name = name
        if parameter_type not in self._PARAMETERS:
            raise ValueError('parameter_type not a valid type.')
        self.parameter_type = parameter_type
        self.value = value

    def get_attributes(self):
        """ returns the atributes of the Parameter as a dict

        """
        return {'name':self.name,'parameterType':self.parameter_type,'value':str(self.value)}

    def get_element(self):
        """ returns the elementTree of the Parameter

        """
        element = ET.Element('ParameterDeclaration',attrib=self.get_attributes())
        return element

class Rule():
    """ Creates a Rule of a comparison
        
        Parameters
        ----------
            rule: what to apply (greaterThan, lessThan, or equalTo)

            parameter: ???

        Attributes
        ----------
            rule: what to apply (greaterThan, lessThan, or equalTo)

            parameter: ???

        Methods
        -------

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,rule,parameter = None):
        """ initalize the Rule
            Parameters
            ----------
                rule: what to apply (greaterThan, lessThan, or equalTo)

                parameter: ???

        """
        if rule not in ['greaterThan','lessThan','equalTo']:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
        self.parameter = parameter

    def get_attributes(self):
        """ returns the atributes of the Rule as a dict

        """
        return {'rule':self.rule}


class Orientation():
    """ Orientation describes the angular orientation of an entity
        
        Parameters
        ----------
            h (float): header 

            p (float): pitch

            r (float): roll

            reference (str): absolute or relative

        Attributes
        ----------
            h (float): header 

            p (float): pitch

            r (float): roll

            reference (str): absolute or relative

        Methods
        -------
            is_filled()
                check is any orientations are set

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,h=None,p=None,r=None,reference = None):
        
        self.h = h
        self.p = p
        self.r = r
        if reference not in ['absolute','relative',None]:
            raise ValueError(reference + '; is not a valid reference type.')
        self.ref = reference

    def is_filled(self):
        """ is_filled check is any orientations are  set

            Returns: boolean

        """
        if self.h or self.p or self.r or self.ref:
            return True
        else:
            return False
    
    def get_attributes(self):
        """ returns the atributes of the DynamicsConstrains as a dict

        """
        retdict = {}
        if self.h:
            retdict['h'] = str(self.h)

        if self.p:
            retdict['p'] = str(self.p)

        if self.r:
            retdict['r'] = str(self.r)

        if self.ref:
            retdict['type'] = str(self.ref)
        
        return retdict
    
    def get_element(self):
        """ returns the elementTree of the DynamicsConstrains

        """
        return ET.Element('Orientation',attrib=self.get_attributes())

class DynamicsShape():
    """ DynamicsShape is used to create a shape
        
        Parameters
        ----------
            shape (str): what dynamics to have, linear, cubic, sinusoidal, or step

            constants (list of floats): coefficients of the shape ## TODO: check this

        Attributes
        ----------
            shape (str): what dynamics to have, linear, cubic, sinusoidal, or step

            constants (list of floats): coefficients of the shape ## TODO: check this

        Methods
        -------
            ## TODO: Fix this one
            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,shape,constants):
        """ initalize the DynamicsShape

            Parameters
            ----------
                shape (str): what dynamics to have, linear, cubic, sinusoidal, or step

                constants (list of floats): coefficients of the shape ## TODO: check this
        
        """
        if shape not in ['linear','cubic','sinusoidal','step']:
            raise ValueError(shape + '; is not a valid shape.')
        self.shape = shape
        self.constants = constants
        #TODO: check how values are supposed to be passed with multiple constants!!

class TransitionDynamics():
    """ TransitionDynamics is used to define how the dynamics of a change
        
        Parameters
        ----------
            shape (str): shape of the transition

            constants (list of float): values of the shape ??? TODO: check how this works

            dimension (str): the dimension of the transition (rate, time or distance)

            value (float): ???

        Attributes
        ----------
            shape (str): shape of the transition

            constants (list of float): values of the shape ??? TODO: check how this works

            dimension (str): the dimension of the transition (rate, time or distance)

            value (float): ???

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,shape,constants,dimension,value):
        """
            Parameters
            ----------
                shape (str): shape of the transition

                constants (list of float): values of the shape ??? TODO: check how this works

                dimension (str): the dimension of the transition (rate, time or distance)

                value (float): ???
        """
        self.dynamics_shape = DynamicsShape(shape,constants)
        if dimension not in ['rate','time','distance']:
            raise ValueError(dimension + ' is not a valid dynamics dimension')
        self.dimension = dimension
        self.value = value

    def get_attributes(self):
        """ returns the atributes of the DynamicsConstrains as a dict

        """
        return {'dynamicsShape':self.dynamics_shape.shape,'value':str(self.value),'dynamicsDimension':str(self.dimension)}

    def get_element(self,name='TransitionDynamics'):
        """ returns the elementTree of the DynamicsConstrains

        """
        return ET.Element(name,self.get_attributes())

class DynamicsConstrains():
    """ DynamicsConstrains is used by triggers
        
        Parameters
        ----------
            max_acceleration (float): maximum acceleration allowed

            max_deceleration (float): maximum deceleration allowed

            max_speed (float): maximum speed allowed

        Attributes
        ----------
            max_acceleration (float): maximum acceleration allowed

            max_deceleration (float): maximum deceleration allowed

            max_speed (float): maximum speed allowed

        Methods
        -------
            is_filled()
                check is any constraints are set

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """

    def __init__(self, max_acceleration=None, max_deceleration=None, max_speed=None):
        """ initalize DynamicsConstrains

        """

        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.max_speed = max_speed

    def is_filled(self):
        """ is_filled check is any constraints are set

            Returns: boolean

        """

        if self.max_acceleration or self.max_deceleration or self.max_speed:
            return True
        else:
            return False

    def get_attributes(self):
        """ returns the atributes of the DynamicsConstrains as a dict

        """
        retdict = {}
        if self.max_speed:
            retdict['maxSpeed'] = str(self.max_speed)
        if self.max_deceleration:
            retdict['maxDeceleration'] = str(self.max_deceleration)
        if self.max_acceleration:
            retdict['maxAcceleration'] = str(self.max_acceleration)
        return retdict

    def get_element(self,name = 'DynamicConstraitns'):
        """ returns the elementTree of the DynamicsConstrains

        """
        return ET.Element(name,attrib=self.get_attributes())
