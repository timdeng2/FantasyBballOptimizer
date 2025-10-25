from .constant import NINE_CAT_STATS, POSITION_MAP, PRO_TEAM_MAP, STATS_MAP, STAT_ID_MAP
from espn_api.utils.utils import json_parsing
from datetime import datetime
from functools import cached_property

class Player(object):
    '''Player are part of team'''
    def __init__(self, data, year, pro_team_schedule = None, news = None):
        self.name = json_parsing(data, 'fullName')
        # if self.name == "Bam Adebayo":
        #     print(data)
        self.playerId = json_parsing(data, 'id')
        self.year = year

        self.position = POSITION_MAP[json_parsing(data, 'defaultPositionId') - 1]
        self.lineupSlot = POSITION_MAP.get(data.get('lineupSlotId'), '')
        self.eligibleSlots = [POSITION_MAP[pos] for pos in json_parsing(data, 'eligibleSlots') if pos < 5]
        self.acquisitionType = json_parsing(data, 'acquisitionType')
        self.proTeam = PRO_TEAM_MAP[json_parsing(data, 'proTeamId')]
        self.injuryStatus = json_parsing(data, 'injuryStatus')
        self.posRank = json_parsing(data, 'positionalRanking')
        self.stats = {}

        self.average_stats = {name: -1 for name in STATS_MAP.values() if name != ''}
        self.projected_stats = {name: -1 for name in STATS_MAP.values() if name != ''}
        self.last_7_stats = {name: -1 for name in STATS_MAP.values() if name != ''}
        self.last_15_stats = {name: -1 for name in STATS_MAP.values() if name != ''}
        self.last_30_stats = {name: -1 for name in STATS_MAP.values() if name != ''}

        self.nine_cat_averages = {name : 0 for name in NINE_CAT_STATS}
        self.nine_cat_projected = {name : 0 for name in NINE_CAT_STATS}
        self.nine_cat_last_7 = {name : 0 for name in NINE_CAT_STATS}
        self.nine_cat_last_15 = {name : 0 for name in NINE_CAT_STATS}
        self.nine_cat_last_30 = {name : 0 for name in NINE_CAT_STATS}

        self.schedule = {}
        self.news = {}
        expected_return_date = json_parsing(data, 'expectedReturnDate')
        self.expected_return_date = datetime(*expected_return_date).date() if expected_return_date else None

        if pro_team_schedule:
            pro_team_id = json_parsing(data, 'proTeamId')
            pro_team = pro_team_schedule.get(pro_team_id, {})
            for key in pro_team:
                game = pro_team[key][0]
                team = game['awayProTeamId'] if game['awayProTeamId'] != pro_team_id else game['homeProTeamId']
                self.schedule[key] = { 'team': PRO_TEAM_MAP[team], 'date': datetime.fromtimestamp(game['date']/1000.0) }

        if news:
            news_feed = news.get("news", {}).get("feed", [])
            self.news = [
                {
                    "published": item.get("published", ""),
                    "headline": item.get("headline", ""),
                    "story": item.get("story", "")
                }
                for item in news_feed
            ]

        # add available stats

        player = data['playerPoolEntry']['player'] if 'playerPoolEntry' in data else data['player']
        self.injuryStatus = player.get('injuryStatus', self.injuryStatus)
        self.injured = player.get('injured', False)

        # print(player.get('stats', []))
        for split in  player.get('stats', []):
            # computes average stats for previous season
            if split['seasonId'] == year - 1:
                if split['id'] == f'00{year - 1}' and split.get('averageStats'):
                    self.average_stats = {
                            name: split['averageStats'].get(stat_id, -1)
                            for stat_id, name in STATS_MAP.items()
                            if name != ''
                        }
            # computes projected stats for current season
            if split['seasonId'] == year:
                id = self._stat_id_pretty(split['id'], split['scoringPeriodId'])
                if id == f'{year}_projected' and split.get('averageStats'):
                    self.projected_stats = {
                            name: split['averageStats'].get(stat_id, -1)
                            for stat_id, name in STATS_MAP.items()
                            if name != ''
                        }
                elif id == f'{year}_last_15' and split.get('averageStats'):
                    self.last_15_stats = {
                            name: split['averageStats'].get(stat_id, -1)
                            for stat_id, name in STATS_MAP.items()
                            if name != ''
                        }
                elif id == f'{year}_last_7' and split.get('averageStats'):
                    self.last_7_stats = {
                            name: split['averageStats'].get(stat_id, -1)
                            for stat_id, name in STATS_MAP.items()
                            if name != ''
                        }
                elif id == f'{year}_last_30' and split.get('averageStats'):
                    self.last_30_stats = {
                            name: split['averageStats'].get(stat_id, -1)
                            for stat_id, name in STATS_MAP.items()
                            if name != ''
                        }
                

                # # Data field empty at start of season? Check back later
                # applied_total = split.get('appliedTotal', 0)
                # applied_avg =  round(split.get('appliedAverage', 0), 2)
                # game = self.schedule.get(id, {})

                # self.stats[id] = dict(applied_total=applied_total, applied_avg=applied_avg, team=game.get('team', None), date=game.get('date', None))
                # if split.get('stats'):
                #     if 'averageStats' in split.keys():
                #         self.stats[id]['avg'] = {STATS_MAP.get(i, i): split['averageStats'][i] for i in split['averageStats'].keys() if STATS_MAP.get(i) != ''}
                #         self.stats[id]['total'] = {STATS_MAP.get(i, i): split['stats'][i] for i in split['stats'].keys() if STATS_MAP.get(i) != ''}
                #     else:
                #         self.stats[id]['avg'] = None
                #         self.stats[id]['total'] = {STATS_MAP.get(i, i): split['stats'][i] for i in split['stats'].keys() if STATS_MAP.get(i) != ''}
        self.total_points = self.stats.get(f'{year}_total', {}).get('applied_total', 0)
        self.avg_points = self.stats.get(f'{year}_total', {}).get('applied_avg', 0)
        self.projected_total_points= self.stats.get(f'{year}_projected', {}).get('applied_total', 0)
        self.projected_avg_points = self.stats.get(f'{year}_projected', {}).get('applied_avg', 0)

        sources0 = [
            self.projected_stats,
            self.average_stats,
            self.last_7_stats,
            self.last_15_stats,
            self.last_30_stats
        ]
        sources1 = [
            self.average_stats,
            self.projected_stats,
            self.last_7_stats,
            self.last_15_stats,
            self.last_30_stats
        ]
        sources2 = [
            self.last_7_stats,
            self.projected_stats,
            self.last_15_stats,
            self.last_30_stats,
            self.average_stats,
        ]
        sources3 = [
            self.last_15_stats,
            self.last_7_stats,
            self.projected_stats,
            self.last_30_stats,
            self.average_stats,
        ]  
        sources4 = [
            self.last_30_stats,
            self.last_15_stats,
            self.last_7_stats,
            self.projected_stats,
            self.average_stats,
        ] 

        self.nine_cat_projected = self.combined_helper(sources0)
        self.nine_cat_averages = self.combined_helper(sources1)
        self.nine_cat_last_7 = self.combined_helper(sources2)
        self.nine_cat_last_15 = self.combined_helper(sources3)
        self.nine_cat_last_30 = self.combined_helper(sources4)

    
    def combined_helper(self, sources):
        combined = {name: -1 for name in NINE_CAT_STATS}
        for stats_dict in sources:
            for stat_name, value in stats_dict.items():
                if stat_name in combined.keys() and combined[stat_name] == -1 and value != -1:
                    combined[stat_name] = value
        
        #ensure none of them is still -1
        for k, v in combined.items():
            if v == -1:
                combined[k] = 0.0
        assert len(combined) == 11
        return combined

    def __repr__(self):
        return f'Player({self.name})'

    def _stat_id_pretty(self, id: str, scoring_period):
        id_type = STAT_ID_MAP.get(id[:2])
        return f'{id[2:]}_{id_type}' if id_type else str(scoring_period)

    @cached_property
    def nine_cat_averages(self):
        return {
            k: round(v, (3 if k in {'FG%', 'FT%'} else 1))
            for k, v in self.stats.get(f'{self.year}_total', {}).get("avg", {}).items()
            if k in NINE_CAT_STATS
        }
