from main import *

app = QApplication(sys.argv)
init_scale()

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

window_starring.show()

app.exec()
