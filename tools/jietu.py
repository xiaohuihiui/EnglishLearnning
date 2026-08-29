import uiautomator2 as u2
import time
import os
import shutil
from PIL import Image

def main():
    # 设置保存的主目录
    save_dir = r"E:\EnglishStudybook\mikann"
    evidence_base_dir = os.path.join(save_dir, "evidence")
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 0. 动态输入保存的文件名（无需写死）
    book_name = input("请输入要保存的 PDF 文件名（例如：kin_no_phrase）：").strip()
    if not book_name:
        book_name = "output_book"
    
    # 最终输出的完整 PDF 路径
    output_pdf_path = os.path.join(save_dir, f"{book_name}.pdf")
    
    # 检查 PDF 是否已存在，若存在则终止运行
    if os.path.exists(output_pdf_path):
        print(f"\n[提示] 文件 '{output_pdf_path}' 已经存在！为了避免覆盖，程序已自动停止。")
        return

    # 创建对应书本专属的截图保存目录
    book_evidence_dir = os.path.join(evidence_base_dir, book_name)
    if not os.path.exists(book_evidence_dir):
        os.makedirs(book_evidence_dir)

    # 获取总页数
    pages_input = input("请输入总页数（默认 0）：").strip()
    total_pages = int(pages_input) if pages_input.isdigit() else 0
    
    # 连接到模拟器
    d = u2.connect("127.0.0.1:7555")
    print(f"已连接到设备: {d.info}")
    
    image_files = []
    print(f"\n开始自动截屏 [{output_pdf_path}]...")

    for page in range(1, total_pages + 1):
        temp_file_name = os.path.join(book_evidence_dir, f"temp_page_{page:03d}.png")
        cropped_name = os.path.join(book_evidence_dir, f"cropped_{page:03d}.png")
        
        # 1. 截图并保存到专属文件夹
        image = d.screenshot()
        image.save(temp_file_name)
        
        # 2. 精确裁剪图像（顶部裁掉 13% 彻底切除控制栏，底部裁掉 10%）
        with Image.open(temp_file_name) as img:
            width, height = img.size
            # cropped = img.crop((0, int(height * 0.13), width, int(height * 0.90))) for abceed
            cropped = img.crop((0, int(height * 0.09), width, int(height * 0.95)))
            cropped.save(cropped_name)
            image_files.append(cropped_name)
            
        os.remove(temp_file_name)  # 只删除未裁剪的原图，保留裁剪后的截图

        print(f"已完成第 {page}/{total_pages} 页")

        # 3. 执行向左滑动翻页
        d.swipe_ext("left", scale=0.8)
        time.sleep(1.5)

    # 4. 打包合并为无密码 PDF
    print("\n正在生成无密码 PDF...")
    if image_files:
        first_img = Image.open(image_files[0]).convert("RGB")
        other_imgs = [Image.open(img_path).convert("RGB") for img_path in image_files[1:]]
        first_img.save(output_pdf_path, save_all=True, append_images=other_imgs)
        print(f"PDF 导出完毕！已生成: {output_pdf_path}")

    # 5. 将截图文件夹压缩保存
    print(f"\n正在将截图压缩打包至 {book_evidence_dir}.zip ...")
    shutil.make_archive(
        base_name=book_evidence_dir,  # 压缩文件路径（无需带 .zip 后缀）
        format='zip', 
        root_dir=book_evidence_dir  # 被压缩的文件夹
    )
    
    # 压缩完成后清理原始图片文件夹，避免占用空间
    shutil.rmtree(book_evidence_dir)
    print(f"截图归档成功！已保存为压缩包: {book_evidence_dir}.zip")

if __name__ == "__main__":
    main()