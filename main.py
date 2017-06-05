import os
import datetime

def run_generator(date_string):
	pass
	
def create_dir(run_date):
	dir_path = './data/' + run_date
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)
	return

if __name__ == "__main__":
	run_date = datetime.date.today()
	run_weekday = run_date.weekday()
	date_string = str(run_date) + "-" + str(run_weekday)
	file_dir = './data/last_run.txt'
	if os.path.exists(file_dir):
		with open(file_dir) as f:
			text = f.read()
		lines = text.split('\n')
		if lines:
			last_run = lines[-1].split('-')
			if len(last_run) == 4:
				last_run_date = \
						datetime.date(
							int(last_run[0]),
							int(last_run[1]),
							int(last_run[2])
						)
				weekday = int(last_run[3])
				delta = run_date - last_run_date
				if abs(delta.days) >= 7 or (delta.days > 0 and weekday > run_weekday) \
					or (delta.days < 0 and weekday < run_weekday):
					# new data collection run about to happen. Record in history as most recent
					# run to be checked next time the program is run
					with open(file_dir, 'a') as f:
						f.write('\n' + date_string)
					create_dir(date_string)
					run_generator(date_string)
					# scrape new data
				else:
					# just use existing data
					print("use existing data")
					run_generator(lines[-1])
			else:
				print("Check run history format")
	else:
		with open(file_dir, 'w') as f:
			f.write("Data Collection Run History:\n")
			f.write("-----------------\n")
			f.write(date_string)
			create_dir(date_string)
			run_generator(date_string)
