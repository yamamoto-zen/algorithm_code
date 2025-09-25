from typing import Tuple
from framework import Alg3D, Board   

class MyAI(Alg3D):
    def get_move(self, board: Board) -> Tuple[int, int]:
        #ここから自由にアルゴリズムを記入
        legal_moves = []
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
