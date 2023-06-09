import typing
from PyQt6 import QtCore
from PyQt6.QtWidgets import QFileDialog, QTabWidget, QCheckBox, QTimeEdit, QDateEdit, QSizePolicy, QScrollArea, QApplication, QColorDialog, QPushButton, QLabel, QMainWindow, QMenu, QLineEdit, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QFormLayout, QComboBox, QCompleter, QDialog
from PyQt6.QtCore import Qt, QSize, QTime, QDate, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QAction
import zoneinfo
import shortuuid
import sys
import data_management

class TextRow(QWidget):
    changedText = pyqtSignal(str)
    def __init__(self, name, key="", placeholder=None):
        super().__init__()
        self.name = name
        self.key = key
        container = QWidget()
        layout = QHBoxLayout()
        self.label = QLabel(name)
        self.line = QLineEdit(self)
        layout.addWidget(self.label)
        layout.addWidget(self.line)
        self.setLayout(layout)
        self.line.setPlaceholderText(name)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(350)

        

        self.line.textEdited.connect(self.changed)
    def setValue(self, value):
        self.line.setText(value)
    def enable(self):
        self.line.setEnabled(True)
    def disable(self):
        self.line.setEnabled(False)
    def value(self):
        return self.line.text()

    def changed(self):
        self.changedText.emit(self.line.text())

class TimeRow(QWidget):
    changedTime = pyqtSignal(str)
    def __init__(self, label):
        super().__init__()
        self.Label = QLabel(label)
        self.TimePick = QTimeEdit()
        self.TimePick.setDisplayFormat("hh:mm:ss")
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.Label)
        self.layout.addWidget(self.TimePick)
        self.setLayout(self.layout)

        self.TimePick.timeChanged.connect(self.changeTime)

    def setTime(self, time):
        qtime = QTime()
        qtime = qtime.fromString(time, "hh:mm:ss")
        self.TimePick.setTime(qtime)

    def value(self):
        return self.TimePick.time().toString("hh:mm:ss")
    
    def changeTime(self, qtime:QTime):
        time = qtime.toString("hh:mm:ss")
        self.changedTime.emit(qtime.toString("hh:mm:ss"))


    
class DateRow(QWidget):
    changedDate = pyqtSignal(str)
    def __init__(self, name):
        super().__init__()
        self.label = QLabel(name)
        self.date = QDateEdit()
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.date)
        self.setLayout(self.layout)
        self.date.dateChanged.connect(self.changeDate)

    def setDate(self, date):
        self.date.setDate(self.convert(date))
    
    def value(self):
        return self.date.date().toString("MM-dd-yyyy")
    
    def convert(self,date):
        year = date[-4:]
        day = date[3:5]
        mon = date[:2]
        return QDate(int(year), int(mon), int(day))
    
    def enable(self):
        self.date.setEnabled(True)
    def disable(self):
        self.date.setEnabled(False)
        
    def changeDate(self, date):
        self.changedDate.emit(date.toString("MM-dd-yyyy"))

class SearchableDropdown(QWidget):
    changedText = pyqtSignal(str)
    def __init__(self, name, key, items):
        super().__init__()
        self.name = name
        self.key = key
        container = QWidget()
        layout = QHBoxLayout()
        self.label = QLabel(name)
        self.completer = QCompleter(items)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.c_box = QComboBox()
        self.c_box.setEditable(True)
        self.c_box.addItems(items)
        self.c_box.setCompleter(self.completer)
        layout.addWidget(self.label)
        layout.addWidget(self.c_box)
        self.setLayout(layout)
        self.setMaximumSize(1000,1000)
        self.c_box.currentTextChanged.connect(self.changeText)

    def setValue(self, value):
        print(value)
        index = self.c_box.findText(value)
        self.c_box.setCurrentIndex(index)

    def value(self):
        return self.c_box.currentText()
    
    def changeText(self, text):
        self.changedText.emit(text)

    def enable(self):
        self.c_box.setEnabled(True)
    def disable(self):
        self.c_box.setEnabled(False)

class TimeZone(QFrame):
    def __init__(self, zone_list, zone_id, data):
        super().__init__()
        self.id = zone_id
        self.data = data
        self.ZoneName = TextRow("Zone Common Name", "")
        self.ZoneSelect = SearchableDropdown("Time Zone", "", zone_list)
        self.FormatSelect = SearchableDropdown("Zone Format", "", ['12h', '24h'])

        layout = QVBoxLayout()
        layout.addWidget(self.ZoneName)
        layout.addWidget(self.ZoneSelect)
        layout.addWidget(self.FormatSelect)

        self.removeButton = QPushButton("Remove")

        layout.addWidget(self.removeButton)



        if data['zones'][zone_id]['text']:
            self.ZoneName.setValue(data['zones'][zone_id]['text'])
        if data['zones'][zone_id]['identifier']:
            self.ZoneSelect.setValue(data['zones'][zone_id]['identifier'])
        if data['zones'][zone_id]['format']:
            self.FormatSelect.setValue(data['zones'][zone_id]['format'])
        
        self.ZoneName.changedText.connect(self.updateZoneName)
        self.ZoneSelect.changedText.connect(self.updateZoneID)
        self.FormatSelect.changedText.connect(self.updateZoneFormat)

        self.removeButton.clicked.connect(self.removeZone)

        self.setLayout(layout)
        self.setLineWidth(1)
        self.setFrameStyle(QFrame.Shape.Panel)

    def removeZone(self):
        self.data['zones'].pop(self.id)
        self.setVisible(False)
    
    def updateZoneName(self, name):
        self.data['zones'][self.id]['text'] = name
    
    def updateZoneID(self, identifier):
        self.data['zones'][self.id]['identifier'] = identifier

    def updateZoneFormat(self, format):
        self.data['zones'][self.id]['format'] = format

