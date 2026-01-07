import numpy as np

# 基本參數
G = 1.0
DT = 0.01
STEPS = 3000

# 畫面範圍
X_LIM = (-3, 3)
Y_LIM = (-3, 3)

# 天體設定（質量、初始位置、初始速度）
BODIES = [
    {
        "mass": 1.0,
        "position": np.array([-1.0, 0.0]),
        "velocity": np.array([0.3, 0.4])
    },
    {
        "mass": 1.0,
        "position": np.array([1.0, 0.0]),
        "velocity": np.array([-0.3, 0.4])
    },
    {
        "mass": 1.0,
        "position": np.array([0.0, 1.5]),
        "velocity": np.array([0.0, -0.6])
    }
]
