class Song:
	def __init__(self, title, artist, rank):
		self.title = title
		self.artist = artist
		self.rank = rank
		self.song_file = title + '_' + artist + '.txt'

	def print_info(self):
		return '{0} by {1}: rank {2}'.format(self._title, self._artist, self._rank)