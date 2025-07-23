
# Enji but PyQt | 胭脂，但是PyQt

## 概述

一个使用 `Python 3.13` + `PySide6`，仿照[胭脂](https://www.bilibili.com/video/BV1ucGzzuEhw/)的PV制作的 Windows 窗口动画程序。灵感来自于 [BSOD-MEMZ](https://github.com/BSOD-MEMZ) 和 [《强 风 大 窗 口》](https://github.com/SunnyDesignor/PowerfulWindSlickedBackHairCS-LX_Improve)

原PV：[https://www.bilibili.com/video/BV1ucGzzuEhw](https://www.bilibili.com/video/BV1ucGzzuEhw)

原作者：[蛋包饭咖喱饭](https://www.bilibili.com/video/BV1ucGzzuEhw/)

**注意**：程序启动时需要释放和载入资源文件，可能要耗费较长时间

**注意**：程序峰值内存占用可能达到 860MB

[下载](https://github.com/hxabcd/enji_but_pyqt/releases/download/latest/)

## 配置

可通过配置环境变量来控制任务栏显示/隐藏和部分调试选项，具体见代码 `main.py` `main()`

## 开发

本项目使用 uv 管理，可以直接使用 `uv sync` 同步环境

但需要注意安装 `win11toast` 时需要存在 Visual Studio C++ 编译工具来进行构建（貌似是）

## 亮点

* 与原PV相同的字体（我也好奇怎么找出来的）

* 基于时间的帧控制

* 动态资源加载

* 关键帧动画

* 尽可能少的 AI 使用（幻觉：你好）

这些真的有用……吗？

其实只要足够生草就行了，大抵是这个人喜欢造轮子罢……
