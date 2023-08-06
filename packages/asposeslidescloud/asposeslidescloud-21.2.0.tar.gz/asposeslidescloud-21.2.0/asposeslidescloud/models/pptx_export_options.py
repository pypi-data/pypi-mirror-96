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

from asposeslidescloud.models.export_options import ExportOptions

class PptxExportOptions(ExportOptions):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'default_regular_font': 'str',
        'format': 'str',
        'conformance': 'str'
    }

    attribute_map = {
        'default_regular_font': 'defaultRegularFont',
        'format': 'format',
        'conformance': 'conformance'
    }

    type_determiners = {
        'format': 'pptx',
    }

    def __init__(self, default_regular_font=None, format='pptx', conformance=None):  # noqa: E501
        """PptxExportOptions - a model defined in Swagger"""  # noqa: E501
        super(PptxExportOptions, self).__init__(default_regular_font, format)

        self._conformance = None
        self.format = 'pptx'

        self.conformance = conformance

    @property
    def conformance(self):
        """Gets the conformance of this PptxExportOptions.  # noqa: E501

        The conformance class to which the PresentationML document conforms. Read/write Conformance.  # noqa: E501

        :return: The conformance of this PptxExportOptions.  # noqa: E501
        :rtype: str
        """
        return self._conformance

    @conformance.setter
    def conformance(self, conformance):
        """Sets the conformance of this PptxExportOptions.

        The conformance class to which the PresentationML document conforms. Read/write Conformance.  # noqa: E501

        :param conformance: The conformance of this PptxExportOptions.  # noqa: E501
        :type: str
        """
        if conformance is not None:
            allowed_values = ["Ecma376_2006", "Iso29500_2008_Transitional", "Iso29500_2008_Strict"]  # noqa: E501
            if conformance.isdigit():
                int_conformance = int(conformance)
                if int_conformance < 0 or int_conformance >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `conformance` ({0}), must be one of {1}"  # noqa: E501
                        .format(conformance, allowed_values)
                    )
                self._conformance = allowed_values[int_conformance]
                return
            if conformance not in allowed_values:
                raise ValueError(
                    "Invalid value for `conformance` ({0}), must be one of {1}"  # noqa: E501
                    .format(conformance, allowed_values)
                )
        self._conformance = conformance

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
        if not isinstance(other, PptxExportOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
