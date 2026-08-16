import keyboard, os, subprocess, shutil, threading, time
from datetime import date
from global_hotkeys import *
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QLineEdit, QPushButton, QSystemTrayIcon, QMenu, QCheckBox, QGridLayout, QTextEdit, QComboBox, QTreeView, QTreeWidgetItem, QAbstractItemView
from PyQt6.QtGui import QIcon, QAction
from oneCtreeparse import DirectoryTreeAdapter

#TODO в файл настроек
TICKET_NUM_FILE = 'tnum.txt'
GIT_PATH = "C:/Git/"
WORK_DIR = "Z:/УК/ИТ/КИС/Гладких/Tasks"
WORK_DONE_DIR = "Z:/УК/ИТ/КИС/Гладких/DoneTasks"
ADDED_COMPONENTS_FILE = "components.txt"
OBSIDIAN_PATH = "C:/Users/user/Documents/Obsidian Vault/УВМ-Сталь/УВМ-Сталь/УВМ-Сталь/АрхивныеЗадачи"
is_alive = True
# """Предполагается 7Zip"""
# ZIP_EXE_PATH = "C:/Program Files/7-Zip/7z.exe"

class AddedComponents(QTextEdit):
    def __init_subclass__(cls):
        return super().__init_subclass__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasText():
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):
        if e.mimeData().hasText():
            if not self._insert_at_drop_pos(e):
                self._append_to_changed_metadata(e.mimeData().text())
            e.acceptProposedAction()
        else:
            e.ignore()

    def _insert_at_drop_pos(self, e) -> bool:
        pos = e.position().toPoint()
        if not self.viewport().rect().contains(pos):
            return False
        cursor = self.cursorForPosition(pos)
        line = cursor.blockNumber()
        lines = self.toPlainText().split('\n')
        if not (0 <= line < len(lines)):
            return False
        path = '#' + e.mimeData().text().lstrip()
        lines.insert(line + 1, path)
        self.setText('\n'.join(lines))
        return True

    def _append_to_changed_metadata(self, path: str):
        #GIV немного маркдауна чтобы потом искать по метаданным
        path = "#" + path.lstrip()
        text = self.toPlainText().rstrip()
        text = (text + '\n') if text else text
        self.setText(text + path)

    def focusOutEvent(self, e):
        with open(ADDED_COMPONENTS_FILE, "w+") as f:
            f.write(self.toPlainText() + '\r\n')

