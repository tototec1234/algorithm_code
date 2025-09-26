from typing import List, Tuple
#from local_driver import Alg3D, Board # ローカル検証用
from framework import Alg3D, Board # 本番用
import math

class MyAI():
    def __init__(self):
        # all possible winning lines
        self.lines = self.generate_lines()
        # ビットボード版勝利パターン
        self.win_patterns_bb = self._generate_win_patterns_bb()
        # check if the game is over
        self.over = False
        self.player = 0
        self.end_value = 0 # 1 if win -1 if lose 0 if
    
    def get_move(
        self,
        board: List[List[List[int]]], # 盤面情報
        player: int, # 先手(黒):1 後手(白):2
        last_move: Tuple[int, int, int] # 直前に置かれた場所(x, y, z)
    ) -> Tuple[int, int]:
        # ビットボード版の実装
        self.player = player
        
        # 配列をビットボードに変換
        black_board, white_board = self._convert_to_bitboard(board)
        
        # 有効手を取得
        legal_moves = self._legal_move_bb(black_board, white_board)
        if not legal_moves:
            return (0, 0)  # フォールバック
        
        print("Legal moves (BB):", legal_moves)
        
        best_score = -math.inf
        best_move = (0, 0)
        
        for action in legal_moves:
            z, y, x = action
            print("Action (BB):", action)
            
            # 勝利手があるかチェック
            new_black, new_white, _ = self._make_move_bb(black_board, white_board, x, y, player)
            if self._check_win_bb(new_black if player == 1 else new_white):
                return (y, x)  # 勝利手を即座に選択
            
            # ビットボード版Alpha-Beta探索
            current = self._alpha_beta_minimax_bb(black_board, white_board, False, 0, 3, 
                                                alpha=-math.inf, beta=math.inf)
            if current > best_score:
                best_score = current
                best_move = (y, x)  # (row, col)形式で返す
        
        return best_move

    def result(self, board, action):
        """
            return the board that result from a move
            board: current board
            move: (x,y,z) where to play
            player: which player is playing
            return new board
        """ 
        board[action[0]][action[1]][action[2]] = self.player
        return board

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

    def is_terminal(self, board):
        """
            check if the game ended
            return 1 if ai win -1 if lose and 0 equal
        """
        enemy = 1 if self.player == 2 else 2
        for line in self.lines:
            if all(board[z][y][x] == self.player for (x,y,z) in line):
                self.over = True
                self.end_value = 1
                break
            elif all(board[z][y][x] == enemy for (x,y,z) in line):
                self.over = True
                self.end_value = -1
                break
        # if board is full
        if all(board[3][y][x] != 0 for x in range(4) for y in range(4)):
            self.over = True
            self.end_value = 0
        return False


    def evaluate(self, board):
        """
            END CONDITION
            return 100 if ai win -100 if lose and 0 equal
        """
        enemy = 1 if self.player == 2 else 2
        score = 0

        if self.over:
            return self.end_value * 100
		# Heuristic scoring
        for line in self.lines:
			# Example line : [(0,0,0), (1,1,1), (2,2,2), (3,3,3)]
			# Example values : [-1, 1, 0, 2]
            values = [board[x][y][z] for (x,y,z) in line]
			
            if values.count(self.player) == 3 and values.count(0) == 1:
                score += 10
            elif values.count(self.player) == 2 and values.count(0) == 2:
                score += 1

            if values.count(enemy) == 3 and values.count(0) == 1:
                score -= 10
            elif values.count(enemy) == 2 and values.count(0) == 2:
                score -= 1

        return score

    def legal_move(self, board):
        """
            use to determine how many legal moves are possible
        """
        action_arr = []

        for plane_i in range(4):
            print("Plane i :", plane_i)
            for row_i in range(4):
                print("Row i :", row_i)
                for space_i in range(4):
                    if board[plane_i][row_i][space_i] == 0 \
                        and (3 == plane_i \
                        or board[plane_i + 1][row_i][space_i] == 0 ):

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
                eval = self.alpha_beta_minimax(self.result(board, action), False, depth + 1, max_depth, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for action in self.legal_move(board):
                eval = self.alpha_beta_minimax(self.result(board, action), True, depth + 1, max_depth, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    # ===== ビットボード基盤関数群 =====
    
    def _convert_to_bitboard(self, board: List[List[List[int]]]) -> Tuple[int, int]:
        """3次元配列をビットボードに変換"""
        black_board = 0
        white_board = 0
        
        for z in range(4):
            for y in range(4):
                for x in range(4):
                    bit_pos = z * 16 + y * 4 + x
                    if board[z][y][x] == 1:  # 黒
                        black_board |= (1 << bit_pos)
                    elif board[z][y][x] == 2:  # 白
                        white_board |= (1 << bit_pos)
        
        return black_board, white_board
    
    def _coord_to_bit(self, x: int, y: int, z: int) -> int:
        """座標をビット位置に変換"""
        return z * 16 + y * 4 + x
    
    def _get_bit(self, board: int, x: int, y: int, z: int) -> bool:
        """指定座標のビットが立っているかチェック"""
        bit_pos = self._coord_to_bit(x, y, z)
        return bool(board & (1 << bit_pos))
    
    def _make_move_bb(self, black_board: int, white_board: int, x: int, y: int, player: int) -> Tuple[int, int, int]:
        """ビットボードに手を打つ（重力ルール適用）"""
        occupied = black_board | white_board
        
        # 下から順に空いている位置を探す
        for z in range(4):
            bit_pos = self._coord_to_bit(x, y, z)
            if not (occupied & (1 << bit_pos)):
                if player == 1:  # 黒
                    return black_board | (1 << bit_pos), white_board, z
                else:  # 白
                    return black_board, white_board | (1 << bit_pos), z
        
        return black_board, white_board, -1  # 置けない場合
    
    def _generate_win_patterns_bb(self) -> List[int]:
        """ビットボード版の勝利パターンを生成"""
        patterns = []
        
        # 元のlinesからビットボードパターンに変換
        for line in self.lines:
            pattern = 0
            for x, y, z in line:
                bit_pos = self._coord_to_bit(x, y, z)
                pattern |= (1 << bit_pos)
            patterns.append(pattern)
        
        return patterns
    
    def _legal_move_bb(self, black_board: int, white_board: int) -> List[Tuple[int, int, int]]:
        """ビットボード版有効手生成"""
        action_arr = []
        occupied = black_board | white_board
        
        for y in range(4):  # row_i
            for x in range(4):  # space_i
                for z in range(4):  # plane_i (下から上へ)
                    bit_pos = self._coord_to_bit(x, y, z)
                    if not (occupied & (1 << bit_pos)):
                        # この位置が空で、かつ重力ルールを満たす
                        if z == 0 or (occupied & (1 << self._coord_to_bit(x, y, z-1))):
                            action_arr.append((z, y, x))  # (plane_i, row_i, space_i)
                            break  # この列でもっとも下の位置のみ
        
        return action_arr
    
    def _is_terminal_bb(self, black_board: int, white_board: int) -> bool:
        """ビットボード版ゲーム終了判定"""
        # 勝者がいるかチェック
        if self._check_win_bb(black_board) or self._check_win_bb(white_board):
            return True
        
        # 盤面が満杯かチェック（最上段がすべて埋まっているか）
        occupied = black_board | white_board
        for y in range(4):
            for x in range(4):
                top_bit = self._coord_to_bit(x, y, 3)  # 最上段(z=3)
                if not (occupied & (1 << top_bit)):
                    return False  # まだ空きがある
        return True  # 満杯
    
    def _check_win_bb(self, board: int) -> bool:
        """ビットボード版勝利判定"""
        for pattern in self.win_patterns_bb:
            if (board & pattern) == pattern:
                return True
        return False
    
    def _evaluate_bb(self, black_board: int, white_board: int) -> int:
        """ビットボード版盤面評価"""
        if self.over:
            return self.end_value * 100
        
        player_board = black_board if self.player == 1 else white_board
        enemy_board = white_board if self.player == 1 else black_board
        
        # 勝利チェック
        if self._check_win_bb(player_board):
            return 100
        if self._check_win_bb(enemy_board):
            return -100
        
        score = 0
        
        # 各勝利パターンでの評価
        for pattern in self.win_patterns_bb:
            player_bits = player_board & pattern
            enemy_bits = enemy_board & pattern
            
            # 相手の石がある場合はスキップ
            if enemy_bits:
                continue
                
            # 自分の石の数をカウント
            player_count = bin(player_bits).count('1')
            
            if player_count == 3:
                score += 10
            elif player_count == 2:
                score += 1
        
        # 相手の脅威を評価
        for pattern in self.win_patterns_bb:
            player_bits = player_board & pattern
            enemy_bits = enemy_board & pattern
            
            # 自分の石がある場合はスキップ
            if player_bits:
                continue
                
            # 相手の石の数をカウント
            enemy_count = bin(enemy_bits).count('1')
            
            if enemy_count == 3:
                score -= 10
            elif enemy_count == 2:
                score -= 1
        
        return score
    
    def _alpha_beta_minimax_bb(self, black_board: int, white_board: int, isMaximiser: bool, 
                              depth: int, max_depth: int, alpha: float, beta: float) -> int:
        """ビットボード版Alpha-Beta探索"""
        if self._is_terminal_bb(black_board, white_board) or depth == max_depth:
            return self._evaluate_bb(black_board, white_board)

        if isMaximiser:
            max_eval = -math.inf
            for action in self._legal_move_bb(black_board, white_board):
                z, y, x = action
                new_black, new_white, _ = self._make_move_bb(black_board, white_board, x, y, self.player)
                eval_score = self._alpha_beta_minimax_bb(new_black, new_white, False, depth + 1, max_depth, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            enemy = 1 if self.player == 2 else 2
            for action in self._legal_move_bb(black_board, white_board):
                z, y, x = action
                new_black, new_white, _ = self._make_move_bb(black_board, white_board, x, y, enemy)
                eval_score = self._alpha_beta_minimax_bb(new_black, new_white, True, depth + 1, max_depth, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval