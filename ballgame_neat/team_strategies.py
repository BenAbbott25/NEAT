import numpy as np
import torch

class team5_strategy: # 1-4 wall
    def __init__(self):
        pass

    def act(self, state):
        state = state[0]

        self.direction = state[0]
        self.defender1state = state[1:4]
        self.defender2state = state[4:7]
        self.strikerstate = state[7:10]
        self.defender3state = state[10:13]
        self.defender4state = state[13:16]
        self.ballstate = state[-4:]

        defender1actions = self.get_defender_actions(self.defender1state, -.75)
        defender2actions = self.get_defender_actions(self.defender2state, -.25)
        strikeractions = self.get_striker_actions(self.strikerstate)
        defender3actions = self.get_defender_actions(self.defender3state, .25)
        defender4actions = self.get_defender_actions(self.defender4state, .75)

        actions = np.concatenate([defender1actions, defender2actions, strikeractions, defender3actions, defender4actions])
        return torch.tensor(actions)
    
    def get_defender_actions(self, player_state, defender_centre):
        action = [0,0,0,0]
        action[0] = 1 if player_state[0] < -0.75 * self.direction else -1

        if player_state[1] != defender_centre:
            action[1] = defender_centre - player_state[1]

        if (self.ballstate[0] < -0.25 and self.direction == 1) or (self.ballstate[0] > 0.25 and self.direction == -1):
            action[1] = 1 if self.ballstate[1] > player_state[1] else -1

        if player_state[2] != 0:
            target_vector_x = self.strikerstate[0] - player_state[0]
            target_vector_y = self.strikerstate[1] - player_state[1]
            action[3] = target_vector_x / max(abs(target_vector_x), abs(target_vector_y))
            action[2] = target_vector_y / max(abs(target_vector_x), abs(target_vector_y))

        return action
    
    def get_striker_actions(self, player_state):
        action = [0,0,0,0]
        if player_state[0] < -0.1 * self.direction:
            action[0] = 1
        elif player_state[0] > 0.1 * self.direction:
            action[0] = -1

        if player_state[1] != 0:
            action[1] = -player_state[1]

        x_offset = -0.1 * self.direction
        if -.25 + x_offset < self.ballstate[0] < .25 + x_offset and -.25 < self.ballstate[1] < .25:
            action[0] = min(max(10*(self.ballstate[0] - player_state[0]), -1), 1)
            action[1] = min(max(10*(self.ballstate[1] - player_state[1]), -1), 1)

        if player_state[2] != 0:
            action[2] = np.random.normal(0, 0.25)
            action[3] = self.direction

        return action

class team6_strategy: # 2-1-2 wing strikes
    def __init__(self):
        pass

    def act(self, state):
        state = state[0]

        self.direction = state[0]
        self.wing1state = state[1:4]
        self.defender1state = state[4:7]
        self.setterstate = state[7:10]
        self.defender2state = state[10:13]
        self.wing2state = state[13:16]
        self.ballstate = state[-4:]

        wing1actions = self.get_wing_actions(self.wing1state, -.75)
        defender1actions = self.get_defender_actions(self.defender1state, -.5)
        setteractions = self.get_setter_actions(self.setterstate)
        defender2actions = self.get_defender_actions(self.defender2state, .5)
        wing2actions = self.get_wing_actions(self.wing2state, .75)

        actions = np.concatenate((wing1actions, defender1actions, setteractions, defender2actions, wing2actions))
        return torch.tensor(actions)
    
    def get_defender_actions(self, player_state, defender_centre):
        action = [0,0,0,0]
        if player_state[0] != -0.75 * self.direction:
            action[0] = -self.direction

        if player_state[1] != defender_centre:
            action[1] = defender_centre - player_state[1]

        if (self.ballstate[0] < -0.25 and self.direction == 1) or (self.ballstate[0] > 0.25 and self.direction == -1):
            action[1] = 1 if self.ballstate[1] > player_state[1] else -1

        if player_state[2] != 0:
            target_vector_x = self.setterstate[0] - player_state[0]
            target_vector_y = self.setterstate[1] - player_state[1]
            action[3] = target_vector_x / max(abs(target_vector_x), abs(target_vector_y))
            action[2] = target_vector_y / max(abs(target_vector_x), abs(target_vector_y))

        return action
    
    def get_setter_actions(self, player_state):
        action = [0,0,0,0]
        if player_state[0] < -0.1 * self.direction:
            action[0] = 1
        elif player_state[0] > 0.1 * self.direction:
            action[0] = -1

        if player_state[1] != 0:
            action[1] = -player_state[1]

        x_offset = -0.1 * self.direction
        if -.25 + x_offset < self.ballstate[0] < .25 + x_offset and -.25 < self.ballstate[1] < .25:
            action[0] = min(max(10*(self.ballstate[0] - player_state[0]), -1), 1)
            action[1] = min(max(10*(self.ballstate[1] - player_state[1]), -1), 1)

        if player_state[2] != 0:
            wing_choice_state = np.random.choice(["wing1state", "wing2state"])
            if wing_choice_state == "wing1state":
                wing_choice_state = self.wing1state
            else:
                wing_choice_state = self.wing2state
            if abs(wing_choice_state[0]) > 0.55:
                target_vector_x = wing_choice_state[0] - player_state[0]
                target_vector_y = wing_choice_state[1] - player_state[1]
                action[3] = target_vector_x / max(abs(target_vector_x), abs(target_vector_y))
                action[2] = target_vector_y / max(abs(target_vector_x), abs(target_vector_y))

        return action
    
    def get_wing_actions(self, player_state, wing_centre):
        action = [0,0,0,self.direction]
        if player_state[0] < 0.65 * self.direction:
            action[0] = 1
        elif player_state[0] > 0.65 * self.direction:
            action[0] = -1

        if player_state[1] != wing_centre:
            action[1] = wing_centre - player_state[1]

        if (self.ballstate[0] > 0.5 and self.direction == 1) or (self.ballstate[0] < -0.5 and self.direction == -1):
            if abs(self.ballstate[1] - wing_centre) < 0.5:
                action[1] = 1 if self.ballstate[1] > player_state[1] else -1

        return action