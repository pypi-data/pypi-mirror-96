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


class TableRow(object):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'cells': 'list[TableCell]',
        'minimal_height': 'float',
        'height': 'float'
    }

    attribute_map = {
        'cells': 'cells',
        'minimal_height': 'minimalHeight',
        'height': 'height'
    }

    type_determiners = {
    }

    def __init__(self, cells=None, minimal_height=None, height=None):  # noqa: E501
        """TableRow - a model defined in Swagger"""  # noqa: E501

        self._cells = None
        self._minimal_height = None
        self._height = None

        if cells is not None:
            self.cells = cells
        self.minimal_height = minimal_height
        self.height = height

    @property
    def cells(self):
        """Gets the cells of this TableRow.  # noqa: E501

        Cells for the row.  # noqa: E501

        :return: The cells of this TableRow.  # noqa: E501
        :rtype: list[TableCell]
        """
        return self._cells

    @cells.setter
    def cells(self, cells):
        """Sets the cells of this TableRow.

        Cells for the row.  # noqa: E501

        :param cells: The cells of this TableRow.  # noqa: E501
        :type: list[TableCell]
        """
        self._cells = cells

    @property
    def minimal_height(self):
        """Gets the minimal_height of this TableRow.  # noqa: E501

        Minimal height of the row.  # noqa: E501

        :return: The minimal_height of this TableRow.  # noqa: E501
        :rtype: float
        """
        return self._minimal_height

    @minimal_height.setter
    def minimal_height(self, minimal_height):
        """Sets the minimal_height of this TableRow.

        Minimal height of the row.  # noqa: E501

        :param minimal_height: The minimal_height of this TableRow.  # noqa: E501
        :type: float
        """
        self._minimal_height = minimal_height

    @property
    def height(self):
        """Gets the height of this TableRow.  # noqa: E501

        Height of the row.  # noqa: E501

        :return: The height of this TableRow.  # noqa: E501
        :rtype: float
        """
        return self._height

    @height.setter
    def height(self, height):
        """Sets the height of this TableRow.

        Height of the row.  # noqa: E501

        :param height: The height of this TableRow.  # noqa: E501
        :type: float
        """
        self._height = height

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
        if not isinstance(other, TableRow):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
