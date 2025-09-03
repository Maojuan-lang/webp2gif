import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import struct
import imageio
import numpy as np
from PIL import Image
import os
import threading


class WebPtoGIFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("WebP 转 GIF 转换器")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # 居中窗口
        self.center_window()

        # 设置样式
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))

        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="WebP 转 GIF 转换器", style="Header.TLabel")
        title_label.pack(pady=10)

        # 拖放区域
        drop_frame = ttk.LabelFrame(main_frame, text="拖放 WebP 文件到这里", padding="10",height=100)
        drop_frame.pack(fill=tk.X, pady=10)
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        drop_frame.pack_propagate(0)

        self.drop_label = ttk.Label(drop_frame, text="拖放文件或点击下方按钮选择文件", wraplength=500)
        self.drop_label.pack(pady=10)

        # 选择文件按钮
        select_button = ttk.Button(main_frame, text="选择 WebP 文件", command=self.select_file)
        select_button.pack(pady=5)

        # 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="转换设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=10)

        # 颜色数量设置
        color_frame = ttk.Frame(settings_frame)
        color_frame.pack(fill=tk.X, pady=5)

        ttk.Label(color_frame, text="颜色深度:").pack(side=tk.LEFT)
        self.color_var = tk.StringVar(value="128")
        color_combo = ttk.Combobox(color_frame, textvariable=self.color_var,
                                   values=["256", "128", "64", "32"], state="readonly", width=10)
        color_combo.pack(side=tk.LEFT, padx=10)

        # 帧数减少比例设置
        frame_frame = ttk.Frame(settings_frame)
        frame_frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame_frame, text="帧数减少比例:").pack(side=tk.LEFT)
        self.frame_var = tk.StringVar(value="1/4")
        frame_combo = ttk.Combobox(frame_frame, textvariable=self.frame_var,
                                   values=["不变", "1/2", "1/3", "1/4"], state="readonly", width=10)
        frame_combo.pack(side=tk.LEFT, padx=10)

        # 输出文件名设置
        output_frame = ttk.Frame(settings_frame)
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_frame, text="输出文件名:").pack(side=tk.LEFT)
        self.output_var = tk.StringVar(value="output.gif")
        output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=20)
        output_entry.pack(side=tk.LEFT, padx=10)

        # 转换按钮
        self.convert_button = ttk.Button(main_frame, text="开始转换", command=self.start_conversion)
        self.convert_button.pack(pady=20)

        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')

        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=5)

        # 存储文件路径
        self.file_path = None

        # 存储原始帧持续时间
        self.original_durations = []

    def generate_output_filename(self, colors, frame_reduction):
        """生成输出文件名，包含颜色深度和帧数减少比例信息"""
        if not self.file_path:
            return "output.gif"

        # 获取原始文件名（不含扩展名）的前几个字符
        original_name = os.path.splitext(os.path.basename(self.file_path))[0]
        # 截取前10个字符，如果文件名较短则使用全名
        name_prefix = original_name[:10] if len(original_name) > 10 else original_name

        # 获取原始文件所在目录
        output_dir = os.path.dirname(self.file_path)

        # 将帧数比例中的斜杠替换为下划线
        frame_ratio = frame_reduction.replace("/", "_")

        # 生成新文件名
        new_filename = f"{name_prefix}_{colors}_{frame_ratio}frames.gif"

        # 返回完整路径
        return os.path.join(output_dir, new_filename)

    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def on_drop(self, event):
        # 处理文件拖放事件
        files = self.root.tk.splitlist(event.data)
        if files and files[0].lower().endswith('.webp'):
            self.file_path = files[0]
            self.drop_label.config(text=f"已选择文件: {os.path.basename(self.file_path)}")
        else:
            messagebox.showerror("错误", "请拖放有效的 WebP 文件")

    def select_file(self):
        # 选择文件对话框
        file_path = filedialog.askopenfilename(
            title="选择 WebP 文件",
            filetypes=[("WebP 文件", "*.webp"), ("所有文件", "*.*")]
        )
        if file_path and file_path.lower().endswith('.webp'):
            self.file_path = file_path
            self.drop_label.config(text=f"已选择文件: {os.path.basename(self.file_path)}")
        elif file_path:
            messagebox.showerror("错误", "请选择有效的 WebP 文件")

    def start_conversion(self):
        # 开始转换
        if not self.file_path:
            messagebox.showerror("错误", "请先选择 WebP 文件")
            return

        # 禁用按钮并显示进度条
        self.convert_button.config(state='disabled')
        self.progress.pack(fill=tk.X, pady=5)
        self.progress.start()
        self.status_var.set("正在转换...")

        # 在新线程中执行转换
        thread = threading.Thread(target=self.convert_webp_to_gif)
        thread.daemon = True
        thread.start()

    def convert_webp_to_gif(self):
        try:
            # 获取用户设置
            colors = int(self.color_var.get())
            frame_reduction = self.frame_var.get()
            output_path = self.generate_output_filename(colors,frame_reduction)

            # 解析帧减少比例
            if frame_reduction == "不变":
                keep_ratio = 1.0
            elif frame_reduction == "1/2":
                keep_ratio = 0.5
            elif frame_reduction == "1/3":
                keep_ratio = 2 / 3
            else:  # 1/4
                keep_ratio = 0.75

            # 读取WebP文件的帧持续时间
            frame_durations = []
            with open(self.file_path, 'rb') as f:
                # 读取文件头部 RIFF 标志
                riff = f.read(4)
                if riff != b'RIFF':
                    raise ValueError("文件不是有效的 WebP 文件")

                # 读取文件大小
                file_size = struct.unpack('<I', f.read(4))[0]

                # 读取文件类型 WEBP 标志
                webp = f.read(4)
                if webp != b'WEBP':
                    raise ValueError("文件不是有效的 WebP 文件")

                while f.tell() < file_size:
                    # 读取四字节的 chunk 标志
                    chunk_id = f.read(4)
                    if chunk_id == b'ANMF':
                        # 读取 ANMF chunk 大小
                        anmf_size = struct.unpack('<I', f.read(4))[0]

                        # 读取 ANMF chunk 数据
                        chunk_data = f.read(anmf_size)

                        # 解析 Frame Duration，偏移量为 12，读取3个字节
                        duration_bytes = chunk_data[12:15]
                        duration = (duration_bytes[2] << 16) + (duration_bytes[1] << 8) + duration_bytes[0]
                        frame_durations.append(duration)
                    else:
                        # 跳过未知的 chunk
                        chunk_size = struct.unpack('<I', f.read(4))[0]
                        f.seek(chunk_size, 1)

            # 使用imageio读取webp文件
            webp_reader = imageio.get_reader(self.file_path)

            # 初始化一个空的gif列表，用于存储每一帧
            gif_frames = []

            # 读取每一帧图像
            for i, frame in enumerate(webp_reader):
                gif_frames.append(frame)

            # 关闭reader
            webp_reader.close()

            # 计算需要保留的帧数
            total_frames = len(gif_frames)
            keep_frames_count = int(total_frames * keep_ratio)

            # 选择要保留的帧索引（均匀分布）
            keep_indices = np.linspace(0, total_frames - 1, keep_frames_count, dtype=int)

            # 创建减少后的帧列表
            reduced_frames = [gif_frames[i] for i in keep_indices]

            # 保持每帧持续时间不变，使用原始持续时间
            # 如果原始持续时间不可用，使用默认值100ms
            if frame_durations and len(frame_durations) >= total_frames:
                # 使用第一帧的持续时间作为所有帧的持续时间
                frame_duration = frame_durations[0]
            else:
                frame_duration = 100  # 默认100ms

            # 对减少后的帧进行颜色量化
            optimized_frames = []
            for frame in reduced_frames:
                pil_img = Image.fromarray(frame)
                # 对图像进行量化
                quantized_img = pil_img.quantize(colors=colors)
                # 转换为RGB模式以便imageio可以处理
                quantized_img_rgb = quantized_img.convert('RGB')
                optimized_frames.append(np.array(quantized_img_rgb))


            # 保存优化后的GIF，每帧使用相同的持续时间
            imageio.mimsave(output_path, optimized_frames, format='GIF', loop=0, duration=frame_duration)

            # 更新UI
            self.root.after(0, self.conversion_complete, total_frames, keep_frames_count)

        except Exception as e:
            # 显示错误信息
            self.root.after(0, lambda: messagebox.showerror("错误", f"转换过程中发生错误: {str(e)}"))
            self.root.after(0, self.reset_ui)

    def conversion_complete(self, total_frames, keep_frames_count):
        # 转换完成
        self.progress.stop()
        self.progress.pack_forget()
        self.convert_button.config(state='normal')
        self.status_var.set(f"转换完成! 帧数从 {total_frames} 减少到 {keep_frames_count}")
        messagebox.showinfo("完成", "转换已完成!")

    def reset_ui(self):
        # 重置UI状态
        self.progress.stop()
        self.progress.pack_forget()
        self.convert_button.config(state='normal')
        self.status_var.set("就绪")


if __name__ == "__main__":
    # 创建支持拖放的Tkinter窗口
    root = TkinterDnD.Tk()
    app = WebPtoGIFConverter(root)
    root.mainloop()