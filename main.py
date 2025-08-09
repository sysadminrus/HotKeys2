from datetime import date
import threading
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLineEdit, QPushButton, QHBoxLayout, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
import keyboard
import os
import subprocess

TICKET_NUM_FILE = 'tnum.txt'
GIT_PATH = "C:/Git/"
"""Предполагается 7Zip"""
ZIP_EXE_PATH = "C:/Program Files/7-Zip/7z.exe"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Номер заявки')
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.central_layout = QHBoxLayout()
        self.ticketNumber = QLineEdit()
        last_ticket_number = load_last_num()
        self.ticketNumber.setText(last_ticket_number)
        self.ticketNumber.returnPressed.connect(self.enterClick)
        self.central_layout.addWidget(self.ticketNumber)
        self.buttonOk = QPushButton('Ok')
        self.buttonOk.setAutoDefault(True)
        self.central_layout.addWidget(self.buttonOk)
        self.widget = QWidget()
        self.widget.setLayout(self.central_layout)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("Bull.png"))
        self.setCentralWidget(self.widget)
        tray_menu = QMenu()
        show_action = QAction("Развернуть", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close_app)
        tray_menu.addAction(exit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_clicked)
        self.tray_icon.show()
        self.hide()
        
    def show_window(self):
        """Развернуть окно приложения"""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)
        self.activateWindow()
    
    def close_app(self):
        """Закрыть приложение"""
        self.tray_icon.hide()
        QApplication.quit()
        
    def tray_icon_clicked(self, reason):
        """Обработка кликов по иконке в трее"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # Обычный клик
            if self.isHidden() or self.isMinimized():
                self.showNormal()
            else:
                self.hide()
    
    def closeEvent(self, event):
        """Сохраним номер задачи"""
        save_last_num(self.ticketNumber.text())
        """Переопределяем закрытие окна - сворачиваем в трей"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Приложение свернуто",
            "Приложение продолжает работать в трее",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def enterClick(self):
        text_of_line = self.ticketNumber.text()
        save_last_num(text_of_line)
        self.hide()

    def buttonOk_pressed(self):
        text_of_line = self.ticketNumber.text()
        save_last_num(text_of_line)
        self.hide()

def comment_hotkey_pressed(window: MainWindow):
    keyboard.write(f'//++GIV {str(date.today())} ({load_last_num()})\n\n//--GIV {str(date.today())} ({load_last_num()})')

def open_notepad():
    if os.path.exists("C:/Program Files/Notepad++/notepad++.exe"):
        sErrCode = subprocess.run('C:/Program Files/Notepad++/notepad++.exe')
        if sErrCode.returncode != 0:
            print(sErrCode)
    
def update_git():
    #TODO Продумать далее
    """Распаковать ConfigFiles.zip в ConfFiles
    Перед этим удаляется старый ConfFiles
    """
    pass

def run_config():
    #TODO А может и не так, а включать ТЖ И ловить по нему ошибку?
    if os.path.exists("C:/Program Files/1cv8/common/1cestart.exe"):
        try:
            subprocess.Popen(args=['C:/Program Files/1cv8/common/1cestart.exe', 'DESIGNER', '/IBName' 'Библиотека стандартных подсистем (демо)', '/NАдминистратор', 
                    '/LoadConfigFromFiles' 'C:/Git/ConfigFiles/', '-Extension' 'УниверсальныеИнструменты', 
                    '-updateConfigDumpInfo', '/Out 1.txt']).communicate(timeout=120)
        except subprocess.TimeoutExpired:
            print(f'Закончилось время')
        except:
            print('Другая ошибка запуска')
        #sErrCode = subprocess.Popen('C:/Program Files/1cv8/common/1cestart.exe DESIGNER /IBName \"Библиотека стандартных подсистем (демо)\" /NАдминистратор /LoadConfigFromFiles C:\Git\ConfigFiles\ -Extension \"УниверсальныеИнструменты\" -updateConfigDumpInfo -SessionTerminate force -v2')
        
        

def wait_keys(window: MainWindow):
    keyboard.add_hotkey('ctrl+alt+k', comment_hotkey_pressed,args=(window, ))
    keyboard.add_hotkey('ctrl+alt+o', open_notepad)
    keyboard.add_hotkey('ctrl+alt+g', update_git)
    keyboard.add_hotkey('ctrl+alt+c', run_config)
    keyboard.wait()

def load_last_num():
    try:
        with open(TICKET_NUM_FILE, "r") as f:
            return f.readline().replace('\r\n', '').strip()
    except:
        return ''
    
def save_last_num(ticketNumber):
        with open(TICKET_NUM_FILE, "w+") as f:
            f.write(ticketNumber + '\r\n')
    
if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon("Bull.png"))
    window = MainWindow()
    threading.Thread(target=wait_keys, args=(window,)).start()
    app.exec()