class EventTab(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.tzs = zoneinfo.available_timezones()
        self.EventName =TextRow("Event Name", "event_name")
        self.EventDate = TextRow("Event Date", "event_date")
        self.EventLoc = TextRow("Event Location", "event_loc")
        self.EventTwitter = TextRow("Event Twitter", "event_twitter")
        self.EventHashtag = TextRow("Event Hashtag", "event_hashtag")
        self.EventTimezone = SearchableDropdown("Event Timezone", "event_timezone", self.tzs)
        self.EventTZText = TextRow("Event Timezone Text", "event_tz_text")
        self.EventTimeFormat = SearchableDropdown("Event Time Format", "event_time_format", ['12h', '24h'])
        self.EventTitleTop = TextRow("Event Top Title Line", "event_title1")
        self.EventTitleBottom = TextRow("Event Bottom Title Line", "event_title2")
        self.EventAuthor = TextRow("Schedule Author", "event_author")
        self.EventSchedule = TextRow("Event Schedule", "event_scheudle")

        self.layout = QFormLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(5,5,5,5)
        
        event_meta = data['event']
        self.EventName.setValue(event_meta['name'])
        self.EventDate.setValue(event_meta['dates'])
        self.EventLoc.setValue(event_meta['location'])
        self.EventTwitter.setValue(event_meta['twitter'])
        self.EventHashtag.setValue(event_meta['hashtag'])
        self.EventTimezone.setValue(event_meta['time zone'])
        self.EventTZText.setValue(event_meta['zone_text'])
        self.EventTimeFormat.setValue(event_meta['time format'])
        self.EventTitleTop.setValue(event_meta['title_line1'])
        self.EventTitleBottom.setValue(event_meta['title_line2'])
        self.EventAuthor.setValue(event_meta['scheduler'])
        self.EventSchedule.setValue(event_meta['official_schedule'])

        self.EventName.changedText.connect(self.updateEventName)
        self.EventDate.changedText.connect(self.updateEventDate)
        self.EventLoc.changedText.connect(self.updateEventLoc)
        self.EventTwitter.changedText.connect(self.updateEventTwitter)
        self.EventHashtag.changedText.connect(self.updateEventHashtag)
        self.EventTimezone.changedText.connect(self.updateEventTimezone)
        self.EventTZText.changedText.connect(self.updateEventTZText)
        self.EventTimeFormat.changedText.connect(self.updateEventTimeFormat)
        self.EventTitleTop.changedText.connect(self.updateEventTopTitle)
        self.EventTitleBottom.changedText.connect(self.updateEventBottomTitle)
        self.EventAuthor.changedText.connect(self.updateEventAuthor)
        self.EventSchedule.changedText.connect(self.updateEventSchedule)

        self.layout.addWidget(self.EventName)
        self.layout.addWidget(self.EventDate)
        self.layout.addWidget(self.EventLoc)
        self.layout.addWidget(self.EventTwitter)
        self.layout.addWidget(self.EventHashtag)
        self.layout.addWidget(self.EventTimezone)
        self.layout.addWidget(self.EventTZText)
        self.layout.addWidget(self.EventTimeFormat)
        self.layout.addWidget(self.EventTitleTop)
        self.layout.addWidget(self.EventTitleBottom)
        self.layout.addWidget(self.EventAuthor)
        self.layout.addWidget(self.EventSchedule)

        


        self.zoneWidgets = []
        for zone in self.data['zones']:
            zoneWidget = TimeZone(self.tzs, zone, data)
            self.zoneWidgets.append(zoneWidget)
            self.layout.addWidget(zoneWidget)
        
        self.AddZone = QPushButton("Add Zone")
        self.AddZone.clicked.connect(self.addZone)
        self.layout.addWidget(self.AddZone)

        self.setLayout(self.layout)

    def addZone(self):
        new_id = shortuuid.uuid()
        zone_obj = {
            "text" : None,
            "identifier" : None,
            "format" : None
        }
        self.data['zones'][new_id] = zone_obj

        newWidget = TimeZone(self.tzs, new_id, self.data)
        self.layout.addWidget(newWidget)

    def updateEventName(self, name):
        self.data['event']['name'] = name
    
    def updateEventDate(self, dates):
        self.data['event']['dates'] = dates

    def updateEventLoc(self, loc):
        self.data['event']['location'] = loc

    def updateEventTwitter(self, twit):
        self.data['event']['twitter'] = twit
    
    def updateEventHashtag(self, tag):
        self.data['event']['hashtag'] = tag
    
    def updateEventTimezone(self, tz):
        self.data['event']['time zone'] = tz

    def updateEventTZText(self, text):
        self.data['event']['zone_text'] = text

    def updateEventTimeFormat(self, format):
        self.data['event']['time format'] = format

    def updateEventTopTitle(self, title):
        self.data['event']['title_line1'] = title

    def updateEventBottomTitle(self, title):
        self.data['event']['title_line2'] = title

    def updateEventAuthor(self, author):
        self.data['event']['scheduler'] = author
    
    def updateEventSchedule(self, sched):
        self.data['event']['official_schedule'] = sched

class GameInfo(QWidget):
    logoUpdated = pyqtSignal(str)
    def __init__(self, data, game_id):
        super().__init__()
        self.data = data
        self.game_id = game_id
        self.GameName = TextRow("Game Name", "")
        self.LogoPath = TextRow("Logo Path", "")
        self.RemoveButton = QPushButton("Remove Game")
        self.Color = GameColor(data, game_id)

        layout = QFormLayout()
        layout.addWidget(self.GameName)
        layout.addWidget(self.LogoPath)
        layout.addWidget(self.Color)
        layout.addWidget(self.RemoveButton)

        self.setLayout(layout)

        if data['games'][game_id] is not None:
            self.GameName.setValue(data['games'][game_id]['name'])
            self.LogoPath.setValue(data['games'][game_id]['logo'])
        self.setMinimumWidth(400)

        self.GameName.changedText.connect(self.updateGameName)
        self.LogoPath.changedText.connect(self.updateGameLogo)

        self.RemoveButton.clicked.connect(self.removeGame)

    def updateGameName(self, name):
        old_name = self.data['games'][self.game_id]['name']
        self.data['game_map'].pop(old_name)
        self.data['game_map'][name] = self.game_id
        self.data['games'][self.game_id]['name'] = name

    def updateGameLogo(self, path):
        self.data['games'][self.game_id]['logo'] = path
        self.logoUpdated.emit(path)
        
    def removeGame(self):
        for block in self.data['blocks']:
            if self.data['blocks'][block]['game'] == self.game_id:
                return
            
        name = self.data['games'][self.game_id]['name']
        self.data['game_map'].pop(name)

        self.data['games'].pop(self.game_id)

        self.parent().setVisible(False)


class GameColor(QWidget):
    def __init__(self, data, game_id):
        super().__init__()
        self.data = data
        self.game_id = game_id
        color = data['games'][game_id]['color']
        box = QPixmap(30, 30)
        box.fill(QColor(color))
        self.ColorBox = QLabel()
        self.ColorBox.setPixmap(box)
        self.ColorName = QLabel(color)
        self.ChangeButton = QPushButton("Change Color")
        layout = QHBoxLayout()
        layout.addWidget(self.ColorName)
        layout.addWidget(self.ColorBox)
        layout.addWidget(self.ChangeButton)
        self.setLayout(layout)
        self.setMinimumSize(400, 60)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.ChangeButton.clicked.connect(self.chooseColor)

    def chooseColor(self):
        self.ColorDialog = QColorDialog()
        color =self.ColorDialog.getColor()
        box = QPixmap(30,30)
        box.fill(color)
        self.ColorBox.setPixmap(box)
        self.ColorName.setText(color.name())

        self.data['games'][self.game_id]['color'] = color.name()


class AddColor(QWidget):
    def __init__(self):
        super().__init__()
        
        self.ColorDialog = QColorDialog()
        self.OpenButton = QPushButton("Choose Color")
        layout = QHBoxLayout()
        layout.addWidget(self.OpenButton)
        self.OpenButton.clicked.connect(self.chooseColor)
        self.setLayout(layout)
        self.setMinimumSize(400, 60)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


    def chooseColor(self):
        color =self.ColorDialog.getColor()
        self.parent().insertColor(color.name())



class GameColors(QWidget):
    def __init__(self, colors):
        super().__init__()
        self.colorWidgets = []
        for color in colors:
            self.colorWidgets.append(GameColor(color))
        self.layout= QVBoxLayout()
        self.layout.setSpacing(1)
        for widget in self.colorWidgets:
            self.layout.addWidget(widget)

        self.layout.addWidget(AddColor())
        self.setLayout(self.layout)
        self.setMinimumSize(400, 100)
        self.layout.setContentsMargins(5, 10, 5, 10)
        self.layout.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        
    def insertColor(self, color):
        self.colorWidgets.append(GameColor(color))
        self.layout.insertWidget(self.layout.count()-1, self.colorWidgets[-1])
        size = self.minimumSize()
        self.setMinimumSize(size.width(), size.height() + 61)

        

class GameBox(QFrame):
    def __init__(self, data, game_id):
        super().__init__()
        self.data = data
        self.game_id = game_id
        self.Logo = None
        if game_id is not None:
            self.Logo = QImage(data['games'][game_id]['logo'])
        else: self.Logo = QImage("E:\\Acekingoffsuit clone\\Game Logos\\SSBUltimate.png")
        self.Logo = self.Logo.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        self.LogoWidget = QLabel()
        self.LogoWidget.setPixmap(QPixmap(self.Logo))
        self.GameInfo = GameInfo(data, game_id)
        
        #self.GameColors = GameColors(game_data['colors'])

        #Scroll = QScrollArea(self)
        #Scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        #Scroll.setWidget(self.GameColors)
        
        self.GameInfo.logoUpdated.connect(self.updateLogo)
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.LogoWidget)
        top_layout.addWidget(self.GameInfo)
        #top_layout.addWidget(Scroll)
        self.setLayout(top_layout)
        self.setMaximumSize(1500, 300)

    def updateLogo(self, path):
        self.Logo = QImage(path)
        self.Logo = self.Logo.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        self.LogoWidget.setPixmap(QPixmap(self.Logo))
        


