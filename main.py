from typing import Tuple
from framework import Alg3D, Board   

class MyAI(Alg3D):
    def get_move(self, board: Board) -> Tuple[int, int]:
        #ここから自由にアルゴリズムを記入
        legal_moves = []
                for x in range(4):
                    for y in range(4):
                        # zが埋まっていなければ合法手
                        for z in range(4):
                            if board[z][y][x] == 0:
                                legal_moves.append((x, y))
                                break
                # ランダムに選択
                return random.choice(legal_moves)
