import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from tqdm import tqdm
from solver import WaveSolver2D
import config

# ==========================================
# KHO BẢN ĐỒ (Map Gallery)
# ==========================================
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
# Dài, hẹp, bị chia cắt liên tục bởi các lớp tường gạch từ ngoài vào trong. Cửa cuốn sắt (#) ở mặt tiền.
# Ý nghĩa: Chứng minh việc đặt cục Wi-Fi ở tầng 1 (hoặc phòng khách đầu nhà) sẽ khiến phòng ngủ cuối nhà hoàn toàn mất mạng do suy hao liên tiếp.
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
# Phòng Giám đốc xây tường gạch kín đáo góc trái. Giữa phòng là không gian họp vách kính 100%. Mặt tiền là kính cường lực toàn cảnh.
# Ý nghĩa: Khoe hiện tượng KHÚC XẠ siêu đẹp. Sóng đi qua phòng họp kính rất mượt và sáng, nhưng đập vào phòng sếp thì bị gọt đi năng lượng ngay lập tức.
MAP_OFFICE = """
########################
#      =               -
#                      -
#      =   -       -   #
#      =   -       -   #
#==   ==   -       -   #
#                      #
#                      #
#                      #
########################
"""

# MẪU 4: TÒA NHÀ CÓ LÕI THANG MÁY
# Một mặt bằng rộng nhưng ngay chính giữa là một khối bê tông khổng lồ (Lõi thang máy/Trục kỹ thuật).
# Ý nghĩa: Đây là "Bóng ma Wi-Fi" trong đời thực. Lõi thang máy (#) hấp thụ 100% sóng, tạo ra một vùng mù (Deadzone) đen sì phía sau nó, đòi hỏi phải lắp 2 cục Router ở 2 bên mới phủ hết được.
MAP_ELEVATOR_CORE = """
########################
-      =       =       -
-                      -
-      =       =       -
#=======       ========#
#                      #
#                      #
#      =       =       #
#      =       =       #
########################
"""

# TỪ ĐIỂN VẬT LIỆU (Material Dictionary)
# Cấu trúc: 'Ký tự' : (Hệ số Damping, Vận tốc truyền sóng C)
MATERIALS = {
    ' ': (1.0, 1.0),   # Không khí: Sóng đi nhanh nhất (C=1.0), không bị cản
    '#': (0.0, 0.0),   # Bê tông/Kim loại: Hấp thụ toàn bộ sóng (Tạo bóng ma Wi-Fi)
    '=': (0.85, 0.6),  # Tường gạch: Làm yếu sóng và làm CHẬM sóng (Gây ra khúc xạ)
    '-': (0.95, 0.8)   # Cửa kính/Gỗ: Xuyên thấu tốt hơn tường, sóng truyền nhanh hơn tường gạch
}

def build_room_from_ascii(solver, ascii_map):
    """Đọc bản đồ ký tự và sinh ra 2 ma trận vật lý (Damping và Velocity C)"""
    lines = [line for line in ascii_map.strip().split('\n') if line.strip()]
    grid_y = len(lines)
    grid_x = max(len(line) for line in lines)
    
    block_h = solver.ny // grid_y
    block_w = solver.nx // grid_x
    
    # Bước 1: Reset toàn bộ phòng thành không khí (Air)
    solver.damping_map.fill(MATERIALS[' '][0])
    solver.c_map.fill(MATERIALS[' '][1])
    
    # Bước 2: Đắp vật liệu theo bản đồ
    for i, row in enumerate(lines):
        for j, char in enumerate(row):
            if char == ' ': # Bỏ qua khoảng trắng để tối ưu tốc độ
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
    
    # [ĐÃ SỬA Ở ĐÂY]: Xóa config.C ở cuối, vì Vận tốc sóng giờ đã tự động 
    # thay đổi theo bản đồ vật liệu (c_map) bên trong class WaveSolver2D.
    solver = WaveSolver2D(config.NX, config.NY, config.DX, config.DY, config.DT)
    
    map_dict = {1: MAP_APARTMENT, 2: MAP_TUBE_HOUSE, 3: MAP_OFFICE, 4: MAP_ELEVATOR_CORE}
    selected_map = map_dict.get(map_choice, MAP_APARTMENT)
    
    # Hàm này giờ đây sẽ tự động gán cả Damping và Vận tốc khúc xạ C cho từng loại tường
    build_room_from_ascii(solver, selected_map)

    # Đề xuất các vị trí test 
    candidate_positions = [(20, 20), (60, 50)]
    best_pos, best_score = None, -1
    best_coverage_map, best_max_amp = None, None

    for pos in candidate_positions:
        max_amp, coverage_mask, score = solver.calculate_coverage(
            router_pos=pos, steps=config.SIM_STEPS, frequency=config.FREQUENCY, threshold=config.E_THRESHOLD
        )
        if score > best_score:
            best_score, best_pos = score, pos
            best_coverage_map, best_max_amp = coverage_mask, max_amp

    return best_pos, best_max_amp, best_coverage_map, solver.damping_map

def get_material_rgba(damping_map):
    """Chuyển đổi ma trận suy hao thành ma trận màu RGBA để phân biệt vật liệu"""
    rgba = np.zeros((damping_map.shape[0], damping_map.shape[1], 4))
    
    # 1. Bê tông/Kim loại (Damping = 0.0): Màu Xám đậm (Cản 100% sóng)
    rgba[damping_map == 0.0] = [0.2, 0.2, 0.2, 1.0] 
    
    # 2. Tường gạch (Damping = 0.85): Màu Cam đất/Nâu gạch
    rgba[damping_map == 0.85] = [0.8, 0.4, 0.2, 1.0] 
    
    # 3. Cửa kính/Gỗ (Damping = 0.95): Màu Xanh lơ trong suốt
    rgba[damping_map == 0.95] = [0.0, 0.8, 0.9, 0.7] 
    
    # 4. Không khí (Damping = 1.0): Hoàn toàn trong suốt (Alpha = 0)
    rgba[damping_map == 1.0] = [0.0, 0.0, 0.0, 0.0] 
    
    return rgba

def visualize_interactive_dashboard(all_results):
    """Hiển thị giao diện và nhận tín hiệu bàn phím (Đã nâng cấp màu vật liệu)"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # --- KHỞI TẠO BẢN ĐỒ SỐ 1 ---
    init_pos, init_amp, init_cov, init_damp = all_results[1]
    
    # Dùng hàm mới để lấy màu vật liệu thay vì np.where
    init_walls_rgba = get_material_rgba(init_damp)

    # Trục 1: Heatmap
    im1 = axes[0].imshow(init_amp, cmap='hot', origin='lower', vmin=0, vmax=1.0)
    im1_walls = axes[0].imshow(init_walls_rgba, origin='lower') # Bỏ alpha=0.5 vì RGBA đã tự xử lý
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

    # --- HÀM XỬ LÝ SỰ KIỆN BÀN PHÍM ---
    def on_key(event):
        if event.key not in ['1', '2', '3', '4']:
            return
        
        map_id = int(event.key)
        best_pos, max_amp, coverage_map, damping_map = all_results[map_id]
        
        # Cập nhật màu vật liệu cho khung hình mới
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
    
    # 1. TÍNH TOÁN TRƯỚC (Pre-compute)
    all_results = {}
    for i in range(1, 5):
        print(f"Computing Map {i}...")
        all_results[i] = run_optimization(i)
    
    print("\n=> Computation complete! Opening Dashboard interface...")
    
    # 2. HIỂN THỊ GIAO DIỆN CHUYỂN TAB
    visualize_interactive_dashboard(all_results)