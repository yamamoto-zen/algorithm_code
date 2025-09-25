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
    ):
        legal_moves = []
        size = len(board)  # たぶん 4 (z, y, x) の順でアクセスする設計想定

        # 各 (x, y) 列の最下段から上に向かって空きを探して、置ける (x, y) を収集
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    if board[z][y][x] == 0:  # 空きマス
                        legal_moves.append((x, y))
                        break  # その列の一番下に置けることが分かったので次の (x, y) へ

        # 置ける場所がない場合のフェイルセーフ
        if not legal_moves:
            return (0, 0)

        # 合法手からランダムに1つ選択
        return random.choice(legal_moves)
