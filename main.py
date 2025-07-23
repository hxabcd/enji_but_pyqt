try:
    import ctypes
    import os
    import time
    from typing import List

    from PySide6.QtCore import QPoint, Qt, QTimer, QUrl
    from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics, QIcon, QPixmap
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
    from PySide6.QtWidgets import QApplication, QWidget
    from win11toast import notify

    from components import (
        Color,
        ContainerWindow,
        DecoratedLabel,
        Decoration,
        DecorationShape,
        FloatLabel,
        HangingWindow,
        SequenceFrame,
        ZoomImageWindow,
        get_res,
        init_scale,
    )

    class Animation(QApplication):
        def __init__(self):
            super().__init__()
            self.setApplicationName("胭脂")
            self.setWindowIcon(QIcon(get_res("resources/teto.ico")))
            init_scale()

            # 初始化字体
            self.font_id1 = QFontDatabase.addApplicationFont(
                get_res("resources/mogihaPen.ttf")
            )
            self.font_family1 = QFontDatabase.applicationFontFamilies(self.font_id1)[0]
            self.font1 = QFont(self.font_family1)
            self.setFont(self.font1)

            self.font_id2 = QFontDatabase.addApplicationFont(
                get_res("resources/AkazukiPOP_subset.otf")
            )
            self.font_family2 = QFontDatabase.applicationFontFamilies(self.font_id2)[0]
            self.font2 = QFont(self.font_family2)

            # 初始化音乐
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)

            self.player.setSource(QUrl.fromLocalFile(get_res("resources/music.m4a")))
            self.audio_output.setVolume(0.5)

            # 初始化窗口
            self.yan = ContainerWindow(
                QWidget(),
                position=("gapL160", "mid"),
                size=(450, 450),
                title="胭",
            )

            self.zhi = ContainerWindow(
                QWidget(),
                position=("gapR160", "mid"),
                size=(450, 450),
                title="脂",
            )

            self.small_teto1 = ContainerWindow(
                QWidget(),
                position=("mid", "mid"),
                size=(620, 600),
                title="神秘红色钻头",
            )

            self.starring = ContainerWindow(
                DecoratedLabel(
                    pixmap=QPixmap(get_res("resources/starring.png")),
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

            self.small_teto2 = ContainerWindow(
                QWidget(),
                position=("mid", "mid"),
                size=(620, 600),
                title="神秘白色钻头",
            )

            self.small_teto3 = ContainerWindow(
                QWidget(),
                position=("mid", "mid"),
                size=(496, 480),
                title="神秘白色钻头",
            )

            self.text_left = ContainerWindow(
                DecoratedLabel(
                    text_size=200,
                    text_align=Qt.AlignmentFlag.AlignRight,
                    decorations=[
                        Decoration(
                            position=QPoint(240, 440),
                            shape=DecorationShape.CIRCLE,
                            size=400,
                        ),
                        Decoration(
                            position=QPoint(240, 440),
                            shape=DecorationShape.CIRCLE,
                            color=Color.BG_COLOR,
                            size=240,
                        ),
                    ],
                ),
                position=("gapL32", "mid"),
                size=(890, 900),
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
                position=("gapR32", "mid"),
                size=(890, 900),
                shake=True,
            )

            # ウェルカムつマイマイ　ようこそ　エントリしました　それでは行きましょう　ゲームスタートです
            afont = QFont("Arial")
            self.kaomoji = ContainerWindow(
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

            # 代码添加日期 2025/07/21
            self.onani64 = FloatLabel("56eB44GuMDcyMeOCkuimi+OBpg==")

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
            self.ta: List[ContainerWindow] = []
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
                self.ta.append(window)

            self.hanging_teto = HangingWindow()

            self.rotating_object = ContainerWindow(
                QWidget(),
                position=("mid", "mid"),
                size=(640, 640),
                title="看不出是什么的神必旋转物体",
            )

            self.nerd_teto = ZoomImageWindow(
                get_res("resources/nerd_teto.jpg"), (553, 500)
            )

            self.gome_teto = ContainerWindow(
                DecoratedLabel(pixmap=QPixmap(get_res("resources/gome_teto.jpg"))),
                position=("mid", "mid"),
                title="果咩纳塞",
            )

            self.minecraft_teto = ZoomImageWindow(
                get_res("resources/minecraft_teto.jpg"),
                (1415, 900),
                duration=1600,
                fade_duration=600,
                out_time=1000,
            )

            self.text_end = ContainerWindow(
                DecoratedLabel(text="thanks for watching", text_size=84),
                position=("gapL160", "mid"),
                title="感谢观看！给个三连吧www",
                shake=True,
            )

            self.teto = ContainerWindow(
                QWidget(),
                position=("gapR32", "mid"),
                size=(950, 900),
                title="TETO",
            )
            # self.teto.setWindowFlags(Qt.WindowStaysOnTopHint)

    def main():
        app = Animation()

        # 预加载
        # 妈的，放在动画序列里预加载要阻塞一秒，真没招了
        # 傻逼 PyQt 不能在子线程预加载
        # 不管内存了 直接全局预载
        teto4: SequenceFrame = app.teto.preload_seqframe(
            get_res("frames/teto4"), constract=False
        )  # type: ignore
        app.teto.preload_seqframe(get_res("frames/teto1"))
        app.flag = 1

        # 载入调试选项
        debug = os.getenv("DEBUG", "false").lower() == "true"
        start_from = int(os.getenv("START_FROM", "0"))
        stop_at = int(os.getenv("STOP_AT", "0"))
        show_update = os.getenv("SHOW_UPDATE", "false").lower() == "true"
        hide_taskbar = os.getenv("HIDE_TASKBAR", "false").lower() == "true"

        # 隐藏任务栏
        if hide_taskbar:
            taskbar_hwnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
            ctypes.windll.user32.ShowWindow(taskbar_hwnd, 0)  # SW_HIDE

            def show_taskbar():
                ctypes.windll.user32.ShowWindow(taskbar_hwnd, 1)

            app.aboutToQuit.connect(show_taskbar)

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
            if debug:
                if show_update:
                    count()
                if start_from and pos < start_from:
                    app.player.setPosition(start_from)
                    return
                if stop_at and pos > stop_at:
                    app.player.stop()
                    return

            if 0 <= pos < 700:
                app.yan.preload_seqframe(get_res("frames/yan"))
                app.zhi.preload_seqframe(get_res("frames/zhi"))
                app.small_teto1.preload_seqframe(get_res("frames/small_teto1"))
            elif 700 <= pos < 9160:
                app.yan.show()
                app.zhi.show()
                app.small_teto1.show()
                app.yan.widget.start_loop(3)
                app.zhi.widget.start_loop(3)
                app.small_teto1.widget.start_loop(3)
            elif 9160 <= pos < 11791:
                app.yan.hide()
                app.zhi.hide()
                app.small_teto1.hide()
                app.small_teto2.preload_seqframe(get_res("frames/small_teto2"))
                if hasattr(app.small_teto1.widget, "index"):
                    app.small_teto2.widget.play_frame(app.small_teto1.widget.index)
                app.small_teto1.unload_widget()
                app.starring.show()
            elif 11791 <= pos < 14260:
                app.starring.hide()
                app.starring.unload_widget()
                app.yan.show()
                app.zhi.show()
                app.small_teto2.show()
                app.small_teto2.widget.start_loop(3)
            elif 14260 <= pos < 14727:
                app.yan.hide()
                app.zhi.hide()
                app.small_teto2.hide()
                app.kaomoji.show()
                app.kaomoji.widget.update_text("▼(-_-)▼")
                app.onani64.show()
            elif 14272 <= pos < 20459:
                app.kaomoji.hide()
                app.onani64.hide()
                app.yan.show()
                app.zhi.show()
                app.small_teto2.show()
            elif 20459 <= pos < 23000:
                app.yan.hide()
                app.zhi.hide()
                app.small_teto2.widget.start_loop(1)
            elif 23000 <= pos < 24116:  # え？うそ
                app.small_teto2.hide()
                app.yan.unload_widget()
                app.zhi.unload_widget()
                app.small_teto2.unload_widget()

                app.text_left.show()
                app.text_left.widget.update_text(
                    "<span style='font-size:560px;'>え</span><span style='font-size:200px;'>？</span><br>——"
                )

                app.teto.show()
                app.teto.relocate()
                app.teto.widget.start_loop(1, "play_keyframe")

            elif 24116 <= pos < 25360:
                app.text_left.widget.update_text(
                    "<span style='font-size:560px;'>え</span><span style='font-size:200px;'>？</span><br>うそ"
                )
            elif 25360 <= pos < 25560:
                app.text_left.widget.update_text("")
                app.text_left.widget.set_decorations([])
            elif 25560 <= pos < 26000:  # 私 天才じゃないの？
                app.text_left.show()
                app.text_left.widget.set_alignment(Qt.AlignmentFlag.AlignLeft)
                app.text_left.widget.set_font_size(140)
                app.text_left.widget.update_text(
                    "<span style='font-size:320px;'>私</span> ——<br>————<br>————"
                )
                app.text_left.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(300, 200),
                            shape=DecorationShape.RECTANGLE,
                            size=160,
                            rotation=45,
                        ),
                        Decoration(
                            position=QPoint(300, 200),
                            shape=DecorationShape.RECTANGLE,
                            color=Color.BG_COLOR,
                            size=80,
                            rotation=45,
                        ),
                    ]
                )
            elif 26000 <= pos < 26700:
                app.text_left.widget.update_text(
                    "<span style='font-size:320px;'>私</span> 天才<br>————<br>————"
                )
            elif 26700 <= pos < 28600:
                app.text_left.widget.update_text(
                    "<span style='font-size:320px;'>私</span> 天才<br>じゃない<br>—の？—"
                )
            elif 28600 <= pos < 28800:
                app.text_left.hide()
                app.teto.preload_seqframe(get_res("frames/teto2"))
                app.teto.smooth_move_to(("gapL32", "mid"))
            elif 28800 <= pos < 29327:  # なぜ なぜ　占い効かない
                app.teto.widget.start_loop(1, "play_keyframe")
                app.text_right.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(330, 240),
                            shape=DecorationShape.CIRCLE,
                            size=160,
                            rotation=45,
                        ),
                        Decoration(
                            position=QPoint(330, 240),
                            shape=DecorationShape.CIRCLE,
                            color=Color.BG_COLOR,
                            size=80,
                            rotation=45,
                        ),
                    ]
                )
                app.text_right.show()
                app.text_right.widget.update_text(
                    "<span style='font-size:240px;'>な</span>ぜ—<br><span style='font-size:240px;'>—</span>—"
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
                app.text_right.widget.set_alignment(Qt.AlignmentFlag.AlignCenter)
                app.text_right.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(250, 450),
                            shape=DecorationShape.RECTANGLE,
                            size=160,
                            rotation=45,
                        ),
                        Decoration(
                            position=QPoint(250, 450),
                            shape=DecorationShape.RECTANGLE,
                            color=Color.BG_COLOR,
                            size=80,
                            rotation=45,
                        ),
                    ]
                )
                app.text_right.widget.set_font_size(160)
                app.text_right.widget.update_text(
                    "<span style='font-size:200px;'>占</span>い<br><span style='font-size:200px;'>—</span>———"
                )
            elif 31126 <= pos < 32692:
                app.text_right.widget.update_text(
                    "<span style='font-size:200px;'>占</span>い<br><span style='font-size:200px;'>効</span>かない"
                )
            elif 32692 <= pos < 34000:
                app.text_right.hide()
                app.teto.hide()
                app.teto.unload_widget()
            elif 34000 <= pos < 34200:  # た た た
                app.ta[0].show()
            elif 34200 <= pos < 34400:
                app.ta[1].show()
            elif 34400 <= pos < 34600:
                app.ta[2].show()
            elif 34600 <= pos < 36093:  # 大変な奴 ベラベラ 何言ってんの？
                for i in range(3):
                    app.ta[i].hide()
                app.text_leftline.show()
                app.hanging_teto.show()
                app.text_leftline.widget.update_text("大変な奴")
                app.text_leftline.raise_()
            elif 36093 <= pos < 36993:
                app.text_rightline.show()
                app.text_rightline.widget.update_text("べうべう")
            elif 36993 <= pos < 39730:
                app.text_leftline.hide()
                app.text_rightline.hide()
                app.text_rightline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(420, 55),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=135,
                        ),
                    ]
                )
                app.text_centerline.show()
                app.text_centerline.widget.update_text("何言ってんの？")
            elif 39730 <= pos < 41063:  # どうでもいいよ、普通の僕に関係ないでしょ？
                app.text_centerline.hide()
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(200, 50),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )
                app.text_leftline.show()
                app.text_leftline.widget.update_text("どうでもいいよ")
            elif 41063 <= pos < 42531:
                app.text_rightline.show()
                app.text_rightline.widget.update_text("普通の僕に")
            elif 42531 <= pos < 44400:
                app.text_leftline.hide()
                app.text_rightline.hide()
                app.text_centerline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(780, 80),
                            shape=DecorationShape.CIRCLE,
                            size=60,
                        ),
                    ]
                )
                app.text_centerline.show()
                app.text_centerline.widget.update_text("関係ないでしょ？")
            elif 44400 <= pos < 45500:
                app.text_centerline.hide()
                app.hanging_teto.hide()
                app.teto.preload_seqframe(get_res("frames/teto3"))
            elif 45500 <= pos < 45800:
                app.teto.show()
                app.teto.move_to(("gapR32", "mid"))
                app.teto.relocate()
                app.teto.widget.start_loop(1, "play_keyframe")
            elif 45800 <= pos < 46366:  # おい！そこの人間！
                app.text_left.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(200, 180),
                            shape=DecorationShape.RECTANGLE,
                            size=130,
                            rotation=45,
                        ),
                    ]
                )
                app.text_left.widget.set_alignment(Qt.AlignmentFlag.AlignLeft)
                app.text_left.show()
                app.text_left.widget.set_font_size(120)
                app.text_left.widget.update_text("おい！<br>")
                app.teto.raise_()
            elif 46366 <= pos < 48399:
                app.text_left.widget.update_text("おい！<br>そこの<br>人間！<br>")
            elif 48399 <= pos < 48766:
                app.text_left.widget.update_text("")
                app.text_left.widget.set_decorations([])
            elif 48766 <= pos < 49233:  # 武器、持ってる？
                app.text_left.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(200, 200),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )

                app.text_left.widget.update_text("武器、<br>")
            elif 49233 <= pos < 51300:
                app.text_left.widget.update_text("武器、<br>持ってる？<br>")
            elif 51300 <= pos < 51632:
                app.text_left.hide()
                app.teto.hide()
                app.teto.unload_widget()
            elif 51632 <= pos < 52700:  # 聞こえたか？聞こえたか？ 肖像 喋った
                app.text_left.show()
                app.text_left.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(140, 80),
                            shape=DecorationShape.TRIANGLE,
                            size=130,
                            rotation=15,
                        ),
                    ]
                )
                app.text_left.widget.set_font_size(120)
                app.text_left.widget.set_alignment(Qt.AlignmentFlag.AlignLeft)
                app.text_left.widget.update_text(
                    "<p style='line-height:125%'>聞こえたか？<br>———————<br>———— ———</p>"
                )
            elif 52700 <= pos < 53500:
                app.text_left.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(140, 80),
                            shape=DecorationShape.TRIANGLE,
                            size=130,
                            rotation=15,
                        ),
                        Decoration(
                            position=QPoint(230, 300),
                            shape=DecorationShape.TRIANGLE,
                            size=130,
                            rotation=320,
                        ),
                    ]
                )
                app.text_left.widget.update_text(
                    "<p style='line-height:125%'>聞こえたか？<br>—聞こえたか？<br>———— ———</p>"
                )
            elif 53500 <= pos < 56300:
                app.text_left.widget.update_text(
                    "<p style='line-height:125%'>聞こえたか？<br>—聞こえたか？<br>——肖像 喋った</p>"
                )
            elif 56300 <= pos < 56800:
                app.text_left.hide()
                if app.teto.res_name != get_res("frames/teto4"):
                    app.teto.load_widget(teto4, get_res("frames/teto4"))
                    teto4.clear()
            elif 56800 <= pos < 57265:
                app.teto.show()
                app.teto.relocate()
                app.teto.widget.start_loop(1, "play_keyframe")
                app.text_leftline.widget.set_decorations([])
                app.text_leftline.show()
                app.text_leftline.widget.update_text("だって")
            elif 57265 <= pos < 59732:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("どんなにバカ")
            elif 59732 <= pos < 60032:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.CIRCLE,
                            size=100,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("でも")
            elif 60032 <= pos < 62565:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("自分を撃つの")
            elif 62565 <= pos < 62900:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.CIRCLE,
                            size=100,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("もっと")
            elif 62900 <= pos < 64892:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("紙の上に")
            elif 64892 <= pos < 66000:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.CIRCLE,
                            size=100,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("臙脂が 必要")
            elif 66000 <= pos < 66090:
                app.text_leftline.hide()
                app.teto.hide()
                app.teto.unload_widget()
                app.kaomoji.show()
                app.kaomoji.widget.update_text("▼(-_-)▼")
                app.kaomoji.move_to(("mid", "mid"))
            elif 66090 <= pos < 66160:
                app.kaomoji.widget.update_text("")
            elif 66160 <= pos < 66290:
                app.kaomoji.widget.update_text("▼(X_X)▼")
            elif 66290 <= pos < 66360:
                app.kaomoji.widget.update_text("")
            elif 66360 <= pos < 66460:
                app.kaomoji.widget.update_text("▼(^_^)▼")
            elif 66460 <= pos < 66525:
                app.kaomoji.widget.update_text("")
            elif 66525 <= pos < 66626:
                app.kaomoji.widget.update_text("▼(O3O)▼")
            elif 66626 <= pos < 66690:
                app.kaomoji.widget.update_text("")
            elif 66690 <= pos < 66800:
                app.kaomoji.widget.update_text("▼(=_=)▼")
            elif 66800 <= pos < 68000:
                app.kaomoji.hide()
                app.teto.preload_seqframe(get_res("frames/teto5"))
            elif 68000 <= pos < 70770:
                app.teto.show()
                app.teto.relocate()
                app.teto.widget.start_loop(1, "play_keyframe")
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("巨大なパレットみたい")
                app.text_leftline.show()
            elif 70770 <= pos < 71630:
                app.text_leftline.hide()
            elif 71630 <= pos < 73690:
                app.text_leftline.widget.update_text("心臓と血管")
                app.text_leftline.show()
            elif 73690 <= pos < 74430:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.CIRCLE,
                            size=100,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("今日も")
            elif 74430 <= pos < 75960:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("気づいてほしい")
            elif 75960 <= pos < 77000:
                app.text_leftline.widget.update_text("困ったな")
                app.small_teto2.preload_seqframe(get_res("frames/small_teto2"))
            elif 77000 <= pos < 79400:
                app.text_leftline.hide()
                app.teto.hide()
                app.teto.unload_widget()
                app.small_teto2.show()
                app.small_teto2.widget.start_loop(3)
            elif 79400 <= pos < 79600:
                app.small_teto2.hide()
                app.small_teto2.unload_widget()
            elif 79600 <= pos < 88200:
                if app.flag:
                    notify(
                        title="布豪！",
                        body="这里理应有一段军火展示，但我们无法帮您打开代码编辑器，或许您可以尝试手动操作一下？（bushi",
                        icon=get_res("resources/nerd_teto.jpg"),
                    )
                    app.flag = 0
            elif 88200 <= pos < 90200:
                app.rotating_object.preload_seqframe(get_res("frames/img1"))
            elif 90200 <= pos < 91000:
                app.rotating_object.show()
                app.rotating_object.widget.start_loop(1, "rotate_frame")
            elif 91000 <= pos < 93800:
                app.text_centerline.show()
                app.text_centerline.widget.set_font_size(72)
                app.text_centerline.widget.update_text("マスカレード、突発暗殺事件")
            elif 93800 <= pos < 96600:
                app.text_centerline.widget.update_text("死者の袖口、反応する硝煙")
            elif 96600 <= pos < 99500:
                app.text_centerline.widget.update_text(
                    "エッシャーの曖昧、自らを指す両手"
                )
            elif 99500 <= pos < 102300:
                app.text_centerline.close()
                app.small_teto3.preload_seqframe(get_res("frames/small_teto3"))
            elif 102300 <= pos < 105100:
                app.rotating_object.hide()
                app.rotating_object.unload_widget()
                app.small_teto3.show()
                app.small_teto3.widget.start_loop(3)
                app.text_centerline.show()
                app.text_centerline.widget.update_text("パラドックス、不適切な比喩")
            elif 105100 <= pos < 108000:
                app.text_centerline.widget.update_text("床屋がカ ツラを剃るように")
            elif 108000 <= pos < 110400:
                app.text_centerline.widget.update_text("自己形成、共軛のひどい理由")
            elif 110400 <= pos < 110900:
                app.small_teto3.hide()
                app.small_teto3.unload_widget()
                app.text_centerline.hide()
            elif 110900 <= pos < 113500:
                app.nerd_teto.show()
            elif 113500 <= pos < 115600:
                app.gome_teto.show()
                app.gome_teto.start_shake(16, 33)
                app.text_centerline.show()
                app.text_centerline.widget.set_font_size(64)
                app.text_centerline.widget.update_text(
                    "ごめんなさい！", fuck=(483 + 32, 85 + 18)
                )
            elif 115600 <= pos < 116200:
                app.text_centerline.hide()
                app.gome_teto.stop_shake()
            elif 116200 <= pos < 118200:
                app.text_centerline.show()
                app.text_centerline.widget.update_text(
                    "たぶん幻覚だよね、でしょ？", fuck=(897 + 32, 85 + 18)
                )
                app.gome_teto.start_shake(16, 33)
            elif 118200 <= pos < 119300:
                app.gome_teto.stop_shake()
                app.gome_teto.fancy_left()
            elif 119300 <= pos < 120300:
                app.nerd_teto.hide()
                app.gome_teto.hide()
                app.text_centerline.hide()
                app.text_left.show()
                app.text_left.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(140, 80),
                            shape=DecorationShape.TRIANGLE,
                            size=130,
                            rotation=15,
                        ),
                    ]
                )
                app.text_left.widget.set_font_size(120)
                app.text_left.widget.set_alignment(Qt.AlignmentFlag.AlignLeft)
                app.text_left.widget.update_text(
                    "<p style='line-height:125%'>見えたか？<br>—————<br>———————————</p>"
                )
            elif 120300 <= pos < 121200:
                app.text_left.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(140, 80),
                            shape=DecorationShape.TRIANGLE,
                            size=130,
                            rotation=15,
                        ),
                        Decoration(
                            position=QPoint(230, 300),
                            shape=DecorationShape.TRIANGLE,
                            size=130,
                            rotation=320,
                        ),
                    ]
                )
                app.text_left.widget.update_text(
                    "<p style='line-height:125%'>見えたか？<br>—見えたか？<br>———————————</p>"
                )
            elif 121200 <= pos < 124000:
                app.text_left.widget.update_text(
                    "<p style='line-height:125%'>見えたか？<br>—見えたか？<br>——嘘なんかじゃない！</p>"
                )
            elif 124000 <= pos < 125900:
                app.text_left.hide()
                app.teto.preload_seqframe(get_res("frames/teto6"))
            elif 125900 <= pos < 126260:
                app.text_leftline.show()
                app.text_leftline.widget.set_decorations([])
                app.text_leftline.widget.update_text("たって")
            elif 126260 <= pos < 128700:
                app.teto.show()
                app.teto.adjustSize()
                app.teto.move_to(("gapR64", "mid"))
                app.teto.widget.start_loop(1, "play_keyframe")
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("どんなにバカ")
            elif 128700 <= pos < 129000:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.CIRCLE,
                            size=100,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("でも")
            elif 129000 <= pos < 131250:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("自分を撃つの")
            elif 131250 <= pos < 131900:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.CIRCLE,
                            size=100,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("もっと")
            elif 131900 <= pos < 133800:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("紙の上に")
            elif 133800 <= pos < 135000:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.CIRCLE,
                            size=100,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("臙脂が 必要")
            elif 135000 <= pos < 135600:
                app.text_leftline.hide()
                app.teto.hide()
                app.teto.preload_seqframe(get_res("frames/teto5"))
            elif 135600 <= pos < 137200:
                app.minecraft_teto.show()
            elif 137200 <= pos < 140000:
                app.minecraft_teto.hide()
                app.teto.show()
                app.teto.adjustSize()
                app.teto.move_to(("gapR32", "mid"))
                app.teto.widget.start_loop(1, "play_keyframe")
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )
                app.text_leftline.show()
                app.text_leftline.widget.update_text("巨大なパレットみたい")
            elif 140000 <= pos < 140800:
                app.text_leftline.widget.label.setText("")
                app.text_leftline.widget.set_decorations([])
            elif 140800 <= pos < 142800:
                app.text_leftline.show()
                app.text_leftline.widget.update_text("心臓と血管")
            elif 142800 <= pos < 143700:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.CIRCLE,
                            size=100,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("今日も")
            elif 143700 <= pos < 145200:
                app.text_leftline.widget.set_decorations(
                    [
                        Decoration(
                            position=QPoint(100, 50),
                            shape=DecorationShape.TRIANGLE,
                            size=100,
                            rotation=45,
                        ),
                    ]
                )
                app.text_leftline.widget.update_text("気づいてほしい")
            elif 145200 <= pos < 146200:
                app.text_leftline.widget.update_text("困ったな")
            elif 146200 <= pos < 148800:
                app.text_leftline.hide()
                app.teto.hide()
                app.teto.unload_widget()
                app.yan.preload_seqframe(get_res("frames/yan"))
                app.zhi.preload_seqframe(get_res("frames/zhi"))
                app.small_teto2.preload_seqframe(get_res("frames/small_teto2"))
            elif 148800 <= pos < 157526:
                app.yan.show()
                app.zhi.show()
                app.small_teto2.show()
                app.yan.widget.start_loop(3)
                app.zhi.widget.start_loop(3)
                app.small_teto2.widget.start_loop(3)
            elif 157526 <= pos < 158927:
                app.yan.hide()
                app.zhi.hide()
                app.small_teto2.hide()
                app.yan.unload_widget()
                app.zhi.unload_widget()
                app.small_teto2.unload_widget()
                app.flag = 1
            elif 158927 <= pos < 160000:
                app.text_end.show()
                if app.flag:
                    notify(
                        title="感谢观看！",
                        body="""本家：胭脂 - 蛋包饭咖喱饭\n程序设计制作：HxAbCd\n特别感谢 BSOD-MEMZ 提供的灵感与支持\n制作不易，不妨支持一下UP主？""",
                        image={
                            "src": get_res("resources/teto2.jpg"),
                            "placement": "hero",
                        },
                        buttons=[
                            {
                                "activationType": "protocol",
                                "arguments": "https://www.bilibili.com/video/BV1ucGzzuEhw/",
                                "content": "观看原视频",
                            },
                            {
                                "activationType": "protocol",
                                "arguments": "https://www.bilibili.com/video/BV18R8wzEEgR/",
                                "content": "给UP三连",
                            },
                            {
                                "activationType": "protocol",
                                "arguments": "https://space.bilibili.com/401002238",
                                "content": "UP的主页",
                            },
                        ],
                    )
                    app.flag = 0

        # 延时退出
        def status_update(status):
            if status == QMediaPlayer.EndOfMedia:
                QTimer.singleShot(2000, app.quit)

        app.player.positionChanged.connect(sequence_update)
        app.player.mediaStatusChanged.connect(status_update)

        app.player.play()

        app.exec()

    if __name__ == "__main__":
        main()
except Exception as e:
    print(f"An error occurred: {e}")
