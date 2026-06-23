import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.grid(True, linestyle='--', alpha=0.6)

# Vẽ các điểm lưới (5-point stencil)
points = {(0,0): '$u_{i,j}^n$', (1,0): '$u_{i+1,j}^n$', (-1,0): '$u_{i-1,j}^n$', 
          (0,1): '$u_{i,j+1}^n$', (0,-1): '$u_{i,j-1}^n$'}

for (x, y), label in points.items():
    color = 'red' if x==0 and y==0 else 'blue'
    size = 150 if x==0 and y==0 else 100
    ax.scatter(x, y, color=color, s=size, zorder=5)
    ax.text(x + 0.1, y + 0.1, label, fontsize=14, fontweight='bold')

# Vẽ mũi tên liên kết
ax.annotate('', xy=(1, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="<->", color='black'))
ax.annotate('', xy=(0, 1), xytext=(0, 0), arrowprops=dict(arrowstyle="<->", color='black'))

ax.set_title("Biểu đồ Lưới Sai phân 5 điểm (5-Point Stencil)", fontsize=16)
plt.axis('off')
plt.show()