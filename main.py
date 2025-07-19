import time
from typing import List

from PySide6.QtCore import QPoint, Qt, QUrl
from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics, QIcon, QPixmap
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
        self.setWindowIcon(QIcon("resources/teto.ico"))
        init_scale()

        # 初始化字体
        self.font_id1 = QFontDatabase.addApplicationFont("resources/mogihaPen.ttf")
        self.font_family1 = QFontDatabase.applicationFontFamilies(self.font_id1)[0]
        self.font1 = QFont(self.font_family1)
        self.setFont(self.font1)

        self.font_id2 = QFontDatabase.addApplicationFont("resources/AkazukiPOP.otf")
        self.font_family2 = QFontDatabase.applicationFontFamilies(self.font_id2)[0]
        self.font2 = QFont(self.font_family2)

        # 初始化音乐
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.player.setSource(QUrl.fromLocalFile("resources/music.m4a"))
        self.audio_output.setVolume(0.5)

        # 初始化窗口
        self.window_yan = ContainerWindow(
            SequenceFrame("frames/yan"),
            position=("gapL180", "mid"),
            size=(450, 450),
            title="胭",
        )

        self.window_zhi = ContainerWindow(
            SequenceFrame("frames/zhi"),
            position=("gapR180", "mid"),
            size=(450, 450),
            title="脂",
        )

        self.window_small_teto1 = ContainerWindow(
            SequenceFrame("frames/small_teto1"),
            position=("mid", "mid"),
            size=(620, 600),
            title="神秘红色钻头",
        )

        self.window_starring = ContainerWindow(
            DecoratedLabel(
                pixmap=QPixmap("frames/starring/0000.png"),
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
            position=("mid", "mid"),
            size=(480, 200),
            title="Starring",
        )

        self.window_small_teto2 = ContainerWindow(
            SequenceFrame("frames/small_teto2"),
            position=("mid", "mid"),
            size=(620, 600),
            title="神秘白色钻头",
        )

        self.text_left = ContainerWindow(
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
            position=("gapL80", "mid"),
            size=(890, 960),
            shake=True,
        )

        self.text_right = ContainerWindow(
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
            position=("gapR80", "mid"),
            size=(920, 780),
            shake=True,
        )

        # ウェルカムつマイマイ　ようこそ　エントリしました　それでは行きましょう　ゲームスタートです
        afont = QFont("Arial")
        self.window_emoji = ContainerWindow(
            DecoratedLabel(
                text_font=afont,
                text_size=200,
                is_bold=True,
                letter_spacing="0",
                text_color=Color.TETO_RED,
                text_align=Qt.AlignmentFlag.AlignCenter,
            ),
            position=("mid", "mid"),
            size=(1400, 840),
            title="神秘字符钻头",
            shake=False,
        )

        self.text_leftline = ContainerWindow(
            DecoratedLabel(
                text_size=90,
                text_align=Qt.AlignmentFlag.AlignLeft,
                decorations=[
                    Decoration(
                        position=QPoint(330, 80),
                        shape=DecorationShape.TRIANGLE,
                        size=100,
                    ),
                ],
                auto_resize=True,
            ),
            position=("gapL96", "mid"),
            shake=True,
        )
        # self.text_leftline.widget.label.setMinimumWidth(480)

        self.text_rightline = ContainerWindow(
            DecoratedLabel(
                text_size=90,
                text_align=Qt.AlignmentFlag.AlignRight,
                decorations=[
                    Decoration(
                        position=QPoint(330, 80),
                        shape=DecorationShape.TRIANGLE,
                        size=100,
                    ),
                ],
                auto_resize=True,
            ),
            position=("gapR96", "mid"),
            shake=True,
        )
        # self.text_rightline.widget.label.setMinimumWidth(480)

        self.text_centerline = ContainerWindow(
            DecoratedLabel(
                text_size=100,
                text_align=Qt.AlignmentFlag.AlignCenter,
                decorations=[],
                auto_resize=True,
            ),
            position=("mid", "mid"),
            size=(800, 180),
            shake=True,
        )

        window_ta_color = [Color.TETO_RED, Color.TETO_RED_DARK, Color.FG_COLOR]
        self.window_ta: List[ContainerWindow] = []
        for i in range(3):
            window = ContainerWindow(
                DecoratedLabel(
                    text="た",
                    text_size=480,
                    text_font=self.font2,
                    text_color=window_ta_color[i],
                ),
                position=(90 + i * 130, 320),
                size=(640, 640),
                title="た",
            )
            window.widget.label.setFixedSize(
                QFontMetrics(self.font2).tightBoundingRect("た").size()
            )
            self.window_ta.append(window)

        self.window_img1 = ContainerWindow(
            SequenceFrame("frames/img1"),
            position=("mid", "mid"),
            size=(640, 640),
            title="看不出是什么的神必旋转物体",
        )


def main():
    app = Animation()

    app.player.play()

    # DEBUG OPTIONS
    start_from = 56000
    stop_at = 0
    show_update = True

    # 性能计数器
    cnt = 0
    current_sec = time.localtime()

    def count():
        nonlocal cnt, current_sec
        if time.localtime() != current_sec:
            current_sec = time.localtime()
            print(f"Updated {cnt} times in 1 second")
            cnt = 0
        cnt += 1

    # 动画序列
    def sequence_update(pos):
        nonlocal start_from
        if show_update:
            count()
        if start_from and pos < start_from:
            app.player.setPosition(start_from)
            return
        if stop_at and pos > stop_at:
            app.player.stop()
            return
        if pos < 9160:
            app.window_yan.show()
            app.window_zhi.show()
            app.window_small_teto1.show()
            app.window_yan.widget.start_loop(3)
            app.window_zhi.widget.start_loop(3)
            app.window_small_teto1.widget.start_loop(3)
        elif 9160 <= pos < 11791:
            app.window_yan.hide()
            app.window_zhi.hide()
            app.window_small_teto1.hide()
            app.window_starring.show()
        elif 11791 <= pos < 14260:
            app.window_starring.hide()
            app.window_yan.show()
            app.window_zhi.show()
            app.window_small_teto2.show()
            app.window_small_teto2.widget.start_loop(3)
        elif 14260 <= pos < 14727:
            app.window_yan.hide()
            app.window_zhi.hide()
            app.window_small_teto2.hide()
            app.window_emoji.show()
            app.window_emoji.widget.update_text("▼(-_-)▼")
        elif 14272 <= pos < 20459:
            app.window_emoji.hide()
            app.window_yan.show()
            app.window_zhi.show()
            app.window_small_teto2.show()

        elif 20459 <= pos < 23000:
            app.window_yan.hide()
            app.window_zhi.hide()
            app.window_small_teto2.widget.start_loop(1)
        elif 23000 <= pos < 24116:  # え？うそ
            app.window_small_teto2.hide()
            app.text_left.show()
            app.text_left.widget.update_text(
                "<span style='font-size:560px;'>え</span><span style='font-size:160px;'>？</span><br>　　"
            )
        elif 24116 <= pos < 25360:
            app.text_left.widget.update_text(
                "<span style='font-size:560px;'>え</span><span style='font-size:160px;'>？</span><br>うそ"
            )
        elif 25360 <= pos < 25560:
            app.text_left.widget.update_text("")
            app.text_left.widget.set_decorations([])
        elif 25560 <= pos < 26000:  # 私 天才じゃないの？
            app.text_left.show()
            app.text_left.widget.set_font_size(150)
            app.text_left.widget.update_text(
                "<span style='font-size:240px;'>私</span> ——<br><br>"
            )
            app.text_left.widget.set_decorations(
                [
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
                ]
            )
        elif 26000 <= pos < 26700:
            app.text_left.widget.update_text(
                "<span style='font-size:240px;'>私</span> 天才<br>————<br>————"
            )
        elif 26700 <= pos < 28650:
            app.text_left.widget.update_text(
                "<span style='font-size:240px;'>私</span> 天才<br>じゃない<br>—の？—"
            )
        elif 28650 <= pos < 28927:
            app.text_left.hide()
        elif 28927 <= pos < 29327:  # なぜ なぜ　占い効かない
            app.text_right.show()
            app.text_right.widget.update_text(
                "<span style='font-size:240px;'>な</span>ぜ<br><span style='font-size:240px;'>—</span>—"
            )
            app.text_right.widget.set_font_size(160)
            app.text_right.widget.set_alignment(Qt.AlignmentFlag.AlignCenter)
        elif 29327 <= pos < 30300:
            app.text_right.widget.update_text(
                "<span style='font-size:240px;'>な</span>ぜ—<br>—<span style='font-size:240px;'>な</span>ぜ"
            )
        elif 30300 <= pos < 30460:
            app.text_left.widget.update_text("")
            app.text_left.widget.set_decorations([])
        elif 30460 <= pos < 31126:
            app.text_right.widget.update_text(
                "<span style='font-size:240px;'>占</span>い<br>"
            )
        elif 31126 <= pos < 32692:
            app.text_right.widget.update_text(
                "<span style='font-size:240px;'>占</span>い<br><span style='font-size:240px;'>効</span>かない"
            )
        elif 32692 <= pos < 34000:
            app.text_right.hide()
        elif 34000 <= pos < 34200:  # た た た
            app.window_ta[0].show()
        elif 34200 <= pos < 34400:
            app.window_ta[1].show()
        elif 34400 <= pos < 34600:
            app.window_ta[2].show()
        elif 34600 <= pos < 36093:  # 大変な奴 ベラベラ 何言ってんの？
            for i in range(3):
                app.window_ta[i].hide()
            app.text_leftline.show()
            app.text_leftline.widget.update_text("大変な奴")
        elif 36093 <= pos < 36993:
            app.text_rightline.show()
            app.text_rightline.widget.update_text("べうべう")
        elif 36993 <= pos < 39730:
            app.text_leftline.hide()
            app.text_rightline.hide()
            app.text_centerline.show()
            app.text_centerline.widget.update_text("何言ってんの？")
        elif 39730 <= pos < 41063:  # どうでもいいよ、普通の僕に関係ないでしょ？
            app.text_centerline.hide()
            app.text_leftline.show()
            app.text_leftline.widget.update_text("どうでもいいよ")
        elif 41063 <= pos < 42531:
            app.text_rightline.show()
            app.text_rightline.widget.update_text("普通の僕に")
        elif 42531 <= pos < 44499:
            app.text_leftline.hide()
            app.text_rightline.hide()
            app.text_centerline.show()
            app.text_centerline.widget.update_text("関係ないでしょ？")
        # 这里理应有个teto的入场动画
        elif 45898 <= pos < 46366:  # おい！そこの人間！
            app.text_centerline.hide()
            app.text_left.show()
            app.text_left.widget.set_font_size(120)
            app.text_left.widget.update_text("おい！<br>")
        elif 46366 <= pos < 48399:
            app.text_left.widget.update_text("おい！<br>そこの人間！<br>")
        elif 48399 <= pos < 48766:
            app.text_left.widget.update_text("")
        elif 48766 <= pos < 49233:  # 武器、持ってる？
            app.text_left.widget.update_text("武器、<br>")
        elif 49233 <= pos < 51300:
            app.text_left.widget.update_text("武器、<br>持ってる？<br>")
        # teto出场动画
        elif 51300 <= pos < 51632:
            app.text_left.hide()
        elif 51632 <= pos < 52698:  # 聞こえたか？聞こえたか？ 肖像 喋った
            app.text_left.show()
            app.text_left.widget.update_text("聞こえたか？<br>")
        elif 52698 <= pos < 53565:
            app.text_left.widget.update_text("聞こえたか？<br>聞こえたか？<br>")
        elif 53565 <= pos < 56365:
            app.text_left.widget.update_text(
                "聞こえたか？<br>聞こえたか？<br>肖像 喋った"
            )
        elif 56365 <= pos < 56933:
            app.text_left.hide()
        elif 56933 <= pos < 57265:
            app.text_leftline.show()
            app.text_leftline.widget.update_text("だって")
        elif 57265 <= pos < 59732:
            app.text_leftline.widget.update_text("どんなにバカ")
        elif 59732 <= pos < 60032:
            app.text_leftline.widget.update_text("でも")
        elif 60032 <= pos < 62565:
            app.text_leftline.widget.update_text("自分を撃つの")
        elif 62565 <= pos < 62900:
            app.text_leftline.widget.update_text("もっと")
        elif 62900 <= pos < 64892:
            app.text_leftline.widget.update_text("紙の上に")
        elif 64892 <= pos < 66000:
            app.text_leftline.widget.update_text("臙脂が 必要")
        elif 66000 <= pos < 66090:
            app.text_leftline.hide()
            app.window_emoji.widget.update_text("▼(-_-)▼")
            app.window_emoji.show()
        elif 66090 <= pos < 66160:
            app.window_emoji.widget.update_text("")
        elif 66160 <= pos < 66290:
            app.window_emoji.widget.update_text("▼(X_X)▼")
        elif 66290 <= pos < 66360:
            app.window_emoji.widget.update_text("")
        elif 66360 <= pos < 66460:
            app.window_emoji.widget.update_text("▼(^_^)▼")
        elif 66460 <= pos < 66525:
            app.window_emoji.widget.update_text("")
        elif 66525 <= pos < 66626:
            app.window_emoji.widget.update_text("▼(O3O)▼")
        elif 66626 <= pos < 66690:
            app.window_emoji.widget.update_text("")
        elif 66690 <= pos < 66790:
            app.window_emoji.widget.update_text("▼(=_=)▼")
        elif 66790 <= pos < 68000:
            app.window_emoji.hide()
        elif 68000 <= pos < 70770:
            app.text_leftline.widget.update_text("巨大なパレットみたい")
            app.text_leftline.show()
        elif 70770 <= pos < 71630:
            app.text_leftline.hide()
        elif 71630 <= pos < 73690:
            app.text_leftline.widget.update_text("心臓と血管")
            app.text_leftline.show()
        elif 73690 <= pos < 74430:
            app.text_leftline.widget.update_text("今日も")
        elif 74430 <= pos < 75960:
            app.text_leftline.widget.update_text("気づいてほしい")
        elif 75960 <= pos < 77000:
            app.text_leftline.widget.update_text("困ったな")
        elif 77000 <= pos < 79400:
            app.text_leftline.hide()
            app.window_small_teto2.show()
            app.window_small_teto2.widget.start_loop(3)
        elif 79400 <= pos < 79600:
            app.window_small_teto2.widget.stop_loop()
            app.window_small_teto2.hide()
        elif 79600 <= pos < 88200:
            # TODO: 军火展示.show()
            ...
        elif 88200 <= pos < 90200:
            # TODO: 军火展示.hide()
            ...
        elif 90200 <= pos < 91000:
            app.window_img1.show()
            app.window_img1.widget.start_loop(1, "rotate_frame")
        elif 91000 <= pos < 93800:
            app.text_centerline.show()
            app.text_centerline.widget.set_font_size(72)
            app.text_centerline.widget.update_text("マスカレード、突発暗殺事件")
        elif 93800 <= pos < 96600:
            app.text_centerline.widget.update_text("死者の袖口、反応する硝煙")
        elif 96600 <= pos < 99500:
            app.text_centerline.widget.update_text("エッシャーの曖昧、自らを指す両手")
        elif 99500 <= pos < 101900:
            app.text_centerline.hide()
        elif 101900 <= pos < 102400:
            app.window_img1.hide()

    app.player.positionChanged.connect(sequence_update)

    app.exec()


if __name__ == "__main__":
    main()
