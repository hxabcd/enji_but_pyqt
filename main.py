import sys

from PySide6.QtCore import QPoint, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QApplication

from components import (
    ContainerWindow,
    DecoratedLabel,
    Decoration,
    SequenceFrame,
    init_scale,
)


class Animation(QApplication):
    def __init__(self):
        super().__init__()
        self.setApplicationName("胭脂")
        init_scale()

        # 初始化字体
        self.font_id = QFontDatabase.addApplicationFont("resources/mogihaPen.ttf")
        self.font_family = QFontDatabase.applicationFontFamilies(self.font_id)[0]
        self.setFont(QFont(self.font_family))

        self.font_bold = QFont(self.font_family)
        self.font_bold.setBold(True)

        # 初始化音乐
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.player.setSource(QUrl.fromLocalFile("resources/music.m4a"))
        self.audio_output.setVolume(0.5)

        # 初始化窗口
        self.window_yan = ContainerWindow(
            SequenceFrame("frames/yan"),
            position=(230, 342),
            size=(450, 450),
            title="胭",
        )

        self.window_zhi = ContainerWindow(
            SequenceFrame("frames/zhi"),
            position=(1280, 342),
            size=(450, 450),
            title="脂",
        )

        self.window_small_teto1 = ContainerWindow(
            SequenceFrame("frames/small_teto1"),
            position=(660, 246),
            size=(620, 600),
            title="神秘红色钻头",
        )

        self.window_starring = ContainerWindow(
            SequenceFrame("frames/starring"),
            position=(729, 445),
            size=(460, 200),
            title="Starring",
        )

        self.window_starring = ContainerWindow(
            DecoratedLabel(
                pixmap=QPixmap("frames/starring/0.png"),
                decorations=[
                    Decoration(
                        position=QPoint(64, 86),
                        size=72,
                        rotation=190,
                    ),
                    Decoration(
                        position=QPoint(366, 80),
                        size=72,
                        rotation=166,
                    ),
                ],
                jitter_frequency=333,
            ),
            position=(729, 445),
            size=(460, 200),
            title="Starring",
        )

        self.window_small_teto2 = ContainerWindow(
            SequenceFrame("frames/small_teto2"),
            position=(660, 246),
            size=(620, 600),
            title="神秘白色钻头",
        )


def main():
    app = Animation()

    app.player.play()

    # 动画序列

    def sequence_update(position):
        if 0 <= position < 9160:
            app.window_small_teto1.show()
            app.window_yan.show()
            app.window_zhi.show()
            app.window_small_teto1.widget.start_loop(3)
            app.window_yan.widget.start_loop(3)
            app.window_zhi.widget.start_loop(3)
        elif 9160 <= position < 11791:
            app.window_small_teto1.hide()
            app.window_yan.hide()
            app.window_zhi.hide()
            app.window_starring.show()
        elif 11791 <= position < 20459:
            app.window_starring.hide()
            app.window_small_teto2.show()
            app.window_small_teto2.widget.start_loop(3)
            app.window_yan.show()
            app.window_zhi.show()
        elif 20459 <= position < 23000:
            app.window_yan.hide()
            app.window_zhi.hide()
            app.window_small_teto2.widget.start_loop(1)
        elif 23000 <= position:
            app.window_small_teto2.hide()
            sys.exit()

    app.player.positionChanged.connect(sequence_update)

    app.exec()


if __name__ == "__main__":
    main()
