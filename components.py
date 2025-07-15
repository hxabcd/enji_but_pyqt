import os
import random
import re
from dataclasses import dataclass, field
from typing import List

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPixmap, QPolygon
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


def scaled(position: tuple[int, int]):
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
    TETO_RED = "#FF7C7F"
    FG_COLOR = "#474747"
    BG_COLOR = "#F2EFF2"


class ContainerWindow(QMainWindow):
    def __init__(
        self,
        widget: QWidget,
        position: tuple[int, int],
        size: tuple[int, int],
        title: str | None = None,
    ):
        """基本容器窗口

        Args:
            widget (QWidget): 中心组件
            position (tuple[int, int]): 窗口位置
            size (tuple[int, int]): 窗口大小
            title (str | None, optional): 窗口标题
        """
        super().__init__()
        self.move(*scaled(position))
        self.resize(*scaled(size))
        if title:
            self.setWindowTitle(title)
        self.widget = widget

        # 初始化窗口
        placeholder = QWidget()
        placeholder.setStyleSheet(f"background-color: {Color.BG_COLOR};")
        self.setCentralWidget(placeholder)
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.widget, stretch=1)


class SequenceFrame(QLabel):
    def __init__(self, res_name: str):
        """序列帧组件

        Args:
            res_name (str): 序列帧资源目录，帧文件名应是数字
        """
        super().__init__()

        self.setStyleSheet(f"background-color: {Color.BG_COLOR};")
        self.setScaledContents(True)

        # 初始化序列帧
        self.frames: List[QPixmap] = []
        self.index = 0
        self.fps = 30
        self.current_loop_duration = -1

        frame_list = sorted(
            os.listdir(res_name),
            key=lambda x: int(re.match(r"\d+", x).group()),  # type: ignore
        )
        for frame in frame_list:
            path = os.path.join(res_name, frame)
            pixmap = QPixmap(path)
            self.frames.append(pixmap)
        if not self.frames:
            raise ValueError(f"No frames found in {res_name}")
        self.setPixmap(scaled_frame(self.frames[0]))

    def start_loop(self, duration: int):
        """循环播放帧"""
        if not hasattr(self, "timer"):
            self.timer = QTimer()
            self.timer.timeout.connect(self.play_frame)
        if self.timer.isActive and duration != self.current_loop_duration:
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


class DecorationShape:
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    TRIANGLE = "triangle"


@dataclass
class Decoration:
    """装饰元素类，适用于DecoratedLabel，可用的形状见DecorationShape"""

    position: QPoint
    shape: str = DecorationShape.TRIANGLE
    color: QColor = field(default_factory=lambda: QColor(Color.TETO_RED))
    size: int = 12
    fill: bool = True
    rotation: float = 0.0


class DecoratedLabel(QWidget):
    def __init__(
        self,
        text: str = "",
        text_size=18,
        text_font=QFont(),
        text_color: QColor = QColor(Color.FG_COLOR),
        pixmap: QPixmap | None = None,
        decorations: List[Decoration] | None = None,
        background_color: QColor = QColor(Color.BG_COLOR),
        jitter_frequency: int = 1000,
        jitter_offset: int = 8,
    ):
        """带有装饰几何图形的标签，几何图形可随机抖动

        Args:
            text (str, optional): 文本
            text_size (int, optional): 字号
            text_font (_type_, optional): 字体
            text_color (QColor, optional): 文本颜色
            pixmap (QPixmap | None, optional): 图像帧（QPixmap）
            decorations (List[Decoration] | None, optional): 装饰元素
            background_color (QColor, optional): 背景颜色
            jitter_frequency (int, optional): 抖动频率（ms）
            jitter_offset (int, optional): 抖动幅度
        """
        super().__init__()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 初始化标签
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.label.setStyleSheet("background-color: transparent;")

        if pixmap is not None:
            self.label.setPixmap(pixmap)
        else:
            self.label.setText(text)
            text_font.setPointSize(text_size)
            self.label.setFont(text_font)
            if text_color:
                self.label.setStyleSheet(f"color: {text_color.name()};")

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        # 初始化装饰与抖动
        self.decorations = decorations or []
        self.jitter_offsets = [QPoint(0, 0) for _ in self.decorations]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_jitter)
        if self.decorations:
            self.timer.start(jitter_frequency)

        self.jitter_offset = jitter_offset

        # 初始化背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), background_color)
        self.setPalette(palette)

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
            pen.setWidth(2)
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
