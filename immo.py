from clanbot import ClanBot
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument('gamertag',
                        nargs=argparse.REMAINDER,
                        help='Your subject\'s gamertag')
    options = parser.parse_args()
    ClanBot().initialize(options.gamertag)

if __name__ == "__main__":
    main()