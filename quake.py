import json
import re

#This divides the words in a log line whenever a ' ' or a '\' character appears.
def read_log_file(log_path):
    lines = []
    with open(log_path, 'r') as file:
        for line in file:
            words = re.split(r'[ \\\\]', line.strip())
            words = [word for word in words if word]
            lines.append(words)
    return lines
    
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
        self.kills_by_means = {}
    
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
        if death_cause in self.kills_by_means:
            self.kills_by_means[death_cause] += 1
        else:
            self.kills_by_means[death_cause] = 1
    
    def world_self_kill(self, player_name, death_cause):
        self.total_kills += 1
        self.kills[player_name] -= 1
        if death_cause in self.kills_by_means:
            self.kills_by_means[death_cause] += 1
        else:
            self.kills_by_means[death_cause] = 1
        
    def report(self):
        game_info = {
            self.name: {
                "total_kills": self.total_kills,
                "players": self.players,
                "kills": self.kills,
                "kills_by_means": self.kills_by_means
            }
        }
        game_info = json.dumps(game_info, indent=2)
        print(game_info)
        print()

def main():
    log_path = "qgames.log"
    
    log_lines = read_log_file(log_path)
    
    game_number = 1
    game_name = 'game_' + str(game_number)
    match = Game(game_name)
    
    for line in log_lines:
        match line[1]:
            #The index is stored first, followed by the username in a subsequent ClientUserinfoChanged event
            case "ClientConnect:":
                match.add_player_index(line[2])
            #When a client info is changed, the username is contained in n\Dono da Bola\t, so the indexes of n and t are used to obtain the name inbetween
            case "ClientUserinfoChanged:":
                #This checks if ClientUserinfoChanged was called right after ClientConnect
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
            #The 'Kill' line is assumed to always be in the shape of "(number with fixed position in line array): x killed y by z" 
            case "Kill:":
                fixed_number_index = 4
                killed_index = line.index('killed')
                by_index = line.index('by')
                death_cause = line[by_index+1]
                killer_player = ' '.join(line[fixed_number_index+1:killed_index])
                killed_player = ' '.join(line[killed_index+1:by_index])
                if killer_player == "<world>" or killer_player == killed_player:
                    match.world_self_kill(killed_player, death_cause)
                else:
                    match.add_kill(killer_player, death_cause)
            case "ShutdownGame:":
                match.report()
                game_number += 1
                game_name = 'game_' + str(game_number)
                match = Game(game_name)
            case "InitGame:":
                #This was done because of line 97 in the log, where a ShutdownGame is omitted.
                if len(match.players) != 0:            
                    match.report()
                    game_number += 1
                    game_name = 'game_' + str(game_number)
                    match = Game(game_name)
            case _:
                pass
    
main()