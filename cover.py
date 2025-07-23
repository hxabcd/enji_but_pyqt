"""视频封面"""

from components import *
from main import Animation

app = Animation()
app.yan.preload_seqframe("frames/yan")
app.zhi.preload_seqframe("frames/zhi")
app.small_teto1.preload_seqframe("frames/small_teto1")
text1 = ContainerWindow(
    DecoratedLabel(
        text="<span style='font-size: 320px;'>但是</span>",
    ),
    position=("mid", "mid"),
)
text2 = ContainerWindow(
    DecoratedLabel(
        text="<span style='color: #0078D4; font-size: 240px;'>Windows</span>",
        # text_font=QFont("Microsoft YaHei"),
    ),
    position=("mid", "mid"),
)


app.yan.show()
app.zhi.show()
app.small_teto1.show()
text1.show()
text2.show()


app.exec()
