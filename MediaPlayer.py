import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
import icon_resource

##################################################################################################
# I made this media player by referring the following sources.                                   #
# credits:-                                                                                      #
# https://codeloop.org/python-how-to-create-media-player-in-pyqt5/                               #
# https://www.pythonguis.com/examples/python-multimedia-player/                                  #
# https://stackoverflow.com/questions/41612790/pyqt5-videowidget-not-showing-in-layout           #
# https://gist.github.com/QuantumCD/6245215                                                      #
# ---------------------------------------------------------------------------------------------- #
# Packaging PyQt5 applications for Windows:-                                                     #
# https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/ #
# ---------------------------------------------------------------------------------------------- #
# PyQt5 Documentation : https://doc.qt.io/qtforpython-5/PySide2/QtMultimedia/QMediaPlayer.html   #
# Book for reference  : "Create GUI Applications with Python&Qt5" by Martin Fitzpatrick          #
##################################################################################################


class Window(QMainWindow):
    def __init__(self, parent=None, border=None):
        super(Window, self).__init__(parent)
        self.resize(860, 600)
        self.setWindowTitle('Chitram Media Player')
        self.setWindowIcon(QIcon(':/icons/wicon_64x64.ico'))
        self.ui_init()

    # --- Mediaplayer UI ---- #
    def ui_init(self):
        # ---- Creating Menu bar Objects ---- #
        menu = self.menuBar()
        file = menu.addMenu("File")
        file.addAction("Open File")
        file.triggered[QAction].connect(self.open_file)

        # ---- Creating Media Objects ---- #
        self.mediaPlayer = QMediaPlayer()
        self.playlist    = QMediaPlaylist()
        self.mediaPlayer.setPlaylist(self.playlist)

        self.videoItem = QGraphicsVideoItem()
        self.videoItem.setAspectRatioMode(Qt.KeepAspectRatio)

        scene = QGraphicsScene(self)
        graphicsView = QGraphicsView(scene)
        graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scene.addItem(self.videoItem)

        self.mediaPlayer.setVideoOutput(self.videoItem)
        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

        # ----- Creating Playlist QListView widget ------ #
        self.playlistView = QListView()
        self.playlistView.setAlternatingRowColors(True)
        self.playlistView.setUniformItemSizes(True)

        self.model = PlaylistModel(self.playlist)
        self.playlistView.setModel(self.model)
        self.playlist.currentIndexChanged.connect(self.playlist_position_changed)

        selection_model = self.playlistView.selectionModel()
        selection_model.selectionChanged.connect(self.playlist_selection_changed)
        self.playlistView.doubleClicked.connect(self.ply)

        self.p_play = QPushButton("  Play Now ")
        self.p_play.setStyleSheet('background-color: rgb(32, 32, 32)')
        self.p_play.setEnabled(False)
        self.p_play.clicked.connect(self.ply)

        self.rm = QPushButton(" Remove ")
        self.rm.setToolTip('Remove Item from Playlist')
        self.rm.setStyleSheet('background-color: rgb(32, 32, 32)')
        self.rm.setEnabled(False)
        self.rm.clicked.connect(self.remove)

        self.playback_Label = QLabel("")
        self.playback_Label.setToolTip('Playback Mode')
        self.playback_Label.setFixedWidth(200)
        self.playback_Label.setStyleSheet("color: silver;""border-style: solid;""border-width: 1px;""border-color: rgba(250, 128, 114, 95);""border-radius: 10px")
        self.playback_Label.setAlignment(Qt.AlignCenter)
        self.playback_Label.setText("Current Playlist is in Loop Off")

        # ----- Creating time progress widgets ------ #
        self.currentTimeLabel = QLabel()
        self.currentTimeLabel.setMinimumSize(80, 0)
        self.currentTimeLabel.setAlignment(Qt.AlignCenter)
        self.currentTimeLabel.setText(hhmmss(0))

        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 0)
        self.time_slider.sliderMoved.connect(self.set_position)

        self.totalTimeLabel = QLabel()
        self.totalTimeLabel.setMinimumSize(80, 0)
        self.totalTimeLabel.setAlignment(Qt.AlignCenter)
        self.totalTimeLabel.setText(hhmmss(0))

        # ------ Creating Control widgets ---------- #
        self.plist = QPushButton(" Playlist")
        self.plist.setIcon(QIcon(":/icons/plist.png"))
        self.plist.setToolTip("Show Playlist")
        self.plist.clicked.connect(self.plistview)
        self.plist.installEventFilter(self)

        self.previous = QPushButton(" Prev")
        self.previous.setIcon(QIcon(":/icons/previous.png"))
        self.previous.pressed.connect(self.playlist.previous)
        self.previous.setEnabled(False)
        self.previous.installEventFilter(self)

        self.next = QPushButton(" Next")
        self.next.setIcon(QIcon(":/icons/next.png"))
        self.next.pressed.connect(self.playlist.next)
        self.next.setEnabled(False)
        self.next.installEventFilter(self)

        self.skip_back = QPushButton()
        self.skip_back.setIcon(QIcon(":/icons/skip_back.png"))
        self.skip_back.setToolTip('Skip 5 sec backward')
        self.skip_back.setEnabled(False)
        self.skip_back.clicked.connect(self.backward)
        self.skip_back.installEventFilter(self)

        self.play = QPushButton()
        self.play.setIcon(QIcon(":/icons/play.png"))
        self.play.setToolTip("Play/Pause")
        self.play.setEnabled(False)
        self.play.pressed.connect(self.play_video)

        self.stop = QPushButton()
        self.stop.setIcon(QIcon(":/icons/stop.png"))
        self.stop.setToolTip("Stop")
        self.stop.setEnabled(False)
        self.stop.pressed.connect(self.mediaPlayer.stop)
        self.stop.installEventFilter(self)

        self.skip_forward = QPushButton()
        self.skip_forward.setIcon(QIcon(":/icons/skip_frwd.png"))
        self.skip_forward.setToolTip('Skip 5 sec forward')
        self.skip_forward.setEnabled(False)
        self.skip_forward.clicked.connect(self.forward)
        self.skip_forward.installEventFilter(self)

        self.playback = QPushButton("")
        self.playback.setIcon(QIcon(":/icons/loop_off.png"))
        self.playback.setToolTip(" Playback Mode ")
        self.playback.clicked.connect(self.playback_mode)
        self.playback.setEnabled(False)
        self.playback.installEventFilter(self)

        self.mute = QPushButton()
        self.mute.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.mute.clicked.connect(self.mute_fn)
        self.mute.installEventFilter(self)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setProperty('value', 50)
        self.volume_slider.valueChanged.connect(self.mediaPlayer.setVolume)


        self.aspr = QPushButton()
        self.aspr.setIcon(QIcon(":/icons/aspr.png"))
        self.aspr.setStyleSheet('border-radius: 5px ;''background-color:#626262')
        self.aspr.setToolTip("Aspect Ratio")
        self.aspr.setCheckable(True)
        self.aspr.setEnabled(False)
        self.aspr.toggled.connect(self.aspRatio)
        self.aspr.installEventFilter(self)

        # --- playback speed ----#
        self.pb_speed = QPushButton("1x")
        self.pb_speed.setToolTip("Playback Speed")
        self.pb_speed.setFixedWidth(50)
        self.pb_speed.setEnabled(False)
        self.menu = QMenu()
        self.menu.addAction("0.25x")
        self.menu.addAction("0.5x")
        self.menu.addAction("0.75x")
        self.menu.addAction("1x       Normal")
        self.menu.addAction("1.25x")
        self.menu.addAction("1.5x")
        self.menu.addAction("1.75x")
        self.menu.addAction("2x")
        self.menu.addAction("2.25x")
        self.menu.addAction("2.5x")
        self.menu.addAction("2.75x")
        self.menu.addAction("3x")
        self.menu.triggered.connect(self.playback_speed)
        self.pb_speed.setMenu(self.menu)


        # ------------ Setting widgets and Layout ---------- #
        self.vbox   = QVBoxLayout()
        self.hbox_1 = QHBoxLayout()
        self.hbox_2 = QHBoxLayout()
        # -- Group box widget -- #
        self.gb = QGroupBox()
        self.gb.setStyleSheet('border-radius: 10px ;''background-color:rgba(42, 42, 42, 90)')
        # -- hbox_1 layout contains time slider and timing labels #
        self.hbox_1.addWidget(self.currentTimeLabel)
        self.hbox_1.addWidget(self.time_slider)
        self.hbox_1.addWidget(self.totalTimeLabel)
        # -- hbox_2 layout contains control widgets in a group box --#
        self.hbox_2.setSpacing(20)
        self.hbox_2.addWidget(self.plist)
        self.hbox_2.addSpacing(20)
        self.hbox_2.addWidget(self.previous)
        self.hbox_2.addWidget(self.next)
        self.hbox_2.addStretch()
        self.hbox_2.addWidget(self.skip_back)
        self.hbox_2.addWidget(self.play)
        self.hbox_2.addWidget(self.stop)
        self.hbox_2.addWidget(self.skip_forward)
        self.hbox_2.addSpacing(5)
        self.hbox_2.addWidget(self.playback)
        self.hbox_2.addStretch()
        self.hbox_2.addWidget(self.mute)
        self.hbox_2.addWidget(self.volume_slider)
        #self.hbox_2.addStretch()
        self.hbox_2.addWidget(self.pb_speed)
        self.hbox_2.addWidget(self.aspr)

        self.gb.setLayout(self.hbox_2)

        self.stack1 = QWidget()
        self.stack2 = QWidget()

        # ------------ stack 1 hbox_3 ------------ #
        self.hbox_3 = QHBoxLayout()
        self.hbox_3.addWidget(graphicsView)
        self.stack1.setLayout(self.hbox_3)

        #-------------- stack 2 vbox_2 ---------- #
        self.hbox_4 = QHBoxLayout()
        self.hbox_4.addStretch(2)
        self.hbox_4.addSpacing(150)
        self.hbox_4.addWidget(self.playback_Label)
        self.hbox_4.addStretch(1)
        self.hbox_4.addWidget(self.p_play)
        self.hbox_4.addSpacing(2)
        self.hbox_4.addWidget(self.rm)
        self.hbox_4.addStretch(1)
        self.hbox_4.setAlignment(Qt.AlignCenter)
        self.vbox_2 = QVBoxLayout()
        self.vbox_2.addWidget(self.playlistView)
        self.vbox_2.addLayout(self.hbox_4)
        self.stack2.setLayout(self.vbox_2)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.stack1)
        self.stack.addWidget(self.stack2)

        self.vbox.addWidget(self.stack)
        self.vbox.addLayout(self.hbox_1)
        self.vbox.addWidget(self.gb)
        self.vbox.setAlignment(Qt.AlignBottom)
        # -- set vbox layout to main window  -- #
        widget = QWidget()
        widget.setLayout(self.vbox)
        self.setCentralWidget(widget)
    # --- end of UI function ----#

    # ---- Function to Resize video display --- #
    def resizeEvent(self, event):
        #print("W", self.width(), "H", self.height())
        h = self.height() - 125
        w = self.width() - 26
        self.videoItem.setSize(QSizeF(w, h))

    # --- Function to Open files and add them to playlist --- #
    def open_file(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Open Video", "", "*.mp4 *.3gp *.mkv, *.avi *.mov *.mp3 *.wav *.wma *.wmv *.flac *.3g2 *.m4a *.m4v *.aac *.asf *.3gpp';;All Files (*.*)") #
        filetype = ['.mp4', '.3gp', '.mkv', '.avi', '.mov', '.mp3', '.wav', '.wma', '.wmv', '.flac', '.3g2', '.m4a', '.m4v', '.aac', '.asf', '.3gpp', '.flv']
        #filetype_caps = ['.MP4', '.3GP', '.MKV', '.AVI', '.MOV', '.MP3', '.WAV', '.WMA', '.WMV', '.FLAC', '.3G2', '.M4A', '.M4V', '.AAC', '.ASF', '.3GPP', '.FLV']
        if filenames:
            for file in filenames:
                if any(x in file for x in filetype):
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(file)))
                else:
                    pass

        self.mediaPlayer.play()
        self.model.layoutChanged.emit()

        self.previous.setEnabled(True)
        self.next.setEnabled(True)
        self.skip_back.setEnabled(True)
        self.play.setEnabled(True)
        self.stop.setEnabled(True)
        self.skip_forward.setEnabled(True)
        self.playback.setEnabled(True)
        self.pb_speed.setEnabled(True)
        self.aspr.setEnabled(True)
        self.p_play.setEnabled(True)
        self.rm.setEnabled(True)

    # --- Function to play the selected file from playlist --- #
    def ply(self):
        self.playlist.setCurrentIndex(self.i)
        self.mediaPlayer.play()

    # --- Function to Remove the selected file from playlist --- #
    def remove(self):
        self.playlist.removeMedia(self.i)
        self.model.layoutChanged.emit()

    def playlist_selection_changed(self, ix):
        # We receive a QItemSelection from selectionChanged.
        self.i = ix.indexes()[0].row()

    def playlist_position_changed(self, i):
        if i > -1:
            ix = self.model.index(i)
            self.playlistView.setCurrentIndex(ix)

    # -- Function to switch between Playlist view and Video view ---- #
    def plistview(self):
        if self.stack.currentIndex() == 0:
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)

    # -- Function to change aspect ratio -- #
    def aspRatio(self):
        if self.aspr.isChecked():
            self.videoItem.setAspectRatioMode(Qt.KeepAspectRatio)
        else:
            self.videoItem.setAspectRatioMode(Qt.IgnoreAspectRatio)

    #-- Function to select playback speed --- #
    def playback_speed(self, action):
        #print("triggred : ", action.text())
        if action.text() == "1x       Normal":
            self.mediaPlayer.setPlaybackRate(1.0)
            self.pb_speed.setText("1x")
        elif action.text() == "0.25x":
            self.mediaPlayer.setPlaybackRate(0.25)
            self.pb_speed.setText("0.25x")
        elif action.text() == "0.5x":
            self.mediaPlayer.setPlaybackRate(0.5)
            self.pb_speed.setText("0.5x")
        elif action.text() == "0.75x":
            self.mediaPlayer.setPlaybackRate(0.75)
            self.pb_speed.setText("0.75x")
        elif action.text() == "1.25x":
            self.mediaPlayer.setPlaybackRate(1.25)
            self.pb_speed.setText("1.25x")
        elif action.text() == "1.5x":
            self.mediaPlayer.setPlaybackRate(1.5)
            self.pb_speed.setText("1.5x")
        elif action.text() == "1.75x":
            self.mediaPlayer.setPlaybackRate(1.75)
            self.pb_speed.setText("1.75x")
        elif action.text() == "2x":
            self.mediaPlayer.setPlaybackRate(2.0)
            self.pb_speed.setText("2x")
        elif action.text() == "2.25x":
            self.mediaPlayer.setPlaybackRate(2.25)
            self.pb_speed.setText("2.25x")
        elif action.text() == "2.5x":
            self.mediaPlayer.setPlaybackRate(2.5)
            self.pb_speed.setText("2.5x")
        elif action.text() == "2.75x":
            self.mediaPlayer.setPlaybackRate(2.75)
            self.pb_speed.setText("2.75x")
        elif action.text() == "3x":
            self.mediaPlayer.setPlaybackRate(3.0)
            self.pb_speed.setText("3x")
        else:
            self.mediaPlayer.setPlaybackRate(1.0)

    # -- Function to select playback mode  --- #
    def playback_mode(self):
        if self.playlist.playbackMode() == QMediaPlaylist.Sequential:
            #print("playback mode changed to Loop")
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
            self.playback.setIcon(QIcon(":/icons/loop_on.png"))
            self.playback_Label.setText(" Current Playlist is in Loop")

        elif self.playlist.playbackMode() == QMediaPlaylist.Loop:
            #print("playback mode changed to item loop")
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
            self.playback.setIcon(QIcon(":/icons/item_loop.png"))
            self.playback_Label.setText(" Current Item is in Loop")

        elif self.playlist.playbackMode() == QMediaPlaylist.CurrentItemInLoop:
            #print("playback mode changed to Random")
            self.playlist.setPlaybackMode(QMediaPlaylist.Random)
            self.playback.setIcon(QIcon(":/icons/shuffle_on.png"))
            self.playback_Label.setText(" Current Playlist is in Shuffle")

        elif self.playlist.playbackMode() == QMediaPlaylist.Random:
            #print("playback mode changed to Sequntial")
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)
            self.playback.setIcon(QIcon(":/icons/loop_off.png"))
            self.playback_Label.setText(" Current Playlist is in Loop off")

    # --- Function to Play or Pause ----- #
    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    # -- Function to change play/pause icon depending on media state --- #
    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.play.setIcon(QIcon(":/icons/pause.png"))
        else:
            self.play.setIcon(QIcon(":/icons/play.png"))

    def position_changed(self, position):
        self.time_slider.blockSignals(True)
        self.time_slider.setValue(position)
        self.time_slider.blockSignals(False)
        if position >= 0:
            self.currentTimeLabel.setText(hhmmss(position))

    def duration_changed(self, duration):
        self.time_slider.setRange(0, duration)
        if duration >= 0:
            self.totalTimeLabel.setText(hhmmss(duration))

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    # -- Functions to skip 5 sec back and forward --- #
    def backward(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() - 5000)

    def forward(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() + 5000)

    def mute_fn(self):
        if self.mediaPlayer.isMuted():
            self.mediaPlayer.setMuted(False)
            self.mute.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        else:
            self.mediaPlayer.setMuted(True)
            self.mute.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))

    # -- Function to avoid spacebar control over all buttons except for play/pause button
    def eventFilter(self,  widget, event):
        if event.type() == QEvent.KeyPress and widget is self.plist:
            if event.key() == Qt.Key_Space:
                return True
        elif event.type() == QEvent.KeyPress and widget is self.playback:
            if event.key() == Qt.Key_Space:
                return True
        elif event.type() == QEvent.KeyPress and widget is self.p_play:
            if event.key() == Qt.Key_Space:
                return True
        elif event.type() == QEvent.KeyPress and widget is self.rm:
            if event.key() == Qt.Key_Space:
                return True
        elif event.type() == QEvent.KeyPress and widget is self.skip_back:
            if event.key() == Qt.Key_Space:
                return True
        elif event.type() == QEvent.KeyPress and widget is self.stop:
            if event.key() == Qt.Key_Space:
                return True
        elif event.type() == QEvent.KeyPress and widget is self.skip_forward:
            if event.key() == Qt.Key_Space:
                return True
        elif event.type() == QEvent.KeyPress and widget is self.mute:
            if event.key() == Qt.Key_Space:
                return True
        elif event.type() == QEvent.KeyPress and widget is self.aspr:
            if event.key() == Qt.Key_Space:
                return True
        elif event.type() == QEvent.KeyPress and widget is self.pb_speed:
            if event.key() == Qt.Key_Space:
                return True
        elif event.type() == QEvent.KeyPress and widget is self.previous:
            if event.key() == Qt.Key_Space:
                return True
        elif event.type() == QEvent.KeyPress and widget is self.next:
            if event.key() == Qt.Key_Space:
                return True

        return super(Window, self).eventFilter(widget, event)

    # -- Function for shortcut keys -- #
    def keyPressEvent(self, event):
        # --- Keyboard shortcut keys ---#
        if event.key() == Qt.Key_S:
            self.mediaPlayer.stop()
        if event.key() == Qt.Key_A:
            self.backward()
        if event.key() == Qt.Key_D:
            self.forward()
        if event.key() == Qt.Key_Space:
            self.play_video()
        if event.key() == Qt.Key_1:
            self.videoItem.setAspectRatioMode(Qt.KeepAspectRatio)
        if event.key() == Qt.Key_2:
            self.videoItem.setAspectRatioMode(Qt.IgnoreAspectRatio)
        if event.key() == Qt.Key_M:
            self.mute_fn()
        if event.key() == Qt.Key_P:
            self.plistview()
        if event.key() == Qt.Key_V:
            self.playlist.previous()
        if event.key() == Qt.Key_N:
            self.playlist.next()
        if event.key() == Qt.Key_Plus:
            self.volume_slider.setValue(self.volume_slider.value() + 2)
        if event.key() == Qt.Key_Minus:
            self.volume_slider.setValue(self.volume_slider.value() - 2)


class PlaylistModel(QAbstractListModel):
    def __init__(self, playlist, *args, **kwargs):
        super(PlaylistModel, self).__init__(*args, **kwargs)
        self.playlist = playlist

    def data(self, index, role):
        if role == Qt.DisplayRole:
            media = self.playlist.media(index.row())
            return media.canonicalUrl().fileName()

    def rowCount(self, index):
        return self.playlist.mediaCount()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # ------- Dark theme color settings --------------- #
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(16, 16, 16))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(65, 65, 65))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid silver; }")
    # ---- Create window object --------- #
    mp = Window()
    mp.show()
    sys.exit(app.exec_())


def hhmmss(ms):
    # --- function to convert from milliseconds to hh:mm:ss
    s = round(ms / 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return ("%d:%02d:%02d" % (h, m, s)) if h else ("%d:%02d" % (m, s))

if __name__ == '__main__':
    # ---- for Windows OS the preferred plugin to support media files -- #
    os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'
    main()
