from enum import Enum
import re

def read_log_file(log_path):
    lines = []
    with open(log_path, 'r') as file:
        for line in file:
            words = re.split(r'[ \\\\]', line.strip())
            words = [word for word in words if word]
            lines.append(words)
    return lines

class DeathCausesCount:
    MOD_UNKNOWN = 0
    MOD_SHOTGUN = 0
    MOD_GAUNTLET = 0
    MOD_MACHINEGUN = 0
    MOD_GRENADE = 0
    MOD_GRENADE_SPLASH = 0
    MOD_ROCKET = 0
    MOD_ROCKET_SPLASH = 0
    MOD_PLASMA = 0
    MOD_PLASMA_SPLASH = 0
    MOD_RAILGUN = 0
    MOD_LIGHTNING = 0
    MOD_BFG = 0
    MOD_BFG_SPLASH = 0
    MOD_WATER = 0
    MOD_SLIME = 0
    MOD_LAVA = 0
    MOD_CRUSH = 0
    MOD_TELEFRAG = 0
    MOD_FALLING = 0
    MOD_SUICIDE = 0
    MOD_TARGET_LASER = 0
    MOD_TRIGGER_HURT = 0
    MOD_NAIL = 0
    MOD_CHAINGUN = 0
    MOD_PROXIMITY_MINE = 0
    MOD_KAMIKAZE = 0
    MOD_JUICED = 0
    MOD_GRAPPLE = 0
    
def find_delete_player(players_array, players_index_array, player_index):
    for i in range(len(players_index_array)):
        if player_index == players_index_array[i]:
            old_player_name = players_array[i]
            del players_array[i]
            del players_index_array[i]
            return old_player_name
    return ""
            
    
class Game:
    def __init__(self, name):
        self.name = name
        self.total_kills = 0
        self.players = []
        self.players_index = []
        self.kills = {}
        self.kills_by_means = DeathCausesCount()
    
    def add_player_index(self,player_index):
        self.players_index.append(player_index)
    
    def add_player_name(self, player_name):
        self.players.append(player_name)
        self.kills[player_name] = 0
        
    def change_player_name(self, new_player_name, player_index):
        old_player_name = find_delete_player(self.players, self.players_index, player_index)
        if old_player_name == "":
            raise Exception("Player not found!")
        self.players.append(new_player_name)
        self.players_index.append(player_index)
        current_player_kills = self.kills[old_player_name]
        del self.kills[old_player_name]
        self.kills[new_player_name] = current_player_kills
        
    def delete_player(self, player_index):
        find_delete_player(self.players, self.players_index, player_index)
    
    def add_kill(self, player_name, death_cause):
        self.total_kills += 1
        self.kills[player_name] += 1
        setattr(self.kills_by_means, death_cause, getattr(self.kills_by_means, death_cause) + 1)
    
    def world_self_kill(self, player_name, death_cause):
        self.total_kills += 1
        self.kills[player_name] -= 1
        setattr(self.kills_by_means, death_cause, getattr(self.kills_by_means, death_cause) + 1)
        
    def report(self):
        print(f"{self.name}:")
        print(f"  Total kills: {self.total_kills}")
        print("  Players and kills:")
        for player, kills in self.kills.items():
            print(f"    {player}: {kills}")
        print("  Death causes:")
        if self.total_kills != 0:
            kill_causes = vars(self.kills_by_means)
            formatted_causes = ', '.join(f"{k} = {v}" for k, v in kill_causes.items())
            print(f"    {formatted_causes}")
        else:
            print("    No kills occurred")
        print()

def main():
    log_path = "qgames.log"
    
    log_lines = read_log_file(log_path)
    
    matches = []
    game_number = 1
    game_name = 'game_' + str(game_number)
    match = Game(game_name)
    
    for line in log_lines:
        match line[1]:
            case "ClientConnect:":
                match.add_player_index(line[2])
            case "ClientUserinfoChanged:":
                if len(match.players) == len(match.players_index):
                    n_index = 3
                    t_index = line.index('t')
                    player_name = ' '.join(line[n_index+1:t_index])
                    match.change_player_name(player_name, line[2])
                else:
                    n_index = 3
                    t_index = line.index('t')
                    player_name = ' '.join(line[n_index+1:t_index])
                    match.add_player_name(player_name)
            case "ClientDisconnect:":
                match.delete_player(line[2])
            case "Kill:":
                first_player_index = 4
                killed_index = line.index('killed')
                by_index = line.index('by')
                death_cause = line[by_index+1]
                killer_player = ' '.join(line[first_player_index+1:killed_index])
                killed_player = ' '.join(line[killed_index+1:by_index])
                if killer_player == "<world>" or killer_player == killed_player:
                    match.world_self_kill(killed_player, death_cause)
                else:
                    match.add_kill(killer_player, death_cause)
            case "ShutdownGame:":
                matches.append(match)
                match.report()
                game_number += 1
                game_name = 'game_' + str(game_number)
                match = Game(game_name)
            case "InitGame:":
                if len(match.players) != 0:            
                    matches.append(match)
                    match.report()
                    game_number += 1
                    game_name = 'game_' + str(game_number)
                    match = Game(game_name)
            case _:
                pass
    
main()