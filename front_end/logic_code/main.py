import re

from PySide6.QtGui import Qt, QIcon, QPixmap

from front_end.ui_code.ui_mian_window import Ui_MainWindow
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QProgressDialog
import subprocess


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.file_path_output = None
        self.size_source = None
        self.size_target = None
        self.type_source = None
        self.type_target = None
        self.shape_source = None
        self.shape_target = None
        self.bit_source = None
        self.bit_target = None
        self.fps_source = None
        self.fps_target = None
        self.file_path = None
        self.size_kmg = None
        self.bit_rate_kmg = None
        self.total_frames = None

        self.setupUi(self)
        # 设置标题
        self.setWindowTitle("视频崽")
        # 设置icon图片
        self.icon.setPixmap(QPixmap("front_end/images/icon.png"))
        # 设置icon中图片为圆角
        self.icon.setStyleSheet("border-radius: 20px; color: white; background-color: #cfe2f3;")
        # 设置button_chooser的点击事件
        self.button_chooser.clicked.connect(self.choose_file)
        # 设置button_start的点击事件
        self.button_start.clicked.connect(self.start)
        # 隐藏部分控件
        self.spinBox.hide()
        self.label_size_unit.hide()
        self.button_start.hide()
        # 将spinBox的值与size_target绑定

    def choose_file(self):
        # 获取文件路径
        self.file_path = QFileDialog.getOpenFileName(self, "选择视频文件", "./", "视频文件(*.mp4 *.avi *.mkv)")[0]
        # 获取文件信息
        self.get_file_info()
        # 设置文件信息
        self.label_size_source.setText(self.get_size(self.size_source))
        # self.type_source.setText(self.type_source)
        self.label_bit_source.setText(self.get_bit_rate(self.bit_source))
        self.label_fps_source.setText(self.fps_source)
        self.label_shape_source.setText(str(self.shape_source[0]) + "x" + str(self.shape_source[1]))
        self.label_size_unit.setText(self.size_kmg)
        # 显示部分控件
        self.spinBox.show()
        self.label_size_unit.show()
        self.button_start.show()

    # 利用ffprobe获取文件大小，格式，分辨率，帧率，码率
    def get_file_info(self):
        output = subprocess.getoutput(
            "ffprobe -v quiet -print_format json -show_format -show_streams " + self.file_path)
        output = eval(output)
        print(output)
        self.size_source = output["format"]["size"]
        self.type_source = output["format"]["format_name"].split(",")[1]
        self.shape_source = [output["streams"][0]["width"], output["streams"][0]["height"]]
        self.bit_source = output["streams"][0]["bit_rate"]
        self.fps_source = output["streams"][0]["r_frame_rate"][:-2]
        self.total_frames = output["streams"][0]["nb_frames"]
        print(self.total_frames)

    def get_bit_rate(self, number):
        # 只保留整数部分
        number = int(number) / 8
        if number < 1024:
            self.bit_rate_kmg = "B/s"
            return str(number) + "B/s"
        elif number < 1024 ** 2:
            self.bit_rate_kmg = "KB/s"
            return str(number // 1024) + "KB/s"
        elif number < 1024 ** 3:
            self.bit_rate_kmg = "MB/s"
            return str(number // 1024 ** 2) + "MB/s"
        elif number < 1024 ** 4:
            self.bit_rate_kmg = "GB/s"
            return str(number // 1024 ** 3) + "GB/s"
        else:
            self.bit_rate_kmg = "TB/s"
            return str(number // 1024 ** 4) + "TB/s"

    def get_size(self, number):
        # 只保留整数部分
        number = int(number)
        if number < 1024:
            self.size_kmg = "B"
            return str(number) + "B"
        elif number < 1024 ** 2:
            self.size_kmg = "KB"
            return str(number // 1024) + "Kb"
        elif number < 1024 ** 3:
            self.size_kmg = "MB"
            return str(number // 1024 ** 2) + "MB"
        elif number < 1024 ** 4:
            self.size_kmg = "GB"
            return str(number // 1024 ** 3) + "GB"
        else:
            self.size_kmg = "TB"
            return str(number // 1024 ** 4) + "TB"

    def start(self):
        # 获取tabwidget的当前页
        current_tab = self.tabWidget.currentIndex()
        if current_tab == 0:
            cmd = self.tab_0_start()

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # 创建进度条窗口
        self.progress_window = QProgressDialog("正在压缩...", "取消", 0, int(self.total_frames), self)
        self.progress_window.setWindowTitle("压缩进度")
        self.progress_window.setWindowModality(Qt.WindowModal)
        self.progress_window.setCancelButton(None)
        self.progress_window.show()

        for line in p.stdout:
            print(line)
            # 从line中提取当前帧，frame= 之后的第一个数字
            current_frame = int(re.findall(r"frame=\s*(\d+)", line)[0])
            # 设置进度条的值
            self.progress_window.setValue(current_frame)
            # 更新界面
            QApplication.processEvents()
            # 如果进度条被取消，就停止压缩
            if self.progress_window.wasCanceled():
                p.kill()
                break
        p.wait()

    def tab_0_start(self):
        self.size_target = self.spinBox.value()
        # 输出路径与输入路径相同
        # 输出文件格式与输入文件格式相同
        # 输出文件名称设为"原文件名_压缩后"
        self.file_path_output = self.file_path.split(".")[0] + "_compressed." + self.file_path.split(".")[1]
        return "ffmpeg -i " + self.file_path + " -fs " + str(self.size_target) + self.size_kmg + " -c:v hevc_videotoolbox " + self.file_path_output
        # return [
        #     "ffmpeg",
        #     "-i",
        #     self.file_path,
        #     "-fs",
        #     str(self.size_target) + self.size_kmg,
        #     "-c:v hevc_videotoolbox",
        #     "outpu"
        # ]


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec_()
