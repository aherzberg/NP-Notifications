id_to_color = {0: "blue circle",
               1: "teal circle",
               2: "green circle",
               3: "yellow circle",
               4: "orange circle",
               5: "red circle",
               6: "pink circle",
               7: "purple circle",
               8: "blue square",
               9: "teal square"
               # TODO: add more colors
               }


def combat_calculate(defender_str, defender_wpn, attacker_str, attacker_wpn):
    # Default to Defenders because a ship with 1 army will show as 0 armies
    winner = "Defenders"
    while defender_str > 0 and attacker_str > 0:
        attacker_str -= defender_wpn + 1
        if attacker_str <= 0:
            winner = "Defenders"
            break
        defender_str -= attacker_wpn
        if defender_str <= 0:
            winner = "Attackers"
            break

    return winner


def get_player_stars(player_id):
    players_stars = []
    for star in Star.list:
        if star.owner == player_id:
            players_stars.append(star)
    return players_stars


def get_player_carriers(player_id):
    players_carriers = []
    for carrier in Carrier.list:
        if carrier.owner == player_id:
            players_carriers.append(carrier)
    return players_carriers


def hostile_carriers_incoming_to_star(star_id, player_id, players_to_ignore):
    hostile_carriers = []
    for carrier in Carrier.list:
        # if carrier owner is in players to ignore config list then don't continue
        if player_id_to_obj(carrier.owner).name not in players_to_ignore:
            # if carrier owner is not the player and is in transit
            if len(carrier.waypoints) > 0 and carrier.owner != player_id:
                # if carrier is coming to this star then add to hostile carriers list
                if carrier.waypoints[0].id == star_id:
                    hostile_carriers.append(carrier.id)

    return hostile_carriers


def star_id_to_object(id):
    for star in Star.list:
        if id == star.id:
            return star


def carrier_id_to_object(id):
    for carrier in Carrier.list:
        if id == carrier.id:
            return carrier


def player_id_to_obj(player_id):
    for player in Player.list:
        if str(player.id) == str(player_id):
            return player
    return "N/A"

class Carrier:
    list = []

    def __init__(self, id, name, strength, position, waypoints, owner):
        self.id = id
        self.strength = strength
        self.position = position
        self.waypoints = waypoints
        self.name = name
        self.owner = owner
        Carrier.list.append(self)

    def print(self):
        print("---------------")
        print("id:" + str(self.id))
        print("name:" + str(self.name))
        print("strength:" + str(self.strength))
        print("position:" + str(self.position))
        for waypoint in self.waypoints:
            print("waypoints:" + str(waypoint.name) + ", ")
        print("owner:" + str(self.owner))


class Star:
    list = []

    def __init__(self,id,name,strength,owner):
        self.id = id
        self.name = name
        self.strength = strength
        self.owner = owner
        Star.list.append(self)

    def print(self):
        print("---------------")
        print("id:" + str(self.id))
        print("name:" + str(self.name))
        print("strength:" + str(self.strength))
        print("owner:" + str(self.owner))


class Player:
    list = []

    def __init__(self, id, name, weapon_resh):
        self.id = id
        self.name = name
        self.weapon_resh = weapon_resh
        Player.list.append(self)

    def print(self):
        print("---------------")
        print("id:" + str(self.id))
        print("name:" + str(self.name))
