from typing import List, Tuple
import random  # ← これが必須
from local_driver import Alg3D, Board   # ローカル検証用
# from framework import Alg3D, Board

class MyAI(Alg3D):
    def get_move(
        self,
        board: List[List[List[int]]],
        player: int,
        last_move: Tuple[int, int, int]
    ) -> Tuple[int, int]:
        # 各次元の長さを個別に取得（将来の非立方体にも耐性）
        size_z = len(board)
        size_y = len(board[0]) if size_z > 0 else 0
        size_x = len(board[0][0]) if size_y > 0 else 0

        legal_moves: list[Tuple[int, int]] = []

        # 各 (x, y) 列の最下段から空きを探し、置ける (x, y) を収集
        for x in range(size_x):
            for y in range(size_y):
                for z in range(size_z):
                    if board[z][y][x] == 0:
                        legal_moves.append((x, y))
                        break  # この (x,y) は z が決まったので次へ

        if not legal_moves:
            # フレームワークに「パス」仕様が無い前提で例外化（不正手を返さない）
            raise RuntimeError("No legal moves available")

        # 合法手からランダムに 1 つ選ぶ（z はフレームワーク側で決定）
        return random.choice(legal_moves)
