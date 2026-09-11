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
    if norm == 0:   # 如果起点终点重合，只返回点或空箭头
        return VGroup(line)
    unit_dir = direction / norm
    # 4. 创建等腰三角形箭头
    tip = Polygon(
        np.array([0, tip_length / 2, 0]),          # 尖端顶点
        np.array([-tip_width / 2, -tip_length / 2, 0]),  # 左下
        np.array([tip_width / 2, -tip_length / 2, 0]),   # 右下
        color=color,
        fill_color=color,
        fill_opacity=1,
        stroke_width=0,   # 无描边，纯填充
    )
    # 5. 旋转使尖端指向 unit_dir（默认尖端朝上，即 (0,1,0)）
    angle = np.arctan2(unit_dir[1], unit_dir[0]) - np.pi / 2
    tip.rotate(angle, about_point=ORIGIN)
    # 6. 将箭头放置到中点
    tip.move_to(mid)
    # 7. 组合返回
    return VGroup(line, tip)
class GratingEquationDerive(Scene):
    def construct(self):
        #  全局设置
        self.camera.background_color = WHITE
        CN_FONT = "SimHei"  # 若无此字体，可改为 "Arial" 或删除 font 参数

        N=4#缝数
        d = 1.5#缝栅间距
        b=0.1#缝宽度
        theta = np.pi / 12#入射角度
        incident_length = 2.6 # 入射光长
        ls=[]
        # 2. 绘制光栅（多缝等距）
        for i in range(N+1):
            ls.append(i * d)

        grating = VGroup()
        for i in ls:
            slit = Line(
                start= i  * DOWN,
                end= (i+d-b)* DOWN,
                color=BLACK, stroke_width=8
            )
            grating.add(slit)
        grating.move_to(ORIGIN + LEFT * 5)
        #显示凸透镜
        tutou_image=SVGMobject(r"assets/svg_images/thin_convex_lens.svg")
        tutou_image.scale(3.5).shift(LEFT*2.5)
        tutou_image.set_z_index(100)
        #tutou_image=DoubleArrow(

        p_line=Line(
            start=UP*4,
            end=DOWN*4,
            color=BLACK, stroke_width=8
        )
        p_line.shift(RIGHT*3)
        self.play(FadeIn(p_line,grating,tutou_image),run_time=1.5)
        self.wait(1)
        # 3. 标注光栅常数 d
        d_line=DoubleArrow(LEFT * 5+d /2 * UP +LEFT*0.25,LEFT * 5+d /2 * DOWN +LEFT*0.25,color=BLACK,stroke_width=2,buff=0)
        d_line_U=Line(
            start=d_line.get_start()+LEFT*0.25,
            end=d_line.get_start()+RIGHT*0.25,
            color=BLACK, stroke_width=2, buff=0
        )
        d_line_D=Line(
            start=d_line.get_end()+LEFT*0.25,
            end=d_line.get_end()+RIGHT*0.25,
            color=BLACK, stroke_width=2, buff=0
        )
        d_label = MathTex(r"d",color=BLACK, font_size=30).next_to(d_line, LEFT, buff=0.2)
        d_mark=VGroup(d_line_U,d_line_D,d_label,d_line)
        self.play(Write(d_mark))
        self.wait(1)
        source=[]
        for i in range(N):
            source.append(grating[i].get_end())
        play_multi_wavefront(
            self,
            source_points=source,
            max_radius=1.5,
            speed=1.0,
            period=0.8,
            num_waves=3,
            colors=[BLACK,BLACK,BLACK,BLACK],
            show_source=False,
            show_direction=False,
        )
        # 4. 入射平行光
        incident_rays = VGroup()
        for i in range(N):
            ray = MidpointArrow(
                start=grating[i].get_end(),
end=grating[i].get_end()+RIGHT*incident_length*np.cos(theta)+UP*incident_length*np.sin(theta),
                color=BLACK, stroke_width=4
            )
            incident_rays.add(ray)
        self.play(Create(incident_rays), run_time=1,lag_ratio=0)
        self.wait(1)
        # 5. 衍射角 θ
        h_line_group = VGroup()
        for i in range(N-1):
            help_line=Line(
                start=incident_rays[i][0].get_end(),
                end=incident_rays[i][0].get_end(),
                color=BLACK, stroke_width=4
            )
            h_line=DashedLine(
                start=incident_rays[i][0].get_start(),
end=incident_rays[i][0].get_start()+DOWN*(d-0.05)*np.cos(theta)+RIGHT*(d-0.05)*np.sin(theta),
                color=BLACK, stroke_width=4
            )
            h_line_group.add(h_line)
        h_line_pin=DashedLine(
            start=incident_rays[2][0].get_start(),
            end=incident_rays[2][0].get_start()+RIGHT*d,
            color=BLACK, stroke_width=4
        )
        self.play(FadeIn(h_line_group,h_line_pin),lag_ratio=0.0)
        theta_label1 = MathTex(r"\theta", font_size=30,color=BLACK).next_to(h_line_group[0], DOWN, buff=0.2)
        theta_angle=Angle(grating[3],h_line_group[1], quadrant=(1,1), radius=0.4, color=BLACK, stroke_width=3)
        right_angle=RightAngle(incident_rays[2][0],h_line_group[1], quadrant=(-1,-1), length=0.15, color=BLACK, stroke_width=2)
        #theta_label2=theta_label1.copy().next_to(h_line_pin, UP, buff=0.1).shift(RIGHT*0.5)
        self.play(Write(theta_label1),Write(theta_angle),Write(right_angle))
        self.wait(1)
        point=np.array([3,3,0])
        out_rays = VGroup()
        for i in range(N):
            ray = MidpointArrow(
                start=incident_rays[i][0].get_end()+RIGHT*0.1,
                end=point,
                color=BLACK, stroke_width=4
            )
            out_rays.add(ray)

        ray=MidpointArrow(
            start=incident_rays[0][0].get_end(),
            end=point,
            color=BLACK, stroke_width=4
        )
        out_rays[0]=ray
        self.play(Create(out_rays), run_time=1,lag_ratio=0)
        P_dot=Dot(point,color=RED,stroke_width=6)
        P_dot_label = MathTex(r"P", font_size=30,color=RED).next_to(P_dot, RIGHT,  buff=0.2)
        self.play(Write(P_dot),Write(P_dot_label))
        self.wait(1)
