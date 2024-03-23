from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QLineEdit, QListWidget, QStyledItemDelegate, QStyle, QListWidgetItem, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal, QProcess
from PyQt6.QtGui import QGuiApplication, QColor, QPixmap, QFont
from datetime import datetime
import sys

############################################
###  COMPILE COMMAND ###
### python -m PyInstaller --onefile --windowed --icon icon.ico --add-data "cartelStudio.png:." --add-data "shader.png:." --add-data "icon.ico:." cartel.py


############ LOGS ##############
master_logs = "Cartel.logs"

##### SETTINGS #####
# TEXTS #
mainControl_title = "Cartel Studio"

# Colors #
mainControl_bgnd =          "background: black;"
mainControl_font_colors =   "color: white;"
mainControl_numpad_style =  "background-color: #3B3B3B; font-size:45px;" + mainControl_font_colors
mainControl_labels =        "font-size: 50px; color: white;"
mainControl_text_field =    "font-size: 50px; background: white; text-align: center;"
mainControl_button_style =  "color: white; font-size:35px; background:#666666;"
display_table =             "background-color: translucent; color: black; font-size: 50px; border: none;"
display_main =              "background: black;"
display_prepare_label =     "color: white; font-size: 50px;"
display_serving_label =     "color: white; font-size: 50px;"
display_texts_prep = "color:white; font-size:50px; background:red;"
display_texts_serv = "color:white; font-size:50px; background:#1ba614;"

# Font Sizes #
mainControl_numpad_height = 100
mainControl_numpad_width = 100
mainControl_grid_horiz_offset = 0       #Move numpad horizontally
mainControl_grid_verti_offset = 3       #Move numpad vertically
mainControl_field_height = 75
display_label_height = 75
display_item_width = 225
speed_sa_scroll = 2.3
max_num_of_items = 10

####################
class FileWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("Cartel Logs")
        self.setStyleSheet(mainControl_bgnd)

    def initUI(self):
        self.resize(1000,500)
        # Read the content of Cartel.txt
        try:
            with open('Cartel.logs', 'r') as file:
                content = file.read()
        except FileNotFoundError:
            content = 'File not found'

        # Create a text edit widget
        self.textEdit = QTextEdit(self)
        self.textEdit.setPlainText(content)
        self.textEdit.setReadOnly(True) 
        self.textEdit.setStyleSheet("color:white;")
        self.textEdit.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Set font size
        font = QFont()
        font.setPointSize(18)  # Set font size to 12 points
        self.textEdit.setFont(font)

        # Set the layout
        layout = QGridLayout()
        layout.addWidget(self.textEdit, 0, 0)
        self.setLayout(layout)

class ScrollableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.startPos = None
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setItemDelegate(NoFocusDelegate())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.startPos is not None:
                diff = int((event.pos().y() - self.startPos.y()) * speed_sa_scroll)
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff)
                self.startPos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.startPos = None

class NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Override painting focus rectangle to avoid drawing it
        option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)

