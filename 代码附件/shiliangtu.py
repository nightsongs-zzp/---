from manim import *
import numpy as np

def move_to_arc_tangent(
    arc: Arc,
    mobject: Mobject,
    buff: float = 0.5,
    t: float = 0.5,
    align_axis: np.ndarray = RIGHT
) -> Mobject:
    center = arc.arc_center
    radius = arc.radius
    start_angle = arc.start_angle
    total_angle = arc.angle
    theta = start_angle + t * total_angle
    point_on_arc = center + radius * np.array([np.cos(theta), np.sin(theta), 0])
    radial_dir = (point_on_arc - center) / radius
    tangent_dir = np.array([-np.sin(theta), np.cos(theta), 0])
    tangent_dir = tangent_dir / np.linalg.norm(tangent_dir)
    if total_angle < 0:
        tangent_dir = -tangent_dir
    new_point = point_on_arc + buff * radial_dir
    mobject.move_to(new_point)
    if np.array_equal(align_axis, RIGHT):
        current_dir = mobject.get_right() - mobject.get_center()
    elif np.array_equal(align_axis, UP):
        current_dir = mobject.get_top() - mobject.get_center()
    else:
        raise ValueError("align_axis 必须是 RIGHT 或 UP")
    if np.linalg.norm(current_dir) < 1e-9:
        current_dir = np.array([1.0, 0.0, 0.0])
    else:
        current_dir = current_dir / np.linalg.norm(current_dir)
    cross = np.cross(current_dir, tangent_dir)
    dot = np.dot(current_dir, tangent_dir)
    angle_to_rotate = np.arctan2(cross, dot)
    mobject.rotate(angle_to_rotate, about_point=mobject.get_center())
    return mobject
class GratingDerive(Scene):
    def construct(self):
        self.camera.background_color = "white"
        x_range = [-5, 5, 1]
        y_range = [-5, 5, 1]
        axis_length = 8

        axis = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=axis_length,
            y_length=axis_length,
            axis_config={"color": WHITE, "stroke_width": 0},
        )
        self.play(Write(axis))
        arrow = VGroup()
        angle = -PI * 0.7
        n = 5
        ave_angle = angle / n
        r = 3
        for i in range(n):
            x1 = r * np.sin(ave_angle * i + PI)
            y1 = r * np.cos(ave_angle * i + PI)
            x2 = r * np.sin(ave_angle * (i + 1) + PI)
            y2 = r * np.cos(ave_angle * (i + 1) + PI)
            arr_each = Arrow(
                start=axis.coords_to_point(x1, y1),
                end=axis.coords_to_point(x2, y2),
                color=BLACK, stroke_width=4, buff=0
            )
            arrow.add(arr_each)
        self.play(Write(arrow[0]), Write(arrow[1]), run_time=2/n)
        help_line=DashedLine(
            start=arrow[0].get_start(),
            end=arrow[0].get_end(),
            color=BLACK, stroke_width=2, buff=0
        )
        help_line.scale(2,about_point=arrow[0].get_start())
        self.play(Write(help_line), run_time=0.5)
        delta_label = MathTex(r"\mathbf{\delta}=2\mathbf{\beta}", font_size=30, color=BLACK)
        delta_label.next_to(help_line, UP,buff=0.1).shift(RIGHT*1.3+DOWN*0.05)
        angle=Angle(arrow[0], arrow[1], radius=0.5, color=BLACK, stroke_width=2)
        self.play(Write(delta_label), Write(angle), run_time=1,lag_ratio=0.0)
        for i in range(n-2):
            self.play(Write(arrow[i+2]), run_time=1/n)
        R = VGroup()
        for i in range(n):


            slit = Line(
                start=ORIGIN,
                end=arrow[i].get_start(),
                color=BLACK, stroke_width=2, buff=0
            )
            R.add(slit)
        slit = Line(
            start=ORIGIN,
            end=arrow[n-1].get_end(),
            color=BLACK, stroke_width=2, buff=0
        )
        R.add(slit)
        self.play(Write(R), run_time=1, lag_ratio=0.0)
        # 显示角度标记（使用 Angle 对象）
        angle_group = VGroup()
        for i in range(n):
            ang = Angle(R[i], R[i+1], radius=0.5, color=BLACK, stroke_width=2)
            angle_group.add(ang)
        self.play(Write(angle_group), run_time=1, lag_ratio=0.0)
        #  重点修改：利用 R 直接计算弧线，放置 2β 标签
        beta_group = VGroup()
        for i in range(n):
 # 获取两条线的方向向量
            dir1 = R[i].get_end() - R[i].get_start()
            dir2 = R[i+1].get_end() - R[i+1].get_start()
            angle1 = np.arctan2(dir1[1], dir1[0])
            angle2 = np.arctan2(dir2[1], dir2[0])
            delta = angle2 - angle1
            # 调整为较小夹角，保证弧线覆盖两条线之间的区域
            if delta < 0:
                start_angle = angle2
                span = -delta
            else:
                start_angle = angle1
                span = delta
            # 创建与 Angle 半径一致的 Arc 对象（只用作位置参考，不显示）
            arc = Arc(radius=0.5, start_angle=start_angle, angle=span)
            beta = MathTex(r"2\mathbf{\beta}", font_size=25, color=BLACK)
            move_to_arc_tangent(arc, beta, buff=0.3, t=0.5, align_axis=UP)
            beta_group.add(beta)
        self.play(Write(beta_group), run_time=1, lag_ratio=0.0)

        # 总箭头
        last_end = arrow[-1].get_end()
        tol_arrow = Arrow(
            start=axis.coords_to_point(0, -r),
            end=last_end,
            color=RED, stroke_width=4, buff=0, tip_length=0.2
        )
        self.play(Write(tol_arrow), run_time=0.75)
        self.wait(1)
        # 修改：移除所有辅助元素，但保留 tol_arrow
        to_fade = VGroup(
            R,
 # 从原点发出的半径线
            angle_group,     # 相邻半径线间的角度弧线
            beta_group,      # 2β 标签
            angle,           # 最初的小角度标记
            help_line,       # 虚线辅助线
            delta_label      # δ=2β 标签
            # 注意：移除了 tol_arrow，因为它需要保留并变形
        )
        self.play(FadeOut(to_fade), run_time=1)
        self.wait(0.5)
        # 将剩余箭头变换为直线首尾相接（竖直方向）
        # 计算每个箭头的长度
        lengths = [arrow[i].get_length() for i in range(n)]
        total_len = sum(lengths)

        # 竖直排列的起点：使直线居中于原点
        start_y = -total_len / 2
        # 为每个箭头生成目标位置（竖直向上，首尾相接）
        for i in range(n):
            start = np.array([0, start_y, 0])
            end = start + np.array([0, lengths[i], 0])  # 沿 y 轴正方向
            arrow[i].generate_target()
            arrow[i].target.put_start_and_end_on(start, end)
            start_y += lengths[i]  # 更新下一个箭头的起点
        # 为 tol_arrow 设置目标状态（起点 = 第一个箭头目标起点，终点 = 最后一个箭头目标终点）
        tol_arrow.generate_target()
        tol_arrow.target.put_start_and_end_on(
            arrow[0].target.get_start(),
            arrow[-1].target.get_end()
        )
        # 播放动画：所有箭头和 tol_arrow 同时移动到各自目标
        self.play(
            *[MoveToTarget(arrow[i]) for i in range(n)],
            MoveToTarget(tol_arrow),
            run_time=2,
            rate_func=smooth
        )
        self.wait(1)
