from typing import List, Tuple, Iterable
import random  # 必須要件
from framework import Alg3D, Board
# from local_driver import Alg3D, Board  # ローカル検証用

class MyAI(Alg3D):
    # チューニング
    MAX_DEPTH = 4
    WIN_SCORE = 10_000_000
    LINE_WEIGHTS = (0, 1, 10, 1000, WIN_SCORE)  # n=0..4

    def __init__(self):
        super().__init__()
        self._lines_cache = None  # すべての勝ちライン（盤サイズごとにキャッシュ）

    # ========= ユーティリティ =========
    @staticmethod
    def _size_xyz(board: List[List[List[int]]]) -> Tuple[int, int, int]:
        sz = len(board)
        sy = len(board[0]) if sz else 0
        sx = len(board[0][0]) if sy else 0
        return sx, sy, sz

    @staticmethod
    def _landing_z(board, x, y) -> int:
        """(x,y) の列で最も低い空き z を返す。無ければ -1。"""
        sz = len(board)
        for z in range(sz):
            if board[z][y][x] == 0:
                return z
        return -1

    def _all_winning_lines(self, sx: int, sy: int, sz: int) -> List[List[Tuple[int,int,int]]]:
        """(0..sx-1, 0..sy-1, 0..sz-1) 上の4連ラインを全列挙。サイズごとに一度だけ生成。"""
        key = (sx, sy, sz)
        if self._lines_cache and self._lines_cache[0] == key:
            return self._lines_cache[1]

        dirs = []
        # 軸方向
        dirs += [(1,0,0), (0,1,0), (0,0,1)]
        # 面対角
        dirs += [(1,1,0), (1,-1,0), (1,0,1), (1,0,-1), (0,1,1), (0,1,-1)]
        # 空間対角
        dirs += [(1,1,1), (1,1,-1), (1,-1,1), (1,-1,-1)]

        lines: List[List[Tuple[int,int,int]]] = []
        for dx, dy, dz in dirs:
            for x in range(sx):
                for y in range(sy):
                    for z in range(sz):
                        x2 = x + (4-1)*dx
                        y2 = y + (4-1)*dy
                        z2 = z + (4-1)*dz
                        if 0 <= x2 < sx and 0 <= y2 < sy and 0 <= z2 < sz:
                            line = [(x + k*dx, y + k*dy, z + k*dz) for k in range(4)]
                            lines.append(line)

        self._lines_cache = (key, lines)
        return lines

    def _is_win_after(self, board, player: int, x: int, y: int) -> bool:
        """(x,y) に置いた直後に勝っているか（z を自動決定）"""
        z = self._landing_z(board, x, y)
        if z < 0:
            return False
        board[z][y][x] = player
        won = self._is_win(board, player, x, y, z)
        board[z][y][x] = 0
        return won

    def _is_win(self, board, player: int, x: int, y: int, z: int) -> bool:
        """最後に置いた (x,y,z) を通る4連があるかチェック。"""
        sx, sy, sz = self._size_xyz(board)
        dirs = [
            (1,0,0),(0,1,0),(0,0,1),
            (1,1,0),(1,-1,0),(1,0,1),(1,0,-1),(0,1,1),(0,1,-1),
            (1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1)
        ]
        for dx,dy,dz in dirs:
            cnt = 1
            # 正方向
            xx,yy,zz = x+dx, y+dy, z+dz
            while 0<=xx<sx and 0<=yy<sy and 0<=zz<sz and board[zz][yy][xx]==player:
                cnt += 1; xx+=dx; yy+=dy; zz+=dz
            # 逆方向
            xx,yy,zz = x-dx, y-dy, z-dz
            while 0<=xx<sx and 0<=yy<sy and 0<=zz<sz and board[zz][yy][xx]==player:
                cnt += 1; xx-=dx; yy-=dy; zz-=dz
            if cnt >= 4:
                return True
        return False

    def _legal_moves_with_z(self, board) -> List[Tuple[int,int,int]]:
        sx, sy, sz = self._size_xyz(board)
        moves = []
        for x in range(sx):
            for y in range(sy):
                z = self._landing_z(board, x, y)
                if z >= 0:
                    moves.append((x, y, z))
        return moves

    def _evaluate(self, board, me: int) -> int:
        """ライン合算の静的評価（自分高い＝プラス）。"""
        sx, sy, sz = self._size_xyz(board)
        lines = self._all_winning_lines(sx, sy, sz)
        total = 0
        opp = 3 - me  # 1/2 プレイヤ切替

        for line in lines:
            myc = 0; opc = 0
            for x,y,z in line:
                v = board[z][y][x]
                if v == me: myc += 1
                elif v == opp: opc += 1
            if myc and opc:
                continue  # 相殺（両者含むラインは無効）
            if myc:
                total += self.LINE_WEIGHTS[myc]
            elif opc:
                total -= self.LINE_WEIGHTS[opc]
        return total

    # ========= α-β探索 =========
    def _search(self, board, depth: int, alpha: int, beta: int, me: int, to_move: int) -> int:
        # ターミナル：勝敗 or 深さ尽き
        moves = self._legal_moves_with_z(board)
        if not moves:
            return 0  # 引き分け
        if depth == 0:
            return self._evaluate(board, me)

        # 即勝ち優先で順序付け（中心寄り + ランダム微調整）
        sx, sy, _ = self._size_xyz(board)
        cx, cy = (sx-1)/2.0, (sy-1)/2.0
        random.shuffle(moves)  # 同点時の多様性
        moves.sort(key=lambda m: abs(m[0]-cx)+abs(m[1]-cy))

        best = -self.WIN_SCORE if to_move == me else self.WIN_SCORE

        for x,y,z in moves:
            board[z][y][x] = to_move

            # 直後勝ちなら即スコア
            if self._is_win(board, to_move, x, y, z):
                score = self.WIN_SCORE if to_move == me else -self.WIN_SCORE
            else:
                score = self._search(board, depth-1, alpha, beta, me, 3-to_move)

            board[z][y][x] = 0

            if to_move == me:
                if score > best: best = score
                if best > alpha: alpha = best
                if alpha >= beta:  # β刈り
                    break
            else:
                if score < best: best = score
                if best < beta: beta = best
                if alpha >= beta:
                    break
        return best

    # ========= メイン入口 =========
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
