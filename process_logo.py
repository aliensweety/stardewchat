"""
Logo图片处理脚本 v2
将白色背景的手绘线稿转换为：
1. 透明背景
2. 纯黑色线稿（消除灰色/白色残留）
3. 生成多种尺寸的logo
"""
from PIL import Image
import os

def process_logo(input_path, output_dir):
    """
    处理logo图片：
    1. 将线稿转为纯黑色
    2. 将白色/浅色背景转换为透明
    3. 裁剪到内容边缘
    4. 生成多种尺寸
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 打开原图
    print(f"正在处理: {input_path}")
    img = Image.open(input_path).convert('RGBA')
    print(f"原始尺寸: {img.size}")
    
    # 获取像素数据
    pixels = img.load()
    width, height = img.size
    
    # 背景阈值：高于此值视为背景（会被设为透明）
    bg_threshold = 200
    # 线稿阈值：低于此值视为线稿（会被设为纯黑）
    line_threshold = 180
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # 计算灰度值
            gray = (r + g + b) // 3
            
            if gray > bg_threshold:
                # 背景像素 -> 完全透明
                pixels[x, y] = (0, 0, 0, 0)
            elif gray < line_threshold:
                # 线稿像素 -> 纯黑色，完全不透明
                pixels[x, y] = (0, 0, 0, 255)
            else:
                # 过渡区域：半透明黑色，实现抗锯齿效果
                alpha = int(255 * (1 - (gray - line_threshold) / (bg_threshold - line_threshold)))
                pixels[x, y] = (0, 0, 0, alpha)
    
    # 裁剪到非透明内容的边界
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        print(f"裁剪后尺寸: {img.size}")
    
    # 添加一些边距
    padding = 30
    new_width = img.width + padding * 2
    new_height = img.height + padding * 2
    padded = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    padded.paste(img, (padding, padding))
    img = padded
    
    # 保存原始透明版本
    original_path = os.path.join(output_dir, 'logo_original.png')
    img.save(original_path, 'PNG')
    print(f"保存原始透明版本: {original_path}")
    
    # 生成不同尺寸的logo
    sizes = {
        'logo_16.png': 16,      # 小图标
        'logo_32.png': 32,      # 标准小图标
        'logo_48.png': 48,      # 中等图标
        'logo_64.png': 64,      # 中等图标
        'logo_128.png': 128,    # 大图标
        'logo_256.png': 256,    # 超大图标
        'logo_512.png': 512,    # 超清图标
    }
    
    for filename, size in sizes.items():
        # 按比例缩放，保持宽高比
        aspect = img.width / img.height
        if aspect > 1:
            new_w = size
            new_h = int(size / aspect)
        else:
            new_h = size
            new_w = int(size * aspect)
        
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # 创建正方形画布，居中放置
        square = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        paste_x = (size - new_w) // 2
        paste_y = (size - new_h) // 2
        square.paste(resized, (paste_x, paste_y))
        
        output_path = os.path.join(output_dir, filename)
        square.save(output_path, 'PNG')
        print(f"生成: {output_path} ({size}x{size})")
    
    # 生成Windows ICO文件（包含多种尺寸）
    ico_sizes = [16, 32, 48, 64, 128, 256]
    ico_images = []
    for size in ico_sizes:
        aspect = img.width / img.height
        if aspect > 1:
            new_w = size
            new_h = int(size / aspect)
        else:
            new_h = size
            new_w = int(size * aspect)
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        square = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        paste_x = (size - new_w) // 2
        paste_y = (size - new_h) // 2
        square.paste(resized, (paste_x, paste_y))
        ico_images.append(square)
    
    ico_path = os.path.join(output_dir, 'app_icon.ico')
    ico_images[0].save(ico_path, format='ICO', sizes=[(s, s) for s in ico_sizes], 
                       append_images=ico_images[1:])
    print(f"生成Windows多尺寸ICO: {ico_path}")
    
    # 生成favicon.ico
    favicon = ico_images[1]  # 32x32
    favicon_path = os.path.join(output_dir, 'favicon.ico')
    favicon.save(favicon_path, format='ICO')
    print(f"生成favicon: {favicon_path}")
    
    print("\n✅ Logo处理完成！")
    print(f"所有文件保存在: {output_dir}")
    print("\n线稿已转换为纯黑色，背景已透明化。")
    return output_dir

if __name__ == '__main__':
    input_file = r'd:\项目\skill开发\项目\stardew-chat\1000075884.png'
    output_directory = r'd:\项目\skill开发\项目\stardew-chat\assets\logo'
    process_logo(input_file, output_directory)
