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
