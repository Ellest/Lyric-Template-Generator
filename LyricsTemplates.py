from collections import defaultdict, deque
from Song import Song
import re
import random

class LyricsTemplates:

	def __init__(self, songs, thrsh, lines):
		self.songs = songs
		self.frequency = defaultdict(list)
		self.states = defaultdict(set)
		self.end_states = set()
		self.data_dir = 'data/'
		# 7 word threshold for each sentence
		# after 7 words, look for the closest word that ends the sentence
		self.sentence_threshold = thrsh
		self.lines_param = lines
		self.generate_states()
		self.template = self.lyric_generator()
		
	def file_path(self, song):
		"""
		Returns the file name associated with a song under a predetermined schema

		:param song: Song object to obtain a file path for
		:returns: file path
		"""
		return self.data_dir + '_'.join(song.artist.split() + song.title.split()) + '.txt'

	def process_word(self, word):
		"""
		Modifies raw text into a word format we can use as states

		:param word: word to modify
		:return: modified word that represents a state
		"""
		word = re.sub('[,.()]', '', word)
		return word.lower()

	def link_states(self, s1, s2):
		self.frequency[s1].append(s2)
		self.states[s1].add(s2)

	def generate_states(self):
		"""
		Generates a states graph given a Song object

		:param song: Song object to extract states from 
		:returns: None
		"""
		for song in self.songs:
			file = self.file_path(song)
			with open(file) as f:
				last = None
				for line in f:			
					words = [self.process_word(w) for w in line[:-1].split()]
					if words:
						if last: 
							self.link_states(last, words[0])
						self.end_states.add(words[-1])
						for i in range(1, len(words)):
							self.link_states(words[i-1], words[i])
						last = words[-1]

	def find_end(self, state):
		"""
		Finds the closest end state from a state. Uses a BFS

		:param state: the starting state 
		:returns: the closest end state 
		"""
		visited = set()
		queue = deque([(state, [state])])
		while queue:
			state, path = queue.popleft()
			for s in self.states[state]:
				if s not in visited:
					_path = path + [s]
					if s in self.end_states: return _path
					queue.append((s, _path))
					visited.add(s)

	def get_random_state(self):
		S = list(self.states.keys())
		return S[random.randint(1, len(S))-1]

	def next_state(self, state):
		if state in self.states:
			return self.frequency[state][random.randint(1, len(self.frequency[state]))-1]

	def lyric_generator(self):
		lines = []
		last = None
		while len(lines) != self.lines_param:
			state = self.get_random_state() if not last else self.next_state(last)
			line = [state]
			while len(line) != self.sentence_threshold and state not in self.end_states:
				state = self.next_state(state)
				line.append(state)
			if state not in self.end_states:
				line.pop()
				line += self.find_end(state)
			lines.append(line)
		return lines



s = Song('give me love', 'ed sheeran', 1)
songs = [s]
LT = LyricsTemplates(songs, 7, 15)
print(LT.states)
print('-----------------------------------------------')
print(LT.end_states)
print('-----------------------------------------------')
for line in LT.template:
	print(' '.join(line))


		


		