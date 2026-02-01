# 🎮 Stardew Chat

通过手机向星露谷游戏发送对话消息的工具。

> ⚠️ **开发中** - 目前为私有仓库，待功能完善后开源

## ✨ 功能特性

- 📱 手机扫码即可发送对话到游戏
- 🔑 可选的密码保护
- 🖥️ 桌面端显示二维码，支持多IP切换
- 🔄 智能输入法切换（中英文无痕切换）
- 📋 发送历史记录（支持清空）
- 🔔 系统托盘运行
- 🍎 支持 Windows 和 macOS

## 📥 下载

从 [Releases](../../releases) 页面下载最新版本：

| 平台 | 文件 |
|------|------|
| Windows | `StardewChat.exe` |
| macOS | `StardewChat-macOS.zip` |

## 🚀 使用方法

### Windows

1. 下载 `StardewChat.exe`
2. 双击运行
3. 用手机扫描二维码
4. 开始发送对话！

### macOS

1. 下载 `StardewChat-macOS.zip`
2. 解压得到 `StardewChat`
3. **首次运行前**，打开终端执行：
   ```bash
   xattr -cr ~/Downloads/StardewChat
   ```
4. 双击运行，或右键点击 → 打开
5. 如果仍提示"无法打开"：
   - 打开「系统设置」→「隐私与安全性」
   - 滚动到底部，点击"仍要打开"
6. **重要**：需要授予辅助功能权限
   - 「系统设置」→「隐私与安全性」→「辅助功能」
   - 添加 `StardewChat` 或 `终端`
7. 用手机扫描二维码，开始使用！

### 游戏设置

- 建议使用**窗口模式**运行星露谷，按键模拟更稳定
- 确保手机和电脑在同一局域网（Wi-Fi）

## 📱 手机端功能

- 输入文字后点击发送
- 发送历史可以恢复之前的文字
- 右上角可清空历史记录

## 🔧 技术栈

- **后端**: Python + Flask
- **桌面端**: Tkinter + pystray
- **按键模拟**: 
  - Windows: pywin32
  - macOS: osascript / Quartz
- **二维码**: qrcode + Pillow
- **自动构建**: GitHub Actions

## 📝 开发计划

- [x] 核心功能（按T、粘贴、回车）
- [x] 输入法无痕切换
- [x] 手机端界面
- [x] 桌面端GUI + 二维码
- [x] 系统托盘（Windows）
- [x] 打包成EXE / App
- [x] GitHub Actions自动构建
- [ ] 更多自定义选项
- [ ] 多语言支持

## 📄 许可证

MIT License

---

Made with 💜 for Stardew Valley players

[github.com/aliensweety](https://github.com/aliensweety)