class AddGameColor(QWidget):
    def __init__(self):
        super().__init__()
        self.ColorName = QLabel("#000000")
        box = QPixmap(30, 30)
        box.fill(QColor("#000000"))
        self.ColorBox = QLabel()
        self.ColorBox.setPixmap(box)
        self.ChangeButton = QPushButton("Change Color")

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.ColorName)
        self.layout.addWidget(self.ColorBox)
        self.layout.addWidget(self.ChangeButton)

        self.setLayout(self.layout)

        self.ChangeButton.clicked.connect(self.changeColor)

    def changeColor(self):
        self.cDialog = QColorDialog()
        color = self.cDialog.getColor()
        self.ColorName.setText(color.name())
        box = QPixmap(30,30)
        box.fill(color)
        self.ColorBox.setPixmap(box)

    def color(self):
        return self.ColorName.text()
        



class GameTab(QFrame):
    def __init__(self, data):
        super().__init__()
        self.GameList = []
        self.data = data
        for game in data['games']:
            self.GameList.append(GameBox(data, game))
        
        self.layout = QVBoxLayout()
        for game in self.GameList:
            self.layout.addWidget(game)
        self.AddGameButton = QPushButton("Add Game")
        self.layout.addWidget(self.AddGameButton)
        self.setLayout(self.layout)

        self.AddGameButton.clicked.connect(self.addGame)

    def addGame(self):
        self.dlg = QDialog()
        self.dlg.setModal(True)
        self.dLayout = QVBoxLayout()
        self.dlg.setLayout(self.dLayout)

        self.GameName= TextRow("Game Name")
        self.LogoPath = TextRow("Logo Path")
        self.Color = AddGameColor()
       
        self.dLayout.addWidget(self.GameName)
        self.dLayout.addWidget(self.LogoPath)
        self.dLayout.addWidget(self.Color)
        
        self.confirmButton = QPushButton("Add Game")
        self.confirmButton.clicked.connect(self.accept)
        self.dLayout.addWidget(self.confirmButton)

        self.dlg.exec()
    def accept(self):
        game_id = shortuuid.uuid()
        name = self.GameName.value()
        logo = self.LogoPath.value()
        color = self.Color.color()

        self.data['game_map'][name] = game_id
        self.data['games'][game_id] = {
            "name" : name,
            "logo" : logo,
            "color" : color
        }

        self.layout.addWidget(GameBox(self.data, game_id))

        self.dlg.accept()

