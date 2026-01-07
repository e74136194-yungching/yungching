import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv

from config import *
from physics import Body, ThreeBodySystem

# 建立天體
bodies = [
    Body(b["mass"], b["position"], b["velocity"])
    for b in BODIES
]

system = ThreeBodySystem(bodies, G)

# ====================
# Matplotlib 設定
# ====================
fig, ax = plt.subplots()
ax.set_xlim(*X_LIM)
ax.set_ylim(*Y_LIM)
ax.set_aspect("equal")

points, = ax.plot([], [], "o")
trails = [ax.plot([], [], "-", alpha=0.6)[0] for _ in bodies]

# ====================
# 更新函式
# ====================
def update(frame):
    system.step(DT)

    xs = [b.r[0] for b in bodies]
    ys = [b.r[1] for b in bodies]
    points.set_data(xs, ys)

    for i, body in enumerate(bodies):
        trail = body.trail[-300:]  # 限制軌跡長度
        if trail:
            x, y = zip(*trail)
            trails[i].set_data(x, y)

    return points, *trails

ani = FuncAnimation(fig, update, frames=STEPS, interval=20)
plt.show()

# ====================
# 輸出軌跡（給 Rhino / Grasshopper）
# ====================
with open("trajectories.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["body", "x", "y"])

    for i, body in enumerate(bodies):
        for p in body.trail:
            writer.writerow([i, p[0], p[1]])

print("Trajectory saved to trajectories.csv")
