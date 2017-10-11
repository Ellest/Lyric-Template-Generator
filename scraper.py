from bs4 import BeautifulSoup, NavigableString, Tag
import urllib3
import requests
import http.client
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import re
import ssl
import certifi
from selenium import webdriver
import time
import urllib.request
from Song import Song
import os
import sys
import traceback

class Scraper:

	def __init__(self, path):
		self._lyrics_list = []
		self._songs = []
		self._path = path + '/'

	def process_artist(self, artist):
		# stripping featured artists. Most lyric sites have lyrics listed under main artist
		if "Featuring" in artist:
			artist = artist[:artist.index("Featuring")]
		# looking for '&' to reduce artist name to singular from composite
		if " & " in artist:
			artist = artist[:artist.index(" & ")]
		# collab sign seems to be A x B
		if " x " in artist:
			artist = artist[:artist.index(" x ")]
		return artist

	def process_title(self, title):
		# strip apostrophes
		if '\'' in title:
			title = re.sub('\'', '', title)
		if '.' in title:
			title = re.sub('.', '', title)
		return title

	def scrape_billboard(self):
		# url of hot 100 on billboard
		url = "http://www.billboard.com/charts/hot-100"
		http = urllib3.PoolManager()
		request_main = http.request('GET', url)
		soup_main = BeautifulSoup(request_main.data, "lxml")
		blocks = soup_main.find_all("div", class_="chart-row__title")
		for i, block in enumerate(blocks):
			title = block.find("h2", class_="chart-row__song").text
			a_tag = block.find("a")
			artist = None
			if a_tag is not None: 
				artist = a_tag.text.lstrip().rstrip() 
			else: 
				artist = block.find("span").text.lstrip().rstrip()
			pTitle, pArtist = self.process_title(title), self.process_artist(artist)
			self._songs.append(Song(pTitle, pArtist, i+1))

	def scrape_lyrics(self, songs):
		lyrics = []
		headers = { 
					'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' 
				  }
		for s in songs:
			time.sleep(5)
			#print (s.title, s.artist)
			# AZLyrics www.azlyrics.com/<artist>/<song title>
			az = "http://www.azlyrics.com/lyrics/" + ''.join(s.artist.split()).lower() + "/" + ''.join(s.title.split()).lower() + ".html"
			print(az)
			# azlyrics structure
			try:
				r = urllib3.Request(az, headers = headers)
				page = urlopen(az, headers = headers)
				soup_az = BeautifulSoup(page.read(), "lxml")
				content_div = soup_az.find("div", class_="col-xs-12 col-lg-8 text-center")
				lyric_div = content_div.find("div", class_=None)
				# change line break tag to dots
				processed = re.sub('<br\s*?>', '.', lyric_div.text)
				lines = processed.split()
				lyrics.append(lines)
				continue
			except URLError: # if no url or other connection errors, skip
				print("no url")
				pass
			# Metrolyrics www.metrolyrics.com/<song title>-lyrics-<name>.html
			metro = "http://www.metrolyrics.com/" + '-'.join(s.title.split()) + "-lyrics-" + '-'.join(s.artist.split()) + ".html"
			# Genius Lyrics https://genius.com/<artist>-<song title>-lyrics
			genius = "https://genius.com/" + '-'.join(s.artist.split()) + "-" + '-'.join(s.title.split()) + "-lyrics"

			#http = urllib3.PoolManager()
			#request_az = http.request('GET', az)

	def scrape_dummy(self):

		# azlyrics structure
		try:
			#page = urlopen('http://www.azlyrics.com/lyrics/edsheeran/theateam.html')
			page = urlopen('http://www.azlyrics.com/lyrics/edsheeran/theteam.html')
			soup = BeautifulSoup(page.read(), "lxml")
			content_div = soup_az.find("div", class_="col-xs-12 col-lg-8 text-center")
			lyric_div = content_div.find("div", class_=None)
			# change line break tag to dots
			processed = re.sub('<br\s*?>', '.', lyric_div.text)
			lines = processed.split()
			return lines
		except URLError: # if no url or other connection errors, skip
			print("no url")
			pass

		# MetroLyrics structure
		try:
			#page = urlopen('http://www.metrolyrics.com/a-team-lyrics-ed-sheeran.html')
			page = urlopen('http://www.metrolyrics.com/aheeran.html')
			soup = BeautifulSoup(page.read(), "lxml")
			lyrics = soup.find("div", {"id": "lyrics-body-text"})
			processed = re.sub('\n', '. ', lyrics.text)
			lines = processed.split()
			return lines
		except URLError: # if no url or other connection errors, skip
			print("no url")
			pass

		# Genius Lyrics structure
		try:
			#page = urlopen('https://genius.com/Ed-sheeran-the-a-team-lyrics')
			url = 'https://genius.com/Ed-sheeran-the-a-team-lyrics'
			client = webdriver.PhantomJS()
			client.get(url)
			soup = BeautifulSoup(client.page_source, 'lxml')
			lyrics_div = soup.find("div", class_="lyrics")
			lyrics_content = lyrics_div.find("p")
			#print(lyrics_content)
			lyrics_a = lyrics_content.find_all("a")
			lines = []
			for obj in lyrics_a:
				for c in obj.contents:
					if len(c) > 0: lines.append(c + '.')			
			return lines
			#lyrics_list.append(c)
			#print(lyrics_list)
		except URLError:
			print("no url")
			pass

		# Song Lyrics structure IMPLEMENT THIS -------------------------------------------
		try:
			pass
		except URLError:
			print("no url")

	def scrape_new(self):
		no_urls = 0
		false_urls = 0
		for i, song in enumerate(self._songs):
			headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36' }
			print(song.title, song.artist)
			# metro structure
			metro = "http://www.metrolyrics.com/" + '-'.join(song.title.split()) + "-lyrics-" + '-'.join(song.artist.split()) + ".html"
			print(metro)
			request = requests.head(metro)
			if request.status_code == 301:
				r = urllib.request.Request(metro, data=None, headers=headers)
				page = urllib.request.urlopen(r)
				soup = BeautifulSoup(page, "lxml")
				lyric_body = soup.find("div", {"id": "lyrics-body-text"})
				verses = lyric_body.find_all("p", class_='verse')
				if verses:
					#print(verses[0])
					#lines = []
					dir = self._path + song.song_file
					self.write_to_file_obj(dir, verses)
					#print(self.song_file_to_list(dir))
					"""
					for verse in verses:
						try:
							processed = re.sub('\n', '.^', verse.text)
							processed = processed.split('^')
							if processed and processed[0] == '.':
								processed = processed[1:]
							lines.extend(processed)
						except:
							print('regex error')
					"""
					#self.write_to_file(lines, song.title, song.artist)
					#self._lyrics_list.append(lines)
					#print(lines)
				else:
					print("Wrong Format?")
					false_urls += 1
			else:
				print("BAD URL")
				no_urls += 1
			if i != len(self._songs)-1: 
				time.sleep(7) # set timeout to not overburdden the server
		print("URLs Failed: ", no_urls)

	def write_to_file_obj(self, dir, soup_obj):
		print(dir)
		if not os.path.exists(dir):
			with open(dir, 'a') as f:
				for obj in soup_obj:
					#print(verse.text)
					f.write(obj.text)
				f.write('\n') # last line missing line break

	def write_to_file(self, lines, title, artist):
		dir = self._path + title + '_' + artist + '.txt'
		print(dir)
		with open(dir, 'a') as f:
			for l in lines:
				f.write(l)

	def get_lyrics(self):
		return self._lyrics_list

	def print_lyrics(self):
		print(self._lyrics_list)

	def print_songs(self):
		for i,s in enumerate(self._songs):
			print('{0}. {1}'.format(i, s.print_info()))

if __name__ == "__main__":
	scraper = Scraper()
	scraper.scrape_billboard()
	scraper.print_lyrics()
	

