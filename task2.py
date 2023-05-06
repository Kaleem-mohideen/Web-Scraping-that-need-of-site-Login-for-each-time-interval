from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os
import demjson
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse, parse_qs
url='http://exam.cscacademy.org/cyberstudent'
url1= "http://exam.cscacademy.org/admin/users/cyberstudents/page:1/limit:100/sort:Cyberstudent.created/direction:desc"
BASE_URL = 'http://exam.cscacademy.org'
options = Options()
driver=webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=options)

driver.set_window_size(1120, 550)

def return_next_page(soup):
	"""
	return next_url if pagination continues else return None

	Parameters
	-------
	soup - BeautifulSoup object - required

	Return 
	-------
	next_url - str or None if no next page
	"""
	next_url = None
	cur_page  = soup.find('div', class_="paging").find('span', class_="current")
	print(cur_page )
	search_next = cur_page.findNext('span').get('class')
	print(search_next)
	if not search_next:
	    next_page_href = cur_page.findNext('span').find('a')['href']
	    next_url = BASE_URL + next_page_href
	print(next_url)
	return next_url

def login(url):
	
	
	driver.get(url)

	driver.find_element("name", "data[Cyberstudent][username]").send_keys("test@gmail.com")
	driver.find_element("name", "data[Cyberstudent][password]").send_keys("9899602744")
	# driver.find_element_by_name("").send_keys(username)
	# driver.find_element_by_name("data[Cyberstudent][password]").send_keys(password)

	# you need to find how to access button on the basis of class attribute
	# here I am doing on the basis of ID
	driver.find_element("class name", "btn").click()
	return driver

def scrape_page(url1, mydata = pd.DataFrame()):

	# login(url)
	headers =  {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/86.0', 
	        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	        'Accept-Language': 'en-US,en;q=0.5',
	        'Connection': 'keep-alive',
	        'Upgrade-Insecure-Requests': '1',
	        'Cache-Control': 'max-age=0'}
	
	

	# set your accessible cookiepath here.
	cookiepath = "cookiepath"

	cookies=driver.get_cookies()
	getCookies=open(cookiepath, "w+")
	getCookies.write(demjson.encode(cookies))
	getCookies.close()
	
	readCookie = open(cookiepath, 'r')
	cookieString = readCookie.read()
	cookie = demjson.decode(cookieString)
	c_jar = requests.cookies.RequestsCookieJar()
	for cookie in cookies:
	    c_jar.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
	

	session = requests.Session()
	response = requests.get(url1, headers=headers, cookies=c_jar)
	# print(response.content)

	soup = BeautifulSoup(response.text, 'html.parser')
	# print(soup)
	table1 = soup.find('table', id='table')
	table1
	print('table',table1)
	if not table1:
		login(url)
		mydata =scrape_page(url1, mydata)
		return mydata
	# Obtain every title of columns with tag <th>
	split_list=url1.split("/")
	print(split_list)

	if any(item.startswith('page:1') for item in split_list) or not any(item.startswith('page:') for item in split_list):
		headers = []
		for i in table1.find_all('th'):
		 title = i.text
		 headers.append(title)
		 mydata = pd.DataFrame(columns = headers)
	# Create a for loop to fill mydata
	# if any(item.endswith('page:7') for item in split_list):
	# 	pass
	# if not any(item.endswith('page:7') for item in split_list):
	for j in table1.find_all('tr')[1:]:
	 row_data = j.find_all('td')
	 row = []
	 for i, j in enumerate(row_data):
	 	if i!=7:
	 		row.append(j.text)
	 	else:
	 		# print(j.find('img')['src'])
	 		if j.find('img')['src'] == "https://exam.cscacademy.org/img/paynow.png":
	 			row.append("Pay Now")
	 		elif j.find('img')['src'] == "https://exam.cscacademy.org/img/paid.png":
	 			row.append("Paid")

	 length = len(mydata)
	 mydata.loc[length] = row
	with pd.option_context('display.max_rows', None, 'display.max_columns', None):
	    print(mydata)
	next_url = return_next_page(soup)
	if next_url is not None:
		scrape_page(next_url, mydata)
	return mydata
	


# login(url)
mydata = scrape_page(url1)
mydata.to_csv('file1.csv')