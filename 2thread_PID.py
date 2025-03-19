import sys
import numpy as np
import cv2
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap, QMovie
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QSplitter
from simple_pyspin import Camera
from PIL import Image
import pandas as pd
import os
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


class Window1(QWidget):
    """播放GIF动画的窗口"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Genshin Impact")
        # 设置窗口为全屏
        self.setGeometry(0, 0, QApplication.desktop().screenGeometry().width(), QApplication.desktop().screenGeometry().height())

        # 设置动画标签
        self.movie = QMovie('genshin.gif')  # 替换为你的实际GIF文件路径
        self.animation_label = QLabel(self)
        self.animation_label.setAlignment(Qt.AlignCenter)
        self.animation_label.setMovie(self.movie)

        # 让GIF自动缩放以适应窗口
        self.animation_label.setScaledContents(True)

        layout = QVBoxLayout()
        layout.addWidget(self.animation_label)
        self.setLayout(layout)

        # 当GIF播放完毕后，关闭当前窗口并打开主窗口
        self.movie.finished.connect(self.on_animation_finished)

        # 开始播放动画
        self.movie.start()

        # 设置一个定时器，10秒后触发关闭窗口
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)  # 使定时器只触发一次
        self.timer.timeout.connect(self.on_timer_timeout)  # 10秒后关闭窗口
        self.timer.start(5400)  # 10秒定时器

    def on_animation_finished(self):
        """GIF播放完后，关闭当前窗口并启动主窗口"""
        print("GIF animation finished.")
        self.close()  # 关闭当前动画窗口
        self.window2 = CameraApp()  # 创建主窗口
        self.window2.show()  # 显示主窗口
        
    def on_timer_timeout(self):
        self.close()  # 关闭当前动画窗口
        self.window2 = CameraApp()  # 创建主窗口
        self.window2.show()  # 显示主窗口

class CameraCaptureThread(QThread):
    update_image_signal = pyqtSignal(Image.Image, list, list, int)  # 用信号传递图像和参数
    
    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.cam = camera
        self.size_ = 700

    def run(self):
        while True:
            PID_exposuretime(self.cam, 4e-3, 4e-4, 8e-4)  # 调整曝光时间
            img_arr = self.cam.get_array()  # 获取图像数据
            params, img_crop, max_value, img_resize, center, length, iimg = draw(img_arr, 2, self.size_)
            
            # 发射信号
            self.update_image_signal.emit(iimg, list(center), list(length), max_value)
            
            if length[0] == 0:
                self.size_ = 700
            else:
                self.size_ = min(max(50, int((length[0] + length[1]) * 2.5)), 1000)

class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Control and Image Analysis")
        self.setGeometry(100, 100, 800, 600)  # 初始大小
        self.setMinimumSize(600, 400)  # 设置最小窗口尺寸
        self.setMaximumSize(1200, 900)  # 设置最大窗口尺寸

        # 主布局
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        # 创建分割器将窗口分成两部分（左侧显示图像，右侧显示表格）
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # 左侧布局（显示图像）
        self.left_layout = QVBoxLayout()
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(self.image_label)
        
        # 创建左侧的 widget
        left_widget = QWidget()
        left_widget.setLayout(self.left_layout)

        # 右侧布局（显示表格和标签）
        self.right_layout = QVBoxLayout()
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(['光斑参数', ' '])
        self.right_layout.addWidget(self.table_widget)

        # 当前增益和曝光时间标签
        self.gain_label = QLabel("当前增益 (dB): 0", self)
        self.exposure_label = QLabel("当前曝光时间 (ms): 0", self)
        self.right_layout.addWidget(self.gain_label)
        self.right_layout.addWidget(self.exposure_label)

        # 创建右侧的 widget
        right_widget = QWidget()
        right_widget.setLayout(self.right_layout)

        # 添加左右 widget 到分割器
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)

        # 设置左右部分的比例（7:3 比例）
        self.splitter.setSizes([700, 300])

        # 相机相关设置
        self.cam = Camera()
        self.cam.init()
        self.cam.AcquisitionFrameRateAuto = 'Off'
        self.cam.AcquisitionFrameRateEnabled = True
        # self.cam.AcquisitionFrameRate = 20
        self.cam.AcquisitionFrameRate = 8
        self.cam.ExposureAuto = 'Off'
        self.cam.GainAuto = 'Off'
        self.cam.Gain = 0
        self.cam.ExposureTime = 5 * 1000
        
        # 创建相机捕捉线程
        self.capture_thread = CameraCaptureThread(self.cam)
        self.capture_thread.update_image_signal.connect(self.update_image)  # 信号连接槽函数
        self.cam.start()
        self.capture_thread.start()

    def update_image(self, iimg, center, length, max_value):
        # 更新图像显示
        img_qt = self.convert_to_qt(iimg)
        self.image_label.setPixmap(img_qt)
        
        # 更新表格
        self.update_table(center, length, max_value)

        # 更新增益和曝光时间标签
        self.gain_label.setText(f"当前增益 (dB): {self.cam.Gain}")
        self.exposure_label.setText(f"当前曝光时间 (ms): {self.cam.ExposureTime / 1000}")

    def update_table(self, center, length, max_value):
        data = {
            '光斑参数': ['长轴/um', '短轴/um', '中心坐标x/pixel', '中心坐标y/pixel', '最大值'],
            ' ': [
                np.max(np.array(length)) * 3.45 * 2,
                np.min(np.array(length)) * 3.45 * 2,
                center[0],
                center[1],
                max_value
            ]
        }
        df = pd.DataFrame(data)
        self.table_widget.setRowCount(len(df))
        for i, (key, value) in enumerate(zip(df['光斑参数'], df[' '])):
            self.table_widget.setItem(i, 0, QTableWidgetItem(str(key)))
            self.table_widget.setItem(i, 1, QTableWidgetItem(str(value)))

    def convert_to_qt(self, img_pil):
        img_rgb = gray_pseudocolor(img_pil)
        img_array = np.array(img_rgb)
        h, w, _ = img_array.shape
        img_qt = QImage(img_array.data, w, h, 3 * w, QImage.Format_RGB888)
        
        # Scale the image to fit within the QLabel
        pixmap = QPixmap.fromImage(img_qt)
        pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        return pixmap


def PID_exposuretime(cam, k_m, k_i, k_d):
    img_arr = cam.get_array()
    img_arr_cov = cv2.GaussianBlur(img_arr, (5, 5), 3)
    Max = np.max(img_arr_cov)

    integral = 0
    last = 400
    diff = 0
    temp = 0

    while (Max < 225 or Max > 245):
        err = 237 - Max
        
        if last == 400:
            diff = 0
        else:
            diff = err - last
        
        temp = cam.ExposureTime * (1 + float(k_m * err + k_i * integral - k_d * diff))
        
        if temp > 20 and temp < 45000:
            cam.ExposureTime = temp
        elif temp <= 20:
            cam.ExposureTime = 20
            img_arr = cam.get_array()
            img_arr_cov = cv2.GaussianBlur(img_arr, (5, 5), 3)
            Max = np.max(img_arr_cov)
            
            if Max > 220:
                break
            
            last = 400
            integral = 0
        else:
            cam.ExposureTime = 45000
            img_arr = cam.get_array()
            img_arr_cov = cv2.GaussianBlur(img_arr, (5, 5), 3)
            Max = np.max(img_arr_cov)
            
            if Max < 250:
                break
            
            last = 400
            integral = 0
        
        img_arr = cam.get_array()
        img_arr_cov = cv2.GaussianBlur(img_arr, (5, 5), 3)
        Max = np.max(img_arr_cov)
        last = err
        integral = integral + err


def draw(img, scale, size):
    scale = int(scale)
    img = np.array(img)
    crop_center, img_crop = crop(img, size)
    max_value = np.max(img_crop)
    reshape = (img_crop.shape[1] // scale, img_crop.shape[0] // scale)
    pic = Image.fromarray(img_crop, 'L')
    pic = pic.resize(reshape, resample=Image.Resampling.LANCZOS)
    img_resize = np.array(pic)
    params, fit_result = fit(img_resize, scale)
    if fit_result is None:
        center, length, angle = ((0, 0), (0, 0), 0)
        img_ell = img
        center_mod = (center[0] + max(crop_center[1] + (-size//2) + 1, 0), center[1] + max(crop_center[0] + (-size//2) + 1, 0))
        return (params, img_crop, max_value, img_resize, center_mod, length, Image.fromarray(img_ell, 'L'))
    else:
        center, length, angle = fit_result
    center_mod = (center[0] + max(crop_center[1] + (-size//2) + 1, 0), center[1] + max(crop_center[0] + (-size//2) + 1, 0))
    img_ell = draw_ellipse(img, center_mod, length, angle, crop_center, size)
    return (params, img_crop, max_value, img_resize, center_mod, length, Image.fromarray(img_ell, 'L'))


def crop(arr, size):
    arr = arr.copy()
    arr_g = cv2.GaussianBlur(arr, (5, 5), 3)
    max_indices = np.argwhere(arr_g == np.max(arr_g))
    mid_index = len(max_indices) // 2
    selected_index = max_indices[mid_index]
    
    half_size = size // 2
    minus_half_size = -size//2
    start_row = max(0, selected_index[0] + minus_half_size + 1)
    end_row = min(arr.shape[0], selected_index[0] + half_size + 1)
    start_col = max(0, selected_index[1] + minus_half_size + 1)
    end_col = min(arr.shape[1], selected_index[1] + half_size + 1)
    
    cropped_area = arr[start_row:end_row, start_col:end_col]
    crop_center = (selected_index[0], selected_index[1])
    
    return (crop_center, cropped_area)


def fit(arr, scale):
    y_length, x_length = arr.shape
    x_data = np.linspace(0, x_length - 1, x_length)
    y_data = np.linspace(0, y_length - 1, y_length)
    x, y = np.meshgrid(x_data, y_data)
    mask = generate_mask(x_length, y_length).ravel()
    
    initial_guess = [200, x_length // 2, y_length // 2, x_length / 12, y_length / 12, 0, 0]
    
    bounds = ([0, 0, 0, 0, 0, -1.0, 0], [np.inf, x_length, y_length, np.inf, np.inf, 1.0, np.inf])
    
    if np.count_nonzero(mask) < 5:  # Ensure enough data points
        print("Too amny zeros")
        return None, None  # Return None if no valid points for fitting
    
    try:
        params, covariance = curve_fit(gaussian_2d_with_xy, (x.ravel()[mask], y.ravel()[mask]), arr.ravel()[mask], p0=initial_guess, bounds=bounds)
    except RuntimeError as e:
        print('Failed Fit:', e)
        return (None, None)

    a_fit, b_x_fit, b_y_fit, sigma_x_fit, sigma_y_fit, c_fit, d_fit = params
    A = np.array([[1/(2*sigma_x_fit**2), -c_fit/(2*sigma_x_fit*sigma_y_fit)],
                  [-c_fit/(2*sigma_x_fit*sigma_y_fit), 1/(2*sigma_y_fit**2)]]) / 2

    eigenvalues, eigenvectors = np.linalg.eig(A)
    O = eigenvectors.T
    angle = np.arccos(O[0, 0])
    if O[0, 1] < 0:
        angle = -angle

    if np.any(eigenvalues <= 0):
        print("Eigenvalues are non-positive. Cannot compute axis lengths.")
        return (None, None)
    
    
    return ((a_fit, b_x_fit * scale, b_y_fit * scale, sigma_x_fit * scale, sigma_y_fit * scale, c_fit, 
             d_fit), ((b_x_fit*scale, b_y_fit*scale), np.sqrt(1 / eigenvalues) * scale, angle))


def draw_ellipse(array, center, length, angle, crop_center, size):
    a, b = length
    if a != 0 and b != 0:
        thickness = 1
        array_shape = array.shape
        y, x = np.indices(array_shape)
        x_center, y_center = center
        x = x - x_center
        y = y - y_center
        theta = angle
        x_rot = x * np.cos(theta) + y * np.sin(theta)
        y_rot = -x * np.sin(theta) + y * np.cos(theta)
        ellipse_equation = (x_rot**2 / a**2 + y_rot**2 / b**2)
        boundary_mask = np.isclose(ellipse_equation, 1, atol=0.015 * np.sqrt(200 * 200 / (a * b)))
        boundary_y, boundary_x = np.where(boundary_mask)
        angles = np.linspace(0, 2 * np.pi, num=12, endpoint=False)
        thickness_levels = np.arange(1, thickness + 1)
        thickness_offsets = np.array([
            np.cos(angles[:, np.newaxis]) * thickness_levels,
            np.sin(angles[:, np.newaxis]) * thickness_levels
        ])
        new_coords = np.array([
            boundary_x[:, np.newaxis] + thickness_offsets[0].reshape(-1),
            boundary_y[:, np.newaxis] + thickness_offsets[1].reshape(-1)
        ]).reshape(2, -1).astype(int)
        valid_mask = (
            (new_coords[0] >= 0) & (new_coords[0] < array_shape[1]) &
            (new_coords[1] >= 0) & (new_coords[1] < array_shape[0])
        )
        array[new_coords[1][valid_mask], new_coords[0][valid_mask]] = 0
    
    thick = 3
    x1 = max(crop_center[0] + (-size)//2 + 1, 0)
    x2 = min(crop_center[0] + size//2, array_shape[0]-1)
    y1 = max(crop_center[1] + (-size)//2 + 1, 0)
    y2 = min(crop_center[1] + size//2, array_shape[1]-1)
    array[x1-thick+1:x2, y1-thick+1:y1+1] = 255
    array[x2:x2+thick, y1-thick+1:y2] = 255
    array[x1+1:x2+thick, y2:y2+thick] = 255
    array[x1-thick+1:x1+1, y1+1:y2+thick] = 255

    return array

def gray_pseudocolor(gray_image, colormap_name='jet'):
    gray_array = np.array(gray_image)
    colormap = plt.get_cmap(colormap_name)
    colored_image = colormap(gray_array / 255.0)
    colored_image = (colored_image[:, :, :3] * 255).astype(np.uint8)
    pseudocolor_image = Image.fromarray(colored_image, mode='RGB')
    return pseudocolor_image

def generate_mask(size_x, size_y):
    random_mask1 = np.random.rand(size_y, size_x)
    random_mask2 = np.random.rand(size_y, size_x)
    x = np.linspace(-size_x//2, size_x//2, size_x)
    y = np.linspace(-size_y//2, size_y//2, size_y)
    x, y = np.meshgrid(x, y)
    
    sigma1 = 0.9 * np.sqrt(size_y * size_x)
    gaussian_weight1 = np.exp(-(x**2 + y**2) / (2 * sigma1**2))
    mask1 = (random_mask1 * gaussian_weight1) > 0.83
    
    sigma2 = 0.08 * np.sqrt(size_y * size_x)
    gaussian_weight2 = np.exp(-(x**2 + y**2) / (2 * sigma2**2))
    mask2 = (random_mask2 * gaussian_weight2) > 0.2
    
    return mask1 | mask2

def gaussian_2d_with_xy(xy, a, b_x, b_y, sigma_x, sigma_y, c, d):
    x, y = xy
    return a * np.exp(-((x - b_x) ** 2 / (2 * sigma_x ** 2) + 
                         (y - b_y) ** 2 / (2 * sigma_y ** 2) - 
                         (c * (x - b_x) * (y - b_y) / (sigma_x * sigma_y)))) + d



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window1()
    window.show()
    sys.exit(app.exec_())