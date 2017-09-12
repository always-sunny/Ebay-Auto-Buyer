# -*- coding: utf-8 -*-
import pycountry
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException
from countryDict import *
from retry import retry
from selenium.common.exceptions import StaleElementReferenceException

approvedCountries = [
"United States",
"Canada",
"Australia",
"United Arab Emirates"
]

orders = []


#################################################
#loop to parse csv file and get info we need
#################################################
f = open('workbook.csv')
csv_f = csv.reader(f)

for index, row in enumerate(csv_f):
	#skip first line; is header row
	if (index > 0):
		temp = []
		temp.append(row[16]) #0 Lineitem quantity
		temp.append(row[17]) #1 Lineitem name
		temp.append(row[34]) #2 Shipping Name
		temp.append(row[35]) #3 Shipping Street
		temp.append(row[39]) #4 Shipping City
		temp.append(row[40]) #5 Shipping Zip
		temp.append(row[41]) #6 Shipping Province
		temp.append(row[42]) #7 Shipping Country
		orders.append(temp)

f.close()

##################################################
#loop to correct blank lines of multi item orders
##################################################
for index, o in enumerate(orders):
	#if shipping name is blank then preceeding lines are also blank
	if (o[2] == ""):
		o[2] = (orders[index-1])[2]
		o[3] = (orders[index-1])[3]
		o[4] = (orders[index-1])[4]
		o[5] = (orders[index-1])[5]
		o[6] = (orders[index-1])[6]
		o[7] = (orders[index-1])[7]
	#print o

##################################################
#loop to purchase
##################################################
index = 1
for o in orders:

	#Change country name FROM alpha 2 TO full name
	t = list(pycountry.countries)
	for country in t:
		if(o[7] == country.alpha2):
			o[7] = country.name

	for ac in approvedCountries:
		if(o[7] == ac):
			#driver = webdriver.Firefox()
			driver = webdriver.Chrome(executable_path='./chromedriver')
			wait = WebDriverWait(driver, 10)

			if (o[1] == "Sri Yantra Necklace"):
				driver.get("http://www.ebay.com/itm/Sri-Yantra-Photo-Cabochon-Glass-Tibet-Silver-Chain-Pendant-Necklace-/152015396110?hash=item2364d2dd0e:g:xWAAAOSwYlJW5uF9")

			elif (o[1] == "Chakra Candle Set with Essential Oils (Paraffin Free)"):
				driver.get("http://www.ebay.com/itm/Chakra-Rainbow-Candle-Aromatic-with-Essential-Oils-Something-Different-/321648977340?hash=item4ae3c5e5bc:g:ogoAAOSwT5tWONJE")

			elif (o[1] == "Powerful Gemstone Necklaces - Blue Turquoise"):
				driver.get("http://www.ebay.com/itm/Natural-Gemstones-Hexagonal-Pointed-Reiki-Chakra-Healing-Pendant-Necklaces-Beads-/290953760876?var=590158605793&hash=item43be32106c:g:hdwAAOxyBLBR9-da")

			elif (o[1] == "Evil Eye Bracelet"):
				driver.get("http://www.ebay.com/itm/Red-Evil-Eye-String-Kabbalah-Bracelet-Mati-Nazar-Bead-Good-Luck-Charm-Protection-/281801387875?hash=item419cabef63:g:mlUAAOSwEetV-Sze")

			elif (o[1] == "Gold Sri Yantra with Superfine Etchingr"):
				driver.get("http://www.ebay.com/itm/14-KT-GOLD-PLATED-SRI-YANTRA-PENDANT-CHARM-ALMOST-2-HIGH-WITH-A-ROPE-CHAIN-132-/141957253193?var=441084342735&hash=item210d4fc849:m:m8x2XafBqbSHJcv9HYxETGw")

			elif (o[1] == "Gemstones for Balancing the Chakras"):
				driver.get("http://www.ebay.com/itm/The-Chakras-Including-an-Updated-List-of-Chakra-Balancing-Colors-/381236322683?hash=item58c374a17b:m:mJaGxZ-Jxd63EJNl7ZT-DRw")

			else:
				#let file know this person was skipped
				print "SKIPPED! - ISSUE FINDING URL"
				print o
				pass

			wait.until(EC.presence_of_element_located((By.ID, 'isCartBtn_btn')))
			wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'qtyInput')))
			input_field = driver.find_element_by_name('quantity')
			input_field.clear()
			input_field.send_keys(o[0])
			driver.find_element_by_id('binBtn_btn').click()
			#GUESTCHECKOUT
			wait.until(EC.presence_of_element_located((By.ID, 'gtChk')))
			driver.find_element_by_id('gtChk').click()

			wait.until(EC.presence_of_element_located((By.ID, 'shpFrame')))
			driver.switch_to_frame(driver.find_element_by_tag_name("iframe"))
			wait.until(EC.presence_of_element_located((By.ID, 'confirmEmail')))
			wait.until(EC.presence_of_element_located((By.ID, 'firstName')))

			#Special case for Australia: Change state/providence to full name
			if(o[7] == "Australia"):
				for state in countryDict:
					if o[6] == state:
						o[6] = countryDict[state]

			print index
			print o

			Select(driver.find_element_by_name('country')).select_by_visible_text(o[7])

			name = o[2].split()

			@retry(StaleElementReferenceException, tries=3)
			def reap():

				driver.find_element_by_name('firstName').send_keys(name[0])

				driver.find_element_by_name('lastName').send_keys(name[1])

				driver.find_element_by_name('address1').send_keys(o[3])

				driver.find_element_by_name('city').send_keys(o[4])

			reap()

			if(o[7]  == "United Arab Emirates"):
				driver.find_element_by_name('state').send_keys(o[6])
			else:
				Select(driver.find_element_by_name('state')).select_by_value(o[6])

			driver.find_element_by_name('zip').send_keys(o[5])

			if(o[7]  == "Australia"):
				driver.find_element_by_name('dayphone1').send_keys("123")
				driver.find_element_by_name('dayphone2').send_keys("4567890")
			elif(o[7 == "United Arab Emirates"]):
				driver.find_element_by_name('dayphone1').send_keys("1234567890")
			else:
				driver.find_element_by_name('dayphone1').send_keys("123")
				driver.find_element_by_name('dayphone2').send_keys("456")
				driver.find_element_by_name('dayphone3').send_keys("7890")

			driver.find_element_by_name('email').send_keys("name@gmail.com")
			driver.find_element_by_name('confirmEmail').send_keys("name@gmail.com")

			driver.switch_to_default_content()
			driver.close();
			driver.quit();
			index = index + 1
