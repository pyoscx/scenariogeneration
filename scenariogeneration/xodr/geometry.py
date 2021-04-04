""" The geometry module contains the basic geometries of OpenDRIVE

"""

import xml.etree.ElementTree as ET

import numpy as np
from .exceptions import NotEnoughInputArguments, ToManyOptionalArguments, MixOfGeometryAddition
from scipy.integrate import quad
from scipy.special import fresnel

class _Geometry():
    """ the _Geometry describes the geometry entry of open drive
        
        Parameters
        ----------
            s (float): the start s value (along road) of the geometry
               
            x (float): start x coordinate of the geometry
                
            y (float):  start y coordinate of the geometry
                
            heading (float): heading of the geometry

            geom_type (Line, Spiral,ParamPoly3, or Arc): the type of geometry

        Attributes
        ----------
            s (float): the start s value (along road) of the geometry
               
            x (float): start x coordinate of the geometry
                
            y (float):  start y coordinate of the geometry
                
            heading (float): heading of the geometry

            geom_type (Line, Spiral,ParamPoly3, or Arc): the type of geometry

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,s,x,y,heading,geom_type):
        """ initalizes the PlanView

        Parameters
        ----------
            s (float): the start s value (along road) of the geometry
               
            x (float): start x coordinate of the geometry
                
            y (float):  start y coordinate of the geometry
                
            heading (float): heading of the geometry

            geom_type (Line, Spiral,ParamPoly3, or Arc): the type of geometry

        """ 
        self.s = s
        self.x = x
        self.y = y
  
        
        self.heading = heading
        self.geom_type = geom_type
        _,_,_,self.length = self.geom_type.get_end_data(self.x,self.y,self.heading)

    def get_end_data(self):
        return self.geom_type.get_end_data(self.x,self.y,self.heading)
        
    def get_start_data(self):
        x,y,heading,self.length = self.geom_type.get_start_data(self.x,self.y,self.heading)
        self.x = x
        self.y = y
        self.heading = heading + np.pi
        self.s = None
        return x,y,heading,self.length

    def set_s(self,s):
        self.s = s

    def get_attributes(self):
        """ returns the attributes of the _Geometry as a dict

        """
        retdict = {}
        retdict['s'] = str(self.s)
        retdict['x'] = str(self.x)
        retdict['y'] = str(self.y)
        retdict['hdg'] = str(self.heading)
        retdict['length'] = str(self.length)
        return retdict


    def get_element(self):
        """ returns the elementTree of the _Geometry

        """
        element = ET.Element('geometry',attrib=self.get_attributes())
        element.append(self.geom_type.get_element())
        return element



class PlanView():
    """ the PlanView is the geometrical description of a road, 
        
        Parameters
        ----------
            x_start (float): start x coordinate of the first geometry
                Default: None

            y_start (float): start y coordinate of the first geometry
                Default: None

            h_start (float): starting heading of the first geometry
                Default: None

        Attributes
        ----------
            present_x (float): the start x coordinate of the next geometry added

            present_y (float): the y coordinate of the next geometry added

            present_h (float): the heading coordinate of the next geometry added

            present_s (float): the along road measure of the next geometry added

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_total_length()
                Returns the full length of the PlanView

            add_geometry(geom,lenght)
                adds a new geometry entry to the planeview

            set_start_point(x_start,y_start,h_start)
                sets the start point and heading of the planview

            adjust_geometries()
                based on the start point, it will adjust all geometries in the planview

    """
    def __init__(self,x_start=None,y_start=None,h_start=None):
        """ initalizes the PlanView
            Note: if multiple roads are used, the start values can be recalculated.


        """ 
        self.present_x = 0
        self.present_y = 0
        self.present_h = 0
        self.present_s = 0
        self.fixed = False
        if all([x_start != None, y_start!=None,h_start!=None]):
            self.set_start_point(x_start, y_start, h_start)
        elif any([x_start != None, y_start!=None,h_start!=None]):
            raise NotEnoughInputArguments('If a start position is wanted for the PlanView, all inputs must be used.')

        self.x_start = None
        self.y_start = None
        self.h_start = None

        self.x_end = None
        self.y_end = None
        self.h_end = None

        self._raw_geometries = []
        self._adjusted_geometries = []
        self._overridden_headings = []

        self.adjusted = False
        # variable to track what mode of adding geometries are used

        self._addition_mode = None

    def add_geometry(self,geom,heading = None):
        """ add_geometry adds a geometry to the planview and will stich together all geometries (in order the order added)
            
            Should be used together with "adjust_roads_and_lanes" in the OpenDrive class. 

            NOTE: DO NOT MIX WITH with add_fixed_geometry
        
        Parameters
        ----------
            geom (Line, Spiral, ParamPoly3, or Arc): the type of geometry

            heading (float): override the previous heading (optional), not recommended
                if used, use for ALL geometries

        """
        if self._addition_mode == 'add_fixed_geometry':
            raise MixOfGeometryAddition("A fixed geometry has already been added, please use either add_geometry or add_fixed_geometry")

        if heading is not None:
            self._overridden_headings.append(heading)
        self._raw_geometries.append(geom)
        self._addition_mode = 'add_geometry'
    
    def add_fixed_geometry(self, geom, x_start, y_start, h_start,s=None):
        """ add_fixed_geometry adds a geometry to a certain point to the planview 

            if s is used, the values will be coded and is up to the user to make correct, not for a correct opendrive file please add the geometires in order
            if s is not used, the geometries are supposed to be added in order (and s will be calculated)
        
            NOTE: DO NOT MIX WITH the method add_geometry

        Parameters
        ----------
            geom (Line, Spiral, ParamPoly3, or Arc): the geometry to add

            x_start (float): start x position of the geometry

            y_start (float): start y position of the geometry

            h_start (float): start heading of the geometry

            s (float): start s value of the geometry (optional)
                Default: None

        """
        if self._addition_mode == 'add_geometry':
            raise MixOfGeometryAddition("A geometry has already been added with add_geometry, please use either add_geometry, or add_fixed_geometry not both")
        
        if s != None:
            pres_s = s
        else:
            pres_s = self.present_s
        
        if not self.fixed:
            self.x_start = x_start
            self.y_start = y_start
            self.h_start = h_start
            self.fixed = True
        
        newgeom = _Geometry(pres_s,x_start,y_start,h_start,geom)
        self._adjusted_geometries.append(newgeom)
        self.x_end, self.y_end, self.h_end, length = newgeom.get_end_data()
        self.present_s += length
        self.adjusted = True
        self._addition_mode == 'add_fixed_geometry'


    def set_start_point(self,x_start=0,y_start=0,h_start=0):
        """ sets the start point of the planview

            Parameters
            ----------
            x_start (float): start x coordinate of the first geometry
                Default: 0

            y_start (float): start y coordinate of the first geometry
                Default: 0

            h_start (float): starting heading of the first geometry
                Default: 0
        """
    
        self.present_x = x_start
        self.present_y = y_start
        self.present_h = h_start
        self.fixed = True

    def get_start_point(self):
        """ returns the start point of the planview

            Parameters
            ----------
        """

        return self.x_start, self.y_start, self.h_start 
        #return self._adjusted_geometries[-1].get_end_point

    def get_end_point(self):
        """ sets the start point of the planview

            Parameters
            ----------
            x_start (float): start x coordinate of the first geometry
                Default: 0

            y_start (float): start y coordinate of the first geometry
                Default: 0

            h_start (float): starting heading of the first geometry
                Default: 0
        """

        return self.x_end, self.y_end, self.h_end 

    def adjust_geometries(self, from_end=False):
        """ Adjusts all geometries to have the correct start point and heading

            Parameters
            ----------
            from_end ([optional]bool): states if (self.present_x, self.present_y, self.present_h) are being interpreted as starting point or ending point of the geometry

        """
        
        if from_end== False:
            self.x_start = self.present_x
            self.y_start = self.present_y
            self.h_start = self.present_h

            for i in range(len(self._raw_geometries)):
                if len(self._overridden_headings) > 0:
                    self.present_h = self._overridden_headings[i]

                newgeom = _Geometry(self.present_s,self.present_x,self.present_y,self.present_h,self._raw_geometries[i])

                self.present_x, self.present_y, self.present_h, length = newgeom.get_end_data()
                self.present_s += length

                self._adjusted_geometries.append(newgeom)
            self.x_end = self.present_x
            self.y_end = self.present_y
            self.h_end = self.present_h

        else: 

            self.x_end = self.present_x
            self.y_end = self.present_y
            self.h_end = self.present_h + np.pi

            lengths = []
            for i in range(len(self._raw_geometries)-1, -1, -1):

                newgeom = _Geometry(self.present_s,self.present_x,self.present_y,self.present_h,self._raw_geometries[i])
                self.present_x,self.present_y,self.present_h, partial_length = newgeom.get_start_data()
                lengths.append(partial_length)
                self._adjusted_geometries.append(newgeom)                  

            self.x_start = self.present_x
            self.y_start = self.present_y
            self.h_start = self.present_h + np.pi

            length = sum(lengths)           
            self.present_s = 0
             
            for i in range(len(self._raw_geometries)):

                newgeom.set_s(self.present_s)
                self.present_s += lengths[i]  

        self.adjusted = True

    def get_total_length(self):
        """ returns the total length of the planView

        """

        return self.present_s

    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """

        element = ET.Element('planView')
        for geom in self._adjusted_geometries:
            element.append(geom.get_element())
        return element



