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

from asposeslidescloud.models.geometry_shape import GeometryShape

class Shape(GeometryShape):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'self_uri': 'ResourceUri',
        'alternate_links': 'list[ResourceUri]',
        'name': 'str',
        'width': 'float',
        'height': 'float',
        'alternative_text': 'str',
        'alternative_text_title': 'str',
        'hidden': 'bool',
        'x': 'float',
        'y': 'float',
        'z_order_position': 'int',
        'shapes': 'ResourceUri',
        'fill_format': 'FillFormat',
        'effect_format': 'EffectFormat',
        'line_format': 'LineFormat',
        'type': 'str',
        'shape_type': 'str',
        'text': 'str',
        'paragraphs': 'ResourceUri'
    }

    attribute_map = {
        'self_uri': 'selfUri',
        'alternate_links': 'alternateLinks',
        'name': 'name',
        'width': 'width',
        'height': 'height',
        'alternative_text': 'alternativeText',
        'alternative_text_title': 'alternativeTextTitle',
        'hidden': 'hidden',
        'x': 'x',
        'y': 'y',
        'z_order_position': 'zOrderPosition',
        'shapes': 'shapes',
        'fill_format': 'fillFormat',
        'effect_format': 'effectFormat',
        'line_format': 'lineFormat',
        'type': 'type',
        'shape_type': 'shapeType',
        'text': 'text',
        'paragraphs': 'paragraphs'
    }

    type_determiners = {
        'type': 'Shape',
    }

    def __init__(self, self_uri=None, alternate_links=None, name=None, width=None, height=None, alternative_text=None, alternative_text_title=None, hidden=None, x=None, y=None, z_order_position=None, shapes=None, fill_format=None, effect_format=None, line_format=None, type='Shape', shape_type=None, text=None, paragraphs=None):  # noqa: E501
        """Shape - a model defined in Swagger"""  # noqa: E501
        super(Shape, self).__init__(self_uri, alternate_links, name, width, height, alternative_text, alternative_text_title, hidden, x, y, z_order_position, shapes, fill_format, effect_format, line_format, type, shape_type)

        self._text = None
        self._paragraphs = None
        self.type = 'Shape'

        if text is not None:
            self.text = text
        if paragraphs is not None:
            self.paragraphs = paragraphs

    @property
    def text(self):
        """Gets the text of this Shape.  # noqa: E501

        Gets or sets the text.  # noqa: E501

        :return: The text of this Shape.  # noqa: E501
        :rtype: str
        """
        return self._text

    @text.setter
    def text(self, text):
        """Sets the text of this Shape.

        Gets or sets the text.  # noqa: E501

        :param text: The text of this Shape.  # noqa: E501
        :type: str
        """
        self._text = text

    @property
    def paragraphs(self):
        """Gets the paragraphs of this Shape.  # noqa: E501

        Get or sets list to paragraphs list  # noqa: E501

        :return: The paragraphs of this Shape.  # noqa: E501
        :rtype: ResourceUri
        """
        return self._paragraphs

    @paragraphs.setter
    def paragraphs(self, paragraphs):
        """Sets the paragraphs of this Shape.

        Get or sets list to paragraphs list  # noqa: E501

        :param paragraphs: The paragraphs of this Shape.  # noqa: E501
        :type: ResourceUri
        """
        self._paragraphs = paragraphs

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
        if not isinstance(other, Shape):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
