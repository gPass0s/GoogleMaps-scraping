import time, random, re, csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime



class GoogleMapsCrawler:


	def __init__(self, registered,companyId):

		
		self.registered = registered
		self.companyId = companyId
		self.fator = 1
		self.page = 1
		self.registersDict = []
		self.registersList = []


	def print_data(self,name,industry,address,website,phone,rate,reviews,key):

		register = {'Company_ID':str(self.companyId),'Company_Name':name,
   					'Industry':industry, 'Street':address['street'],
   					'Town':address['city'],'State':address['state'],'Zipcode':address['zipcode'],
   					'Country':address['country'],'Website':website,'Phone_Number':phone,
   					'Rate':rate,'Reviews':reviews, 'Register_Key': key}

		self.registersDict.append(register)

		register = []
		register.append(str(self.companyId))
		register.append(name)
		register.append(industry)
		register.append(address['street'])
		register.append(address['city'])
		register.append(address['state'])
		register.append(address['zipcode'])
		register.append(address['country'])
		register.append(website)
		register.append(phone)
		register.append(rate)
		register.append(reviews)
		register.append(key)
		self.registersList.append(register)
		print(';'.join(register))

	def break_address(self,fullAddress, address):
	
		addressArray = fullAddress.split(',')
		address['country'] = addressArray[-1].strip(' ')
		countryIndex = addressArray.index(addressArray[-1])	
		
		if address['country'] == 'Australia':
			address['state'] = addressArray[countryIndex-1].split(' ')[-2].strip(' ')
			address['zipcode'] = addressArray[countryIndex-1].split(' ')[-1].strip(' ')
			address['city'] = addressArray[countryIndex-1].split(address['state'] + ' ' + \
										 address['zipcode'])[0].strip(' ')

			addressArray = fullAddress.split(", " + address['city'] + " " + address['state'] + \
											 " " + address['zipcode'])
			address['street'] = addressArray[0].strip(' ').strip(' ')

		
		elif address['country'] == 'USA' or address['country'] == 'New Zealand':
			address['state'] = addressArray[countryIndex-1].split(' ')[0].strip(' ')
			address['city'] = addressArray[countryIndex-2].strip(' ')
			address['zipcode'] = addressArray[countryIndex-1].split(' ')[1].strip(' ')
			addressArray = fullAddress.split(", " + address['city'])
			address['street'] = addressArray[0].strip(' ').strip(' ')


		elif address['country'] == 'UK':
			address['state'] = "N/A"
			address['zipcode'] = addressArray[countryIndex-1].split(' ')[-2].strip(' ') + " " + \
								 addressArray[countryIndex-1].split(' ')[-1].strip(' ')
			
			address['city'] = addressArray[countryIndex-1].split(address['zipcode'])[0].strip(' ')
			addressArray = fullAddress.split(", " + address['city'])
			address['street'] = addressArray[0].strip(' ').strip(' ')

		return address

	def grab_the_meat(self,browser,key):
		
		try:
			soup = BeautifulSoup(browser.page_source, 'lxml')
			
			name = 'Not found'
			if soup.findAll("h1",{"class":"section-hero-header-title GLOBAL__gm2-headline-5"}):
				name = soup.findAll("h1",{"class":"section-hero-header-title GLOBAL__gm2-headline-5"})[0].text

			if 'Not found' in name: 
				time.sleep(random.uniform(self.fator*15,self.fator*22.5))
				soup = BeautifulSoup(browser.page_source, 'lxml')
				name = soup.findAll("h1",{"class":"section-hero-header-title GLOBAL__gm2-headline-5"})[0].text
				if self.fator > 2:
					self.fator = self.fator*1.02
				else:
					self.fator = self.fator*1.1

			if name == "Not found": return None
			if ";" in name: name = name.replace(";",",")

			rate = 'Not found'
			industry = 'Not found'
			reviews = '0'
			address = {"street": "Not found", "city": "Not found", 
						"state":"Not found", "zipcode": "Not Found", "country": "Not Found"}
			website = "Not found"
			phone = "Not found"

			allData = soup.findAll("span",{"class":"widget-pane-link"},{"jsan":"7.widget-pane-link"})
			
			for data in allData:
				if data.text != '':
					if "+" in data.text and "," not in data.text and phone == 'Not found':
						phone = data.text
					elif "." in data.text and "," not in data.text and website== 'Not found':
						website = data.text
					elif address['street'] == 'Not found':
						address = self.break_address(data.text,address)

			if soup.findAll("span",{"class":"section-star-display"}):
				rate = soup.findAll("span",{"class":"section-star-display"})[0].text

			
			if soup.findAll("button",{"jsaction":"pane.rating.category"}):
				industry = soup.findAll("button",{"jsaction":"pane.rating.category"})[0].text

			
			if soup.findAll("button",{"jsaction":"pane.rating.moreReviews"}):
				reviews = soup.findAll("button",{"jsaction":"pane.rating.moreReviews"})[0].text
				reviews = re.findall(r'\d+',reviews)[0]

			
			key = (name+address['street']).encode("utf-8").hex()

			

			self.print_data(name,industry,address,website,phone,rate,reviews,key)
			self.companyId +=1
			
		except:
			'''if name != "Not found":
				self.print_data(name,industry,address,website,phone,rate,reviews)
				self.companyId +=1'''

			return None



	def scan_section(self,browser, error=False):

		while True:
			
			try:
				time.sleep(random.uniform(self.fator*0.7,self.fator*1))
				soup = BeautifulSoup(browser.page_source, 'lxml')
				results = soup.findAll("div",{"class":"section-result-text-content"})
				searchLimit = len(results)
				i = 1
				for result in results:

					
					name = soup.findAll("h3",{"class":"section-result-title"})[i-1].span.text
					try:
						address = soup.findAll("span",{"class":"section-result-location"})[i-1].text
					except:
						address = "Not found"

					key = (name+address).encode("utf-8").hex()
					
					if key not in self.registered:
						self.registered[key] = 1
						resultCard = browser.\
									 find_element_by_xpath("(//div[@class='section-result-title-container'])["+str(i)+"]")
						try:
							resultCard.click()
						except:
							time.sleep(random.uniform(self.fator*3.75,self.fator*5.625))
							i = 100
							break

						lastUrl = browser.current_url
						time.sleep(random.uniform(self.fator*2,self.fator*2.5))
						self.grab_the_meat(browser,key)
						try:
							goBack = browser.find_element_by_xpath("//button[@class='section-back-to-list-button blue-link noprint']")
							goBack.click()
						except:
							browser.get(browser.current_url)
						break
					i+=1

				if i>searchLimit: break
			except:
				time.sleep(random.uniform(self.fator*3.75,self.fator*5.625))
				if not error:
					browser.get(browser.current_url)
					self.page = 1
				continue


	def loop_all_sections(self,browser):
		
		error = False
	
		while True:
			time.sleep(random.uniform(self.fator*2.5,self.fator*5))
			try:
				self.scan_section(browser)
				browser.delete_all_cookies()
				time.sleep(random.uniform(self.fator*0.5,self.fator*1))
				#if (self.page/8 - self.page//8) == 0: time.sleep(random.uniform(15*self.fator,22.5*self.fator))
				nextButton = browser.find_element_by_xpath("//button[@jsaction='pane.paginationSection.nextPage']")
				nextButton.click()
				error = False
				self.page += 1
		
			except:
				if error: break
				error = True
				browser.get(browser.current_url)
				time.sleep(random.uniform(self.fator*3.75,self.fator*5.625))
				sendError = True
				for i in range(1,self.page):
					#if (i/5 - i//5) == 0: time.sleep(random.uniform(self.fator*7.5,self.fator*11.25))
					self.scan_section(browser,sendError)
					time.sleep(random.uniform(self.fator*3.75,self.fator*5.625))
					try:
						nextButton = browser.find_element_by_xpath("//button[@jsaction='pane.paginationSection.nextPage']")
						nextButton.click()
					except:
						break

	def run(self, searchTerm):

		browser = webdriver.Chrome()
		browser.get('https://www.google.com/maps?hl=en')
		inputField = browser.find_element_by_id('searchboxinput')
		time.sleep(4)
		inputField.send_keys(searchTerm)
		button = browser.find_element_by_id('searchbox-searchbutton')
		browser.delete_all_cookies()
		time.sleep(random.uniform(2.5,5))
		button.click()
		self.loop_all_sections(browser)
		browser.delete_all_cookies()
		browser.quit()


	def terminate(self, searchTerm, outputPath, outputFile):

		if self.registersDict:
			exportFile = pd.DataFrame(self.registersDict)

			columns = ['Company_ID', 'Company_Name', 'Industry','Street','Town',
					'State','Zipcode','Country','Website', 'Phone_Number','Rate','Reviews','Register_Key']
			
			exportFile = exportFile[columns]
			
			currrentTime = str(datetime.now())
			date = currrentTime.split(' ')[0]
			hour = currrentTime.split(' ')[1].split(':')[0]
			minute = currrentTime.split(' ')[1].split(':')[1]
			sec =  int(float(currrentTime.split(' ')[1].split(':')[2])//1)
			time = str(hour) + "-" + str(minute) + "-" + str(sec)
			filename = outputPath + "/" + searchTerm + "_" + date + "_" + time + ".csv"

			exportFile.to_csv(filename, sep=';', encoding = 'utf-8',index=False)

			with open(outputFile, 'a', newline='') as f:
				writer = csv.writer(f,delimiter=";")
				for row in self.registersList:
					writer.writerow(row)
				f.close()

			

