"""
Python wrapper for the Undocumented NHL API by jayblackedout
"""

import requests
from datetime import datetime as dt, timedelta

BASE = "https://statsapi.web.nhl.com/api/v1/"


class Schedule:
    """
    Representation of the NHL API Schedule dataset

    ...

    Attributes
    ----------
    team_id : int
        The Team ID of the defined team

    Methods
    -------
    game_info()
        Parses the json data and returns a dict of game info
    datetime_info()
        Parses the json data and returns a dict of date and UTC time info
    """

    def __init__(self, team_id):
        """Returns the json data of the defined team's next scheduled game"""
        endpoint = f"teams/{team_id}?expand=team.schedule.next"
        url = BASE + endpoint
        self.response = requests.get(url)
        self.data = self.response.json()

    def game_info(self):
        """Parses the json data and returns a dict of game info"""
        response = self.response
        data = self.data
        if response.status_code == requests.codes.ok:
            try:
                next_game = data["teams"][0]["nextGameSchedule"]
                games = next_game["dates"][0]["games"][0]
                game_id = games["gamePk"]
                live_feed = games["link"]
                game_state = games["status"]["detailedState"]
                away_id = games["teams"]["away"]["team"]["id"]
                home_id = games["teams"]["home"]["team"]["id"]
                away_name = games["teams"]["away"]["team"]["name"]
                home_name = games["teams"]["home"]["team"]["name"]
                output = {
                    "game_id": game_id,
                    "live_feed": live_feed,
                    "game_state": game_state,
                    "away_id": away_id,
                    "home_id": home_id,
                    "away_name": away_name,
                    "home_name": home_name,
                }
            except KeyError:
                output = {"game_state": "No Game Scheduled"}
            return output

    def datetime_info(self):
        """Parses the json data and returns a dict of date and UTC time info"""
        response = self.response
        data = self.data
        try:
            games = \
                data["teams"][0]["nextGameSchedule"]["dates"][0]["games"][0]
            x = games["gameDate"]
            next_game_date = \
                dt.strptime(x, "%Y-%m-%dT%H:%M:%SZ").strftime("%B %d, %Y")
            next_game_time = \
                dt.strptime(x, "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M")
            next_game_datetime = x
            output = {
                "next_game_date": next_game_date,
                "next_game_time": next_game_time,
                "next_game_datetime": next_game_datetime,
            }
        except KeyError:
            output = {"next_game_datetime": "None"}
        return output


class Scoring:
    """
    Representation of the NHL API Scoring dataset

    ...

    Attributes
    ----------
    team_id : int
        The Team ID of the defined team

    Methods
    -------
    scoring_info()
        Parses the json data and returns a dict of scoring info
    """

    def __init__(self, team_id):
        """Returns the json data of the defined team's last/current game"""
        endpoint = f"schedule?teamId={team_id}&hydrate=scoringplays"
        url = BASE + endpoint
        self.response = requests.get(url)
        self.data = self.response.json()

    def scoring_info(self):
        """Parses the json data and returns a dict of scoring info"""
        response = self.response
        data = self.data
        if response.status_code == requests.codes.ok:
            if data["totalItems"] == 1:
                games = data["dates"][0]["games"][0]
                game_state = games["status"]["detailedState"]
                away = games["teams"]["away"]["team"]
                home = games["teams"]["home"]["team"]
                away_id = away["id"]
                home_id = home["id"]
                away_name = away["name"]
                home_name = home["name"]
                away_score = games["teams"]["away"]["score"]
                home_score = games["teams"]["home"]["score"]
                plays = games["scoringPlays"]
                if plays != []:
                    last_goal = plays[-1]["result"]["description"]
                    goal_type = plays[-1]["result"]["strength"]["code"]
                    goal_event_id = plays[-1]["about"]["eventId"]
                    goal_team_id = plays[-1]["team"]["id"]
                    goal_team_name = plays[-1]["team"]["name"]
                    output = {
                        "game_state": game_state,
                        "last_goal": last_goal,
                        "goal_type": goal_type,
                        "goal_team_id": goal_team_id,
                        "goal_event_id": goal_event_id,
                        "goal_team_name": goal_team_name,
                        "away_id": away_id,
                        "home_id": home_id,
                        "away_name": away_name,
                        "home_name": home_name,
                        "away_score": away_score,
                        "home_score": home_score,
                    }
                else:
                    output = {
                        "game_state": game_state,
                        "away_id": away_id,
                        "home_id": home_id,
                        "away_name": away_name,
                        "home_name": home_name,
                        "away_score": away_score,
                        "home_score": home_score,
                    }
                return output
            else:
                return


