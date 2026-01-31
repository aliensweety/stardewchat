# -*- coding: utf-8 -*-
"""
跨平台按键模拟模块
Windows: 使用 pywin32
macOS: 使用 pyobjc (Quartz)
"""

import sys
import time
import subprocess

PLATFORM = sys.platform


if PLATFORM == 'darwin':
    # macOS 实现
    MACOS_AVAILABLE = False
    
    try:
        from Quartz import (
            CGEventCreateKeyboardEvent,
            CGEventPost,
            kCGHIDEventTap,
            CGEventSourceCreate,
            kCGEventSourceStateHIDSystemState,
            CGEventSetFlags,
            kCGEventFlagMaskCommand
        )
        from AppKit import NSWorkspace
        MACOS_AVAILABLE = True
    except ImportError:
        pass
    
    # macOS 键码映射
    KEY_T = 0x11
    KEY_RETURN = 0x24
    KEY_V = 0x09
    KEY_COMMAND = 0x37
    
    if MACOS_AVAILABLE:
        def press_key(keycode, flags=0):
            """按下并释放一个键"""
            source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
            event = CGEventCreateKeyboardEvent(source, keycode, True)
            if flags:
                CGEventSetFlags(event, flags)
            CGEventPost(kCGHIDEventTap, event)
            time.sleep(0.05)
            event = CGEventCreateKeyboardEvent(source, keycode, False)
            CGEventPost(kCGHIDEventTap, event)
            time.sleep(0.05)
        
        def press_key_t():
            press_key(KEY_T)
        
        def press_enter():
            press_key(KEY_RETURN)
        
        def paste_text(text):
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            time.sleep(0.1)
            source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
            event = CGEventCreateKeyboardEvent(source, KEY_V, True)
            CGEventSetFlags(event, kCGEventFlagMaskCommand)
            CGEventPost(kCGHIDEventTap, event)
            time.sleep(0.05)
            event = CGEventCreateKeyboardEvent(source, KEY_V, False)
            CGEventPost(kCGHIDEventTap, event)
            time.sleep(0.1)
        
        def find_stardew_window():
            workspace = NSWorkspace.sharedWorkspace()
            apps = workspace.runningApplications()
            for app in apps:
                name = app.localizedName()
                if name and ('Stardew' in name or '星露谷' in name):
                    return app
            return None
        
        def activate_window(app):
            if app:
                app.activateWithOptions_(0)
                time.sleep(0.2)
                return True
            return False
    else:
        # 备用实现：使用osascript
        def press_key_t():
            subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "t"'], capture_output=True)
        
        def press_enter():
            subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke return'], capture_output=True)
        
        def paste_text(text):
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            time.sleep(0.1)
            subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "v" using command down'], capture_output=True)
        
        def find_stardew_window():
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to get name of every process whose name contains "Stardew"'],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.stdout.strip() else None
        
        def activate_window(app_name):
            if app_name:
                subprocess.run(['osascript', '-e', f'tell application "{app_name}" to activate'], capture_output=True)
                time.sleep(0.2)
                return True
            return False
    
    def get_current_input_source():
        return None
    
    def is_chinese_input(source):
        return False
    
    def switch_to_english():
        pass
    
    def restore_input(source):
        pass


elif PLATFORM == 'win32':
    # Windows 实现
    import win32api
    import win32con
    import win32gui
    import win32clipboard
    import ctypes
    
    def press_key_with_scancode(vk_code, scan_code):
        """按下并释放按键（带扫描码）"""
        win32api.keybd_event(vk_code, scan_code, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(vk_code, scan_code, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
    
    def press_key_t():
        """按T键"""
        press_key_with_scancode(0x54, 0x14)
    
    def press_enter():
        """按回车键"""
        press_key_with_scancode(win32con.VK_RETURN, 0x1C)
    
    def paste_text(text):
        """设置剪贴板并粘贴"""
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        time.sleep(0.1)
        
        # Ctrl+V
        win32api.keybd_event(win32con.VK_CONTROL, 0x1D, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x56, 0x2F, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x56, 0x2F, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_CONTROL, 0x1D, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
    
    def find_stardew_window():
        """查找星露谷窗口"""
        def callback(hwnd, windows):
            title = win32gui.GetWindowText(hwnd)
            if 'Stardew Valley' in title or '星露谷' in title:
                windows.append(hwnd)
            return True
        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows[0] if windows else None
    
    def activate_window(hwnd):
        """激活窗口"""
        if hwnd:
            try:
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.15)
                return True
            except:
                pass
        return False
    
    def get_current_input_source():
        """获取当前键盘布局"""
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
        return ctypes.windll.user32.GetKeyboardLayout(thread_id)
    
    def is_chinese_input(layout):
        """判断是否为中文输入法"""
        lang_id = layout & 0xFFFF
        return lang_id in (0x0804, 0x0404, 0x0C04, 0x1004, 0x1404)
    
    def switch_to_english():
        """切换到英文键盘"""
        english = ctypes.windll.user32.LoadKeyboardLayoutW("00000409", 1)
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        ctypes.windll.user32.PostMessageW(hwnd, 0x0050, 0, english)
        time.sleep(0.1)
    
    def restore_input(layout):
        """恢复输入法"""
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        ctypes.windll.user32.PostMessageW(hwnd, 0x0050, 0, layout)
        time.sleep(0.1)

else:
    raise NotImplementedError(f"不支持的平台: {PLATFORM}")


def send_to_stardew(text):
    """
    发送对话到星露谷
    跨平台统一接口
    """
    # 1. 激活窗口
    window = find_stardew_window()
    if window:
        activate_window(window)
    
    # 2. 处理输入法（仅Windows）
    original_input = None
    if PLATFORM == 'win32':
        original_input = get_current_input_source()
        if is_chinese_input(original_input):
            switch_to_english()
    
    # 3. 按T打开对话框
    press_key_t()
    time.sleep(0.25)
    
    # 4. 恢复输入法
    if PLATFORM == 'win32' and original_input and is_chinese_input(original_input):
        restore_input(original_input)
    
    # 5. 粘贴文字
    paste_text(text)
    time.sleep(0.1)
    
    # 6. 按回车发送
    press_enter()
