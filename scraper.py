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

def process_artist(artist):
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

def process_title(title):
	# strip apostrophes
	if '\'' in title:
		title = re.sub('\'', '', title)
	if '.' in title:
		title = re.sub('.', '', title)
	return title

def scrape_billboard():
	url = "http://www.billboard.com/charts/hot-100"
	http = urllib3.PoolManager()
	request_main = http.request('GET', url)
	soup_main = BeautifulSoup(request_main.data, "lxml")
	blocks = soup_main.find_all("div", class_="chart-row__title")
	songs = []
	for i, block in enumerate(blocks):
		title = block.find("h2", class_="chart-row__song").text
		a_tag = block.find("a")
		artist = None
		if a_tag is not None: 
			artist = a_tag.text.lstrip().rstrip() 
		else: 
			artist = block.find("h3").text.lstrip().rstrip()
		pTitle = process_title(title)
		pArtist = process_artist(artist)
		songs.append(Song(process_title(title), process_artist(artist), i+1))
	return songs

def scrape_lyrics(songs):
	lyrics = []
	headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
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

def scrape_dummy():

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

def scrape_new(songs):
	lyrics_list = []
	no_urls = 0
	false_urls = 0
	for s in songs:
		time.sleep(7)
		headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36' }
		print(s.title, s.artist)
		# metro structure
		try:
			metro = "http://www.metrolyrics.com/" + '-'.join(s.title.split()) + "-lyrics-" + '-'.join(s.artist.split()) + ".html"
			print(metro)
			r = urllib.request.Request(metro, data=None, headers=headers)
			page = urllib.request.urlopen(r)
			soup = BeautifulSoup(page, "lxml")
			lyrics = soup.find("div", {"id": "lyrics-body-text"})
			if lyrics:
				processed = re.sub('\n', '. ', lyrics.text)
				lines = processed.split()
				lyrics_list.append(lines)
			else:
				print("Wrong Format?")
				false_urls += 1
		except URLError:
			print("BAD URL")
			no_urls += 1
		#r = requests.get('http://www.azlyrics.com/lyrics/edsheeran/theateam.html', headers=headers)
		#page = urlopen(r).read()
		"""
		soup = BeautifulSoup(page.read(), "lxml")
		content_div = soup_az.find("div", class_="col-xs-12 col-lg-8 text-center")
		lyric_div = content_div.find("div", class_=None)
		# change line break tag to dots
		processed = re.sub('<br\s*?>', '.', lyric_div.text)
		lines = processed.split()
		return lines
		"""
	print("URLs Failed: ", no_urls)

if __name__ == "__main__":
	songs = scrape_billboard()
	scrape_new(songs)
	#scrape_lyrics(songs)
	#print(scrape_dummy())

