import sys
import math
from time import sleep
from threading import Thread

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *

import image_rc
from class_data import Song, playList


class Disk(QLabel):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.parent    = parent
		self.path      = 130
		self.path_mini = 110
		self.size      = 110
		self.angle     = 0
		self.pix       = QPixmap(":/disk_1.jpg")
		self.zoom      = False
		self.rotate    = False
		self.circle    = QRect(25 + self.size/2, 30 + self.size/2 + 10, 2*10, 2*10)
		
		self.setFixedSize(self.path, self.path)

	def paintEvent(self, e):

		t = QTransform()
		t.translate(self.size/2, self.size/2)
		t.rotate(self.angle)
		t.translate(-self.size/2, -self.size/2)

		beta = math.atan(1/2) + math.radians(self.angle)
		addition = (self.path - self.size)/2
		x_ = addition*math.sqrt(5)*math.sin(beta)
		y_ = addition*math.sqrt(5)*math.cos(beta)

		qp = QPainter(self)
		qp.setTransform(t)
		qp.setRenderHint(QPainter.SmoothPixmapTransform)
		qp.setRenderHint(QPainter.Antialiasing)
		p = self.pix.scaled(self.size, self.size, transformMode=Qt.SmoothTransformation)
		t = QTransform()
		t.translate(x_, y_)
		brush = QBrush(p)
		brush.setTransform(t)
		qp.setBrush(brush)
		qp.setPen(QPen(Qt.transparent))
		qp.drawRoundedRect(QRect(x_, y_, self.size, self.size), self.size/2, self.size/2)

		qp.setBrush(QColor("#fff"))
		qp.setPen(QColor("#fff"))
		qp.setRenderHint(QPainter.Antialiasing)
		r = 10 * (self.size/self.path_mini)
		self.circle = QRect(25 + 130/2 - r, 30 + 2*addition + self.size/2 - r, 2*r, 2*r)
		qp.drawRoundedRect(QRect(x_ + self.size/2 - r, y_ + self.size/2 - r, 2*r, 2*r), r, r)

		super().paintEvent(e)

	def setPixmap(self, image):
		if isinstance(image, bytes):
			p = QPixmap()
			p.loadFromData(image)
			self.pix = p.scaled(self.path, self.path, transformMode=Qt.SmoothTransformation)
		else:
			self.pix = QPixmap(image)

	def switchRotate(self):
		self.rotate = not self.rotate

	def switchMode(self):
		self.zoom = not self.zoom

class subButton(QWidget):
	clicked = pyqtSignal()

	def __init__(self, image):
		super().__init__()
		self.setFixedSize(80, 80)

		self.lb = QLabel()
		self.pix = QPixmap(":/%s.png"%image)
		self.pix = self.pix.scaled(50, 50, transformMode=Qt.SmoothTransformation)
		self.pix_on = QPixmap(":/%s_on.png"%image)
		self.pix_on = self.pix_on.scaled(50, 50, transformMode=Qt.SmoothTransformation)
		self.lb.setScaledContents(True)
		self.lb.setPixmap(self.pix)
		
		v = QVBoxLayout()
		v.addStretch()
		v.addWidget(self.lb)
		v.addStretch()
		w = QWidget(self)
		w.setFixedSize(80, 80)
		w.setObjectName("contain")
		h = QHBoxLayout(w)
		h.addStretch()
		h.addLayout(v)
		h.addStretch()
		
		self.setStyle("fff")

	def setStyle(self, color):
		self.setStyleSheet("""
			QWidget#contain{
				background-color: #%s;
				border: 1 solid #%s;
				border-radius: 10;
			}
			"""%(color, color))

	def mousePressEvent(self, e):
		self.clicked.emit()

	def enterEvent(self, e):
		self.lb.setPixmap(self.pix_on)
		self.setStyle("DDDEDE")

	def leaveEvent(self, e):
		self.lb.setPixmap(self.pix)
		self.setStyle("fff")
		
