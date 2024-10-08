"""
This the primary class for the Mario Expert agent. It contains the logic for the Mario Expert agent to play the game and choose actions.

Your goal is to implement the functions and methods required to enable choose_action to select the best action for the agent to take.

Original Mario Manual: https://www.thegameisafootarcade.com/wp-content/uploads/2017/04/Super-Mario-Land-Game-Manual.pdf
"""

import json
import logging
import random
import math

import cv2
from mario_environment import MarioEnvironment
from pyboy.utils import WindowEvent
from enum import Enum

class Action(Enum):
    DOWN = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    JUMP = 4
    PRESS_B = 5
    JUMP_OBS = 6
    JUMP_EMPTY = 7
    JUMP_POWER_UP = 8
    JUMP_SKIP_ENEMY = 9
    JUMP_RIGHT = 10
    ENEMY_LEFT = 11
    JUMP_STAIRS = 12
    TUNNEL_LEFT = 13
    JUMP_BIG_GAP = 14
    JUMP_EMPTY_REDUCED = 15

class Element(Enum):
    GUMBA = 15
    GROUND = 10
    BLOCK = 12
    POWERUP = 13
    PIPE = 14
    PICKUP = 6
    MARIO = 1
    EMPTY = 0
    TOAD = 16
    FLY = 18
    ARCHER = 19

row, col = 0, 0
prev_x = 0
curr_x = 0
prev_action = Action.RIGHT
next_action = Action.RIGHT

