from typing import List, Tuple
#from local_driver import Alg3D, Board # ローカル検証用
# from framework import Alg3D, Board # 本番用
import math

class MyAI():
    def __init__(self):
        # all possible winning lines
        self.lines = self.generate_lines()
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
        # ここにアルゴリズムを書く
        self.player = player
        
        best_score = -math.inf
        best_move = (0, 0)
        legal_moves = self.legal_move(board)
        
        if not legal_moves:
            return (0, 0)  # フォールバック
        
        print("Legal moves :", legal_moves)
        
        for action in legal_moves:
            print("Action :", action)
            
            # 手を適用した新しい盤面を作成
            new_board = self.result(board, action)
            
            # 勝利手があるかチェック
            if self.is_terminal(new_board) and self.end_value == 1:
                return (action[1], action[2])  # (row, col)形式で返す
            
            # 新しい盤面でミニマックス探索を実行
            current = self.alpha_beta_minimax(new_board, False, 0, 3, alpha=-math.inf, beta=math.inf)
            
            if current > best_score:
                best_score = current
                best_move = (action[1], action[2])  # (row, col)形式で返す
        
        return best_move

    def result(self, board, action):
        """
            return the board that result from a move
            board: current board
            move: (plane_i, row_i, space_i) where to play
            player: which player is playing
            return new board (copy)
        """ 
        # ボードのディープコピーを作成して副作用を避ける
        import copy
        new_board = copy.deepcopy(board)
        new_board[action[0]][action[1]][action[2]] = self.player
        return new_board

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
            return True if game is over, False otherwise
            Updates self.end_value: 1 if ai win, -1 if lose, 0 if draw
        """
        # プレイヤーが設定されていない場合はゲーム継続とみなす
        if self.player == 0:
            self.over = False
            return False
            
        enemy = 1 if self.player == 2 else 2
        
        # 勝利判定
        for line in self.lines:
            if all(board[z][y][x] == self.player for (x,y,z) in line):
                self.over = True
                self.end_value = 1
                return True
            elif all(board[z][y][x] == enemy for (x,y,z) in line):
                self.over = True
                self.end_value = -1
                return True
        
        # 盤面が満杯かどうか
        if all(board[3][y][x] != 0 for x in range(4) for y in range(4)):
            self.over = True
            self.end_value = 0
            return True
            
        # ゲーム継続
        self.over = False
        return False


    def evaluate(self, board):
        """
            END CONDITION
            return 100 if ai win -100 if lose and 0 equal
        """
        # プレイヤーが設定されていない場合は0を返す
        if self.player == 0:
            return 0
            
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

        for row_i in range(4):
            for space_i in range(4):
                # 下から上に向かって最初の空きスペースを探す
                for plane_i in range(4):
                    if board[plane_i][row_i][space_i] == 0:
                        # 重力ルール：最下段または下に石がある場合のみ置ける
                        if plane_i == 0 or board[plane_i - 1][row_i][space_i] != 0:
                            action_arr.append((plane_i, row_i, space_i))
                            break  # この列では一番下の空きスペースのみ
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