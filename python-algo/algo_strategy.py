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


class atkStructure:
    def __init__(self):
        self.as_op = []
        self.as_t = []
        self.as_w = []
        self.as_s = []

        self.add('build', [],
                 [[0, 13], [22, 13], [23, 13], [24, 13], [25, 13], [1, 12], [2, 11], [3, 10], [4, 9], [5, 8], [6, 7],
                  [7, 6], [8, 5], [9, 4], [15, 4], [10, 3], [14, 3], [11, 2], [13, 2], [12, 1]],
                 [[24, 12], [23, 11], [22, 10], [21, 9], [20, 8], [19, 7], [18, 6], [17, 5], [16, 4]])

        self.add('upgrade', [], [],
                 [[24, 12], [23, 11], [22, 10], [21, 9], [20, 8]])

    def add(self, op, turret_ls, wall_ls, support_ls):
        self.as_op.append(op)
        self.as_t.append(turret_ls)
        self.as_w.append(wall_ls)
        self.as_s.append(support_ls)

    def deploy(self, game_state):
        for op, turret_ls, wall_ls, support_ls in zip(self.as_op, self.as_t, self.as_w, self.as_s):
            if op == 'build':
                if len(turret_ls):
                    game_state.attempt_spawn(TURRET, turret_ls)
                if len(wall_ls):
                    game_state.attempt_spawn(WALL, wall_ls)
                if len(support_ls):
                    game_state.attempt_spawn(SUPPORT, support_ls)
            else:
                if len(turret_ls):
                    game_state.attempt_upgrade(turret_ls)
                if len(wall_ls):
                    game_state.attempt_upgrade(wall_ls)
                if len(support_ls):
                    game_state.attempt_upgrade(support_ls)

    def remove_all(self, game_state):
        for op, turret_ls, wall_ls, support_ls in zip(self.as_op, self.as_t, self.as_w, self.as_s):
            if op == 'build':
                for turret in turret_ls:
                    game_state.attempt_remove(turret)
                for wall in wall_ls:
                    game_state.attempt_remove(wall)
                for support in support_ls:
                    game_state.attempt_remove(support)


