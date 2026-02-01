# -*- coding: utf-8 -*-
"""
Stardew Valley Chat Tool - GUI版本
极简现代风格桌面程序
"""

import os
import sys
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
from PIL import Image, ImageTk, ImageDraw

# 确保能找到server模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import server
from server import app, get_local_ip, get_all_local_ips

# 全局变量
server_thread = None
root = None
tray_icon = None
current_ip_index = 0
all_ips = []

# 颜色配置 - 浅色主题
COLORS = {
    'bg': '#f5f5f7',           # 苹果风格浅灰白背景
    'card_bg': '#ffffff',       # 卡片白色
    'text': '#1d1d1f',         # 深色文字
    'text_secondary': '#86868b', # 次要文字
    'accent': '#8B5CF6',        # 紫色强调色
    'accent_hover': '#7C3AED',
}


def get_server_url(ip=None):
    if ip is None:
        ip = get_local_ip()
    return f"http://{ip}:5001"


def get_logo_path():
    """获取logo文件路径"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_path, 'assets', 'logo', 'logo_64.png')
    if os.path.exists(logo_path):
        return logo_path
    return None


def get_icon_path():
    """获取ico图标文件路径"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    ico_path = os.path.join(base_path, 'assets', 'logo', 'app_icon.ico')
    if os.path.exists(ico_path):
        return ico_path
    return None


def generate_qr_image(url, size=200):
    """生成二维码图片"""
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1d1d1f", back_color="white")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


def load_logo_image(size=48):
    """加载logo图片"""
    logo_path = get_logo_path()
    if logo_path and os.path.exists(logo_path):
        img = Image.open(logo_path)
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    return None


def create_tray_icon():
    """创建系统托盘图标"""
    try:
        import pystray
        from pystray import MenuItem as item
        
        # 尝试加载logo，否则创建默认图标
        logo_path = get_logo_path()
        if logo_path and os.path.exists(logo_path):
            image = Image.open(logo_path).resize((64, 64), Image.Resampling.LANCZOS)
            # 添加白色背景
            bg = Image.new('RGB', (64, 64), 'white')
            bg.paste(image, mask=image.split()[3] if image.mode == 'RGBA' else None)
            image = bg
        else:
            icon_size = 64
            image = Image.new('RGB', (icon_size, icon_size), '#8B5CF6')
            draw = ImageDraw.Draw(image)
            draw.ellipse([16, 20, 48, 44], fill='white')
        
        def show_window(icon, item):
            root.deiconify()
            root.lift()
        
        def quit_app(icon, item):
            icon.stop()
            root.destroy()
            os._exit(0)
        
        menu = (
            item('显示窗口', show_window, default=True),
            item('退出', quit_app)
        )
        
        icon = pystray.Icon("stardew_chat", image, "StardewChat", menu)
        return icon
    except ImportError:
        return None


def start_server():
    """在后台线程启动Flask服务器"""
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)