class StreamInfo(QWidget):
    updateLogo = pyqtSignal(str)
    removeStream = pyqtSignal()
    def __init__(self, data, stream_id):
        self.data = data
        self.id = stream_id
        super().__init__()
        self.StreamPlat = TextRow("Stream Platform", "")
        self.StreamName = TextRow("Stream Channel", "")
        self.LogoPath = TextRow("Logo Path", "")
        self.RemoveButton = QPushButton("Remove Stream")

        layout = QFormLayout()
        layout.addWidget(self.StreamPlat)
        layout.addWidget(self.StreamName)
        layout.addWidget(self.LogoPath)
        layout.addWidget(self.RemoveButton)

        self.StreamPlat.changedText.connect(self.updateStreamPlat)
        self.StreamName.changedText.connect(self.updateStreamName)
        self.LogoPath.changedText.connect(self.updateStreamLogo)
        self.RemoveButton.clicked.connect(self.removeStream)

        self.setLayout(layout)

        if data['streams'][stream_id]['platform']:
            self.StreamPlat.setValue(data['streams'][stream_id]['platform'])
        if data['streams'][stream_id]['stream']:
            self.StreamName.setValue(data['streams'][stream_id]['stream'])
        if data['streams'][stream_id]['logo']:
            self.LogoPath.setValue( data['streams'][stream_id]['logo'])
        self.setMinimumWidth(400)
    
    def updateStreamPlat(self, plat):
        old_link = self.data['streams'][self.id]['platform'] + self.data['streams'][self.id]['stream']
        self.data['streams'][self.id]['platform'] = plat
        new_link = plat + self.data['streams'][self.id]['stream']
        self.data['stream_map'].pop(old_link)
        self.data['stream_map'][new_link] = self.id

    def updateStreamName(self, name):
        old_link = self.data['streams'][self.id]['platform'] + self.data['streams'][self.id]['stream']
        self.data['streams'][self.id]['stream'] = name
        new_link = self.data['streams'][self.id]['platform'] + name
        self.data['stream_map'].pop(old_link)
        self.data['stream_map'][new_link] = self.id

    def updateStreamLogo(self, logo):
        self.data['streams'][self.id]['logo'] = logo
        self.updateLogo.emit(logo)

    def removeStream(self):
        if len(self.data['streams'][self.id]['blocks']) > 0:
            return
        else:
            self.data['streams'].pop(self.id)
            self.parent().setVisible(False)
            for day in self.data['days']:
                try:
                    index =self.data['days'][day]['streams'].index(self.id)
                except ValueError:
                    continue
                self.data['days'][day]['streams'].pop(index)
        
        


class StreamBox(QWidget):
    def __init__(self, data, stream_id):
        super().__init__()
        self.Logo = None
        if data['streams'][stream_id] is not None:
            self.Logo = QImage(data['streams'][stream_id]['logo'])
        else: self.Logo = QImage("E:\\Acekingoffsuit clone\\Game Logos\\SSBUltimate.png")
        self.Logo = self.Logo.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        self.LogoWidget = QLabel()
        self.LogoWidget.setPixmap(QPixmap(self.Logo))
        self.StreamInfo = StreamInfo(data, stream_id)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.LogoWidget)
        self.layout.addWidget(self.StreamInfo)
        self.setLayout(self.layout)
        self.StreamInfo.updateLogo.connect(self.updateLogo)
        
    def updateLogo(self, path):
        self.Logo = QImage(path)
        self.Logo = self.Logo.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        self.LogoWidget.setPixmap(QPixmap(self.Logo))

