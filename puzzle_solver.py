import itertools
import collections
import random

class Node:
    def __init__(self, puzzle, parent=None, action=None):
        self.puzzle = puzzle
        self.parent = parent
        self.action = action
        if parent is not None:
            self.g = parent.g + 1
        else:
            self.g = 0

    @property
    def score(self):
        return self.g + self.h

    @property
    def state(self):
        return str(self)

    @property
    def path(self):
        node, p = self, []
        while node:
            p.append(node)
            node = node.parent
        yield from reversed(p)

    @property
    def solved(self):
        return self.puzzle.solved

    @property
    def actions(self):
        return self.puzzle.actions

    @property
    def h(self):
        return self.puzzle.manhattan

    @property
    def f(self):
        return self.h + self.g

    def __str__(self):
        return str(self.puzzle)

class Solver:
    def __init__(self, start, goal):
        self.start = start
        self.goal = goal

    def solve(self):
        queue = collections.deque([Node(self.start)])
        seen = set()
        seen.add(queue[0].state)
        while queue:
            queue = collections.deque(sorted(list(queue), key=lambda node: node.f))
            node = queue.popleft()
            if node.solved:
                return list(node.path)

            for move, action in node.actions:
                child = Node(move(), node, action)
                if child.state not in seen:
                    queue.appendleft(child)
                    seen.add(child.state)

        return None

class Puzzle:
    def __init__(self, board):
        self.width = len(board[0])
        self.board = board

    @property
    def solved(self):
        goal_state = [[f"/uploads/piece_{i}_{j}.png" for j in range(3)] for i in range(3)]
        goal_state[-1][-1] = 0
        return self.board == goal_state

    @property
    def actions(self):
        def create_move(at, to):
            return lambda: self._move(at, to)

        moves = []
        for i, j in itertools.product(range(self.width), range(self.width)):
            direcs = {'R': (i, j - 1), 'L': (i, j + 1), 'D': (i - 1, j), 'U': (i + 1, j)}
            for action, (r, c) in direcs.items():
                if r >= 0 and c >= 0 and r < self.width and c < self.width and self.board[r][c] == 0:
                    move = create_move((i, j), (r, c)), action
                    moves.append(move)
        return moves

    @property
    def manhattan(self):
        distance = 0
        for i in range(3):
            for j in range(3):
                if self.board[i][j] != 0:
                    try:
                        parts = self.board[i][j].split('_')
                        x = int(parts[1])
                        y = int(parts[2].split('.')[0])
                        distance += abs(x - i) + abs(y - j)
                    except Exception as e:
                        print(f"Error calculating Manhattan distance: {e}")
                        print(f"Board piece: {self.board[i][j]}")
        return distance

    def shuffle(self):
        puzzle = self
        for _ in range(1000):
            puzzle = random.choice(puzzle.actions)[0]()
        return puzzle

    def copy(self):
        board = []
        for row in self.board:
            board.append([x for x in row])
        return Puzzle(board)

    def _move(self, at, to):
        copy = self.copy()
        i, j = at
        r, c = to
        copy.board[i][j], copy.board[r][c] = copy.board[r][c], copy.board[i][j]
        return copy

    def pprint(self):
        for row in self.board:
            print(row)
        print()

    def __str__(self):
        return ''.join(map(str, self))

    def __iter__(self):
        for row in self.board:
            yield from row

