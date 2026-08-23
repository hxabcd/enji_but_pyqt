
# Enji but PyQt | 胭脂，但是PyQt

一个使用 `Python` + `PySide6`，仿照[胭脂](https://www.bilibili.com/video/BV1ucGzzuEhw/)的MV制作的 Windows 窗口动画程序。由 [BSOD-MEMZ](https://github.com/BSOD-MEMZ) 提供灵感，受到了 [《强 风 大 窗 口》](https://github.com/SunnyDesignor/PowerfulWindSlickedBackHairCS-LX_Improve) 的启发。

视频演示：https://www.bilibili.com/video/BV18R8wzEEgR

本家：https://www.bilibili.com/video/BV1ucGzzuEhw

原作者：[蛋包饭咖喱饭](https://www.bilibili.com/video/BV1ucGzzuEhw/)

> [!NOTE]
> 程序启动时需要释放和载入资源文件，可能要耗费较长时间；程序峰值内存占用可能达到 860MB

> [!NOTE]
> 程序在运行过程中会动态加载资源，如您的运行设备性能一般，动画的播放可能会发生滞后

支持的系统：Windows 10 及以上版本 | [下载](https://github.com/hxabcd/enji_but_pyqt/releases)

## 开发

可通过配置环境变量来控制任务栏显示/隐藏和部分调试选项，具体见代码 `main.py` `main()`

本项目使用 uv 管理环境，可以直接使用 `uv sync` 同步环境

## 亮点

> 更多创作细节，见博客文章[欸，我不是窗口吗？——胭脂，但是Windows](https://0xabcd.dev/posts/enji_but_pyqt/)

* 与原MV相同的字体（我也好奇怎么找出来的）

* 基于时间的帧控制

* 动态资源加载

* 关键帧动画

* 尽可能少的 AI 使用（幻觉：你好）

这些真的有用……吗？

其实只要足够生草就行了，大抵是这个人喜欢造轮子罢……
