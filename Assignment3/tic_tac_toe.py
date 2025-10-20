from copy import deepcopy
import math

State = tuple[int, list[list[int | None]]]  # Tuple of player (whose turn it is),
                                            # and board
Action = tuple[int, int]  # Where to place the player's piece

class Game:
    def initial_state(self) -> State:
        return (0, [[None, None, None], [None, None, None], [None, None, None]])

    def to_move(self, state: State) -> int:
        player_index, _ = state
        return player_index

    def actions(self, state: State) -> list[Action]:
        _, board = state
        actions = []
        for row in range(3):
            for col in range(3):
                if board[row][col] is None:
                    actions.append((row, col))
        return actions

    def result(self, state: State, action: Action) -> State:
        _, board = state
        row, col = action
        next_board = deepcopy(board)
        next_board[row][col] = self.to_move(state)
        return (self.to_move(state) + 1) % 2, next_board

    def is_winner(self, state: State, player: int) -> bool:
        _, board = state
        for row in range(3):
            if all(board[row][col] == player for col in range(3)):
                return True
        for col in range(3):
            if all(board[row][col] == player for row in range(3)):
                return True
        if all(board[i][i] == player for i in range(3)):
            return True
        return all(board[i][2 - i] == player for i in range(3))

    def is_terminal(self, state: State) -> bool:
        _, board = state
        if self.is_winner(state, (self.to_move(state) + 1) % 2):
            return True
        return all(board[row][col] is not None for row in range(3) for col in range(3))

    def utility(self, state, player):
        assert self.is_terminal(state)
        if self.is_winner(state, player):
            return 1
        if self.is_winner(state, (player + 1) % 2):
            return -1
        return 0

    def print(self, state: State):
        _, board = state
        print()
        for row in range(3):
            cells = [
                ' ' if board[row][col] is None else 'x' if board[row][col] == 0 else 'o'
                for col in range(3)
            ]
            print(f' {cells[0]} | {cells[1]} | {cells[2]}')
            if row < 2:
                print('---+---+---')
        print()
        if self.is_terminal(state):
            if self.utility(state, 0) > 0:
                print(f'P1 won')
            elif self.utility(state, 1) > 0:
                print(f'P2 won')
            else:
                print('The game is a draw')
        else:
            print(f'It is P{self.to_move(state)+1}\'s turn to move')

# Implementation of minimax and alpha-beta pruning for a simple game
def minimax_search(game: Game, state: State) -> Action | None:
    max_player = game.to_move(state)

    def max_value(current_state: State):
        if game.is_terminal(current_state):
            return game.utility(current_state, max_player), None

        best_value = -math.inf
        best_action = None

        for action in game.actions(current_state):
            value_for_action, _ = min_value(game.result(current_state, action))
            if value_for_action > best_value:
                best_value = value_for_action
                best_action = action

        return best_value, best_action

    def min_value(current_state: State):
        if game.is_terminal(current_state):
            return game.utility(current_state, max_player), None

        best_value = math.inf
        best_action = None

        for action in game.actions(current_state):
            value_for_action, _ = max_value(game.result(current_state, action))
            if value_for_action < best_value:
                best_value = value_for_action
                best_action = action

        return best_value, best_action

    _, chosen_action = max_value(state)
    return chosen_action

def alphabeta_search(game: Game, state: State) -> Action | None:
    maximizing_player = game.to_move(state)

    def max_value(current_state: State, alpha: float, beta: float):
        if game.is_terminal(current_state):
            return game.utility(current_state, maximizing_player), None

        best_value = -math.inf
        best_action = None

        for action in game.actions(current_state):
            next_state = game.result(current_state, action)
            value, _ = min_value(next_state, alpha, beta)

            if value > best_value:
                best_value = value
                best_action = action

            if best_value >= beta:
                return best_value, best_action  # prune
            alpha = max(alpha, best_value)

        return best_value, best_action

    def min_value(current_state: State, alpha: float, beta: float):
        if game.is_terminal(current_state):
            return game.utility(current_state, maximizing_player), None

        best_value = math.inf
        best_action = None

        for action in game.actions(current_state):
            next_state = game.result(current_state, action)
            value, _ = max_value(next_state, alpha, beta)

            if value < best_value:
                best_value = value
                best_action = action

            if best_value <= alpha:
                return best_value, best_action  # prune
            beta = min(beta, best_value)

        return best_value, best_action

    _, chosen_action = max_value(state, -math.inf, math.inf)
    return chosen_action


game = Game()


# Minimax run
state = game.initial_state()
print("=== Minimax ===")
game.print(state)
while not game.is_terminal(state):
    player = game.to_move(state)
    action = minimax_search(game, state) # The player whose turn it is
                                         # is the MAX player
    print(f'P{player+1}\'s action: {action}')
    assert action is not None
    state = game.result(state, action)
    game.print(state)


# Alphabeta run
state = game.initial_state()
print("\n=== Alpha–Beta ===")
game.print(state)
while not game.is_terminal(state):
    player = game.to_move(state)
    action = alphabeta_search(game, state) # The player whose turn it is
                                         # is the MAX player
    print(f'P{player+1}\'s action: {action}')
    assert action is not None
    state = game.result(state, action)
    game.print(state)
