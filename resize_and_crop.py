#!/usr/bin/env python3
try:
    from PIL import Image
except ImportError:
    print("[错误] 未检测到 Pillow 库。请先运行: pip install pillow")
    exit(1)
import os
import sys

TARGET_SIZE = (1242, 2688)

def print_usage():
    print("""
图片批量缩放并居中裁剪工具

用法:
  python resize_and_crop.py <input_dir> <output_dir>

参数说明:
  <input_dir>   输入图片文件夹，支持png/jpg/jpeg
  <output_dir>  输出图片文件夹，不存在会自动创建

示例:
  python resize_and_crop.py ./raw_images ./output_images

""")

def process_image(input_path, output_path):
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
    if not os.path.isdir(input_dir):
        print(f"[错误] 输入目录不存在: {input_dir}")
        sys.exit(1)
    os.makedirs(output_dir, exist_ok=True)
    images = [f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if not images:
        print(f"[提示] 输入目录中未找到图片文件: {input_dir}")
        sys.exit(0)
    print(f"共检测到 {len(images)} 张图片，开始处理...")
    for idx, fname in enumerate(images, 1):
        in_path = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, fname)
        try:
            process_image(in_path, out_path)
            print(f"[{idx}/{len(images)}] 处理完成: {fname}")
        except Exception as e:
            print(f"[{idx}/{len(images)}] 处理失败: {fname}，原因: {e}")
    print("\n全部处理完成。输出目录:", output_dir)

if __name__ == "__main__":
    main()
