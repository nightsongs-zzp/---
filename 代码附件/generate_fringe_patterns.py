import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import LinearSegmentedColormap
# 中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans SC', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
# 物理参数 —— 与 generate_figures.py 完全一致
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
COLOR_SINGLE = '#3b82b6'   # 蓝色 —— 单缝衍射
COLOR_MULTI  = '#ef4444'   # 红色 —— 多缝干涉
COLOR_TOTAL  = '#8b5cf6'   # 紫色 —— 光栅总效果

N_VERTICAL = 600           # 条纹垂直方向的像素数
Y_TOP = 3.0                # 纵向范围（任意单位，仅用于显示）
def make_colormap(hex_color):
    """创建从白色(强度=0)到目标颜色(强度=1)的 LinearSegmentedColormap"""
    r, g, b = tuple(int(hex_color.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    cdict = {
        'red':   [(0.0, 1.0, 1.0), (1.0, r, r)],
        'green': [(0.0, 1.0, 1.0), (1.0, g, g)],
        'blue':  [(0.0, 1.0, 1.0), (1.0, b, b)],
    }
    return LinearSegmentedColormap(f'white_to_{hex_color.lstrip("#")}', cdict)
def make_fringe_2d(intensity_1d, gamma=1.0):
    """将一维光强分布扩展为二维条纹图，gamma < 1 可提升暗纹可见度"""
    i_norm = intensity_1d / np.max(intensity_1d)
    i_gamma = i_norm ** gamma       # gamma 校正：压缩动态范围，次峰更可见
    return np.tile(i_gamma, (N_VERTICAL, 1))
def save_figure(fig, filename):
    fig.savefig(filename, dpi=200, facecolor=fig.get_facecolor(),
                edgecolor='none', bbox_inches='tight', pad_inches=0.3)
    print(f"  -> 已保存: {filename}")
def style_fringe_ax(ax):
    """去除所有坐标轴，白底"""
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-Y_TOP, Y_TOP)
    ax.set_facecolor('white')
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
# 图1: 单缝衍射条纹
fig1, ax1 = plt.subplots(figsize=(FIG_W, FIG_H), facecolor='white')
style_fringe_ax(ax1)

fringe_single = make_fringe_2d(I_single, gamma=0.35)   # 大幅提升次级峰可见度
cmap_single = make_colormap(COLOR_SINGLE)
ax1.imshow(fringe_single, cmap=cmap_single, aspect='auto',
           extent=[-1.0, 1.0, -Y_TOP, Y_TOP], origin='lower')

save_figure(fig1, '01_single_slit_fringe.png')
plt.close(fig1)
# 图2: 多缝干涉条纹
fig2, ax2 = plt.subplots(figsize=(FIG_W, FIG_H), facecolor='white')
style_fringe_ax(ax2)

fringe_multi = make_fringe_2d(I_multi)   # 各级主极大等亮，无需 gamma
cmap_multi = make_colormap(COLOR_MULTI)
ax2.imshow(fringe_multi, cmap=cmap_multi, aspect='auto',
           extent=[-1.0, 1.0, -Y_TOP, Y_TOP], origin='lower')

save_figure(fig2, '02_multi_slit_fringe.png')
plt.close(fig2)
# 图3: 光栅衍射总条纹
fig3, ax3 = plt.subplots(figsize=(FIG_W, FIG_H), facecolor='white')
style_fringe_ax(ax3)
fringe_total = make_fringe_2d(I_total, gamma=0.45) # 让包络调制后的外层峰可见
cmap_total = make_colormap(COLOR_TOTAL)
ax3.imshow(fringe_total, cmap=cmap_total, aspect='auto',
           extent=[-1.0, 1.0, -Y_TOP, Y_TOP], origin='lower')
save_figure(fig3,'03_grating_total_fringe.png')
plt.close(fig3)
print("\n三张条纹图全部生成完毕！")
