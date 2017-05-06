from dateutil import parser
from datetime import datetime
from pytz import timezone
import os
import json
import requests
import pytz
import time

class ClanBot(object):
    """
    Clan bot!
    """

    def __init__(self):
        self.api_key = str(os.environ['BUNGIE_API_KEY'])
        self.session = requests.Session()
        self.session.headers['X-API-Key'] = self.api_key  
        self.user_base_uri = 'https://www.bungie.net/Platform/User/'
        self.destiny_base_uri = 'https://www.bungie.net/Platform/Destiny/'
        self.group_base_uri = 'https://www.bungie.net/Platform/Group/'
        self.clan_dict = {'Members':{}}
        self.clan_id = '548440' #http://bungienetplatform.wikia.com/wiki/GroupSearch
        self.clan_members = []
        self.est = timezone('US/Eastern')
        self.GAMERTAG = 'Ethernic'
        self.gamertag = None
        self.last_played = None
        self.last_played_days = None
        self.member_since = None
        self.member_since_days = None
        self.membership_id = None 
        self.membership_type = '2' # -1=both, 1=xbox, 2=psn
        self.destiny_membership_id = None
        self.destiny_account_summary = None
        self.timefmt = '%Y-%m-%d %H:%M:%S %Z'

    def RateLimited(maxPerSecond):
        minInterval = 1.0 / float(maxPerSecond)
        def decorate(func):
            lastTimeCalled = [0.0]
            def rateLimitedFunction(*args,**kargs):
                elapsed = time.clock() - lastTimeCalled[0]
                leftToWait = minInterval - elapsed
                if leftToWait>0:
                    time.sleep(leftToWait)
                ret = func(*args,**kargs)
                lastTimeCalled[0] = time.clock()
                return ret
            return rateLimitedFunction
        return decorate
    
    def display_stats(self):
        play_date = None
        member_date = None
        if not self.clan_dict['Members']:
            play_date = parser.parse(self.last_played).astimezone(self.est).strftime(self.timefmt)
            self.last_played_days = str(self.date_math(parser.parse(self.last_played)))
            #print '{0}'.format(self.gamertag)
            #print 'Last played: {0} days ({1})'.format(self.last_played_days, play_date)
        else:
            for key in self.clan_dict['Members'].keys():
                if self.gamertag in key.lower():
                    self.gamertag = key
            self.member_since = self.clan_dict['Members'][self.gamertag]['approvalDate']
            self.last_played = self.clan_dict['Members'][self.gamertag]['lastPlayed']
            member_date = parser.parse(self.member_since).astimezone(self.est).strftime(self.timefmt)
            play_date = parser.parse(self.last_played).astimezone(self.est).strftime(self.timefmt)
            self.member_since_days = str(self.date_math(parser.parse(self.member_since)))
            self.last_played_days = str(self.date_math(parser.parse(self.last_played)))

        print '{0}'.format(self.gamertag)
        if self.clan_dict['Members']:
            print 'Member since: {0} days ({1})'.format(self.member_since_days, member_date)
        print 'Last played: {0} days ({1})'.format(self.last_played_days, play_date) 
    
    def get_clan_id(self):
        i = 0
        full_uri = self.user_base_uri + 'GetBungieAccount/' + self.destiny_membership_id + '/' + self.membership_type + '/'
        details = self.get_request(full_uri)
        if len(details['Response']['clans']) > 1:
            while i < len(details['Response']['clans']):
                if details['Response']['clans'][i]['platformType'] == 2:
                    self.clan_id = str(details['Response']['clans'][i]['groupId'])
                    break
                else:
                    i += 1
        else:
            self.clan_id = str(details['Response']['clans'][i]['groupId'])

    def get_clan_members(self):
        current_page = 1
        has_more = True
        while has_more:
            full_uri = self.group_base_uri + self.clan_id + '/MembersV3/?currentPage='
            paged_members = self.get_request(full_uri+str(current_page))
            self.clan_members.extend(paged_members['Response']['results'])
            current_page += 1
            has_more = paged_members['Response']['hasMore']
        i = 0
        while i < len(self.clan_members):
            GAMERTAG = str(self.clan_members[i]['user']['psnDisplayName'])
            try:
                self.clan_dict['Members'][GAMERTAG]['approvalDate'] = self.clan_members[i]['approvalDate']
            except KeyError:
                self.clan_dict['Members'][GAMERTAG] = {'approvalDate': self.clan_members[i]['approvalDate']}
            self.clan_dict['Members'][GAMERTAG]['membershipId'] = self.clan_members[i]['membershipId']
            i += 1

    def date_math(self, older):
        now = datetime.now(pytz.utc)
        diff = now - older
        return diff.days

    def get_destiny_details(self, *GAMERTAG):
        i = 0
        if not GAMERTAG:
            PLAYER = self.gamertag
        else:
            PLAYER = GAMERTAG[0]
        full_uri = self.destiny_base_uri + 'SearchDestinyPlayer/-1/' + PLAYER
        details = self.get_request(full_uri)
        if len(details['Response']) > 1:
            while i < len(details['Response']):
                if details['Response'][i]['membershipType'] == int(self.membership_type):
                    self.destiny_membership_id = details['Response'][i]['membershipId']
                    break
                else:
                    i += 1
        else:
            self.destiny_membership_id = details['Response'][i]['membershipId']

    def get_last_played(self):
        i = 0
        date_list = []
        while i < len(self.destiny_account_summary['Response']['data']['characters']):
            date_list.append(self.destiny_account_summary['Response']['data']['characters'][i]['characterBase']['dateLastPlayed'])
            i += 1
        self.last_played = max(date_list)#parse(max(date_list)).astimezone(est)
        
    def get_destiny_account_summary(self, *DESTINYID):
        if not DESTINYID:
            MEMBERSHIPID = self.destiny_membership_id
        else:
            MEMBERSHIPID = DESTINYID
        full_uri = self.destiny_base_uri + self.membership_type + '/Account/' + MEMBERSHIPID + '/Summary/' 
        self.destiny_account_summary = self.get_request(full_uri)
        #print self.destiny_account_summary['ThrottleSeconds']

    @RateLimited(10)
    def get_request(self, full_uri):
        response = self.session.get(full_uri)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print "Problem retrieving: {0}".format(full_uri)
            exit(1)

    def initialize(self, *options):
        i = 0
        if options[0].file:
            with open(options[0].file, 'r') as f:
                self.clan_dict = json.load(f)
            f.close()
            if not options[0].gamertag:
                for key in self.clan_dict['Members'].keys():
                    self.gamertag = key
                    self.last_played = self.clan_dict['Members'][key]['lastPlayed']
                    self.display_stats()
        if options[0].update:
            self.get_clan_members()
            self.populate_stats()
        elif options[0].gamertag:
            while i < len(options[0].gamertag):
                self.gamertag=options[0].gamertag[i]
                if options[0].file:
                    self.display_stats()
                else:
                    self.get_stats()
                i += 1

    def populate_stats(self):
        for key in self.clan_dict['Members'].keys():
            self.get_destiny_details(key)
            self.clan_dict['Members'][key]['destinyMembershipId'] = self.destiny_membership_id
            self.get_destiny_account_summary()
            self.get_last_played()
            self.clan_dict['Members'][key]['lastPlayed'] = self.last_played
        with open('stats.json', 'w') as f:
            json.dump(self.clan_dict, f)
        f.close()

    def get_stats(self):
        self.get_destiny_details()
        self.get_destiny_account_summary()
        self.get_last_played()
        #self.display_stats()
        #self.get_clan_id()
        #print json.dumps(self.clan_dict, ensure_ascii=False)
        #print len(self.clan_dict['Members'])
        self.display_stats()