class primaryButton(QWidget):
	clicked = pyqtSignal()

	def __init__(self, parent):
		super().__init__()
		self.setFixedSize(80, 80)
		self.parent  = parent
		size = 40

		self.pause    = QPixmap(":/pause.png").scaled(size+10, size+10, transformMode=Qt.SmoothTransformation)
		self.pause_on = QPixmap(":/pause_on.png").scaled(size+10, size+10, transformMode=Qt.SmoothTransformation)
		self.play     = QPixmap(":/play.png").scaled(size, size, transformMode=Qt.SmoothTransformation)
		self.play_on   = QPixmap(":/play_on.png").scaled(size, size, transformMode=Qt.SmoothTransformation)

		self.lb = QLabel()
		self.lb.setScaledContents(True)
		self.lb.setPixmap(self.play)
		
		v = QVBoxLayout()
		v.addStretch()
		v.addWidget(self.lb)
		v.addStretch()
		w = QWidget(self)
		w.setFixedSize(80, 80)
		w.setObjectName("contain")
		h = QHBoxLayout(w)
		h.addStretch()
		h.addLayout(v)
		h.addStretch()
		
		self.setStyle("fff")

	def setStyle(self, color):
		self.setStyleSheet("""
			QWidget#contain{
				background-color: #%s;
				border: 1 solid #%s;
				border-radius: 10;
			}
			"""%(color, color))

	def mousePressEvent(self, e):
		if self.parent.currentSong:
			if self.parent.playing:
				self.lb.setPixmap(self.play_on)
			else:
				self.lb.setPixmap(self.pause_on)

			self.clicked.emit()

	def enterEvent(self, e):
		if self.parent.playing:
			self.lb.setPixmap(self.pause_on)
		else:
			self.lb.setPixmap(self.play_on)

		self.setStyle("DDDEDE")

	def leaveEvent(self, e):
		if self.parent.playing:
			self.lb.setPixmap(self.pause)
		else:
			self.lb.setPixmap(self.play)

		self.setStyle("fff")


class subBar(QWidget):

	def __init__(self, parent):
		super().__init__(parent)
		self.title  = "None"
		self.artist = "None"
		self.length = 0
		self.title_off = 0
		self.artist_off = 0
		self.title_bound = False
		self.artist_bound = False

		self.height = 75
		self.v_length = 200
		self.width  = 400
		self.offset = 75
		self.hide   = True

		self.setFixedSize(self.width, self.height)

	def paintEvent(self, e):
		qp = QPainter(self)
		qp.setPen(QColor("#FFF0F5"))
		qp.setBrush(QColor("#FFF0F5"))
		qp.setRenderHint(QPainter.Antialiasing)
		qp.drawRoundedRect(QRect(0, self.offset + 5, self.width, self.height + 15), 15, 15)
		
		font = QFont()
		font.setFamily("Tahoma")
		font.setPointSize(12)

		qp.setPen(QColor("#0f0f0f"))
		qp.setFont(font)
		qp.drawText(170 - self.title_off, 30 + self.offset, self.title)
		font.setPointSize(9)
		qp.setPen(QColor("#9B9DA1"))
		qp.setFont(font)
		qp.drawText(170 - self.artist_off, 45 + self.offset, self.artist)

		qp.setPen(QColor("#FFF0F5"))
		qp.setBrush(QColor("#FFF0F5"))
		qp.setRenderHint(QPainter.Antialiasing)
		qp.drawRect(15, self.offset + 15, 155, self.height + 15)
		left = 170 + self.v_length
		qp.drawRoundedRect(QRect(left, self.offset + 10, self.width - left + 2, self.height), 15, 15)

		qp.setPen(QColor("#D2D6D7"))
		qp.setBrush(QColor("#D2D6D7"))
		qp.drawRoundedRect(QRect(170, 60 + self.offset, self.v_length, 4), 2, 2)

		self.rect = QRect(185, 60 + self.offset, self.v_length, 16)

		qp.setPen(QColor("#FD6D94"))
		qp.setBrush(QColor("#FD6D94"))
		qp.drawRoundedRect(QRect(170, 60 + self.offset, self.length, 4), 2, 2)
		
		super().paintEvent(e)

	def setLength(self, length):
		self.length = length

	def setInfo(self, title, artist):
		self.title  = title
		self.artist = artist

		font = QFont()
		font.setFamily("Tahoma")
		font.setPointSize(12)
		metrics = QFontMetrics(font)
		title_width = metrics.width(self.title)
		artist_width = metrics.width(self.artist)

		if title_width > self.v_length:
			self.title_bound  = True
			self.title_offset_max = title_width - self.v_length
		else:
			self.title_bound = False
		self.title_off = 0

		if artist_width > self.v_length:
			self.artist_bound  = True
			self.artist_offset_max = artist_width - self.v_length
		else:
			self.artist_bound = False
		self.artist_off = 0

	def switchMode(self):
		self.hide = not self.hide


