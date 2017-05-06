from clanbot import ClanBot
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument('-f', '--file',
                        action='store',
                        type=str,
                        dest='file',
                        help='stats file to parse')
    parser.add_argument('-l', '--last-played',
                        action='store_true',
                        dest='last_played',
                        help='display last played time for player')
    parser.add_argument('-u', '--update',
                        action='store_true',
                        dest='update',
                        help='update stats.json with fresh data, will take a while')
    parser.add_argument('gamertag',
                        nargs=argparse.REMAINDER,
                        help='your subject\'s gamertag')
    options = parser.parse_args()
    if not options:
        ClanBot().initialize()
    else:
        ClanBot().initialize(options)

if __name__ == "__main__":
    main()