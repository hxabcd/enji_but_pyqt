import math
import os

from PIL import Image

INPUT_DIR = r"d:\MyPC\Advanced\Code\Python\Projects\enji_but_pyqt\frames\teto4"
SCALE = 0.8333333334  # 缩放比例
OLD_COLOR_HEX = "#FF8689"
NEW_COLOR_HEX = "#FF8689"
COLOR_TOLERANCE = 0  # 近似色容差
SUPPORTED_EXTS = (".png", ".jpg", ".jpeg", ".bmp")


def hex_to_rgb(hex_color):
    """将十六进制颜色转换为RGB元组"""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def color_distance(color1, color2):
    """
    计算两个颜色之间的欧几里得距离，用于判断颜色的相似度
    :param color1: 第一个颜色 (R, G, B)
    :param color2: 第二个颜色 (R, G, B)
    :return: 两个颜色之间的欧几里得距离
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(color1, color2)))


def replace_color(img, old_color, new_color, tolerance):
    """
    替换图片中的近似色
    :param img: Pillow Image 对象
    :param old_color: 要替换的颜色 (R, G, B)
    :param new_color: 替换后的颜色 (R, G, B)
    :param tolerance: 颜色差异容差
    :return: 修改后的图片
    """
    if new_color == old_color:
        return img

    img = img.convert("RGB")
    pixels = img.load()
    for x in range(img.width):
        for y in range(img.height):
            current_color = pixels[x, y]
            if color_distance(current_color, old_color) <= tolerance:
                pixels[x, y] = new_color
    return img


def process_image(path):
    """
    处理单张图片：替换颜色并按比例缩放
    :param path: 图片文件路径
    """
    img = Image.open(path)
    old_color = hex_to_rgb(OLD_COLOR_HEX)
    new_color = hex_to_rgb(NEW_COLOR_HEX)

    # 替换近似颜色
    img = replace_color(img, old_color, new_color, COLOR_TOLERANCE)

    # 缩放图片
    new_size = (int(img.width * SCALE), int(img.height * SCALE))
    img = img.resize(new_size)

    # 保存修改后的图片，覆盖原图
    img.save(path)
    print(f"处理完成: {path}")


def main():
    """
    批量处理input目录中的所有图片
    """
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(SUPPORTED_EXTS):
            path = os.path.join(INPUT_DIR, filename)
            process_image(path)


if __name__ == "__main__":
    main()
