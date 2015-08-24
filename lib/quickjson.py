import sys
import xbmc

if sys.version_info < (2, 7):
    import simplejson as json
else:
    import json

def get_movies():
    """Gets simple art data for all movies in the library."""
    json_request = get_baserequest('VideoLibrary.GetMovies')
    json_request['params']['properties'] = ['file', 'imdbnumber', 'art']
    json_request['params']['sort'] = {'method': 'label'}

    json_result = execute_jsonrpc(json_request)
    if _check_json_result(json_result, 'movies'):
        return json_result['result']['movies']
    else:
        return []

def get_tvshows():
    """Gets simple art data for all TV shows in the library."""
    json_request = get_baserequest('VideoLibrary.GetTVShows')
    json_request['params']['properties'] = ['file', 'imdbnumber', 'art']
    json_request['params']['sort'] = {'method': 'label'}

    json_result = execute_jsonrpc(json_request)
    if _check_json_result(json_result, 'tvshows'):
        return json_result['result']['tvshows']
    else:
        return []

def get_musicvideos():
    """Gets simple art data for all music videos in the library."""
    json_request = get_baserequest('VideoLibrary.GetMusicVideos')
    json_request['params']['properties'] = ['file', 'art']
    json_request['params']['sort'] = {'method': 'label'}

    json_result = execute_jsonrpc(json_request)
    if _check_json_result(json_result, 'musicvideos'):
        return json_result['result']['musicvideos']
    else:
        return []

def execute_jsonrpc(jsonrpc_command):
    if isinstance(jsonrpc_command, dict):
        jsonrpc_command = json.dumps(jsonrpc_command, ensure_ascii=False)
        if isinstance(jsonrpc_command, unicode):
            jsonrpc_command = jsonrpc_command.encode('utf-8')

    json_result = xbmc.executeJSONRPC(jsonrpc_command)
    return _json_to_str(json.loads(json_result))

def get_baserequest(jsonrpc_method):
    return {'jsonrpc': '2.0', 'method': jsonrpc_method, 'params': {}, 'id': 1}

def _check_json_result(json_result, result_key):
    return 'result' in json_result and result_key in json_result['result']

def _json_to_str(jsoninput):
    """Ensures all keys/values from a dict from json.load is happily encoded to the utf-8 strings that Kodi generally prefers."""
    if isinstance(jsoninput, dict):
        return {_json_to_str(key): _json_to_str(value) for key, value in jsoninput.iteritems()}
    elif isinstance(jsoninput, list):
        return [_json_to_str(item) for item in jsoninput]
    elif isinstance(jsoninput, unicode):
        return jsoninput.encode('utf-8')
    else:
        return jsoninput
