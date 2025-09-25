from typing import List, Tuple
import random  # ← これが必須
# from local_driver import Alg3D, Board   # ローカル検証用
from framework import Alg3D, Board

class MyAI(Alg3D):
    def get_move(
        self,
        board: List[List[List[int]]],
        player: int,
        last_move: Tuple[int, int, int]
    ) -> Tuple[int, int]:

        moves = self._legal_moves_with_z(board)
        if not moves:
            raise RuntimeError("No legal moves available")

        # 1) 自分の即勝ち
        for x,y,_z in moves:
            if self._is_win_after(board, player, x, y):
                return (x, y)

        # 2) 相手の即勝ちをブロック
        opp = 3 - player
        for x,y,z in moves:
            board[z][y][x] = player  # 仮置きして相手の次手をチェック
            their_moves = self._legal_moves_with_z(board)
            must_block = False
            for ox,oy,_oz in their_moves:
                if self._is_win_after(board, opp, ox, oy):
                    must_block = True
                    break
            board[z][y][x] = 0
            if must_block:
                return (x, y)

        # 3) α-β探索（ミニマックス）
        best_score = -self.WIN_SCORE
        best_xy = (moves[0][0], moves[0][1])

        # 移動順を軽く整える（中心優先 + ランダム）
        sx, sy, _ = self._size_xyz(board)
        cx, cy = (sx-1)/2.0, (sy-1)/2.0
        random.shuffle(moves)
        moves.sort(key=lambda m: abs(m[0]-cx)+abs(m[1]-cy))

        for x,y,z in moves:
            board[z][y][x] = player
            if self._is_win(board, player, x, y, z):
                board[z][y][x] = 0
                return (x, y)

            score = self._search(board, self.MAX_DEPTH-1, -self.WIN_SCORE, self.WIN_SCORE, player, 3-player)
            board[z][y][x] = 0

            if score > best_score:
                best_score = score
                best_xy = (x, y)

        return best_xy