class volumeBar(QWidget):

	def __init__(self, parent):
		super().__init__(parent)
		self.length   = 90
		self.size     = 3

		self.height   = 30
		self.width    = 140
		self.offset   = -20
		self.hide     = True
		self.alive    = True
		
		self.setFixedSize(self.width, self.height)

	def paintEvent(self, e):
		qp = QPainter(self)
		qp.setPen(QColor("#FFF0F5"))
		qp.setBrush(QColor("#FFF0F5"))
		qp.setRenderHint(QPainter.Antialiasing)
		qp.drawRoundedRect(QRect(0, self.offset - 10, self.width, self.height), 10, 10)
		
		qp.setPen(QColor("#D2D6D7"))
		qp.setBrush(QColor("#D2D6D7"))
		qp.drawRoundedRect(QRect(10, self.offset + 6, self.width - 20, 4), 2, 2)
		self.rect = QRect(230, 180 + self.offset, self.width - 20, 18)

		qp.setPen(QColor("#FD6D94"))
		qp.setBrush(QColor("#FD6D94"))
		qp.drawRoundedRect(QRect(10, self.offset + 6, self.length, 4), 2, 2)
		
		super().paintEvent(e)

	def setLength(self, length):
		self.length = length

	def setInfo(self, title, artist):
		self.title  = title
		self.artist = artist

	def switchMode(self):
		self.hide = not self.hide


class exitLine(QWidget):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent
		self.height = 100
		self.width  = 15
		
		self.setFixedSize(self.width, self.height)

	def enterEvent(self, e):
		self.parent.setCursor(QCursor(Qt.PointingHandCursor))

	def leaveEvent(self, e):
		self.parent.setCursor(QCursor(Qt.ArrowCursor))

	def mousePressEvent(self, e):
		self.parent.close()

	def paintEvent(self, e):
		qp = QPainter(self)
		qp.setPen(QColor("#FD6D94"))
		qp.setBrush(QColor("#FD6D94"))
		qp.setRenderHint(QPainter.Antialiasing)
		qp.drawRoundedRect(QRect(0, 0, 30, 100), 15, 15)
	
		super().paintEvent(e)


