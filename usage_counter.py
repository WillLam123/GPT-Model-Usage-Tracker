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


        self.setGeometry(1910, 100, 200, 400)


        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.layout)


        close_layout = QVBoxLayout()
        self.close_btn = QPushButton('X')
        self.close_btn.setFixedWidth(50)
        self.close_btn.clicked.connect(self.hideWindow)
        close_layout.addStretch()
        close_layout.addWidget(self.close_btn)
        self.layout.addLayout(close_layout)


        self.models = {
            '4': {'label': QLabel('4: 0'), 'timestamps': [], 'refresh_period': 10800},
            '4o': {'label': QLabel('4o: 0'), 'timestamps': [], 'refresh_period': 10800},
            '01p': {'label': QLabel('01p: 0'), 'timestamps': [], 'refresh_period': 604800},
            '01m': {'label': QLabel('01m: 0'), 'timestamps': [], 'refresh_period': 86400}
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



        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.checkExpiredTimestamps)
        self.check_timer.start(60000)  # 60秒


        self.animation = QPropertyAnimation(self, b"geometry")
        screen_geometry = QApplication.desktop().screenGeometry()
        self.screen_width = screen_geometry.width()
        self.enterEvent = self.enterWidget
        self.leaveEvent = self.leaveWidget

    def initTrayIcon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("path_to_icon.png"))
        self.tray_icon.setToolTip("Model Usage Tracker")


        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.showWindow)
        tray_menu.addAction(show_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

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

        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Running",
            "Minimize to system tray",
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

            self.models[model]['timestamps'].pop(0)
            self.models[model]['label'].setText(f"{model}: {len(self.models[model]['timestamps'])}")
            self.saveData()
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
                QMessageBox.warning(self, "Loading Error", f"Unable to load JSON：{e}")

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
            QMessageBox.warning(self, "Saving Error", f"Unable to save JSON：{e}")

    def checkExpiredTimestamps(self):
        current_time = time.time()
        updated = False
        for model, model_data in self.models.items():
            refresh_period = model_data['refresh_period']
            timestamps = model_data['timestamps']
            expired = [ts for ts in timestamps if current_time - ts >= refresh_period]
            if expired:
                for ts in expired:
                    timestamps.remove(ts)
                    updated = True

            self.models[model]['label'].setText(f"{model}: {len(timestamps)}")
        if updated:
            self.saveData()

    def updateCountsBasedOnTime(self):

        self.checkExpiredTimestamps()

    def updateLabels(self):
        for model, model_data in self.models.items():
            self.models[model]['label'].setText(f"{model}: {len(model_data['timestamps'])}")

if __name__ == '__main__':
    app = QApplication(sys.argv)


    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Systray", "Not available")
        sys.exit(1)

    QApplication.setQuitOnLastWindowClosed(False)

    ex = CountApp()
    ex.show()
    sys.exit(app.exec_())
