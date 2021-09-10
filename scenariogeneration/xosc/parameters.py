""" the parameters module contains the classes related to the ParameterValueDistributionDefinition that was introduced in OpenScenario V1.1

"""
import xml.etree.ElementTree as ET

from .enumerations import VersionBase, XMLNS, XSI
from .utils import _StochasticDistributionType,  FileHeader, VersionBase, printToFile, ParameterAssignment
from .exceptions import NotEnoughInputArguments, OpenSCENARIOVersionError


class _HistogramBin():
    """ the _HistogramBin is used by Histogram to define the bins
        
        Parameters
        ----------  
            weight (float): the weight of the bin

            range (Range): the range of the bin

        Attributes
        ----------
            weight (float): the weight of the bin

            range (Range): the range of the bin

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self, weight, range = None):
        """ initalizes the Histogram

        Parameters
        ----------
            weight (float): the weight of the bin

            range (Range): the range of the bin

        """ 
        if range and not isinstance(range,Range):
            raise TypeError('range input is not of type Histogram')
        self.weight = weight
        self.range = range

    def __eq__(self,other):
        if isinstance(other,_HistogramBin):
            if self.get_attributes() == other.get_attributes() and \
                self.range == other.range:
               return True
        return False

    def get_attributes(self):
        """ returns the attributes of the HistogramBin as a dict

        """
        retdict = {'weight':str(self.weight)}
        return retdict

    def get_element(self):
        """ returns the elementTree of the HistogramBin

        """
        element = ET.Element('HistogramBin',self.get_attributes())
        element.append(self.range.get_element())
        return element

class _ProbabilityDistributionSetElement():
    """ the _ProbabilityDistributionSetElement is used by ProbabilityDistributionSet to define the elements
        
        Parameters
        ----------  
            value (string): possible value

            weight (float): weight of the value

        Attributes
        ----------
            value (string): possible value

            weight (float): weight of the value

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self, value, weight):
        """ initalizes the Histogram

        Parameters
        ----------
            value (string): possible value

            weight (float): weight of the value

        """ 
        self.value = value
        self.weight = weight

    def __eq__(self,other):
        if isinstance(other,_ProbabilityDistributionSetElement):
            if self.get_attributes() == other.get_attributes():
               return True
        return False

    def get_attributes(self):
        """ returns the attributes of the _ProbabilityDistributionSetElement as a dict

        """
        retdict = {'value':self.value,'weight':str(self.weight)}
        return retdict

    def get_element(self):
        """ returns the elementTree of the _ProbabilityDistributionSetElement

        """
        element = ET.Element('Element',self.get_attributes())
        return element

class Range():
    """ the Range creates a Range used by parameter distributions
        
        Parameters
        ----------
            lower (float): lower limit of the range

            upper (float): upper limit of the range

        Attributes
        ----------
            lower (float): lower limit of the range

            upper (float): upper limit of the range

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,lower,upper):
        """ initalizes the Range

        Parameters
        ----------
            lower (float): lower limit of the range

            upper (float): upper limit of the range

        """ 
        self.lower = lower
        self.upper = upper

    def __eq__(self,other):
        if isinstance(other,Range):
            if self.get_attributes() == other.get_attributes():
               return True
        return False

    def get_attributes(self):
        """ returns the attributes of the Range as a dict

        """
        retdict = {'lowerLimit':str(self.lower),'upperLimit':str(self.upper)}
        return retdict

    def get_element(self):
        """ returns the elementTree of the Range

        """
        element = ET.Element('Range',self.get_attributes())
        return element


## Stocastic distributions
class Stocastic():
    """ Creates the Stocastic type of parameter distributions
        
        Parameters
        ----------
            number_of_tests (int): number of tests to run 

            random_seed (float): the seed for the run
                Default: None

        Attributes
        ----------
            number_of_tests (int): number of tests to run 

            random_seed (float): the seed for the run

            distributions (dict of *StochasticDistribution): the distributions for the parameters

        Methods
        -------
            add_distribution(parametername, distribution)
                Adds a parameter/distribution pair

            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,number_of_tests,random_seed=None):
        """ initalizes the Stocastic 

        Parameters
        ----------
            number_of_tests (int): number of tests to run

            random_seed (float): the seed for the run
                Default: None

        """ 
        self.number_of_tests = number_of_tests
        self.random_seed = random_seed
        self.distributions = {}

    def __eq__(self,other):
        if isinstance(other,Stocastic):
            if self.get_attributes() == other.get_attributes() and \
                self.distributions == other.distributions:
               return True
        return False
    def add_distribution(self,parametername,distribution):
        """ adds a parameter and a related distribution to it

        Parameters
        ----------
            parametername (str): name of the parameter

            distribution (StochasticDistribution): the distribution of that parameter

        """ 
        if not isinstance(distribution,_StochasticDistributionType):
            raise TypeError('distribution input is not a valid StochasticDistribution')
        self.distributions[parametername] = distribution

    def get_attributes(self):
        """ returns the attributes of the Stochastic as a dict

        """
        retdict = {'numberOfTestRuns':str(self.number_of_tests),'randomSeed':str(self.random_seed)}
        return retdict

    def get_element(self):
        """ returns the elementTree of the Stochastic

        """
        element = ET.Element('Stochastic',self.get_attributes())
        if not self.distributions:
            raise NotEnoughInputArguments('No distribution has been added')
        for d in self.distributions:
            # dist = ET.SubElement(element,'stochasticDistribution',)
            dist = ET.SubElement(element, 'StochasticDistribution', attrib={'parameterName':d})
            dist.append(self.distributions[d].get_element())
            
        return element

