"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
import numpy as np

from .enumerations import ContactPoint
from ..helpers import enum2str


def get_lane_sec_and_s_for_lane_calc(road, contact_point):
    """Helping function to get a lane_section and s coordinate for calculations, at either the end or start of a road

    Parameters
    ----------
        road (Road): the road to be used

        contact_point (ContactPoint): start or end of the road

    Returns
    -------
        lanesection (int): 0 or -1

        s (float): the s coordinate at start or end of the road
    """

    relevant_s = 0
    if contact_point == ContactPoint.start:
        relevant_lanesection = 0  # since we are at the start the first lane section is relevant for determining widths for lane offset
    elif contact_point == ContactPoint.end:
        relevant_lanesection = (
            -1
        )  # since we are at the end the last lane section is relevant for determining widths for lane offset

        for geom in road.planview._raw_geometries:
            relevant_s += geom.length

    return relevant_lanesection, relevant_s


def get_coeffs_for_poly3(length, lane_offset, zero_start, lane_width_end=None):
    """get_coeffs_for_poly3 creates the coefficients for a third degree polynomial, can be used for all kinds of descriptions in xodr.

    Assuming that the derivative is 0 at the start and end of the segment.

    Parameters
    ----------
        length (float): length of the segment in the s direction

        lane_offset (float): the lane offset (width) of the lane

        zero_start (bool): True; start with zero and ends with lane_offset width,
                           False; start with lane_offset and ends with zero width

        lane_width_end (float): specify the ending lane width for lanes that may start
                                and end with different widths

    Return
    ------
        coefficients (float,float,float,float): polynomial coefficients corresponding to "a, b, c, d" in the OpenDrive polynomials
    """
    # might be expanded for other cases, not now if needed yet though
    start_heading = 0
    end_heading = 0
    s0 = 0
    s1 = length

    # create the linear system
    A = np.array(
        [
            [0, 1, 2 * s0, 3 * s0**2],
            [0, 1, 2 * s1, 3 * s1**2],
            [1, s0, s0**2, s0**3],
            [1, s1, s1**2, s1**3],
        ]
    )
    if zero_start:
        B = [start_heading, end_heading, 0, lane_offset]
    else:
        B = [start_heading, end_heading, lane_offset, 0]

    if lane_width_end is not None:
        B = [start_heading, end_heading, lane_offset, lane_width_end]

    # calculate and return the coefficients
    return np.linalg.solve(A, B)


class XodrBase:
    """Sets up common functionality for xodr generating classes by enabling userdata inputs

    Parameters
    ----------

    Attributes
    ----------
        user_data (list of UserData): all userdata added

        includes (list of str): all includes (filenames)

        data_quality (DataQuality): All

    Methods
    -------

        add_userdata(userdata)
            adds a userdata to the xodr entry

        add_dataquality(dataquality)
            adds dataquality to the xodr entry

    """

    def __init__(self):
        """initalize the UserData"""
        self.user_data = []
        self.data_quality = None

    def __eq__(self, other):
        if (
            self.user_data == other.user_data
            and self.data_quality == other.data_quality
        ):
            return True

        return False

    def add_userdata(self, userdata):
        """Adds a userdata entry to the xodr entry

        Parameters
        ----------
            userdata (Userdata): the data to be added
        """
        if not isinstance(userdata, UserData):
            raise TypeError("userdata is not of type UserData.")
        self.user_data.append(userdata)

    def add_dataquality(self, dataquality):
        """Adds a dataquality entry to the xodr entry

        Parameters
        ----------
            dataquality (DataQuality): the data to be added
        """
        if not isinstance(dataquality, DataQuality):
            raise TypeError("dataquality is not of type DataQuality.")
        self.data_quality = dataquality

    def _add_additional_data_to_element(self, element):
        """returns the elementTree of the Junction"""
        for ud in self.user_data:
            element.append(ud.get_element())
        if self.data_quality:
            element.append(self.data_quality.get_element())
        return element