class MarioController(MarioEnvironment):
    """
    The MarioController class represents a controller for the Mario game environment.

    You can build upon this class all you want to implement your Mario Expert agent.

    Args:
        act_freq (int): The frequency at which actions are performed. Defaults to 10.
        emulation_speed (int): The speed of the game emulation. Defaults to 0.
        headless (bool): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(
        self,
        act_freq: int = 10,
        emulation_speed: int = 0,
        headless: bool = False,
    ) -> None:
        super().__init__(
            act_freq=act_freq,
            emulation_speed=emulation_speed,
            headless=headless,
        )

        self.act_freq = act_freq

        # Example of valid actions based purely on the buttons you can press
        valid_actions: list[WindowEvent] = [
            WindowEvent.PRESS_ARROW_DOWN,
            WindowEvent.PRESS_ARROW_LEFT,
            WindowEvent.PRESS_ARROW_RIGHT,
            WindowEvent.PRESS_ARROW_UP,
            WindowEvent.PRESS_BUTTON_A,
            WindowEvent.PRESS_BUTTON_B,
        ]

        release_button: list[WindowEvent] = [
            WindowEvent.RELEASE_ARROW_DOWN,
            WindowEvent.RELEASE_ARROW_LEFT,
            WindowEvent.RELEASE_ARROW_RIGHT,
            WindowEvent.RELEASE_ARROW_UP,
            WindowEvent.RELEASE_BUTTON_A,
            WindowEvent.RELEASE_BUTTON_B,
        ]

        self.valid_actions = valid_actions
        self.release_button = release_button

    def run_action(self, action: int) -> None:
        """
        Runs actions by pushing buttons for a set period of time. Certain actions can be pressed for longer, with different codes corresponding to each case.
        Action.JUMP <= Action.JUMP_OBS (jump obstacle)
        """
        # extended hold duration when jumping over obstacles
        if action == Action.JUMP_OBS.value:
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            for _ in range(self.act_freq*10):
                self.pyboy.tick()

            action = Action.JUMP.value

        elif action == Action.JUMP_POWER_UP.value:
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            for _ in range(self.act_freq):
                self.pyboy.tick()
            
            action = Action.JUMP.value
            #self.pyboy.send_input(self.release_button[action])
        elif action == Action.JUMP_EMPTY.value:
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            self.pyboy.send_input(self.valid_actions[Action.RIGHT.value])

            for _ in range(self.act_freq * 5):
                self.pyboy.tick()
            
            print("releasing right jump empty")
            self.pyboy.send_input(self.release_button[Action.JUMP.value])            
            action = Action.RIGHT.value
        
        elif action == Action.JUMP_BIG_GAP.value:
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            # self.pyboy.send_input(self.valid_actions[Action.RIGHT.value])

            for _ in range(self.act_freq * 10):
                self.pyboy.tick()
            
            print("releasing right jump empty")
            self.pyboy.send_input(self.release_button[Action.JUMP.value])            
            action = Action.RIGHT.value

        elif action == Action.ENEMY_LEFT.value:
            self.pyboy.send_input(self.valid_actions[Action.LEFT.value])
            time = int(self.act_freq)
            for _ in range(time):
                self.pyboy.tick()
            
            print("releasing enemy left")
            action = Action.LEFT.value

        elif action == Action.TUNNEL_LEFT.value:
            self.pyboy.send_input(self.valid_actions[Action.LEFT.value])
            for _ in range(self.act_freq*2):
                self.pyboy.tick()
            
            action = Action.LEFT.value
            
        elif action == Action.JUMP_SKIP_ENEMY.value:
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            self.pyboy.send_input(self.valid_actions[Action.RIGHT.value])
            for _ in range(self.act_freq * 2):
                self.pyboy.tick()
            self.pyboy.send_input(self.release_button[Action.RIGHT.value])
            action = Action.JUMP.value
        
        elif action == Action.JUMP_RIGHT.value:
            # normal jump right with normal button press timings
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            self.pyboy.send_input(self.valid_actions[Action.RIGHT.value])
            for _ in range(self.act_freq):
                self.pyboy.tick()
            self.pyboy.send_input(self.release_button[Action.RIGHT.value])
            action = Action.JUMP.value
        
        elif action == Action.JUMP_STAIRS.value:
            # normal jump right with normal button press timings
            self.pyboy.send_input(self.valid_actions[Action.LEFT.value])
            time = int(self.act_freq * 0.2)
            for _ in range(time):
                self.pyboy.tick()
            self.pyboy.send_input(self.release_button[Action.LEFT.value])
            
            self.pyboy.send_input(self.valid_actions[Action.RIGHT.value])
            for _ in range(self.act_freq): 
                self.pyboy.tick()
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            for _ in range(self.act_freq):
                self.pyboy.tick()
            self.pyboy.send_input(self.release_button[Action.JUMP.value])
            action = Action.RIGHT.value

        elif action == Action.JUMP_EMPTY_REDUCED.value:
            self.pyboy.send_input(self.valid_actions[Action.JUMP.value])
            self.pyboy.send_input(self.valid_actions[Action.RIGHT.value])

            for _ in range(self.act_freq * 1):
                self.pyboy.tick()
            
            print("REDUCED JUMP EMPTY")
            self.pyboy.send_input(self.release_button[Action.JUMP.value])            
            action = Action.RIGHT.value

        else:
            # normal hold duration on all other inputs
            self.pyboy.send_input(self.valid_actions[action])
            for _ in range(self.act_freq):
                self.pyboy.tick()

        self.pyboy.send_input(self.release_button[action])

class MarioExpert:
    """
    The MarioExpert class represents an expert agent for playing the Mario game.

    Edit this class to implement the logic for the Mario Expert agent to play the game.

    Do NOT edit the input parameters for the __init__ method.

    Args:
        results_path (str): The path to save the results and video of the gameplay.
        headless (bool, optional): Whether to run the game in headless mode. Defaults to False.
    """

    def __init__(self, results_path: str, headless=False):
        self.results_path = results_path

        self.environment = MarioController(headless=headless)

        self.video = None

    def get_distance(self, row0, col0, row1, col1):
        return math.sqrt(((col1-col0) * (col1-col0)) + ((row1-row0) * (row1-row0))) # pythagoras

    """
    Checks surroundings of Mario, to see if he's in the air. Returns true if all surrounding values are the same
    """
    def check_surrounding(self, row, col, game_area, value):
        print(f"checking surrounding for {value}")
        return (game_area[row - 1][col - 2] == value and
                game_area[row - 1][col - 1] == value and
                game_area[row - 1][col] == value and
                game_area[row - 1][col + 1] == value and
                game_area[row][col - 2] == value and
                game_area[row][col + 1] == value and
                game_area[row + 1][col - 2] == value and
                game_area[row + 1][col + 1] == value and
                game_area[row + 2][col - 2] == value and
                game_area[row + 2][col - 1 == value] and
                game_area[row + 2][col] == value and
                game_area[row + 2][col + 1] == value)

    """
    Gets mario's position, returns the top right corner of Mario
    11 <- this one
    11
    """
    def find_mario(self, game_area, row, col):
        x, y = game_area.shape
        for a in range(x):
            for b in range(y):
                if game_area[a][b] == 1:
                    return (a, b + 1)
        return 0, 0  # if mario is not found
    
    def find_enemy(self, game_area):
        x,y = game_area.shape
        for a in range(x):
            for b in range(y):
                if game_area[a][b] >= Element.GUMBA.value:
                    return (a, b)
        return 10000,0
    
    def get_enemy_dist(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks
                if game_area[a, b] >= 15:  # found enemy
                    # Compute distance 
                    if b >= col:  # If enemy is to the right of Mario
                        distance = self.get_distance(row, col, a, b)
                        return distance, game_area[a, b]
        # Return a default large distance and a default value if no enemy is found
        return 10000, None

    def check_platform_jump(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks
                if game_area[a, b] == Element.BLOCK.value:
                    # Compute distance
                    if a < row and b > col:  # If block is above and to the right of Mario
                        distance = self.get_distance(row, col, a, b)
                        print(f"distance to platform: {distance}")
                        if distance <= 7.0:
                            return True  # Found platform to jump on
        return False

    """
    Check for obstacle to jump over
    """
    def check_obstacle(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        if row <= 14: 
            for b in range(y):  # Iterate over columns
                for a in range(x):  # Iterate over rows
                    # Check for blocks or pipes
                    if (game_area[a][b] == Element.BLOCK.value or 
                        game_area[a][b] == Element.PIPE.value or
                        (game_area[a][b] == Element.GROUND.value and b > col and a <= row+1)):
                        if b > col:  # If block is to the right of Mario
                            distance = self.get_distance(row, col, a, b)
                            # print(f"distance to obs: {distance}")
                            if game_area[a, b] == Element.BLOCK.value:
                                if game_area[a+1,b] == Element.BLOCK.value and game_area[a-1,b] == Element.BLOCK.value:
                                    print(f"Distance to block: {distance}")

                            elif game_area[a,b] == Element.PIPE.value:
                                print(f"distance to pipe: {distance}")

                            elif game_area[a,b] == Element.GROUND.value:
                                # print(f"block loc: {a,b}")
                                # print(f"above value: {game_area[a-1,b]}")
                                if game_area[a+1,b] == Element.GROUND.value:
                                    # normal obstacle 
                                    if game_area[a-1,b] == Element.GROUND.value:
                                        print(f"Distance to Hill: {distance}")
                                        if distance <= 1.0:
                                            return "obstacle found"
                                    # # if found stairs below mario
                                    elif a == row+1: #and game_area[a-1,b] == Element.EMPTY.value:
                                        if distance <= 2.0:
                                            return "found stairs"
                            
                            if distance <= 2.0:
                                return "obstacle found"  # jump over obstacle
        return False

    def check_empty_jump(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for empty to the right below mario
                if (game_area[a][b] == Element.EMPTY.value and (a == row+2) and (b > col)):  
                        # check if ground is wide enough
                        if ((game_area[a][b-1] == Element.GROUND.value and
                            game_area[a][b-2] == Element.GROUND.value and
                            game_area[a][b-3] == Element.GROUND.value) or 
                            (game_area[a][b-1] == Element.BLOCK.value and
                            game_area[a][b-2] == Element.BLOCK.value and
                            game_area[a][b-3] == Element.BLOCK.value)): #and
                            #(game_area[a-1][b-1]) in [0, 1]):
                            # If ground is to the right and below of Mario and block next to it is ground
                            print(f"Empty loc: {a},{b}")
                            distance = self.get_distance(row, col, a, b)
                            print(f"Distance to empty: {distance}")
                            if distance <= 2.9: # changed from 2.5 to 2.9
                                return True  # jump over empty
        return False

    def check_power_up(self, row, col, game_area):
        x, y = game_area.shape  # x is the number of rows, y is the number of columns
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks
                if game_area[a, b] == Element.POWERUP.value and self.check_on_ground(row, col, game_area) == True:
                    if row >= a and b >= col:  # If power up is to the right and above Mario
                        distance = self.get_distance(row, col, a, b)
                        print(f"Distance to power up: {distance}")
                        if distance <= 3.0 and game_area[row+2,col] == Element.GROUND.value: # if on ground
                            return True
                        return False # missed power up
                    
    def check_on_ground(self, row, col, game_area):
        x, y = game_area.shape
        for b in range(y):  # Iterate over columns
            for a in range(x):  # Iterate over rows
                # Check for blocks
                if game_area[a, b] == Element.GROUND.value:
                    if col == b:  # If ground is under Mario
                        # check adjacent squares for ground
                        if game_area[a,b+1] == Element.GROUND.value and game_area[a][b-1] == Element.GROUND.value:
                            return True
        return False
    
    
    def choose_action(self):
        global prev_action, next_action, prev_x, curr_x
        global row, col

        curr_action = 0
        state = self.environment.game_state()
        game_area = self.environment.game_area()
        print(game_area)

        row,col = self.find_mario(game_area, row, col) # get game area
        enemy_row, enemy_col = self.find_enemy(game_area)
        curr_x = self.environment.get_x_position()

        print(f"prev_action: {prev_action}")
        print(f"Mario loc: {row},{col}")
        print(f"curr_x: {curr_x}")
        print(f"Enemy loc: {enemy_row},{enemy_col}")
        print(f"Level: {self.environment.get_world()} {self.environment.get_stage()}")
        
        # VARIABLES TO TRACK ENEMIES OR OBJECTS TO JUMP OVER/ REACT TO
        enemy_dist, enemy_type = self.get_enemy_dist(row, col, game_area)
        obstacle_check = self.check_obstacle(row, col, game_area)

        print(f"enemy distance: {enemy_dist}")

        if row < 14:
            
            # CHECK IF STANDING ON A PIPE
            if game_area[row+2][col] == Element.PIPE.value:
                    if(prev_action in [Action.JUMP, Action.JUMP_EMPTY, Action.JUMP_OBS, Action.JUMP_POWER_UP]):
                        curr_action = Action.UP
                        print("up pipe")
                    else:
                        print("jump off pipe")
                        curr_action = Action.JUMP_RIGHT

            # CHECK IF THERE IS AN ENEMY ABOVE
            elif enemy_row < row and enemy_col > col and enemy_dist < 6.0:
                curr_action = Action.LEFT

            # CHECK IF THERE IS AN ENEMY BELOW
            elif (row + 2 <= enemy_row and
                    enemy_row != 0 and 
                    prev_action in [Action.RIGHT]  and
                    (game_area[row+2][col] != Element.EMPTY.value and
                    enemy_dist < 7)): 
                    print("jump skip over enemy")
                    curr_action = Action.JUMP_EMPTY

            # IF TOO CLOSE TO AN ENEMY, REACT
            elif enemy_dist <= 4.5:
                # PROCESS GUMBAS
                if enemy_type == Element.GUMBA.value:
                    # normal case
                    if prev_action == Action.RIGHT:
                        curr_action = Action.JUMP # jump over gumba
                    # edge cases
                    # mario too close to gumba, just skip gumba
                    elif prev_action == Action.ENEMY_LEFT and enemy_dist < 2 and enemy_dist > 1.5:
                        curr_action = Action.JUMP_SKIP_ENEMY
                    # if prev action was jump, can't jump again
                    elif prev_action == Action.ENEMY_LEFT and enemy_dist >= 1.5:
                        # can jump over enemy now, needs to jump to the right
                        # print("jump right")
                        curr_action = Action.JUMP

                    # mario just jumped or in air
                    elif prev_action == Action.JUMP:
                        if enemy_dist < 5:
                            # safe to move left
                            print("gumba left")
                            curr_action = Action.ENEMY_LEFT 
                        else:
                            curr_action = Action.JUMP_RIGHT
                    
                    else:
                        curr_action = Action.JUMP
                
                # PROCESS TOAD ENEMIES                    
                elif enemy_type == Element.TOAD.value and enemy_dist <= 4:
                    print("toad left")
                    if prev_action == Action.JUMP:
                        curr_action = Action.LEFT
                    else:
                        curr_action = Action.JUMP

                # PROCESS FLY ENEMIES
                elif enemy_type == Element.FLY.value and enemy_dist <= 3:
                    if prev_action == Action.JUMP:
                        print("fly left")
                        curr_action = Action.LEFT
                    else:
                        curr_action = Action.JUMP

                # PROCESS ARCHER ENEMIES
                # only jump if it's on the same row, otherwise just escape
                elif enemy_type == Element.ARCHER.value and enemy_dist <= 4 and enemy_row == row:
                    if prev_action == Action.JUMP:
                        print("archer left")
                        curr_action = Action.LEFT
                    else:
                        curr_action = Action.JUMP

                else:
                    print("=====================")
                    print("Unknown Enemy found")
                    print(f"Unknown enemy value: {enemy_type}")
                    print("=====================")
                    curr_action = Action.RIGHT

            # CHECK EMPTY JUMP (PLATFORMS, OR HOLES)
            elif self.check_empty_jump(row, col, game_area):
                if 2282 <= curr_x <= 2286 and self.environment.get_stage() == 1 and self.environment.get_world() == 1: # edge case
                    curr_action = Action.UP
                # IN LEVEL 1-2, JUMP SHORTER DISTANCES
                elif self.environment.get_world() == 1 and self.environment.get_stage() == 2:
                    print("jump empty reduced")
                    curr_action = Action.JUMP_EMPTY_REDUCED
                elif prev_action == Action.JUMP_EMPTY or prev_action == Action.JUMP_BIG_GAP or prev_action == Action.JUMP_EMPTY_REDUCED:
                    print("jump over empty")
                    curr_action = Action.LEFT
                elif prev_action == Action.UP:
                    curr_action = Action.JUMP_BIG_GAP
                else:
                    curr_action = Action.JUMP_EMPTY

            # JUMP TO COLLECT POWER UP BOXES
            elif self.check_power_up(row, col, game_area):
                if(prev_action == Action.JUMP_POWER_UP):
                    print("Power up right")
                    curr_action = Action.RIGHT
                elif prev_action == Action.JUMP:
                    curr_action = Action.UP # stop so that mario can check for power ups
                else:
                    curr_action = Action.JUMP_POWER_UP

            # JUMP OVER OBSTACLES
            elif obstacle_check in ["obstacle found", "found stairs", True]:
                print(f"prev_x: {prev_x}")
                print(f"curr_x: {curr_x}")

                if prev_x == curr_x and obstacle_check == "found stairs":
                    curr_action = Action.JUMP_STAIRS

                elif prev_action == Action.JUMP_OBS:
                    print("jump over obstacle")
                    curr_action = Action.RIGHT

                else:
                    curr_action = Action.JUMP_OBS

            elif row == 0:
                curr_action = Action.UP  # when mario is off screen/ dead, move up
            else:
                curr_action = Action.RIGHT

        else:
            curr_action = Action.UP
        
        # fix up stuck condition
        if prev_action == Action.UP and curr_action == Action.UP:
            curr_action = Action.RIGHT
        
        prev_action = curr_action # record current action

        print("Action: ", curr_action)
        prev_x = curr_x
        return curr_action.value  # Return the value of the current action
    
    def step(self):
        """
        Runs each step of the game
        """
        #input("Press enter to continue") # for testing
        # Choose an action - button press or other...
        action = self.choose_action()
        # Run the action on the environment
        self.environment.run_action(action)

    def play(self):
        """
        Do NOT edit this method.
        """
        self.environment.reset()

        frame = self.environment.grab_frame()
        height, width, _ = frame.shape

        self.start_video(f"{self.results_path}/mario_expert.mp4", width, height)

        while not self.environment.get_game_over():
            frame = self.environment.grab_frame()
            self.video.write(frame)

            self.step()

        final_stats = self.environment.game_state()
        logging.info(f"Final Stats: {final_stats}")

        with open(f"{self.results_path}/results.json", "w", encoding="utf-8") as file:
            json.dump(final_stats, file)

        self.stop_video()

    def start_video(self, video_name, width, height, fps=30):
        """
        Do NOT edit this method.
        """
        self.video = cv2.VideoWriter(
            video_name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
        )

    def stop_video(self) -> None:
        """
        Do NOT edit this method.
        """
        self.video.release()


    