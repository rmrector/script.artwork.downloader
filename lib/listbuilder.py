import sys
import urllib
import xbmcgui
import xbmcplugin

def handle_pluginlist():
    path = get_pluginpath(True)
    if path['path'][0] == 'multiimage':
        build_list(multiimage(path), path['handle'])

def multiimage(path):
    """Stitch together a bunch of images for a 'multiimage' control. Feed it as many images as you want, any empty values are safely ignored. Great for multi fanart, like below:
    plugin://script.artwork.downloader/multiimage/?image=$INFO[Container(9001).ListItem.Art(fanart)]&amp;&amp;image=$INFO[Container(9001).ListItem.Art(fanart1)]&amp;&amp;image=$INFO[Container(9001).ListItem.Art(fanart2)]&amp;&amp;image=$INFO[Container(9001).ListItem.Art(fanart3)]&amp;&amp;image=$INFO[Container(9001).ListItem.Art(fanart4)]&amp;&amp;image=$INFO[Container(9001).ListItem.Art(fanart5)]
    """
    if 'image' not in path['query'] or not path['query']['image']:
        return []
    elif isinstance(path['query']['image'], list):
        return [unquoteimage(image) for image in path['query']['image'] if image]
    else:
        return [unquoteimage(path['query']['image'])]

def get_pluginpath(doublequerysplit=False):
    """Split path into a handy dict.
    Parameter 'doublequerysplit' requires '&&' to separate query bits, so skins can pass in paths that contain a querysplit.

    Returns dict keys:
    'handle' is plugin handle as int
    'path' is a list of folder/filename components
    'query' is another dict of the query. Duplicated keys are returned as a list of values"""
    path = sys.argv[0].split('://')[1].rstrip('/').split('/')[1:] # cuts out addon id
    query_list = sys.argv[2].lstrip('?').split('&&' if doublequerysplit else '&')
    query = {}
    if query_list and query_list[0]:
        for item in query_list:
            key, value = item.split("=")
            if key in query:
                if isinstance(query[key], list):
                    query[key].append(value)
                else:
                    query[key] = [query[key], value]
            else:
                query[key] = value

    return {'handle': int(sys.argv[1]), 'path': path, 'query': query}

def build_list(items, handle):
    """Pack up a list of image URLs into the plugin list"""
    xbmcplugin.setContent(handle, 'files')
    xbmcplugin.addDirectoryItems(handle, [(item, xbmcgui.ListItem(item)) for item in items])
    xbmcplugin.endOfDirectory(handle)

def unquoteimage(imagestring):
    if imagestring.startswith('image://'):
        return urllib.unquote(imagestring[8:-1])
    else:
        return imagestring
