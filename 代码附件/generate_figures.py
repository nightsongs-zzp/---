import numpy as np
import matplotlib.pyplot as plt
import matplotlib
# 中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans SC', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
# 物理参数 —— 窄包络配置，让调制结构清晰可见
A = 3.0             # 缝宽 a（增大 → 包络更窄，结构更丰富）
D = 12.0            # 光栅常数 d（d/a = 4，每第4级干涉峰缺级）
N = 6               # 缝数
WAVELENGTH = 1.0    # 波长 λ
# 数据计算
SIN_THETA = np.linspace(-1.0, 1.0, 4000)
alpha = np.pi * A * SIN_THETA / WAVELENGTH
beta  = np.pi * D * SIN_THETA / WAVELENGTH
with np.errstate(divide='ignore', invalid='ignore'):
    I_single = np.where(
        np.abs(alpha) < 1e-12, 1.0,
        (np.sin(alpha) / alpha) ** 2
    )
    I_multi = np.where(
        np.abs(np.sin(beta)) < 1e-12,
        np.where(np.abs(beta % np.pi) < 1e-12, float(N ** 2), 0.0),
        (np.sin(N * beta) / np.sin(beta)) ** 2
    )
I_total = I_single * I_multi
# 共享配置
FIG_W, FIG_H = 12.8, 7.2  # 16:9
COLOR_SINGLE = '#3b82b6'
COLOR_MULTI  = '#ef4444'
COLOR_TOTAL  = '#8b5cf6'
def style_ax(ax, y_max=1.15):
    """统一轴样式 —— 白底，无网格，无标题，粗体黑色坐标"""
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-0.05 * y_max, y_max * 1.12)
    ax.set_xlabel('sin θ', fontsize=18, fontweight='bold', color='black', labelpad=8)
    ax.set_ylabel('相\n对\n强\n度\n', fontsize=18, fontweight='bold', color='black', rotation=0, labelpad=8, va='center')
    ax.tick_params(labelsize=13, colors='black')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_facecolor('white')
    for spine in ax.spines.values():
        spine.set_color('black')
def save_figure(fig, filename):
    fig.savefig(filename, dpi=200, facecolor=fig.get_facecolor(),
                edgecolor='none', bbox_inches='tight', pad_inches=0.3)
    print(f"  -> 已保存: {filename}")
# 图1: 单缝衍射因子 —— 纯曲线
fig1, ax1 = plt.subplots(figsize=(FIG_W, FIG_H), facecolor='white')
style_ax(ax1, y_max=1.0)
ax1.fill_between(SIN_THETA, 0, I_single, color=COLOR_SINGLE, alpha=0.18,
linewidth=0)
ax1.plot(SIN_THETA,I_single,color=COLOR_SINGLE, linewidth=2.8, zorder=3)
save_figure(fig1, '01_single_slit.png')
plt.close(fig1)
# 图2: 多缝干涉因子 —— 纯曲线
fig2, ax2 = plt.subplots(figsize=(FIG_W, FIG_H), facecolor='white')
style_ax(ax2, y_max=N**2)
ax2.plot(SIN_THETA, I_multi, color=COLOR_MULTI, linewidth=1.3, zorder=3)
save_figure(fig2, '02_multi_slit.png')
plt.close(fig2)
# 图3: 光栅总光强 —— 调制叠加（保留包络虚线以体现调制关系）
fig3, ax3 = plt.subplots(figsize=(FIG_W, FIG_H), facecolor='white')
style_ax(ax3, y_max=N**2)
ax3.fill_between(SIN_THETA, 0, I_total, color=COLOR_TOTAL, alpha=0.22, linewidth=0)
ax3.plot(SIN_THETA, I_total, color=COLOR_TOTAL, linewidth=2.2, zorder=4)
ax3.plot(SIN_THETA, I_single * N**2, color=COLOR_SINGLE, linewidth=1.8,
         linestyle='--', alpha=0.5, zorder=3)
save_figure(fig3, '03_grating_total.png')
plt.close(fig3)
print("\n三张图片全部生成完毕！")
