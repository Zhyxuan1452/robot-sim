# 智能巡检机器人 · 二维仿真

基于 Web 的二维网格巡检仿真：用网页按钮（或方向键）控制机器人逐格移动，
遇到障碍物或地图边界时留在原位并返回受阻原因；机器人成功离开起点后再返回，
完成一轮巡检并留下记录。

## 在线演示

> 待公布：公网部署完成后，培训工作组会提供演示域名，届时补充到这里。

`（待补充）https://...`

## 镜像地址

```
docker.io/zhyxuan1452/robot-sim:latest
```

一键运行：

```bash
docker run -d -p 8080:8080 --name robot-sim zhyxuan1452/robot-sim:latest
```

打开 <http://localhost:8080>。

停止并清理：

```bash
docker stop robot-sim && docker rm robot-sim
```

## 快速开始（本地开发）

### 方式一：Docker Compose

```bash
docker compose up --build -d
```

### 方式二：本地 Python

```bash
pip install -r requirements.txt
python app.py
```

## 使用说明

1. 页面左侧是 10×10 地图，深灰色方块是障碍物，虚线框是**起点**，蓝色圆点是机器人。
2. 用方向键或右侧「上/下/左/右」按钮移动，每按一次走一格。
3. 撞到障碍物或地图边界：位置不变，页面提示「移动受阻」。
4. 离开起点后再次回到起点：**完成一轮**，右下角记录列表新增「第 N 轮 + 完成时间」。
5. 停在起点不动、刷新页面、无效移动，都不会重复计数。

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/state` | 返回地图、机器人位置、起点、状态、轮次记录 |
| POST | `/api/move` | 请求体 `{"dir":"up|down|left|right"}`，返回是否成功、原因、位置、是否完成一轮 |
| GET | `/health` | 健康检查，返回 `{"status":"ok"}` |

`/api/move` 返回示例：

```json
{"ok": false, "reason": "blocked", "round_completed": false, "robot": {"x": 1, "y": 1}}
```

`reason` 取值：`ok` / `blocked` / `out_of_bounds` / `invalid_direction`。

## 架构

```
浏览器（Canvas 渲染 + 按钮）
        │  POST /api/move
        ▼
   app.py（Flask 路由，只转发）
        │  调用
        ▼
   sim.py（地图 + 机器人 + 移动规则 + 轮次状态机）
```

**约定**：能不能进入某个格子，只由 `sim.py` 判断；前端只渲染后端返回的状态。
初始版本状态保存在内存中，进程重启后轮次记录会清空。

## 目录结构

```
robot-sim/
├── app.py                       # HTTP 层
├── sim.py                       # 仿真核心（唯一规则来源）
├── static/index.html            # 前端页面
├── tests/test_sim.py            # 单元测试
├── docs/需求.md                  # 需求与验收标准
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml     # 测试 + 构建检查
├── .github/workflows/publish.yml# 构建并推送到 Docker Hub
└── README.md
```

## 测试

```bash
python -m unittest discover -s tests -v
```

## CI / CD

- `ci`：每次推送运行单元测试，并构建镜像、启动容器做健康检查
- `publish`：推送 `main` 后自动构建并发布镜像到 Docker Hub

## 已知限制

- 状态保存在内存，重启即丢失。
- 单实例部署，不支持多用户各自独立的机器人状态。
- 二维仿真，未接入真实机器人。