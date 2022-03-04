import time

import gamelib
import random
import math
import warnings
from sys import maxsize
import json

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""


class defStructure:
    def __init__(self, game_state):
        self.ds_op = []
        self.ds_t = []
        self.ds_w = []
        self.ds_s = []
        self.gs = game_state

    def add(self, op, turret_ls, wall_ls, support_ls):
        self.ds_op.append(op)
        self.ds_t.append(turret_ls)
        self.ds_w.append(wall_ls)
        self.ds_s.append(support_ls)

    def deploy(self):
        for op, turret_ls, wall_ls, support_ls in zip(self.ds_op, self.ds_t, self.ds_w, self.ds_s):
            if op == 'build':
                if len(turret_ls):
                    self.gs.attempt_spawn(TURRET, turret_ls)
                if len(wall_ls):
                    self.gs.attempt_spawn(WALL, wall_ls)
                if len(support_ls):
                    self.gs.attempt_spawn(SUPPORT, support_ls)
            else:
                if len(turret_ls):
                    self.gs.attempt_upgrade(turret_ls)
                if len(wall_ls):
                    self.gs.attempt_upgrade(wall_ls)
                if len(support_ls):
                    self.gs.attempt_upgrade(support_ls)


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0

        self.scored_on_locations = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        # game_state.attempt_spawn(DEMOLISHER, [24, 12], 2)

        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  # Comment or remove this line to enable warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    # 主要逻辑
    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """

        self.defend(game_state)
        self.attack(game_state)

        """
        
        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)


        # If the turn is less than 5, stall with interceptors and wait to see enemy's base
        if game_state.turn_number < 5:
            self.stall_with_interceptors(game_state)
        else:
            # Now let's analyze the enemy base to see where their defenses are concentrated.
            # If they have many units in the front we can build a line for our demolishers to attack them at long range.
            if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15]) > 10:
                self.demolisher_line_strategy(game_state)
            else:
                # They don't have many units in the front so lets figure out their least defended area and send Scouts there.

                # Only spawn Scouts every other turn
                # Sending more at once is better since attacks can only hit a single scout at a time
                if game_state.turn_number % 2 == 1:
                    # To simplify we will just check sending them from back left and right
                    scout_spawn_location_options = [[13, 0], [14, 0]]
                    best_location = self.least_damage_spawn_location(game_state, scout_spawn_location_options)
                    game_state.attempt_spawn(SCOUT, best_location, 1000)

                # Lastly, if we have spare SP, let's build some supports
                support_locations = [[13, 2], [14, 2], [13, 3], [14, 3]]
                game_state.attempt_spawn(SUPPORT, support_locations)
        """

    def defend(self, game_state):
        ds = defStructure(game_state)
        ds.add('build', [[2, 11], [25, 11]], [], [])
        ds.add('build', [[8, 9], [19, 9]], [], [])
        ds.add('build', [[12, 9], [15, 9]], [], [])
        ds.add('build', [[5, 9], [22, 9]], [], [])
        ds.add('build', [], [[0, 13], [1, 13], [2, 13]], [])
        ds.add('build', [], [[27, 13], [26, 13], [25, 13]], [])
        ds.add('build', [], [[1, 12], [26, 12]], [])
        ds.add('build', [], [[3, 12], [4, 11], [5, 10]], [])
        ds.add('build', [], [[24, 12], [23, 11], [22, 10]], [])

        ds.add('build', [],
               [[7, 10], [21, 10], [8, 10], [20, 10], [9, 10], [19, 10], [10, 10], [18, 10], [11, 10], [17, 10],
                [12, 10], [16, 10], [13, 10], [15, 10], [14, 10]], [])

        ds.add('upgrade', [[2, 11], [25, 11]], [], [])
        ds.add('upgrade', [[8, 9], [19, 9]], [], [])
        ds.add('build', [], [], [[8, 8], [8, 7]])

        ds.add('upgrade', [], [[0, 13], [1, 13], [2, 13]], [])
        ds.add('upgrade', [], [[27, 13], [26, 13], [25, 13]], [])
        ds.add('upgrade', [], [[1, 12], [26, 12]], [])
        ds.add('upgrade', [[12, 9], [15, 9]], [], [])
        ds.add('upgrade', [[5, 9], [22, 9]], [], [])
        ds.add('upgrade', [], [[3, 12], [4, 11], [5, 10]], [])
        ds.add('upgrade', [], [[24, 12], [23, 11], [22, 10]], [])

        ds.add('build', [[9, 9], [7, 8]], [], [])
        ds.add('build', [[11, 9], [7, 9]], [], [])

        ds.add('upgrade', [],
               [[7, 10], [21, 10], [8, 10], [20, 10], [9, 10], [19, 10], [10, 10], [18, 10], [11, 10], [17, 10],
                [12, 10], [16, 10], [13, 10], [15, 10], [14, 10]], [])
        ds.add('upgrade', [[9, 9], [7, 8]], [], [])
        ds.add('upgrade', [[11, 9], [7, 9]], [], [])

        ds.add('build', [[2, 12], [25, 12]], [], [])
        ds.add('build', [[3, 11], [24, 11]], [], [])
        ds.add('upgrade', [[2, 12], [25, 12]], [], [])
        ds.add('upgrade', [[3, 11], [24, 11]], [], [])

        ds.add('build', [], [], [[10, 5], [9, 6]])
        ds.add('build', [], [], [[11, 4], [12, 3]])
        ds.add('build', [], [], [[14, 2], [13, 2]])
        ds.add('build', [], [], [[13, 3], [12, 4]])
        ds.add('build', [], [], [[11, 5], [10, 6]])
        ds.add('build', [], [], [[9, 7]])

        ds.deploy()



    def attack(self, game_state):
        thres = max(game_state.turn_number // 8 + 5, 15)

        # 不够阈值，每轮两个破坏者伺候
        if game_state.turn_number % 3:
            if game_state.get_resource(MP) < thres:
                self.stall_with_demolisher(game_state, num=game_state.turn_number // 15 + 3)
            else:
                self.stall_with_scout(game_state)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place turrets that attack enemy units
        turret_locations = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(TURRET, turret_locations)

        # Place walls in front of turrets to soak up damage for them
        wall_locations = [[8, 12], [19, 12]]
        game_state.attempt_spawn(WALL, wall_locations)
        # upgrade walls so they soak more damage
        game_state.attempt_upgrade(wall_locations)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build turret one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1] + 1]
            game_state.attempt_spawn(TURRET, build_location)

    def stall_with_scout(self, game_state):
        """
        只放置士兵在[11, 2] ][16, 2]
        选择一个点进行放置
        """
        scout_spawn_location_options = [[11, 2], [16, 2]]
        best_location = self.least_damage_spawn_location(game_state, scout_spawn_location_options)

        while game_state.get_resource(MP) >= game_state.type_cost(SCOUT)[MP] and len(best_location) > 0:
            game_state.attempt_spawn(SCOUT, scout_spawn_location_options)

        # 随机放置

        # friendly_edges = game_state.game_map.get_edge_locations(
        #     game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        #
        # deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        #
        # while game_state.get_resource(MP) >= game_state.type_cost(SCOUT)[MP] and len(deploy_locations) > 0:
        #     deploy_index = random.randint(0, len(deploy_locations) - 1)
        #     deploy_location = deploy_locations[deploy_index]
        #     game_state.attempt_spawn(SCOUT, deploy_location)

    def stall_with_demolisher(self, game_state, num):
        """
        只放置破坏者在[11, 2] ][16, 2]
        选择一个点进行放置
        """
        scout_spawn_location_options = [[11, 2], [16, 2]]
        best_location = self.least_damage_spawn_location(game_state, scout_spawn_location_options)

        while game_state.get_resource(MP) >= game_state.type_cost(DEMOLISHER)[MP] and len(
                best_location) > 0 and num > 0:
            game_state.attempt_spawn(DEMOLISHER, best_location)
            num -= 1

        # 随机放置

        # friendly_edges = game_state.game_map.get_edge_locations(
        #     game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        #
        # deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        #
        # while game_state.get_resource(MP) >= game_state.type_cost(DEMOLISHER)[MP] and len(
        #         deploy_locations) > 0 and num > 0:
        #     deploy_index = random.randint(0, len(deploy_locations) - 1)
        #     deploy_location = deploy_locations[deploy_index]
        #     game_state.attempt_spawn(DEMOLISHER, deploy_location)
        #     num -= 1

    def stall_with_interceptors(self, game_state):
        """
        Send out interceptors at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(
            game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

        # Remove locations that are blocked by our own structures
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)

        # While we have remaining MP to spend lets send out interceptors randomly.
        while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP] and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]

            game_state.attempt_spawn(INTERCEPTOR, deploy_location)
            """
            We don't have to remove the location since multiple mobile 
            units can occupy the same space.
            """

    def demolisher_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our demolisher can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [WALL, TURRET, SUPPORT]
        cheapest_unit = WALL
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost[game_state.MP] < gamelib.GameUnit(cheapest_unit, game_state.config).cost[game_state.MP]:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our demolisher from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn demolishers next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(DEMOLISHER, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET,
                                                                                             game_state.config).damage_i
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x=None, valid_y=None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (
                            valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
