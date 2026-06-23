import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from tqdm import tqdm
from solver import WaveSolver2D
import config

MAP_APARTMENT = """
########################
#      =       =       #
#      =       =       #
#      =       =       #
#   ====   =====   ====#
#                      #
#                      #
#                      -
#                      -
########################
"""

# MẪU 2: NHÀ ỐNG ĐẶC TRƯNG VIỆT NAM
MAP_TUBE_HOUSE = """
########################
#      =       =       #
#      =       =       #
#==   ====   =====   ==#
#                      #
#===  ====   =====   ==#
#      =       =       #
#      =       =       #
#      =       =       #
########################
"""

# MẪU 3: VĂN PHÒNG LÀM VIỆC HIỆN ĐẠI
MAP_OFFICE = """
########################
#      =               -
#      =   ---------   -
#      =   -       -   #
#      =   -       -   #
#===  ==   -       -   #
#          ---------   #
#                      #
#                      #
########################
"""

# MẪU 4: TÒA NHÀ CÓ LÕI THANG MÁY
MAP_ELEVATOR_CORE = """
########################
-     =          =     -
-     =          =     -
-  ====  ######  =     -
#        ######        #
#        ######        #
#  ====  ######        #
-     =                -
-     =                -
########################
"""

MATERIALS = {
    ' ': (1.0, 1.0),   # Không khí
    '#': (0.0, 0.0),   # Bê tông/Kim loại
    '=': (0.85, 0.6),  # Tường gạch
    '-': (0.95, 0.8)   # Cửa kính/Gỗ
}

def build_room_from_ascii(solver, ascii_map):
    """Đọc bản đồ ký tự và sinh ra 2 ma trận vật lý (Damping và Velocity C)"""
    lines = [line for line in ascii_map.strip().split('\n') if line.strip()]
    grid_y = len(lines)
    grid_x = max(len(line) for line in lines)
    
    block_h = solver.ny // grid_y
    block_w = solver.nx // grid_x
    
    # Create map
    solver.damping_map.fill(MATERIALS[' '][0])
    solver.c_map.fill(MATERIALS[' '][1])

    for i, row in enumerate(lines):
        for j, char in enumerate(row):
            if char == ' ': 
                continue
                
            y_start = i * block_h
            y_end = (i + 1) * block_h if i < grid_y - 1 else solver.ny
            x_start = j * block_w
            x_end = (j + 1) * block_w if j < grid_x - 1 else solver.nx
            
            if char in MATERIALS:
                damp, c_vel = MATERIALS[char]
                solver.damping_map[y_start:y_end, x_start:x_end] = damp
                solver.c_map[y_start:y_end, x_start:x_end] = c_vel
                
def run_optimization(map_choice):
    """Tính toán dữ liệu cho 1 bản đồ cụ thể"""
    solver = WaveSolver2D(config.NX, config.NY, config.DX, config.DY, config.DT)
    
    map_dict = {1: MAP_APARTMENT, 2: MAP_TUBE_HOUSE, 3: MAP_OFFICE, 4: MAP_ELEVATOR_CORE}
    selected_map = map_dict.get(map_choice, MAP_APARTMENT)
    
    build_room_from_ascii(solver, selected_map)

    # GRID SEARCH 
    candidate_positions = []
    for y in range(config.ROUTER_SEARCH_STEP, config.NY, config.ROUTER_SEARCH_STEP):
        for x in range(config.ROUTER_SEARCH_STEP, config.NX, config.ROUTER_SEARCH_STEP):
            if solver.damping_map[y, x] == 1.0: # Chỉ đặt ở không khí
                candidate_positions.append((x, y))
    # không gian đứng được TRƯỚC khi chạy vòng lặp
    walkable_mask = (solver.damping_map >= 0.95)
    
    best_pos, best_score = None, -1
    best_coverage_map, best_max_amp = None, None
    for pos in tqdm(candidate_positions, desc=f"Computing Map {map_choice}", leave=False):
        
        # Dùng dấu '_' để vứt bỏ cái điểm số thô (chứa cả tường) của solver.py
        max_amp, coverage_mask, _ = solver.calculate_coverage(
            router_pos=pos, steps=config.SIM_STEPS, frequency=config.FREQUENCY, threshold=config.E_THRESHOLD
        )
        
        # (Lọc bỏ tường)
        valid_coverage_mask = np.logical_and(coverage_mask, walkable_mask)
        real_score = np.sum(valid_coverage_mask)

        # Grid Search 
        if real_score > best_score:
            best_score, best_pos = real_score, pos
            best_coverage_map, best_max_amp = coverage_mask, max_amp
    return best_pos, best_max_amp, best_coverage_map, solver.damping_map

