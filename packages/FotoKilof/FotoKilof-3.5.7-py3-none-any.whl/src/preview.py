# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
Copyright (c) 2019-2020 Tomasz Łuczak, TeaM-TL

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

"""
module contains function for generating preview and histogram:
- preview_histogram
- preview_convert
 """

import os
import tempfile

import common
import log
import magick


def preview_histogram(file_in, gm_or_im):
    """
    histogram generation
    file_in - fullname image file
    dir_temp - fullname temporary directory
    --
    return: fullname of histogram
    """

    cmd_magick = gm_or_im + "convert"
    file_histogram = os.path.join(tempfile.gettempdir(),
                                  "fotokilof_" + os.getlogin() \
                                  + "_histogram.ppm")
    command = " -define histogram:unique-colors=false histogram:"
    command = " histogram:"

    magick.magick(command, file_in, file_histogram, cmd_magick)
    try:
        os.system(command)
        return file_histogram
    except:
        log.write_log("Error in convert_histogram: " + command, "E")


def preview_convert(file_in, command, size, gm_or_im):
    """
    preview generation
    file_in - fullname image file
    dir_temp - fullname temporary directory
    command - additional command for imagemagick or space
    --
    return: fullname preview file and size
    """
    try:
        image_size = magick.get_image_size(file_in, gm_or_im)
        width = str(image_size[0])
        height = str(image_size[1])
        filesize = common.humansize(os.path.getsize(file_in))

        cmd_magick = gm_or_im + "convert"
        command = " -resize " + str(size) + "x" + str(size) + command
        file_preview = os.path.join(tempfile.gettempdir(),
                                    "fotokilof_" + os.getlogin() \
                                    + "_preview.ppm")
        magick.magick(command, file_in, file_preview, cmd_magick)

        result = {'filename': file_preview, 'size': filesize, \
                'width': width, 'height': height}
    except:
        log.write_log("Error in preview_convert: return", "E")
        result = None

    return result

# EOF
