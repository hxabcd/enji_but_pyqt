import os
import random
import re
from dataclasses import dataclass, field
from typing import List, Literal

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPen,
    QPixmap,
    QPolygon,
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
    scale = screen.logicalDotsPerInch() / 96


def scaled(position: List[int] | tuple[int, int]):
    """缩放坐标，并减去标题栏高度"""
    return int(position[0] * scale), int((position[1] - 32) * scale)


def scaled_frame(frame: QPixmap):
    """缩放帧"""
    return frame.scaled(
        int(frame.width() * scale),
        int(frame.height() * scale),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


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
    pos = [0, 0]
    for i in range(2):
        if isinstance(position[i], int):
            pos[i] = position[i]  # type: ignore
        elif position[i] == "mid":
            pos[i] = (RESOLUTION[i] - size[i]) // 2
        else:
            match = re.match(r"gap(L|R)(\d+)", position[i])  # type: ignore
            if side := match.group(1):
                gap = int(match.group(2)) if match else 20
                pos[i] = gap if side == "L" else RESOLUTION[i] - size[i] - gap
            else:
                ValueError("Position argument is invalid.")
    return pos


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
        self.index = 0
        self.fps = 30

        frame_list = sorted(os.listdir(res_name))
        for frame in frame_list:
            path = os.path.join(res_name, frame)
            pixmap = QPixmap(path)
            self.frames.append(pixmap)
        if not self.frames:
            raise ValueError(f"No frames found in {res_name}")
        self.setPixmap(scaled_frame(self.frames[0]))

    def start_loop(
        self,
        duration: int,
        method: Literal["play_frame", "rotate_frame"] = "play_frame",
    ):
        """循环播放帧"""
        if not hasattr(self, "timer") or method != getattr(
            self, "current_method", None
        ):
            self.timer = QTimer()
            self.timer.timeout.connect(getattr(self, method))
            self.current_method = method
        if self.timer.isActive and duration != getattr(
            self, "current_loop_duration", None
        ):
            self.timer.stop()
        if not self.timer.isActive():
            self.timer.start(1000 * duration // self.fps)
            self.current_loop_duration = duration

    def stop_loop(self):
        """停止循环帧"""
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

    def play_frame(self, index: int | None = None):
        """播放帧，可向前/向后，index 为空时切换下一帧"""
        if index is None:
            self.index = (self.index + 1) % len(self.frames)
            self.setPixmap(scaled_frame(self.frames[self.index]))
        elif abs(index) < len(self.frames):
            self.index = index if index > 0 else len(self.frames) + index
            self.setPixmap(scaled_frame(self.frames[self.index]))
        else:
            raise IndexError("Index out of range for frames.")

    def rotate_frame(self, angle=1):
        """旋转帧"""
        # 貌似不可用
        transform = QPixmap(self.frames[self.index])
        painter = QPainter()
        rotated = QPixmap(transform.size())
        rotated.fill(Qt.transparent)
        painter.begin(rotated)
        center = transform.rect().center()
        painter.translate(center)
        painter.rotate(angle)
        painter.translate(-center)
        painter.drawPixmap(0, 0, transform)
        painter.end()
        self.setPixmap(scaled_frame(rotated))


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
        letter_spacing: str = "-28px",
        text_color: QColor = Color.FG_COLOR,
        text_align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
        pixmap: QPixmap | None = None,
        decorations: List[Decoration] = [],
        background_color: QColor = Color.BG_COLOR,
        jitter_frequency: int = 1000,
        jitter_offset: int = 0,
        auto_resize: bool = False,
    ):
        """带有装饰几何图形的标签，几何图形可随机抖动

        Args:
            text (str, optional): 文本
            text_size (int, optional): 字号
            text_font (QFont, optional): 字体
            text_color (QColor, optional): 文本颜色
            text_align (Qt.AlignmentFlag): 对齐方式
            pixmap (QPixmap, optional): 图像（QPixmap）
            decorations (List[Decoration], optional): 装饰元素
            background_color (QColor, optional): 背景颜色
            jitter_frequency (int, optional): 抖动频率（ms）
            jitter_offset (int, optional): 抖动幅度
        """
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
        if not (
            decorations != getattr(self, "decorations", None)
            or jitter_frequency != getattr(self, "jitter_frequency", None)
            or jitter_offset != getattr(self, "jitter_offset", None)
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
            self.label.setStyleSheet(f"""
                color: {self.color.name()};
                background-color: transparent;
                letter-spacing: {self.letter_spacing};
                text-align: {ALIGN_MAP[flag]};
            """)

    def update_text(self, text: str, resize: bool | None = None):
        if self.label.text() == text:
            return
        self.label.setText(f" {text} ")
        if resize if resize is not None else self.auto_resize:
            self.label.adjustSize()
            self.adjustSize()
            parent: ContainerWindow = self.parentWidget().parentWidget()  # type: ignore
            parent.adjustSize()
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


class ContainerWindow(QMainWindow):
    def __init__(
        self,
        widget: SequenceFrame | DecoratedLabel | QLabel,
        position: tuple[int | str, int | str],
        size: tuple[int, int] | None = None,
        title: str | None = None,
        shake: bool = False,
    ):
        """基本容器窗口

        Args:
            widget (QWidget): 中心组件
            position (tuple[int, int]): 窗口位置
            size (tuple[int, int]): 窗口大小
            title (str | None, optional): 窗口标题
        """
        super().__init__()

        self.position = position
        if title:
            self.setWindowTitle(title)
        self.widget = widget

        # 初始化窗口
        placeholder = QWidget()
        placeholder.setStyleSheet(f"background-color: {Color.BG_COLOR.name()};")
        self.setCentralWidget(placeholder)
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.widget, stretch=1)

        if size is None:
            self.adjustSize()
            self.relocate()
        else:
            self.resize(*scaled(size))
            self.move(*scaled(process_position(position, size)))

        self._current_offset = 1
        self._current_interval = 33

        if shake:
            self.start_shake()

    def relocate(self):
        size = self.size().width(), self.size().height()
        self.move(*scaled(process_position(self.position, size)))
        self._original_pos = self.pos()

    def start_shake(self, offset=1, interval=33):
        """抖动窗口

        Args:
            offset (int, optional): 抖动幅度. Defaults to 1.
            interval (int, optional): 抖动频率(ms). Defaults to 33.
        """
        if not hasattr(self, "_shake_timer"):
            self._original_pos = self.pos()
            self._shake_timer = QTimer(self)
        if (self._shake_timer.isActive() and offset != self._current_offset) or (
            self._shake_timer.isActive() and interval != self._current_interval
        ):
            self._shake_timer.stop()

        if not self._shake_timer.isActive():

            def _do_shake():
                dx = random.randint(-offset, offset)
                dy = random.randint(-offset, offset)
                self.move(self._original_pos + QPoint(dx, dy))

            self._current_offset = offset
            self._current_interval = interval

            self._shake_timer.timeout.connect(_do_shake)
            self._shake_timer.start(interval)

    def stop_shake(self):
        if hasattr(self, "_shake_timer") and self._shake_timer.isActive():
            self._shake_timer.stop()
