from .constants import MaxUtility, MaxTime, MaxDepth
import time
from checkers.constants import ROWS, COLS, RED, WHITE
import copy
from checkers.game import Game

class State:
    def __init__(self, game, isPlayer, moves = 0):
        self.game = Game(None, copy.deepcopy(game.selected), copy.deepcopy(game.board), copy.deepcopy(game.turn), copy.deepcopy(game.valid_moves))
        self.moves = moves
        self.isPlayer = isPlayer

    def is_goal_state(self):
        if self.game.winner() is not None:
            return True
        else:
            return False

    def goal_state_utility(self):
        if self.game.winner() == self.isPlayer:
            return MaxUtility
        else:
            return -MaxUtility

    def get_successor(self):
        successors = []
        for row in range(ROWS):
            for col in range(COLS):
                Piece = self.game.board.get_piece(row, col)
                if Piece != 0 and Piece.color == self.game.turn:
                    self.game.select(row, col)
                    for move in self.game.valid_moves:
                        moves = [Piece, move[0], move[1]]
                        gameCopy = Game(self.game.win, copy.deepcopy(Piece), copy.deepcopy(self.game.board), copy.deepcopy(self.game.turn), copy.deepcopy(self.game.valid_moves))
                        mrow, mcol = move
                        gameCopy.make_move(Piece, mrow, mcol)
                        successors.append(State(gameCopy, self.isPlayer, moves))

        return successors

    def heurestic_function(state):
        red, white = 0, 0
        for row in range(ROWS):
            for col in range(COLS):
                Piece = state.game.board.get_piece(row, col)
                if Piece !=0:
                    if Piece.color == RED:
                        if Piece.queen == False:
                            red += 1.0
                        else:
                            red += 1.5
                    else:
                        if Piece.queen == False:
                            white += 1.0
                        else:
                            white += 1.5
        if state.isPlayer == RED:
            return red-white
        else:
            return white-red

    def iterativeMiniMax(state, evalFunc = heurestic_function):
        startTime = time.time()
        def minimax_search(state, depth):
            def maxVal(state, depth):
                val = -MaxUtility
                for succ in state.get_successor():
                    val = max(val, minimax_search(succ, depth))
                return val

            def minVal(state, depth):
                val = MaxUtility
                for succ in state.get_successor():
                    val = min(val, minimax_search(succ, depth-1))
                return val

            if state.is_goal_state():
                return state.goal_state_utility()

            if depth <= 0 or time.time() - startTime > MaxTime:
                return state.heurestic_function()

            return maxVal(state, depth) if state.game.turn == state.isPlayer else minVal(state, depth)

        bestMove = None
        for depth in range(1, MaxDepth):
            if time.time() - startTime > MaxTime:
                break
            val = -MaxUtility
            for succ in state.get_successor():
                score = minimax_search(succ, depth)
                if score > val:
                    val, bestMove = score, succ.moves
        return bestMove