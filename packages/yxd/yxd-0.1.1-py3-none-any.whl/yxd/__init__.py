import argparse
import os
from .arch import checker, Arch
from .arguments import Arguments
from .downloader import Downloader
from .settings import Settings
from .youtube import api
from pathlib import Path
from requests.exceptions import RequestException


'''
Most of CLI modules refer to
Petter Kraabøl's Twitch-Chat-Downloader
https://github.com/PetterKraabol/Twitch-Chat-Downloader
(MIT License)

'''
__copyright__ = 'Copyright (C) 2020 vb'
__version__ = '0.1.1'
__license__ = 'AGPLv3'
__author__ = 'vb'
__author_email__ = 'vb4256874@noreply.github.com'
__url__ = "https://github.com/vb4256874/yxd"


def main():
    parser = argparse.ArgumentParser(description=f'yxd {__version__}')
    parser.add_argument('-v', f'--{Arguments.Name.VIDEO}', type=str,
                        help='Video ID (or URL that includes Video ID).'
                        'You can specify multiple video IDs by '
                        'separating them with commas without spaces.\n'
                        'If ID starts with a hyphen (-), enclose the ID in square brackets.')
    parser.add_argument('-c', f'--{Arguments.Name.CHANNEL}', type=str,
                        help='Channel ID (or URL of channel page)')
    parser.add_argument(f'--{Arguments.Name.FIRST}', type=int,
                        default=5, help='Download transcript from the last n VODs')
    parser.add_argument(f'--{Arguments.Name.API_KEY.replace("_", "-")}', type=str, help='YouTube API key')
    parser.add_argument('-o', f'--{Arguments.Name.OUTPUT}', type=str,
                        help='Output directory (end with "/"). default="./"', default='./')
    parser.add_argument('-e', f'--{Arguments.Name.SAVE_ERROR_DATA}', action='store_true',
                        help='Save error data when error occurs(".dat" file)')
    parser.add_argument(f'--{Arguments.Name.VERSION}', action='store_true',
                        help='Show version')
    parser.add_argument('-s', f'--{Arguments.Name.SKIP_DUPLICATE}', action='store_true',
                        help='Skip already extracted videos.This option is valid when `-o` option is specified.')
    parser.add_argument(f'--{Arguments.Name.SETTINGS}', action='store_true', help='Print settings file location')
    parser.add_argument(f'--{Arguments.Name.SETTINGS_FILE.replace("_", "-")}', type=str,
                        # default=str(Path.home()) + '/.config/yxd/settings.json',
                        default=str(Path.home()) + '/.config/yxd/settings.json',
                        help='Use a custom settings file')
    parser.add_argument(f'--{Arguments.Name.LOG}', action='store_true', help='Save log file')
    Arguments(parser.parse_args().__dict__)

    if checker.is_pythonista_2() or checker.is_pythonista_3():
        arch = Arch.IOS
        print("DETECTED PYTHONISTA,\n BUT IT IS NOT IMPLEMENTED NOW.\nPlease looking forward to implementing it...")
        exit(0)
    else:
        arch = Arch.STANDARD
    arch = Arch.STANDARD
    Settings(Arguments().settings_file,
             reference_filepath=f'{os.path.dirname(os.path.abspath(__file__))}/settings.reference.json.py', arch=arch)

    if not Settings().config.get('EULA', None) or not Settings().config.get('EULA', None) == 'agreed':
        print()
        print("!!CAUTION!!\n"
        "The use of this tool is at your own risk.\n"
        "The author of this program is not responsible for any damage \n"
        "caused by this tool or bugs or specifications\n"
        "or other incidental actions.\n"
        f"You will be deemed to have agreed to the items listed in the LICENSE.\n"
        "Type `yes` if you agree with the above.\n")
        while True:
            ans = input()
            if ans == 'yes':
                Settings().config['EULA'] = "agreed"
                Settings().save()
                break
            elif ans == "":
                continue
            else:
                return

    # Print version
    if Arguments().print_version:
        print(f'v{__version__}')
        return

    if Arguments().api_key or Settings().config.get('api_key', None):
        Settings().config['api_key'] = Arguments().api_key or Settings().config['api_key']
    else:
        for i in range(3):
            typed_apikey = input('Enter YouTube API key: ').strip()
            if api.check_validation(typed_apikey):
                print("Confirmed the entered YouTube API key.")
                Settings().config['api_key'] = typed_apikey
                Settings().save()
                break
            print("The entered API key is NOT valid or exceeds quota limit. Please try again or enter other key.")
            print(f"--number of attempts:{3-i-1} remaining--")
            print()
        else:
            print("Unable to determine the valid YouTube API key, or you have exceeded the available quota.")
            print("(CANNOT support any inquiries about the YouTube API.)")
            return


    # Scan folder
    dir_videos = set()
    if Arguments().output:
        path = Arguments().output
    else:
        path = "./"
    if not os.path.exists(path):
        print(f"Directory not found:{path}")
        return
    if Arguments().skip_duplicate:
        print("Scanning output dirctory...")
        dir_videos.update([f[:11] for f in os.listdir(
            path) if os.path.isfile(os.path.join(path, f))])

    # Extract
    if Arguments().video_ids or Arguments().channels:
        try:
            if Arguments().video_ids:
                Downloader(dir_videos).videos(Arguments().video_ids)

            if Arguments().channels:
                Downloader(dir_videos).channels(Arguments().channels)

            return
        except KeyboardInterrupt:
            print('Cancelled')
            return
        except RequestException as e:
            print("Network Error has occured:",e)
            print()
            return
    parser.print_help()
