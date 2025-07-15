import os
import random
import re
from typing import List

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPixmap, QPolygon
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget


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


class ImageWindow(QMainWindow):
    def __init__(
        self,
        position: tuple[int, int],
        size: tuple[int, int],
        res_name: str,
        title: str | None = None,
    ):
        super().__init__()
        self.move(*scaled(position))
        self.resize(*scaled(size))
        if title:
            self.setWindowTitle(title)

        # 初始化窗口
        widget = QWidget()
        widget.setStyleSheet("background-color: #F2EFF2;")
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image = QLabel()
        self.image.setStyleSheet("background-color: #F2EFF2;")
        self.image.setScaledContents(True)
        layout.addWidget(self.image)

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
        self.image.setPixmap(scaled_frame(self.frames[0]))

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
        """播放帧, 可向前/向后, index 为空时切换下一帧"""
        if index is None:
            self.index = (self.index + 1) % len(self.frames)
            self.image.setPixmap(scaled_frame(self.frames[self.index]))
        elif abs(index) < len(self.frames):
            self.index = index if index > 0 else len(self.frames) + index
            self.image.setPixmap(scaled_frame(self.frames[self.index]))
        else:
            raise IndexError("Index out of range for frames.")


class DecorationShape:
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    TRIANGLE = "triangle"


class Decoration:
    def __init__(
        self,
        position: QPoint,
        shape: str = DecorationShape.CIRCLE,
        color: QColor = QColor("red"),
        size: int = 12,
        fill: bool = False,
        rotation: float = 0.0,
    ):
        self.position = position
        self.shape = shape
        self.color = color
        self.size = size
        self.fill = fill
        self.rotation = rotation


class JitterLabelWidget(QWidget):
    def __init__(
        self,
        text: str,
        text_size=18,
        text_font=QFont(),
        text_color: QColor | None = None,
        background_color: QColor = QColor("white"),
        decorations: List[Decoration] | None = None,
        parent=None,
    ):
        super().__init__(parent)

        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)

        text_font.setPointSize(text_size)
        self.label.setFont(text_font)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        self.decorations = decorations or []
        self.jitter_offsets = [QPoint(0, 0) for _ in self.decorations]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_jitter)
        if self.decorations:
            self.timer.start(333)

        self.setMinimumSize(100, 50)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), background_color)
        self.setPalette(palette)

        if text_color:
            self.label.setStyleSheet(f"color: {text_color.name()};")

    def set_text(self, text: str):
        self.label.setText(text)

    def update_jitter(self):
        self.jitter_offsets = [
            QPoint(random.randint(-8, 8), random.randint(-8, 8))
            for _ in self.decorations
        ]
        self.update()

    def paintEvent(self, event):
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


class JitterLabelWindow(QMainWindow):
    def __init__(
        self,
        position: tuple[int, int],
        size: tuple[int, int],
        title: str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__()
        self.move(*scaled(position))
        self.resize(*scaled(size))
        if title:
            self.setWindowTitle(title)

        # 初始化窗口
        widget = JitterLabelWidget(*args, **kwargs)
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image = QLabel()
        self.image.setStyleSheet("background-color: #F2EFF2;")
        self.image.setScaledContents(True)
        layout.addWidget(self.image)
