import requests
import sys
import cv2
import json
import csv
import time 
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup, SoupStrainer
import urllib

##________________________________SAVING VECHICLES DETAILS TO CSV__________________##

def toCSV(json_file):
	
	data_file = open('unknown_vehicle.csv', 'a')
	csv_writer = csv.writer(data_file)
	csv_writer.writerow(json_file.values())
	data_file.close() 
	#print("\n Vehicle Registered")




##____________________________Getting Vehicle Details________________________________##

def get_vehicle_details(license=''):
	
	lic_region = license[:6]
	lic_no = license[6:]
	
	origin = 'https://rtovehicle.info'
	url = 'https://rtovehicle.info/index.php'
	post_url='https://rtovehicle.info/batman.php'

	head = {
		'Host': 'rtovehicle.info',
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
		'Accept': '*/*',
		'Accept-Language': 'en-US,en;q=0.5',
		'Accept-Encoding': 'gzip, deflate, br',
		'Referer': 'https://rtovehicle.info/index.php',
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'X-Requested-With': 'XMLHttpRequest',
		'Origin': 'https://rtovehicle.info',
		'Connection': 'keep-alive',
	}

	r = requests.get(url=url,headers = head)

	sys.stdout.write("\n Gathering Vehicle Information")

	time.sleep(1)

	data = {
		'r1[]':lic_region,
		'r2':lic_no,
		'auth' :'Y29tLmRlbHVzaW9uYWwudmVoaWNsZWluZm8='
	}

	data_encode = { 'r1%5B%5D':'MH15GB',
					'r2':'9973',
					'auth':'Y29tLmRlbHVzaW9uYWwudmVoaWNsZWluZm8%3D' }
					
	post = requests.post(url=post_url, data = data,headers = head)

	psoup = BeautifulSoup(post.text,'html.parser')
	vehicle_json = post.json()
	
	#toCSV(vehicle_json)
	
	headers = vehicle_json.keys()
	values = vehicle_json.values()
	vehicle_df = pd.DataFrame(values,index = headers)
#	vehicle_df = vehicle_df.drop(['e_no','c_no','reason'],axis=0)
	return vehicle_df
'''
df = get_vehicle_details()
print(df.iloc[0,0])'''
