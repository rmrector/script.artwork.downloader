#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2011-2014 Martijn Kaijser
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import sys
import xbmc
from lib import common
from lib import listbuilder
from lib.main import Main
from lib.utils import log

def main():
    # simplify the initial script in an attempt to reduce the start delay, and for multi fanart nearly every millisecond can count.
    if sys.argv[0].startswith('plugin://'):
        listbuilder.handle_pluginlist()
    else:
        log('######## Artwork Downloader: Initializing...............................', xbmc.LOGNOTICE)
        log('## Add-on Name = %s' % str(common.__addonname__), xbmc.LOGNOTICE)
        log('## Version     = %s' % str(common.__version__), xbmc.LOGNOTICE)
        Main()
        log('script stopped', xbmc.LOGNOTICE)

if __name__ == '__main__':
    main()
