import sys
import json
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QDockWidget,
    QSystemTrayIcon, QMenu, QAction, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QIcon

DATA_FILE = 'count_data.json'

class CountApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initTrayIcon()
        self.loadData()
        self.updateCountsBasedOnTime()

    def initUI(self):
        self.setWindowTitle('Model Usage Tracker')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)

        # 设置窗口大小和初始位置
        self.setGeometry(1910, 100, 200, 400)  # 根据屏幕分辨率调整

        # 布局
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.layout)

        # 添加关闭按钮
        close_layout = QVBoxLayout()
        self.close_btn = QPushButton('X')
        self.close_btn.setFixedWidth(50)
        self.close_btn.clicked.connect(self.hideWindow)
        close_layout.addStretch()
        close_layout.addWidget(self.close_btn)
        self.layout.addLayout(close_layout)

        # 模型数据: {模型名称: { 'label': QLabel, 'timestamps': list, 'refresh_period': int }}
        self.models = {
            '4': {'label': QLabel('4: 0'), 'timestamps': [], 'refresh_period': 10800},    # 3小时
            '4o': {'label': QLabel('4o: 0'), 'timestamps': [], 'refresh_period': 10800},
            '01p': {'label': QLabel('01p: 0'), 'timestamps': [], 'refresh_period': 604800},  # 7天
            '01m': {'label': QLabel('01m: 0'), 'timestamps': [], 'refresh_period': 86400}    # 1天
        }

        for model, data in self.models.items():
            model_layout = QVBoxLayout()
            label = data['label']

            btn_inc = QPushButton('+')
            btn_dec = QPushButton('-')
            btn_inc.setFixedWidth(50)
            btn_dec.setFixedWidth(50)
            btn_inc.clicked.connect(lambda _, m=model: self.incrementCount(m))
            btn_dec.clicked.connect(lambda _, m=model: self.decrementCount(m))

            btn_layout = QVBoxLayout()
            btn_layout.addWidget(btn_inc)
            btn_layout.addWidget(btn_dec)

            model_layout.addWidget(label)
            model_layout.addLayout(btn_layout)
            self.layout.addLayout(model_layout)


        # 全局定时器，每分钟检查一次
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.checkExpiredTimestamps)
        self.check_timer.start(60000)  # 60秒

        # 动画效果
        self.animation = QPropertyAnimation(self, b"geometry")
        screen_geometry = QApplication.desktop().screenGeometry()
        self.screen_width = screen_geometry.width()
        self.enterEvent = self.enterWidget
        self.leaveEvent = self.leaveWidget

    def initTrayIcon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("path_to_icon.png"))  # 替换为您的图标路径
        self.tray_icon.setToolTip("Model Usage Tracker")

        # 创建右键菜单
        tray_menu = QMenu()

        show_action = QAction("显示", self)
        show_action.triggered.connect(self.showWindow)
        tray_menu.addAction(show_action)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # 双击托盘图标显示窗口
        self.tray_icon.activated.connect(self.onTrayIconActivated)

    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showWindow()

    def showWindow(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def hideWindow(self):
        self.hide()

    def closeEvent(self, event):
        # 最小化到托盘而不是退出
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "运行中",
            "程序已最小化到系统托盘。",
            QSystemTrayIcon.Information,
            2000
        )

    def incrementCount(self, model):
        current_time = time.time()
        self.models[model]['timestamps'].append(current_time)
        self.models[model]['label'].setText(f"{model}: {len(self.models[model]['timestamps'])}")
        self.saveData()

    def decrementCount(self, model):
        if self.models[model]['timestamps']:
            # 移除最早的时间戳
            self.models[model]['timestamps'].pop(0)
            self.models[model]['label'].setText(f"{model}: {len(self.models[model]['timestamps'])}")
            self.saveData()

    def autoDecrementCount(self, model):
        # 这个方法不再需要，因为我们使用全局定时器
        pass

    def enterWidget(self, event):
        new_rect = QRect(self.screen_width - 70, 100, 70, 400)
        self.animateDock(new_rect)

    def leaveWidget(self, event):
        new_rect = QRect(self.screen_width - 5, 100, 70, 400)
        self.animateDock(new_rect)

    def animateDock(self, new_rect):
        self.animation.stop()
        self.animation.setDuration(300)
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(new_rect)
        self.animation.start()

    def loadData(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                for model, model_data in data.items():
                    if model in self.models:
                        self.models[model]['timestamps'] = model_data.get('timestamps', [])
            except Exception as e:
                QMessageBox.warning(self, "加载数据失败", f"无法加载数据文件：{e}")

    def saveData(self):
        data = {}
        for model, model_data in self.models.items():
            data[model] = {
                'timestamps': model_data['timestamps']
            }
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            QMessageBox.warning(self, "保存数据失败", f"无法保存数据文件：{e}")

    def checkExpiredTimestamps(self):
        current_time = time.time()
        updated = False
        for model, model_data in self.models.items():
            refresh_period = model_data['refresh_period']
            timestamps = model_data['timestamps']
            # 找出所有过期的时间戳
            expired = [ts for ts in timestamps if current_time - ts >= refresh_period]
            if expired:
                for ts in expired:
                    timestamps.remove(ts)
                    updated = True
            # 更新标签
            self.models[model]['label'].setText(f"{model}: {len(timestamps)}")
        if updated:
            self.saveData()

    def updateCountsBasedOnTime(self):
        # 立即检查一次
        self.checkExpiredTimestamps()

    def updateLabels(self):
        for model, model_data in self.models.items():
            self.models[model]['label'].setText(f"{model}: {len(model_data['timestamps'])}")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 检查系统是否支持系统托盘
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Systray", "系统托盘不可用！")
        sys.exit(1)

    QApplication.setQuitOnLastWindowClosed(False)  # 确保应用在托盘时继续运行

    ex = CountApp()
    ex.show()
    sys.exit(app.exec_())
