#!/usr/bin/env python3
try:
    from PIL import Image
except ImportError:
    print("[错误] 未检测到 Pillow 库。请先运行: pip install pillow")
    exit(1)
import os
import sys
import requests
import json
import base64

TARGET_SIZE = (1242, 2688)

def print_usage():
    print("""
图片批量缩放并居中裁剪工具

用法:
  python resize_and_crop.py <input_dir> <output_dir> [options]

参数说明:
  <input_dir>   输入图片文件夹，支持png/jpg/jpeg
  <output_dir>  输出图片文件夹，不存在会自动创建

选项:
  --tinypng      使用TinyPNG API压缩（需要设置环境变量TINY_PNG_API_KEY）

示例:
  python resize_and_crop.py ./raw_images ./output_images
  python resize_and_crop.py ./raw_images ./output_images --tinypng

环境变量:
  TINY_PNG_API_KEY   TinyPNG API密钥，从 https://tinypng.com/developers 获取

""")

def compress_with_tinypng(input_path, output_path, api_key):
    """使用TinyPNG API压缩图片"""
    try:
        # 读取图片文件
        with open(input_path, 'rb') as f:
            image_data = f.read()
        
        # TinyPNG API需要Base64编码的认证
        # 格式: Basic base64(api_key:)
        auth_string = f"{api_key}:"
        auth_b64 = base64.b64encode(auth_string.encode()).decode()
        
        # 发送到TinyPNG API
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/octet-stream'
        }
        
        response = requests.post(
            'https://api.tinypng.com/shrink',
            data=image_data,
            headers=headers
        )
        
        if response.status_code == 201:
            # 压缩成功，下载压缩后的图片
            result = response.json()
            compressed_url = result['output']['url']
            
            # 下载压缩后的图片
            compressed_response = requests.get(compressed_url)
            if compressed_response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(compressed_response.content)
                
                # 显示压缩信息
                original_size = len(image_data)
                compressed_size = len(compressed_response.content)
                compression_ratio = (1 - compressed_size / original_size) * 100
                print(f"    压缩: {original_size/1024:.1f}KB -> {compressed_size/1024:.1f}KB (减少{compression_ratio:.1f}%)")
                return True
            else:
                print(f"    下载压缩图片失败: {compressed_response.status_code}")
                return False
        else:
            print(f"    TinyPNG API错误: {response.status_code}")
            if response.status_code == 401:
                print("    API密钥无效，请检查TINY_PNG_API_KEY环境变量")
            elif response.status_code == 429:
                print("    API调用次数超限，请稍后重试")
            elif response.status_code == 400:
                print("    API请求格式错误，请检查图片格式是否支持")
                try:
                    error_info = response.json()
                    if 'message' in error_info:
                        print(f"    错误详情: {error_info['message']}")
                except:
                    pass
            return False
            
    except Exception as e:
        print(f"    TinyPNG压缩失败: {e}")
        return False

def process_image(input_path, output_path, use_tinypng=False, api_key=None):
    img = Image.open(input_path)
    # 1. 等比缩放到目标尺寸的短边
    img_ratio = img.width / img.height
    target_ratio = TARGET_SIZE[0] / TARGET_SIZE[1]
    if img_ratio > target_ratio:
        # 图片比目标宽，先以高度为基准缩放
        new_height = TARGET_SIZE[1]
        new_width = int(img_ratio * new_height)
    else:
        # 图片比目标窄或正好，先以宽度为基准缩放
        new_width = TARGET_SIZE[0]
        new_height = int(new_width / img_ratio)
    img = img.resize((new_width, new_height), Image.LANCZOS)
    # 2. 居中裁剪到目标尺寸
    left = (new_width - TARGET_SIZE[0]) // 2
    top = (new_height - TARGET_SIZE[1]) // 2
    right = left + TARGET_SIZE[0]
    bottom = top + TARGET_SIZE[1]
    img = img.crop((left, top, right, bottom))
    
    if use_tinypng and api_key:
        # 先保存临时文件，然后用TinyPNG压缩
        # 使用原始文件扩展名，避免PIL无法识别的问题
        temp_path = output_path + '_temp' + os.path.splitext(output_path)[1]
        img.save(temp_path)
        
        # 使用TinyPNG压缩
        success = compress_with_tinypng(temp_path, output_path, api_key)
        
        # 删除临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if not success:
            # 如果TinyPNG失败，使用普通保存
            print("    回退到普通保存")
            img.save(output_path)
    else:
        img.save(output_path)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_usage()
        sys.exit(0)
    if len(sys.argv) < 3:
        print("[错误] 参数不足。请指定输入和输出文件夹。\n")
        print_usage()
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # 检查是否使用TinyPNG
    use_tinypng = "--tinypng" in sys.argv
    api_key = None
    
    if use_tinypng:
        api_key = os.environ.get('TINY_PNG_API_KEY')
        if not api_key:
            print("[错误] 未设置TINY_PNG_API_KEY环境变量")
            print("请设置环境变量: export TINY_PNG_API_KEY='your_api_key'")
            print("或从 https://tinypng.com/developers 获取API密钥")
            sys.exit(1)
        
        # 检查requests库
        try:
            import requests
        except ImportError:
            print("[错误] 未检测到requests库。请先运行: pip install requests")
            sys.exit(1)
    
    if not os.path.isdir(input_dir):
        print(f"[错误] 输入目录不存在: {input_dir}")
        sys.exit(1)
    os.makedirs(output_dir, exist_ok=True)
    images = [f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if not images:
        print(f"[提示] 输入目录中未找到图片文件: {input_dir}")
        sys.exit(0)
    
    mode = "TinyPNG压缩" if use_tinypng else "普通处理"
    print(f"共检测到 {len(images)} 张图片，开始{mode}...")
    
    for idx, fname in enumerate(images, 1):
        in_path = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, fname)
        try:
            process_image(in_path, out_path, use_tinypng, api_key)
            print(f"[{idx}/{len(images)}] 处理完成: {fname}")
        except Exception as e:
            print(f"[{idx}/{len(images)}] 处理失败: {fname}，原因: {e}")
    print("\n全部处理完成。输出目录:", output_dir)

if __name__ == "__main__":
    main()
