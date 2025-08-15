import json
import os
import random
import re
import sys
from dataclasses import dataclass, field
from typing import Callable, List, Literal

from PySide6.QtCore import (
    QEasingCurve,
    QElapsedTimer,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QHideEvent,
    QPainter,
    QPen,
    QPixmap,
    QPolygon,
    QShowEvent,
    QTransform,
    QScreen,
)
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


def init_scale():
    """初始化缩放"""
    screen = QApplication.primaryScreen()
    global scale
    screen_size = screen.size()
    # 计算基于1920x1080基准的缩放比例
    width_scale = screen_size.width() / 1920
    height_scale = screen_size.height() / 1080
    # 使用较小的缩放比例保持比例
    scale = min(width_scale, height_scale)
    # 设置环境变量
    os.environ["QT_SCALE_FACTOR"] = str(scale)


def scaled(position: List[int] | tuple[int, int]):
    """缩放坐标，并减去标题栏高度"""
    return int(position[0] * scale), int((position[1] - 16) * scale)


def scaled_frame(frame: QPixmap):
    """缩放帧"""
    return frame.scaled(
        int(frame.width() * scale),
        int(frame.height() * scale),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def get_res(relative_path):
    """获取资源路径"""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    elif getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


class Color:
    TETO_RED = QColor("#FF7C7F")
    TETO_RED_DARK = QColor("#D87678")
    FG_COLOR = QColor("#474747")
    BG_COLOR = QColor("#F2EFF2")


ALIGN_MAP = {
    Qt.AlignmentFlag.AlignLeft: "left",
    Qt.AlignmentFlag.AlignCenter: "center",
    Qt.AlignmentFlag.AlignRight: "right",
}

RESOLUTION = [1920, 1080]


def process_position(position: tuple[int | str, int | str], size: tuple[int, int]):
    """处理窗口位置
    窗口位置为mid时，会基于窗口大小被转换为屏幕中心位置
    窗口位置含gapLXX/gapRXX时，会自动转换为据屏幕边缘XX的位置
    """
    # 获取屏幕尺寸
    screen = QApplication.primaryScreen()
    screen_size = screen.size() if screen else QSize(1920, 1080)
    screen_width = screen_size.width()
    screen_height = screen_size.height()
    pos = [0, 0]
    for i in range(2):
        if isinstance(position[i], int):
            pos[i] = position[i]  # type: ignore
        elif position[i] == "mid":
            # 垂直位置调整：使用屏幕高度的45%而不是50%来避免窗口偏下
            if i == 1:  # y轴位置
                pos[i] = int(screen_height * 0.45) - size[i] // 2
            else:  # x轴位置
                pos[i] = (screen_width - size[i]) // 2
        else:
            match = re.match(r"gap(L|R)(\d+)", position[i])  # type: ignore
            if side := match.group(1):
                gap = int(match.group(2)) if match else 20
                # 使用百分比计算位置
                gap_value = int(screen_width * (gap / 1920))
                # 垂直位置调整：使用屏幕高度的45%而不是50%来避免窗口偏下
                if i == 1:  # y轴位置
                    pos[i] = int(screen_height * 0.45) - size[i] // 2
                else:  # x轴位置
                    pos[i] = gap_value if side == "L" else screen_width - size[i] - gap_value
            else:
                ValueError("Position argument is invalid.")
    return pos

class FrameController(QObject):
    def __init__(self, fps: int = 30, parent=None):
        super().__init__(parent)
        self._fps = max(1, fps)
        self._frame_duration = 1000.0 / self._fps
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.PreciseTimer)
        self._elapsed = QElapsedTimer()
        self._running = False
        self._loop = True
        self._callback = None
        self._step = 1
        self._current_step = 1  # 记录当前生效的步进值
        self._timer.setInterval(1000 // 60)
        self._timer.timeout.connect(self._on_tick)

    def start(self, callback: Callable[[], None], step: int = 1, loop: bool = True):
        step = max(1, step)

        # 已在运行，返回
        if self._running and step == self._current_step:
            return

        # step改变，更新
        if self._running:
            self._current_step = step
            self._step = step
            return

        # 启动
        self._callback = callback
        self._step = step
        self._current_step = step
        self._loop = loop
        self._elapsed.start()
        self._timer.start()
        self._running = True

    def stop(self):
        if not self._running:
            return
        self._timer.stop()
        self._running = False
        self._callback = None

    def is_running(self) -> bool:
        return self._running

    def _on_tick(self):
        if self._callback is None:
            return

        elapsed_ms = self._elapsed.elapsed()
        expected_frame = int(elapsed_ms / self._frame_duration)

        if not hasattr(self, "_last_frame"):
            self._last_frame = 0

        delta = expected_frame - self._last_frame
        if delta >= self._step:
            for _ in range(delta // self._step):
                self._callback()
            self._last_frame = expected_frame


class SequenceFrame(QLabel):
    def __init__(self, res_name: str):
        """序列帧组件

        Args:
            res_name (str): 序列帧资源目录，帧文件名应是数字
        """
        super().__init__()

        self.setStyleSheet(f"background-color: {Color.BG_COLOR.name()};")
        self.setScaledContents(True)

        # 初始化序列帧
        self.frames: List[QPixmap] = []
        self.frames_index: dict[str, int] = {}
        self.index = 0
        self.fps = 30

        # 载入帧
        frame_count = 0
        frame_list = sorted(os.listdir(res_name))
        for frame in frame_list:
            if frame == "metadata.json":
                with open(os.path.join(res_name, frame), encoding="utf-8") as f:
                    self.metadata: dict[str, str] = json.load(f)
                continue
            path = os.path.join(res_name, frame)
            pixmap = QPixmap(path)
            self.frames.append(pixmap)
            self.frames_index[frame] = frame_count
            frame_count += 1

        if not self.frames:
            raise ValueError(f"No frames found in {res_name}")
        self.setPixmap(scaled_frame(self.frames[0]))

        print(f"{res_name} is inited with {len(self.frames)} frames")

        # 初始化循环帧
        self.is_looping = False
        self.current_loop_duration = None
        self.current_method = None
        self.loop_on_show = False
        self.frame_controller = FrameController(fps=self.fps, parent=self)

    def start_loop(
        self,
        duration: int,
        method: Literal["play_frame", "play_keyframe", "rotate_frame"] = "play_frame",
    ):
        """循环播放帧"""
        callback = getattr(self, method)
        self.frame_controller.start(callback, step=duration, loop=True)

    def stop_loop(self):
        """停止循环帧"""
        self.frame_controller.stop()

    def play_frame(self, index: int | None = None):
        """播放帧，可向前/向后，index 为空时切换下一帧"""
        if index is None:
            self.index = (self.index + 1) % len(self.frames)
        elif index == self.index:
            return
        elif abs(index) < len(self.frames):
            self.index = index if index > 0 else len(self.frames) + index
        else:
            raise IndexError("Index out of range for frames.")
        self.setPixmap(scaled_frame(self.frames[self.index]))

    def play_keyframe(self):
        """从元数据播放关键帧"""
        assert self.metadata
        try:
            self.index += 1
            next_frame = self.frames[self.frames_index[self.metadata[str(self.index)]]]
            self.setPixmap(scaled_frame(next_frame))
        except KeyError:
            self.stop_loop()

    def rotate_frame(self, angle=0.5625):
        """旋转帧"""
        pixmap = self.frames[self.index]
        self.rotated_angle = angle + getattr(self, "rotated_angle", 0)

        transform = QTransform().rotate(self.rotated_angle)
        rotated = pixmap.transformed(transform, mode=Qt.SmoothTransformation)

        # 将旋转后的图像绘制回原尺寸画布中居中裁剪
        result = QPixmap(pixmap.size())
        result.fill(Qt.transparent)

        painter = QPainter(result)
        x = (pixmap.width() - rotated.width()) // 2
        y = (pixmap.height() - rotated.height()) // 2
        painter.drawPixmap(x, y, rotated)
        painter.end()

        self.setPixmap(scaled_frame(result))

    def reset_rotate(self):
        """重置旋转状态"""
        self.rotate_frame = 0
        self.setPixmap(self.frames[self.index])

    # 隐藏时停止循环，显示时恢复循环

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        if self.loop_on_show:
            self.start_loop(self.current_loop_duration, self.current_method)  # type: ignore

    def hideEvent(self, event: QHideEvent):
        super().hideEvent(event)
        if self.is_looping:
            self.loop_on_show = True
            self.stop_loop()

    def cleanup(self):
        """释放资源"""
        self.stop_loop()
        self.frames.clear()
        self.frames_index.clear()
        if hasattr(self, "metadata"):
            self.metadata.clear()


class DecorationShape:
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    TRIANGLE = "triangle"


@dataclass
class Decoration:
    """装饰元素类，适用于DecoratedLabel，可用的形状见DecorationShape"""

    position: QPoint
    shape: str = DecorationShape.TRIANGLE
    color: QColor = field(default_factory=lambda: Color.TETO_RED)
    size: int = 12
    width: int = 2
    fill: bool = True
    rotation: float = 0.0


class DecoratedLabel(QWidget):
    def __init__(
        self,
        text: str = "",
        text_size: int | None = None,
        text_font: QFont = QFont(),
        is_bold: bool = False,
        letter_spacing: str = "-16px",
        line_height: str = "1.2em",
        text_color: QColor = Color.FG_COLOR,
        text_align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
        pixmap: QPixmap | None = None,
        decorations: List[Decoration] = [],
        background_color: QColor = Color.BG_COLOR,
        jitter_frequency: int = 1000,
        jitter_offset: int = 0,
        auto_resize: bool = False,
    ):
        """带有装饰几何图形的标签，几何图形可随机抖动"""
        super().__init__()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 初始化标签
        self.label = QLabel()
        self.label.setAlignment(text_align)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.color = text_color
        self.letter_spacing = letter_spacing
        self.label.setStyleSheet(f"""
            color: {self.color.name()};
            background-color: transparent;
            letter-spacing: {self.letter_spacing};
            text-align: {ALIGN_MAP[text_align]};
        """)

        if pixmap is not None:
            self.label.setPixmap(pixmap)
        else:
            self.label.setText(text)
            self.text_font = text_font
            self.text_font.setBold(is_bold)
            if text_size:
                self.set_font_size(text_size)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        # 初始化装饰与抖动
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_jitter)
        self.set_decorations(decorations, jitter_frequency, jitter_offset)

        # 初始化背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), background_color)
        self.setPalette(palette)

        # 自动缩放
        self.auto_resize = auto_resize

    def set_decorations(
        self,
        decorations: List[Decoration],
        jitter_frequency: int = 1000,
        jitter_offset: int = 0,
    ):
        if (
            decorations == getattr(self, "decorations", None)
            and jitter_frequency == getattr(self, "jitter_frequency", None)
            and jitter_offset == getattr(self, "jitter_offset", None)
        ):
            return

        self.decorations = decorations
        self.jitter_frequency = jitter_frequency
        self.jitter_offset = jitter_offset
        self.jitter_offsets = [QPoint(0, 0) for _ in self.decorations]

        if self.decorations:
            self.timer.start(self.jitter_frequency)
        else:
            self.timer.stop()
        self.update()

    def set_font_size(self, size: int):
        self.text_font.setPointSize(size)
        self.label.setFont(self.text_font)

    def set_alignment(self, flag: Qt.AlignmentFlag):
        if self.label.alignment() != flag:
            self.label.setAlignment(flag)
            self.update_stylesheet()

    def set_letter_spacing(self, letter_spacing: str):
        """设置字间距"""
        if self.letter_spacing != letter_spacing:
            self.letter_spacing = letter_spacing
            self.update_stylesheet()

    def update_stylesheet(self):
        """更新样式表"""
        self.label.setStyleSheet(f"""
            color: {self.color.name()};
            background-color: transparent;
            letter-spacing: {self.letter_spacing};
            text-align: {ALIGN_MAP[self.label.alignment()]};
        """)

    def update_text(
        self, text: str, resize: bool | None = None, fuck: tuple[int, int] | None = None
    ):
        if self.label.text() == text:
            return
        self.label.setText(text)
        if resize if resize is not None else self.auto_resize:
            print(self.label.text())
            self.label.adjustSize()
            self.adjustSize()
            parent: ContainerWindow = self.parentWidget().parentWidget()  # type: ignore
            if fuck:
                # 操 我是真没招了 他妈的 adjustSize() 调出来一堆白的
                parent.setFixedSize(*fuck)
            else:
                parent.adjustSize()
            parent.setFixedWidth(self.size().width() + 32)
            parent.relocate()

    def update_jitter(self):
        """更新抖动"""
        self.jitter_offsets = [
            QPoint(
                random.randint(-self.jitter_offset, self.jitter_offset),
                random.randint(-self.jitter_offset, self.jitter_offset),
            )
            for _ in self.decorations
        ]
        self.update()

    def paintEvent(self, event):
        """绘制事件，这玩意AI写的，我也看不懂……"""
        super().paintEvent(event)
        if not self.decorations:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for deco, offset in zip(self.decorations, self.jitter_offsets):
            pos = deco.position + offset
            painter.save()
            painter.translate(pos)
            if deco.rotation:
                painter.rotate(deco.rotation)

            pen = QPen(deco.color)
            pen.setWidth(deco.width)
            painter.setPen(pen)
            painter.setBrush(QBrush(deco.color) if deco.fill else Qt.NoBrush)

            s = deco.size // 2
            if deco.shape == DecorationShape.CIRCLE:
                painter.drawEllipse(QPoint(0, 0), s, s)
            elif deco.shape == DecorationShape.RECTANGLE:
                painter.drawRect(-s, -s, deco.size, deco.size)
            elif deco.shape == DecorationShape.TRIANGLE:
                points = QPolygon([QPoint(0, -s), QPoint(-s, s), QPoint(s, s)])
                painter.drawPolygon(points)

            painter.restore()


class FloatLabel(QLabel):
    def __init__(self, text: str):
        super().__init__()

     # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_size = screen.size() if screen else QSize(1920, 1080)

        self.setText("56eB44GuMDcyMeOCkuimi+OBpg==")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("color: #DEDBDE;")
        self.setFont(QFont("Consolas", 28))
        self.adjustSize()
        
        # 动态计算位置
        x = (screen_size.width() - self.width()) // 2
        y = int(screen_size.height() * 0.35)  # 35%高度位置
        self.move(x,y)


class ContainerWindow(QMainWindow):
    def __init__(
        self,
        widget: SequenceFrame | DecoratedLabel | QWidget,
        position: tuple[int | str, int | str],
        size: tuple[int, int] | None = None,
        title: str | None = None,
        shake: bool = False,
    ):
        """基本容器窗口"""
        super().__init__()

        self.position = position
        if title:
            self.setWindowTitle(title)
        self.widget = widget

        # 初始化窗口
        placeholder = QWidget()
        placeholder.setStyleSheet(f"background-color: {Color.BG_COLOR.name()};")
        self.setCentralWidget(placeholder)
        self._layout = QVBoxLayout(placeholder)
        self._layout.setAlignment(Qt.AlignCenter)
        self._layout.addWidget(self.widget, stretch=1)
        self.res_name = "default"

        if size is None:
            self.adjustSize()
            self.relocate()
        else:
            self.resize(*scaled(size))
            self.move(*scaled(process_position(position, size)))

        # 初始化晃动
        self.is_shaking = False
        self.current_offset = None
        self.current_interval = None
        self.shake_on_show = False

        if shake:
            self.start_shake()

        self._lefting = False

    def preload_seqframe(self, name: str, constract: bool = True):
        if self.res_name == name:
            return
        widget = SequenceFrame(name) if name != "empty" else QWidget()
        if constract:
            self.load_widget(widget, name)
        else:
            return widget

    def load_widget(self, widget: SequenceFrame | QWidget, name: str):
        """加载组件，释放旧组件内存"""
        if self.widget is not None:
            # 释放旧组件
            self._layout.removeWidget(self.widget)
            self.widget.setParent(None)
            if hasattr(self.widget, "cleanup"):
                self.widget.cleanup()
            self.widget.deleteLater()
        self._layout.addWidget(widget)
        self.widget = widget
        if name == "empty":
            print(f"Unloaded {self.res_name}")
        else:
            print(f"Loaded {name} for {self.res_name}")
        self.res_name = name

    def unload_widget(self):
        """卸载组件"""
        self.preload_seqframe("empty")

    def relocate(self):
        size = self.width(), self.height()
        self.move(*scaled(process_position(self.position, size)))
        self._original_pos = self.pos()

    def move_to(self, position: tuple[int | str, int | str] | None = None, force=False):
        """移动窗口到指定位置"""
        if position is None:
            return
        if position == self.position and not force:
            return
        self.position = position

        size = self.width(), self.height()
        new_pos = scaled(process_position(position, size))
        if new_pos != self.pos():
            self.relocate()

    def smooth_move_to(
        self,
        target_pos: tuple[int | str, int | str],
        duration: int = 200,
        easing: QEasingCurve.Type = QEasingCurve.OutCubic,
    ):
        """平滑移动窗口"""
        if (
            hasattr(self, "_move_anim")
            and self._move_anim.state() == QPropertyAnimation.Running
        ):
            return

        self._move_anim = QPropertyAnimation(self, b"pos", self)
        self._move_anim.setDuration(duration)
        self._move_anim.setStartValue(self.pos())
        self._move_anim.setEndValue(
            QPoint(*scaled(process_position(target_pos, (self.width(), self.height()))))
        )
        self._move_anim.setEasingCurve(easing)
        self._move_anim.start()

    def start_shake(self, offset=1, interval=33):
        """抖动窗口

        Args:
            offset (int, optional): 抖动幅度. Defaults to 1.
            interval (int, optional): 抖动频率(ms). Defaults to 33.
        """
        if not hasattr(self, "timer"):
            self._original_pos = self.pos()
            self.timer = QTimer(self)
        if self.is_shaking and (
            (offset != self.current_offset) or (interval != self.current_interval)
        ):
            self.stop_shake
        if not self.is_shaking:
            self._original_pos = self.pos()

            def do_shake():
                dx = random.randint(-offset, offset)
                dy = random.randint(-offset, offset)
                self.move(self._original_pos + QPoint(dx, dy))

            self.current_offset = offset
            self.current_interval = interval

            self.timer.timeout.connect(do_shake)
            self.timer.start(interval)
            self.is_shaking = False

    def stop_shake(self):
        if hasattr(self, "shake_timer") and self.is_shaking:
            self.timer.stop()
            self.is_shaking = False

    def fancy_left(self):
        if self._lefting:
            return

        # 向右略微移动
        anim1 = QPropertyAnimation(self, b"pos", self)
        anim1.setDuration(300)
        start_pos = self.pos()
        end_pos = start_pos + QPoint(40, 0)
        anim1.setStartValue(start_pos)
        anim1.setEndValue(end_pos)
        anim1.setEasingCurve(QEasingCurve.OutCubic)

        # 向左冲出屏幕
        anim2 = QPropertyAnimation(self, b"pos", self)
        anim2.setDuration(300)
        anim2.setStartValue(end_pos)
        out_x = -self.width()
        anim2.setEndValue(QPoint(out_x, start_pos.y()))
        anim2.setEasingCurve(QEasingCurve.InCubic)

        # 串行动画
        def start_anim2():
            anim2.start()

        anim1.finished.connect(start_anim2)
        anim1.start()
        self._lefting = True

    # 隐藏时停止循环，显示时恢复循环

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if self.shake_on_show:
            self.start_shake(self.current_offset, self.current_interval)  # type: ignore

    def hideEvent(self, event: QHideEvent) -> None:
        super().hideEvent(event)
        if self.is_shaking:
            self.shake_on_show = True
            self.stop_shake()


class RopeWidget(QWidget):
    def __init__(self, target_window: QMainWindow):
        super().__init__()
        self.target_window = target_window
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 165)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor("#CDA4AB"), 4)
        painter.setPen(pen)

        screen_center = QPoint(self.width() // 2, -300)  # 固定点在屏幕外上方

        win_geom = self.target_window.geometry()
        p1 = QPoint(win_geom.left() + 64, win_geom.top() - 32)  # 左上角
        p2 = QPoint(win_geom.center().x(), win_geom.top() - 32)  # 中上
        p3 = QPoint(win_geom.right() - 64, win_geom.top() - 32)  # 右上角

        for p in [p1, p2, p3]:
            painter.drawLine(screen_center, p)


class HangingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_size = screen.size() if screen else QSize(1920, 1080)

         # 动态设置位置和大小
        width = int(screen_size.width() * 0.27)  # 屏幕宽度的27%
        height = int(screen_size.height() * 0.47)  # 屏幕高度的47%
        x = (screen_size.width() - width) // 2
        y = int(screen_size.height() * 0.15)  # 屏幕高度的15%

        self.setGeometry(704, 284, 512, 512)
        self.setWindowTitle("神秘木偶钻头")

        self.widget = SequenceFrame(get_res("frames/doll_teto"))
        self.rope = RopeWidget(self)

        placeholder = QWidget()
        placeholder.setStyleSheet(f"background-color: {Color.BG_COLOR.name()};")
        self.setCentralWidget(placeholder)
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.widget, stretch=1)

        self._drag_pos = None

    def showEvent(self, event):
        super().showEvent(event)
        self.rope.showFullScreen()

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        self.rope.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


