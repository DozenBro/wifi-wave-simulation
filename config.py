# ==========================================
# CẤU HÌNH KHÔNG GIAN LƯỚI (Grid Settings)
# ==========================================
NX = 120        # Kích thước trục X (chiều rộng phòng)
NY = 100        # Kích thước trục Y (chiều dài phòng)
DX = 1.0        # Khoảng cách giữa 2 điểm lưới (Delta x)
DY = 1.0        # Delta y

# ==========================================
# THÔNG SỐ VẬT LÝ VÀ TOÁN HỌC (Physics & Math)
# ==========================================
C = 1.0         # Tốc độ truyền sóng (Wi-Fi)
DT = 0.5        # Bước nhảy thời gian (Delta t). 
                # Đảm bảo điều kiện CFL: C * DT / DX <= 0.707 để không vỡ ma trận!

# Hệ số suy hao môi trường (Damping)
DAMPING_AIR = 1.0       # Không khí (Không suy hao)
DAMPING_WALL = 0.85     # Tường gạch (Sóng đi qua bị giảm biên độ)
DAMPING_CONCRETE = 0.0  # Tường bê tông (Hấp thụ/phản xạ 100%, không xuyên qua)

# Tần số phát sóng của Router
FREQUENCY = 0.1 

# ==========================================
# THÔNG SỐ TỐI ƯU HÓA (Optimization)
# ==========================================
E_THRESHOLD = 0.05      # Ngưỡng cường độ sóng tối thiểu để "có mạng" (Eth)
SIM_STEPS = 600         # Số bước thời gian để sóng lấp đầy phòng