from PySide6.QtCore import QPoint, Qt, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QApplication

from components import (
    Color,
    ContainerWindow,
    DecoratedLabel,
    Decoration,
    DecorationShape,
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
                jitter_offset=8,
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

        self.window_text1 = ContainerWindow(
            DecoratedLabel(
                text_size=200,
                text_align=Qt.AlignmentFlag.AlignRight,
                decorations=[
                    Decoration(
                        position=QPoint(240, 480),
                        shape=DecorationShape.CIRCLE,
                        size=400,
                    ),
                    Decoration(
                        position=QPoint(240, 480),
                        shape=DecorationShape.CIRCLE,
                        color=Color.BG_COLOR,
                        size=200,
                    ),
                ],
            ),
            position=(147, 60),
            size=(890, 960),
            shake=True,
        )

        self.window_text2 = ContainerWindow(
            DecoratedLabel(
                text_size=160,
                text_align=Qt.AlignmentFlag.AlignRight,
                decorations=[
                    Decoration(
                        position=QPoint(300, 240),
                        shape=DecorationShape.RECTANGLE,
                        size=160,
                        rotation=45,
                    ),
                    Decoration(
                        position=QPoint(300, 240),
                        shape=DecorationShape.RECTANGLE,
                        color=Color.BG_COLOR,
                        size=80,
                        rotation=45,
                    ),
                ],
            ),
            position=(147, 60),
            size=(890, 960),
            shake=True,
        )


def main():
    app = Animation()

    app.player.play()

    # 动画序列

    def sequence_update(pos):
        if pos < 9160:
            app.player.setPosition(23000)
            return
            app.window_small_teto1.show()
            app.window_yan.show()
            app.window_zhi.show()
            app.window_small_teto1.widget.start_loop(3)
            app.window_yan.widget.start_loop(3)
            app.window_zhi.widget.start_loop(3)
        elif pos < 11791:
            app.window_small_teto1.hide()
            app.window_yan.hide()
            app.window_zhi.hide()
            app.window_starring.show()
        elif pos < 20459:
            app.window_starring.hide()
            app.window_small_teto2.show()
            app.window_small_teto2.widget.start_loop(3)
            app.window_yan.show()
            app.window_zhi.show()
        elif pos < 23000:
            app.window_yan.hide()
            app.window_zhi.hide()
            app.window_small_teto2.widget.start_loop(1)
        elif pos < 24116:
            app.window_small_teto2.hide()
            app.window_text1.setLabelText(
                "<span style='font-size:560px;'>え</span><span style='font-size:160px;'>？</span><br>　　"
            )
            app.window_text1.show()
            app.window_text1.start_shake()
        elif pos < 25360:
            app.window_text1.setLabelText(
                "<span style='font-size:560px;'>え</span><span style='font-size:160px;'>？</span><br>うそ"
            )
        elif pos < 25560:
            app.window_text1.stop_shake()
            app.window_text1.hide()
        elif pos < 26000:
            app.window_text2.show()
            app.window_text2.setLabelText("私 　　\n　　　　\n　　　　")
        elif pos < 26700:
            app.window_text2.setLabelText("私 天才\n　　　　\n　　　　")
        elif pos < 28650:
            app.window_text2.setLabelText("私 天才\nじゃない\n　の？　")

    app.player.positionChanged.connect(sequence_update)

    app.exec()


if __name__ == "__main__":
    main()
