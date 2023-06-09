import sys
import json
import data_management as dm

test_file = "E:\\FGC_Projects\\ScheduleJSONGen\\texasshowdown2023.json"

#data = dm.parseJSON(dm.loadJSON(test_file))
data = dm.load_empty()
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QMenu, QScrollArea, QTimeEdit

import widgets
app = QApplication(sys.argv)
mainWindow = widgets.mainWindow(data)
app.exec()




