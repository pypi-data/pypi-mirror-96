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

from asposeslidescloud.models.task import Task

class UpdateShape(Task):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'shape': 'ShapeBase',
        'shape_path': 'str'
    }

    attribute_map = {
        'type': 'type',
        'shape': 'shape',
        'shape_path': 'shapePath'
    }

    type_determiners = {
        'type': 'UpdateShape',
    }

    def __init__(self, type='UpdateShape', shape=None, shape_path=None):  # noqa: E501
        """UpdateShape - a model defined in Swagger"""  # noqa: E501
        super(UpdateShape, self).__init__(type)

        self._shape = None
        self._shape_path = None
        self.type = 'UpdateShape'

        if shape is not None:
            self.shape = shape
        if shape_path is not None:
            self.shape_path = shape_path

    @property
    def shape(self):
        """Gets the shape of this UpdateShape.  # noqa: E501

        Shape DTO.  # noqa: E501

        :return: The shape of this UpdateShape.  # noqa: E501
        :rtype: ShapeBase
        """
        return self._shape

    @shape.setter
    def shape(self, shape):
        """Sets the shape of this UpdateShape.

        Shape DTO.  # noqa: E501

        :param shape: The shape of this UpdateShape.  # noqa: E501
        :type: ShapeBase
        """
        self._shape = shape

    @property
    def shape_path(self):
        """Gets the shape_path of this UpdateShape.  # noqa: E501

        Shape path for a grouped or SmartArt shape.  # noqa: E501

        :return: The shape_path of this UpdateShape.  # noqa: E501
        :rtype: str
        """
        return self._shape_path

    @shape_path.setter
    def shape_path(self, shape_path):
        """Sets the shape_path of this UpdateShape.

        Shape path for a grouped or SmartArt shape.  # noqa: E501

        :param shape_path: The shape_path of this UpdateShape.  # noqa: E501
        :type: str
        """
        self._shape_path = shape_path

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
        if not isinstance(other, UpdateShape):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
