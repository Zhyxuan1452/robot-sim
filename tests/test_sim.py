"""仿真核心的单元测试。运行：python -m unittest discover -s tests -v"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sim import Sim  # noqa: E402


def build():
    # 起点 (1,1)；右侧 (2,1) 是障碍
    return Sim(width=5, height=5, start=(1, 1), obstacles=[(2, 1)])


class TestSim(unittest.TestCase):
    def test_initial_state(self):
        s = build()
        d = s.to_dict()
        self.assertEqual(d["robot"], {"x": 1, "y": 1})
        self.assertEqual(d["status"], "not_started")
        self.assertEqual(len(d["rounds"]), 0)

    def test_normal_move(self):
        s = build()
        r = s.move("down")
        self.assertTrue(r["ok"])
        self.assertEqual(r["robot"], {"x": 1, "y": 2})
        self.assertEqual(r["reason"], "ok")

    def test_blocked_by_obstacle(self):
        s = build()
        r = s.move("right")
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "blocked")
        self.assertEqual(r["robot"], {"x": 1, "y": 1})  # 位置不变

    def test_out_of_bounds(self):
        s = build()
        r = s.move("up")
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "out_of_bounds")
        self.assertEqual(r["robot"], {"x": 1, "y": 1})

    def test_invalid_direction(self):
        s = build()
        r = s.move("northeast")
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "invalid_direction")

    def test_round_completion(self):
        s = build()
        s.move("down")          # 离开起点
        r = s.move("up")        # 回到起点
        self.assertTrue(r["round_completed"])
        self.assertEqual(len(r["rounds"]), 1)
        self.assertEqual(r["rounds"][0]["round"], 1)
        # 完成后状态回到未出发
        self.assertEqual(s.to_dict()["status"], "not_started")

    def test_staying_at_start_does_not_complete(self):
        s = build()
        s.to_dict()
        s.to_dict()             # 多次读取状态
        self.assertEqual(len(s.rounds), 0)

        s.move("down")
        s.move("up")            # 第 1 轮
        s.to_dict(); s.to_dict()
        self.assertEqual(len(s.rounds), 1)
        # 没有再次离开，直接回到起点不应新增
        s.move("down")
        s.move("up")            # 第 2 轮
        self.assertEqual(len(s.rounds), 2)

    def test_invalid_move_does_not_complete(self):
        s = build()
        s.move("down")          # 离开
        s.move("right")         # (2,2) 可行
        s.move("right")         # (3,2) 可行
        # 制造无效移动：走到边界外
        s.move("down"); s.move("down"); s.move("down")  # (3,4) 边界内
        r = s.move("down")      # (3,5) 越界
        self.assertFalse(r["ok"])
        self.assertFalse(r["round_completed"])
        self.assertEqual(len(s.rounds), 0)


if __name__ == "__main__":
    unittest.main()