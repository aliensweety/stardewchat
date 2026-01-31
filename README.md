# 🎮 Stardew Chat

通过手机向星露谷游戏发送对话消息的工具。

> ⚠️ **开发中** - 目前为私有仓库，待功能完善后开源

## 功能特性

- 📱 手机扫码即可发送对话到游戏
- 🔑 可选的密码保护
- 🖥️ 桌面端显示二维码，支持多IP切换
- 🔄 智能输入法切换（中英文无痕切换）
- 📋 发送历史记录
- 🔔 系统托盘运行

## 使用方法

### 运行服务

```bash
cd stardew-chat
start.bat
```

或直接运行GUI版本：

```bash
python gui.py
```

### 连接手机

1. 确保手机和电脑在同一局域网
2. 扫描电脑端显示的二维码
3. 在手机上输入文字，点击发送

### 游戏设置

- 建议使用**窗口模式**运行星露谷，按键模拟更稳定
- 支持中英文输入法自动切换

## 技术栈

- **后端**: Python + Flask
- **桌面端**: Tkinter + pystray
- **按键模拟**: pywin32
- **二维码**: qrcode + Pillow

## 目录结构

```
stardew-chat/
├── server.py        # Flask服务器 + 按键模拟
├── gui.py           # 桌面GUI程序
├── start.bat        # 快速启动脚本
├── build.bat        # 打包EXE脚本
├── requirements.txt # Python依赖
└── templates/
    └── index.html   # 手机端页面
```

## 开发计划

- [x] 核心功能（按T、粘贴、回车）
- [x] 输入法无痕切换
- [x] 手机端界面
- [x] 桌面端GUI + 二维码
- [x] 系统托盘
- [ ] 打包成EXE
- [ ] macOS支持

## 许可证

MIT License

---

Made with 💜 for Stardew Valley players
