from clanbot import ClanBot
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument('-c', '--clan',
                        action='store',
                        type=str,
                        dest='clan',
                        help='specify clan in quotes')
    parser.add_argument('-f', '--file',
                        action='store',
                        type=str,
                        dest='file',
                        help='stats file to parse')
    parser.add_argument('-l', '--live',
                        action='store_true',
                        dest='live',
                        help='get live stats for last played')
    parser.add_argument('-u', '--update',
                        action='store_true',
                        dest='update',
                        help='update stats.json with fresh data, will take a while')
    parser.add_argument('gamertag',
                        nargs=argparse.REMAINDER,
                        help='your subject\'s gamertag')
    options = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)
    else:
        ClanBot().initialize(options)

if __name__ == "__main__":
    main()