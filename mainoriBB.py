from typing import List, Tuple
# from local_driver import Alg3D, Board # ローカル検証用
from framework import Alg3D, Board # 本番用
import math

class MyAI(Alg3D):
    def __init__(self):
        # BitBoard representation: 64-bit integers for 4x4x4 board
        self.player1_board = 0
        self.player2_board = 0
        
        # all possible winning lines (precomputed as bitboards)
        self.winning_lines = self.generate_winning_lines()
        # check if the game is over
        self.over = False
        self.player = 0
        self.end_value = 0 # 1 if win -1 if lose 0 if
        
        # Position weights as flattened array (64 positions)
        self.position_weights = self.generate_position_weights()

    def coord_to_bit(self, x: int, y: int, z: int) -> int:
        """Convert 3D coordinates to bit position (0-63)"""
        return x * 16 + y * 4 + z
    
    def bit_to_coord(self, bit_pos: int) -> Tuple[int, int, int]:
        """Convert bit position to 3D coordinates"""
        x = bit_pos // 16
        y = (bit_pos % 16) // 4
        z = bit_pos % 4
        return (x, y, z)
    
    def generate_position_weights(self) -> List[int]:
        """Generate position weights as a flattened array"""
        weights_3d = [
            [  # z = 0
                [3, 4, 4, 3],
                [4, 6, 6, 4],
                [4, 6, 6, 4],
                [3, 4, 4, 3]
            ],
            [  # z = 1
                [4, 6, 6, 4],
                [6, 8, 8, 6],
                [6, 8, 8, 6],
                [4, 6, 6, 4]
            ],
            [  # z = 2
                [4, 6, 6, 4],
                [6, 8, 8, 6],
                [6, 8, 8, 6],
                [4, 6, 6, 4]
            ],
            [  # z = 3
                [3, 4, 4, 3],
                [4, 6, 6, 4],
                [4, 6, 6, 4],
                [3, 4, 4, 3]
            ]
        ]
        
        # Flatten to 64-element array
        flattened = [0] * 64
        for x in range(4):
            for y in range(4):
                for z in range(4):
                    bit_pos = self.coord_to_bit(x, y, z)
                    flattened[bit_pos] = weights_3d[z][x][y]
        return flattened

    def board_to_bitboards(self, board: List[List[List[int]]]) -> Tuple[int, int]:
        """Convert 3D array board to bitboards"""
        player1_board = 0
        player2_board = 0
        
        for x in range(4):
            for y in range(4):
                for z in range(4):
                    cell_value = board[x][y][z]
                    bit_pos = self.coord_to_bit(x, y, z)
                    if cell_value == 1:
                        player1_board |= (1 << bit_pos)
                    elif cell_value == 2:
                        player2_board |= (1 << bit_pos)
        
        return player1_board, player2_board
    
    def get_move(
        self,
        board: List[List[List[int]]], # 盤面情報
        player: int, # 先手(黒):1 後手(白):2
        last_move: Tuple[int, int, int] # 直前に置かれた場所(x, y, z)
    ) -> Tuple[int, int]:
        # ここにアルゴリズムを書く
        self.player = player
        # Convert board to bitboards
        self.player1_board, self.player2_board = self.board_to_bitboards(board)
        
        best_score = -math.inf
        best_move = (0, 0)
        
        for action in self.legal_moves_bitboard():
            self.over = False
            self.end_value = 0
            
            # Create new bitboard state
            new_player1, new_player2 = self.make_move_bitboard(action, True)
            
            current = self.alpha_beta_minimax_bitboard(new_player1, new_player2, False, 0, 9, alpha=-math.inf, beta=math.inf)
            
            if current > best_score:
                best_score = current
                x, y, z = self.bit_to_coord(action)
                best_move = (y, z)  # Return (y, z) as expected by interface
        
        return best_move

    def make_move_bitboard(self, bit_pos: int, is_maximiser: bool = True) -> Tuple[int, int]:
        """Make a move on bitboards and return new state"""
        new_player1 = self.player1_board
        new_player2 = self.player2_board
        
        if is_maximiser:
            if self.player == 1:
                new_player1 |= (1 << bit_pos)
            else:
                new_player2 |= (1 << bit_pos)
        else:
            if self.player == 1:
                new_player2 |= (1 << bit_pos)
            else:
                new_player1 |= (1 << bit_pos)
        
        return new_player1, new_player2

    def legal_moves_bitboard(self) -> List[int]:
        """Get legal moves as bit positions"""
        occupied = self.player1_board | self.player2_board
        legal_moves = []
        
        for bit_pos in range(64):
            if occupied & (1 << bit_pos):
                continue  # Position is occupied
            
            x, y, z = self.bit_to_coord(bit_pos)
            
            # Check if this is a valid gravity move
            if x == 0 or (occupied & (1 << self.coord_to_bit(x-1, y, z))):
                legal_moves.append(bit_pos)
        
        return legal_moves

    def result(self, board, action, isMaximiser=True):
        """
            return the board that result from a move
            board: current board
            move: (x,y,z) where to play
            player: which player is playing
            return new board
        """ 
        # Create a deep copy of the board
        new_board = [[[board[x][y][z] for z in range(4)] for y in range(4)] for x in range(4)]
        new_board[action[0]][action[1]][action[2]] = self.player if isMaximiser else (1 if self.player == 2 else 2)
        return new_board

    def generate_winning_lines(self) -> List[int]:
        """Generate all winning lines as bitboards"""
        lines = []
        rng = range(4)
        
        # Horizontal lines (x direction)
        for z in rng:
            for y in rng:
                line_bits = 0
                for x in rng:
                    bit_pos = self.coord_to_bit(x, y, z)
                    line_bits |= (1 << bit_pos)
                lines.append(line_bits)
        
        # Horizontal lines (y direction)
        for z in rng:
            for x in rng:
                line_bits = 0
                for y in rng:
                    bit_pos = self.coord_to_bit(x, y, z)
                    line_bits |= (1 << bit_pos)
                lines.append(line_bits)
        
        # Vertical lines (z direction)
        for y in rng:
            for x in rng:
                line_bits = 0
                for z in rng:
                    bit_pos = self.coord_to_bit(x, y, z)
                    line_bits |= (1 << bit_pos)
                lines.append(line_bits)
        
        # Diagonal lines in each z-plane
        for z in rng:
            # Main diagonal
            line_bits = 0
            for i in rng:
                bit_pos = self.coord_to_bit(i, i, z)
                line_bits |= (1 << bit_pos)
            lines.append(line_bits)
            
            # Anti diagonal
            line_bits = 0
            for i in rng:
                bit_pos = self.coord_to_bit(i, 3-i, z)
                line_bits |= (1 << bit_pos)
            lines.append(line_bits)
        
        # Diagonal lines in y planes
        for y in rng:
            line_bits = 0
            for i in rng:
                bit_pos = self.coord_to_bit(i, y, i)
                line_bits |= (1 << bit_pos)
            lines.append(line_bits)
            
            line_bits = 0
            for i in rng:
                bit_pos = self.coord_to_bit(i, y, 3-i)
                line_bits |= (1 << bit_pos)
            lines.append(line_bits)
        
        # Diagonal lines in x planes
        for x in rng:
            line_bits = 0
            for i in rng:
                bit_pos = self.coord_to_bit(x, i, i)
                line_bits |= (1 << bit_pos)
            lines.append(line_bits)
            
            line_bits = 0
            for i in rng:
                bit_pos = self.coord_to_bit(x, i, 3-i)
                line_bits |= (1 << bit_pos)
            lines.append(line_bits)
        
        # 3D diagonals
        line_bits = 0
        for i in rng:
            bit_pos = self.coord_to_bit(i, i, i)
            line_bits |= (1 << bit_pos)
        lines.append(line_bits)
        
        line_bits = 0
        for i in rng:
            bit_pos = self.coord_to_bit(i, i, 3-i)
            line_bits |= (1 << bit_pos)
        lines.append(line_bits)
        
        line_bits = 0
        for i in rng:
            bit_pos = self.coord_to_bit(i, 3-i, i)
            line_bits |= (1 << bit_pos)
        lines.append(line_bits)
        
        line_bits = 0
        for i in rng:
            bit_pos = self.coord_to_bit(3-i, i, i)
            line_bits |= (1 << bit_pos)
        lines.append(line_bits)
        
        return lines

    # 旧バージョン（互換性のため保持）- BitBoard版を優先使用
    def generate_lines(self):
        lines = []
        rng = range(4)
        for z in rng:
            for y in rng:
                lines.append([(x,y,z) for x in rng])
        for z in rng:
            for x in rng:
                lines.append([(x,y,z) for y in rng])
        for y in rng:
            for x in rng:
                lines.append([(x,y,z) for z in rng])

        for z in rng:
            lines.append([(i,i,z) for i in rng])
            lines.append([(i,3-i,z) for i in rng])
        for y in rng:
            lines.append([(i,y,i) for i in rng])
            lines.append([(i,y,3-i) for i in rng])
        for x in rng:
            lines.append([(x,i,i) for i in rng])
            lines.append([(x,i,3-i) for i in rng])

        # diagonal
        lines.append([(i,i,i) for i in rng])
        lines.append([(i,i,3-i) for i in rng])
        lines.append([(i,3-i,i) for i in rng])
        lines.append([(3-i,i,i) for i in rng])
        return lines

    def is_terminal_bitboard(self, player1_board: int, player2_board: int) -> bool:
        """Check if game is terminal using bitboards"""
        # Check for wins
        current_player_board = player1_board if self.player == 1 else player2_board
        enemy_board = player2_board if self.player == 1 else player1_board
        
        for line in self.winning_lines:
            if (current_player_board & line) == line:
                self.over = True
                self.end_value = 1
                return True
            elif (enemy_board & line) == line:
                self.over = True
                self.end_value = -1
                return True
        
        # Check if board is full (top plane all occupied)
        top_plane_mask = 0
        for y in range(4):
            for z in range(4):
                top_plane_mask |= (1 << self.coord_to_bit(3, y, z))
        
        if (player1_board | player2_board) & top_plane_mask == top_plane_mask:
            self.over = True
            self.end_value = 0
        
        return self.over

    def evaluate_bitboard(self, player1_board: int, player2_board: int) -> int:
        """Evaluate position using bitboards"""
        if self.over:
            return self.end_value * 1000
        
        score = 0
        current_player_board = player1_board if self.player == 1 else player2_board
        enemy_board = player2_board if self.player == 1 else player1_board
        
        # Evaluate each winning line
        for line in self.winning_lines:
            current_pieces = bin(current_player_board & line).count('1')
            enemy_pieces = bin(enemy_board & line).count('1')
            empty_pieces = 4 - current_pieces - enemy_pieces
            
            # Only evaluate lines that are not blocked by enemy
            if enemy_pieces == 0:
                if current_pieces == 3 and empty_pieces == 1:
                    score += 100
                elif current_pieces == 2 and empty_pieces == 2:
                    score += 10
            
            # Penalty for enemy threats
            if current_pieces == 0:
                if enemy_pieces == 3 and empty_pieces == 1:
                    score -= 100
                elif enemy_pieces == 2 and empty_pieces == 2:
                    score -= 10
        
        # Position weights
        for bit_pos in range(64):
            if current_player_board & (1 << bit_pos):
                score += self.position_weights[bit_pos]
            elif enemy_board & (1 << bit_pos):
                score -= self.position_weights[bit_pos]
        
        return score

    def alpha_beta_minimax_bitboard(self, player1_board: int, player2_board: int, 
                                   is_maximiser: bool, depth: int, max_depth: int, 
                                   alpha: float, beta: float) -> float:
        """Alpha-beta minimax with bitboards"""
        # Temporarily set boards for evaluation
        old_p1, old_p2 = self.player1_board, self.player2_board
        self.player1_board, self.player2_board = player1_board, player2_board
        
        if self.is_terminal_bitboard(player1_board, player2_board) or depth == max_depth:
            result = self.evaluate_bitboard(player1_board, player2_board)
            self.player1_board, self.player2_board = old_p1, old_p2
            return result
        
        occupied = player1_board | player2_board
        legal_moves = []
        
        for bit_pos in range(64):
            if occupied & (1 << bit_pos):
                continue
            x, y, z = self.bit_to_coord(bit_pos)
            if x == 0 or (occupied & (1 << self.coord_to_bit(x-1, y, z))):
                legal_moves.append(bit_pos)
        
        if is_maximiser:
            max_eval = -math.inf
            for bit_pos in legal_moves:
                new_p1, new_p2 = player1_board, player2_board
                if self.player == 1:
                    new_p1 |= (1 << bit_pos)
                else:
                    new_p2 |= (1 << bit_pos)
                
                eval_score = self.alpha_beta_minimax_bitboard(new_p1, new_p2, False, depth + 1, max_depth, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            self.player1_board, self.player2_board = old_p1, old_p2
            return max_eval
        else:
            min_eval = math.inf
            for bit_pos in legal_moves:
                new_p1, new_p2 = player1_board, player2_board
                if self.player == 1:
                    new_p2 |= (1 << bit_pos)
                else:
                    new_p1 |= (1 << bit_pos)
                
                eval_score = self.alpha_beta_minimax_bitboard(new_p1, new_p2, True, depth + 1, max_depth, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            self.player1_board, self.player2_board = old_p1, old_p2
            return min_eval

    def is_terminal(self, board):
        """
            check if the game ended
            return 1 if ai win -1 if lose and 0 equal
        """
        enemy = 1 if self.player == 2 else 2
        for line in self.lines:


            if all(board[x][y][z] == self.player for (x,y,z) in line):
                self.over = True
                self.end_value = 1
                # print("You WIN")

                return True
            elif all(board[x][y][z] == enemy for (x,y,z) in line):
                self.over = True
                self.end_value = -1
                # print("You lose")
                return True
        # if board is full
        if all(board[3][y][x] != 0 for x in range(4) for y in range(4)):
            self.over = True
            self.end_value = 0
            # print("Draw")
        return self.over


    def evaluate(self, board):
        """
            END CONDITION
            return 100 if ai win -100 if lose and 0 equal
        """
        enemy = 1 if self.player == 2 else 2
        score = 0

        if self.over:
            return self.end_value * 1000
        # Heuristic scoring
        for line in self.lines:
			# Example line : [(0,0,0), (1,1,1), (2,2,2), (3,3,3)]
			# Example values : [-1, 1, 0, 2]
            values = [board[x][y][z] for (x,y,z) in line]
			
            if values.count(self.player) == 3 and values.count(0) == 1:
                score += 100
            elif values.count(self.player) == 2 and values.count(0) == 2:
                score += 10

            if values.count(enemy) == 3 and values.count(0) == 1:
                score -= 100
            elif values.count(enemy) == 2 and values.count(0) == 2:
                score -= 10

        # Position Weight
        for x in range(4):
            for y in range(4):
                for z in range(4):
                    if board[x][y][z] == self.player:
                        score += self.position_weights[z][x][y]
                    elif board[x][y][z] == enemy:
                        score -= self.position_weights[z][x][y]

        return score

    def legal_move(self, board):
        """
            use to determine how many legal moves are possible
        """
        action_arr = []

        for plane_i in range(4):
            # print("Plane i :", plane_i)
            for row_i in range(4):
                # print("Row i :", row_i)
                for space_i in range(4):
                    if board[plane_i][row_i][space_i] == 0 \
                        and (plane_i == 0 \
                        or board[plane_i - 1][row_i][space_i] > 0 ):

                        action_arr.append((plane_i, row_i, space_i))
        return action_arr

    def alpha_beta_minimax(self, board, isMaximiser, depth, max_depth, alpha, beta):
        """
            isMaximiser: is the computer turn to check in the three
            depth: how far in the three you are
            max_deth: maximmum depth
        """
        if self.is_terminal(board) or depth == max_depth:
            return self.evaluate(board)

        if isMaximiser:
            max_eval = -math.inf
            for action in self.legal_move(board):
                new_board = self.result(board, action, isMaximiser=True)
                eval = self.alpha_beta_minimax(new_board, False, depth + 1, max_depth, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for action in self.legal_move(board):
                new_board = self.result(board, action, isMaximiser=False)
                eval = self.alpha_beta_minimax(new_board, True, depth + 1, max_depth, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

