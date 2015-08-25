import os
import xbmc
import xbmcgui
import xbmcvfs

import common
import quickjson
import utils
from settings import get_limit
from utils import log

limits = get_limit()

localize = common.__localize__
messages = {
    'canceled': localize(32017),
    'finished': localize(32012),
    'title': localize(32042),
    'processing': localize(32021),
    'movies': localize(32071),
    'tvshows': localize(32081),
    'musicvideos': localize(32091),
    'upgradeonce': localize(32155),
    'noitems': localize(32156)
}

def classic_extrafanart_tolibrary():
    progress = xbmcgui.DialogProgress()
    progress.create(messages['title'])
    progress.update(0, messages['processing'])

    max_fanart = limits['limit_extrafanart_max'] + 1
    movies = quickjson.get_movies()
    tvshows = quickjson.get_tvshows()
    musicvideos = quickjson.get_musicvideos()
    mediacount = len(movies) + len(tvshows) + len(musicvideos)
    if not mediacount:
        progress.close()
        xbmcgui.Dialog().ok(messages['title'], messages['noitems'])
        return

    canceled = False
    checkedcount = 0
    extrafanart_added = 0
    progress.update(1, '%s: %s' % (messages['processing'], messages['movies']))
    for movie in movies:
        extrafanart_added += _add_extrafanart_tolibrary('movie', movie, max_fanart)
        checkedcount += 1
        if checkedcount % 10 == 0:
            progress.update(checkedcount * 100 / mediacount, line2=movie['label'])
        if progress.iscanceled():
            canceled = True
            break

    if not canceled:
        progress.update(checkedcount * 100 / mediacount, '%s: %s' % (messages['processing'], messages['tvshows']))
        for tvshow in tvshows:
            extrafanart_added += _add_extrafanart_tolibrary('tvshow', tvshow, max_fanart)
            checkedcount += 1
            if checkedcount % 10 == 0:
                progress.update(checkedcount * 100 / mediacount, line2=tvshow['label'])
            if progress.iscanceled():
                canceled = True
                break

    if not canceled:
        progress.update(checkedcount * 100 / mediacount, '%s: %s' % (messages['processing'], messages['musicvideos']))
        for musicvideo in musicvideos:
            extrafanart_added += _add_extrafanart_tolibrary('musicvideo', musicvideo, max_fanart)
            checkedcount += 1
            if checkedcount % 10 == 0:
                progress.update(checkedcount * 100 / mediacount, line2=musicvideo['label'])
            if progress.iscanceled():
                canceled = True
                break

    message = "Scanned %s media and added %s extra fanart to the library.[CR]%s" % (checkedcount, extrafanart_added, messages['upgradeonce'])
    progress.close()

    xbmcgui.Dialog().ok("%s: %s" % (messages['canceled'] if canceled else messages['finished'], messages['title']), message)

def _add_extrafanart_tolibrary(itemtype, item, max_fanart):
    extrafanart_dir = os.path.dirname(item['file']).rstrip('/') + '/extrafanart/'
    if not xbmcvfs.exists(extrafanart_dir):
        return 0

    dbfanart = []
    for arttype, art in item['art'].iteritems():
        if arttype.startswith('fanart'):
            dbfanart.append(utils.unquoteimage(art))

    if len(dbfanart) >= max_fanart:
        return 0

    newfanart = []
    _, extrafanarts = xbmcvfs.listdir(extrafanart_dir)
    for extrafanart in extrafanarts:
        if not next((True for x in dbfanart if x.endswith(extrafanart)), False):
            newfanart_url = extrafanart_dir + extrafanart
            newfanart.append(newfanart_url)

    if not newfanart:
        return 0

    dbfanart_count = len(dbfanart)
    newfanartdict = {}
    maxaddindex = min(max_fanart - dbfanart_count, len(newfanart) - 1)
    for newfanart_index in range(maxaddindex):
        newfanartdict['fanart%s' % (dbfanart_count + newfanart_index)] = newfanart[newfanart_index]

    if itemtype == 'movie':
        id_param = 'movieid'
        jsonrpc_method = 'VideoLibrary.SetMovieDetails'
    elif itemtype == 'tvshow':
        id_param = 'tvshowid'
        jsonrpc_method = 'VideoLibrary.SetTVShowDetails'
    elif itemtype == 'musicvideo':
        id_param = 'musicvideoid'
        jsonrpc_method = 'VideoLibrary.SetMusicVideoDetails'
    else:
        log("Something is up, I don't know what to do with a '%s'. Not adding extrafanart for the selected item to library. %s" % (itemtype, item), xbmc.LOGWARNING)
        return 0

    json_request = quickjson.get_baserequest(jsonrpc_method)
    json_request['params'][id_param] = item[id_param]
    json_request['params']['art'] = newfanartdict
    quickjson.execute_jsonrpc(json_request)
    return len(newfanartdict)