def get_material_rgba(damping_map):
    """Chuyển đổi ma trận suy hao thành ma trận màu RGBA để phân biệt vật liệu"""
    rgba = np.zeros((damping_map.shape[0], damping_map.shape[1], 4))
    
    # Materials configuration:
    rgba[damping_map == 0.0] = [0.2, 0.2, 0.2, 1.0] 
    
    rgba[damping_map == 0.85] = [0.8, 0.4, 0.2, 1.0] 
    
    rgba[damping_map == 0.95] = [0.0, 0.8, 0.9, 0.7] 
    
    rgba[damping_map == 1.0] = [0.0, 0.0, 0.0, 0.0] 
    
    return rgba

def visualize_interactive_dashboard(all_results):
    """Hiển thị giao diện và nhận tín hiệu bàn phím (Đã nâng cấp màu vật liệu)"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Map init
    init_pos, init_amp, init_cov, init_damp = all_results[1]
    init_walls_rgba = get_material_rgba(init_damp)

    # Trục 1: Heatmap
    im1 = axes[0].imshow(init_amp, cmap='hot', origin='lower', vmin=0, vmax=1.0)
    im1_walls = axes[0].imshow(init_walls_rgba, origin='lower') 
    point1, = axes[0].plot(init_pos[0], init_pos[1], 'go', markersize=10, label='Router (Optimal)')
    axes[0].set_title("Maximum Wi-Fi Intensity Heatmap")
    axes[0].legend(loc="upper right")
    fig.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)

    # Trục 2: Coverage
    im2 = axes[1].imshow(init_cov, cmap='Blues', origin='lower')
    im2_walls = axes[1].imshow(init_walls_rgba, origin='lower')
    point2, = axes[1].plot(init_pos[0], init_pos[1], 'go', markersize=10)
    axes[1].set_title(f"Network Coverage Area (Eth Threshold = {config.E_THRESHOLD})")

    title_text = fig.suptitle("Displaying Map 1 (Press keys 1, 2, 3, 4 to switch maps)", fontsize=14, fontweight='bold')

    # change map on key press
    def on_key(event):
        if event.key not in ['1', '2', '3', '4']:
            return
        
        map_id = int(event.key)
        best_pos, max_amp, coverage_map, damping_map = all_results[map_id]
        
        walls_rgba = get_material_rgba(damping_map)

        im1.set_data(max_amp)
        im1_walls.set_data(walls_rgba)
        point1.set_data([best_pos[0]], [best_pos[1]])

        im2.set_data(coverage_map)
        im2_walls.set_data(walls_rgba)
        point2.set_data([best_pos[0]], [best_pos[1]])

        title_text.set_text(f"Displaying Map {map_id} (Press keys 1, 2, 3, 4 to switch maps)")
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('key_press_event', on_key)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("2D WAVE EQUATION SIMULATION - OPTIMIZING WI-FI PLACEMENT")
    print("System is pre-computing 4 maps. This process will take about 10-15 seconds, please wait...\n")
    
    # 1. TÍNH TOÁN TRƯỚC (Pre-compute) VÀ IN KẾT QUẢ RA TERMINAL
    all_results = {}
    for i in range(1, 5):
        best_pos, best_max_amp, best_coverage_map, damping_map = run_optimization(i)
        all_results[i] = (best_pos, best_max_amp, best_coverage_map, damping_map)
        
        # Đếm số pixel "có mạng"
        walkable_mask = (damping_map >= 0.95)
        walkable_pixels = np.sum(walkable_mask)
        
        # 2. Lọc vùng phủ sóng HỢP LỆ (Vừa có mạng VÀ Vừa đứng được)
        valid_coverage_mask = np.logical_and(best_coverage_map, walkable_mask)
        coverage_score = np.sum(valid_coverage_mask)
        
        # 3. Tính tỷ lệ % chuẩn xác tuyệt đối
        coverage_percent = (coverage_score / walkable_pixels) * 100
        
        # Biên độ cường độ đỉnh
        peak_amp = np.max(best_max_amp)
        
        print(f"\n=> KẾT QUẢ BẢN ĐỒ {i}:")
        print(f"   - Tọa độ Router tối ưu (x, y) : {best_pos}")
        print(f"   - Cường độ sóng đỉnh (Peak)   : {peak_amp:.4f}")
        print(f"   - Diện tích phủ sóng (%)      : {coverage_percent:.2f}%")
        print("-" * 50)
    
    print("\n=> Computation complete! Opening Dashboard interface...")
    
    visualize_interactive_dashboard(all_results)