class minimalPlayer(QWidget):

	def __init__(self):
		super().__init__()
		self.setWindowFlags(Qt.Window|Qt.FramelessWindowHint|Qt.WindowMinMaxButtonsHint)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.press  = False
		self.oldPos = None
		self.alive  = True
		width       = 425

		self.setFixedSize(width, 200)

		self.player      = QMediaPlayer()
		self.playlist    = playList()
		self.currentSong = None
		self.playing     = False

		self.q = QWidget(self)
		self.q.setFixedSize(width, 200)

		#### SUB BAR ####
		self.sub = subBar(self.q)
		self.sub.setGeometry(15, 5, self.sub.width, self.sub.height + 10)
		#### SUB BAR ####

		#### MAIN BAR ####
		self.bar = QWidget(self.q)
		self.bar.setFixedSize(width, 100)
		self.bar.setObjectName("bar")
		self.bar.setGeometry(0, 80, width, 100)

		previous_btn = subButton("previous")
		play_btn     = primaryButton(self)
		next_btn     = subButton("next")

		layout = QHBoxLayout(self.bar)
		layout.addStretch()
		layout.addWidget(previous_btn)
		layout.addWidget(play_btn)
		layout.addWidget(next_btn)
		#### MAIN BAR ####

		### EXIT ###
		self.exit = exitLine(self)
		self.exit.setGeometry(0, 80, 15, 100)
		### EXIT ###

		#### DISK ####
		self.disk = Disk(self.q)
		radius = self.disk.path_mini
		margin_left = 25
		margin_top = 180 - radius - 40
		self.disk.setGeometry(margin_left, margin_top, radius, radius)
		#### DISK ####

		#### VOLUME ####
		self.volume = volumeBar(self)
		self.volume.setGeometry(220, 180, self.volume.width, self.volume.height - 10)
		#### VOLUME ####

		self.player.positionChanged.connect(self.updateBar)
		next_btn.clicked.connect(self.playNextSong)
		previous_btn.clicked.connect(self.playPreviousSong)
		play_btn.clicked.connect(self.playSong)

		self.Thread = Thread(target=self.target)
		self.Thread.start()

		self.setAcceptDrops(True)
		self.setStyleSheet("""
			QWidget#bar{
				background-color: #fff;
				border: 1 solid #fff;
				border-radius: 15;
			}
			""")

	def target(self):
		delay_t = 30
		delay_a = 30
		while self.alive:
			if self.sub.hide:
				if self.sub.offset < self.sub.height:
					self.sub.offset += 6
				if self.volume.offset > -20:
					self.volume.offset -= 1.5
			else:
				if self.sub.offset > 0:
					self.sub.offset -= 6
				if self.volume.offset < 0:
					self.volume.offset += 1.5

			if self.sub.title_bound:
				if self.sub.title_off < self.sub.title_offset_max:
					if delay_t > 0:
						delay_t -= 1
					else:
						self.sub.title_off += 0.4
				else:
					if delay_t < 30:
						delay_t += 1
					else:
						self.sub.title_off = 0

			if self.sub.artist_bound:
				if self.sub.artist_off < self.sub.artist_offset_max:
					if delay_a > 0:
						delay_a -= 1
					else:
						self.sub.artist_off += 0.4
				else:
					if delay_a < 30:
						delay_a += 1
					else:
						self.sub.artist_off = 0

			if self.disk.rotate:
				self.disk.angle += 1
				if self.disk.angle == 360:
					self.disk.angle = 0

			if self.disk.zoom:
				if self.disk.size < self.disk.path:
					self.disk.size += 2/3
			else:
				if self.disk.size > self.disk.path_mini:
					self.disk.size -= 2/3
			self.update()
			sleep(0.015)

	def updateBar(self):
		if self.player.duration():
			position = self.player.position() / self.player.duration()
			self.sub.setLength(position * self.sub.v_length)
			if position == 1:
				self.playNextSong()

	def playPreviousSong(self):
		if self.currentSong:
			preSong = self.playlist.pre(self.currentSong)
			self.updateSong(preSong)

	def playNextSong(self):
		if self.currentSong:
			nextSong = self.playlist.next(self.currentSong)
			self.updateSong(nextSong)

	def playSong(self):
		if self.currentSong:
			if self.playing:
				self.player.pause()
				self.disk.switchMode()
				self.disk.switchRotate()
			else:
				self.player.play()
				self.disk.switchMode()
				self.disk.switchRotate()
				if self.sub.hide:
					self.sub.switchMode()
					self.volume.switchMode()
			self.playing = not self.playing

	def updateSong(self, song):
		self.currentSong = song
		self.sub.setInfo(song.title, song.artist)
		self.player.setMedia(song.song)
		self.sub.setLength(0)
		self.disk.setPixmap(song.image)
		self.playSong()
		self.playSong()

	def dropEvent(self, e):
		if e.mimeData().hasUrls:
			e.accept()
			for url in e.mimeData().urls():
				for extension in self.playlist.extension:
					if extension in url.toLocalFile():
						self.currentSong = Song(url.toLocalFile())
						self.playlist.append(self.currentSong)
						self.updateSong(self.currentSong)
		else:
			e.ignore()

	def dragEnterEvent(self, e):
		if e.mimeData().hasUrls:
			e.accept()
		else:
			e.ignore()

	def dragMoveEvent(self, e):
		if e.mimeData().hasUrls:
			e.accept()
		else:
			e.ignore()

	def closeEvent(self, e):
		if self.Thread.isAlive():
			self.alive = False
			self.Thread.join()
		e.accept()

	def mousePressEvent(self, e):
		if self.disk.circle.contains(e.pos()):
			self.sub.switchMode()
			self.volume.switchMode()

		elif self.volume.rect.contains(e.pos()):
			self.volume.setLength(e.pos().x() - 230)
			volume = int((e.pos().x() - 230)/(self.volume.width - 20)*100)
			self.player.setVolume(volume)

		elif self.sub.rect.contains(e.pos()):
			if self.player.duration():
				self.sub.setLength(e.pos().x() - 185)
				position = (e.pos().x() - 185)/self.sub.v_length * self.player.duration()
				self.player.setPosition(position)

		else:
			self.press = True
			self.oldPos = e.globalPos()

	def mouseMoveEvent(self, e):
		if self.volume.rect.contains(e.pos()):
			self.volume.setLength(e.pos().x() - 230)
			volume = int((e.pos().x() - 230)/(self.volume.width - 20)*100)
			self.player.setVolume(volume)

		elif self.sub.rect.contains(e.pos()):
			if self.player.duration():
				self.sub.setLength(e.pos().x() - 185)
				position = (e.pos().x() - 185)/self.sub.v_length * self.player.duration()
				self.player.setPosition(position)

		else:
			if self.press:
				delta = QPoint(e.globalPos() - self.oldPos)
				self.move(self.x() + delta.x(), self.y() + delta.y())
				self.oldPos = e.globalPos()

	def mouseReleaseEvent(self, e):
		self.press = False
		self.oldPos = None

				  
if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = minimalPlayer()
	ex.show()
	sys.exit(app.exec_())