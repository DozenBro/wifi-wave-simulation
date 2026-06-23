import numpy as np

class WaveSolver2D:
    def __init__(self, nx, ny, dx, dy, dt): 
        self.nx = nx
        self.ny = ny
        self.dt = dt
        self.dx = dx
        self.dy = dy
        
        self.u_prev = np.zeros((ny, nx))
        self.u_curr = np.zeros((ny, nx))
        self.u_next = np.zeros((ny, nx))
        
        self.damping_map = np.ones((ny, nx))  # Hệ số suy hao 
        self.c_map = np.ones((ny, nx))        # Vận tốc sóng 
        
        self.time_step = 0

    def step(self, router_pos, frequency):
        # Hệ số Courant bây giờ là một MA TRẬN (thay đổi theo vật liệu)
        r_x = (self.c_map[1:-1, 1:-1] * self.dt / self.dx) ** 2
        r_y = (self.c_map[1:-1, 1:-1] * self.dt / self.dy) ** 2

        laplacian = (
            self.u_curr[2:, 1:-1] + self.u_curr[:-2, 1:-1] - 2 * self.u_curr[1:-1, 1:-1]
        ) * r_x + (
            self.u_curr[1:-1, 2:] + self.u_curr[1:-1, :-2] - 2 * self.u_curr[1:-1, 1:-1]
        ) * r_y

        self.u_next[1:-1, 1:-1] = self.damping_map[1:-1, 1:-1] * (
            2 * self.u_curr[1:-1, 1:-1] - self.u_prev[1:-1, 1:-1] + laplacian
        )

        rx, ry = router_pos
        self.u_next[ry, rx] = np.sin(2 * np.pi * frequency * self.time_step * self.dt)

        self.u_prev[:] = self.u_curr[:]
        self.u_curr[:] = self.u_next[:]
        self.time_step += 1

    def calculate_coverage(self, router_pos, steps, frequency, threshold):
        self.u_prev.fill(0)
        self.u_curr.fill(0)
        self.u_next.fill(0)
        self.time_step = 0
        max_amplitude = np.zeros((self.ny, self.nx))

        for _ in range(steps):
            self.step(router_pos, frequency)
            max_amplitude = np.maximum(max_amplitude, np.abs(self.u_curr))

        coverage_mask = max_amplitude >= threshold
        return max_amplitude, coverage_mask, np.sum(coverage_mask)