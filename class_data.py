import random

import mutagen
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtCore import QUrl

DEFAULT_NAME = "Unknown"
DEFAULT_DISK = [":/disk_1.jpg", ":/disk_2.jpg"]

class Song:
	def __init__(self, url):
		self.url    = url
		info        = mutagen.File(url)
		self.song   = QMediaContent(QUrl.fromLocalFile(url))

		if ".mp3" in url:
			try:
				self.artist = info["TPE1"].text[0]
			except:
				self.artist = DEFAULT_NAME
			try:
				self.title = info["TIT2"].text[0]
			except:
				self.title = DEFAULT_NAME
			self.image = random.choice(DEFAULT_DISK)

		elif ".flac" in url:
			try:
				self.artist = ",".join(info["artist"])
			except:
				self.artist = DEFAULT_NAME
			try:
				self.title = info["title"][0]
			except:
				self.title = DEFAULT_NAME
			try:
				a = mutagen.flac.FLAC(url)
				self.image = a.pictures[0].data
			except:
				self.image = random.choice(DEFAULT_DISK)
			
		elif ".wma" in url:
			try:
				self.artist = str(info["Author"][0])
			except:
				self.artist = DEFAULT_NAME
			try:
				self.title = str(info["Title"][0])
			except:
				self.title = DEFAULT_NAME
			self.image = random.choice(DEFAULT_DISK)
			

class playList:
	def __init__(self):
		self.__list    = []
		self.extension = [".mp3", ".flac", ".wma"]

	def append(self, songIn):
		for song in self.__list:
			if song.url == songIn.url:
				self.__list.remove(song)
		self.__list.append(songIn)

	def pre(self, songIn):
		for c, song in enumerate(self.__list):
			if song.url == songIn.url:
				return self.__list[(c-1)%len(self.__list)]

	def next(self, songIn):
		for c, song in enumerate(self.__list):
			if song.url == songIn.url:
				return self.__list[(c+1)%len(self.__list)]