class NormalDistribution(_StochasticDistributionType):
    """ the NormalDistribution is a stocastic distribution
        
        Parameters
        ----------
            expected_value (float): the expected value (mean) of the distribution

            variance (float): variance of the distribution

            range (Range): limit of the values (optional)
                Default: None

        Attributes
        ----------
            expected_value (float): the expected value (mean) of the distribution

            variance (float): variance of the distribution

            range (Range): limit of the values (optional)

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self, expected_value, variance, range = None):
        """ initalizes the NormalDistribution

        Parameters
        ----------
            expected_value (float): the expected value (mean) of the distribution

            variance (float): variance of the distribution

            range (Range): limit of the values (optional)
                Default: None

        """ 
        if range and not isinstance(range,Range):
            raise TypeError('range input is not of type Range')
        self.expected_value = expected_value
        self.variance = variance
        self.range = range

    def __eq__(self,other):
        if isinstance(other,NormalDistribution):
            if self.get_attributes() == other.get_attributes() and \
                self.range == other.range:
               return True
        return False

    def get_attributes(self):
        """ returns the attributes of the NormalDistribution as a dict

        """
        retdict = {'expectedValue':str(self.expected_value),'variance':str(self.variance)}
        return retdict

    def get_element(self):
        """ returns the elementTree of the NormalDistribution

        """
        element = ET.Element('NormalDistribution',self.get_attributes())
        if self.range:
            element.append(self.range.get_element())
        return element

class UniformDistribution(_StochasticDistributionType):
    """ the UniformDistribution is a stocastic distribution
        
        Parameters
        ----------
            range (Range): limit of the values

        Attributes
        ----------
            range (Range): limit of the values

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

    """
    def __init__(self, expected_value, variance, range = None):
        """ initalizes the UniformDistribution

        Parameters
        ----------
            range (Range): limit of the values (optional)


        """ 
        if range and not isinstance(range,Range):
            raise TypeError('range input is not of type Range')
        self.range = range

    def __eq__(self,other):
        if isinstance(other,UniformDistribution):
            if self.range == other.range:
               return True
        return False

    def get_element(self):
        """ returns the elementTree of the UniformDistribution

        """
        element = ET.Element('UniformDistribution',self.get_attributes())
        element.append(self.range.get_element())
        return element

class PoissonDistribution(_StochasticDistributionType):
    """ the PoissonDistribution is a stocastic distribution
        
        Parameters
        ----------
            expected_value (float): the expected value of the distribution

            range (Range): limit of the values (optional)
                Default: None

        Attributes
        ----------
            expected_value (float): the expected value of the distribution

            range (Range): limit of the values (optional)

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self, expected_value, range = None):
        """ initalizes the PoissonDistribution

        Parameters
        ----------
            expected_value (float): the expected value of the distribution

            range (Range): limit of the values (optional)
                Default: None

        """ 
        if range and not isinstance(range,Range):
            raise TypeError('range input is not of type Range')
        self.expected_value = expected_value
        self.range = range

    def __eq__(self,other):
        if isinstance(other,PoissonDistribution):
            if self.get_attributes() == other.get_attributes() and \
                self.range == other.range:
               return True
        return False

    def get_attributes(self):
        """ returns the attributes of the PoissonDistribution as a dict

        """
        retdict = {'expectedValue':str(self.expected_value)}
        return retdict

    def get_element(self):
        """ returns the elementTree of the PoissonDistribution

        """
        element = ET.Element('PoissonDistribution',self.get_attributes())
        if self.range:
            element.append(self.range.get_element())
        return element

