import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageDraw, ImageTk


class BatchCoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量矩形覆盖工具（统一方案）")
        self.root.geometry("900x600")

        self.files = []  # 所有待处理图片路径
        self.rects = []  # 全局统一矩形列表 [(x1,y1,x2,y2), ...]
        self.start_xy = None
        self.tmp_rect_id = None  # 当前正在画的矩形 id

        self.setup_ui()

    # ---------------- UI ----------------
    def setup_ui(self):
        # 顶部工具栏
        bar = ttk.Frame(self.root)
        bar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(bar, text="导入图片/文件夹", command=self.load_images).pack(
            side=tk.LEFT
        )
        ttk.Button(bar, text="清空矩形", command=self.clear_rects).pack(side=tk.LEFT)
        ttk.Button(bar, text="批量导出", command=self.export_all).pack(side=tk.LEFT)

        self.lbl_cnt = ttk.Label(bar, text="共 0 张")
        self.lbl_cnt.pack(side=tk.LEFT, padx=10)

        # 颜色选择
        self.color_var = tk.StringVar(value="#000000")
        ttk.Label(bar, text="填充色:").pack(side=tk.LEFT)
        ttk.Entry(bar, textvariable=self.color_var, width=8).pack(side=tk.LEFT)

        # 画布
        self.canvas = tk.Canvas(self.root, bg="#555")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas.bind("<Button-1>", self.on_down)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_up)

    # ---------------- 逻辑 ----------------
    def load_images(self):
        """导入图片或整个文件夹"""
        paths = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")],
        )
        if not paths:
            folder = filedialog.askdirectory(title="选择图片所在文件夹")
            if folder:
                paths = [
                    os.path.join(folder, f)
                    for f in os.listdir(folder)
                    if f.lower().endswith(
                        (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
                    )
                ]

        if not paths:
            return
        self.files = list(paths)
        self.show_preview()
        self.lbl_cnt.config(text=f"共 {len(self.files)} 张")

    def show_preview(self):
        """显示第一张作为预览"""
        if not self.files:
            return
        self.img = Image.open(self.files[0]).convert("RGBA")
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas.config(
            scrollregion=(0, 0, self.tk_img.width(), self.tk_img.height())
        )
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        self.redraw_rects()

    # ---------------- 画矩形 ----------------
    def on_down(self, ev):
        self.start_xy = (ev.x, ev.y)
        if self.tmp_rect_id:
            self.canvas.delete(self.tmp_rect_id)

    def on_drag(self, ev):
        if not self.start_xy:
            return
        x0, y0 = self.start_xy
        if self.tmp_rect_id:
            self.canvas.delete(self.tmp_rect_id)
        self.tmp_rect_id = self.canvas.create_rectangle(
            x0, y0, ev.x, ev.y, fill=self.color_var.get(), outline=""
        )

    def on_up(self, ev):
        if not self.start_xy:
            return
        x0, y0 = self.start_xy
        x1, y1 = ev.x, ev.y
        rect = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        self.rects.append(rect)
        self.start_xy = None
        if self.tmp_rect_id:
            self.canvas.delete(self.tmp_rect_id)
            self.tmp_rect_id = None
        self.redraw_rects()

    def clear_rects(self):
        self.rects.clear()
        self.redraw_rects()

    def redraw_rects(self):
        self.canvas.delete("rect")
        for r in self.rects:
            self.canvas.create_rectangle(
                *r, fill=self.color_var.get(), outline="", tags="rect"
            )

    # ---------------- 导出 ----------------
    def export_all(self):
        if not self.files:
            messagebox.showwarning("提示", "请先导入图片")
            return
        out_dir = filedialog.askdirectory(title="选择导出目录")
        if not out_dir:
            return
        color = self.color_var.get()
        try:
            color_rgb = Image.new("RGBA", (1, 1), color=color).getpixel((0, 0))
        except ValueError:
            messagebox.showerror("颜色格式错误", "请使用 #RRGGBB 或名字如 red")
            return

        for path in self.files:
            img = Image.open(path).convert("RGBA")
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            for x1, y1, x2, y2 in self.rects:
                draw.rectangle([x1, y1, x2, y2], fill=color_rgb)
            out = Image.alpha_composite(img, overlay).convert("RGB")
            name, ext = os.path.splitext(os.path.basename(path))
            out.save(os.path.join(out_dir, f"{name}{ext}"))
        messagebox.showinfo("完成", f"已导出到 {out_dir}")


if __name__ == "__main__":
    root = tk.Tk()
    BatchCoverApp(root)
    root.mainloop()
