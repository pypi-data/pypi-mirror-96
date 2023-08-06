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

from asposeslidescloud.models.resource_base import ResourceBase

class Theme(ResourceBase):


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
        'color_scheme': 'ResourceUri',
        'font_scheme': 'ResourceUri',
        'format_scheme': 'ResourceUri'
    }

    attribute_map = {
        'self_uri': 'selfUri',
        'alternate_links': 'alternateLinks',
        'name': 'name',
        'color_scheme': 'colorScheme',
        'font_scheme': 'fontScheme',
        'format_scheme': 'formatScheme'
    }

    type_determiners = {
    }

    def __init__(self, self_uri=None, alternate_links=None, name=None, color_scheme=None, font_scheme=None, format_scheme=None):  # noqa: E501
        """Theme - a model defined in Swagger"""  # noqa: E501
        super(Theme, self).__init__(self_uri, alternate_links)

        self._name = None
        self._color_scheme = None
        self._font_scheme = None
        self._format_scheme = None

        if name is not None:
            self.name = name
        if color_scheme is not None:
            self.color_scheme = color_scheme
        if font_scheme is not None:
            self.font_scheme = font_scheme
        if format_scheme is not None:
            self.format_scheme = format_scheme

    @property
    def name(self):
        """Gets the name of this Theme.  # noqa: E501

        Name.  # noqa: E501

        :return: The name of this Theme.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Theme.

        Name.  # noqa: E501

        :param name: The name of this Theme.  # noqa: E501
        :type: str
        """
        self._name = name

    @property
    def color_scheme(self):
        """Gets the color_scheme of this Theme.  # noqa: E501

        Color scheme.  # noqa: E501

        :return: The color_scheme of this Theme.  # noqa: E501
        :rtype: ResourceUri
        """
        return self._color_scheme

    @color_scheme.setter
    def color_scheme(self, color_scheme):
        """Sets the color_scheme of this Theme.

        Color scheme.  # noqa: E501

        :param color_scheme: The color_scheme of this Theme.  # noqa: E501
        :type: ResourceUri
        """
        self._color_scheme = color_scheme

    @property
    def font_scheme(self):
        """Gets the font_scheme of this Theme.  # noqa: E501

        Font scheme.  # noqa: E501

        :return: The font_scheme of this Theme.  # noqa: E501
        :rtype: ResourceUri
        """
        return self._font_scheme

    @font_scheme.setter
    def font_scheme(self, font_scheme):
        """Sets the font_scheme of this Theme.

        Font scheme.  # noqa: E501

        :param font_scheme: The font_scheme of this Theme.  # noqa: E501
        :type: ResourceUri
        """
        self._font_scheme = font_scheme

    @property
    def format_scheme(self):
        """Gets the format_scheme of this Theme.  # noqa: E501

        Format scheme.  # noqa: E501

        :return: The format_scheme of this Theme.  # noqa: E501
        :rtype: ResourceUri
        """
        return self._format_scheme

    @format_scheme.setter
    def format_scheme(self, format_scheme):
        """Sets the format_scheme of this Theme.

        Format scheme.  # noqa: E501

        :param format_scheme: The format_scheme of this Theme.  # noqa: E501
        :type: ResourceUri
        """
        self._format_scheme = format_scheme

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
        if not isinstance(other, Theme):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
