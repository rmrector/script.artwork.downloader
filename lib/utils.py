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

#import modules
import lib.common
import os
import socket
import xbmc
import xbmcgui
import unicodedata
import urllib
import urllib2
import sys

# Use json instead of simplejson when python v2.7 or greater
if sys.version_info < (2, 7):
    import simplejson as json
else:
    import json
# Commoncache plugin import
try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

### import libraries
from lib.script_exceptions import *
from urllib2 import HTTPError, URLError

### get addon info
__addon__        = lib.common.__addon__
__localize__     = lib.common.__localize__
__addonname__    = lib.common.__addonname__
__icon__         = lib.common.__icon__
__addonid__ = lib.common.__addonid__

cache = StorageServer.StorageServer("ArtworkDownloader",240)

### Adjust default timeout to stop script hanging
socket.setdefaulttimeout(20)
### Cache bool
CACHE_ON = True

### Declare dialog
dialog = xbmcgui.DialogProgress()


# Fixes unicode problems
def string_unicode(text, encoding='utf-8'):
    try:
        text = unicode( text, encoding )
    except:
        pass
    return text

def normalize_string(text):
    try:
        text = unicodedata.normalize('NFKD', string_unicode(text)).encode('ascii', 'ignore')
    except:
        pass
    return text

# Define log messages
def log(txt, severity=xbmc.LOGDEBUG):
    if severity == xbmc.LOGDEBUG and not __addon__.getSetting("debug_enabled") == 'true':
        pass
    else:
        if severity < xbmc.LOGNOTICE:
            severity = xbmc.LOGNOTICE
        try:
            message = ('[%s] %s' % (__addonid__,txt) )
            xbmc.log(msg=message, level=severity)
        except UnicodeEncodeError:
            try:
                message = normalize_string('%s: %s' % (__addonname__,txt) )
                xbmc.log(msg=message, level=severity)
            except:
                message = ('%s: UnicodeEncodeError' %__addonname__)
                xbmc.log(msg=message, level=xbmc.LOGWARNING)

# Define dialogs
def dialog_msg(action,
               percentage = 0,
               line0 = '',
               line1 = '',
               line2 = '',
               line3 = '',
               background = False,
               nolabel = __localize__(32026),
               yeslabel = __localize__(32025),
               cancelled = False):

    # Dialog logic
    if not line0 == '':
        line0 = __addonname__ + line0
    else:
        line0 = __addonname__
    if not background:
        if action == 'create':
            dialog.create(__addonname__, line1, line2, line3)
        if action == 'update':
            dialog.update(percentage, line1, line2, line3)
        if action == 'close':
            dialog.close()
        if action == 'iscanceled':
            if dialog.iscanceled():
                return True
            else:
                return False
        if action == 'okdialog':
            xbmcgui.Dialog().ok(line0, line1, line2, line3)
        if action == 'yesno':
            return xbmcgui.Dialog().yesno(line0, line1, line2, line3, nolabel, yeslabel)
    if background:
        if (action == 'create' or action == 'okdialog'):
            if line2 == '':
                msg = line1
            else:
                msg = line1 + ': ' + line2
            if cancelled == False:
                xbmc.executebuiltin("XBMC.Notification(%s, %s, 7500, %s)" % (line0, msg, __icon__))

# Retrieve JSON data from cache function
def get_data(url, data_type ='json'):
    log('API: %s'% url)
    if CACHE_ON:
        result = cache.cacheFunction(get_data_new, url, data_type)
    else:
        result = get_data_new(url, data_type)
    if not result:
        result = 'Empty'
    return result

# Retrieve JSON data from site
def get_data_new(url, data_type):
    log('Cache expired. Retrieving new data')
    data = []
    try:
        request = urllib2.Request(url)
        # TMDB needs a header to be able to read the data
        if url.startswith("http://api.themoviedb.org"):
            request.add_header("Accept", "application/json")
        req = urllib2.urlopen(request)
        if data_type == 'json':
            data = json.loads(req.read())
            if not data:
                data = 'Empty'
        else:
            data = req.read()
        req.close()
    except HTTPError, e:
        if e.code == 400:
            raise HTTP400Error(url)
        elif e.code == 404:
            raise HTTP404Error(url)
        elif e.code == 503:
            raise HTTP503Error(url)
        elif e.code == 429:
            # Too many requests.
            xbmc.sleep(2000)
            return get_data_new(url, data_type)
        else:
            raise DownloadError(str(e))
    except URLError:
        raise HTTPTimeout(url)
    except socket.timeout, e:
        raise HTTPTimeout(url)
    except:
        data = 'Empty'
    return data

# Clean filenames for illegal character in the safest way for windows
def clean_filename(filename):
    illegal_char = '<>:"/\|?*'
    for char in illegal_char:
        filename = filename.replace( char , '' )
    return filename

def save_nfo_file(data, target):
    try:
        # open source path for writing and write xmlSource
        file_object = open(target.encode("utf-8"), "w")
        file_object.write(data.encode( "utf-8" ))
        file_object.close()
        return True
    except Exception, e:
        log(str(e), xbmc.LOGERROR)
        return False

def unquoteimage(imagestring):
    if imagestring.startswith('image://'):
        return urllib.unquote(imagestring[8:-1])
    else:
        return imagestring

def basename(path):
    return os.path.splitext(os.path.basename(path))[0]

watch_addon_filter = ['*']

_log_level_tag_lookup = {
    xbmc.LOGDEBUG: 'D',
    xbmc.LOGINFO: 'I'
}

def rlog(message, level=xbmc.LOGDEBUG):
    if '*' not in watch_addon_filter and __addonid__ not in watch_addon_filter and level < xbmc.LOGNOTICE:
        return

    if level < xbmc.LOGNOTICE:
        # Don't want to turn on full Kodi debug logging, so just elevate at the moment
        level_tag = _log_level_tag_lookup[level] + ': ' if level in _log_level_tag_lookup else ''
        level = xbmc.LOGNOTICE
    else:
        level_tag = ''

    if isinstance(message, (dict, list, tuple)):
        message = json.dumps(message, skipkeys=True, ensure_ascii=False, indent=2, cls=LogJSONEncoder)
        if isinstance(message, unicode):
            message = message.encode('utf-8')
    elif isinstance(message, unicode):
        message = message.encode('utf-8')
    elif not isinstance(message, str):
        message = str(message)

    #Log to file
    file_message = '%s[%s] %s' % (level_tag, __addonid__, message)
    xbmc.log(file_message, level)

class LogJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, tuple):
            return list(obj)
        # switch this to isinstance collections.Mapping (make dict) and collections.Iterable (make list)
        elif hasattr(obj, 'keys'):
            return dict((key, obj[key]) for key in obj.keys())
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