class Histogram(_StochasticDistributionType):
    """ the Histogram is a stocastic distribution
        
        Parameters
        ----------

        Attributes
        ----------
            bins (list of _HistogramBin): the bins defining the histogram

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            add_bin(weight,range)
                adds a weight and a range to a bin

    """
    def __init__(self):
        """ initalizes the Histogram

        """ 
        self.bins = []

    def __eq__(self,other):
        if isinstance(other,Histogram):
            if self.bins == other.bins:
               return True
        return False

    def add_bin(self,weight,range):
        """ returns the attributes of the Histogram as a dict

            Parameters
            ----------
                weight (float): the weight of the bin

                range (Range): the range of the bin

        """
        self.bins.append(_HistogramBin(weight,range))
        

    def get_element(self):
        """ returns the elementTree of the Histogram

        """
        element = ET.Element('Histogram')
        if not self.bins:
            raise NotEnoughInputArguments('The Histogram has no bins, please use add_bin to add atleast one.')
        for bin in self.bins:
            element.append(bin.get_element())
        return element

class ProbabilityDistributionSet(_StochasticDistributionType):
    """ the ProbabilityDistributionSet is a stocastic distribution
        
        Parameters
        ----------

        Attributes
        ----------
            sets (list of _ProbabilityDistributionSetElement): the sets defining the ProbabilityDistributionSet

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            add_set(value, weight)
                adds a weight and a range to a bin

    """
    def __init__(self):
        """ initalizes the ProbabilityDistributionSet

        """ 
        self.sets = []

    def __eq__(self,other):
        if isinstance(other,ProbabilityDistributionSet):
            if self.sets == other.sets:
               return True
        return False

    def add_set(self, value, weight):
        """ adds a set element to the ProbabilityDistributionSet

            Parameters
            ----------
                value (string): possible value

                weight (float): weight of the value

        """
        self.sets.append(_ProbabilityDistributionSetElement(value,weight))
        

    def get_element(self):
        """ returns the elementTree of the ProbabilityDistributionSet

        """
        element = ET.Element('ProbabilityDistributionSet')
        if not self.sets:
            raise NotEnoughInputArguments('No sets were added to the ProbabilityDistributionSet, please use add_set')
        for bin in self.sets:
            element.append(bin.get_element())
        return element

### Deterministic 



class ParameterValueSet():
    """ Creates the ParameterValueSet used by the DeterministicMultiParameterDistribution
        
        Parameters
        ----------


        Attributes
        ----------

            assignments (list of ParameterAssignment): the the assignments for the ValueSet

        Methods
        -------
            add_parameter(parameterref, value)
                Adds a parameter value pair

            get_element(elementname)
                Returns the full ElementTree of the class

    """
    def __init__(self):
        """ initalizes the ParameterValueSet 

        """ 

        self.sets = []

    def __eq__(self,other):
        if isinstance(other,ParameterValueSet):
            if self.sets == other.sets:
               return True
        return False

    def add_parameter(self,parameterref,value):
        """ adds a parameter and a value

        Parameters
        ----------
            parameterref (str): name of the parameters

            value (str): value of the parameters

        """ 

        self.sets.append(ParameterAssignment(parameterref,value))


    def get_element(self):
        """ returns the elementTree of the ParameterValueSet

        """
        element = ET.Element('ParameterValueSet')
        
        if not self.sets:
            raise NotEnoughInputArguments('No sets has been added')
        for s in self.sets:            
            element.append(s.get_element())
            
        return element

