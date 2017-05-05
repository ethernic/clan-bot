from dateutil.parser import parse
from pytz import timezone
import os
import json
import requests

class ClanBot(object):
    """
    Clan bot!
    """

    def __init__(self):
        self.api_key = str(os.environ["BUNGIE_API_KEY"])
        self.session = requests.Session()
        self.session.headers["X-API-Key"] = self.api_key
        
        self.user_base_uri = "https://www.bungie.net/Platform/User/"
        self.destiny_base_uri = "https://www.bungie.net/Platform/Destiny"
        self.GAMERTAG = "Ethernic"
        self.gamertag = None
        self.last_played = None
        self.membership_id = None 
        self.membership_type = '2'
        self.destiny_membership_id = None
        self.destiny_account_summary = None
        self.timefmt = '%Y-%m-%d %H:%M:%S %Z'
        
    def display_stats(self):
        print "{0}".format(self.gamertag)
        print "Last played: {0}".format(self.last_played.strftime(self.timefmt))

    def get_membership_id(self):    
        full_uri = self.user_base_uri + 'SearchUsers/?q=' + self.gamertag
        parsed = self.get_request(full_uri)
        self.membership_id = parsed['Response'][0]['membershipId']
    
    def get_destiny_membership_id(self):
        full_uri = self.user_base_uri + 'GetBungieAccount/' + self.membership_id + '/254/'
        i = 0
        parsed = self.get_request(full_uri)
        while i < len(parsed['Response']['destinyAccounts']):
            if parsed['Response']['destinyAccounts'][i]['userInfo']['membershipType'] == int(self.membership_type):
                self.destiny_membership_id = parsed['Response']['destinyAccounts'][i]['userInfo']['membershipId']
                break
            else:
                i += 1
        #self.destiny_membership_id = parsed['Response']['destinyAccounts'][0]['userInfo']['membershipId']

    def get_last_played(self):
        i = 0
        date_list = []
        est = timezone('US/Eastern')
        while i < len(self.destiny_account_summary['Response']['data']['characters']):
            date_list.append(self.destiny_account_summary['Response']['data']['characters'][i]['characterBase']['dateLastPlayed'])
            i += 1
        self.last_played = parse(max(date_list)).astimezone(est)
        
    def get_destiny_account_summary(self):
        full_uri = self.destiny_base_uri + '/' + self.membership_type + '/Account/' + self.destiny_membership_id + '/Summary/' 
        self.destiny_account_summary = self.get_request(full_uri)

    def get_request(self, full_uri):
        response = self.session.get(full_uri)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print "Problem retrieving: {0}".format(full_uri)
            exit(1)

    def initialize(self, gamertag):
        i = 0
        while i < len(gamertag):
            self.gamertag = gamertag[i]
            self.get_stats()
            i += 1

    def get_stats(self):
        self.get_membership_id()
        self.get_destiny_membership_id()
        self.get_destiny_account_summary()
        self.get_last_played()
        self.display_stats()