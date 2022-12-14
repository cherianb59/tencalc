import random 
from tenprofiles import *

class Player():
     def __init__(self, game, player_name, initial_player_state , player_profile ):
        self.name = player_name
        if initial_player_state == None:
            self.points = 0 
            self.games  = 0 
            self.sets  = 0 
            self.match  = 0 
        else :
            self.points = initial_player_state["points"] 
            self.games  = initial_player_state["games"]
            self.sets  = initial_player_state["sets"]
            self.match  = initial_player_state["match"]

        self.profile = player_profile
        self.game = game
        self.state = {}
        self.state["point_streak"] = 0
        self.state["pressure_point"] = 0
        self.state["winning_sets"] = 0
        self.state["big_point"] = 0
        self.state["service"] = False

class Match():
    def __init__(self, game_id, seed  = None , player_names = ["0","1"], player_states = [None,None], player_profiles = [default_player_profile, default_player_profile] , set_limit = 3 ):
        self.id = game_id
        #define players
        self.a = Player(self, player_names[0], player_states[0],player_profiles[0])
        self.b = Player(self, player_names[1], player_states[1],player_profiles[1])
        self.set_limit = set_limit
        random.seed(seed)

    def run_match(self):
       # print("playing_match")
        match_result = 0 
        #TODO make this defined in Match initialisation
        self.a.state["service"] = True
        self.b.state["service"] = False
        while match_result == 0:
            match_result = check_match(self.a.sets,self.b.sets,self.set_limit)
            if   match_result == 1 :
                self.a.match = 1
                self.b.match = 0
            elif match_result == -1 :
                self.a.match = 0
                self.b.match = 1
            else :                
                self.run_set()
                
    def run_set(self):
        #print("playing_set")
        set_result =  0 
        while set_result == 0:
            set_result = check_set(self.a.games,self.b.games)
            if   set_result == 1 :
                self.a.sets += 1
                self.a.games = 0
                self.b.games = 0
            elif set_result == -1 :
                self.b.sets += 1
                self.a.games = 0
                self.b.games = 0
            else :
                self.run_game()        
                
    def run_game(self):              
        game_result =  0 
        while game_result == 0:
            game_result = check_game(self.a.points,self.b.points)
            if game_result == 1 or game_result == -1 :
                #reset points
                self.a.points = 0
                self.b.points = 0
                self.a.state["point_streak"] = 0
                self.b.state["point_streak"] = 0
                #switch serving
                self.a.state["service"] = not(self.a.state["service"])
                self.b.state["service"] = not(self.b.state["service"])
                
            if game_result == 1 :
                self.a.games += 1
            elif game_result == -1 :
                self.b.games += 1
            else :
                #print(self.a.state["service"] )
                if self.a.state["service"] :
                    probability = calculate_p(self.a,self.b)
                else :
                    probability = 1 - calculate_p(self.b,self.a)
                point = run_point(probability)                        
                if point : 
                    self.a.points += 1 
                    self.a.state["point_streak"] = 1
                    self.b.state["point_streak"] = 0
                else : 
                    self.b.points += 1 
                    self.a.state["point_streak"] = 0
                    self.b.state["point_streak"] = 1

#helper functions                
def calculate_p(server, receiver):    
  '''
Calculate the probability of the server winning a service point
  '''
  
  base_p = server.profile["win_serve_p"] 
  base_p += server.state["point_streak"] * server.profile["point_streak_adv"] +  receiver.state["point_streak"] * receiver.profile["point_streak_adv"]
  base_p += server.state["pressure_point"] * server.profile["pressure_point_adv"] + receiver.state["pressure_point"] * receiver.profile["pressure_point_adv"]
  return(base_p)


#a point is just a roll of the dice
def run_point(p :float) ->bool:
    #print(p)
    return(random.uniform(0,1)<p)

def determine_pressure_point(server_points :int, server_games :int, receiver_points :int, receiver_games :int) ->bool:    
  '''
Determine if the current point is a pressure point, a pressure point is a break point or set point
  '''
  #break point (also covers set points for receiver) last condition ensures non tiebreaker games
  if receiver_points >= 3 and receiver_points > server_points and server_games <= 5 : return(True)
  #set point for server (non tiebreaker)
  if server_points >= 3 and server_games >= 5 and server_games > receiver_games: return(True)
  #set point (tiebreaker) covers both server and receiver
  if (server_games == 6 and receiver_games == 6) and (server_points >=6 or reciever_points >= 6 ) and (server_points != reciever_points): return(True)
  return(False)
    
#winning conditions 
def check_game(a_set:int,b_set:int) ->int:
    if (a_set-b_set) >= 2 and a_set >= 4 : return(1)
    elif (b_set-a_set) >= 2 and b_set >= 4 : return(-1)
    else: return(0)

def check_tiebreaker_game(a_game:int,b_game:int)->bool:
    return(a_game == 6 and b_game == 6)
    
def check_tiebreaker(a_point,b_point)->int:
    if (a_point - b_point) >= 2 and a_point >= 7 : return(1)
    elif (b_point - a_point) >= 2 and b_point >= 7 : return(-1)
    else: return(0)

def check_set(a_game :int, b_game :int, tiebreaker_flag:bool = True)->int:
    if   ((a_game - b_game) >= 2 and a_game >= 6) or (tiebreaker_flag  == True and a_game == 7 and b_game == 6) : 
        return(1)
    elif ((b_game-a_game) >= 2 and b_game >= 6) or (tiebreaker_flag  == True and a_game==6 and b_game==7) : 
        return(-1)
    else: return(0)

def check_match(a_set :int , b_set :int ,set_limit :int)->int:
    if a_set==set_limit: return(1)
    if b_set==set_limit: return(-1)
    else: return(0)
            