from typing import List, Tuple
#rom local_driver import Alg3D, Board   # ローカル検証用
from framework import Alg3D, Board

class MyAI(Alg3D):
    def get_move(
        self,
        board: List[List[List[int]]],
        player: int,
        last_move: Tuple[int, int, int]:
        # ここにアルゴリズムを書く        legal_moves = []
        size = len(board)  # たぶん 4

        # (x, y) を走査して、まだ高さ z に空きがあれば合法手に追加
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    if board[z][y][x] == 0:  # 空きマス
                        legal_moves.append((x, y))
                        break  # 一番下(zが小さい方)に置けるので次のyへ

        # 万が一置ける場所がない場合は左上に置く（安全策）
        if not legal_moves:
            return (0, 0)

        # ランダムに返す
        return random.choice(legal_moves)
