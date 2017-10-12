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

"""
This is the main scraper class. It can be thought of as a well behaved scraping
bot that scrapes song lyrics of websites. Checks if the website exists by using
a head request and only scrapes when the exact url is found as redirections are)
frequent.

"""

class Scraper:

	def __init__(self, path):
		self._lyrics_list = []
		self._songs = []
		self._path = path + '/'

	def process_artist(self, artist):
		"""
		Cleans string format to extract user info.

		:returns: string
		"""
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
		"""
		Cleans string format to extract title info.

		:returns: string
		"""
		# strip apostrophes
		if '\'' in title:
			title = re.sub('\'', '', title)
		if '.' in title:
			title = re.sub('.', '', title)
		return title

	def scrape_billboard(self):
		"""
		Method that handles scraping billboard's hot 100. Updates instance variables 
		to store list of top songs 

		:returns: void
		"""
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

	def scrape_layer(self):
		"""
		Scrapes through multiple sites if one a url didn't exist for a site.

		:returns: void 
		"""
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
		"""
		Main method for scraping and parsing data. First checks if the url exists. 
		If it does we scrape the potential url corresponding to the song, then 
		prints the lyrics for the users

		:returns: void
		"""
		no_urls = 0
		false_urls = 0
		for i, song in enumerate(self._songs):
			headers = { 
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36' 
				}
			# metro structure
			metro = "http://www.metrolyrics.com/" + '-'.join(song.title.split()) + "-lyrics-" + '-'.join(song.artist.split()) + ".html"
			request = requests.head(metro) # check if site exists
			if request.status_code == 301: # 301 == moved permanantely (new url exists)
				r = urllib.request.Request(metro, data=None, headers=headers)
				page = urllib.request.urlopen(r)
				soup = BeautifulSoup(page, "lxml")
				lyric_body = soup.find("div", {"id": "lyrics-body-text"})
				verses = lyric_body.find_all("p", class_='verse')
				if verses:
					dir = self._path + song.song_file
					self.write_to_file_obj(dir, verses)
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
		"""
		Helper function for writing a BeautifulSoup obj to a file

		:returns: void
		"""
		if not os.path.exists(dir):
			with open(dir, 'a') as f:
				for obj in soup_obj:
					#print(verse.text)
					f.write(obj.text)
				f.write('\n') # last line missing line break

	def get_lyrics(self):
		"""
		Returns the lyrics list.

		:returns: void
		"""
		return self._lyrics_list

	def print_lyrics(self):
		"""
		Prints the lyrics list.

		:returns: void
		"""
		print(self._lyrics_list)

	def print_songs(self):
		"""
		Prints the list of all songs successfully parsed from billboard's hot 100

		:returns: void
		"""
		for i,s in enumerate(self._songs):
			print('{0}. {1}'.format(i, s.print_info()))

if __name__ == "__main__":
	scraper = Scraper()
	scraper.scrape_billboard()
	scraper.print_lyrics()
	