def run_gui():
    """运行GUI主窗口"""
    global root, server_thread, tray_icon, current_ip_index, all_ips
    
    # 获取所有IP
    all_ips = get_all_local_ips()
    current_ip_index = 0
    
    # 启动服务器线程
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 创建主窗口
    root = tk.Tk()
    root.title("StardewChat")
    root.geometry("360x520")
    root.resizable(False, False)
    root.configure(bg=COLORS['bg'])
    
    # 设置窗口图标
    ico_path = get_icon_path()
    if ico_path:
        try:
            root.iconbitmap(ico_path)
        except:
            pass
    
    # 主容器
    main_frame = tk.Frame(root, bg=COLORS['bg'])
    main_frame.pack(fill='both', expand=True, padx=30, pady=20)
    
    # === 顶部Logo和标题 ===
    header_frame = tk.Frame(main_frame, bg=COLORS['bg'])
    header_frame.pack(fill='x', pady=(0, 20))
    
    # Logo图片
    logo_image = load_logo_image(42)
    if logo_image:
        logo_label = tk.Label(header_frame, image=logo_image, bg=COLORS['bg'])
        logo_label.image = logo_image
        logo_label.pack(side='left')
    
    # 标题文字
    title_label = tk.Label(
        header_frame, 
        text="StardewChat", 
        font=("Segoe UI", 20, "bold"),
        fg=COLORS['text'],
        bg=COLORS['bg']
    )
    title_label.pack(side='left', padx=(10, 0))
    
    # 服务状态指示
    status_dot = tk.Label(
        header_frame,
        text="●",
        font=("Segoe UI", 8),
        fg='#22c55e',
        bg=COLORS['bg']
    )
    status_dot.pack(side='left', padx=(8, 0))
    
    # === 二维码卡片 ===
    qr_card = tk.Frame(main_frame, bg=COLORS['card_bg'], highlightthickness=0)
    qr_card.pack(fill='x', pady=(0, 16))
    
    # 二维码内边距容器
    qr_inner = tk.Frame(qr_card, bg=COLORS['card_bg'])
    qr_inner.pack(padx=20, pady=20)
    
    # 扫码提示
    tk.Label(
        qr_inner,
        text="手机扫码访问",
        font=("Microsoft YaHei", 11),
        fg=COLORS['text_secondary'],
        bg=COLORS['card_bg']
    ).pack(pady=(0, 12))
    
    # 二维码
    current_url = get_server_url(all_ips[0])
    qr_image = generate_qr_image(current_url)
    qr_label = tk.Label(qr_inner, image=qr_image, bg=COLORS['card_bg'])
    qr_label.image = qr_image
    qr_label.pack()
    
    # URL显示
    url_frame = tk.Frame(qr_inner, bg=COLORS['card_bg'])
    url_frame.pack(pady=(12, 0))
    
    url_label = tk.Label(
        url_frame,
        text=current_url,
        font=("Consolas", 12),
        fg=COLORS['accent'],
        bg=COLORS['card_bg'],
        cursor="hand2"
    )
    url_label.pack(side='left')
    url_label.bind("<Button-1>", lambda e: webbrowser.open(url_label.cget("text")))
    
    # 切换IP按钮（只有多个IP时显示）
    def switch_ip():
        global current_ip_index
        if len(all_ips) <= 1:
            return
        current_ip_index = (current_ip_index + 1) % len(all_ips)
        new_ip = all_ips[current_ip_index]
        new_url = get_server_url(new_ip)
        
        # 更新URL标签
        url_label.config(text=new_url)
        
        # 更新二维码
        new_qr = generate_qr_image(new_url)
        qr_label.config(image=new_qr)
        qr_label.image = new_qr
        
        # 更新按钮提示
        switch_btn.config(text=f"⟳ {current_ip_index + 1}/{len(all_ips)}")
    
    if len(all_ips) > 1:
        switch_btn = tk.Button(
            url_frame,
            text=f"⟳ 1/{len(all_ips)}",
            font=("Segoe UI", 9),
            bg=COLORS['bg'],
            fg=COLORS['text_secondary'],
            activebackground=COLORS['bg'],
            activeforeground=COLORS['text'],
            relief='flat',
            cursor='hand2',
            command=switch_ip
        )
        switch_btn.pack(side='left', padx=(12, 0))
    
    # === 设置按钮 ===
    def open_settings():
        """打开设置弹窗"""
        settings_win = tk.Toplevel(root)
        settings_win.title("设置")
        settings_win.geometry("320x280")
        settings_win.resizable(False, False)
        settings_win.configure(bg=COLORS['bg'])
        settings_win.transient(root)
        settings_win.grab_set()
        
        # 居中显示
        settings_win.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() - settings_win.winfo_width()) // 2
        y = root.winfo_y() + (root.winfo_height() - settings_win.winfo_height()) // 2
        settings_win.geometry(f"+{x}+{y}")
        
        # 设置窗口图标
        if ico_path:
            try:
                settings_win.iconbitmap(ico_path)
            except:
                pass
        
        settings_frame = tk.Frame(settings_win, bg=COLORS['bg'])
        settings_frame.pack(fill='both', expand=True, padx=24, pady=20)
        
        # 密码设置
        tk.Label(
            settings_frame,
            text="访问密码",
            font=("Microsoft YaHei", 12, "bold"),
            fg=COLORS['text'],
            bg=COLORS['bg']
        ).pack(anchor='w')
        
        tk.Label(
            settings_frame,
            text="设置后手机端需要输入密码才能访问",
            font=("Microsoft YaHei", 9),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg']
        ).pack(anchor='w', pady=(2, 8))
        
        pwd_frame = tk.Frame(settings_frame, bg=COLORS['bg'])
        pwd_frame.pack(fill='x')
        
        password_entry = tk.Entry(
            pwd_frame,
            font=("Microsoft YaHei", 11),
            show="*",
            width=18,
            bg=COLORS['card_bg'],
            fg=COLORS['text'],
            insertbackground=COLORS['text'],
            relief='flat',
            highlightthickness=1,
            highlightbackground='#e5e5e5',
            highlightcolor=COLORS['accent']
        )
        password_entry.pack(side='left', ipady=8)
        
        def set_password():
            pwd = password_entry.get().strip()
            server.ACCESS_PASSWORD = pwd
            if pwd:
                messagebox.showinfo("成功", "密码已设置\n手机验证后30天内无需再次输入", parent=settings_win)
            else:
                messagebox.showinfo("成功", "密码已清除（无需密码）", parent=settings_win)
        
        set_pwd_btn = tk.Button(
            pwd_frame,
            text="设置",
            font=("Microsoft YaHei", 10),
            bg=COLORS['accent'],
            fg='white',
            activebackground=COLORS['accent_hover'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            command=set_password
        )
        set_pwd_btn.pack(side='left', padx=(10, 0), ipadx=16, ipady=6)
        
        # 分隔线
        ttk.Separator(settings_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # GitHub链接
        tk.Label(
            settings_frame,
            text="关于",
            font=("Microsoft YaHei", 12, "bold"),
            fg=COLORS['text'],
            bg=COLORS['bg']
        ).pack(anchor='w')
        
        github_link = tk.Label(
            settings_frame,
            text="🌟 github.com/aliensweety",
            font=("Consolas", 10),
            fg=COLORS['accent'],
            bg=COLORS['bg'],
            cursor='hand2'
        )
        github_link.pack(anchor='w', pady=(8, 0))
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/aliensweety"))
        
        # 关闭按钮
        tk.Button(
            settings_frame,
            text="关闭",
            font=("Microsoft YaHei", 10),
            bg=COLORS['bg'],
            fg=COLORS['text_secondary'],
            activebackground=COLORS['bg'],
            relief='flat',
            cursor='hand2',
            command=settings_win.destroy
        ).pack(side='bottom', pady=(20, 0))
    
    settings_btn = tk.Button(
        main_frame,
        text="⚙  设置",
        font=("Segoe UI", 11),
        bg=COLORS['card_bg'],
        fg=COLORS['text_secondary'],
        activebackground=COLORS['card_bg'],
        activeforeground=COLORS['text'],
        relief='flat',
        cursor='hand2',
        command=open_settings
    )
    settings_btn.pack(pady=(0, 16), ipadx=20, ipady=8)
    
    # === 底部提示 ===
    tip_label = tk.Label(
        main_frame,
        text="最小化后可在托盘找到",
        font=("Microsoft YaHei", 9),
        fg=COLORS['text_secondary'],
        bg=COLORS['bg']
    )
    tip_label.pack(side='bottom')
    
    # 托盘图标
    tray_icon = create_tray_icon()
    if tray_icon:
        tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
        tray_thread.start()
        
        def on_minimize(event):
            if root.state() == 'iconic':
                root.withdraw()
        
        root.bind('<Unmap>', on_minimize)
    
    # 关闭时清理
    def on_closing():
        if tray_icon:
            tray_icon.stop()
        root.destroy()
        os._exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 运行主循环
    root.mainloop()


if __name__ == '__main__':
    run_gui()
