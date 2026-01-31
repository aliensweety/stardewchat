# -*- coding: utf-8 -*-
"""
Stardew Valley Chat Tool
在手机端输入文字，发送到星露谷对话框
"""

import os
import time
import socket
import ctypes
import win32api
import win32con
import win32gui
import win32clipboard
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


def get_all_local_ips():
    """获取所有本机IP地址（已排序，最可能的在前面）"""
    import socket
    import subprocess
    
    all_ips = set()
    
    try:
        # 方法1：通过hostname获取
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2]
        all_ips.update(ips)
    except:
        pass
    
    try:
        # 方法2：通过ipconfig获取更全面的信息
        result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
        for line in result.stdout.split('\n'):
            line = line.strip()
            if 'IPv4' in line and ':' in line:
                ip = line.split(':')[-1].strip()
                if ip:
                    all_ips.add(ip)
    except:
        pass
    
    # 过滤和排序
    # 优先级：192.168.x > 10.x > 其他 > 172.x > 127.x
    def ip_priority(ip):
        if ip.startswith('192.168.'):
            return (0, ip)
        elif ip.startswith('10.'):
            return (1, ip)
        elif ip.startswith('172.') and not ip.startswith('172.16.') and not ip.startswith('172.17.') and not ip.startswith('172.18.') and not ip.startswith('172.19.'):
            # 172.16-31 是私有地址，172.17-19常被Docker占用
            return (2, ip)
        elif ip.startswith('127.'):
            return (9, ip)
        elif ip.startswith('172.'):
            return (8, ip)  # Docker/WSL等虚拟网络
        else:
            return (3, ip)
    
    sorted_ips = sorted(all_ips, key=ip_priority)
    
    # 移除127.0.0.1（除非它是唯一的）
    result = [ip for ip in sorted_ips if not ip.startswith('127.')]
    if not result:
        result = ['127.0.0.1']
    
    return result


def get_local_ip():
    """获取最可能的本机局域网IP"""
    ips = get_all_local_ips()
    return ips[0] if ips else "127.0.0.1"


def find_stardew_window():
    """查找星露谷游戏窗口"""
    def callback(hwnd, windows):
        title = win32gui.GetWindowText(hwnd)
        if 'Stardew Valley' in title or '星露谷' in title:
            windows.append(hwnd)
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None


def activate_window(hwnd):
    """激活指定窗口"""
    if hwnd:
        try:
            # 尝试将窗口带到前台
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            return True
        except:
            pass
    return False


def press_key_with_scancode(vk_code, scan_code):
    """按下并释放按键（带扫描码，更兼容游戏）"""
    # 按下
    win32api.keybd_event(vk_code, scan_code, 0, 0)
    time.sleep(0.05)
    # 释放
    win32api.keybd_event(vk_code, scan_code, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)


def press_enter():
    """按回车键"""
    # Enter的扫描码是0x1C
    press_key_with_scancode(win32con.VK_RETURN, 0x1C)


def paste_text(text):
    """设置剪贴板并粘贴"""
    # 设置剪贴板
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    time.sleep(0.1)
    
    # Ctrl+V 粘贴 (Ctrl扫描码=0x1D, V扫描码=0x2F)
    win32api.keybd_event(win32con.VK_CONTROL, 0x1D, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(0x56, 0x2F, 0, 0)  # V键
    time.sleep(0.05)
    win32api.keybd_event(0x56, 0x2F, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_CONTROL, 0x1D, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)


def get_current_keyboard_layout():
    """获取当前键盘布局ID"""
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
    layout = ctypes.windll.user32.GetKeyboardLayout(thread_id)
    return layout


def is_chinese_layout(layout):
    """判断是否为中文输入法"""
    # 布局ID的低16位是语言ID
    # 0x0804 = 简体中文, 0x0404 = 繁体中文
    lang_id = layout & 0xFFFF
    return lang_id in (0x0804, 0x0404, 0x0C04, 0x1004, 0x1404)


def switch_keyboard_layout(layout_id):
    """切换到指定键盘布局"""
    WM_INPUTLANGCHANGEREQUEST = 0x0050
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    ctypes.windll.user32.PostMessageW(hwnd, WM_INPUTLANGCHANGEREQUEST, 0, layout_id)
    time.sleep(0.1)


def get_english_layout():
    """获取英文键盘布局"""
    return ctypes.windll.user32.LoadKeyboardLayoutW("00000409", 1)


def send_to_stardew(text):
    """
    发送对话到星露谷
    流程：激活窗口 -> 无痕切换输入法 -> 按T打开对话框 -> 粘贴文字 -> Enter发送 -> 恢复输入法
    """
    # 1. 尝试激活星露谷窗口
    hwnd = find_stardew_window()
    if hwnd:
        activate_window(hwnd)
        time.sleep(0.15)
    
    # 2. 检测并保存当前输入法状态
    original_layout = get_current_keyboard_layout()
    was_chinese = is_chinese_layout(original_layout)
    
    # 3. 如果是中文，切换到英文
    if was_chinese:
        switch_keyboard_layout(get_english_layout())
    
    # 4. 按 T 打开对话框 (T的扫描码是0x14)
    press_key_with_scancode(0x54, 0x14)
    time.sleep(0.25)  # 等待对话框打开
    
    # 5. 如果之前是中文，切回去（这样用户在对话框里可以打中文）
    if was_chinese:
        switch_keyboard_layout(original_layout)
    
    # 6. 粘贴文字
    paste_text(text)
    time.sleep(0.1)
    
    # 7. 按 Enter 发送
    press_enter()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/send', methods=['POST'])
def send():
    """发送对话到星露谷"""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'success': False, 'message': '文本为空'})
    
    try:
        send_to_stardew(text)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/info')
def info():
    """获取服务信息（IP、端口）"""
    ip = get_local_ip()
    port = 5001
    return jsonify({
        'ip': ip,
        'port': port,
        'url': f'http://{ip}:{port}'
    })


@app.route('/api/qrcode')
def qrcode_img():
    """生成访问二维码"""
    import qrcode
    import io
    import base64
    
    ip = get_local_ip()
    url = f'http://{ip}:5001'
    
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({'qrcode': f'data:image/png;base64,{img_str}'})


# 简单密码验证（存储在内存中，重启后需要重新设置）
ACCESS_PASSWORD = ""


@app.route('/api/password', methods=['GET', 'POST'])
def password():
    """密码管理"""
    global ACCESS_PASSWORD
    
    if request.method == 'GET':
        # 返回是否已设置密码
        return jsonify({'has_password': bool(ACCESS_PASSWORD)})
    else:
        data = request.get_json()
        action = data.get('action', '')
        
        if action == 'set':
            # 设置密码
            new_password = data.get('password', '').strip()
            ACCESS_PASSWORD = new_password
            return jsonify({'success': True})
        
        elif action == 'verify':
            # 验证密码
            input_password = data.get('password', '').strip()
            if not ACCESS_PASSWORD:
                return jsonify({'success': True})  # 未设置密码，直接通过
            return jsonify({'success': input_password == ACCESS_PASSWORD})
        
        return jsonify({'success': False, 'message': '未知操作'})


if __name__ == '__main__':
    ip = get_local_ip()
    port = 5001
    
    print("=" * 50)
    print("  Stardew Valley Chat Tool")
    print("=" * 50)
    print(f"\n手机访问: http://{ip}:{port}")
    print("\n使用方法:")
    print("  1. 打开星露谷游戏（窗口模式更可靠）")
    print("  2. 在手机上输入文字并点击发送")
    print("\n按 Ctrl+C 停止服务\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)