class StreamTab(QWidget):
    def __init__(self, data):
        self.data = data
        super().__init__()
        self.StreamList = []
        for stream in data['streams']:
            self.StreamList.append(StreamBox(data, stream))
        
        self.layout = QVBoxLayout()
        for stream in self.StreamList:
            self.layout.addWidget(stream)
        self.AddStreamButton = QPushButton("Add Stream")
        self.layout.addWidget(self.AddStreamButton)
        self.setLayout(self.layout)

        self.AddStreamButton.clicked.connect(self.openDialog)

        self.dlg = QDialog()
        self.dlg.setModal(True)
        self.dLayout = QVBoxLayout()
        self.dlg.setLayout(self.dLayout)

    def openDialog(self):
        self.dlg = QDialog()
        self.dlg.setModal(True)
        self.dLayout = QVBoxLayout()
        self.dlg.setLayout(self.dLayout)

        self.Plat = TextRow("Platform")
        self.Channel = TextRow("Channel")
        self.LogoPath = TextRow("Logo Path")
       
        self.dLayout.addWidget(self.Plat)
        self.dLayout.addWidget(self.Channel)
        self.dLayout.addWidget(self.LogoPath)
        
        self.confirmButton = QPushButton("Add Stream")
        self.confirmButton.clicked.connect(self.accept)
        self.dLayout.addWidget(self.confirmButton)

        self.dlg.exec()


    def accept(self):
        platform = self.Plat.value()
        channel = self.Channel.value()
        path = self.LogoPath.value()

        stream_id = shortuuid.uuid()
        stream_link = platform + channel

        self.data['stream_map'][stream_link] = stream_id

        self.data['streams'][stream_id] = {
            "platform" : platform,
            "stream" : channel,
            "logo" : path,
            "blocks" : []
        }

        index = self.layout.count() - 1
        self.layout.insertWidget(index, StreamBox(self.data, stream_id))

        self.dlg.accept()


class BlockColor(QWidget):
    def __init__(self, color):
        super().__init__()
        box = QPixmap(30, 30)
        box.fill(QColor(color))
        self.ColorBox = QLabel()
        self.ColorBox.setPixmap(box)
        self.ColorName = QLabel(color)
        layout = QHBoxLayout()
        layout.addWidget(self.ColorName)
        layout.addWidget(self.ColorBox)
        self.setLayout(layout)
        self.setMinimumSize(400, 60)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    def changeColor(self, color):
        box = QPixmap(30, 30)
        box.fill(QColor(color))
        self.ColorBox.setPixmap(box)
        self.ColorName.setText(color)



        

class BlockInfo(QWidget):
    gameUpdated = pyqtSignal(str)
    def __init__(self, data, block_id):
        self.id = block_id
        self.data = data
        super().__init__()
        game_list = list(self.data['game_map'].keys())
        self.Game = SearchableDropdown("Game", "", game_list)
        self.GameOverride = QCheckBox("Override Game Name")
        self.GameName = TextRow("Game Name Override")
        self.GameName.hide()

        self.Logo = TextRow("Logo")
        self.Logo.disable()
        self.LogoOverride = QCheckBox("Override Game Logo")
        self.BlockLogo = TextRow("Logo Override")
        self.BlockLogo.hide()

        self.layout = QFormLayout()
        self.layout.addWidget(self.Game)
        #self.layout.addWidget(self.GameName)
        #self.layout.addWidget(self.GameOverride)
        
        self.layout.addWidget(self.Logo)
        self.layout.addWidget(self.BlockLogo)
        #self.layout.addWidget(self.LogoOverride)

        self.ColorDialog = QColorDialog()
        self.BlockColor = BlockColor("#FFFFFF")
        self.layout.addWidget(self.BlockColor)
        self.ColorChange = QPushButton("Change Color")
        #self.layout.addWidget(self.ColorChange)


        self.Round = TextRow("Round")
        self.layout.addWidget(self.Round)
        self.StartTime = TimeRow("Start Time")
        self.EndTime = TimeRow("End Time")
        self.layout.addWidget(self.StartTime)
        self.layout.addWidget(self.EndTime)
        self.removeButton = QPushButton("Remove")
        self.layout.addWidget(self.removeButton)

        self.removeButton.clicked.connect(self.removeBlock)

        
        self.setLayout(self.layout)

        self.GameOverride.stateChanged.connect(self.toggleGameOverride)
        self.LogoOverride.stateChanged.connect(self.toggleLogoOverride)
        self.ColorChange.clicked.connect(self.changeColor)

        self.Game.changedText.connect(self.updateGame)
        self.Round.changedText.connect(self.updateRound)
        self.StartTime.changedTime.connect(self.updateStart)
        self.EndTime.changedTime.connect(self.updateEnd)


        
        if data['blocks'][block_id] is not None:
            game_id = data['blocks'][block_id]['game']
            self.Logo.setValue(data['games'][game_id]['logo'])
            if data['games'][game_id]['name']:
                self.Game.setValue(data['games'][game_id]['name'])
            if data['games'][game_id]['color']:
                self.BlockColor.changeColor(data['games'][game_id]['color'])
            if data['blocks'][block_id]['start']:
                self.StartTime.setTime(data['blocks'][block_id]['start'])
            if data['blocks'][block_id]['end']:
                self.EndTime.setTime(data['blocks'][block_id]['end'])
            if data['blocks'][block_id]['round']:
                self.Round.setValue(data['blocks'][block_id]['round'])

    def updateGame(self, game):
        try:
            game_id = self.data['game_map'][game]
        except KeyError:
            return
        self.data['blocks'][self.id]['game'] = game_id
        self.gameUpdated.emit(game_id)

    def updateRound(self, round):
        self.data['blocks'][self.id]['round'] = round

    def updateStart(self, start):
        self.data['blocks'][self.id]['start'] = start

    def updateEnd(self, end):
        self.data['blocks'][self.id]['end'] = end

    

    def changeColor(self):
        color = self.ColorDialog.getColor()
        self.BlockColor.changeColor(color.name())

    def removeBlock(self):
        self.parent().setVisible(False)
        self.parent().parent().layout.removeWidget(self)
        for day in self.data['days']:
            try:
                index = self.data['days'][day]['blocks'].index(self.id)
                self.data['days'][day]['blocks'].pop(index)
            except ValueError:
                continue
        
        for stream in self.data['streams']:
            try:
                index = self.data['streams'][stream]['blocks'].index(self.id)
                self.data['streams'][stream]['blocks'].pop(index)
            except ValueError:
                continue
        self.data['blocks'].pop(self.id)
        

            
    def toggleGameOverride(self, state):
        if state == 2:
            self.Game.hide()
            self.GameName.show()
        else:
            self.Game.show()
            self.GameName.hide()

    def toggleLogoOverride(self, state):
        if state == 2:
            self.Logo.hide()
            self.BlockLogo.show()
        else:
            self.Logo.show()
            self.BlockLogo.hide()



