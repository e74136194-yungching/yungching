import numpy as np
import matplotlib.pyplot as plt

# --- 三體引力參數 ---
G = 1.0  # 引力常數

# 初始質量
m1, m2, m3 = 1.0, 1.0, 1.0

# 初始位置 (可改)
r1 = np.array([0.5, 0.0])
r2 = np.array([-0.5, 0.0])
r3 = np.array([0.0, 0.8])

# 初始速度 (可改)
v1 = np.array([0.0, 1.0])
v2 = np.array([0.0, -1.0])
v3 = np.array([-1.0, 0.0])

# 用來存軌跡
r1_list, r2_list, r3_list = [], [], []

# --- 引力加速度 ---
def acceleration(r, ra, m):
    diff = ra - r
    dist3 = np.linalg.norm(diff)**3
    return G * m * diff / dist3

# --- 時間迭代參數 ---
dt = 0.001
steps = 20000   # 可改（越大越久）

# --- 主迴圈 ---
for _ in range(steps):
    # 計算三體間加速度
    a1 = acceleration(r1, r2, m2) + acceleration(r1, r3, m3)
    a2 = acceleration(r2, r1, m1) + acceleration(r2, r3, m3)
    a3 = acceleration(r3, r1, m1) + acceleration(r3, r2, m2)

    # 更新速度
    v1 += a1 * dt
    v2 += a2 * dt
    v3 += a3 * dt

    # 更新位置
    r1 += v1 * dt
    r2 += v2 * dt
    r3 += v3 * dt

    # 保存軌跡
    r1_list.append(r1.copy())
    r2_list.append(r2.copy())
    r3_list.append(r3.copy())

# --- 畫圖 ---
r1_list, r2_list, r3_list = np.array(r1_list), np.array(r2_list), np.array(r3_list)

plt.plot(r1_list[:,0], r1_list[:,1], label="Body 1")
plt.plot(r2_list[:,0], r2_list[:,1], label="Body 2")
plt.plot(r3_list[:,0], r3_list[:,1], label="Body 3")
plt.legend()
plt.gca().set_aspect('equal', 'box')
plt.title("Three-Body Simulation")
plt.show()

