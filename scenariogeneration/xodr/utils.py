"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import xml.etree.ElementTree as ET
from typing import Optional

import numpy as np

from ..helpers import enum2str
from .enumerations import ContactPoint


def get_lane_sec_and_s_for_lane_calc(
    road: "Road", contact_point: "ContactPoint"
) -> tuple[int, float]:
    """Get a lane section and s-coordinate for calculations at either the
    start or end of a road.

    Parameters
    ----------
    road : Road
        The road to be used.
    contact_point : ContactPoint
        Start or end of the road.

    Returns
    -------
    tuple[int, float]
        A tuple containing:
        - lanesection (int): 0 or -1, indicating the relevant lane section.
        - s (float): The s-coordinate at the start or end of the road.
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


def get_coeffs_for_poly3(
    length: float,
    lane_offset: float,
    zero_start: bool,
    lane_width_end: Optional[float] = None,
) -> tuple[float, float, float, float]:
    """Create the coefficients for a third-degree polynomial, which can be
    used for various descriptions in OpenDRIVE.

    Assumes that the derivative is 0 at the start and end of the segment.

    Parameters
    ----------
    length : float
        Length of the segment in the s-direction.
    lane_offset : float
        The lane offset (width) of the lane.
    zero_start : bool
        If True, starts with zero and ends with `lane_offset` width.
        If False, starts with `lane_offset` and ends with zero width.
    lane_width_end : float, optional
        Specifies the ending lane width for lanes that may start and end
        with different widths. Default is None.

    Returns
    -------
    tuple[float, float, float, float]
        Polynomial coefficients corresponding to "a, b, c, d" in the
        OpenDRIVE polynomials.
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
    """Sets up common functionality for xodr-generating classes by enabling
    userdata inputs.

    Attributes
    ----------
    user_data : list[UserData]
        All userdata added to the xodr entry.
    data_quality : DataQuality, optional
        Data quality information for the xodr entry.

    Methods
    -------
    add_userdata(userdata)
        Adds a userdata entry to the xodr entry.
    add_dataquality(dataquality)
        Adds a data quality entry to the xodr entry.
    _add_additional_data_to_element(element)
        Adds userdata and data quality to an XML element.
    """

    def __init__(self) -> None:
        """Initialize the XodrBase instance.

        Attributes
        ----------
        user_data : list[UserData]
            A list to store all userdata entries added to the xodr entry.
        data_quality : Optional[DataQuality]
            Data quality information for the xodr entry.
        """
        self.user_data = []
        self.data_quality = None

    def __eq__(self, other: object) -> bool:
        if (
            self.user_data == other.user_data
            and self.data_quality == other.data_quality
        ):
            return True

        return False

    def add_userdata(self, userdata: "UserData") -> None:
        """Add a userdata entry to the xodr entry.

        Parameters
        ----------
        userdata : UserData
            The userdata to be added.

        Raises
        ------
        TypeError
            If the provided userdata is not of type UserData.
        """
        if not isinstance(userdata, UserData):
            raise TypeError("userdata is not of type UserData.")
        self.user_data.append(userdata)

    def add_dataquality(self, dataquality: "DataQuality") -> None:
        """Add a data quality entry to the xodr entry.

        Parameters
        ----------
        dataquality : DataQuality
            The data quality to be added.

        Raises
        ------
        TypeError
            If the provided dataquality is not of type DataQuality.
        """
        if not isinstance(dataquality, DataQuality):
            raise TypeError("dataquality is not of type DataQuality.")
        self.data_quality = dataquality

    def _add_additional_data_to_element(
        self, element: ET.Element
    ) -> ET.Element:
        """Add userdata and data quality to an XML element.

        Parameters
        ----------
        element : ET.Element
            The XML element to which userdata and data quality will be added.

        Returns
        -------
        ET.Element
            The updated XML element.
        """
        for ud in self.user_data:
            element.append(ud.get_element())
        if self.data_quality:
            element.append(self.data_quality.get_element())
        return element


