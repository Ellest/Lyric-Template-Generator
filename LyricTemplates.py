import os
import datetime
from Scraper import Scraper
import traceback
from TemplateGenerator import TemplateGenerator

"""
Main class that handles working directories, run histories, and user inputs. 
Maintains a run history and cache scraped lyrics in a folder titled with 
the run date and uses this cached data instead of re-scraping everything if 
the following run is within a week. If last_run.txt is corrupted, deleting this 
file will allow this class to re-create a new file of the right structure 
and use that file to store the run history. 

"""

class LyricsTemplates:

	def __init__(self, threshold, line_number, look_back):
		self._history_file = './data/last_run.txt'
		data_dir = self.try_scrape()
		# generate a TemplateGenerator with given params
		_LT = TemplateGenerator(threshold, line_number, look_back, data_dir)
		_LT.print_template()

	def run_scraper(self, path):
		"""
		Creates a Scraper object and scrapes data through the object
		
		:params path: working directory to save files
		:return: void
		"""
		_scraper = Scraper(path)
		_scraper.scrape_billboard()
		_scraper.scrape_new()

	
	def try_create_dir(self, dir_path):
		"""
		Creates working directory if it doesn't exist.

		:params dir_path: directory to create
		:return: void
		"""
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)

	def try_scrape(self):
		"""
		Checks run history to see if data collection is needed to generate a lyric 
		template. Runs data collection if either run history is void or the last 
		run was more than a week ago.

		:return: string
		"""
		run_date = datetime.date.today()
		run_weekday = run_date.weekday()
		date_string = str(run_date) + "-" + str(run_weekday)
		dir_path = './data/' + date_string
		if os.path.exists(self._history_file):
			with open(self._history_file) as f:
				text = f.read()
			lines = text.split('\n')
			if lines:
				last_run = lines[-1].split('-')
				if len(last_run) == 4:
					# generate date obj
					last_run_date = datetime.date(
										int(last_run[0]),
										int(last_run[1]),
										int(last_run[2])
									)
					weekday = int(last_run[3])
					# date diff
					delta = run_date - last_run_date
					# if more than a week ago. Uses weekday for day comparison
					if abs(delta.days) >= 7 or (delta.days > 0 and weekday > run_weekday) \
						or (delta.days < 0 and weekday < run_weekday):
						# try generator first
						# scrape new data
						run_scraper(dir_path)
						print("Creating new directory for lyrics data")
						try_create_dir(dir_path)
						# new data collection run about to happen. Record in history as most recent
						# run to be checked next time the program is run
						with open(self._history_file, 'a') as f:
							f.write('\n' + date_string)
					else:
						# just use existing data
						print("Recent run exists. Using existing data")
				else:
					print("Check run history format")
		else:
			try:
				try_create_dir(dir_path)
				run_scraper(dir_path)
				# write to run history
				with open(self._history_file, 'w') as f:
					f.write("Data Collection Run History:\n")
					f.write("-----------------\n")
					f.write(date_string)
			except:
				traceback.print_exc() # print error
		return dir_path

if __name__ == '__main__':
	# example isolated usage
	myTemplate = LyricsTemplates(7, 15, 2)
