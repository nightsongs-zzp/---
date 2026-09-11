from manim import *
import numpy as np
def MidpointArrow(
    start: np.ndarray,
    end: np.ndarray,
    color: str = BLUE,
    stroke_width: float = 4,
    tip_length: float = 0.2,
    tip_width: float = 0.1,
    **kwargs
) -> VGroup:
    # 1. 绘制主线段（不带箭头）
    line = Line(start, end, color=color, stroke_width=stroke_width, **kwargs)
    # 2. 计算中点
    mid = (start + end) / 2
    # 3. 计算方向（从起点指向终点）
    direction = end - start
    norm = np.linalg.norm(direction)
    unit_dir = direction / norm
    # 4. 创建等腰三角形箭头（顶点朝上，即 y 轴正方向）
    tip = Polygon(
        np.array([0, tip_length / 2, 0]),          # 尖端顶点
        np.array([-tip_width / 2, -tip_length / 2, 0]),  # 左下
        np.array([tip_width / 2, -tip_length / 2, 0]),   # 右下
        color=color,
        fill_color=color,
        fill_opacity=1,
        stroke_width=0,   # 无描边，纯填充
                  )
    # 5. 旋转使尖端指向 unit_dir
    angle = np.arctan2(unit_dir[1], unit_dir[0]) - np.pi / 2
    tip.rotate(angle, about_point=ORIGIN)
    # 6. 将箭头放置到中点
    tip.move_to(mid)
    # 7. 组合返回
    return VGroup(line, tip)

class GratingDerive(Scene):
    def construct(self):
        self.camera.background_color = "white"
        #入射
        d = 0.5
        inlight = VGroup()
        for i in range(-2, 2):
            light = MidpointArrow(
                start=LEFT * 4 + (i+0.65) * d * DOWN,
                end=LEFT * 1 + (i+0.65) * d * DOWN,
                color=BLACK, stroke_width=4
                  )
            inlight.add(light)
        N_lable = Text("N条光",font="SimSun", font_size=25,color=BLACK).next_to(inlight[0][1], DOWN, buff=0.5)
        inlight.add(N_lable)
        cond1 = Text("平行光",font="SimSun", font_size=24,color=BLACK).next_to(inlight[0][0], UL, buff=0.5)
        inlight.move_to(ORIGIN + LEFT * 5)
        self.play(FadeIn(inlight))
        self.play(Write(cond1))
        self.wait(0.5)
        self.play(FadeOut(cond1))
        #单缝绘制
        fen=VGroup()
        slit = Line(
            start= 6  * UP,
            end=   0.75  * UP,
            color=BLACK, stroke_width=8
                  )
        fen.add(slit)
        slit= Line(
            start=  -6  * UP,
            end=  -0.75  * UP,
            color=BLACK, stroke_width=8
                  )
        fen.add(slit)
        self.play(FadeIn(fen))
        dbarrow=DoubleArrow(
            start=0.75*UP,
            end=0.75*DOWN,
            color=BLACK, stroke_width=4,buff=0
                  )


        a_lable=MathTex(r"a", font_size=30,color=BLACK).next_to(dbarrow, RIGHT, buff=0.1)
        self.play(FadeIn(dbarrow,a_lable))
        self.wait(0.5)
        self.play(FadeOut(dbarrow,a_lable))
        self.play(inlight.animate.move_to(ORIGIN+LEFT*1.5 ))
        bacegroup=VGroup(inlight,fen)
        self.play(bacegroup.animate.shift(LEFT*3).scale(2))
        helpline=VGroup()
        for i in range(4):
            slit= DashedLine(
                start=inlight[i][0].get_end(),
                end=inlight[i][0].get_end()+RIGHT*0.8,
                color=BLACK, stroke_width=4
                  )
            helpline.add(slit)
        for i in range(3):
            lable= MathTex(r"\frac{a}{N}", font_size=30,color=BLACK).next_to(helpline[i], DOWN, buff=0.1)
            helpline.add(lable)
        self.play(FadeIn(helpline))
        phase=VGroup()
        for i in range(4):
            phase_circle=Circle(radius=0.5,
                                color=BLACK,
                                fill_color=WHITE,
      fill_opacity=0).move_to(helpline[i].get_end()).shift(RIGHT*1.0)
            phase.add(phase_circle)
        for i in range(4):
            phase_arrow= Vector(
            direction=RIGHT* 0.5,
            color=BLACK,
            stroke_width=6
         ).move_to(phase[i].get_center()+RIGHT*0.25)
            phase.add(phase_arrow)
        cod2=Text("相位", font_size=24,color=BLACK).next_to(phase[0], UP, buff=0.5)
        #出射
        outlight=VGroup()
        for i in range(2):
            slit=Arrow(
                start=inlight[i][0].get_end(),
     end=inlight[i][0].get_end()+RIGHT*1.3,
                color=BLACK, stroke_width=4,buff=0,tip_length=0.2
                  )
            outlight.add(slit)
        self.play(FadeIn(phase,outlight))