class Live:
    """
    Representation of the NHL API Live dataset

    ...

    Attributes
    ----------
    game_id : int
        The Game ID of the defined game

    Methods
    -------
    live_info()
        Parses the json data and returns a dict of play/event info
    """

    def __init__(self, game_id):
        """Returns the json data of the defined team's live game"""
        endpoint = f"game/{game_id}/feed/live"
        url = BASE + endpoint
        self.response = requests.get(url)
        self.data = self.response.json()

    def live_info(self):
        """Parses the json data and returns a dict of play/event info"""
        response = self.response
        data = self.data
        if response.status_code == requests.codes.ok:
            plays = data["liveData"]["plays"]
            if plays["allPlays"] != []:
                teams = data["gameData"]["teams"]
                away_id = teams["away"]["id"]
                home_id = teams["home"]["id"]
                away_abbr = teams["away"]["abbreviation"]
                home_abbr = teams["home"]["abbreviation"]
                last_event = plays["allPlays"][-1]["result"]["event"]
                last_desc = plays["allPlays"][-1]["result"]["description"]
                output = {
                    "away_id": away_id,
                    "home_id": home_id,
                    "away_abbr": away_abbr,
                    "home_abbr": home_abbr,
                    "last_event": last_event,
                    "last_desc": last_desc,
                }
                return output
            else:
                return


class Linescore:
    """
    Representation of the NHL API Linescore dataset

    ...

    Attributes
    ----------
    team_id : int
        The Team ID of the defined team

    Methods
    -------
    linescore_info()
        Parses the json data and returns a dict of linescore info
    """

    def __init__(self, team_id):
        """Returns the json data of the defined team's last/current game"""
        endpoint = \
            f"schedule?teamId={team_id}&expand=schedule.linescore"
        url = BASE + endpoint
        self.response = requests.get(url)
        self.data = self.response.json()

    def linescore_info(self):
        """Parses the json data and returns a dict of linescore info"""
        response = self.response
        data = self.data
        if response.status_code == requests.codes.ok:
            if data["totalItems"] == 1:
                try:
                    linescore = data["dates"][0]["games"][0]["linescore"]
                    current_period = linescore["currentPeriodOrdinal"]
                    time_remaining = linescore["currentPeriodTimeRemaining"]
                    away = linescore["teams"]["away"]
                    home = linescore["teams"]["home"]
                    away_id = away["team"]["id"]
                    home_id = home["team"]["id"]
                    away_name = away["team"]["name"]
                    home_name = home["team"]["name"]
                    away_sog = away["shotsOnGoal"]
                    home_sog = home["shotsOnGoal"]
                    output = {
                        "current_period": current_period,
                        "time_remaining": time_remaining,
                        "away_id": away_id,
                        "home_id": home_id,
                        "away_name": away_name,
                        "home_name": home_name,
                        "away_sog": away_sog,
                        "home_sog": home_sog,
                    }
                except KeyError:
                    output = None
                return output
            else:
                return


class Broadcasts:
    """
    Representation of the NHL API Broadcast dataset

    ...

    Attributes
    ----------
    team_id : int
        The Team ID of the defined team

    Methods
    -------
    broadcast_info()
        Parses the json data and returns a dict of broadcast info
    """

    def __init__(self, team_id):
        """Returns the json data of the defined team's last/current game"""
        endpoint = f"teams/{team_id}?expand=team.schedule.next&" + \
            "expand=schedule.broadcasts.all"
        url = BASE + endpoint
        self.response = requests.get(url)
        self.data = self.response.json()

    def broadcast_info(self):
        """Parses the json data and returns a dict of broadcast info"""
        response = self.response
        data = self.data
        if response.status_code == requests.codes.ok:
            try:
                dates = data["teams"][0]["nextGameSchedule"]["dates"][0]
                info = dates["games"][0]["broadcasts"]
                nat = [x["name"] for x in info if x["type"] == "national"]
                away = [x["name"] for x in info if x["type"] == "away"]
                home = [x["name"] for x in info if x["type"] == "home"]
                output = {
                    "national_broadcasts": nat,
                    "away_broadcasts": away,
                    "home_broadcasts": home,
                }
            except KeyError:
                print("Keyerror")
                output = None
            return output
