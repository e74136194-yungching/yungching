# -*- coding: utf-8 -*-
import rhinoscriptsyntax as rs
import math
import sys

# ------------------------------------------------------------------
# Figure-8 Braided Sculpture (Rhino 8 Compatible - Fixed Loft Error)
# ------------------------------------------------------------------

def create_braided_sculpture_loft():
    """
    計算 Figure-8 軌道，並沿著軌道創建三個互相編織的曲面實體。
    """
    # 設置輸出訊息編碼以確保中文顯示正常
    # 這行程式碼主要針對舊版 Python (Rhino 5/6 使用的 IronPython)
    if sys.version_info.major < 3:
        try:
            reload(sys)
            sys.setdefaultencoding('utf-8')
        except NameError:
            pass # 忽略 Python 3 環境下的錯誤

    rs.EnableRedraw(False)
    
    print("--- 1. 初始化三體 Figure-8 軌道參數 ---")
    
    # --- 物理與初始條件 (基於 Figure-8 週期軌道) ---
    # 這些精確的參數能確保軌道完美閉合
    p1_x = 0.97000436
    p1_y = -0.24308753
    v1_x = 0.46620368
    v1_y = 0.43236573
    
    # 由於是等質量三體，且總質心不動 (0,0,0)，V3 必須抵銷 V1 和 V2
    v3_x = -2 * v1_x
    v3_y = -2 * v1_y
    
    # --- 模擬與幾何設定 ---
    TOTAL_STEPS = 632  # 完成一個完美迴圈所需的總步數
    DT = 0.01          # 模擬時間步長
    SCALE = 40.0       # 放大比例
    
    # 實體結構設定
    SECTION_RADIUS = 1.8 # 截面圓的半徑
    DENSITY = 2          # 每 N 步繪製一個截面圓 (越低越密)
    
    # 編織效果設定
    TWIST_RATE = 0.15    # 沿著路徑的旋轉速度
    BRAID_WIDTH = 2.5    # 編織的寬度 (實體之間的間隔距離)
    
    # 初始狀態 (X, Y, Z)
    bodies_pos = [
        [p1_x, p1_y, 0],       # Body 1
        [-p1_x, -p1_y, 0],     # Body 2
        [0, 0, 0]              # Body 3
    ]
    # 初始速度 (Vx, Vy, Vz)
    bodies_vel = [
        [v1_x, v1_y, 0],
        [v1_x, v1_y, 0],
        [v3_x, v3_y, 0]
    ]
    
    core_path = []
    
    print("--- 2. 計算 Figure-8 軌跡 (歐拉積分) ---")
    
    # Physics Loop (歐拉積分計算)
    for t in range(TOTAL_STEPS):
        forces = [[0.0, 0.0, 0.0] for _ in range(3)]
        
        # 1. 計算引力 (F = G*M*M / r^2, 這裡 G=M=1)
        for i in range(3):
            for j in range(3):
                if i == j: continue
                
                dx = bodies_pos[j][0] - bodies_pos[i][0]
                dy = bodies_pos[j][1] - bodies_pos[i][1]
                dz = bodies_pos[j][2] - bodies_pos[i][2]
                
                dist_sq = dx*dx + dy*dy + dz*dz
                dist = math.sqrt(dist_sq)
                
                f = 1.0 / dist_sq
                
                # 累加受到的分力 Fx = F * (dx/dist)
                forces[i][0] += f * (dx/dist)
                forces[i][1] += f * (dy/dist)
                forces[i][2] += f * (dz/dist)
        
        # 2. 更新速度與位置 (歐拉法)
        for i in range(3):
            # 速度更新: v = v + a * DT (a=F, M=1)
            bodies_vel[i][0] += forces[i][0] * DT
            bodies_vel[i][1] += forces[i][1] * DT
            bodies_vel[i][2] += forces[i][2] * DT
            
            # 位置更新: r = r + v * DT
            bodies_pos[i][0] += bodies_vel[i][0] * DT
            bodies_pos[i][1] += bodies_vel[i][1] * DT
            bodies_pos[i][2] += bodies_vel[i][2] * DT
            
        # 3. 記錄核心路徑 (取 Body 1 的位置)
        x = bodies_pos[0][0]
        y = bodies_pos[0][1]
        
        # 增加 Z 軸波動，創造莫比烏斯環般的扭曲效果
        # 讓 Z 軸波動的週期與 TOTAL_STEPS 匹配 (產生一個完整週期)
        z = math.sin(2 * math.pi * t / TOTAL_STEPS) * 0.5 
        
        core_path.append( (x*SCALE, y*SCALE, z*SCALE) )

    print("--- 3. 幾何處理：創建 Layer 與中心曲線 ---")
    
    # 創建 Layer 設置
    layer_names = ["Orbit_Red", "Orbit_Green", "Orbit_Blue"]
    layer_colors = [(220, 20, 20), (20, 220, 20), (20, 20, 220)]
    
    for name, color in zip(layer_names, layer_colors):
        if not rs.IsLayer(name):
            rs.AddLayer(name, color)

    # 使用記錄的點創建中心曲線
    temp_crv = rs.AddInterpCurve(core_path, degree=3)
    if not temp_crv: 
        print("錯誤: 無法建立核心曲線。")
        rs.EnableRedraw(True)
        return
    
    crv_domain = rs.CurveDomain(temp_crv)
    
    print("--- 4. 生成截面圓並準備放樣 ---")
    
    # 收集每條編織軌道上的圓形 (用作放樣截面)
    crv_collections = [[], [], []] 
    
    total_len = len(core_path)
    if total_len < 2: 
        rs.DeleteObject(temp_crv)
        return
    
    # 計算步長，確保每段距離的圓形密度一致
    step_size = (crv_domain[1] - crv_domain[0]) / (total_len / DENSITY)
    
    current_t = crv_domain[0]
    counter = 0
    
    while current_t <= crv_domain[1] and counter < total_len:
        # 獲取垂直於曲線方向的平面 (Frame)
        plane = rs.CurvePerpFrame(temp_crv, current_t)
        
        # 計算旋轉角度 (加入時間變化率來實現編織)
        rotation_base = counter * TWIST_RATE
        
        # 為 3 個軌道創建 3 個偏移圓
        for k in range(3):
            # 120 度分離 (2 * PI / 3)
            angle = rotation_base + (k * (2 * math.pi / 3))
            
            # 計算偏移向量 (在垂直平面上)
            vec_u = rs.VectorScale(plane.XAxis, math.cos(angle) * BRAID_WIDTH)
            vec_v = rs.VectorScale(plane.YAxis, math.sin(angle) * BRAID_WIDTH)
            
            # 最終 3D 圓心位置
            center_point = rs.PointAdd(plane.Origin, rs.VectorAdd(vec_u, vec_v))
            
            # 創建圓形 (截面)
            circle = rs.AddCircle(center_point, SECTION_RADIUS) 
            
            # 將圓形對齊到 CurvePerpFrame 提供的平面上
            if circle:
                # 1. 旋轉圓形使其與平面方向一致 (從 WorldXYPlane 轉換到新的 Plane)
                transform = rs.XformChangeBasis(rs.WorldXYPlane(), plane)
                rs.TransformObject(circle, transform)
                
                # 2. 存儲圓形供放樣使用
                crv_collections[k].append(circle)
                
        current_t += step_size
        counter += 1

    print("--- 5. 放樣 (Loft) 創建實體曲面 ---")
    
    # 進行放樣
    loft_surfaces = []
    for k in range(3):
        rs.CurrentLayer(layer_names[k])
        
        # **錯誤修正**：使用整數代碼 0 (Normal)，而非字串 'Normal'
        # 0 (Normal) 類型適合這種結構性模型
        loft = rs.AddLoftSrf(crv_collections[k], loft_type=0, closed=True)
        
        if loft:
            loft_surfaces.extend(loft)
        
        # 清理中間步驟產生的圓形物件
        rs.DeleteObjects(crv_collections[k])

    print("--- 6. 清理與完成 ---")
    
    # 清理臨時曲線
    rs.DeleteObject(temp_crv)
    
    rs.EnableRedraw(True)
    rs.ZoomExtents()
    print("完成。三體 Figure-8 編織實體雕塑已創建。")

if __name__ == "__main__":
    create_braided_sculpture_loft()
