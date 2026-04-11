import os
import re
import sys

from PySide6.QtCore import (
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
)

scale = None
screen_size = None
physical_size = None


def init_screen():
    """初始化屏幕"""
    global scale, screen_size, physical_size

    app = QApplication.instance() or QApplication(sys.argv)
    screen = app.primaryScreen()

    scale = screen.devicePixelRatio()

    geo = screen.geometry()
    screen_size = geo.width(), geo.height()
    physical_size = (
        int(screen_size[0] * scale),
        int(screen_size[1] * scale),
    )

    return


def scaled_size(size: list[int] | tuple[int, int]):
    """缩放尺寸"""
    design_scale, _, _ = get_design_metrics()
    return round(size[0] * design_scale), round(size[1] * design_scale)


def scaled(position: list[int] | tuple[int, int]):
    """将基准(1920x1080)坐标映射到实际屏幕的16:9可视区域"""
    design_scale, offset_x, offset_y = get_design_metrics()

    x = round(offset_x + position[0] * design_scale)
    y = round(offset_y + position[1] * design_scale)
    return x, y


def get_design_metrics():
    """返回基准分辨率到实际屏幕16:9可视区域的映射参数"""
    if scale is None or screen_size is None:
        raise RuntimeError("Screen is not initialized. Call init_screen() first.")

    screen_w, screen_h = screen_size
    # Qt6 的窗口几何/移动坐标使用逻辑像素，不能再额外乘 devicePixelRatio，
    # 否则会出现窗口整体偏向右下（相当于重复缩放）。
    physical_w = screen_w
    physical_h = screen_h

    target_ratio = RESOLUTION[0] / RESOLUTION[1]
    screen_ratio = physical_w / physical_h

    if screen_ratio >= target_ratio:
        visible_h = physical_h
        visible_w = visible_h * target_ratio
        offset_x = (physical_w - visible_w) / 2
        offset_y = 0
    else:
        visible_w = physical_w
        visible_h = visible_w / target_ratio
        offset_x = 0
        offset_y = (physical_h - visible_h) / 2

    design_scale = visible_w / RESOLUTION[0]
    return design_scale, offset_x, offset_y


def to_base_size(size: list[int] | tuple[int, int]):
    """将实际像素尺寸转换回基准(1920x1080)尺寸"""
    design_scale, _, _ = get_design_metrics()
    return round(size[0] / design_scale), round(size[1] / design_scale)


def scaled_font_size(point_size: int):
    """将基准字号映射到当前16:9可视区域字号"""
    design_scale, _, _ = get_design_metrics()
    return max(1, round(point_size * design_scale))


def scaled_frame(frame: QPixmap):
    """缩放帧"""
    design_scale, _, _ = get_design_metrics()
    return frame.scaled(
        round(frame.width() * design_scale),
        round(frame.height() * design_scale),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def get_res(relative_path):
    """获取资源路径"""
    if path := getattr(sys, "_MEIPASS", None):
        base_path = path
    elif getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


ALIGN_MAP = {
    Qt.AlignmentFlag.AlignLeft: "left",
    Qt.AlignmentFlag.AlignCenter: "center",
    Qt.AlignmentFlag.AlignRight: "right",
}

RESOLUTION = [1920, 1080]


def process_position(position: tuple[int | str, int | str], size: tuple[int, int]):
    """处理窗口位置（基于1080P）
    窗口位置为 mid 时，会基于窗口大小被转换为屏幕中心位置
    窗口位置含 gap + L/R/T/B + {NUM} 时，会自动转换为据屏幕 左/右/上/下 边缘 NUM 的位置
    """
    pos = [0, 0]
    for i in range(2):
        if isinstance(position[i], int):
            pos[i] = position[i]  # type: ignore
        elif position[i] == "mid":
            pos[i] = (RESOLUTION[i] - size[i]) // 2
        else:
            match = re.match(r"gap(L|R|B|T)(\d+)", position[i])  # type: ignore
            if side := match.group(1):
                gap = int(match.group(2)) if match else 20
                pos[i] = gap if side in ["L", "T"] else RESOLUTION[i] - size[i] - gap
            else:
                ValueError("Position argument is invalid.")
    return pos


class Color:
    TETO_RED = QColor("#FF7C7F")
    TETO_RED_DARK = QColor("#D87678")
    FG_COLOR = QColor("#474747")
    BG_COLOR = QColor("#F2EFF2")
