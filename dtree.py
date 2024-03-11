class Node(object):
    def __init__(self, matchup_acquisitions, value=0, teams=[]):
        self.matchup_acquisitions = matchup_acquisitions
        self.teams = teams
        self.value = value
        self.swap = [] #list of tree objects

    def add_swap_list(self, obj):
        self.swap.append(obj)

    def show(self):
        print(f"Matchup Acquistions Used: {self.matchup_acquisitions}")
        print(f"Teams: {self.teams}")
        if self.value == 1:
            print(f"Playing Today ({self.value})")
        else:
            print(f"Not Playing Today ({self.value})")
        print("List of Available Options:\n-------------------")
        for i in self.swap:
            print(list(i.teams))