class Line():
    """ the line class creates a line type of geometry

        Parameters
        ----------
            length (float): length of the line

        Attributes
        ----------
            length (float): length of the line

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_end_data(x,y,h)
                Returns the end point of the geometry

    """
    def __init__(self,length):
        self.length = length

    def get_end_data(self,x,y,h):
        """ Returns the end point of the geometry
        
        Parameters
        ----------
            x (float): x start point of the geometry

            y (float): y start point of the geometry

            h (float): start heading of the geometry

        Returns
        ----------
            x (float): the final x point

            y (float): the final y point

            h (float): the final heading

            length (float): length of the road

        """

        new_x = self.length*np.cos(h) + x
        new_y = self.length*np.sin(h) + y
        new_h = h

        return new_x, new_y, new_h, self.length

    def get_start_data(self, end_x, end_y, end_h):
        """ Returns the end point of the geometry
        
        Parameters
        ----------
            end_x (float): x end point of the geometry

            end_y (float): y end point of the geometry

            end_h (float): end heading of the geometry

        Returns
        ----------
            x (float): the start x point

            y (float): the start y point

            h (float): the start heading

            length (float): length of the road

        """
        start_x = self.length*np.cos(end_h) + end_x
        start_y = self.length*np.sin(end_h) + end_y
        start_h = end_h

        return start_x, start_y, start_h, self.length
    
    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """
        element = ET.Element('line')
        
        return element



class Spiral():
    """ the Spiral (Clothoid) creates a spiral type of geometry
        
        Parameters
        ----------
            curvstart (float): starting curvature of the Spiral
 
            curvend (float): final curvature of the Spiral
 
            length (float): length of the spiral (optional, or use, angle, or cdot)

            angle (float): the angle of the spiral (optional, or use length, or cdot)

            cdot (float): the curvature change of the spiral (optional, or use length, or angle)

        Attributes
        ----------
            curvstart (float): starting curvature of the Spiral
 
            curvend (float): final curvature of the Spiral
 
        Methods
        -------
            get_element()
                Returns the full ElementTree of the class
 
            get_attributes()
                Returns a dictionary of all attributes of the class
 
            get_end_data(x,y,h)
                Returns the end point of the geometry        
    """
    def __init__(self,curvstart,curvend,length=None,angle=None,cdot=None):
        """ initalizes the Spline
 
        Parameters
        ----------
            curvstart (float): starting curvature of the Spiral
 
            curvend (float): final curvature of the Spiral
        """ 
        self.curvstart = curvstart
        self.curvend = curvend
        if length == None and angle == None and cdot == None:
            raise NotEnoughInputArguments('Spiral is underdefined')
        if sum([x!=None for x in [length,angle,cdot]]) > 1:
            raise ToManyOptionalArguments('Spiral is overdefined, please use only one of the optional inputs')
        if angle:
            self.length = 2*abs(angle)/np.maximum(abs(curvend),abs(curvstart))

        elif cdot:
            self.length =  (self.curvend - self.curvstart) / cdot
        else:
            self.length = length
 
    def get_end_data(self,x,y,h):
        """ Returns the end point of the geometry
        
        Parameters
        ----------
            x (float): x start point of the geometry
 
            y (float): y start point of the geometry
 
            h (float): start heading of the geometry
 
        Returns
        ---------
 
            x (float): the final x point
            y (float): the final y point
            h (float): the final heading
            l (float): length of the spiral
        """
        spiral = EulerSpiral.createFromLengthAndCurvature(self.length, self.curvstart, self.curvend)
        (deltax, deltay, t) = spiral.calc(self.length, x, y, self.curvstart, h)

 
        return deltax, deltay, t, self.length

    def get_start_data(self, end_x, end_y, end_h):
        """ Returns the end point of the geometry
        
        Parameters
        ----------
            end_x (float): x end point of the geometry
 
            end_y (float): y end point of the geometry
 
            end_h (float): end heading of the geometry

        Returns
        ---------
 
            x (float): the start x point
            y (float): the start y point
            h (float): the start heading of the inverse geometry 
            l (float): length of the spiral

        """

        spiral = EulerSpiral.createFromLengthAndCurvature(self.length, -self.curvend, -self.curvstart)
        (deltax, deltay, t) = spiral.calc(self.length, end_x, end_y, -self.curvend, end_h)

 
        return deltax, deltay, t, self.length

 
    def get_attributes(self):
        """ returns the attributes of the Line as a dict
 
        """
        return {'curvStart': str(self.curvstart), 'curvEnd': str(self.curvend)}
 
    def get_element(self):
        """ returns the elementTree of the Line
 
        """
        element = ET.Element('spiral',attrib=self.get_attributes())
        
        return element
        

class Arc():
    """ the Arc creates a arc type of geometry
        
        Parameters
        ----------
            curvature (float): curvature of the arc

            length (float): length of the arc (optional or use angle)

            angle (float): angle of the arc (optional or use length)

        Attributes
        ----------
            curvature (float): curvature of the arc

            length (float): length of the arc 

            angle (float): angle of the arc

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

            get_end_data(x,y,h)
                Returns the end point of the geometry
    """
    def __init__(self,curvature,length = None, angle=None):
        """ initalizes the Arc

        Parameters
        ----------
            curvature (float): curvature of the arc

            length (float): length of the arc (optional or use angle)

            angle (float): angle of the arc (optional or use length)

        """

        if length == None and angle == None:
            raise NotEnoughInputArguments('neither length nor angle defined, for arc')
        
        if length != None and angle != None:
            raise ToManyOptionalArguments('both length and angle set, only one is requiered')

        self.length = length
        self.angle = angle
        if curvature == 0:
            raise ValueError('You are creating a straight line, please use Line instead')
        self.curvature = curvature

    def get_end_data(self,x,y,h):
        """ Returns information about the end point of the geometry
        
        Parameters
        ----------
            x (float): x start point of the geometry

            y (float): y start point of the geometry

            h (float): start heading of the geometry

        Returns
        ---------
            
            x (float): the final x point

            y (float): the final y point

            h (float): the final heading

            length (float): length of the element

        """
        radius = 1/np.abs(self.curvature)
        if self.curvature < 0:
            phi_0 = h + np.pi/2
            x_0 = x - np.cos(phi_0)*radius
            y_0 = y - np.sin(phi_0)*radius

        else:
            phi_0 = h - np.pi/2
            x_0 = x - np.cos(phi_0)*radius
            y_0 = y - np.sin(phi_0)*radius

        if self.length:
            self.angle = self.length * self.curvature

        new_ang = self.angle + phi_0
        if self.angle:         
            self.length = np.abs(radius*self.angle)

            

        new_h = h + self.angle
        new_x = np.cos(new_ang)*radius + x_0
        new_y = np.sin(new_ang)*radius + y_0

        return new_x, new_y, new_h, self.length

    def get_start_data(self,end_x,end_y,end_h):
        """ Returns information about the end point of the geometry
        
        Parameters
        ----------
            end_x (float): x final point of the geometry

            end_y (float): y final point of the geometry

            end_h (float): final heading of the geometry

        Returns
        ---------
            
            x (float): the start x point

            y (float): the start y point

            h (float): the start heading of the inverse geometry 

            length (float): length of the element

        """
        x = end_x
        y = end_y 
        h = end_h
        inv_curv = - self.curvature 
        radius = 1/np.abs(inv_curv)
        if inv_curv < 0:
            phi_0 = h + np.pi/2
            x_0 = x - np.cos(phi_0)*radius
            y_0 = y - np.sin(phi_0)*radius

        else:
            phi_0 = h - np.pi/2
            x_0 = x - np.cos(phi_0)*radius
            y_0 = y - np.sin(phi_0)*radius

        if self.length:
            self.angle = self.length * inv_curv

        new_ang = self.angle + phi_0
        if self.angle:         
            self.length = np.abs(radius*self.angle)
        

        new_h = h + self.angle
        new_x = np.cos(new_ang)*radius + x_0
        new_y = np.sin(new_ang)*radius + y_0
        return new_x, new_y, new_h, self.length

    def get_attributes(self):
        """ returns the attributes of the Arc as a dict

        """
        return {'curvature': str(self.curvature)}

    def get_element(self):
        """ returns the elementTree of the Arc

        """
        element = ET.Element('arc',attrib=self.get_attributes())
        
        return element



class ParamPoly3():
    """ the ParamPoly3 class creates a parampoly3 type of geometry, in the coordinate systeme U (along road), V (normal to the road)
        
        the polynomials are on the form
        uv(p) = a + b*p + c*p^2 + d*p^3

        Parameters
        ----------
            au (float): coefficient a of the u polynomial
            
            bu (float): coefficient b of the u polynomial

            cu (float): coefficient c of the u polynomial

            du (float): coefficient d of the u polynomial

            av (float): coefficient a of the v polynomial

            bv (float): coefficient b of the v polynomial

            cv (float): coefficient c of the v polynomial

            dv (float): coefficient d of the v polynomial

            prange (str): "normalized" or "arcLength"
                Default: "normalized"

            length (float): total length of arc, used if prange == arcLength

        Attributes
        ----------
            au (float): coefficient a of the u polynomial
            
            bu (float): coefficient b of the u polynomial

            cu (float): coefficient c of the u polynomial

            du (float): coefficient d of the u polynomial

            av (float): coefficient a of the v polynomial

            bv (float): coefficient b of the v polynomial

            cv (float): coefficient c of the v polynomial

            dv (float): coefficient d of the v polynomial
           
            prange (str): "normalized" or "arcLength"
                Default: "normalized"

            length (float): total length of arc, used if prange == arcLength

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

            get_end_coordinate(length,x,y,h)
                Returns the end point of the geometry
    """
    def __init__(self,au,bu,cu,du,av,bv,cv,dv,prange='normalized',length=None):
        """ initalizes the ParamPoly3

        Parameters
        ----------
            au (float): coefficient a of the u polynomial
            
            bu (float): coefficient b of the u polynomial

            cu (float): coefficient c of the u polynomial

            du (float): coefficient d of the u polynomial

            av (float): coefficient a of the v polynomial

            bv (float): coefficient b of the v polynomial

            cv (float): coefficient c of the v polynomial

            dv (float): coefficient d of the v polynomial
           
            prange (str): "normalized" or "arcLength"
                Default: "normalized"
                
            length (float): total length of arc, used if prange == arcLength
        """ 
        
        self.au = au
        self.bu = bu
        self.cu = cu
        self.du = du
        self.av = av
        self.bv = bv
        self.cv = cv
        self.dv = dv
        self.prange = prange
        if prange == 'arcLength' and length == None:
            raise ValueError('No length was provided for Arc with arcLength option')
        self.length = length

    def _integrand(self,p):
        """ integral function to calulate length of polynomial,
            #TODO: This is not tested or verified...
        """
        return np.sqrt(
            (abs(3*self.du*p**2 + 2*self.cu*p + self.bu))**2 + 
            (abs(3*self.dv*p**2 + 2*self.cv*p + self.bv))**2)

    def get_start_data(self,x,y,h):
        """ Returns the start point of the geometry
        
        Parameters
        ----------
            x (float): x end point of the geometry

            y (float): y end point of the geometry

            h (float): end heading of the geometry

        Returns
        ---------
            x (float): the start x point
            y (float): the start y point
            h (float): the start heading
            length (float): the length of the geometry

        """
        if self.prange == 'normalized':
            p = 1
            I = quad(self._integrand,0,1)
            self.length = I[0]
        else:
            p = self.length
        newu = self.au + self.bu*p + self.cu*p**2 + self.du*p**3
        newv = self.av + self.bv*p + self.cv*p**2 + self.dv*p**3

        new_x = x - (newu*np.cos(h)-np.sin(h)*newv)
        new_y = y - (newu*np.sin(h)+np.cos(h)*newv)
        new_h = h - np.arctan2(self.bv + 2*self.cv*p + 3*self.dv*p**2,self.bu + 2*self.cu*p + 3*self.du*p**2)

        return new_x, new_y, new_h, self.length
    def get_end_data(self,x,y,h):
        """ Returns the end point of the geometry
        
        Parameters
        ----------
            x (float): x final point of the geometry

            y (float): y final point of the geometry

            h (float): final heading of the geometry

        Returns
        ---------
            x (float): the start x point
            y (float): the start y point
            h (float): the start heading of the inverse geometry 
            length (float): length of the polynomial

        """
        if self.prange == 'normalized':
            p = 1
            I = quad(self._integrand,0,1)
            self.length = I[0]
        else:
            p = self.length
        newu = self.au + self.bu*p + self.cu*p**2 + self.du*p**3
        newv = self.av + self.bv*p + self.cv*p**2 + self.dv*p**3

        new_x = x + newu*np.cos(h)-np.sin(h)*newv
        new_y = y + newu*np.sin(h)+np.cos(h)*newv
        new_h = h + np.arctan2(self.bv + 2*self.cv*p + 3*self.dv*p**2,self.bu + 2*self.cu*p + 3*self.du*p**2)

        return new_x, new_y, new_h, self.length


    def get_attributes(self):
        """ returns the attributes of the ParamPoly3 as a dict

        """
        retdict = {}
        retdict['aU'] = str(self.au)
        retdict['bU'] = str(self.bu)
        retdict['cU'] = str(self.cu)
        retdict['dU'] = str(self.du)
        retdict['aV'] = str(self.av)
        retdict['bV'] = str(self.bv)
        retdict['cV'] = str(self.cv)
        retdict['dV'] = str(self.dv)
        retdict['pRange'] = self.prange
        return retdict
        

    def get_element(self):
        """ returns the elementTree of the ParamPoly3

        """
        element = ET.Element('paramPoly3',attrib=self.get_attributes())
        
        return element


class EulerSpiral(object):

    def __init__(self, gamma):
        self._gamma = gamma

    @staticmethod
    def createFromLengthAndCurvature(length, curvStart, curvEnd):
        return EulerSpiral(1 * (curvEnd - curvStart) / length)

    def calc(self, s, x0=0, y0=0, kappa0=0, theta0=0):

        # Start
        C0 = x0 + 1j * y0

        if self._gamma == 0 and kappa0 == 0:
            # Straight line
            Cs = C0 + s * np.exp(1j * theta0 )

        elif self._gamma == 0 and kappa0 != 0:
            # Arc
            Cs = C0 + np.exp(1j * theta0) / kappa0 * (np.sin(kappa0 * s) + 1j * (1 - np.cos(kappa0 * s)))

        else:
            # Fresnel integrals
            Sa, Ca = fresnel((kappa0 + self._gamma * s) / np.sqrt(np.pi * np.abs(self._gamma)))
            Sb, Cb = fresnel(kappa0 / np.sqrt(np.pi * np.abs(self._gamma)))

            # Euler Spiral
            Cs1 = np.sqrt(np.pi / np.abs(self._gamma)) * np.exp(1j * (theta0 - kappa0**2 / 2 / self._gamma))
            Cs2 = np.sign(self._gamma) * (Ca - Cb) + 1j * Sa - 1j * Sb

            Cs = C0 + Cs1 * Cs2

        # Tangent at each point
        theta = self._gamma * s**2 / 2 + kappa0 * s + theta0

        return (Cs.real, Cs.imag, theta)