class MainWindow(QMainWindow):
    show_window_signal = pyqtSignal()

    def __init__(self):
        super().__init__()        
        self.setWindowTitle('Номер заявки')
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.central_layout = QGridLayout()
        self.ticketNumber = QLineEdit()
        last_ticket_number = load_last_num()
        '''Дерево конфигурации'''
        self.configTree = QTreeView()
        self.configTree.setDragEnabled(True)
        self.configTree.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.configTree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.configTree.setExpandsOnDoubleClick(True)
        self.central_layout.addWidget(self.configTree,2,1)
        '''Текст для заметки с новыми компонентами'''
        self.added_components = AddedComponents()
        self.added_components.setText(load_added_components())
        self.central_layout.addWidget(self.added_components,2,0)
        '''Номер тикета'''
        self.ticketNumber.setText(last_ticket_number)
        self.current_ticket_number = last_ticket_number
        self.ticketNumber.returnPressed.connect(self.enterClick)
        self.ticketNumber.editingFinished.connect(self.on_ticket_number_edited)
        self.central_layout.addWidget(self.ticketNumber,3,0)
        '''Список выбора конфигураций'''
        self.listOfConfigs = QComboBox()
        self.listOfConfigs.addItem("TMS")
        self.listOfConfigs.addItem("ERP")
        self.listOfConfigs.currentIndexChanged.connect(self.configChanged)
        self.central_layout.addWidget(self.listOfConfigs,3,1)

        '''Кнопка Ок'''
        self.buttonOk = QPushButton('Ok')
        self.buttonOk.setAutoDefault(True)
        self.buttonOk.clicked.connect(self.enterClick)
        '''Создать при нажатии на OK рабочую директорию для задачи'''
        self.checkCreateInWork = QCheckBox('Создать в работе')
        self.checkCreateInWork.stateChanged.connect(self.checkbox_state_changed)
        self.central_layout.addWidget(self.checkCreateInWork,4,0)
        '''Переместить файлы по задаче в выполненные'''
        self.checkCopyInDone = QCheckBox('Переместить в выполненные')
        self.checkCopyInDone.stateChanged.connect(self.checkbox_state_changed)
        self.central_layout.addWidget(self.checkCopyInDone,5,0)        
        self.central_layout.addWidget(self.buttonOk,6,0)
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
        self.show_window_signal.connect(self.toggle_window)
        self.tray_icon.show()
        #self.hide() 
        # Не понятное поведение, но если не показывать при старте, то не вызывается хоткеями.
        self.show()
        self.configChanged()

    def checkbox_state_changed(self):
        if self.checkCreateInWork.isChecked():
            self.checkCopyInDone.setEnabled(False)
        else:
            self.checkCopyInDone.setEnabled(True)
        if self.checkCopyInDone.isChecked():
            self.checkCreateInWork.setEnabled(False)
        else:
            self.checkCreateInWork.setEnabled(True)
        
    def show_window(self):
        """Развернуть окно приложения"""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)
        self.activateWindow()
    
    def close_app(self):
        """Закрыть приложение"""
        self.tray_icon.hide()
        stop_global_hotkeys()
        QApplication.quit()
        
    def toggle_window(self):
        if self.isHidden() or self.isMinimized():
            self.show_window()
        else:
            self.hide()

    def tray_icon_clicked(self, reason):
        """Обработка кликов по иконке в трее"""
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            self.toggle_window()
    
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
        save_last_num(self.ticketNumber.text())
        if self.checkCreateInWork.isChecked():
            try:
                if not os.path.exists(WORK_DIR):
                    os.makedirs(WORK_DIR)
                if not os.path.exists(f'{WORK_DIR}/{self.ticketNumber.text()}'):
                    os.makedirs(f'{WORK_DIR}/{self.ticketNumber.text()}')
                else:
                    print('Директория уже существует')
            except OSError as errorDescription: 
                print("OS Error" + str(errorDescription))
        if self.checkCopyInDone.isChecked() and os.path.exists(f'{WORK_DIR}/{self.ticketNumber.text()}'):
            if not os.path.exists(WORK_DONE_DIR):
                os.makedirs(WORK_DONE_DIR)    
            shutil.move(f'{WORK_DIR}/{self.ticketNumber.text()}', WORK_DONE_DIR)
        self.hide()

    def configChanged(self):
        selected_config = self.listOfConfigs.currentText()
        adapterModel = DirectoryTreeAdapter(os.path.join('1CMetadata', selected_config))
        self.configTree.setModel(adapterModel)

    def on_ticket_number_edited(self):
        new_num = self.ticketNumber.text().strip()
        if not new_num or new_num == self.current_ticket_number:
            return
        self._archive_current_note()
        self._load_template(new_num)
        self.current_ticket_number = new_num
        save_last_num(new_num)

    def _archive_current_note(self):
        old_num = self.current_ticket_number
        if not old_num:
            return
        os.makedirs(OBSIDIAN_PATH, exist_ok=True)
        note = self.added_components.toPlainText().strip()
        header = f'#НомерЗадачи : {old_num}'
        content = note if header in note else header + '\n\n' + note
        with open(os.path.join(OBSIDIAN_PATH, f'{old_num}.md'), 'w', encoding='utf-8') as f:
            f.write(content)

    def _find_existing_note_file(self, new_num):
        if not os.path.isdir(OBSIDIAN_PATH):
            return None
        matches = []
        for name in os.listdir(OBSIDIAN_PATH):
            if not name.lower().endswith('.md'):
                continue
            base = name[:-3]
            if base.casefold().startswith(new_num.casefold()):
                matches.append(name)
        if not matches:
            return None
        return os.path.join(OBSIDIAN_PATH, sorted(matches)[0])

    def _load_template(self, new_num):
        existing = self._find_existing_note_file(new_num)
        if existing is not None:
            with open(existing, encoding='utf-8') as f:
                self.added_components.setText(f.read())
            return
        with open('components.md', encoding='utf-8') as f:
            template = f.read()
        self.added_components.setText(template.replace('{ticketNumber}', new_num))

def comment_hotkey_pressed() -> None:
    keyboard.write(f'//++GIV {str(date.today().strftime("%d%m%Y"))} ({load_last_num()})\r\n//--GIV {str(date.today().strftime("%d%m%Y"))} ({load_last_num()})')

def open_notepad() -> None:
    if os.path.exists("C:/Program Files/Notepad++/notepad++.exe"):
        sErrCode = subprocess.run('C:/Program Files/Notepad++/notepad++.exe')
        if sErrCode.returncode != 0:
            print(sErrCode)
    
def open_window() -> None:
    window.show_window_signal.emit()
        
def run_global_hotkeys():
    bindings = [
        ["control + alt + k", None, comment_hotkey_pressed, True],
        ["control + alt + o", None, open_window, True],
        ["control + alt + t", None, paste_path_to_task, True],
    ]
    register_hotkeys(bindings)
    start_checking_hotkeys()
    while is_alive:
        time.sleep(0.1)

def stop_global_hotkeys():
    global is_alive
    is_alive = False
    stop_checking_hotkeys()

def load_last_num():
    try:
        with open(TICKET_NUM_FILE, "r") as f:
            return f.readline().replace('\r\n', '').strip()
    except OSError:
        return 'Ошибка чтения файла тикета'
    
def save_last_num(ticketNumber):
        with open(TICKET_NUM_FILE, "w+") as f:
            f.write(ticketNumber + '\r\n')


def paste_path_to_task():
    keyboard.write(f'{WORK_DIR}/{load_last_num()}')

def load_added_components():
    try:
        with open(ADDED_COMPONENTS_FILE, "r") as f:
            return "".join(f.readlines())
    except OSError:
        return 'Ошибка чтения файла тикета'

app = QApplication([])
app.setWindowIcon(QIcon("Bull.png"))
window = MainWindow()

if __name__ == "__main__":
    threading.Thread(target=run_global_hotkeys, daemon=True).start()
    app.exec()
    