class defStructure:
    def __init__(self):
        self.ds_op = []
        self.ds_t = []
        self.ds_w = []
        self.ds_s = []

        # self.ds_door = [[22, 10]]

        self.important_structure = []

        self.add('build', [[1, 12], [25, 12], [23, 11], [20, 10]],
                 [[0, 13], [26, 13], [27, 13], [2, 11], [24, 11], [3, 10], [4, 9], [19, 9], [5, 8], [18, 8], [6, 7],
                  [17, 7], [7, 6], [8, 6], [9, 6], [16, 6], [10, 5], [15, 5], [11, 4], [14, 4], [12, 3], [13, 3]], [])

        self.add('build', [[23, 12], [21, 11], [25, 11]], [[24, 13], [24, 12], [26, 12]], [])
        self.add('build', [], [[1, 13], [2, 13]], [])
        self.add('build', [[2, 12]], [], [])

        self.add('build', [[21, 12], [19, 11], [20, 11]],
                 [[23, 13], [25, 13], [18, 12], [19, 12], [20, 12]], [])

        self.add('upgrade', [], [[0, 13], [26, 13], [27, 13], [2, 11], [3, 10], [4, 9]], [])

        self.add('build', [[21, 10], [23, 10], [23, 9], [22, 8]],
                 [[24, 10]], [])

        self.add('upgrade', [[1, 12]], [], [])

        self.add('upgrade',
                 [[1, 12], [25, 12], [23, 12], [19, 11], [20, 10], [21, 12], [23, 11], [21, 11], [25, 11], [20, 11],
                  [21, 10], [23, 10], [23, 9], [22, 8]], [], [])

        self.add('upgrade', [], [[1, 13], [2, 13]], [])
        self.add('upgrade', [[2, 12]], [], [])

        self.add('upgrade', [],
                 [[23, 13], [24, 13], [25, 13], [18, 12], [19, 12], [20, 12], [24, 12], [24, 11],
                  [26, 12], [24, 10]], [])

        self.add('build', [], [], [[15, 6]])

        self.add('build', [[19, 8], [18, 7], [21, 7], [17, 6], [20, 6], [20, 9]], [], [])

        self.add('upgrade', [[19, 8], [18, 7], [21, 7], [17, 6], [20, 6], [20, 9]], [], [])

        self.add('build', [], [], [[19, 10], [18, 9], [17, 8], [16, 7], [15, 6], [14, 5]])

        self.add('build', [], [], [[18, 10], [17, 9], [16, 8], [15, 7], [14, 6], [13, 5], [12, 4]])

        self.add('upgrade', [], [], [[18, 10], [17, 9], [16, 8], [15, 7], [14, 6], [13, 5], [12, 4]])

    def add(self, op, turret_ls, wall_ls, support_ls):
        self.ds_op.append(op)
        self.ds_t.append(turret_ls)
        self.ds_w.append(wall_ls)
        self.ds_s.append(support_ls)

    # def rebuild(self, game_state):
    #     for turret_ls in self.ds_t:
    #         for turret in turret_ls:
    #             st = game_state.contains_stationary_unit(turret)
    #             if st == False:
    #                 continue
    #             if (st.upgraded) and (st.health < 0.5 * st.max_health):
    #                 game_state.attempt_remove(turret)
    #             if (not st.upgraded) and (st.health < 0.8 * st.max_health):
    #                 game_state.attempt_remove(turret)
    #     for wall_ls in self.ds_w:
    #         for wall in wall_ls:
    #             st = game_state.contains_stationary_unit(wall)
    #             if st == False:
    #                 continue
    #             if (st.upgraded) and (st.health < 0.75 * st.max_health):
    #                 game_state.attempt_remove(wall)
    #             if (not st.upgraded) and (st.health < 0.9 * st.max_health):
    #                 game_state.attempt_remove(wall)

    # def processAttackSig(self, this_round_attack, next_round_attack, game_state):
    #     if not this_round_attack:
    #         game_state.attempt_spawn(WALL, self.ds_door)
    #     if next_round_attack:
    #         game_state.attempt_remove(self.ds_door)

    def deploy(self, game_state):
        for op, turret_ls, wall_ls, support_ls in zip(self.ds_op, self.ds_t, self.ds_w, self.ds_s):
            if op == 'build':
                if len(turret_ls):
                    game_state.attempt_spawn(TURRET, turret_ls)
                if len(wall_ls):
                    game_state.attempt_spawn(WALL, wall_ls)
                if len(support_ls):
                    game_state.attempt_spawn(SUPPORT, support_ls)
            else:
                if len(turret_ls):
                    game_state.attempt_upgrade(turret_ls)
                if len(wall_ls):
                    game_state.attempt_upgrade(wall_ls)
                if len(support_ls):
                    game_state.attempt_upgrade(support_ls)

    def remove_all(self, game_state):
        for op, turret_ls, wall_ls, support_ls in zip(self.ds_op, self.ds_t, self.ds_w, self.ds_s):
            if op == 'build':
                for turret in turret_ls:
                    game_state.attempt_remove(turret)
                for wall in wall_ls:
                    game_state.attempt_remove(wall)
                for support in support_ls:
                    game_state.attempt_remove(support)

    def all_SP(self, game_state):
        all_sp = game_state.get_resource(0)
        for op, turret_ls, wall_ls, support_ls in zip(self.ds_op, self.ds_t, self.ds_w, self.ds_s):
            if op == 'build':
                for turret in turret_ls:
                    st = game_state.contains_stationary_unit(turret)
                    if st == False:
                        continue
                    if st.upgraded:
                        all_sp += (st.health / st.max_health) * 0.9 * 6
                    else:
                        all_sp += (st.health / st.max_health) * 0.97 * 2
                for wall in wall_ls:
                    st = game_state.contains_stationary_unit(wall)
                    if st == False:
                        continue
                    if st.upgraded:
                        all_sp += (st.health / st.max_health) * 0.9 * 2
                    else:
                        all_sp += (st.health / st.max_health) * 0.97 * 1
                for support in support_ls:
                    st = game_state.contains_stationary_unit(support)
                    if st == False:
                        continue
                    if st.upgraded:
                        all_sp += (st.health / st.max_health) * 0.9 * 8
                    else:
                        all_sp += (st.health / st.max_health) * 0.97 * 4
        return all_sp


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

        self.ds = defStructure()
        self.atks = atkStructure()
        self.special_attack_flag = False

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
        if game_state.turn_number <= 20:
            cur_flag, future_flag = self.attack(game_state)
            self.defend(game_state, cur_flag, future_flag)
        else:
            if self.special_attack_flag:
                self.special_attack_flag = False
                self.atks.deploy(game_state)
                self.atks.remove_all(game_state)

                # 发起突围
                self.attack_right_corner(game_state)
            else:
                if self.check_attack_right_corner(game_state):
                    self.special_attack_flag = True
                    self.ds.remove_all(game_state)
                else:
                    self.ds.deploy(game_state)

                # interceptor 去吃
                others_mp = game_state.get_resource(MP, 1)
                self.stall_with_interceptors(game_state, others_mp // 10)

    def defend(self, game_state, cur_flag, future_flag):
        # self.ds.processAttackSig(cur_flag, future_flag, game_state)
        # self.ds.rebuild(game_state)
        self.ds.deploy(game_state)

    def check_right_corner_attacker(self, game_state):
        path = [[24, 10], [24, 11], [25, 11], [25, 12], [26, 12], [26, 13], [27, 13], [27, 14]]
        harm_point = 0
        for point in path:
            for attacker in game_state.get_attackers(point, 1):
                if attacker.upgraded:
                    harm_point += 15
                else:
                    harm_point += 6
        return harm_point

    def check_right_corner_defender(self, game_state):
        path = [[27, 14], [26, 14], [25, 14]]
        defend_point = 0
        for point in path:
            point_instant = game_state.contains_stationary_unit(point)
            if not point_instant:
                continue

            if point_instant.unit_type == WALL:
                defend_point += 120 if point_instant.upgraded else 60
            if point_instant.unit_type == TURRET:
                defend_point += 60
        return defend_point

    def check_attack_right_corner(self, game_state):
        '''
            1. 结构点太少
            2. 对方的MP较少（12)
            3. 根据对方的防守计算 & 进攻 计算破坏者数量
            4. 剩下的全部scout
        '''
        if self.ds.all_SP(game_state) < 80:
            return False

        others_mp = game_state.get_resource(MP, 1)
        my_mp = game_state.get_resource(MP, 0)

        if others_mp >= 12:
            return False

        harm_point = self.check_right_corner_attacker(game_state)
        defend_point = self.check_right_corner_defender(game_state)

        num_demolisher = math.ceil(defend_point / 8)

        # 当前移动点不够造出足够破坏者
        if num_demolisher * 3 <= my_mp:
            return False
        return True

    def attack_right_corner(self, game_state):
        others_mp = game_state.get_resource(MP, 1)
        my_mp = game_state.get_resource(MP, 0)

        harm_point = self.check_right_corner_attacker(game_state)
        defend_point = self.check_right_corner_defender(game_state)

        num_demolisher = math.ceil(defend_point / 8)

        # 当前移动点不够造出足够破坏者
        if num_demolisher * 3 <= my_mp:
            return

        self.stall_with_demolisher(game_state, num_demolisher)
        self.stall_with_scout(game_state)

    def attack(self, game_state):
        others_mp = game_state.get_resource(MP, 1)
        self.stall_with_interceptors(game_state, others_mp // 10)

        cur_flag = False
        future_flag = False
        if game_state.turn_number % 4 == 0:
            self.stall_with_demolisher(game_state, 100)
            cur_flag = True
        if game_state.turn_number % 4 == 2:
            self.stall_with_scout(game_state)
            cur_flag = True

        future_flag = not cur_flag
        return cur_flag, future_flag

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
        scout_spawn_location_options = [[13, 0]]
        best_location = self.least_damage_spawn_location(game_state, scout_spawn_location_options)

        while game_state.get_resource(MP) >= game_state.type_cost(SCOUT)[MP] and len(best_location) > 0:
            game_state.attempt_spawn(SCOUT, scout_spawn_location_options)

    def stall_with_demolisher(self, game_state, num):
        """
        只放置破坏者在[11, 2] ][16, 2]
        选择一个点进行放置
        """
        scout_spawn_location_options = [[21, 7]]
        best_location = self.least_damage_spawn_location(game_state, scout_spawn_location_options)

        while game_state.get_resource(MP) >= game_state.type_cost(DEMOLISHER)[MP] and len(
                best_location) > 0 and num > 0:
            game_state.attempt_spawn(DEMOLISHER, best_location)
            num -= 1

    def stall_with_interceptors(self, game_state, num):
        interceptor_spawn_location_options = [[19, 5]]
        best_location = self.least_damage_spawn_location(game_state, interceptor_spawn_location_options)

        while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP] and len(
                best_location) > 0 and num > 0:
            game_state.attempt_spawn(INTERCEPTOR, interceptor_spawn_location_options)
            num -= 1

    # def stall_with_interceptors(self, game_state):
    #     """
    #     Send out interceptors at random locations to defend our base from enemy moving units.
    #     """
    #     # We can spawn moving units on our edges so a list of all our edge locations
    #     friendly_edges = game_state.game_map.get_edge_locations(
    #         game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
    #
    #     # Remove locations that are blocked by our own structures
    #     # since we can't deploy units there.
    #     deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
    #
    #     # While we have remaining MP to spend lets send out interceptors randomly.
    #     while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP] and len(deploy_locations) > 0:
    #         # Choose a random deploy location.
    #         deploy_index = random.randint(0, len(deploy_locations) - 1)
    #         deploy_location = deploy_locations[deploy_index]
    #
    #         game_state.attempt_spawn(INTERCEPTOR, deploy_location)
    #         """
    #         We don't have to remove the location since multiple mobile
    #         units can occupy the same space.
    #         """

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