class ZoomImageWindow(QMainWindow):
    def __init__(
        self, image_path, rect_size, duration=4000, fade_duration=1000, out_time=2000
    ):
        super().__init__()

        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_size = screen.size() if screen else QSize(1920, 1080)

        rect_size = (
            int(screen_size.width() * (rect_size[0] / 1920)),
            int(screen_size.height() * (rect_size[1] / 1080))
        )

        self.setWindowTitle("NERD TETO")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.out_time = out_time

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background: transparent;")
        self.image_label.setAttribute(Qt.WA_TranslucentBackground)
        self.image_label.setScaledContents(True)

        pixmap = QPixmap(image_path)
        self.original_pixmap = pixmap
        self.rect_size = rect_size
        self.image_label.setPixmap(
            pixmap.scaled(*rect_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # type: ignore
        )

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget = QWidget(self)
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)
        self.resize(*rect_size)

        # 缩放动画
        self.zoom_anim = QPropertyAnimation(self.image_label, b"geometry", self)
        self.zoom_anim.setDuration(duration)
        self.zoom_anim.setStartValue(
            QRect(
                (self.width() - rect_size[0]) // 2 + rect_size[0] // 4,
                (self.height() - rect_size[1]) // 2 + rect_size[1] // 4,
                rect_size[0] // 2,
                rect_size[1] // 2,
            )
        )
        self.zoom_anim.setEndValue(
            QRect(
                (self.width() - rect_size[0]) // 2,
                (self.height() - rect_size[1]) // 2,
                rect_size[0],
                rect_size[1],
            )
        )
        self.zoom_anim.setEasingCurve(QEasingCurve.OutCubic)

        # 淡入动画
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self.fade_anim.setDuration(fade_duration)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutQuad)

        # 淡出动画
        self.fade_out_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self.fade_out_anim.setDuration(fade_duration)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.InQuad)

    def fade_out(self):
        self.fade_out_anim.start()

    def showEvent(self, event):
        super().showEvent(event)
        self.image_label.setWindowOpacity(0.0)
        self.zoom_anim.start()
        self.fade_anim.start()
        QTimer.singleShot(self.out_time, self.fade_out)