class DeterministicMultiParameterDistribution():
    """ Creates the DeterministicMultiParameterDistribution type of parameter distributions
        
        Parameters
        ----------


        Attributes
        ----------

            distributions (list of ParameterValueSet): the distributions for the parameters

        Methods
        -------
            add_value_set(parameter_value_set)
                Adds a parameter value set

            get_element(elementname)
                Returns the full ElementTree of the class

    """
    def __init__(self):
        """ initalizes the DeterministicMultiParameterDistribution 

        """ 

        self.sets = []

    def __eq__(self,other):
        if isinstance(other,DeterministicMultiParameterDistribution):
            if self.sets == other.sets:
               return True
        return False

    def add_value_set(self,parameter_value_set):
        """ adds a parameter and a related distribution to it

        Parameters
        ----------
            parameter_value_set (ParameterValueSet): a set of parameters

        """ 
        if not isinstance(parameter_value_set,ParameterValueSet):
            raise TypeError('distribution input is not of type ParameterValueSet')
        self.sets.append(parameter_value_set)


    def get_element(self):
        """ returns the elementTree of the DeterministicMultiParameterDistribution

        """
        element = ET.Element('DeterministicMultiParameterDistribution')
        value_set_element = ET.SubElement(element,'ValueSetDistribution')
        if not self.sets:
            raise NotEnoughInputArguments('No sets has been added')
        for d in self.sets:            
            value_set_element.append(d.get_element())
            
        return element

