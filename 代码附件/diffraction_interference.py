from manim import *
import numpy as np
class DiffractionAndInterference(Scene):
    def construct(self):
        self.camera.background_color = WHITE
# 物理参数
        d_over_a = 4.0      # 光栅常数 / 缝宽
        N = 5               # 缝数
        # 强度函数
        def single(x):
            # 单缝衍射因子：I_single = (sin(πx)/(πx))² = sinc(x)²
            return np.sinc(x) ** 2
        def inter(x):
            # 多缝干涉因子：I_inter = (sin(Nγ)/(N sinγ))², γ = π(d/a)x
            gamma = np.pi * d_over_a * x
            with np.errstate(divide='ignore', invalid='ignore'):
                result = np.where(
                    np.abs(np.sin(gamma)) < 1e-12,
                    1.0,   # 主极大位置
                    (np.sin(N * gamma) / (N * np.sin(gamma))) ** 2
                )
            return result
        def total(x):
            return single(x) * inter(x)
        # 单缝衍射包络线（虚线）
        single_solid = axes.plot(single, x_range=x_range, color=GRAY, stroke_width=3)
        single_curve = DashedVMobject(single_solid, num_dashes=50,dashed_ratio=0.7)
        single_curve.set_color(BLUE_D).set_stroke(width=4)
        # 多缝干涉因子
        inter_curve = axes.plot(inter, x_range=x_range, color=RED, stroke_width=2)
        # 总强度曲线
        total_curve = axes.plot(total, x_range=x_range, color=PURPLE, stroke_width=4)
        #  动画流程
        # 2. 多缝干涉因子
        #self.play(FadeIn(inter_curve), run_time=3)
        #area = axes.get_area(inter_curve, x_range=[-3, 3], color=RED, opacity=0.3)
        #self.play(FadeIn(area))
        #self.wait(1)
# 之后如果曲线变化（例如改变参数），填充会自动重绘


        #  坐标轴（黑色）
        title_text = "光栅衍射：单缝衍射与多缝干涉"
        title = Text(title_text, font="SimHei", color=WHITE, font_size=32)
        title.to_edge(UP, buff=0.4)
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 1.2, 0.2],
            axis_config={"color": BLACK, "stroke_width": 2},
            tips=False,
        )
        axes.next_to(title, DOWN, buff=0.8)


        axes_labels = axes.get_axis_labels(
            y_label=MathTex(r"I/I_0", color=BLACK),
        )
        title = Text("光栅衍射：单缝衍射与多缝干涉", font_size=36, color=BLACK).to_edge(UP)

        self.play(Write(axes), Write(axes_labels))
        #self.wait(0.5)
        #  曲线
        x_range = [-3, 3, 0.001]
        # 1. 单缝衍射包络线（虚线）
        self.play(Create(single_curve), run_time=2)
        self.wait(1)
        # 3. 展示乘法关系（文字说明）
        multiply_note = Text(
            "单缝衍射因子 × 多缝干涉因子\n→ 光栅总强",
           fot_size=24, color=BLACK
        ).to_edge(DOWN)
        #self.play(Write(multiply_note))
        #self.wait(1)
        # 4. 平滑变形：干涉曲线复制变形为总强度曲线，
        #    同时单缝包络线和干涉曲线变淡，突出总强度
        self.play(
        ReplacementTransform(graph_area_group, total_curve),
        )
        self.play(total_curve.animate.set_opacity(0.7))
        #  聚焦半角宽度：横向拉伸动画
        # 1. 淡出其他曲线和标签
        fade_out_others = VGroup(
            single_curve,
            axes_labels
        )
        self.play(FadeOut(fade_out_others), run_time=1)
        self.wait(0.3)
        # 2. 计算水平拉伸比例
        #  x 范围 [-0.2,0.2] 长度 0.4
        # 希望中心区域放大，拉伸倍数 k = 6 / 0.4 = 15
        k = 15
        # 4. 第二步：创建新坐标轴并变换
        axes_new = Axes(
            x_range=[-0.2, 0.2, 0.05],
            y_range=[0, 1.2, 0.2],
            axis_config={"color": BLACK, "stroke_width": 2},
            tips=False,
        )
        axes_new.next_to(title, DOWN, buff=0.8)
        # 3. 第一步：仅水平拉伸曲线
        self.play(
            total_curve.animate.apply_function(
                lambda p: np.array([p[0] * k, p[1], p[2]])
            ),Transform(axes, axes_new),

            run_time=2,
            rate_func=smooth
        )
        self.wait(0.3)
        total_curve_correct = axes_new.plot(
            total,
            x_range=[-0.2, 0.2, 0.0001],
            color=PURPLE,
            stroke_width=4,
        )
        # 5. 标记半角宽度
        x_center = 0
        x_dark = 0.05
        y_top = 1.3
        line_center = DashedLine(
            start=axes_new.coords_to_point(x_center, 0),
end=axes_new.coords_to_point(x_center, y_top),
            color=BLACK, stroke_width=2, dash_length=0.1
        )
        line_dark = DashedLine(
            start=axes_new.coords_to_point(x_dark, 0),
            end=axes_new.coords_to_point(x_dark, y_top),
            color=BLACK, stroke_width=2, dash_length=0.1
        )
        arrow_y = 1.1
        half_width_arrow = DoubleArrow(
            start=axes_new.coords_to_point(x_center, arrow_y),
            end=axes_new.coords_to_point(x_dark, arrow_y),
            color=BLACK, buff=0,
stroke_width=3,
            tip_length=0.15
        )
        half_width_label = MathTex(r"\Delta \theta_{\text{half}}", font_size=30, color=BLACK)
        half_width_label.next_to(half_width_arrow, DOWN, buff=0.1)

        self.play(
            Create(line_center),
            Create(line_dark),
            run_time=1
        )
        self.play(
            GrowArrow(half_width_arrow),
            Write(half_width_label),
            run_time=1
        )
        self.wait(1.5)