def play_wavefront(
    scene,
    source_point=LEFT * 4,      # 波源位置
    max_radius=10,              # 最大扩散半径（到达后消失）
    speed=2.0,                  # 波速
    period=0.8,                 # 波前发射间隔（秒）
    num_waves=10,               # 波前数量
    color=BLUE,                 # 波前颜色
    stroke_width=3,             # 波前线宽
    start_angle=-PI / 2,        # 圆弧起始角度（右侧半圆）
    angle=PI,                   # 圆弧覆盖角度
    show_source=True,           # 是否显示波源标记
    show_direction=True,        # 是否显示传播方向箭头
):
    # 内部辅助函数：根据当前时间计算第 index 个波前的圆弧
    def get_wavefront_arc(index, current_time):
        emit_time = index * period
        radius = speed * (current_time - emit_time)
        # 尚未发出或已超出最大半径：返回空对象（不可见）
        if radius <= 0 or radius > max_radius:
            return VGroup()
        # 透明度随半径增大而降低，到达 max_radius 时完全透明（消失）
        alpha = 1 - radius / max_radius
        arc = Arc(
            radius=radius,
            start_angle=start_angle,
            angle=angle,
            arc_center=source_point,
            stroke_color=color,
            stroke_width=stroke_width,
        )
        arc.set_stroke(opacity=alpha)
        return arc
    # 时间跟踪器
    time_tracker = ValueTracker(0)
    # 动画总时长：最后一个波前发射后传播到最大半径
    total_time = (num_waves - 1) * period + max_radius / speed
    if show_source:
        source_dot = Dot(source_point, color=YELLOW)
        source_label = Text("波源", font_size=24).next_to(source_dot, DOWN)
        scene.add(source_dot, source_label)
    # 方向指示
    if show_direction:
        direction_arrow = Arrow(
            source_point,
            source_point + RIGHT * 2,
            buff=0,
            color=WHITE,
        )
        direction_label = Text("传播方向", font_size=24).next_to(direction_arrow, UP)
        scene.add(direction_arrow, direction_label)
    # 创建所有波前圆弧（使用 always_redraw 实时更新）
    wavefronts = VGroup()
    for i in range(num_waves):
        wf = always_redraw(
            lambda i=i: get_wavefront_arc(i, time_tracker.get_value())
        )
        wavefronts.add(wf)
    scene.add(wavefronts)

    # 播放动画：时间线性推进
    scene.play(
        time_tracker.animate.set_value(total_time),
        run_time=total_time,
        rate_func=linear,
    )
