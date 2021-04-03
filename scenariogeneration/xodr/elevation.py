import xml.etree.ElementTree as ET




class _Poly3Profile():
    """ the _Poly3Profile class describes a poly3  along s of a road, the elevation is described as a third degree polynomial
        elev(ds) = a + b*ds + c*ds^2 * d*ds^3
        or (if t is used)
        shape (ds) = a + b*dt + c*dt^2 * d*dt^3

        This class is used for both elevation, superElevation and shape

        Parameters
        ----------
            s (float): s start coordinate of the elevation

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial

            t (float): t variable (used only for shape)
                Default: None

        Attributes
        ----------
            s (float): s start coordinate of the elevation

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial

            t (float): t variable (used only for shape)

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns the attributes of the class

    """
    def __init__(self, s, a, b, c, d, t = None):
        """ initalize the Elevation class

        Parameters
        ----------
            s (float): s start coordinate of the elevation

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial

            t (float): t variable (used only for shape)
                Default: None


        """
        self.s = s
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.t = t

    def get_attributes(self):
        """ returns the attributes of the Elevetion

        """
    
        retdict = {}
        retdict['s'] = str(self.s)
        if self.t != None:
            retdict['t'] = str(self.t)
        retdict['a'] = str(self.a)
        retdict['b'] = str(self.b)
        retdict['c'] = str(self.c)
        retdict['d'] = str(self.d)
        return retdict

    def get_element(self,elementname):
        """ returns the elementTree of the Elevation

            Parameters
            ----------
                elementname (str): name of the element, can be elevation, superelevation or shape
        """
        if elementname == 'shape' and self.t == None:
            raise ValueError('When shape is used, the t value has to be set.')
        elif elementname != 'shape' and self.t != None:
            raise ValueError('When shape is not used, the t value should not be set.')

        element = ET.Element(elementname,attrib=self.get_attributes())
        
        return element

class ElevationProfile():
    """ the ElevationProfile creates the elevationProfile element of the road in opendrive,


        Attributes
        ----------
            elevations (list of _Poly3Profile):

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            add_elevation(elevation)
                adds an elevation profile to the road
    """
    def __init__(self):
        """ initalize the ElevationProfile class

        """
        self.elevations = []

    def add_elevation(self,elevation):
        """ adds an elevation to the ElevationProfile

            Parameters
            ----------
                elevation (_Poly3Profile): the elevation profile to add to the ElevationProfile

        """
        if not isinstance(elevation,_Poly3Profile):
            raise TypeError('add_elevation requires an _Poly3Profile as input, not ' + str(type(elevation)))
        self.elevations.append(elevation)

    def get_element(self):
        """ returns the elementTree of the ElevationProfile

        """
        
        element = ET.Element('elevationProfile')
        for i in self.elevations:
            element.append(i.get_element('elevation'))
        
        return element



class LateralProfile():
    """ the LateralProfile creates the elevationProfile element of the road in opendrive,


        Attributes
        ----------
            superelevation (list of _Poly3Profile): list of superelevations of the road

            shape (list of _Poly3Profile): list of shapes for the road 

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            add_superelevation(superelevation)
                adds an superelevation profile to the road

            add_shape(shape)
                adds a shape to the lateral profile
    """
    def __init__(self):
        """ initalize the LateralProfile class

        """
        self.superelevations = []
        self.shapes = []

    def add_superelevation(self,superelevation):
        """ adds an elevation to the LateralProfile

            Parameters
            ----------
                superelevation (_Poly3Profile): the elevation profile to add to the LateralProfile

        """
        if not isinstance(superelevation,_Poly3Profile):
            raise TypeError('add_elevation requires an _Elevation as input, not ' + str(type(superelevation)))
        self.superelevations.append(superelevation)

    def add_shape(self,shape):
        """ adds an elevation to the LateralProfile

            Parameters
            ----------
                shape (_Poly3Profile): the elevation profile to add to the LateralProfile

        """
        if not isinstance(shape,_Poly3Profile):
            raise TypeError('add_elevation requires an _Elevation as input, not ' + str(type(shape)))
        self.shapes.append(shape)

    def get_element(self):
        """ returns the elementTree of the LateralProfile

        """
        
        element = ET.Element('lateralProfile')
        for i in self.superelevations:
            element.append(i.get_element('superelevation'))
        for i in self.shapes:
            element.append(i.get_element('shape'))
        return element


