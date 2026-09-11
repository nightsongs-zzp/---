from manim import *
import numpy as np

class SingleSlitDiffraction(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        #  参数设置
        x_min, x_max = -3, 3
        #  创建坐标系
        axes = Axes(
            x_range=[x_min, x_max, 1],        # 步长改为1，对应λ/a的整数倍
            y_range=[0, 1.2, 0.2],
            axis_config={"color": BLACK, "stroke_width": 2},
            x_axis_config={
                "numbers_to_include": np.arange(x_min, x_max + 1, 1),
                "color": BLACK,
            },
            y_axis_config={
                "numbers_to_include": np.arange(0, 1.4, 0.2),
                "color": BLACK,
            },
            tips=False,
        )
        # x轴标签：λ/a
        x_label = MathTex(r"\lambda / a", color=BLACK).scale(0.8)
        _label.next_to(axes.x_axis.get_right(), DOWN, buff=0.2)
        # y轴标签：I/I₀
        y_label = MathTex(r"I / I_0", color=BLACK).scale(0.8)
        y_label.next_to(axes.y_axis.get_top(), RIGHT, buff=0.2)
        self.play(Create(axes), Write(x_label), Write(y_label))
        #  强度曲线
        intensity = lambda x: np.sinc(x) ** 2
        graph = axes.plot(
            intensity,
            x_range=[x_min, x_max],
            color="#1B088A",
            stroke_width=2.5,
        )
        shadow=axes.get_area(
            graph=graph,
            color=BLUE,
            opacity=0.3,
        )
        self.play(Create(graph), run_time=4)
        self.play(FadeIn(shadow))
        self.wait(2)
        #  在x轴下方标注关键位置数字
        # 暗纹位置：x = ±1, ±2
        # 明纹位置：x ≈ ±1.43, ±2.46
        x_positions = {
            -2.46: "-2.46",
            -2.0:  "-2",
            -1.43: "-1.43",
            -1.0:  "-1",
            0:     "0",
            1.0:   "1",
            1.43:  "1.43",
            2.0:   "2",
            2.46:  "2.46",
        }
        x_ticks = VGroup()
        for x_val, text in x_positions.items():
            tick = Text(text, color=BLACK).scale(0.35)
            tick.next_to(axes.c2p(x_val, 0), DOWN, buff=0.2)
            x_ticks.add(tick)
        self.play(Write(x_ticks), run_time=2)
        #  标记明纹位置
        bright_fringes = [
            (0,        1.0,       "1.0000"),
            (1.4303,   0.0472,    "0.0472"),
            (-1.4303,  0.0472,    "0.0472"),
            (2.4590,   0.0165,    "0.0165"),
            (-2.4590,  0.0165,    "0.0165"),
        ]
        for x_val, i_val, i_text in bright_fringes:
            # 红点标记明纹位置
            point = Dot(axes.c2p(x_val, i_val), color=RED, radius=0.08)

            # I/I₀ 数值标注在点上方
            label = MathTex(r"I/I_0 = " + i_text, color=RED).scale(0.5)
            label.next_to(point, UP, buff=0.15)
            self.play(
                FadeIn(point),
                Write(label),
                run_time=0.6
            )

        self.wait(3)
