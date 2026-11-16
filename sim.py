"""仿真核心：地图、机器人、移动规则、巡检轮次。

这一层是唯一判断"能不能进入某个格子"的地方。
前端和 API 只负责转发与展示。
"""
import time

DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


class Sim:
    def __init__(self, width=10, height=10, start=(1, 1), obstacles=None):
        self.w = width
        self.h = height
        self.start = (start[0], start[1])
        self.obstacles = set((x, y) for x, y in (obstacles or []))
        self.pos = [start[0], start[1]]
        self.left_start = False   # 是否曾经成功离开过起点
        self.rounds = []

    # ---------- 查询 ----------
    def _pos(self):
        return {"robot": {"x": self.pos[0], "y": self.pos[1]}}

    def to_dict(self):
        return {
            "map": {
                "width": self.w,
                "height": self.h,
                "obstacles": sorted([list(o) for o in self.obstacles]),
            },
            "robot": {"x": self.pos[0], "y": self.pos[1]},
            "start": {"x": self.start[0], "y": self.start[1]},
            "status": "away" if self.left_start else "not_started",
            "rounds": self.rounds,
        }

    # ---------- 行为 ----------
    def move(self, direction):
        if direction not in DIRS:
            return {"ok": False, "reason": "invalid_direction",
                    "round_completed": False, **self._pos()}

        dx, dy = DIRS[direction]
        nx, ny = self.pos[0] + dx, self.pos[1] + dy

        # 边界
        if not (0 <= nx < self.w and 0 <= ny < self.h):
            return {"ok": False, "reason": "out_of_bounds",
                    "round_completed": False, **self._pos()}

        # 障碍物
        if (nx, ny) in self.obstacles:
            return {"ok": False, "reason": "blocked",
                    "round_completed": False, **self._pos()}

        self.pos = [nx, ny]
        completed = False

        if (nx, ny) != self.start:
            # 成功离开起点
            self.left_start = True
        elif self.left_start:
            # 曾经离开过，现在回到起点 => 完成一轮
            self.left_start = False
            self.rounds.append({
                "round": len(self.rounds) + 1,
                "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            })
            completed = True

        return {"ok": True, "reason": "ok", "round_completed": completed,
                **self._pos(), "rounds": self.rounds}