class BlockBox(QFrame):
    def __init__(self, data, block_id):
        super().__init__()
        self.id = block_id
        self.data = data

        self.Logo = None
        self.gameId = data['blocks'][block_id]['game'] 
        if self.gameId is not None:
            self.Logo = QImage(data['games'][self.gameId]['logo'])
        else: 
            self.Logo = QImage("ssbu.png")
        self.Logo = self.Logo.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        self.LogoWidget = QLabel()
        self.LogoWidget.setPixmap(QPixmap(self.Logo))
        

        self.layout = QHBoxLayout()
        self.BlockInfo = BlockInfo(data, block_id)
        self.layout.addWidget(self.LogoWidget)
        self.layout.addWidget(self.BlockInfo)
        self.setLayout(self.layout)
        self.setMaximumSize(600, 350)

        self.setLineWidth(1)
        self.setFrameStyle(QFrame.Shape.Panel)
        self.BlockInfo.gameUpdated.connect(self.updateLogo)

    def updateLogo(self, game_id):
        self.Logo = QImage(self.data['games'][game_id]['logo'])
        self.Logo = self.Logo.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        self.LogoWidget.setPixmap(QPixmap(self.Logo))



class StreamBlocksTab(QWidget):
    def __init__(self, data, stream_id, day_id):
        super().__init__()
        self.stream = stream_id
        self.day = day_id
        self.data = data
        self.layout = QVBoxLayout()
        self.blocks = 0
        for block in data['streams'][stream_id]['blocks']:
            if block in data['days'][day_id]['blocks']:
                self.layout.addWidget(BlockBox(data, block))
                self.blocks += 1

        self.setLayout(self.layout)
        self.AddButton = QPushButton("Add Block")
        self.layout.addWidget(self.AddButton)
        self.layout.addStretch()
        self.AddButton.clicked.connect(self.openDialog)

        

    def openDialog(self):
        self.dlg = QDialog()
        self.dlg.setModal(True)
        self.dLayout = QVBoxLayout()
        self.dlg.setLayout(self.dLayout)
        self.games = list(self.data['game_map'].keys())
        self.c_box = SearchableDropdown("Game", "", self.games)
        self.round = TextRow("Round")
        self.start = TimeRow("Start Time")
        self.end   = TimeRow("End Time")
        
       
        self.dLayout.addWidget(self.c_box)
        self.dLayout.addWidget(self.round)
        self.dLayout.addWidget(self.start)
        self.dLayout.addWidget(self.end)
        
        self.confirmButton = QPushButton("Add Block")
        self.confirmButton.clicked.connect(self.accept)
        self.dLayout.addWidget(self.confirmButton)

        self.dlg.exec()
        
    def blockCount(self):
        return self.blocks
    
    def accept(self):
        game_id = self.data['game_map'][self.c_box.value()]
        round = self.round.value()
        start = self.start.value()
        end = self.end.value()

        block_id = shortuuid.uuid()
        self.data['days'][self.day]['blocks'].append(block_id)
        self.data['streams'][self.stream]['blocks'].append(block_id)
        self.data['blocks'][block_id] = {
            "game" : game_id,
            "round" : round,
            "start" : start,
            "end" : end
        }
        index = self.layout.count() - 2
        self.layout.insertWidget(index, BlockBox(self.data, block_id))
        
        self.blocks+=1

        self.dlg.accept()


class StreamDayInfo(QWidget):
    def __init__(self, data, stream_id):
        super().__init__()
        self.data = data
        self.stream_id = stream_id
        self.Platform = TextRow("Platform")
        self.Channel = TextRow("Channel")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.Platform)
        self.layout.addWidget(self.Channel)
        self.Platform.disable()
        self.Channel.disable()
        stream = data['streams'][stream_id]
        if stream:
            self.Platform.setValue(stream['platform'])
            self.Channel.setValue(stream['stream'])
        self.setLayout(self.layout)
        self.removeButton = QPushButton("remove")
        self.layout.addWidget(self.removeButton)
        self.removeButton.clicked.connect(self.removeStream)

    def removeStream(self):
        if len(self.data['streams'][self.stream_id]['blocks']) > 0:
            return
        else:
            self.parent().setVisible(False)
            day_id = self.parent().parent().id
            index = self.data['days'][day_id]['streams'].index(self.stream_id)
            self.data['days'][day_id]['streams'].pop(index)

        
class StreamDayBox(QFrame):
    def __init__(self, data, stream_id):
        super().__init__()
        self.Logo = None
        self.data = data
        self.id= stream_id
        if data['streams'][stream_id]['logo'] is not None:
            self.Logo = QImage(data['streams'][stream_id]['logo'])
        else: 
            self.Logo = QImage("ssbu.png")
        self.Logo = self.Logo.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        self.LogoWidget = QLabel()
        self.LogoWidget.setPixmap(QPixmap(self.Logo))
        self.Info = StreamDayInfo(data, stream_id)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.LogoWidget)
        self.layout.addWidget(self.Info)
        self.setLayout(self.layout)
        self.setMaximumSize(650, 200)
        self.setMinimumSize(650, 200)
        
        
        
        self.setLineWidth(1)
        self.setFrameStyle(QFrame.Shape.Panel)

    

    def mousePressEvent(self, e):
        self.parent().parent().loadStreamBlocks(self.id)