class NumberItem(QWidget):
    remove_signal = pyqtSignal()
    change_stat = pyqtSignal()

    def __init__(self, number, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        self.label = QPushButton(str(number), self)
        self.label.setStyleSheet(mainControl_button_style)
        self.label.setFixedHeight(mainControl_field_height)
        self.serve_button = QPushButton("SERVE", self)
        self.serve_button.setStyleSheet(mainControl_button_style)
        self.serve_button.setFixedHeight(mainControl_field_height)
        layout.addWidget(QLabel(), 0, 0)
        layout.addWidget(self.label, 0, 1, 1, 3)
        layout.addWidget(self.serve_button, 0, 4, 1, 3)
        layout.addWidget(QLabel(), 0, 7)
        self.setLayout(layout)

        self.serve_button.clicked.connect(self.remove_me)
        self.label.clicked.connect(self.change_status)

    def remove_me(self):
        self.remove_signal.emit()
    
    def change_status(self):
        self.label.setEnabled(False)
        self.change_stat.emit()
        self.label.setStyleSheet(mainControl_button_style + "background-color: #1ba614;" )
    
    def enableButtons(self):
        self.label.setEnabled(True)
        self.serve_button.setEnabled(True)

class NoFocusTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

class Display(QWidget):
    def __init__(self):
        super().__init__()
        self.startDisplay()
        self.setWindowTitle("Cartel Display")
        self.setStyleSheet(display_main)
    
    def startDisplay(self):
        layout = QGridLayout()

        # Load the image
        pixmap = QPixmap("cartelStudio.png")

        # Create a QLabel and set the pixmap
        logo = QLabel()
        logo.setPixmap(pixmap)
        layout.addWidget(logo, 0, 0, 4, 2)

        prep_label = QLabel("PREPARING")
        prep_label.setStyleSheet(display_texts_prep)
        prep_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prep_label.setFixedHeight(display_label_height)
        layout.addWidget(prep_label, 0, 0)

        serv_label = QLabel("SERVING")
        serv_label.setStyleSheet(display_texts_serv)
        serv_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        serv_label.setFixedHeight(display_label_height)
        layout.addWidget(serv_label, 0, 1)
        self.prep_table = NoFocusTableWidget(0, 0)
        self.serv_table = NoFocusTableWidget(0, 0)

        tables = [self.prep_table, self.serv_table]
        for i, table in enumerate(tables):
            label = QLabel("")
            label.setStyleSheet("background-color: rgba(255, 255, 255, 0); border: 2px dashed white;")
            top_padding = QLabel("")
            top_padding.setStyleSheet("background-color: translucent;")
            top_padding.setFixedHeight(10)
            bot_padding = QLabel("")
            bot_padding.setStyleSheet("background-color: translucent;")
            bot_padding.setFixedHeight(10)
            table.horizontalHeader().setVisible(False)
            table.verticalHeader().setVisible(False)
            table.setStyleSheet(display_table)
            table.resizeRowsToContents()
            table.setFixedWidth(0)
            table.setCursor(Qt.CursorShape.ForbiddenCursor)
            table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            layout.addWidget(top_padding, 1, i, 1, 1)
            layout.addWidget(bot_padding, 3, i, 1, 1)
            layout.addWidget(label, 1, i, 3, 1)
            layout.addWidget(table, 2, i, 1, 1, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.setLayout(layout)
    
class mainController (QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(mainControl_title)
        # self.setStyleSheet(mainControl_bgnd)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(0, 0, 0))
        self.setPalette(p)
        self.startUI()
        self.display_screen = Display()
    
    def startUI(self):
        self.showFullScreen()
        layout = QGridLayout()
        self.setLayout(layout)
        self.prepare = []
        self.serve = []
        ########### LABELS ###############
        enterNumber = QLabel("QUEUE NUM: ")
        enterNumber.setStyleSheet(mainControl_labels)
        layout.addWidget(enterNumber, 0, 0, 1, 3) 

        ########### TEXT FIELD ###########
        self.input_field = QLineEdit()
        self.input_field.setFixedHeight(mainControl_field_height)
        self.input_field.setStyleSheet(mainControl_text_field)
        self.input_field.setMaximumWidth(300)
        layout.addWidget(self.input_field, 0, 3)

        ########### BUTTONS ##############
        self.add_button = QPushButton("ADD")
        self.add_button.clicked.connect(lambda:self.add_number(self.input_field.text()))
        
        self.display_button = QPushButton("DISPLAY")
        self.display_button.clicked.connect(lambda:self.show_display())

        self.logs = QPushButton("LOGS")
        self.logs.clicked.connect(lambda:self.open_logs())

        self.exit = QPushButton("X")
        self.exit.clicked.connect(lambda:self.shutdown_system())

        btns = [self.add_button, self.display_button, self.logs, self.exit]
        for btn in btns:
            btn.setStyleSheet(mainControl_button_style)
            btn.setFixedHeight(mainControl_field_height)

        layout.addWidget(self.add_button, 0, 4)
        layout.addWidget(self.display_button, 0, 5)
        layout.addWidget(self.logs, 0, 6)
        layout.addWidget(self.exit, 0, 7)

        ########### MAIN VIEW ############
        self.list_widget = ScrollableListWidget(self)
        self.list_widget.setStyleSheet("background : black;")
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)  # Disable selection mode
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        layout.addWidget(self.list_widget, 1, 3, 8, 5)
        
        ########### NUMPAD ###############
        button_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'DEL']

        for i, label in enumerate(button_labels):
            button = QPushButton(label, self)
            button.setFixedHeight(mainControl_numpad_height)
            button.setFixedWidth(mainControl_numpad_width)
            button.setStyleSheet(mainControl_numpad_style)
            button.clicked.connect(lambda _, l=label: self.append_number(l))
            if label == '0':
                layout.addWidget(button,mainControl_grid_verti_offset + 3, 
                                 mainControl_grid_horiz_offset + 1)
                continue
            elif label == 'DEL':
                layout.addWidget(button,mainControl_grid_verti_offset + 3, 
                                 mainControl_grid_horiz_offset + 2)
                continue
            else:
                layout.addWidget(button, mainControl_grid_verti_offset + (i // 3), 
                                 mainControl_grid_horiz_offset + (i % 3))

    def append_number(self, number):
        if number == 'DEL':
            current_text = self.input_field.text()
            if current_text:
                new_text = current_text[:-1]  # Remove the last character
                self.input_field.setText(new_text)
        else:
            current_text = self.input_field.text()
            self.input_field.setText(current_text + str(number))
    
    def add_number(self, number):
        if self.input_field.text() == "":
            return
        if not number.isdigit():
            self.input_field.clear()
            return
        if number in self.prepare:
            self.input_field.clear()
            return
        elif number in self.serve:
            self.input_field.clear()
            return
        self.input_field.clear()
        item = QListWidgetItem(self.list_widget)
        widget = NumberItem(int(number))
        item.setSizeHint(widget.sizeHint())
        self.list_widget.setItemWidget(item, widget)
        self.prepare.append(number)
        self.updateMasterLogs("ADDED_NEW_NUMBER", number)

        widget.remove_signal.connect(lambda: self.remove_item(item, number))
        widget.change_stat.connect(lambda: self.change_stat(item, number))

        self.add_to_display()

    def remove_item(self, item, number):
        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)
        if number in self.prepare:
            self.prepare.remove(number)
            self.updateMasterLogs("SERVED", number)
        if number in self.serve:
            self.serve.remove(number)
            self.updateMasterLogs("SERVED", number)
        self.refreshTable(self.prepare, self.display_screen.prep_table)
        self.refreshTable(self.serve, self.display_screen.serv_table)
        self.buildTable(self.prepare, self.display_screen.prep_table)
        self.buildTable(self.serve, self.display_screen.serv_table)
    
    def change_stat(self, item, number):
        self.prepare.remove(number)
        self.serve.append(number)
        self.updateMasterLogs("FINISHED_PREPARING", number)
        self.refreshTable(self.prepare, self.display_screen.prep_table)
        self.refreshTable(self.serve, self.display_screen.serv_table)
        self.buildTable(self.prepare, self.display_screen.prep_table)
        self.buildTable(self.serve, self.display_screen.serv_table)

    def show_display(self):
        screens = QGuiApplication.screens()

        if len(screens) > 1:  # Check if there is more than one screen
            second_screen = screens[1]  # Get the second screen
            screen_geometry = second_screen.geometry()

            self.second_window = self.display_screen
            self.second_window.setGeometry(screen_geometry)
            self.second_window.show()
            self.second_window.showFullScreen()
        
        else:
            self.display_screen.show()
    
    def add_to_display(self):
        self.refreshTable(self.prepare, self.display_screen.prep_table)
        self.buildTable(self.prepare, self.display_screen.prep_table)
    
    def buildTable(self, arr, table):
        for i, nums in enumerate(arr):
            mite = QTableWidgetItem(nums)
            mite.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            mite.setBackground(QColor("white"))
            # mite.setFixedWidth(display_item_width)
            print(f"i: {i}, len(arr): {len(arr)}")
            table.setItem(i % max_num_of_items, (i//max_num_of_items), mite)


    def refreshTable(self, arr, table):
        table.setColumnCount(((len(arr) - 1)//max_num_of_items) + 1)
        if len(arr) >= max_num_of_items:
            table.setRowCount(max_num_of_items)
        else:
            table.setRowCount(len(arr) % max_num_of_items)
        for x in range(0, len(arr) + 1):
            empty_stuff = QTableWidgetItem("")
            empty_stuff.setBackground(QColor(0, 0, 0, 0))
            table.setItem(x % max_num_of_items, x//max_num_of_items, empty_stuff)

        row_sizes = []
        for row in range(table.rowCount()):
            row_width = table.rowHeight(row)
            row_sizes.append(row_width)

        col_sizes = []
        for col in range(table.columnCount()):
            table.setColumnWidth(col, display_item_width)
            col_width = table.columnWidth(col)
            col_sizes.append(col_width)

        prep_width = sum(col_sizes)
        prep_height = sum(row_sizes)
        table.setFixedHeight(prep_height)
        table.setFixedWidth(prep_width)
    
    def open_logs(self):
        # Create a new window
        self.logs_Window = FileWindow()
        self.logs_Window.show()
    
    def updateMasterLogs(self, action, msg):
        cartel_logs = open(master_logs,"a")
        self.checkLines()
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cartel_logs.write(f"{current_time} | {action} => {msg}\n")
        cartel_logs.close()
        return
    
    def checkLines(self):
        cartel_logs = open(master_logs, "r")
        tmp = cartel_logs.readlines()
        if len(tmp) > 10000000:
            tmp.pop(0)
            cartel_logs.close()
            cartel_logs = open(master_logs, "w")
            for things in tmp:
                cartel_logs.write(things)
            cartel_logs.close()

    def closeEvent(self, event):
        if self.display_screen is not None:
            self.display_screen.close()
            self.display_screen = None
        if self.logs_Window is not None:
            self.logs_Window.close()
            self.logs_Window = None

    def shutdown_system(self):
        confirm_shutdown = QMessageBox.question(self, "Confirm Shutdown", "Are you sure you want to shut down the system?",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm_shutdown == QMessageBox.StandardButton.Yes:
            print("START SHUTDOWN")
            if sys.platform.startswith('win'):
                # Windows system shutdown
                QProcess.startDetached("shutdown", ["/s", "/t", "0"], "")

            elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
                # Linux or macOS system shutdown
                QProcess.startDetached("sudo", ["shutdown", "-h", "now"])

            else:
                # Unsupported platform
                QM

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cartel = mainController()
    cartel.show()
    sys.exit(app.exec())