def play_multi_wavefront(
    scene,
    source_points,               # 波源位置列表，例如 [LEFT*4, ORIGIN, RIGHT*3]
    max_radius=10,               # 最大扩散半径（所有源统一）
    speed=2.0,                   # 波速（所有源统一）
    period=0.8,                  # 波前发射间隔（所有源统一）
    num_waves=10,                # 每个源的波前数量（统一）
    colors=None,                 # 可选：每个源的颜色列表，长度需与 source_points 一致
    stroke_width=3,              # 波前线宽
    start_angle=-PI / 2,         # 圆弧起始角度（统一，可后续扩展为列表）
    angle=PI,                    # 圆弧覆盖角度（统一）
    show_source=True,            # 是否显示波源标记
    show_direction=False,        # 是否显示传播方向（多源时通常关闭，以免箭头过多）
):

    if colors is None:
        colors = [BLUE] * len(source_points)
    else:
        assert len(colors) == len(source_points), "colors 列表长度必须与 source_points 相同"

 # 时间跟踪器（所有源共享）
    time_tracker = ValueTracker(0)
    total_time = (num_waves - 1) * period + max_radius / speed

    # 为每个波源添加标记（可选）
    if show_source:
        for pt in source_points:
            dot = Dot(pt, color=YELLOW)
            label = Text("波源", font_size=24).next_to(dot, DOWN)
            scene.add(dot, label)

    # 为每个波源添加方向指示（可选）
    if show_direction:
        for pt in source_points:
            arrow = Arrow(pt, pt + RIGHT * 2, buff=0, color=WHITE)
            scene.add(arrow)
    # 为每个波源创建波前圆弧组
    all_wavefronts = VGroup()
    for idx, (src, col) in enumerate(zip(source_points, colors)):
        # 内部辅助函数：返回第 wave_index 个波前在当前时间下的圆弧
        def get_arc(src=src, col=col, wave_index=idx, current_time=None):
            # 注意：这里 wave_index 参数被外层 idx 覆盖，实际需要为每个 wave 单独生成闭包
            pass  # 占位，实际在下方循环中创建

        # 创建该源的 num_waves 个波前
        for wave_idx in range(num_waves):
            # 使用闭包捕获 src, col, wave_idx
            def make_wavefront(src=src, col=col, wave_idx=wave_idx):
                def updater():
                    current_time = time_tracker.get_value()
                    emit_time = wave_idx * period
                    radius = speed * (current_time - emit_time)
                    if radius <= 0 or radius > max_radius:
                        return VGroup()
                    alpha = 1 - radius / max_radius
                    arc = Arc(
                        radius=radius,
                        start_angle=start_angle,
                        angle=angle,
                        arc_center=src,
                        stroke_color=col,
                        stroke_width=stroke_width,
                    )
                    arc.set_stroke(opacity=alpha)
                    return arc
                return always_redraw(updater)
            wf = make_wavefront(src, col, wave_idx)
            all_wavefronts.add(wf)
    scene.add(all_wavefronts)
    # 一次性播放整个时间推进动画
    scene.play(
        time_tracker.animate.set_value(total_time),
        run_time=total_time,
        rate_func=linear,
    )
