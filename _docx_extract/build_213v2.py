# -*- coding: utf-8 -*-
"""由 213.tex 生成 213[2].tex(修正版研究报告):
1) 章节体系 \chapter 1-6(删除 0.x 编号); 2) 摘要/附件 \chapter* + 目录条目;
3) 全部源代码剥离正文, 改为外部附件(代码附件目录), 正文仅留功能简述+带底色示例代码;
4) 术语统一(夫琅禾费/惠更斯-菲涅耳/Manim)与中英文标点;
5) 公式变量说明统一为"式中："、公式间距; 6) 图 \label、(a)(b)(c)(d) 显式引用、图注完善;
7) 拆分拥挤大段、修正错别字与断句。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
SRC = os.path.join(PROJECT, '213.tex')
DST = os.path.join(PROJECT, '213[2].tex')

with open(SRC, encoding='utf-8') as f:
    t = f.read()

def rep(t, old, new, label='', n=1):
    cnt = t.count(old)
    if n is None:
        ok = cnt >= 1
    else:
        ok = cnt == n
    if not ok:
        raise SystemExit('[FAIL] %s: 期望 %s 处, 实际 %d 处' % (label or old[:50], n, cnt))
    return t.replace(old, new)

# ================= 1. 全局术语与专有名词 =================
t = rep(t, '夫琅和费', '夫琅禾费', '夫琅和费->夫琅禾费', n=None)
t = rep(t, '惠更斯 - 菲涅耳', '惠更斯-菲涅耳', '惠更斯 - 菲涅耳 统一', n=None)
t = rep(t, 'manim', 'Manim', 'manim->Manim', n=None)
t = rep(t, 'html & 交互式仿真网页开发', 'HTML & 交互式仿真网页开发', 'html->HTML', n=1)

# ================= 2. 导言区 =================
t = rep(t, '\\documentclass[12pt,a4paper]{ctexrep}',
        '\\documentclass[12pt,a4paper]{ctexrep}\n\n'
        '% ---- 章节标题格式(一级标题编号 1,2,3...) ----\n'
        '\\ctexset{\n'
        '  chapter = {\n'
        '    name = {},\n'
        '    number = \\arabic{chapter},\n'
        '    format = \\centering\\zihao{3}\\heiti,\n'
        '    titleformat = \\centering\\zihao{3}\\heiti,\n'
        '    beforeskip = 10pt,\n'
        '    afterskip = 24pt,\n'
        '  },\n'
        '  section = {\n'
        '    format = \\zihao{4}\\heiti,\n'
        '    beforeskip = 18pt,\n'
        '    afterskip = 10pt,\n'
        '  },\n'
        '  subsection = {\n'
        '    format = \\zihao{-4}\\heiti,\n'
        '    beforeskip = 14pt,\n'
        '    afterskip = 8pt,\n'
        '  },\n'
        '}', '插入 ctexset', n=1)

t = rep(t, '\\usepackage{enumitem}',
        '\\usepackage{enumitem}\n\n'
        '% ---- 公式与浮动体间距(全文统一) ----\n'
        '\\setlength{\\abovedisplayskip}{8pt plus 2pt minus 2pt}\n'
        '\\setlength{\\belowdisplayskip}{8pt plus 2pt minus 2pt}\n'
        '\\setlength{\\abovedisplayshortskip}{4pt plus 1pt minus 1pt}\n'
        '\\setlength{\\belowdisplayshortskip}{4pt plus 1pt minus 1pt}\n'
        '\\setlength{\\intextsep}{10pt plus 2pt minus 2pt}\n'
        '\\setlength{\\textfloatsep}{12pt plus 2pt minus 2pt}\n'
        '\\setlength{\\floatsep}{10pt plus 2pt minus 2pt}', '插入间距设置', n=1)

t = rep(t, '  keepspaces=true,\n  frame=single,',
        '  keepspaces=true,\n  backgroundcolor=\\color{gray!12},\n  frame=single,',
        '代码块加底色', n=1)

t = rep(t, "% ---- 参考资料标题 ----\n\\renewcommand{\\bibname}{参考资料}\n",
        '', '移除 bibname(改为手排参考文献列表)', n=1)

# ================= 3. 层级重构 =================
t = rep(t, '\\subsection{', '\\section{', 'subsection->section', n=None)
t = rep(t, '\\subsubsection{', '\\subsection{', 'subsubsection->subsection', n=None)
for name in ['项目概述', '基本理论', '实验与仿真设计', '视频设计与呈现', '创新点与总结']:
    t = rep(t, '\\section{%s}' % name, '\\chapter{%s}' % name, '根章节 %s' % name, n=1)

# ---------- 摘要(重写为与正文一致的准确表述, 关键词全角标点) ----------
ABSTRACT = (
    '\\chapter*{摘要}\n'
    '\\addcontentsline{toc}{chapter}{摘要}\n\n'
    '本项目围绕大学物理理论课中的光栅衍射主题，融合理论分析、数值仿真与微视频制作，系统阐述了从单缝衍射、多缝干涉到光栅衍射的完整物理图像。理论层面，以惠更斯-菲涅耳原理为出发点，推导单缝夫琅禾费衍射与多缝干涉的光强分布公式，进而得到光栅衍射总光强公式，重点剖析缺级现象、亮纹半角宽度与色分辨本领等核心特性。仿真层面，基于 Python 科学计算生态（NumPy、Matplotlib）对单缝衍射、多缝干涉、光栅缺级及色分辨本领进行数值模拟，并结合 Manim 动画引擎与 Blender 三维渲染技术，将抽象的矢量叠加与光强分布过程转化为直观的动态画面。在此基础上制作完成约 3 分钟的科普微视频，以「大国重器悬念引入—原理拆解—特性分析—应用升华」的叙事结构，将光栅衍射原理与光刻机、郭守敬望远镜（LAMOST）等国家重大科技工程相结合，并配套开发可参数调节的交互式仿真网页。项目实现了理论、仿真、动画与实验素材的有机融合，为大学物理理论课辅助教学提供了一套集科学性、直观性与趣味性于一体的微视频教学资源。\n\n'
    '\\noindent 关键词：\\textbf{光栅衍射；夫琅禾费衍射；缺级现象；色分辨本领；微视频教学}\n\n'
    '\\tableofcontents'
)
new_t = re.sub(r'\\section\*\{摘要\}\n.*?\n\\tableofcontents', lambda m: ABSTRACT, t, count=1, flags=re.S)
assert new_t != t, '摘要块替换失败'
t = new_t

# ---------- 参考资料(手排编号列表, 成为第 6 章) ----------
NEW_REF = (
    '\\chapter{参考资料}\n\n'
    '\\begin{enumerate}[label={[\\arabic*]}, leftmargin=3em, itemsep=4pt]\n'
    '\\item 赵凯华, 钟锡华. 光学[M]. 北京大学出版社, 2004.\n'
    '\\item 梁铨廷. 物理光学[M]. 电子工业出版社, 2012.\n'
    '\\item 张三慧. 大学物理学：波动与光学分册[M]. 清华大学出版社, 2019.\n'
    '\\item 郁道银, 谈恒英. 工程光学[M]. 机械工业出版社, 2016.\n'
    '\\item 中国科学院国家天文台. 郭守敬望远镜（LAMOST）科学成果简介[EB/OL].\n'
    '\\item 周炳琨. 激光原理[M]. 国防工业出版社, 2014.\n'
    '\\item 约瑟夫·W·古德曼. 傅里叶光学导论[M]. 电子工业出版社, 2020.\n'
    '\\end{enumerate}'
)
new_t = re.sub(r'\\section\{参考资料\}.*?\\end\{thebibliography\}', lambda m: NEW_REF, t, count=1, flags=re.S)
assert new_t != t, '参考资料块替换失败'
t = new_t

# ---------- 附件1 ----------
t = rep(t, '\\section*{附件1：组员分工}\n\\addcontentsline{toc}{section}{附件1：组员分工}',
        '\\chapter*{附件1：组员分工}\n\\addcontentsline{toc}{chapter}{附件1：组员分工}', '附件1', n=1)

# ================= 4. 正文修正 =================
# --- 基本理论 ---
t = rep(t,
        '其中：\n\n'
        '$U(P)$ 为空间场点 $P$ 的复振幅；\n\n'
        'U(Q)为波前上某点 Q（次级波源）处的波扰,$C$ 为比例常数；\n\n'
        '$K(\\theta)$ 为倾斜因子，描述子波振幅随衍射角 $\\theta$ 的变化规律；\n\n'
        '$dS$ 为波前 $S$ 上的面元；$r$ 为面元到场点 $P$ 的距离；$k$ 为波数，$k=\\frac{2\\pi}{\\lambda}$；',
        '\\noindent 式中：$U(P)$ 为空间场点 $P$ 的复振幅；$U(Q)$ 为波前上某点 $Q$（次级波源）处的波扰；$C$ 为比例常数；$K(\\theta)$ 为倾斜因子，描述子波振幅随衍射角 $\\theta$ 的变化规律；$\\mathrm{d}\\sigma$ 为波前 $\\Sigma$ 上的面元；$r$ 为面元到场点 $P$ 的距离；$k$ 为波数，$k=\\frac{2\\pi}{\\lambda}$。',
        '惠更斯公式变量说明', n=1)

t = rep(t, '整体几何尺寸与距离 zz 成正比。具有稳定的分布规律。',
        '整体几何尺寸与距离 $z$ 成正比，具有稳定的分布规律。', '距离 zz 笔误', n=1)

t = rep(t, '其中，${I}_{0}$ 为中央主极大的光强；$\\alpha$ 为单缝衍射的相位参数，物理意义是狭缝边缘与中心的子波在衍射角 $\\theta$ 方向的相位差的一半，表达式为：',
        '式中：${I}_{0}$ 为中央主极大的光强；$\\alpha$ 为单缝衍射的相位参数，其物理意义是狭缝边缘与中心的子波在衍射角 $\\theta$ 方向的相位差的一半，表达式为：',
        '单缝光强变量说明', n=1)

t = rep(t, '其中，${I}_{1}$ 为单条缝在该方向的光强。',
        '式中：${I}_{1}$ 为单条缝在该方向的光强。', '多缝变量说明', n=1)

t = rep(t, '（$k=0,\\pm1,\\pm2\\cdots$）', '（$k=0,\\pm1,\\pm2,\\cdots$）', '级次标点', n=1)

t = rep(t,
        '主极大条纹细锐明亮，光强远高于次极大；\n\n'
        '两个相邻主极大之间，分布着 $N-1$ 条暗纹和 $N-2$ 个次极大；\n\n'
        '缝数 $N$ 越大，主极大条纹越细越亮，背景越暗，分光效果越好。',
        '\\begin{itemize}[leftmargin=2em, itemsep=2pt]\n'
        '\\item 主极大条纹细锐明亮，光强远高于次极大；\n'
        '\\item 两个相邻主极大之间，分布着 $N-1$ 条暗纹和 $N-2$ 个次极大；\n'
        '\\item 缝数 $N$ 越大，主极大条纹越细越亮，背景越暗，分光效果越好。\n'
        '\\end{itemize}',
        '干涉图样特征列表化', n=1)

t = rep(t, '其中，$\\alpha=\\frac{\\pi a\\sin \\theta}{\\lambda}$，$\\beta=\\frac{\\pi d\\sin \\theta}{\\lambda}$。',
        '式中：$\\alpha=\\frac{\\pi a\\sin\\theta}{\\lambda}$，$\\beta=\\frac{\\pi d\\sin\\theta}{\\lambda}$。',
        '光栅总光强变量说明', n=1)

t = rep(t, r"k=\frac{d}{a}{k}^{'}({k}^{'}=\pm1,\pm2,\pm3\cdots)",
        r"k=\frac{d}{a}k'\qquad(k'=\pm1,\pm2,\pm3,\cdots)",
        '缺级级次公式', n=1)

t = rep(t, '第 k 级主极大半角宽度公式为：', '第 $k$ 级主极大半角宽度公式为：', '第k级', n=1)

t = rep(t, '式中：N 为光栅总刻缝数，d 为光栅常数，$\\theta_k$ 为第 k 级衍射角。',
        '式中：$N$ 为光栅总刻缝数，$d$ 为光栅常数，$\\theta_k$ 为第 $k$ 级衍射角。',
        '半角宽度变量说明', n=1)

t = rep(t, '仅由\\textbf{衍射级次 k} 和\\textbf{总刻缝数 N} 决定',
        '仅由\\textbf{衍射级次 $k$} 和\\textbf{总刻缝数 $N$} 决定', '分辨本领变量', n=1)

# --- 实验与仿真设计 ---
t = rep(t, '所输出的图像、曲线及帧序列均可直接用于视频渲染合成。',
        '所输出的图像、曲线及帧序列均可直接用于视频渲染合成。仿真代码界面如图~\\ref{fig:code}所示。',
        '仿真工具图引用', n=1)

t = rep(t, '\\caption{仿真代码界面}',
        '\\caption{仿真代码界面（Python 数值仿真）}\n\\label{fig:code}', '仿真代码界面图注', n=1)

t = rep(t, '仿真统一采用归一化波长 λ = 1.0，以 sinθ 作为衍射角采样变量并覆盖',
        '仿真统一采用归一化波长 $\\lambda=1.0$，以 $\\sin\\theta$ 作为衍射角采样变量并覆盖',
        '参数设置-波长', n=1)
new_t = re.sub(r'覆盖 \[[^\]]*1, 1[^\]]*\] 全域', lambda m: '覆盖 $[-1,\\,1]$ 全域', t, count=1)
assert new_t != t, '参数设置-区间替换失败'
t = new_t
t = rep(t, '可变核心参数包括单缝缝宽 a、光栅常数 d 与光栅总缝数 N。',
        '可变核心参数包括单缝缝宽 $a$、光栅常数 $d$ 与光栅总缝数 $N$。', '参数设置-变量', n=1)
t = rep(t, '基准工况取 a = 3.0、d = 12.0、N = 6，对应 d/a = 4，此时',
        '基准工况取 $a=3.0$、$d=12.0$、$N=6$，对应 $d/a=4$，此时', '参数设置-基准工况', n=1)
t = rep(t, '在此基础上另设多组对照工况，如 d/a = 3、4、6、8、12 与衍射级次 k = 1、2、3、5、8，分别考察是缺级规律、亮纹半角宽度及色分辨本领随参数的变化。',
        '在此基础上另设多组对照工况，如 $d/a=3,4,6,8,12$ 与衍射级次 $k=1,2,3,5,8$，分别考察缺级规律、亮纹半角宽度及色分辨本领随参数的变化。',
        '参数设置-对照工况', n=1)

t = rep(t,
        '完整输出五类仿真成果：单缝衍射光强分布与条纹图样、多缝干涉精细条纹、光栅衍射缺级对比图样、不同缝数下半角宽度变化动画、多组参数下色分辨本领对比曲线。所有成果严格贴合物理公式，保证科普视频的科学性与严谨性。',
        '完整输出五类仿真成果：单缝衍射光强分布与条纹图样、多缝干涉精细条纹、光栅衍射缺级对比图样、不同缝数下半角宽度变化动画、多组参数下色分辨本领对比曲线。所有成果严格贴合物理公式，保证科普视频的科学性与严谨性。主要数值仿真输出如图~\\ref{fig:sim-output}所示，其中(a)为单缝衍射光强分布曲线，(b)为对应的二维衍射条纹图样，(c)(d)为多缝干涉因子的光强分布与条纹图样，(e)(f)为光栅衍射总光强分布与总图样，可清晰观察到单缝包络对干涉条纹的调制与缺级现象。色分辨本领随缝数的变化、考虑缺级后最高可用级次下的色分辨本领以及可分辨最小波长差随缝数的变化分别如图~\\ref{fig:resolving-N}、图~\\ref{fig:resolving-missing}与图~\\ref{fig:resolving-dlambda}所示。',
        '仿真输出成果图引用', n=1)

# 图 label: 单图
t = rep(t, '\\caption{光栅色分辨本领随缝数的变化}',
        '\\caption{光栅色分辨本领随缝数的变化}\n\\label{fig:resolving-N}', 'fig:resolving-N', n=1)
t = rep(t, '\\caption{考虑缺级：最高可用级次下的色分辨本领}',
        '\\caption{考虑缺级：最高可用级次下的色分辨本领}\n\\label{fig:resolving-missing}', 'fig:resolving-missing', n=1)
t = rep(t, '\\caption{可分辨的最小波长差随缝数的变化}',
        '\\caption{可分辨的最小波长差随缝数的变化}\n\\label{fig:resolving-dlambda}', 'fig:resolving-dlambda', n=1)
t = rep(t, '\\caption{实验装置图}', '\\caption{实验装置图}\n\\label{fig:setup}', 'fig:setup', n=1)

# 图 label: 仿真输出 6 子图
t = rep(t, '\\caption{单缝衍射光强分布}',
        '\\caption{单缝衍射光强分布}\n\\label{fig:sim-a}', 'fig:sim-a', n=1)
t = rep(t, '\\caption{单缝衍射图样}',
        '\\caption{单缝衍射图样}\n\\label{fig:sim-b}', 'fig:sim-b', n=1)
t = rep(t, '\\caption{多缝干涉因子光强分布}',
        '\\caption{多缝干涉因子光强分布}\n\\label{fig:sim-c}', 'fig:sim-c', n=1)
t = rep(t, '\\caption{多缝干涉因子图样}',
        '\\caption{多缝干涉因子图样}\n\\label{fig:sim-d}', 'fig:sim-d', n=1)
t = rep(t, '\\caption{光栅总光强分布}',
        '\\caption{光栅总光强分布}\n\\label{fig:sim-e}', 'fig:sim-e', n=1)
t = rep(t, '\\caption{光栅总图样}\n\\end{subfigure}\n\\end{figure}',
        '\\caption{光栅总图样}\n\\label{fig:sim-f}\n\\end{subfigure}\n\n'
        '\\caption{光栅衍射数值仿真输出成果}\n\\label{fig:sim-output}\n\\end{figure}',
        'fig:sim-f/组图注', n=1)

# 实验器材
t = rep(t, '氦氖激光器（632.8nm 单色光源）', '氦氖激光器（632.8 nm 单色光源）', '实验器材单位', n=1)

# 实验内容与步骤 -> 分步列表
t = rep(t,
        '首先搭建同轴光学光路，校准激光器、衍射元件、光屏中心对齐，保证入射光垂直入射。单缝衍射实验中，逐步调节狭缝宽度，观测条纹宽窄、亮度变化规律并记录现象。光栅衍射实验中，更换不同光栅常数的光栅，观测规则明亮条纹，验证光栅分光特性。选用满足整数比值关系的光栅，清晰观测缺级现象，记录缺级级次。最后对比不同总缝数光栅的谱线精细度，定性验证半角宽度与分辨本领规律。',
        '\\begin{enumerate}[label={第\\arabic*步：}, leftmargin=2.6em, itemsep=2pt]\n'
        '\\item 搭建同轴光学光路，校准激光器、衍射元件、光屏中心对齐，保证入射光垂直入射。\n'
        '\\item 单缝衍射实验：逐步调节狭缝宽度，观测条纹宽窄、亮度变化规律并记录现象。\n'
        '\\item 光栅衍射实验：更换不同光栅常数的光栅，观测规则明亮条纹，验证光栅分光特性。\n'
        '\\item 缺级验证：选用满足整数比值关系的光栅，清晰观测缺级现象，记录缺级级次。\n'
        '\\item 对比分析：对比不同总缝数光栅的谱线精细度，定性验证半角宽度与分辨本领规律。\n'
        '\\end{enumerate}\n\n'
        '实验装置如图~\\ref{fig:setup}所示。',
        '实验内容与步骤', n=1)

t = rep(t, '保证实验结果可靠。',
        '保证实验结果可靠。不同缝数下观测到的衍射光强分布如图~\\ref{fig:diffraction-N}所示，(a)(b)(c)(d)依次对应 $N=1$、$N=2$、$N=5$、$N=100$，可直观看到主极大锐度随缝数增加而提高、半角宽度随之减小的规律。',
        '实验数据图引用', n=1)

# 图 label: N=1/2/5/100 子图
t = rep(t, '\\caption{N=1衍射光强分布}',
        '\\caption{$N=1$ 衍射光强分布}\n\\label{fig:diff-a}', 'fig:diff-a', n=1)
t = rep(t, '\\caption{N=2衍射光强分布}',
        '\\caption{$N=2$ 衍射光强分布}\n\\label{fig:diff-b}', 'fig:diff-b', n=1)
t = rep(t, '\\caption{N=5衍射光强分布}',
        '\\caption{$N=5$ 衍射光强分布}\n\\label{fig:diff-c}', 'fig:diff-c', n=1)
t = rep(t, '\\caption{N=100衍射光强分布}\n\\end{subfigure}\n\\end{figure}',
        '\\caption{$N=100$ 衍射光强分布}\n\\label{fig:diff-d}\n\\end{subfigure}\n\n'
        '\\caption{不同缝数下的衍射光强分布}\n\\label{fig:diffraction-N}\n\\end{figure}',
        'fig:diff-d/组图注', n=1)

# --- 视频设计与呈现 ---
t = rep(t, '全套工具均为行业主流专业软件', '全套工具均为行业主流专业软件。', '制作工具补句号', n=1)

# 三维光场演化动画: 拆分+错别字+图引用
t = rep(t, '以几何节点程序化计算 +波纹修改器为核心技术方案', '以几何节点程序化计算+波纹修改器为核心技术方案', '光场动画-空格', n=1)
t = rep(t, '三维可视化视频制作。衍射光场程序化生成 基于惠更斯-菲涅耳原理',
        '三维可视化视频制作。\n\n衍射光场程序化生成基于惠更斯-菲涅耳原理', '光场动画-拆分1', n=1)
t = rep(t, '生成起伏的三维波场曲面。 场景背景同步配套',
        '生成起伏的三维波场曲面。\n\n场景背景同步配套', '光场动画-拆分2', n=1)
t = rep(t, '理论特征完全吻合。 从三维视角可直观观察到',
        '理论特征完全吻合。\n\n从三维视角可直观观察到', '光场动画-拆分3', n=1)
t = rep(t, '准确复现了多缝衍射的条纹的特性。',
        '准确复现了多缝衍射条纹的特性。Blender 建模界面与几何节点工作流如图~\\ref{fig:blender}所示，(a)为建模界面，(b)为工作流。',
        '光场动画-错别字+图引用', n=1)

# 图 label: Blender 组
t = rep(t, '\\caption{Blender建模界面}',
        '\\caption{Blender建模界面}\n\\label{fig:blender-a}', 'fig:blender-a', n=1)
t = rep(t, '\\caption{Blender工作流}\n\\end{subfigure}\n\\end{figure}',
        '\\caption{Blender工作流}\n\\label{fig:blender-b}\n\\end{subfigure}\n\n'
        '\\caption{Blender 三维光场动画制作}\n\\label{fig:blender}\n\\end{figure}',
        'fig:blender-b/组图注', n=1)

# 二维衍射光路动画: 拆分+数学符号+图引用
t = rep(t, '动态标注缝宽a、光栅常数d、衍射角θ、光程差、相位差等关键物理量。动画使用色彩区分入射光',
        '动态标注缝宽 $a$、光栅常数 $d$、衍射角 $\\theta$、光程差、相位差等关键物理量。\n\n动画使用色彩区分入射光',
        '光路动画-拆分', n=1)
t = rep(t, '适配课堂教学的演示需求。',
        '适配课堂教学的演示需求。动画效果与代码界面如图~\\ref{fig:optical-path}所示，(a)为单缝衍射光路动画效果图，(b)为对应的 Manim 代码界面。',
        '光路动画-图引用', n=1)

# 图 label: 光路动画组
t = rep(t, '\\caption{单缝衍射光路动画效果图}',
        '\\caption{单缝衍射光路动画效果图}\n\\label{fig:path-a}', 'fig:path-a', n=1)
t = rep(t, '\\caption{单缝衍射光路动画Manim代码界面}\n\\end{subfigure}\n\\end{figure}',
        '\\caption{单缝衍射光路动画 Manim 代码界面}\n\\label{fig:path-b}\n\\end{subfigure}\n\n'
        '\\caption{二维衍射光路动画}\n\\label{fig:optical-path}\n\\end{figure}',
        'fig:path-b/组图注', n=1)

# 光强分布动画: 拆分+图引用
t = rep(t, '得到光栅衍射总光强的完整过程。针对缺级、半角宽度',
        '得到光栅衍射总光强的完整过程。\n\n针对缺级、半角宽度', '光强动画-拆分', n=1)
t = rep(t, '而不是单纯记忆数学表达式。',
        '而不是单纯记忆数学表达式。多缝干涉光强分布效果与代码界面如图~\\ref{fig:intensity}所示。',
        '光强动画-图引用', n=1)

# 图 label: 光强分布动画组
t = rep(t, '\\caption{多缝干涉光强分布效果图}',
        '\\caption{多缝干涉光强分布效果图}\n\\label{fig:inten-a}', 'fig:inten-a', n=1)
t = rep(t, '\\caption{多缝干涉光强分布Manim代码界面}\n\\end{subfigure}\n\\end{figure}',
        '\\caption{多缝干涉光强分布 Manim 代码界面}\n\\label{fig:inten-b}\n\\end{subfigure}\n\n'
        '\\caption{光强分布动画}\n\\label{fig:intensity}\n\\end{figure}',
        'fig:inten-b/组图注', n=1)

# 公式推导动画: 图引用
t = rep(t, '而非死记公式。',
        '而非死记公式。公式推导动画效果与制作代码界面如图~\\ref{fig:formula}所示，(a)为多缝干涉公式效果图，(b)为制作代码界面。',
        '公式动画-图引用', n=1)

# 图 label: 公式推导动画组
t = rep(t, '\\caption{多缝干涉公式效果图}',
        '\\caption{多缝干涉公式效果图}\n\\label{fig:form-a}', 'fig:form-a', n=1)
t = rep(t, '\\caption{多缝干涉公式制作代码界面}\n\\end{subfigure}\n\\end{figure}',
        '\\caption{多缝干涉公式制作代码界面}\n\\label{fig:form-b}\n\\end{subfigure}\n\n'
        '\\caption{公式推导动画}\n\\label{fig:formula}\n\\end{figure}',
        'fig:form-b/组图注', n=1)

# 剪辑动画: 补充说明文字
t = rep(t, '\\subsection{剪辑动画}\n\n\\begin{figure}',
        '\\subsection{剪辑动画}\n\n光栅衍射历史部分与片尾部分的剪辑界面如图~\\ref{fig:editing}所示，(a)为历史部分剪辑界面，(b)为片尾部分剪辑界面。\n\n\\begin{figure}',
        '剪辑动画-说明文字', n=1)

# 图 label: 剪辑组
t = rep(t, '\\caption{光栅衍射历史部分剪辑界面}',
        '\\caption{光栅衍射历史部分剪辑界面}\n\\label{fig:edit-a}', 'fig:edit-a', n=1)
t = rep(t, '\\caption{光栅衍射片尾部分剪辑界面}\n\\end{subfigure}\n\\end{figure}',
        '\\caption{光栅衍射片尾部分剪辑界面}\n\\label{fig:edit-b}\n\\end{subfigure}\n\n'
        '\\caption{视频剪辑界面}\n\\label{fig:editing}\n\\end{figure}',
        'fig:edit-b/组图注', n=1)

# 素材分类与规整: 拆分+图引用
t = rep(t, '五大类。实拍素材包含光刻机官方宣传片',
        '五大类。\n\n实拍素材包含光刻机官方宣传片', '素材分类-拆分1', n=1)
t = rep(t, '沉浸式背景配乐。所有素材统一分辨率',
        '沉浸式背景配乐。\n\n所有素材统一分辨率', '素材分类-拆分2', n=1)
t = rep(t, '便于剪辑整合。',
        '便于剪辑整合。剪辑草稿界面如图~\\ref{fig:draft}所示。', '素材分类-图引用', n=1)
t = rep(t, '\\caption{剪辑草稿界面}', '\\caption{剪辑草稿界面}\n\\label{fig:draft}', 'fig:draft', n=1)

# 剪辑节奏把控: 拆分+图引用
t = rep(t, '适配观众理解吸收速度；转场方式精细化区分',
        '适配观众理解吸收速度。\n\n转场方式精细化区分', '剪辑节奏-拆分', n=1)
t = rep(t, '整体节奏层次分明、观感舒适。',
        '整体节奏层次分明、观感舒适。各段配音整合的剪辑界面如图~\\ref{fig:dubbing}所示。',
        '剪辑节奏-图引用', n=1)
t = rep(t, '\\caption{汇总各段加配音剪辑界面}',
        '\\caption{汇总各段加配音剪辑界面}\n\\label{fig:dubbing}', 'fig:dubbing', n=1)

# 音画同步与包装规范: 拆分+图引用
t = rep(t, '色彩分区明确。字幕严格遵循学术规范',
        '色彩分区明确。\n\n字幕严格遵循学术规范', '音画同步-拆分', n=1)
t = rep(t, '画质达到竞赛级作品标准。',
        '画质达到竞赛级作品标准。字幕与背景音乐制作界面如图~\\ref{fig:subtitles}所示。',
        '音画同步-图引用', n=1)
t = rep(t, '\\caption{加字幕背景音乐剪辑界面}',
        '\\caption{加字幕背景音乐剪辑界面}\n\\label{fig:subtitles}', 'fig:subtitles', n=1)

# ================= 5. 附件2: 代码剥离 =================
NEW_APP2 = (
    '\\chapter*{附件2：程序代码（外部附件）}\n'
    '\\addcontentsline{toc}{chapter}{附件2：程序代码（外部附件）}\n\n'
    '为保证报告正文的紧凑性与可读性，全部 8 个程序源码文件不再内嵌于正文，而以电子附件形式随报告一并提交，存放于「代码附件」目录。各文件功能简述如下：\n\n'
    '\\begin{table}[htbp]\n'
    '\\centering\n'
    '\\small\n'
    '\\begin{tabular}{lll}\n'
    '\\toprule\n'
    '文件名 & 类型 & 功能简述 \\\\\n'
    '\\midrule\n'
    'danfenyanshe.py & Manim 动画 & 单缝衍射光路动画：入射平行光、单缝绘制、相位圆（矢量）示意、出射光角度变换与光强曲线演示 \\\\\n'
    'diffraction\\_interference.py & Manim 动画 & 光栅衍射总光强曲线演示：单缝衍射因子与多缝干涉因子相乘、半角宽度标记动画 \\\\\n'
    'shiliangtu.py & Manim 动画 & 旋转矢量法动画：$N$ 个振幅矢量首尾相接形成合矢量，演示多缝干涉相位叠加 \\\\\n'
    'guangshan.py & Manim 动画 & 光栅衍射光路动画：多缝光栅、入射平行光、波前传播与衍射角标注 \\\\\n'
    'single\\_slit.py & Manim 动画 & 单缝衍射光强分布曲线、暗纹与明纹位置标注动画 \\\\\n'
    'generate\\_figures.py & 数值仿真绘图 & 计算并绘制单缝衍射、多缝干涉、光栅总光强归一化曲线（对应图~\\ref{fig:sim-output}(a)(c)(e)） \\\\\n'
    'generate\\_fringe\\_patterns.py & 数值仿真绘图 & 由一维光强分布生成二维条纹图样（对应图~\\ref{fig:sim-output}(b)(d)(f)） \\\\\n'
    'generate\\_resolving\\_power.py & 数值仿真绘图 & 色分辨本领 $R=kN$、缺级修正及可分辨最小波长差随缝数变化曲线（对应图~\\ref{fig:resolving-N}、图~\\ref{fig:resolving-missing}、图~\\ref{fig:resolving-dlambda}） \\\\\n'
    '\\bottomrule\n'
    '\\end{tabular}\n'
    '\\end{table}\n\n'
    '以光栅衍射总光强的数值计算为例，其核心实现如下（完整源码见「代码附件」目录）：\n\n'
    '\\begin{lstlisting}[style=pycode]\n'
    'alpha = np.pi * a * sin_theta / wavelength\n'
    'beta  = np.pi * d * sin_theta / wavelength\n'
    "with np.errstate(divide='ignore', invalid='ignore'):\n"
    '    I_single = np.where(np.abs(alpha) < 1e-12, 1.0,\n'
    '                        (np.sin(alpha) / alpha) ** 2)     # 单缝衍射因子\n'
    '    I_multi  = np.where(np.abs(np.sin(beta)) < 1e-12,\n'
    '                        np.where(np.abs(beta % np.pi) < 1e-12, N**2, 0.0),\n'
    '                        (np.sin(N * beta) / np.sin(beta)) ** 2)   # 多缝干涉因子\n'
    'I_total = I_single * I_multi     # 光栅衍射总光强\n'
    '\\end{lstlisting}\n\n'
    '\\end{document}\n'
)
idx = t.index('\\section*{附件2：全部代码}')
t = t[:idx] + NEW_APP2

# ================= 6. 完整性检查 =================
checks = {
    '无残留 \\section* 星号节': '\\section*' not in t,
    '二级标题 \\section 共 16 个': t.count('\\section{') == 16,
    '三级标题 \\subsection 共 36 个': t.count('\\subsection{') == 36,
    '\\chapter 共 6 个': t.count('\\chapter{') == 6,
    '\\chapter* 共 3 个(摘要/附件1/附件2)': t.count('\\chapter*{') == 3,
    '夫琅和费已全部替换': '夫琅和费' not in t,
    '惠更斯 - 菲涅耳已全部替换': '惠更斯 - 菲涅耳' not in t,
    'thebibliography 已移除': 'thebibliography' not in t,
    'lstlisting 仅剩示例代码': t.count('\\begin{lstlisting}') == 1,
    '目录条目数(contentsline+8)': t.count('\\addcontentsline') == 3,
    '图 label 数': t.count('\\label{fig:') >= 30,
    '结束标记唯一': t.count('\\end{document}') == 1,
}
for k, v in checks.items():
    print('%-40s %s' % (k, 'OK' if v else '!!FAILED!!'))

with open(DST, 'w', encoding='utf-8') as f:
    f.write(t)
print('written:', DST, len(t.splitlines()), 'lines')
