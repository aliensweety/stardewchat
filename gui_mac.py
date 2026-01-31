# -*- coding: utf-8 -*-
"""
Stardew Valley Chat Tool - macOS GUI版本
"""

import os
import sys
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
from PIL import Image, ImageTk, ImageDraw

# 确保能找到模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import server_cross as server
from server_cross import app, get_local_ip, get_all_local_ips

# 全局变量
server_thread = None
root = None
current_ip_index = 0
all_ips = []


def get_server_url(ip=None):
    if ip is None:
        ip = get_local_ip()
    return f"http://{ip}:5001"


def generate_qr_image(url, size=180):
    """生成二维码图片"""
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


def start_server():
    """在后台线程启动Flask服务器"""
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)


def run_gui():
    """运行GUI主窗口"""
    global root, server_thread, current_ip_index, all_ips
    
    # 获取所有IP
    all_ips = get_all_local_ips()
    current_ip_index = 0
    
    # 启动服务器线程
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # 创建主窗口
    root = tk.Tk()
    root.title("星露谷Chat")
    root.geometry("340x520")
    root.resizable(False, False)
    root.configure(bg='#1a1a2e')
    
    # 标题
    title_label = tk.Label(
        root, 
        text="🎮 星露谷Chat", 
        font=("Helvetica", 18, "bold"),
        fg='#8B5CF6',
        bg='#1a1a2e'
    )
    title_label.pack(pady=(15, 5))
    
    # 服务器状态
    status_label = tk.Label(
        root,
        text="✓ 服务已启动",
        font=("Helvetica", 10),
        fg='#4ade80',
        bg='#1a1a2e'
    )
    status_label.pack()
    
    # 扫码提示
    tk.Label(
        root,
        text="手机扫码访问",
        font=("Helvetica", 10),
        fg='#888',
        bg='#1a1a2e'
    ).pack(pady=(12, 5))
    
    # 二维码容器
    qr_frame = tk.Frame(root, bg='white', padx=8, pady=8)
    qr_frame.pack()
    
    # 初始二维码
    current_url = get_server_url(all_ips[0]) if all_ips else get_server_url()
    qr_image = generate_qr_image(current_url)
    qr_label = tk.Label(qr_frame, image=qr_image, bg='white')
    qr_label.image = qr_image
    qr_label.pack()
    
    # URL显示区域
    tk.Label(
        root,
        text="或在浏览器打开",
        font=("Helvetica", 9),
        fg='#666',
        bg='#1a1a2e'
    ).pack(pady=(8, 2))
    
    # URL和切换按钮行
    url_row = tk.Frame(root, bg='#1a1a2e')
    url_row.pack()
    
    url_label = tk.Label(
        url_row,
        text=current_url,
        font=("Menlo", 11),
        fg='#EC4899',
        bg='#1a1a2e',
        cursor="hand2"
    )
    url_label.pack(side='left')
    url_label.bind("<Button-1>", lambda e: webbrowser.open(url_label.cget("text")))
    
    # 切换IP按钮
    def switch_ip():
        global current_ip_index
        if len(all_ips) <= 1:
            return
        current_ip_index = (current_ip_index + 1) % len(all_ips)
        new_ip = all_ips[current_ip_index]
        new_url = get_server_url(new_ip)
        url_label.config(text=new_url)
        new_qr = generate_qr_image(new_url)
        qr_label.config(image=new_qr)
        qr_label.image = new_qr
        switch_btn.config(text=f"切换 ({current_ip_index + 1}/{len(all_ips)})")
    
    if len(all_ips) > 1:
        switch_btn = tk.Button(
            url_row,
            text=f"切换 (1/{len(all_ips)})",
            font=("Helvetica", 8),
            bg='#3d3d5c',
            fg='#888',
            activebackground='#4d4d6c',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            command=switch_ip
        )
        switch_btn.pack(side='left', padx=(8, 0), ipadx=6, ipady=1)
    
    # 分隔线
    ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=12)
    
    # 密码设置区域
    password_frame = tk.Frame(root, bg='#1a1a2e')
    password_frame.pack(fill='x', padx=25)
    
    tk.Label(
        password_frame,
        text="访问密码（可选，留空则无需密码）",
        font=("Helvetica", 9),
        fg='#888',
        bg='#1a1a2e'
    ).pack(anchor='w')
    
    pwd_row = tk.Frame(password_frame, bg='#1a1a2e')
    pwd_row.pack(fill='x', pady=(5, 0))
    
    password_entry = tk.Entry(
        pwd_row,
        font=("Helvetica", 11),
        show="*",
        width=18,
        bg='#2d2d44',
        fg='white',
        insertbackground='white',
        relief='flat',
        highlightthickness=1,
        highlightbackground='#3d3d5c',
        highlightcolor='#8B5CF6'
    )
    password_entry.pack(side='left', ipady=6)
    
    def set_password():
        pwd = password_entry.get().strip()
        server.ACCESS_PASSWORD = pwd
        if pwd:
            messagebox.showinfo("成功", "密码已设置\n手机验证后30天内无需再次输入")
        else:
            messagebox.showinfo("成功", "密码已清除（无需密码）")
    
    set_pwd_btn = tk.Button(
        pwd_row,
        text="设置",
        font=("Helvetica", 9),
        bg='#8B5CF6',
        fg='white',
        activebackground='#7C3AED',
        activeforeground='white',
        relief='flat',
        cursor='hand2',
        command=set_password
    )
    set_pwd_btn.pack(side='left', padx=(10, 0), ipadx=12, ipady=4)
    
    # 底部信息
    bottom_frame = tk.Frame(root, bg='#1a1a2e')
    bottom_frame.pack(side='bottom', pady=10)
    
    tk.Label(
        bottom_frame,
        text="🌟 即将开源，敬请期待",
        font=("Helvetica", 9),
        fg='#666',
        bg='#1a1a2e'
    ).pack()
    
    github_link = tk.Label(
        bottom_frame,
        text="github.com/aliensweety",
        font=("Menlo", 9),
        fg='#8B5CF6',
        bg='#1a1a2e',
        cursor='hand2'
    )
    github_link.pack()
    github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/aliensweety"))
    
    tk.Label(
        bottom_frame,
        text="请保持此窗口运行",
        font=("Helvetica", 8),
        fg='#444',
        bg='#1a1a2e'
    ).pack(pady=(8, 0))
    
    # 关闭
    def on_closing():
        root.destroy()
        os._exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == '__main__':
    run_gui()
