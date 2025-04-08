# we are making a jeopardy scoring system
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication, QShortcut, QMainWindow, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QKeySequence, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5 import QtWidgets, QtCore, QtGui
import threading, sys

class CommandListener(QObject):
    # Signal to send new multiplier to the GUI
    multiplier_changed = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        threading.Thread(target=self.listen_for_commands, daemon=True).start()

    def listen_for_commands(self):
        while True:
            command = sys.stdin.readline().strip()
            try:
                print(command)
                key, value = command.split()
                if key == "m":
                    new_multiplier = int(value)
                    allowed = [100, 200, 300, 400, 500]
                    if new_multiplier in allowed:
                        self.multiplier_changed.emit(new_multiplier)
                        print("Emitted:", new_multiplier)
                    else:
                        raise ValueError
                elif key[0] == "t":
                    # adding a flat value
                    team = key[1:]
                    # we need to find the team and print their current score
                    # check if value is an integer
                    try:
                        int(value)
                    except ValueError:
                        raise ValueError
                    
                    a = window.boxes
                    for key in a:
                        if key == f"Team {team}":
                            window.boxes[key].setScore(int(value) + window.boxes[key].getScore())
                            window.boxes[key].updateScore()
                            window.updateSorted(window.boxes[key], 0)
                            break
                    
            except (ValueError, IndexError):
                print("Invalid command. Usage: m <100|200|300|400|500> or t<Team Number> <value>")

class CustomScoring():
    def __init__(self):
        self.score = 0 # Set the initial to 0
        self.placement = 1 # the placement of the team

    def add(self, amount): # this might be reworked
        self.score += amount + (self.placement - 1) * 50 # add the amount and the placement bonus
        
    def subtract(self, amount):
        self.score -= amount # This is fixed to 100
    
    def getScore(self):
        return self.score

    def setScore(self, score):
        self.score = score

    def getScoreAsString(self):
        return str(self.score)

    def setPlacement(self, placement):
        self.placement = placement
    
    def getPlacement(self):
        return self.placement
    

