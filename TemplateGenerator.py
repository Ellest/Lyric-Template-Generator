from collections import defaultdict, deque
from Song import Song
import re
import random
import os

"""
This is the template generator class. Handles all operations related to generating
the template. Uses a Markov chain where each state is an n-gram of the lyrics. I'v
tried multiple variations, including different n-grams on the character level, but
it seemed using n-grams on a word level generate templates that make the more sense.

"""

class TemplateGenerator:

	def __init__(self, thrsh, lines, pre_state, data_dir):
		self.frequency = defaultdict(list)
		self.states = defaultdict(set)
		self.end_states = set()
		self.data_dir = data_dir + '/'
		# 7 word threshold for each sentence
		# after 7 words, look for the closest word that ends the sentence
		self.sentence_threshold = thrsh
		self.lines_param = lines
		self.pre_state = pre_state
		self.generate_states() # generate states of the markov model
		self._template = None
		self._template = self.generate_lyric_template()

	def process_word(self, word):
		"""
		Modifies raw text into a word format we can use as states

		:param word: word to modify
		:returns: modified word that represents a state
		"""
		word = re.sub('[,.()]', '', word)
		return word.lower()

	def link_states(self, s1, s2):
		"""
		Links two given states together. Creates a mapping in the hashmap (dictionary)

		:returns: void
		"""
		self.frequency[s1].append(s2)
		self.states[s1].add(s2)

	def song_file_to_list(self, dir):
		"""
		Returns a generator to allow iteration over the given dir (if exists).
		This avoid having to load the entire file list into memory.

		:returns: generator
		"""
		for line in open(dir).readlines():
			# modify the string by removing the line break character
			line_alt = re.sub('\n', '.', line)
			if line_alt != '.':
				yield(line_alt)

	def generate_states(self):
		"""
		Generates a states graph given a Song object

		:param song: Song object to extract states from 
		:returns: void
		"""
		for file in os.listdir(self.data_dir):
			line_gen = self.song_file_to_list(os.path.join(self.data_dir, file))
			last = None
			for line in line_gen:
				# removing endline char at end
				words = [self.process_word(w) for w in line[:-1].split()] 
				# if a valid line
				if len(words) > 1:
					# if this line is not the first, the last two words in the 
					# previous line serves as states. 
					if last: 
						self.link_states(last, tuple(words[0:2]))
					self.end_states.add(words[-1])
					# link states
					for i in range(self.pre_state, len(words)):
						self.link_states(tuple(words[i-self.pre_state: i]), words[i])
					last = words[-1]
		"""
		for song in self.songs:
			file = self.file_path(song)
			with open(file) as f:
				last = None
				for line in f:			
					words = [self.process_word(w) for w in line[:-1].split()] # removing endline char at end
					if len(words) > 1:
						state = deque()
						if last: 
							self.link_states(last, tuple(words[0:2]))
						self.end_states.add(words[-1])
						for i in range(self.pre_state, len(words)):
							self.link_states(tuple(words[i-self.pre_state: i]), words[i])
						last = words[-1]
		"""
	def find_end(self, line):
		"""
		Finds the closest end state from a state. Uses a BFS travel to locate
		the closest (or one of the closest) end state.

		:param state: the starting state 
		:returns: the closest end state 
		"""
		visited = set()
		last = line[-2:]
		queue = deque([last])
		while queue:
			path = queue.popleft()
			state = tuple(path[-2:])
			for s in self.states[state]:
				if s not in visited:
					_path = path + [s]
					if s in self.end_states: return _path
					queue.append(_path)
					visited.add(s)

	def get_random_state(self):
		"""
		Generate a random state from the entire pool of states.

		:param state: the starting state 
		:returns: the closest end state 
		"""
		S = list(self.states.keys())
		rand = S[random.randint(1, len(S))-1]
		while rand in self.end_states:
			rand = S[random.randint(1, len(S))-1]
		return rand

	def next_state(self, line):
		"""
		Returns a random state from the pool of valid states following the current line.
		
		:param line: line
		:returns: void
		"""
		prev = tuple(line[-2:]) # grab last two words in the line
		if prev in self.states:
			return random.choice(self.frequency[prev])
			#return self.frequency[prev][random.randint(1, len(self.frequency[prev]))-1]

	def generate_lyric_template(self):
		"""
		Main method for generating lyrics. Utilizes helper functions 

		:returns: string list
		"""
		lines = []
		last = None
		while len(lines) != self.lines_param:
			state = self.get_random_state() if not last else self.next_state(last)
			line = [s for s in state]
			while len(line) != self.sentence_threshold and state not in self.end_states:
				state = self.next_state(line)
				line.append(state)
			if state not in self.end_states:
				line += self.find_end(line)
			lines.append(line)
		return lines

	def print_template(self):
		"""
		Helper function to print the generated lyric template in a legible format.

		:returns: void
		"""
		print("--------------- Generated Template ---------------")
		for line in self._template:
			print(' '.join(line))
		print("--------------------------------------------------")

if __name__ == '__main__':
	# example isolated usage
	threshold = 7
	line_number = 15
	look_back = 2
	LT = TemplateGenerator(threshold, line_number, look_back)
	print(LT.states)
	print('-----------------------------------------------')
	print(LT.end_states)
	print('-----------------------------------------------')
	LT.print_template()


		


		