class UserData:
    """Sets up additional data for any entry of OpenDRIVE.

    Attributes
    ----------
    code : str
        Code of the userdata.
    value : str, optional
        Value of the userdata.
    user_data_content : list[ET.Element]
        List of all extra elements added.

    Methods
    -------
    add_userdata_content(content)
        Adds extra elements to the userdata.
    get_element()
        Returns the full ElementTree representation of the UserData.
    get_attributes()
        Returns a dictionary of all attributes of the UserData.
    """

    def __init__(self, code: str, value: Optional[str] = None) -> None:
        """Initialize the UserData.

        Parameters
        ----------
        code : str
            Code of the userdata.
        value : str, optional
            Value of the userdata. Default is None.
        """
        self.code = code
        self.value = value
        self.userdata_content = []

    def add_userdata_content(self, content: ET.Element) -> None:
        """Add extra elements to the userdata.

        Parameters
        ----------
        content : ET.Element
            The element to be added.
        """
        self.userdata_content.append(content)

    def _element_equals(self, e1: ET.Element, e2: ET.Element) -> bool:
        """Compare two XML elements for equality.

        Parameters
        ----------
        e1 : ET.Element
            The first element to compare.
        e2 : ET.Element
            The second element to compare.

        Returns
        -------
        bool
            True if the elements are equal, False otherwise.
        """
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

    def __eq__(self, other: object) -> bool:
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

    def get_attributes(self) -> dict[str, str]:
        """Return the attributes of the UserData as a dictionary.

        Returns
        -------
        dict[str, str]
            A dictionary containing the attributes of the UserData.
        """
        retdict = {}
        retdict["code"] = str(self.code)
        if self.value is not None:
            retdict["value"] = str(self.value)
        return retdict

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the UserData.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the UserData.
        """
        element = ET.Element("userData", attrib=self.get_attributes())
        for i in self.userdata_content:
            element.append(i)
        return element


class DataQuality:
    """Sets up DataQuality for any entry of OpenDRIVE.

    Attributes
    ----------
    date : str, optional
        Date of the data.
    post_processing : RawDataPostProcessing, optional
        Postprocessing definition.
    source : RawDataSource, optional
        Source of the data.
    post_processing_comment : str, optional
        Comment about the postprocessing.
    source_comment : str, optional
        Comment about the source.
    xy_abs : float, optional
        Absolute xy error.
    xy_rel : float, optional
        Relative xy error.
    z_abs : float, optional
        Absolute z error.
    z_rel : float, optional
        Relative z error.

    Methods
    -------
    add_raw_data_info(date, post_processing, source, post_processing_comment, source_comment)
        Adds raw data information.
    add_error(xy_abs, xy_rel, z_abs, z_rel)
        Adds error information.
    get_element()
        Returns the full ElementTree representation of the DataQuality.
    """

    def __init__(self) -> None:
        """Initialize the DataQuality instance.

        Attributes
        ----------
        date : Optional[str]
            Date of the data.
        post_processing : Optional[RawDataPostProcessing]
            Postprocessing definition.
        source : Optional[RawDataSource]
            Source of the data.
        post_processing_comment : Optional[str]
            Comment about the postprocessing.
        source_comment : Optional[str]
            Comment about the source.
        xy_abs : Optional[float]
            Absolute xy error.
        xy_rel : Optional[float]
            Relative xy error.
        z_abs : Optional[float]
            Absolute z error.
        z_rel : Optional[float]
            Relative z error.
        _error_added : bool
            Indicates if error information has been added.
        _raw_data_added : bool
            Indicates if raw data information has been added.
        """
        self.date: Optional[str] = None
        self.post_processing: Optional["RawDataPostProcessing"] = None
        self.source: Optional["RawDataSource"] = None
        self.post_processing_comment: Optional[str] = None
        self.source_comment: Optional[str] = None
        self.xy_abs: Optional[float] = None
        self.xy_rel: Optional[float] = None
        self.z_abs: Optional[float] = None
        self.z_rel: Optional[float] = None
        self._error_added: bool = False
        self._raw_data_added: bool = False

    def add_raw_data_info(
        self,
        date: str,
        post_processing: "RawDataPostProcessing",
        source: "RawDataSource",
        post_processing_comment: Optional[str] = None,
        source_comment: Optional[str] = None,
    ) -> None:
        """Add raw data information to the DataQuality.

        Parameters
        ----------
        date : str
            Date of the data.
        post_processing : RawDataPostProcessing
            Postprocessing definition.
        source : RawDataSource
            Source of the data.
        post_processing_comment : str, optional
            Comment about the postprocessing. Default is None.
        source_comment : str, optional
            Comment about the source. Default is None.
        """

        self.date = date
        self.post_processing = post_processing
        self.source = source
        self.post_processing_comment = post_processing_comment
        self.source_comment = source_comment
        self._raw_data_added = True

    def add_error(
        self, xy_abs: float, xy_rel: float, z_abs: float, z_rel: float
    ) -> None:
        """Add error information to the DataQuality.

        Parameters
        ----------
        xy_abs : float
            Absolute xy error.
        xy_rel : float
            Relative xy error.
        z_abs : float
            Absolute z error.
        z_rel : float
            Relative z error.
        """
        self.xy_abs = xy_abs
        self.xy_rel = xy_rel
        self.z_abs = z_abs
        self.z_rel = z_rel
        self._error_added = True

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DataQuality):
            if (
                self.date == other.date
                and self.post_processing == other.post_processing
                and self.source == other.source
                and self.post_processing_comment
                == other.post_processing_comment
                and self.source_comment == other.source_comment
                and self.xy_abs == other.xy_abs
                and self.xy_rel == other.xy_rel
                and self.z_abs == other.z_abs
                and self.z_rel == other.z_rel
            ):
                return True
        return False

    def get_element(self) -> ET.Element:
        """Return the ElementTree representation of the DataQuality.

        Returns
        -------
        ET.Element
            The XML ElementTree representation of the DataQuality.
        """
        element = ET.Element("dataQuality")
        if self._raw_data_added:
            raw_data_attrib = {
                "date": self.date,
                "postProcessing": enum2str(self.post_processing),
                "source": enum2str(self.source),
            }
            if self.post_processing_comment is not None:
                raw_data_attrib["postProcessingComment"] = (
                    self.post_processing_comment
                )
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
