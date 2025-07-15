import sys

from PySide6.QtCore import QPoint, QUrl
from PySide6.QtGui import QColor
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QApplication

from components import (
    Decoration,
    DecorationShape,
    ImageWindow,
    JitterLabelWindow,
    init_scale,
)


def main():
    app = QApplication(sys.argv)
    init_scale()
    app.setApplicationName("胭脂")

    # 窗口初始化

    window_yan = ImageWindow(
        position=(230, 342),
        size=(450, 450),
        res_name="frames/yan",
        title="胭",
    )

    window_zhi = ImageWindow(
        position=(1280, 342),
        size=(450, 450),
        res_name="frames/zhi",
        title="脂",
    )

    window_small_teto1 = ImageWindow(
        position=(660, 246),
        size=(620, 600),
        res_name="frames/small_teto1",
        title="神秘红色钻头",
    )

    window_starring = JitterLabelWindow(
        position=(752, 464),
        size=(435, 164),
        title="Starring",
        text="Starring\nKasane Teto",
        text_size=32,
        text_color=QColor("#343134"),
        background_color=QColor("#F2EFF2"),
        decorations=[
            Decoration(
                position=QPoint(64, 86),
                shape=DecorationShape.TRIANGLE,
                size=72,
                color=QColor("#FF7C7F"),
                fill=True,
                rotation=190,
            ),
            Decoration(
                position=QPoint(366, 80),
                shape=DecorationShape.TRIANGLE,
                size=72,
                color=QColor("#FF7C7F"),
                fill=True,
                rotation=166,
            ),
        ],
    )

    window_small_teto2 = ImageWindow(
        position=(660, 246),
        size=(620, 600),
        res_name="frames/small_teto2",
        title="神秘白色钻头",
    )

    # 播放音乐

    player = QMediaPlayer()
    audio_output = QAudioOutput()
    player.setAudioOutput(audio_output)

    player.setSource(QUrl.fromLocalFile("music.m4a"))
    audio_output.setVolume(0.5)

    player.play()

    # 动画序列

    def sequence_update(position):
        if 0 <= position < 9160:
            window_small_teto1.show()
            window_yan.show()
            window_zhi.show()
            window_small_teto1.start_loop(3)
            window_yan.start_loop(3)
            window_zhi.start_loop(3)
        elif 9160 <= position < 11791:
            window_small_teto1.hide()
            window_yan.hide()
            window_zhi.hide()
            window_starring.show()
        elif 11791 <= position < 20459:
            window_starring.hide()
            window_small_teto2.show()
            window_small_teto2.start_loop(3)
            window_yan.show()
            window_zhi.show()
        elif 20459 <= position < 23000:
            window_yan.hide()
            window_zhi.hide()
            window_small_teto2.start_loop(1)
        elif 23000 <= position:
            window_small_teto2.hide()
            sys.exit()

    player.positionChanged.connect(sequence_update)

    app.exec()


if __name__ == "__main__":
    main()
