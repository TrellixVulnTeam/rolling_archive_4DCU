# sudo pip3 install py2exe xdelta3

from functools import reduce
import os
import tarfile
import datetime
from calendar import monthrange
import xdelta3

class Archive:

	backup_location = ""
	month_folders = []

	def __init__(self, backup_location, months):
		self.backup_location = backup_location
		self.month_folders = list(map(lambda month: backup_location + "/" + month, months))
		__create_folders()

	
	# Creates the folder structure or does nothing if it already exists
	def __create_folders(self):
		if not os.path.exists(self.backup_location):
                        os.makedirs(self.backup_location)

		for month in self.month_folders:
                	if not os.path.exists(month):
                        	os.makedirs(month)

				
	# Returns a list of binary strings of data for the month from file
	def __get_month(self, month):
                month_data = []
		
                days_in_month = monthrange(datetime.date.today().year, datetime.date.today().month)[1]
                for day in range(days_in_month):
                        day_file = self.month_folders[month] + "/" + day
                        if os.path.isfile(day_file):
                                with open(day_file, 'rb') as f:
                                        self.month_data.append(f.read())
                        else:
                                self.month_data.append(b'')
                
                return month_data

				
	# Clears the month and flushes the file
	def __clear_month(self, month):
                days_in_month = monthrange(datetime.date.today().year, datetime.date.today().month)[1]
                for day in range(days_in_month):
                        day_file = self.month_folders[month] + "/" + str(day)
			if os.path.isfile(day_file):
                        	os.remove(day_file)


	# Returns the (day, month) to retrieve from backup
	def __get_day_location(self, backup_date):
                today = datetime.datetime.strptime(str(datetime.date.today()), "%Y-%m-%d")
                retrieve = datetime.datetime.strptime(str(backup_date), "%d-%m-%Y")
                days_ago = (today - retrieve).days
                if days_ago < 0:
                        days_ago = 0

                months = [monthrange(datetime.date.today().year, datetime.date.today().month)[1],
                monthrange(datetime.date.today().year, datetime.date.today().month - 1)[1],
                monthrange(datetime.date.today().year, datetime.date.today().month - 2)[1],
                monthrange(datetime.date.today().year, datetime.date.today().month - 3)[1]]

                month = 0
                today = today.day
                if today - days_ago <= 0:
                        month += 1
                        days_ago -= today
                else:
                        return (today - days_ago, 0)
                
                while days_ago > 0 and month < 3:
                        if days_ago - months[month] < 0:
                                break

                        days_ago -= months[month]
                        month += 1
                
                if days_ago > months[3]:
                	return (months[3], 3)
                else:
                	return (months[month] - days_ago, month)
                	
                	
        # Writes the file associated with backup_date to restore_file_location
	def retrieve_day(self, restore_location, backup_date):
		(day, month) = __get_day_location(self, backup_date)
		month_data = __get_month(month)
		day_data = reduce(xdelta3.decode, month_data[:day])
		
		# Write the days data to a temp file
		temp_file = self.backup_location + "/temp.tar.xz"
		with open(temp_file, "wb") as f:
                	f.write(day_data)

		# Then uncompress it to restore_location
		with tarfile.open(temp_file, "r:xz") as tar:
			tar.extractall(path=restore_location)
		os.remove(temp_file)
		
		
	# Writes the backup_folders to the current day
	def archive_day(self, backup_folders):
                day = datetime.datetime.today().day
                month = datetime.datetime.today().month % 4
                		  
                # Tar backup_folders togeather
                temp_file = self.backup_location + "/temp.tar.xz"
                day_data = b""
		with tarfile.open(temp_file, "x:xz") as tar:
                	for folder in backup_folders:
                                tar.add(folder)
                with open(temp_file, "rb") as binary:
                        day_data = binary.read()
		os.remove(temp_file)
                
                # Write to disk
                day_file = month_folders[month] + "/" + str(day)
                if day == 0:
                	__clear_month(month)
                	with open(day_file, "wb") as f:
                		f.write(day_data)
                else:
                        month_data = __get_month(self, month)
                        last_day = reduce(xdelta3.decode, month_data[:day])
                        with open(day_file, "wb") as f:
                                f.write(xdelta3.encode(last_day, day_data))

archive = Archive("/home/dunadmin/test_backup", ['month1','month2','month3','month4'])
archive.archive_day(["/home/dunadmin/Downloads"])
archive.retrieve_day("/home/dunadmin/test_restore", "01-02-2017")