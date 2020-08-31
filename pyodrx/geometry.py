import xml.etree.ElementTree as ET




class Sprial():
    """ the Spiral (Clothoid) creates a spiral type of geometry
        
        Parameters
        ----------
            curvstart (float): starting curvature of the Spiral

            curvend (float): final curvature of the Spiral

            
        Attributes
        ----------
            curvstart (float): starting curvature of the Spiral

            curvend (float): final curvature of the Spiral

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,curvstart,curvend):
        """ initalizes the Spiral

        Parameters
        ----------
            curvstart (float): starting curvature of the Spiral

            curvend (float): final curvature of the Spiral
        """ 
        self.curvstart = curvstart
        self.curvend = curvend


    def get_attributes(self):
        """ returns the attributes of the WorldPostion as a dict

        """
        return {'curvStart': str(self.curvstart), 'curvEnd': str(self.curvend)}

    def get_element(self):
        """ returns the elementTree of the WorldPostion

            Parameters
            ----------
                elementname (str): used if another name is needed for the position
                    Default: Position
        """
        element = ET.Element('spiral',attrib=self.get_attributes())
        
        return element