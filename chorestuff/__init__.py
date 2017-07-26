from .common import *
from .sql import *
from .texport import *


parser = argparse.ArgumentParser(description='Chores tracker and bill generator.')

"""
parser.add_argument('--db-file', '-db', action='store', type=str, default='videos.db', help='Path to DB file. (default: videos.db)')
parser.add_argument('--time-window', '-t', action='store', type=int, default=48, help='Time window to download subscriptions in hours. Zero means everything. (default: 48)')
parser.add_argument('--verbose', '-v', action='count', help='Verbosity of the output.')

parser.add_argument('files', action='store', nargs='*', type=str, default='', help='Links for standalone video download.')

parser.add_argument('--force', action='store_true', help='Force download of videos and metadata.')
parser.add_argument('--no-update-subscriptions', action='store_false', help='Do not update channel subscriptions.')
parser.add_argument('--no-extra-information', action='store_false', help='Do not download metadata.')
parser.add_argument('--no-download', action='store_false', help='Do not download pending videos.')
parser.add_argument('--no-update-videos', action='store_false', help='Do not check for newly uploaded videos.')
"""

