import numpy as np
from PyQt5.QtCore import QThread, QObject, QCoreApplication
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QLabel, \
    QVBoxLayout, QHBoxLayout, QMenuBar, QComboBox
from pyqtgraph import ImageView

from ..functions import colormap_functions
from .styleSheet import start_button_stylesheet, stop_button_stylesheet


class imageViewerWidget(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(1, 0, 1, 5)

        self.imageViewer = ImageView()
        self.imageViewer.getHistogramWidget().hide()
        self.histogramToggle = False
        self.imageViewer.ui.roiBtn.hide()
        self.imageViewer.ui.menuBtn.hide()
        self.layout.addWidget(self.imageViewer)

        self.optionsMenu = QMenuBar()
        self.optionsMenu.addMenu("Options")

        self.layout.addWidget(self.imageViewer)

        self.buttons = QHBoxLayout()
        self.buttons.setContentsMargins(5, 0, 5, 0)
        self.toggleHistogramButton = QPushButton("Adjust histogram")
        self.buttons.addWidget(self.toggleHistogramButton)

        self.buttons.addWidget(QLabel("Colormap:"))
        self.colorMapsComboBox = QComboBox()
        self.colorMapsComboBox.addItems(["None", 'viridis', 'plasma', 'coolwarm', 'Spectral', 'bwr',
                                         'twilight', 'hsv', 'baker', 'jet', 'rainbow'])
        self.buttons.addWidget(self.colorMapsComboBox)

        self.buttons.addWidget(QLabel("Frame rate:"))
        self.framerateLineedit = QLineEdit("10")
        self.buttons.addWidget(self.framerateLineedit)

        self.fastRewindButton = QPushButton("<<")
        self.buttons.addWidget(self.fastRewindButton)
        self.rewindButton = QPushButton("<")
        self.buttons.addWidget(self.rewindButton)
        self.playPauseButton = QPushButton("Play")
        self.playToggle = False
        self.buttons.addWidget(self.playPauseButton)
        self.forwardButton = QPushButton(">")
        self.buttons.addWidget(self.forwardButton)
        self.fastForwardButton = QPushButton(">>")
        self.buttons.addWidget(self.fastForwardButton)
        self.layout.addLayout(self.buttons)

        self.toggleHistogramButton.clicked.connect(self.onToggleHistogramClicked)
        self.colorMapsComboBox.currentTextChanged.connect(self.onToggleColormapChange)
        self.fastRewindButton.clicked.connect(self.onfastRewindButtonClicked)
        self.rewindButton.clicked.connect(self.onRewindButtonClicked)
        self.playPauseButton.clicked.connect(self.onPlayButtonClicked)
        self.forwardButton.clicked.connect(self.onForwardButtonClicked)
        self.fastForwardButton.clicked.connect(self.onfastForwardButtonClicked)

        self.setStyleSheet("QWidget:window {background-color: white;}")

        self.length = 0

        self.image = None
        self.colorMap = "None"

        # create thread
        self.thread = QThread()

        # create object which will be moved to another thread
        self.worker = ImageViewMonitor()
        self.worker.moveToThread(self.thread)

    def displayImage(self, pos=None, size=None):
        self.show()
        if pos is None:
            pass

        if size is None:
            self.resize(800, 900)
        else:
            self.resize(size)

    def setWindowTitle(self, title):
        self.imageViewer.setWindowTitle(title)

    def updateImageViewer(self, image):
        self.image = np.array(image)

        shape = self.image.shape
        if len(shape) == 4:
            self.imageViewer.setImage(self.image, axes={'t': 0, 'x': 2, 'y': 1, 'c': 3})
            self.length = shape[0]
        elif len(shape) == 3:
            self.imageViewer.setImage(self.image, axes={'t': 0, 'x': 2, 'y': 1})
            self.length = shape[0]
        elif len(shape) == 2:
            self.imageViewer.setImage(self.image, axes={'x': 1, 'y': 0})

    def onToggleHistogramClicked(self):
        if self.histogramToggle is True:
            self.imageViewer.getHistogramWidget().hide()
            self.histogramToggle = False
        else:
            self.imageViewer.getHistogramWidget().show()
            self.onToggleColormapChange()
            self.histogramToggle = True

    def onToggleColormapChange(self):
        self.colorMap = self.colorMapsComboBox.currentText()
        if self.colorMap == "None":
            colormap = colormap_functions.parse_colormap("Greys_r")
        else:
            colormap = colormap_functions.parse_colormap(self.colorMap)

        colormap._init()
        lut = (colormap._lut * 255).view(np.ndarray)
        self.imageViewer.imageItem.setLookupTable(lut)

    def onRewindButtonClicked(self):
        self.imageViewer.jumpFrames(-1)

    def onForwardButtonClicked(self):
        self.imageViewer.jumpFrames(1)

    def onfastRewindButtonClicked(self):
        self.imageViewer.setCurrentIndex(0)

    def onfastForwardButtonClicked(self):
        self.imageViewer.setCurrentIndex(self.length-1)

    def onPlayButtonClicked(self):
        if self.playToggle is False:
            # TODO: check if frame rate is valid
            frameRate = int(self.framerateLineedit.text())
            self.imageViewer.play(frameRate)
            self.playPauseButton.setText("Pause")
            self.playPauseButton.setStyleSheet(stop_button_stylesheet)
            self.playToggle = True
            self.worker.startRepeat(self.imageViewer, self.length)
            self.thread.start()
        else:
            self.imageViewer.play(0)
            self.playPauseButton.setText("Play")
            self.playPauseButton.setStyleSheet(start_button_stylesheet)
            self.playToggle = False
            self.worker.stopRepeat()
            self.thread.quit()


class ImageViewMonitor(QObject):
    def __init__(self):
        super(QObject, self).__init__()
        self._abort = False

    def startRepeat(self, imageviewer, length):
        self._abort = False
        while True:
            QCoreApplication.processEvents()
            if imageviewer.currentIndex == length-1:
                imageviewer.setCurrentIndex(0)

            if self._abort:
                break

    def stopRepeat(self):
        self._abort = True