class PlayerBox(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name
        # make itself a 100 x 100 box
        self.widget = QWidget()
        self.Vwidget = QVBoxLayout()

        self.name = name
        self.nameLabel = QLabel(self.name)

        self.nameLabel.setStyleSheet(f"color: #000000; font-size: 20px; font-weight: bold; padding: 0px; margin: 0px; border: none; border-bottom-width: 2px; border-bottom-style: solid; border-bottom-color: #000000")
        self.nameLabel.setAlignment(Qt.AlignCenter) # centered Text
        self.nameLabel.setContentsMargins(0, 0, 0, 0) # remove padding

        self.score = CustomScoring()
        self.scoreLabel = QLabel(self.score.getScoreAsString())
        self.scoreLabel.setAlignment(Qt.AlignCenter) # centered Text
        self.scoreLabel.setStyleSheet(f"background-color: #2A3698; color: #FFFFFF; font-size: 20px; font-weight: bold; padding: 0px; margin: 0px; border: none")
        self.scoreLabel.setContentsMargins(0, 0, 0, 0) # remove padding

        self.buttons = QWidget()
        self.buttonArray = QHBoxLayout()
        self.buttonArray.setAlignment(Qt.AlignCenter)
        self.buttonArray.setContentsMargins(0, 0, 0, 0) # remove padding 2DA94E

        self.addButton = QPushButton("+")
        self.addButton.setStyleSheet(f"background-color: transparent; font-size: 25px; font-weight: bold; color: #2DA94E") # get a muted green
        # self.addButton.clicked.connect(lambda:self.add())
        self.buttonArray.addWidget(self.addButton)

        self.subtractButton = QPushButton("-")
        self.subtractButton.setStyleSheet(f"background-color: transparent; font-size: 25px; font-weight: bold; color: #FF0000")
        # self.subtractButton.clicked.connect(lambda:self.sub())
        self.buttonArray.addWidget(self.subtractButton)

        self.buttons.setLayout(self.buttonArray)

        self.Vwidget.addWidget(self.nameLabel)
        self.Vwidget.addWidget(self.scoreLabel)
        self.Vwidget.addWidget(self.buttons)
        self.widget.setFixedSize(110, 110)
        self.widget.setStyleSheet(f"background-color: #FFFFFF")
        self.widget.setLayout(self.Vwidget)

    def getBox(self):
        return self.widget

    def setPlacement(self, placement):
        self.score.setPlacement(placement)

    def getPlacement(self):
        return self.score.getPlacement()

    def add(self, value):
        self.score.add(value)
        self.updateScore()

    def sub(self):
        self.score.subtract(50)
        self.updateScore()

    def updateScore(self):
        self.scoreLabel.setText(self.score.getScoreAsString())

    def getScore(self):
        return self.score.getScore() # return the integer version of the score

    def setScore(self, score):
        self.score.setScore(score)
        self.updateScore()

class JeopardyUI(QMainWindow):
    def __init__(self, players):
        super().__init__()
        self.players = players
        self.widget = QWidget(self)

        self.setCentralWidget(self.widget)
        #setup shortcut
        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self.close_application)
        self.initUI()
        self.mouse_press_pos = None

    def initUI(self):

        def makeMultiplierVBox():
            vBox = QVBoxLayout()
            vBox.setAlignment(Qt.AlignCenter)
            vBox.setSpacing(5)
            # th vbox needs to be made of 5 buttons
            # 100, 200, 300, 400, 500
            buttons = [100, 200, 300, 400, 500]
            for button in buttons:
                b = QPushButton(str(button))
                b.setStyleSheet(f"background-color: #FFFFFF; font-size: 11; font-weight: bold; color: #2A3698")
                b.setFixedSize(100, 20)
                b.setContentsMargins(0, 0, 0, 0) # remove padding
                b.clicked.connect(lambda _, value=button: newGlobalScore(value))
                vBox.addWidget(b)
            return vBox

        print("InitUI")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Removes title bar and border
        self.setAttribute(Qt.WA_TranslucentBackground)  # Make the window transparent

        # This needs to be a 100 x 100 box with 200 pixels on each side AND 20 px in between each box
        layout = QHBoxLayout(self.widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 0)  # left, top, right, bottom
        self.boxes = {}
        for i in range(len(self.players)):
            # fill the dictionary with the appropriate keys
            self.boxes[self.players[i]] = None

        for i in range(len(self.players)):
            self.boxes[self.players[i]] = PlayerBox(self.players[i])

        # adding the buttons
        for i in range(len(self.boxes)):
            self.boxes[self.players[i]].addButton.clicked.connect(lambda _, b=self.boxes[self.players[i]]: self.updateSorted(b, 1))
            self.boxes[self.players[i]].subtractButton.clicked.connect(lambda _, b=self.boxes[self.players[i]]: self.updateSorted(b, -1))

        for i in range(len(self.players)):
            layout.addWidget(self.boxes[self.players[i]].getBox(), stretch = 1)

        # add another widget to it
        layout.addLayout(makeMultiplierVBox())

    def updateSorted(self, box, value):
        f = open("log.txt", "a")

        #current standing
        f.write("====================\n")
        f.write("Current Standings\n")
        f.write("====================\n")
        for key in self.boxes:
            f.write(f"{key} has {self.boxes[key].getScore()} points\n")
        f.write("====================\n")

        s = ""
        if value == 1:
            box.add(currentQuestionValue)
            s += f"{box.name} has {box.getScore()} points increasing by {currentQuestionValue}*\n"
        if value == -1:
            box.sub()
            s += f"{box.name} has {box.getScore()} points decreasing by 50\n"

        # sort the boxes by score
        sortedBoxes = sorted(self.boxes.values(), key=lambda x: x.getScore(), reverse=True)

        # we need to work out how the placements will be distributed
        cScore = sortedBoxes[0].getScore()
        placement = 1
        pBuffer = 0
        sortedBoxes[0].setPlacement(placement)
        s += "====================\n"
        s += f"{sortedBoxes[0].name} is in {sortedBoxes[0].getPlacement()} place with {sortedBoxes[0].getScore()} points\n"
        counter = 1


        for _ in range(1, len(sortedBoxes)): # we can skip the first element
            print(cScore, sortedBoxes[counter].getScore())
            if cScore == sortedBoxes[counter].getScore():
                # This is a tie
                sortedBoxes[counter].setPlacement(placement)
                pBuffer += 1
            else:
                placement = placement + pBuffer + 1
                pBuffer = 0

                sortedBoxes[counter].setPlacement(placement)
            s += f"{sortedBoxes[counter].name} is in {sortedBoxes[counter].getPlacement()} place with {sortedBoxes[counter].getScore()} points\n"
            counter += 1

        print(s)
        f.write(s)
        f.close()

    def mousePressEvent(self, event):
        self.mouse_press_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.mouse_press_pos:
            delta = event.globalPos() - self.mouse_press_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.mouse_press_pos = event.globalPos()

    def close_application(self):
        print("Closing")
        self.close()
        QApplication.quit()
        
def newGlobalScore(value):
    global currentQuestionValue
    print("New Global Score:", value)
    currentQuestionValue = value





global curentQuestionValue
currentQuestionValue = 500

QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)


teamCount = 4
names = []
for i in range(teamCount):
    names.append(f'Team {i+1}')

app = QApplication([])

window = JeopardyUI(names)
window.show()

listener = CommandListener()
listener.multiplier_changed.connect(lambda value: newGlobalScore(value))

app.exec()
