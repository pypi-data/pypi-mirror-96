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

class Save(Task):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'type': 'str',
        'format': 'str',
        'output': 'OutputFile',
        'options': 'ExportOptions'
    }

    attribute_map = {
        'type': 'type',
        'format': 'format',
        'output': 'output',
        'options': 'options'
    }

    type_determiners = {
        'type': 'Save',
    }

    def __init__(self, type='Save', format=None, output=None, options=None):  # noqa: E501
        """Save - a model defined in Swagger"""  # noqa: E501
        super(Save, self).__init__(type)

        self._format = None
        self._output = None
        self._options = None
        self.type = 'Save'

        self.format = format
        if output is not None:
            self.output = output
        if options is not None:
            self.options = options

    @property
    def format(self):
        """Gets the format of this Save.  # noqa: E501

        Format.  # noqa: E501

        :return: The format of this Save.  # noqa: E501
        :rtype: str
        """
        return self._format

    @format.setter
    def format(self, format):
        """Sets the format of this Save.

        Format.  # noqa: E501

        :param format: The format of this Save.  # noqa: E501
        :type: str
        """
        if format is not None:
            allowed_values = ["Pdf", "Xps", "Tiff", "Pptx", "Odp", "Otp", "Ppt", "Pps", "Ppsx", "Pptm", "Ppsm", "Pot", "Potx", "Potm", "Html", "Swf", "Svg", "Jpeg", "Png", "Gif", "Bmp", "Fodp"]  # noqa: E501
            if format.isdigit():
                int_format = int(format)
                if int_format < 0 or int_format >= len(allowed_values):
                    raise ValueError(
                        "Invalid value for `format` ({0}), must be one of {1}"  # noqa: E501
                        .format(format, allowed_values)
                    )
                self._format = allowed_values[int_format]
                return
            if format not in allowed_values:
                raise ValueError(
                    "Invalid value for `format` ({0}), must be one of {1}"  # noqa: E501
                    .format(format, allowed_values)
                )
        self._format = format

    @property
    def output(self):
        """Gets the output of this Save.  # noqa: E501

        Output file.  # noqa: E501

        :return: The output of this Save.  # noqa: E501
        :rtype: OutputFile
        """
        return self._output

    @output.setter
    def output(self, output):
        """Sets the output of this Save.

        Output file.  # noqa: E501

        :param output: The output of this Save.  # noqa: E501
        :type: OutputFile
        """
        self._output = output

    @property
    def options(self):
        """Gets the options of this Save.  # noqa: E501

        Save options.  # noqa: E501

        :return: The options of this Save.  # noqa: E501
        :rtype: ExportOptions
        """
        return self._options

    @options.setter
    def options(self, options):
        """Sets the options of this Save.

        Save options.  # noqa: E501

        :param options: The options of this Save.  # noqa: E501
        :type: ExportOptions
        """
        self._options = options

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
        if not isinstance(other, Save):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
