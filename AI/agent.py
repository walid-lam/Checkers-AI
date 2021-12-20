from .constants import MaxUtility, MaxTime, MaxDepth, ROWS, COLS, RED
import time
import copy

class Agent:
    def __init__(self, color, board, redToMove, moves):
        self.color = color
        self.board = board
        self.redToMove = redToMove
        self.moves = moves

    def is_goal_state(self):
        redS, whiteS = False, False
        for row in self.board:
            for cell in row:
                if cell == 'r' or cell == 'R':
                    redS = True
                elif cell == 'w' or cell == 'W':
                    whiteS = True
                if redS and whiteS: return False
        self.isLoserRed = whiteS
        return True

    def goal_state_utility(self):
        return MaxUtility if self.color != self.isLoserRed else -MaxUtility

    def get_successor(self):
        def _get_steps(piece):
            RED_steps = [(-1, -1), (-1, 1)]
            WHITE_steps = [(1, -1), (1, 1)]
            steps = []
            if piece != 'w': steps.extend(RED_steps)
            if piece != 'r': steps.extend(WHITE_steps)
            return steps

        def _generate_move(board, x, y, successors):
            for step in _get_steps(board[x][y]):
                dx, dy = x + step[0], y + step[1]
                if 0 <= dx < ROWS and COLS > dy >= 0  and board[dx][dy] == 0:
                    boardC = copy.deepcopy(board)
                    boardC[x][y], boardC[dx][dy] = 0, boardC[x][y]
                    if dx == 7 or dy == 7:
                        boardC[dx][dy] = boardC[dx][dy].upper()
                    successors.append(Agent(self.color, boardC, not self.redToMove, [(x,y), (dx, dy)]))

        def _generate_jump(board, x, y, moves, successors):
            canJump = True
            for step in _get_steps(board[x][y]):
                dx, dy = x + step[0], y + step[1]
                if dx >= 0 and dx < ROWS and dy >= 0 and dy < COLS and board[dx][dy] != 0 and board[x][y].lower() != board[dx][dy].lower():
                    jx, jy = dx + step[0], dy + step[1]
                    if 0 <= jx < ROWS and COLS > jy >= 0 and board[jx][jy] == 0:
                        board[jx][jy], save = board[x][y], board[dx][dy]
                        board[dx][dy] = board[x][y] = 0
                        previous = board[jx][jy]
                        if jx == 7 or jx == 0:
                            board[jx][jy].upper()
                        moves.append((jx, jy))
                        _generate_jump(board, jx, jy, moves, successors)
                        moves.pop()
                        board[x][y], board[dx][dy], board[jx][jy] = previous, save, 0
                        canJump = False
            if canJump and len(moves) > 1:
                successors.append((Agent(self.color, copy.deepcopy(board), not self.redToMove, copy.deepcopy(moves))))

        player = 'r' if self.redToMove else 'w'
        successors = []

        for i in range(ROWS):
            for j in range(COLS):
                if self.board[i][j] != 0 and self.board[i][j].lower() == player:
                    _generate_jump(self.board, i, j, [(i, j)], successors)
        if len(successors) > 0:
            return successors

        for i in range(ROWS):
            for j in range(COLS):
                if self.board[i][j] != 0 and self.board[i][j].lower() == player:
                    _generate_move(self.board, i, j, successors)
        return successors

    def heurestic_function(state):
        red, white = 0, 0
        for row in state.board:
            for cell in row:
                if cell == 'r': red+=1.0
                elif cell == 'R': red+=1.5
                if cell == 'w': white+=1.0
                elif cell == 'W': white+=1.5
        if state.redToMove == RED:
            return red-white
        else:
            return white-red

    def iterativeMiniMax(self, state):
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

            return maxVal(state, depth) if state.redToMove == self.color else minVal(state, depth)

        bestMove = None
        for depth in range(1, MaxDepth):
            if time.time() - startTime > MaxTime:
                break
            val = -MaxUtility
            for succ in state.get_successor():
                score = minimax_search(succ, depth)
                if score > val:
                    val, bestMove = score, succ.moves
        print(val, bestMove)
        return bestMove