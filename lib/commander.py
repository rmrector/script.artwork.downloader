import sys
import xbmc

from lib import common
from lib import upgrade
from lib.main import Main
from lib.utils import log

def handle_command():
    command = get_command()
    if 'mode' in command and command['mode'] == 'upgrade':
        if 'upgrade' in command and command['upgrade'] == 'classic_extrafanart_tolibrary':
            upgrade.classic_extrafanart_tolibrary()
    else:
        log('######## Artwork Downloader: Initializing...............................', xbmc.LOGNOTICE)
        log('## Add-on Name = %s' % str(common.__addonname__), xbmc.LOGNOTICE)
        log('## Version     = %s' % str(common.__version__), xbmc.LOGNOTICE)
        Main()
        log('script stopped', xbmc.LOGNOTICE)

def get_command():
    """Build a dictionary of all arguments. The arguements are split key, value on '=' with the keys lowercased to ease comparison. Arguments without '=' are just set to True with a lowercased key, but you can just check if it exists ('if <key> in command')."""
    command = {}
    for x in range(1, len(sys.argv)):
        arg = sys.argv[x].split("=")
        command[arg[0].strip().lower()] = arg[1].strip() if len(arg) > 1 else True

    return command
