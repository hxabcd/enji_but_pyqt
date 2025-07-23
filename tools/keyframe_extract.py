import json
import os
import sys
import time

import cv2
import imagehash
from PIL import Image
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import DoubleSpinBox, LineEdit, PushButton, SpinBox, Theme, setTheme
from qfluentwidgets import FluentIcon as FIF


# ---------- 后台线程 ----------
class KeyframeWorker(QThread):
    progress = Signal(int)
    message = Signal(str)
    finished = Signal(bool)

    def __init__(self, src, dst, fps, hash_th, pix_th):
        super().__init__()
        self.src, self.dst = src, dst
        self.fps, self.hash_th, self.pix_th = fps, hash_th, pix_th
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        try:
            os.makedirs(self.dst, exist_ok=True)
            files = sorted(os.listdir(self.src))
            total = len(files)
            if total == 0:
                self.message.emit("输入目录为空！")
                self.finished.emit(False)
                return

            meta, last_img, last_hash, last_name = {}, None, None, None
            for i, fname in enumerate(files):
                if not self._running:
                    self.finished.emit(False)
                    return
                path = os.path.join(self.src, fname)
                img = cv2.imread(path)
                if img is None:
                    self.message.emit(f"跳过：{fname}")
                    continue

                pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                cur_hash = imagehash.phash(pil)

                if last_img is None:
                    keep = True
                else:
                    hash_diff = cur_hash - last_hash
                    diff = cv2.absdiff(img, last_img)
                    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                    pixel_ratio = cv2.countNonZero(gray) / gray.size
                    keep = hash_diff > self.hash_th or pixel_ratio > self.pix_th

                if keep:
                    cv2.imwrite(os.path.join(self.dst, fname), img)
                    last_name, last_hash, last_img = fname, cur_hash, img.copy()
                    self.message.emit(f"关键帧：{fname}")

                meta[i] = last_name
                self.progress.emit(i + 1)

            with open(
                os.path.join(self.dst, "metadata.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(meta, f, ensure_ascii=False)
            self.message.emit("完成 ✔")
            self.finished.emit(True)
        except Exception as e:
            self.message.emit(f"错误：{e}")
            self.finished.emit(False)


# ---------- 自定义可拖放输入框 ----------
class DropLineEdit(LineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setClearButtonEnabled(True)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e: QDropEvent):
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.setText(path)


# ---------- 主窗口 ----------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        setTheme(Theme.DARK)
        self.setWindowTitle("Keyframe Extractor")
        self.resize(680, 520)
        self.setAcceptDrops(True)

        # 输入/输出
        src_label = QLabel("源帧目录")
        dst_label = QLabel("输出目录")
        self.src_edit = DropLineEdit()
        self.dst_edit = DropLineEdit()
        browse_src = PushButton(FIF.FOLDER, "浏览")
        browse_dst = PushButton(FIF.FOLDER, "浏览")
        browse_src.clicked.connect(lambda: self.browse(self.src_edit))
        browse_dst.clicked.connect(lambda: self.browse(self.dst_edit))

        # 参数
        self.fps_spin = SpinBox()
        self.fps_spin.setValue(30)
        self.hash_spin = DoubleSpinBox()
        self.hash_spin.setSingleStep(0.001)
        self.hash_spin.setValue(5)
        self.pix_spin = DoubleSpinBox()
        self.pix_spin.setSingleStep(0.001)
        self.pix_spin.setValue(0.05)

        # 控制
        self.start_btn = PushButton(FIF.PLAY, "开始")
        self.stop_btn = PushButton(FIF.CLOSE, "停止")
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_task)
        self.stop_btn.clicked.connect(self.stop_task)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)

        # 日志
        self.log_edit = QTextEdit()
        self.log_edit.setMaximumHeight(180)

        # 布局
        grid = QVBoxLayout()
        for label, edit, btn in (
            (src_label, self.src_edit, browse_src),
            (dst_label, self.dst_edit, browse_dst),
        ):
            h = QHBoxLayout()
            h.addWidget(label)
            h.addWidget(edit, 1)
            h.addWidget(btn)
            grid.addLayout(h)

        para = QHBoxLayout()
        para.addWidget(QLabel("FPS", alignment=Qt.AlignmentFlag.AlignRight))
        para.addWidget(self.fps_spin)
        para.addWidget(QLabel("Hash", alignment=Qt.AlignmentFlag.AlignRight))
        para.addWidget(self.hash_spin)
        para.addWidget(QLabel("像素", alignment=Qt.AlignmentFlag.AlignRight))
        para.addWidget(self.pix_spin)

        ctrl = QHBoxLayout()
        ctrl.addWidget(self.start_btn)
        ctrl.addWidget(self.stop_btn)

        v = QVBoxLayout(self)
        v.addLayout(grid)
        v.addLayout(para)
        v.addLayout(ctrl)
        v.addWidget(self.progress)
        v.addWidget(self.log_edit)

        self.worker = None
        self.setStyleSheet("""
            QProgressBar {
                border-radius: 8px;
                text-align: center;
                background:#2c2c2c;
            }
            QProgressBar::chunk {
                border-radius: 8px;
            }
        """)

    def browse(self, line):
        path = QFileDialog.getExistingDirectory(self, "选择目录")
        if path:
            line.setText(path)

    def start_task(self):
        src, dst = self.src_edit.text(), self.dst_edit.text()
        if not src or not dst:
            self.log("请填完整路径")
            return
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress.setValue(0)
        self.log_edit.clear()

        self.worker = KeyframeWorker(
            src,
            dst,
            self.fps_spin.value(),
            self.hash_spin.value(),
            # self.pix_spin.value(),
            0.005,
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.message.connect(self.log)
        self.worker.finished.connect(self.task_done)
        self.worker.start()

    def stop_task(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.log("已取消")
            self.task_done(False)

    def task_done(self, ok):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if ok:
            self.progress.setValue(self.progress.maximum())

    def log(self, text):
        self.log_edit.append(f"[{time.strftime('%H:%M:%S')}] {text}")


# ---------- main ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