class DistributionRange():
    """ Creates the DistributionRange used to define a Single parameter distribution
        
        Parameters
        ----------
            step_width (double): step size of the distribution

            range (Range): the range of the parameter

        Attributes
        ----------

            step_width (double): step size of the distribution

            range (Range): the range of the parameter


        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,step_width,range):
        """ initalizes the DistributionRange 

            Parameters
            ----------
                step_width (double): step size of the distribution

                range (Range): the range of the parameter

        """ 

        self.step_width = step_width
        if not isinstance(range,Range):
            raise TypeError("range is not of type Range.")
        self.range = range

    def __eq__(self,other):
        if isinstance(other,DistributionRange):
            if self.get_attributes() == other.get_attributes() and \
                self.range == other.range:
               return True
        return False

    def get_attributes(self):
        """ returns the attributes of the DistributionRange as a dict

        """
        retdict = {'stepWidth':str(self.step_width)}
        return retdict


    def get_element(self):
        """ returns the elementTree of the DistributionRange

        """
        element = ET.Element('DistributionRange',attrib=self.get_attributes())
        element.append(self.range.get_element())
            
        return element


class DistributionSet():
    """ Creates the DistributionSet used to define a Single parameter distribution
        
        Parameters
        ----------

        Attributes
        ----------

            value_elements (list of str double): a list of all values

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

    """
    def __init__(self):
        """ initalizes the DistributionSet 

        """ 
        self.value_elements = []
        
    def __eq__(self,other):
        if isinstance(other,DistributionSet):
            if  self.value_elements == other.value_elements:
               return True
        return False

    def add_value(self,value):
        """ adds a value to the DistirbutionSet

            Parameters
            ----------
                value (str): the value to be added to the distribution
        """
        self.value_elements.append(value)

    def get_element(self):
        """ returns the elementTree of the DistributionSet

        """
        element = ET.Element('DistributionSet')
        if not self.value_elements:
            raise NotEnoughInputArguments('No values has been added to the DistributionSet')
        for value in self.value_elements:
            ET.SubElement(element,'Element',attrib={'value':value})
            
        return element

class Deterministic():
    """ Creates the Deterministic type of parameter distributions
        
        Parameters
        ----------


        Attributes
        ----------

            multi_distributions (list of DeterministicMultiParameterDistribution): multi parameter distributions

            single_distributions (dict of DistributionSet/DistributionRange): single parameter distribution

        Methods
        -------
            add_multi_distribution(distribution)
                Adds a DeterministicMultiParameterDistribution

            add_single_distribution(parametername,distribution)
                adds a DeterministicSingleParameterDistribution

            get_element(elementname)
                Returns the full ElementTree of the class

    """
    def __init__(self):
        """ initalizes the Deterministic 

        """ 

        self.multi_distributions = []
        self.single_distributions = {}
    def __eq__(self,other):
        if isinstance(other,Deterministic):
            if self.multi_distributions == other.multi_distributions and \
               self.single_distributions == other.single_distributions:
               return True
        return False

    def add_multi_distribution(self,distribution):
        """ adds a DeterministicMultiParameterDistribution

            Parameters
            ----------
                distribution (DeterministicMultiParameterDistribution): the distribution of that parameter

        """ 
        if not isinstance(distribution,DeterministicMultiParameterDistribution):
            raise TypeError('distribution input is not of type DeterministicMultiParameterDistribution')
        self.multi_distributions.append(distribution)
    
    def add_single_distribution(self,parametername,distribution):
        """ adds a parameter and a related distribution to it

            Parameters
            ----------
                parametername (str): reference to the parameter

                distribution (DistributionSet or DistributionRange): the distribution of that parameter

        """ 
        if not (isinstance(distribution,DistributionSet) or isinstance(distribution,DistributionRange)):
            raise TypeError('distribution input is not of type DeterministicMultiParameterDistribution')
        self.single_distributions[parametername] = distribution

    def get_element(self):
        """ returns the elementTree of the Deterministic

        """

        element = ET.Element('Deterministic')
        for md in self.multi_distributions:
            element.append(md.get_element())
        for d in self.single_distributions:
            dist = ET.SubElement(element,'DeterministicSingleParameterDistribution',attrib={'parameterName':d})
            dist.append(self.single_distributions[d].get_element())
            
            
        return element


## wrapper 

class ParameterValueDistribution(VersionBase):
    """ Creates the the ParameterValueDistribution file for open scenario
        
        Parameters
        ----------
            number_of_tests (int): number of tests to run 

            random_seed (float): the seed for the run
                Default: None

        Attributes
        ----------
            number_of_tests (int): number of tests to run 

            random_seed (float): the seed for the run

            distributions (dict of *StochasticDistribution): the distributions for the parameters

        Methods
        -------
            write_xml(filename)
                write a open scenario xml

            get_element(elementname)
                Returns the full ElementTree of the class

    """
    _XMLNS = XMLNS
    _XSI = XSI
    def __init__(self, description, author, scenario_file, parameter_distribution, osc_minor_version=1):
        """ initalizes the Stocastic 

        Parameters
        ----------
            description (str): a description of the parameter set

            author (str): the author of the file

            scenario_file (str): path to the scenario that the parameter distribution should set

            parameter_distribution (Stocastic or Deterministic): the parameter distribution

            osc_minor_version (int): the osi version wanted (Note: only available from OpenSCENARIO V1.1.0)

        """ 
        self.header = FileHeader(description,author,revMinor=osc_minor_version)
        if not isinstance(parameter_distribution,Stocastic):
            raise TypeError(type(parameter_distribution) + "is not of type Stocastic or Deterministic")
        self.scenario_file = scenario_file
        self.parameter_distribution = parameter_distribution

    def __eq__(self,other):
        if isinstance(other,ParameterValueDistribution):
            if self.header == other.header and \
                self.scenario_file == other.scenario_file and \
                self.parameter_distribution == other.parameter_distribution:
               return True
        return False
 
    def get_element(self):
        """ returns the elementTree of the Stochastic

        """
        if self.isVersion(minor=0):
            raise OpenSCENARIOVersionError('Everything related to ParameterValueDistribution was introduced in OpenSCENARIO V1.1')
        element = ET.Element('OpenSCENARIO',attrib={'xmlns:xsi':self._XMLNS,'xsi:noNamespaceSchemaLocation':self._XSI})
        element.append(self.header.get_element())
        parameterdist = ET.SubElement(element,'ParameterValueDistribution')
        ET.SubElement(parameterdist,'ScenarioFile',attrib={'filepath':self.scenario_file})
        parameterdist.append(self.parameter_distribution.get_element())
            
        return element


    def write_xml(self,filename,prettyprint = True):
        """ write_xml writes the parametervaluedistribution xml file

        Parameters
        ----------
            filename (str): path and filename of the wanted xml file

            prettyprint (bool): pretty print or ugly print?
                Default: True

        """
        printToFile(self.get_element(),filename,prettyprint)