class StreamDayTab(QWidget):
    def __init__(self, day, data):
        super().__init__()
        self.layout = QVBoxLayout()
        self.data = data
        self.id = day
        minimumSize = 500
        for stream in data['days'][day]['streams']:
            self.layout.addWidget(StreamDayBox(data, stream))
            minimumSize += 500
        self.setMinimumSize(500,minimumSize)
        
        self.AddButton = QPushButton("Add Stream")
        self.AddButton.setMaximumWidth(500)
        self.layout.addWidget(self.AddButton)
        self.setLayout(self.layout)
        self.layout.addStretch()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.AddButton.clicked.connect(self.openDialog)

        

    def openDialog(self):
        self.dlg = QDialog()
        self.dlg.setModal(True)
        self.dLayout = QVBoxLayout()
        self.dlg.setLayout(self.dLayout)
        self.streams = list(self.data['stream_map'].keys())
        self.c_box = SearchableDropdown("Stream", "", self.streams)
        self.confirmButton = QPushButton("Add Stream")
        self.confirmButton.clicked.connect(self.accept)
        self.dLayout.addWidget(self.c_box)
        self.dLayout.addWidget(self.confirmButton)
        self.dlg.exec()

    def accept(self):
        stream_id = self.data['stream_map'][self.c_box.value()]
        if not stream_id in self.data['days'][self.id]['streams']:
            self.data['days'][self.id]['streams'].append(stream_id)
            index = self.layout.count() - 2
            self.layout.insertWidget(index ,StreamDayBox(self.data, stream_id))

        self.dlg.accept()



    



