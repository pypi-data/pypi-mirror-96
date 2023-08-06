# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose">
#   Copyright (c) 2018 Aspose.Slides for Cloud
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

import pprint
import re  # noqa: F401

import six


class LineFormat(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'alignment': 'str',
        'cap_style': 'str',
        'dash_style': 'str',
        'join_style': 'str',
        'style': 'str',
        'sketch_type': 'str',
        'begin_arrow_head': 'ArrowHeadProperties',
        'end_arrow_head': 'ArrowHeadProperties',
        'custom_dash_pattern': 'CustomDashPattern',
        'fill_format': 'FillFormat',
        'miter_limit': 'float',
        'width': 'float'
    }

    attribute_map = {
        'alignment': 'alignment',
        'cap_style': 'capStyle',
        'dash_style': 'dashStyle',
        'join_style': 'joinStyle',
        'style': 'style',
        'sketch_type': 'sketchType',
        'begin_arrow_head': 'beginArrowHead',
        'end_arrow_head': 'endArrowHead',
        'custom_dash_pattern': 'customDashPattern',
        'fill_format': 'fillFormat',
        'miter_limit': 'miterLimit',
        'width': 'width'
    }

    type_determiners = {
    }

    def __init__(self, alignment=None, cap_style=None, dash_style=None, join_style=None, style=None, sketch_type=None, begin_arrow_head=None, end_arrow_head=None, custom_dash_pattern=None, fill_format=None, miter_limit=None, width=None):  # noqa: E501
        """LineFormat - a model defined in Swagger"""  # noqa: E501

        self._alignment = None
        self._cap_style = None
        self._dash_style = None
        self._join_style = None
        self._style = None
        self._sketch_type = None
        self._begin_arrow_head = None
        self._end_arrow_head = None
        self._custom_dash_pattern = None
        self._fill_format = None
        self._miter_limit = None
        self._width = None

        if alignment is not None:
            self.alignment = alignment
        if cap_style is not None:
            self.cap_style = cap_style
        if dash_style is not None:
            self.dash_style = dash_style
        if join_style is not None:
            self.join_style = join_style
        if style is not None:
            self.style = style
        if sketch_type is not None:
            self.sketch_type = sketch_type
        if begin_arrow_head is not None:
            self.begin_arrow_head = begin_arrow_head
        if end_arrow_head is not None:
            self.end_arrow_head = end_arrow_head
        if custom_dash_pattern is not None:
            self.custom_dash_pattern = custom_dash_pattern
        if fill_format is not None:
            self.fill_format = fill_format
        if miter_limit is not None:
            self.miter_limit = miter_limit
        if width is not None:
            self.width = width

    @property
    def alignment(self):
        """Gets the alignment of this LineFormat.  # noqa: E501

        Alignment.  # noqa: E501

        :return: The alignment of this LineFormat.  # noqa: E501
        :rtype: str
        """
        return self._alignment

    @alignment.setter
    def alignment(self, alignment):
        """Sets the alignment of this LineFormat.

        Alignment.  # noqa: E501

        :param alignment: The alignment of this LineFormat.  # noqa: E501
        :type: str
        """
        if alignment is not None:
            allowed_values = ["Center", "Inset", "NotDefined"]  # noqa: E501
            if alignment.isdigit():
                int_alignment = int(alignment)
                if int_alignment < 0 or int_alignment >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `alignment` ({0}), must be one of {1}"  # noqa: E501
                        .format(alignment, allowed_values)
                    )
                self._alignment = allowed_values[int_alignment]
                return
            if alignment not in allowed_values:
                raise ValueError(
                    "Invalid value for `alignment` ({0}), must be one of {1}"  # noqa: E501
                    .format(alignment, allowed_values)
                )
        self._alignment = alignment

    @property
    def cap_style(self):
        """Gets the cap_style of this LineFormat.  # noqa: E501

        Cap style.  # noqa: E501

        :return: The cap_style of this LineFormat.  # noqa: E501
        :rtype: str
        """
        return self._cap_style

    @cap_style.setter
    def cap_style(self, cap_style):
        """Sets the cap_style of this LineFormat.

        Cap style.  # noqa: E501

        :param cap_style: The cap_style of this LineFormat.  # noqa: E501
        :type: str
        """
        if cap_style is not None:
            allowed_values = ["Round", "Square", "Flat", "NotDefined"]  # noqa: E501
            if cap_style.isdigit():
                int_cap_style = int(cap_style)
                if int_cap_style < 0 or int_cap_style >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `cap_style` ({0}), must be one of {1}"  # noqa: E501
                        .format(cap_style, allowed_values)
                    )
                self._cap_style = allowed_values[int_cap_style]
                return
            if cap_style not in allowed_values:
                raise ValueError(
                    "Invalid value for `cap_style` ({0}), must be one of {1}"  # noqa: E501
                    .format(cap_style, allowed_values)
                )
        self._cap_style = cap_style

    @property
    def dash_style(self):
        """Gets the dash_style of this LineFormat.  # noqa: E501

        Dash style.  # noqa: E501

        :return: The dash_style of this LineFormat.  # noqa: E501
        :rtype: str
        """
        return self._dash_style

    @dash_style.setter
    def dash_style(self, dash_style):
        """Sets the dash_style of this LineFormat.

        Dash style.  # noqa: E501

        :param dash_style: The dash_style of this LineFormat.  # noqa: E501
        :type: str
        """
        if dash_style is not None:
            allowed_values = ["Solid", "Dot", "Dash", "LargeDash", "DashDot", "LargeDashDot", "LargeDashDotDot", "SystemDash", "SystemDot", "SystemDashDot", "SystemDashDotDot", "Custom", "NotDefined"]  # noqa: E501
            if dash_style.isdigit():
                int_dash_style = int(dash_style)
                if int_dash_style < 0 or int_dash_style >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `dash_style` ({0}), must be one of {1}"  # noqa: E501
                        .format(dash_style, allowed_values)
                    )
                self._dash_style = allowed_values[int_dash_style]
                return
            if dash_style not in allowed_values:
                raise ValueError(
                    "Invalid value for `dash_style` ({0}), must be one of {1}"  # noqa: E501
                    .format(dash_style, allowed_values)
                )
        self._dash_style = dash_style

    @property
    def join_style(self):
        """Gets the join_style of this LineFormat.  # noqa: E501

        Join style.  # noqa: E501

        :return: The join_style of this LineFormat.  # noqa: E501
        :rtype: str
        """
        return self._join_style

    @join_style.setter
    def join_style(self, join_style):
        """Sets the join_style of this LineFormat.

        Join style.  # noqa: E501

        :param join_style: The join_style of this LineFormat.  # noqa: E501
        :type: str
        """
        if join_style is not None:
            allowed_values = ["Round", "Bevel", "Miter", "NotDefined"]  # noqa: E501
            if join_style.isdigit():
                int_join_style = int(join_style)
                if int_join_style < 0 or int_join_style >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `join_style` ({0}), must be one of {1}"  # noqa: E501
                        .format(join_style, allowed_values)
                    )
                self._join_style = allowed_values[int_join_style]
                return
            if join_style not in allowed_values:
                raise ValueError(
                    "Invalid value for `join_style` ({0}), must be one of {1}"  # noqa: E501
                    .format(join_style, allowed_values)
                )
        self._join_style = join_style

    @property
    def style(self):
        """Gets the style of this LineFormat.  # noqa: E501

        Style.  # noqa: E501

        :return: The style of this LineFormat.  # noqa: E501
        :rtype: str
        """
        return self._style

    @style.setter
    def style(self, style):
        """Sets the style of this LineFormat.

        Style.  # noqa: E501

        :param style: The style of this LineFormat.  # noqa: E501
        :type: str
        """
        if style is not None:
            allowed_values = ["Single", "ThinThin", "ThinThick", "ThickThin", "ThickBetweenThin", "NotDefined"]  # noqa: E501
            if style.isdigit():
                int_style = int(style)
                if int_style < 0 or int_style >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `style` ({0}), must be one of {1}"  # noqa: E501
                        .format(style, allowed_values)
                    )
                self._style = allowed_values[int_style]
                return
            if style not in allowed_values:
                raise ValueError(
                    "Invalid value for `style` ({0}), must be one of {1}"  # noqa: E501
                    .format(style, allowed_values)
                )
        self._style = style

    @property
    def sketch_type(self):
        """Gets the sketch_type of this LineFormat.  # noqa: E501

        Sketch type.  # noqa: E501

        :return: The sketch_type of this LineFormat.  # noqa: E501
        :rtype: str
        """
        return self._sketch_type

    @sketch_type.setter
    def sketch_type(self, sketch_type):
        """Sets the sketch_type of this LineFormat.

        Sketch type.  # noqa: E501

        :param sketch_type: The sketch_type of this LineFormat.  # noqa: E501
        :type: str
        """
        if sketch_type is not None:
            allowed_values = ["None", "Curved", "Freehand", "Scribble", "NotDefined"]  # noqa: E501
            if sketch_type.isdigit():
                int_sketch_type = int(sketch_type)
                if int_sketch_type < 0 or int_sketch_type >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `sketch_type` ({0}), must be one of {1}"  # noqa: E501
                        .format(sketch_type, allowed_values)
                    )
                self._sketch_type = allowed_values[int_sketch_type]
                return
            if sketch_type not in allowed_values:
                raise ValueError(
                    "Invalid value for `sketch_type` ({0}), must be one of {1}"  # noqa: E501
                    .format(sketch_type, allowed_values)
                )
        self._sketch_type = sketch_type

    @property
    def begin_arrow_head(self):
        """Gets the begin_arrow_head of this LineFormat.  # noqa: E501

        Begin arrowhead.  # noqa: E501

        :return: The begin_arrow_head of this LineFormat.  # noqa: E501
        :rtype: ArrowHeadProperties
        """
        return self._begin_arrow_head

    @begin_arrow_head.setter
    def begin_arrow_head(self, begin_arrow_head):
        """Sets the begin_arrow_head of this LineFormat.

        Begin arrowhead.  # noqa: E501

        :param begin_arrow_head: The begin_arrow_head of this LineFormat.  # noqa: E501
        :type: ArrowHeadProperties
        """
        self._begin_arrow_head = begin_arrow_head

    @property
    def end_arrow_head(self):
        """Gets the end_arrow_head of this LineFormat.  # noqa: E501

        End arrowhead.  # noqa: E501

        :return: The end_arrow_head of this LineFormat.  # noqa: E501
        :rtype: ArrowHeadProperties
        """
        return self._end_arrow_head

    @end_arrow_head.setter
    def end_arrow_head(self, end_arrow_head):
        """Sets the end_arrow_head of this LineFormat.

        End arrowhead.  # noqa: E501

        :param end_arrow_head: The end_arrow_head of this LineFormat.  # noqa: E501
        :type: ArrowHeadProperties
        """
        self._end_arrow_head = end_arrow_head

    @property
    def custom_dash_pattern(self):
        """Gets the custom_dash_pattern of this LineFormat.  # noqa: E501

        Custom dash pattern.  # noqa: E501

        :return: The custom_dash_pattern of this LineFormat.  # noqa: E501
        :rtype: CustomDashPattern
        """
        return self._custom_dash_pattern

    @custom_dash_pattern.setter
    def custom_dash_pattern(self, custom_dash_pattern):
        """Sets the custom_dash_pattern of this LineFormat.

        Custom dash pattern.  # noqa: E501

        :param custom_dash_pattern: The custom_dash_pattern of this LineFormat.  # noqa: E501
        :type: CustomDashPattern
        """
        self._custom_dash_pattern = custom_dash_pattern

    @property
    def fill_format(self):
        """Gets the fill_format of this LineFormat.  # noqa: E501

        Fill format.  # noqa: E501

        :return: The fill_format of this LineFormat.  # noqa: E501
        :rtype: FillFormat
        """
        return self._fill_format

    @fill_format.setter
    def fill_format(self, fill_format):
        """Sets the fill_format of this LineFormat.

        Fill format.  # noqa: E501

        :param fill_format: The fill_format of this LineFormat.  # noqa: E501
        :type: FillFormat
        """
        self._fill_format = fill_format

    @property
    def miter_limit(self):
        """Gets the miter_limit of this LineFormat.  # noqa: E501

        Miter limit.  # noqa: E501

        :return: The miter_limit of this LineFormat.  # noqa: E501
        :rtype: float
        """
        return self._miter_limit

    @miter_limit.setter
    def miter_limit(self, miter_limit):
        """Sets the miter_limit of this LineFormat.

        Miter limit.  # noqa: E501

        :param miter_limit: The miter_limit of this LineFormat.  # noqa: E501
        :type: float
        """
        self._miter_limit = miter_limit

    @property
    def width(self):
        """Gets the width of this LineFormat.  # noqa: E501

        Width.  # noqa: E501

        :return: The width of this LineFormat.  # noqa: E501
        :rtype: float
        """
        return self._width

    @width.setter
    def width(self, width):
        """Sets the width of this LineFormat.

        Width.  # noqa: E501

        :param width: The width of this LineFormat.  # noqa: E501
        :type: float
        """
        self._width = width

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, LineFormat):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