#光的角度变换
        helpline_right_line=DashedLine(
            start=inlight[0][0].get_end(),
            end=inlight[1][0].get_end(),
            color=BLACK, stroke_width=4
                  )
        helpline_aside_line=helpline[0]
        right_angle = RightAngle(outlight[1], helpline_aside_line, length=0.2, color=BLACK,quadrant=(-1,-1))
        theta_lable= MathTex(r"\theta", font_size=25,color=BLACK).next_to(helpline[1], UP, buff=0.05)
        self.play(FadeIn(helpline_aside_line))
        self.play(FadeIn(helpline_right_line,theta_lable),helpline_aside_line.animate.rotate(0.9273,IN,about_point=helpline_aside_line.get_start()),helpline[4].animate.shift(LEFT*0.7),outlight[0].animate.rotate(0.6435,OUT,about_point=outlight[0].get_start()),            outlight[1].animate.rotate(0.6435,OUT,about_point=outlight[1].get_start()),
                  #出射角度
                  phase[4].animate.rotate(0.0,OUT,about_point=phase[4].get_start()),
                  phase[5].animate.rotate(0.3,OUT,about_point=phase[5].get_start()),
                  phase[6].animate.rotate(0.6,OUT,about_point=phase[6].get_start()),
                  phase[7].animate.rotate(0.9,OUT,about_point=phase[7].get_start()),
                  )
        self.play(FadeIn(right_angle))
        self.wait(1)
        self.play(FadeOut(phase))
        self.wait(1)
         # 光强曲线可视化
        a = 1.0
        d = 3.0
        wavelength = 1.0
        I0 = 1.0
        def intensity_func(sintheta, N):
            alpha = np.pi * a * sintheta / wavelength
            beta = np.pi * d * sintheta / wavelength
            with np.errstate(divide='ignore', invalid='ignore'):
                diff = np.square(np.sin(alpha) / alpha)
                diff[alpha == 0] = 1.0
                inter = np.square(np.sin(N * beta) / np.sin(beta))
                # 主极大处
                inter[np.abs(beta % np.pi) < 1e-8] = N**2
                inter[np.isnan(inter)] = 0
            return I0 * diff * inter
        axes = Axes(
            x_range=[-2, 2, 0.2],
            y_range=[0, 120, 20],
            axis_config={"include_numbers": False},
            x_length=10,
            y_length=5,
            color=BLACK,
                  )
        x_label = axes.get_x_axis_label(r"\sin\theta")
        y_label = axes.get_y_axis_label(r"I/I_0", edge=UP, direction=UP)

        N_values = [1]
        colors = [BLACK]
        curves = VGroup()
        labels = VGroup()
        for i, N in enumerate(N_values):
            x_vals = np.linspace(-2, 2, 200)
            y_vals = intensity_func(x_vals, N)

            curve = axes.plot_line_graph(
                x_vals, y_vals,
                line_color=colors[i],
                add_vertex_dots=False,
                stroke_width=2,
                  )
            label = Text(f"N = {N}", color=colors[i], font_size=30).to_corner(UP + RIGHT)
            if i > 0:
                label.next_to(labels[-1], DOWN, buff=0.2)
            curves.add(curve)
            labels.add(label)

        self.play(Create(axes), Write(x_label), Write(y_label))
        self.wait(1)

        for i, N in enumerate(N_values):
            self.play(Create(curves[i]), Write(labels[i]), run_time=2.0)
            self.wait(1)
