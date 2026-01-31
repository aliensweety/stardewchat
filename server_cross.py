# -*- coding: utf-8 -*-
"""
Stardew Valley Chat Tool - 跨平台服务器
支持 Windows 和 macOS
"""

import os
import sys
import time
import socket
import subprocess
from flask import Flask, render_template, request, jsonify

# 导入跨平台按键模拟模块
from input_simulator import send_to_stardew

app = Flask(__name__)

# 简单密码验证
ACCESS_PASSWORD = ""


def get_all_local_ips():
    """获取所有本机IP地址"""
    all_ips = set()
    
    try:
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2]
        all_ips.update(ips)
    except:
        pass
    
    # 平台特定IP获取
    if sys.platform == 'darwin':
        try:
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'inet ' in line and '127.0.0.1' not in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        all_ips.add(parts[1])
        except:
            pass
    elif sys.platform == 'win32':
        try:
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
            for line in result.stdout.split('\n'):
                if 'IPv4' in line and ':' in line:
                    ip = line.split(':')[-1].strip()
                    if ip:
                        all_ips.add(ip)
        except:
            pass
    
    # 排序
    def ip_priority(ip):
        if ip.startswith('192.168.'):
            return (0, ip)
        elif ip.startswith('10.'):
            return (1, ip)
        elif ip.startswith('127.'):
            return (9, ip)
        elif ip.startswith('172.'):
            return (8, ip)
        else:
            return (3, ip)
    
    sorted_ips = sorted(all_ips, key=ip_priority)
    result = [ip for ip in sorted_ips if not ip.startswith('127.')]
    
    return result if result else ['127.0.0.1']


def get_local_ip():
    """获取最可能的本机IP"""
    ips = get_all_local_ips()
    return ips[0] if ips else "127.0.0.1"


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
    """获取服务信息"""
    ip = get_local_ip()
    return jsonify({
        'ip': ip,
        'port': 5001,
        'url': f'http://{ip}:5001',
        'all_ips': get_all_local_ips()
    })


@app.route('/api/password', methods=['GET', 'POST'])
def password():
    """密码管理"""
    global ACCESS_PASSWORD
    
    if request.method == 'GET':
        return jsonify({'has_password': bool(ACCESS_PASSWORD)})
    else:
        data = request.get_json()
        action = data.get('action', '')
        
        if action == 'set':
            ACCESS_PASSWORD = data.get('password', '').strip()
            return jsonify({'success': True})
        elif action == 'verify':
            if not ACCESS_PASSWORD:
                return jsonify({'success': True})
            return jsonify({'success': data.get('password', '') == ACCESS_PASSWORD})
        
        return jsonify({'success': False})


if __name__ == '__main__':
    ip = get_local_ip()
    port = 5001
    
    print("=" * 50)
    print("  Stardew Valley Chat Tool")
    print("=" * 50)
    print(f"\n访问地址: http://{ip}:{port}")
    print(f"平台: {sys.platform}")
    print("\n按 Ctrl+C 停止服务\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)
