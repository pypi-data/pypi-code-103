import argparse
import pathlib
import json

from fad.scraper import Scraper
from fad.utils import get_default_config_path, get_downloads_dir

def start_downloader(config):
    scraper = Scraper(config)    
    scraper.login()
    anchors = scraper.get_anchors()
    scraper.download_photos(anchors)

def get_config_from_parser():
    parser = argparse.ArgumentParser(description='Download an album (users, pages or groups) from Facebook with Selenium')
    # add parser arguments
    parser.add_argument('-D', '--debug', dest='debug',
                        default=False, action='store_true',
                        help='Enable debug mode to see progress in Firefox browser')
    parser.add_argument('-C', '--config', dest='config',
                        type=pathlib.Path,
                        help='The path to your config file')
    parser.add_argument('-U', '--user', dest='user',
                        default=False, action='store_true',
                        help='The album is an user\'s photos album')
    parser.add_argument('-P', '--page', dest='page',
                        default=False, action='store_true',
                        help='The album is a page\'s photos album')
    parser.add_argument('-G', '--group', dest='group',
                        default=False, action='store_true',
                        help='The album is a group\'s photos album')
    parser.add_argument('-a', '--album', dest='album',
                        help='The full url of the facebook album, starting with "https://facebook.com/"')
    parser.add_argument('-d', '--dir', dest='dir',
                        default=get_downloads_dir(), type=pathlib.Path,
                        help='The directory where you want save your downloaded album')
    parser.add_argument('-n', '--name', dest='name',
                        help='The album\'s name, (also the name of subdirectory)')
    parser.add_argument('-e', '--email', dest='email',
                        help='Your facebook email to login')
    parser.add_argument('-p', '--passwd', dest='password',
                        help='Your facebook password to login')
    parser.add_argument('--timeout', dest='timeout', 
                        default=5, type=int,
                        help='The timeout for scrolling the end of the album (in seconds), default 5')
    parser.add_argument('--wait', dest='wait_timeout',
                        default=10, type=int,
                        help='The timeout for waiting an element that will attach on the DOM tree (in seconds), default 30')
    
    args = parser.parse_args()
    config = {}
    config_path = ''
    # read configurations a json file
    if args.config: # from an explicit path
        config_path = args.config
    elif not args.config and not args.user and not args.group and not args.page: # from default path ./config.json
        config_path = get_default_config_path()

    if config_path:
        with open(config_path) as f:
            config = json.load(f)
            f.close()
        return config

    # read configurations from arguments
    if not args.album:
        print('Album URL is missing')
        exit()

    if args.page:
        type = 'page'
    elif args.group:
        type = 'group'
    else: # default
        type = 'user'

    config =  {
        'debug': args.debug,
        'type': type,
        'album': args.album,
        'dir': args.dir,
        'name': args.name,
        'email': args.email,
        'password': args.password,
        'timeout': args.timeout,
        'wait_timeout': args.wait_timeout,
    }
    return config

def main() -> None:
    config = get_config_from_parser()
    # print(config)    
    start_downloader(config)

if __name__ == '__main__':
    main()
