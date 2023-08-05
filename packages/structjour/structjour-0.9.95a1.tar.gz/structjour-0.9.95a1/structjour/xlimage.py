# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

'''
Created on Oct 16, 2018

@author: Mike Petersen
'''
import logging
import os

from PIL import Image as PILImage
from PIL import ImageGrab
from openpyxl.drawing.image import Image


class XLImage:
    '''Handle image stuff'''

#     20.238095238095237
    def __init__(self, default='structjour/images/ZeroSubstanceCreation_500x334.png', heightInCells=20, pixPerCell=19.3):
        '''
        Create the XLImage, set the name and the size image here.
        :params default: Location of a default image to use
        :params heightInCells: Determine the height based on how many excel rows for the height.
        :params pixPerCell: The aproximate number of pixels per excel row.  Because this is
                            determined by issues beyond our control, it will (eventually) be
                            configurable in user settings. The number of pixels is unscientifically
                            determined (by me) to be about 19.3.

        '''
        if not os.path.exists(default):
            ddiirr = os.path.dirname(__file__)
            os.chdir(os.path.realpath(ddiirr))
            os.chdir(os.path.realpath('../'))
            if not os.path.exists(default):
                logging.warning('Cannot locate default image', default)
        self.defaultImage = default
        self.numCells = heightInCells
        self.pixPerCell = pixPerCell
        self.name = None

    def adjustSizeByHeight(self, sz, cells=None):
        '''
        Adjust size to keep the aspect ratio the same as determined by self.numCells and
        self.pixPerCell
        '''
        w, h = sz
        cells = cells if cells else self.numCells
        newHeight = cells * self.pixPerCell
        newWidth = newHeight * w / h
        nw = int(newWidth)
        nh = int(newHeight)
        return(nw, nh)

    def getDefaultPILImage(self):
        '''Return a default image'''
        im = PILImage.open(self.defaultImage)
        return im

    def getPilImageNoDramaForReal(self, name):
        '''
        '''
        # Setting  a default size for this method-- this should go in pref somehow
        img = None
        try:

            pilImage = ImageGrab.grabclipboard()
            if not pilImage:
                return None, 'Failed to retrieve image from clipboard.'
            nn, ext = os.path.splitext(name)
            pilImage.save(name, ext[1:])

            img = Image(name)

        except IOError as e:
            logging.error(e)
            if img:
                return img
            return None, e.__str__()

        return img, name

    def getPilImageNoDrama(self, name, outdir):
        '''
        Grab the contents of the clipboard to image. Warn the user if no image is retrieved. Then
        save the image to the indicated place {outdir/name.png} and return an image and the fname.
        :params name: The name to save the image.
        :param outdir: The location to save the images.
        :return img, pname: The pathname of the image we save. On failure return None and error
                            message
        '''

        # Setting  a default size for this method-- this should go in pref somehow
        CELLS = 33
        img = None
        try:
            if not os.path.exists(outdir):
                os.mkdir(outdir)

            # pilImage = self.getPilImage(msg)
            pilImage = ImageGrab.grabclipboard()
            # ext = pilImage.format.lower()
            if not pilImage:
                return None, 'Failed to retrieve image from clipboard.'
            newSize = self.adjustSizeByHeight(pilImage.size, CELLS)
            pilImage = pilImage.resize(newSize, PILImage.ANTIALIAS)

            pname, ext = self.getResizeName(name, outdir)
            pilImage.save(pname, ext)

            img = Image(pname)

        except IOError as e:
            logging.error(e)
            if img:
                return img
            return None, e.__str__()

        return img, pname

    def getResizeName(self, orig, outdir):
        '''
        Set the extension and format to png. (Be sure to save it with a png format). Create the
        pathfile name and return it.
        :params orig: The original pathfile name.
        :params outdir: The location to save to.
        :return: A tuple (newFileName, extension)
        '''
        import re

        def resub(s):
            '''Callable for re.sub. I am sure there is very cool concise re thing to do this but wtf.'''
            digit = s.string[s.span()[0] + 1:s.span()[1] - 1]
            digit = str((int(digit) + 1))
            return '(' + digit + ')'

        orig = orig.replace(":", "-")
        x = os.path.splitext(orig)
        newName = x[0]
        newName += '.png'
        self.name = newName

        newName = os.path.join(os.path.normpath(outdir), newName)
        # count = 0
        while True:
            # count += 1
            if os.path.exists(newName):

                nn, ext = os.path.splitext(newName)
                nn2 = re.sub('\\((-?\\d+)\\)', resub, nn)
                if nn2 == nn:
                    nn2 = nn2 + '(1)'
                newName = '{}{}'.format(nn2, ext)
            else:
                break

        return (newName, os.path.splitext(newName)[1][1:])