class UserData:
    """Sets up addtional data for any entry of OpenDRIVE

    Parameters
    ----------
        code (str): code of the userdata

        value (str): value of the userdata
            Default: None

    Attributes
    ----------
        code (str): code of the userdata

        value (str): value of the userdata

        user_data_content (list of ET.element): list of all extra elements added

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        add_userdata_content(ET.element)
            adds extra elements to the userdata

    """

    def __init__(self, code, value=None):
        """initalize the UserData"""
        self.code = code
        self.value = value
        self.userdata_content = []

    def add_userdata_content(self, content):
        """add_userdata_content adds extra elements to userdata

        Parameters
        ----------
            content (ET.element): the element to be added
        """
        self.userdata_content.append(content)

    def _element_equals(self, e1, e2):
        if e1.tag != e2.tag:
            return False
        if e1.text != e2.text:
            return False
        if e1.tail != e2.tail:
            return False
        if e1.attrib != e2.attrib:
            return False
        if len(e1) != len(e2):
            return False
        return all(self._elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

    def __eq__(self, other):
        if isinstance(other, UserData):
            if self.get_attributes() == other.get_attributes() and len(
                self.userdata_content
            ) == len(other.userdata_content):
                for i in range(len(self.userdata_content)):
                    if not self._element_equals(
                        self.userdata_content[i], other.userdata_content[i]
                    ):
                        return False
                return True
        return False

    def get_attributes(self):
        """returns the attributes as a dict of the JunctionGroup"""
        retdict = {}
        retdict["code"] = str(self.code)
        if self.value is not None:
            retdict["value"] = str(self.value)
        return retdict

    def get_element(self):
        """returns the elementTree of the Junction"""
        element = ET.Element("userData", attrib=self.get_attributes())
        for i in self.userdata_content:
            element.append(i)
        return element


class DataQuality:
    """Sets up DataQuality for any entry of OpenDRIVE


    Attributes
    ----------
        date (str): code of the userdata

        post_processing (RawDataPostProcessing): postprocessing definition

        source (RawDataSource): source of the data

        post_processing_comment (str): comment of the postprocessing

        source_comment (str): comment of the soure

        xy_abs (float): absolute xy error

        xy_rel (float): relative xy error

        z_abs (float): absolute z error

        z_rel (float): relative z error

    Methods
    -------
        get_element()
            Returns the full ElementTree of the class

        get_attributes()
            Returns a dictionary of all attributes of the class

        add_raw_data_info(date, post_processing, source, post_processing_comment, source_comment)
            adds raw data info

        add_error(xy_abs, xy_rel, z_abs,z_rel)
            adds error info
    """

    def __init__(self):
        """initalize the UserData"""
        self.date = None
        self.post_processing = None
        self.source = None
        self.post_processing_comment = None
        self.source_comment = None
        self.xy_abs = None
        self.xy_rel = None
        self.z_abs = None
        self.z_rel = None
        self._error_added = False
        self._raw_data_added = False

    def add_raw_data_info(
        self,
        date,
        post_processing,
        source,
        post_processing_comment=None,
        source_comment=None,
    ):
        """add_raw_data_info adds data for the RawData entry

        Parameters
        ----------
            date (str): code of the userdata

            post_processing (RawDataPostProcessing): postprocessing definition

            source (RawDataSource): source of the data

            post_processing_comment (str): comment of the postprocessing
                Default: None

            source_comment (str): comment of the soure
                Default: None
        """

        self.date = date
        self.post_processing = post_processing
        self.source = source
        self.post_processing_comment = post_processing_comment
        self.source_comment = source_comment
        self._raw_data_added = True

    def add_error(self, xy_abs, xy_rel, z_abs, z_rel):
        """add_error adds data to the error element

        Parameters
        ----------
            xy_abs (float): absolute xy error

            xy_rel (float): relative xy error

            z_abs (float): absolute z error

            z_rel (float): relative z error
        """
        self.xy_abs = xy_abs
        self.xy_rel = xy_rel
        self.z_abs = z_abs
        self.z_rel = z_rel
        self._error_added = True

    def __eq__(self, other):
        if isinstance(other, DataQuality):
            if (
                self.date == other.date
                and self.post_processing == other.post_processing
                and self.source == other.source
                and self.post_processing_comment == other.post_processing_comment
                and self.source_comment == other.source_comment
                and self.xy_abs == other.xy_abs
                and self.xy_rel == other.xy_rel
                and self.z_abs == other.z_abs
                and self.z_rel == other.z_rel
            ):
                return True
        return False

    def get_element(self):
        """returns the elementTree of the Junction"""
        element = ET.Element("dataQuality")
        if self._raw_data_added:
            raw_data_attrib = {
                "date": self.date,
                "postProcessing": enum2str(self.post_processing),
                "source": enum2str(self.source),
            }
            if self.post_processing_comment is not None:
                raw_data_attrib["postProcessingComment"] = self.post_processing_comment
            if self.source_comment is not None:
                raw_data_attrib["sourceComment"] = self.source_comment

            ET.SubElement(element, "rawData", attrib=raw_data_attrib)

        if self._error_added:
            ET.SubElement(
                element,
                "error",
                attrib={
                    "xyAbsolute": str(self.xy_abs),
                    "xyRelative": str(self.xy_rel),
                    "zAbsolute": str(self.z_rel),
                    "zRelative": str(self.z_rel),
                },
            )
        return element
