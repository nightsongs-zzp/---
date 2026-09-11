import numpy as np
import matplotlib.pyplot as plt
import matplotlib
# 中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans SC', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
# 物理参数（自拟）
K_LIST  = [1, 2, 3, 5, 8]        # 图1: 衍射级次
DA_LIST = [3, 4, 6, 8, 12]       # 图2/3: 光栅常数与缝宽之比 d/a
LAMBDA  = 589.3                  # 图3 的参考波长 (nm)
# 配色（经 dataviz 校验）与共享样式
FIG_W, FIG_H = 12.8, 7.2         # 16:9
INK  = '#0b0b0b'                 # 主墨色（坐标）
GRID = '#e1e0d9'                 # 发丝网格线
# 图1: 类别色（固定顺序，k 的身份标识）
COLORS_ORDER = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4']
# 图2/3: 顺序蓝渐变
COLORS_DA = ['#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b']
def style_ax(ax, xlabel, ylabel, xlim, ylim, logx=False, logy=False):
    """定量对比曲线轴样式 —— 白底，粗体黑坐标，浅色横向发丝网格"""
    if logx:
        ax.set_xscale('log')
    if logy:
        ax.set_yscale('log')
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_facecolor('white')
    ax.set_xlabel(xlabel, fontsize=18, fontweight='bold', color=INK, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=18, fontweight='bold', color=INK, labelpad=8)
    ax.tick_params(labelsize=13, colors=INK, width=1.2)
    for spine in ax.spines.values():
        spine.set_color(INK)
    ax.grid(axis='y', color=GRID, linewidth=1.0)
    ax.set_axisbelow(True)
def add_legend(ax, loc):
    ax.legend(loc=loc, frameon=False, fontsize=12.5)

def save_figure(fig, filename):
    fig.savefig(filename, dpi=200, facecolor=fig.get_facecolor(),
                edgecolor='none', bbox_inches='tight', pad_inches=0.3)
    print(f"  -> 已保存: {filename}")
# 图1: R = kN 随缝数 N 的变化（不同级次 k）
fig1, ax1 = plt.subplots(figsize=(FIG_W, FIG_H), facecolor='white')
N_MAX1 = 400
N1 = np.linspace(0, N_MAX1, 800)

for k, c in zip(K_LIST, COLORS_ORDER):
    ax1.plot(N1, k * N1, color=c, linewidth=3.0, label=f'k = {k}', zorder=3)
    ax1.text(N_MAX1 * 1.015, k * N_MAX1, f'k={k}',color=c,fontsize=13,fontweight='bold', va='center')
style_ax(ax1, '缝数 N', '色分辨本领 R = λ/Δλ', (0, N_MAX1 * 1.12), (0, 8 * N_MAX1 * 1.06))
add_legend(ax1, 'upper left')
save_figure(fig1, '光栅色分辨本领随缝数的变化.png')
plt.close(fig1)
# 图2: 考虑缺级 —— 最高可用级次下的 R 随 N 的变化（不同 d/a）
fig2, ax2 = plt.subplots(figsize=(FIG_W,
FIG_H), facecolor='white')
N_MAX2 = 500
N2 = np.linspace(0, N_MAX2, 800)

for da, c in zip(DA_LIST, COLORS_DA):
    k_max = da - 1
    ax2.plot(N2, k_max * N2, color=c, linewidth=3.0,
             label=f'd/a = {da}（最高级次 k = {k_max}）', zorder=3)
style_ax(ax2, '缝数 N', '色分辨本领 R = λ/Δλ', (0, N_MAX2 * 1.12), (0, 11 * N_MAX2 * 1.06))
add_legend(ax2, 'upper left')
save_figure(fig2, '考虑缺级：最高可用级次下的色分辨本领.png')
plt.close(fig2)
# 图3: 可分辨最小波长差 Δλ = λ/R 随 N 的变化（λ = 589.3 nm）
fig3, ax3 = plt.subplots(figsize=(FIG_W, FIG_H), facecolor='white')
N3 = np.logspace(0, 4, 800)

for da, c in zip(DA_LIST, COLORS_DA):
    k_max = da - 1
    ax3.plot(N3, LAMBDA / (k_max * N3), color=c, linewidth=3.0,
             label=f'd/a = {da}（最高级次 k = {k_max}）', zorder=3)
    ax3.text(10**4 * 1.02, LAMBDA / (k_max * 10**4), f'{da}',
             color=c, fontsize=13, fontweight='bold', va='center')
style_ax(ax3, '缝数 N', '可分辨的最小波长差 Δλ / nm',
         (1, 10**4 * 1.18), (0.001, 320), logx=True, logy=True)
add_legend(ax3, 'upper right')
save_figure(fig3, '可分辨的最小波长差随缝数的变化.png')
plt.close(fig3)
print("\n三张色分辨本领对比曲线全部生成完毕！")