class DayBox(QFrame):
    def __init__(self, day, id, data):
        self.id = id
        super().__init__()
        self.layout = QVBoxLayout()
        self.Day = SearchableDropdown("Day", "", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        self.Date = DateRow("Date")
        self.layout.addWidget(self.Day)
        self.layout.addWidget(self.Date)
        self.RemoveButton = QPushButton("Remove")
        self.layout.addWidget(self.RemoveButton)
        self.data = data
        self.RemoveButton.clicked.connect(self.removeDay)
        

        if day['day']:
            self.Day.setValue(day['day'])
        if day['date']:
            self.Date.setDate(day['date'])
        self.setLayout(self.layout)
        self.setLineWidth(1)
        self.setFrameStyle(QFrame.Shape.Panel)
        self.setMinimumSize(200, 150)
        self.setMaximumSize(400, 150)
        self.Day.changedText.connect(self.updateDay)
        self.Date.changedDate.connect(self.updateDate)

    def updateDay(self, day):
        self.data['days'][self.id]['day'] = day

    def updateDate(self, date):
        self.data['days'][self.id]['date'] = date

    def mousePressEvent(self, e):
        try:
            self.parent().parent().loadDayStreams(self.id)
        except:
            return
    def setEditable(self, value:bool):
        if value:
            self.Day.enable()
            self.Date.enable()
            self.RemoveButton.setEnabled(True)
            self.RemoveButton.setVisible(True)
        else:
            self.Day.disable()
            self.Date.disable()
            self.RemoveButton.setVisible(False)
    def removeDay(self):
        
        if len(self.data['days'][self.id]['streams']) > 0:
            return
        self.parent().adjustSize()
        self.setVisible(False)
        self.data['days'].pop(self.id)
class DaysTab(QWidget):
    def __init__(self, days, data):
        super().__init__()
        self.data = data
        self.layout = QVBoxLayout()
        self.setMaximumSize(500, 10000)
        self.setMinimumSize(500, 300)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.dayWidgets = []
        for day in days:
            widget = DayBox(days[day], day, data)
            self.layout.addWidget(widget)
            self.dayWidgets.append(widget)
        self.AddButton = QPushButton("Add Day")
        self.layout.addWidget(self.AddButton)
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.AddButton.clicked.connect(self.addDay)

    def setEditable(self, value:bool):
        for widget in self.dayWidgets:
            widget.setEditable(value)

    
    def addDay(self):
        day_id = shortuuid.uuid()
        day_obj = {
            "day" : None,
            "date" : None,
            "blocks" : [],
            "streams" : []
        }
        self.data['days'][day_id] = day_obj

        newDayWidget = DayBox(day_obj, day_id, self.data)
        index = self.layout.count() - 1
        self.layout.insertWidget(index, newDayWidget)
        size = self.size()
        self.setMinimumSize(size.width(), size.height() + 550)



class BlocksTab(QFrame):
    def __init__(self, data):
        self.data = data
        super().__init__()
        self.layout = QHBoxLayout()
        self.DaysTab = DaysTab(data['days'], data)
        self.DaysTab.setEditable(False)
        self.currentDayID = None
        self.currentStreamKey = None
        self.layout.addWidget(self.DaysTab)
        self.layout.setAlignment(self.DaysTab, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.layout)
        self.StreamsColumn = None
        self.BlockColumn = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.setMinimumSize(1000, 2000)
        self.setMaximumSize(1920, 25000)
        self.layout.addStretch()
        self.setLineWidth(1)
        self.setFrameStyle(QFrame.Shape.Panel)
        
    def loadDayStreams(self, id):
        if self.currentDayID == id: return
        self.currentDayID = id
        if self.StreamsColumn:
            self.layout.removeWidget(self.StreamsColumn)
        else:
            size = self.minimumSize()
            self.setMinimumSize(size.width()+500, size.height())
        if self.BlockColumn:
            self.BlockColumn.setVisible(False)
            self.layout.removeWidget(self.BlockColumn)
        self.StreamsColumn = StreamDayTab(self.currentDayID, self.data)
        
        index = self.layout.count() - 1
        self.layout.insertWidget(index, self.StreamsColumn)

        height = self.StreamsColumn.layout.count() * 250
        self.setMinimumHeight(height)
        self.adjustSize()

    def loadStreamBlocks(self, stream_id):
        self.stream_id = stream_id
        if self.BlockColumn:
            self.layout.removeWidget(self.BlockColumn)
        else:
            size = self.minimumSize()
            self.setMinimumSize(size.width()+500, size.height())
        self.BlockColumn = StreamBlocksTab(self.data, self.stream_id, self.currentDayID)
        index = self.layout.count() - 1
        self.layout.insertWidget(index, self.BlockColumn)
        size = self.size()
        blockHeight = self.BlockColumn.blockCount() * 500
        if size.height() < blockHeight:
            self.setMinimumSize(size.width(), blockHeight)


class mainTab(QTabWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.oldIndex = None

        self.EventArea = QScrollArea()
        self.EventTab = EventTab(data)
        self.EventArea.setWidget(self.EventTab)
        self.addTab(self.EventArea, "Event")

       
        self.BlocksArea = QScrollArea()
        self.BlocksTab = BlocksTab(data)
        self.BlocksArea.setWidget(self.BlocksTab)
        self.addTab(self.BlocksArea, "Blocks")
        
        self.DaysArea = QScrollArea()
        self.DaysTab = DaysTab(data['days'], data)
        self.DaysArea.setWidget(self.DaysTab)
        self.addTab(self.DaysArea, "Days")
        
        self.GamesArea = QScrollArea()
        self.GamesTab = GameTab(data)
        self.GamesArea.setWidget(self.GamesTab)
        self.addTab(self.GamesArea, "Games")
        
        self.StreamArea = QScrollArea()
        self.StreamTab = StreamTab(data)
        self.StreamArea.setWidget(self.StreamTab)
        self.addTab(self.StreamArea, "Streams")

        self.setMinimumSize(3000, 3000)

        self.currentChanged.connect(self.changeTabs)

    
    def changeTabs(self, newIndex):
        label = self.tabText(newIndex)
        if label == "Blocks":
            self.BlocksTab = BlocksTab(self.data)
            self.BlocksArea.setWidget(self.BlocksTab)
        elif label == "Days":
            self.DaysTab = DaysTab(self.data['days'], self.data)
            self.DaysArea.setWidget(self.DaysTab)
        elif label == "Games":
            self.GamesTab = GameTab(self.data)
            self.GamesArea.setWidget(self.GamesTab)
        elif label == "Streams":
            self.StreamTab = StreamTab(self.data)
            self.StreamArea.setWidget(self.StreamTab)
        elif label == "Event":
            self.EventTab = EventTab(self.data)
            self.EventArea.setWidget(self.EventTab)


class mainWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.ScrollArea = QScrollArea()
        self.ScrollArea.setWidget(mainTab(data))
        
        self.setCentralWidget(self.ScrollArea)
        self.resize(1920, 1000)
        self.show()

        self.fileMenu = self.menuBar().addMenu("&File")

        newAction = QAction("&Create New", self)
        newAction.triggered.connect(self.createNew)

        loadAction = QAction("&Load File", self)
        loadAction.triggered.connect(self.loadFile)
        
        saveAction = QAction("&Save File", self)
        saveAction.triggered.connect(self.saveFile)
        self.fileMenu.addAction(newAction)
        self.fileMenu.addAction(loadAction)
        self.fileMenu.addAction(saveAction)

    def createNew(self):
        self.hide()
        new_data = data_management.load_empty()
        self.data['days'] = new_data['days']
        self.data['event'] = new_data['event']
        self.data['games'] = new_data['games']
        self.data['streams'] = new_data['streams']
        self.data['blocks'] = new_data['blocks']
        self.data['zones'] = new_data['zones']
        self.data['game_map'] = new_data['game_map']
        self.data['stream_map'] = new_data['stream_map']
        self.ScrollArea.setWidget(mainTab(self.data))
        self.show()

    def loadFile(self):
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dlg.setFileMode(QFileDialog.FileMode.ExistingFile)
        fileName = dlg.getOpenFileName(self, "Open Schedule", ".", "Schedule File (*.json)")
        json = data_management.loadJSON(fileName[0])
        new_data = data_management.parseJSON2(json)

        self.hide()
        self.data['days'] = new_data['days']
        self.data['event'] = new_data['event']
        self.data['games'] = new_data['games']
        self.data['streams'] = new_data['streams']
        self.data['blocks'] = new_data['blocks']
        self.data['zones'] = new_data['zones']
        self.data['game_map'] = new_data['game_map']
        self.data['stream_map'] = new_data['stream_map']
        self.ScrollArea.setWidget(mainTab(self.data))
        self.show()

    def saveFile(self):
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dlg.setFileMode(QFileDialog.FileMode.AnyFile)
        fileName = dlg.getSaveFileName(self, "Open Schedule", ".", "Schedule File (*.json)")
        print(fileName)
        data_management.save_data(fileName[0], self.data)

def createWindow(data):
    
    #window = widgets.TextRow("yes", "tes")
    window = QScrollArea()
    scroll = QScrollArea()
    scroll.setWidget(mainTab(data))

    #window.setWidget(widgets.GameBox(data[4]['Street Fighter V']))
    #window.setWidget(widgets.EventTab(data))
    #window.setWidget(widgets.BlockBox(data['blocks'][list(data['blocks'].keys())[1]]))
    window = QMainWindow()
    fileMenu = window.menuBar().addMenu("&File")
    window.setCentralWidget(scroll)
    window.resize(1920, 1080)
    window.show()
            
       