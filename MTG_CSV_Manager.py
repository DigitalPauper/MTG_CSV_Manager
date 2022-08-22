from selenium import webdriver
from selenium.webdriver.common.by import By
from termcolor import cprint
from termcolor import colored
from datetime import datetime
import pandas as pd
import urllib.request, os, time, random


#                                           ABOUT
##########################################################################################################
# This program takes CSV files with Magic: The Gathering card information scrapes, and stores relevent 
#   information about the selected card printing. 
# 
# Title line names matter, but order does not
#  CSV Title Line structured below: 
# 
#  Card Name;Card Set;Set Abbreviation;Card Number;Foil;Languange;Rarity;Card Condition;Copies;Price;Image Name;Scryfall URL;TCGP URL;Updated
# 
#                                         08-18-2022
##########################################################################################################
# 

# [USER DEFINED VARIABLES]
# path to the CSV file to analyze
# csv_path = "MTG_Collection_CSVs/MTG_Collection_Black.csv"
csv_path = "MTG_Test_Collection_Blue_copy.csv"

image_folder = (f'{csv_path.replace(".csv","")}_CardImages')

# the amount of time the web scraper dwells on a webpage before moving on
min_dwell_time = 4
max_dwell_time = 5

# scrapes Scryfall for all printings of a card given only its name
setScrape = True
setScrapeAllCards = True          # scrapes cards that already have set information
setScrapePrintImageURLs = False    # returns the card's scryfafll image URL to the termimnal
setScrapeSaveImage = True         # saves the image to the CardImages folder
setScrapeInteractive = True       # scrapes sets and waits for the user to select the correct card before saving info and continuing

# navigates to the card, then to the associated TCG Player link and scrapes the market median pricing data
priceScrape = True

# sums the price collumn at the end of the routine
priceSum = True

# prints more information during the web scrape navigation phase 
debug = False
# [END USER DEFINED VARIABLES]


#                                           TODO
##########################################################################################################
# 
#  
##########################################################################################################

currentDirectory = os.getcwd()
path = os.path.join(currentDirectory, image_folder)

punctuation = '''!()[]{};:'"\<>.,/?@#$%^&*_~'''
# punctuation stripping table to remove undesired inputs from URLs and filters
punctuationTranslationTable = str.maketrans("","",punctuation)

# open the specified CSV file
df = pd.read_csv(csv_path, sep=';', header=None)
# determine the length and width of the file
num_rows, num_collumns = df.shape

# place holder for constructed URLs to navigate
url = ""

# place holder for scraped price information
valuation = float(0.00)

# place holders for collumn heading reference numbers
card_name_collumn_number = 0
card_set_collumn_number = 0
set_abbreviation_collumn_number = 0
card_number_collumn_number = 0
foiling_collumn_number = 0
art_collumn_number = 0
printing_collumn_number = 0
languange_collumn_number = 0
rarity_collumn_number = 0
card_condition_collumn_number = 0
copies_collumn_number = 0
price_collumn_number = 0
image_url_collumn_number = 0
image_name_collumn_number = 0
scryfall_url_collumn_number = 0
tcgp_url_collumn_number = 0
updated_collumn_number = 0

# extract collumn numbers of specific headings
for c in range(0,num_collumns):
    if df.iloc[0,c] ==  'Card Name': 
        card_name_collumn_number = c
    elif df.iloc[0,c] ==  'Card Set':
        card_set_collumn_number = c
    elif df.iloc[0,c] ==  'Set Abbreviation':
        set_abbreviation_collumn_number = c
    elif df.iloc[0,c] ==  'Card Number':
        card_number_collumn_number = c
    elif df.iloc[0,c] ==  'Foil':
        foiling_collumn_number = c
    elif df.iloc[0,c] ==  'Languange':
        languange_collumn_number = c
    elif df.iloc[0,c] ==  'Rarity':
        rarity_collumn_number = c
    elif df.iloc[0,c] ==  'Card Condition':
        card_condition_collumn_number = c
    elif df.iloc[0,c] ==  'Copies':
        copies_collumn_number = c
    elif df.iloc[0,c] ==  'Price':
        price_collumn_number = c
    elif df.iloc[0,c] ==  'Image Name':
        image_name_collumn_number = c
    elif df.iloc[0,c] ==  'Scryfall URL':
        scryfall_url_collumn_number = c
    elif df.iloc[0,c] ==  'TCGP URL':
        tcgp_url_collumn_number = c
    elif 'Updated' in df.iloc[0,c]:
        updated_collumn_number = c

def row_StringBuilder(row):
    # Name
    rowString = (f'{df.iloc[row,card_name_collumn_number]}')
    # Set
    if not pd.isna(df.iloc[row,card_set_collumn_number]):       # if card set is populated
        rowString = rowString + (f'; {df.iloc[row,card_set_collumn_number]}')
    # Card Number
    if not pd.isna(df.iloc[row,card_number_collumn_number]):       # if card number is populated
        rowString = rowString + (f'; {df.iloc[row,card_number_collumn_number]}')
    # Foiling
    if not pd.isna(df.iloc[row,foiling_collumn_number]):       # if card foiling is populated
        rowString = rowString + (f'; {df.iloc[row,foiling_collumn_number]}')                           
    # Languange
    if not pd.isna(df.iloc[row,languange_collumn_number]):       # if card languange is populated
        rowString = rowString + (f'; {df.iloc[row,languange_collumn_number]}')
    return rowString

def get_input_integer(lowerLimit, upperLimit):
    validInput = False
    inputMessage = (f'Select Set: ')
    while not validInput:
        userInput = input(inputMessage)        # 'Select set: '
        try:
            if (lowerLimit <= int(userInput) <= upperLimit):
                validInput = True
                return int(userInput)
            else:
                print(f'{colored("Invalid input:", "red", attrs=["bold"])} [{userInput}] is outside of range {lowerLimit} to {upperLimit}')
        except ValueError:
            print(f'{colored("Invalid input:", "red", attrs=["bold"])} [{userInput}] is not a valid number')

def scrape_Scryfall(row):
    # If Card Name exists without a set, scrape Scryfall for all possible printings for easier file filling
    cardName = df.iloc[row,card_name_collumn_number]
    scryfallCardName = cardName.replace(",","%2C").replace("'","%27").replace(" ","+")
    scryfallURL = (f'https://scryfall.com/search?q=%21%22{scryfallCardName}%22+include%3Aextras&order=released&as=checklist&unique=prints')
    if debug:
        cprint(f'{scryfallURL}', 'yellow', attrs=['bold'])
    browser.get(scryfallURL)  # navigate to next URL
    dwell_time = random.randrange(min_dwell_time, max_dwell_time, 1)
    time.sleep(dwell_time)
    try:
        browser.find_element(By.CLASS_NAME, 'prints-current-set-name')
        parentElement = browser.find_element(By.CLASS_NAME, 'prints-current-set-name')
        # scrape card info
        setname = parentElement.text.split(' (')[0]
        setAbbreviation = parentElement.text.split(' ')[-1].translate(punctuationTranslationTable)
        parentElement = browser.find_element(By.CLASS_NAME, 'prints-current-set-details')
        cardNumber = parentElement.text.split(' · ')[0].translate(punctuationTranslationTable)
        cardLanguange = parentElement.text.split(' · ')[2]
        cardRarity = parentElement.text.split(' · ')[1]
        # format rarity
        if cardRarity ==  'Common': 
            cardRarity = 'C'
        elif cardRarity ==  'Uncommmon':
            cardRarity = 'U'
        elif cardRarity ==  'Rare':
            cardRarity = 'R'
        elif cardRarity ==  'Mythic Rare':
            cardRarity = 'M'
        cardImage = browser.find_element(By.CLASS_NAME, 'card-image-front')
        image = cardImage.find_element(By.TAG_NAME, 'img')
        image_URL = image.get_attribute("src")
        scryfallURL = browser.current_url
        url = ''
        if setScrapePrintImageURLs:
            url = image_URL
        print(f'0)  {colored(cardName, "white", attrs=["bold"])}  {setAbbreviation}  {cardNumber}  {colored(setname, "magenta", attrs=["bold"])}  {cardRarity}  {cardLanguange}  {colored(url, "cyan", attrs=["bold"])}')
        if setScrapeInteractive:
            # auto-select the only result
            selection = 0            
            print(f'Selected [{colored(selection, "yellow", attrs=["bold"])}]  {colored(cardName, "white", attrs=["bold"])}  {setAbbreviation}  {cardNumber}  {colored(setname, "magenta", attrs=["bold"])}  {cardRarity}  {cardLanguange}  {colored(url, "cyan", attrs=["bold"])}')
    except Exception:
        setTitles = []
        setAbbreviation = []
        cardNumbers = []
        printingLanguange = []
        printingRarity = []
        imageLinks = []
        cardURLs = []
        page_body_contents = browser.find_elements(By.TAG_NAME, 'tbody')
        for child in page_body_contents:
            cardInfoContainers = child.find_elements(By.TAG_NAME, 'tr')
            for card in cardInfoContainers:
                cardInfoSubContainers = card.find_elements(By.TAG_NAME, 'td')
                # scrape card info
                set = cardInfoSubContainers[0].find_element(By.TAG_NAME, 'abbr').get_attribute("title")
                abbreviation = cardInfoSubContainers[0].find_element(By.TAG_NAME, 'abbr').text
                number = cardInfoSubContainers[1].find_element(By.TAG_NAME, 'a').text
                languange = cardInfoSubContainers[6].find_element(By.TAG_NAME, 'abbr').text
                # format languange
                if languange ==  'EN': 
                    languange = 'English'
                elif languange ==  'JA':
                    languange = 'Japanese'
                rarity = cardInfoSubContainers[5].find_element(By.TAG_NAME, 'abbr').text
                cardURL = cardInfoSubContainers[2].find_element(By.TAG_NAME, 'a').get_attribute('href')
                setTitles.append(set)
                setAbbreviation.append(abbreviation)
                cardNumbers.append(number)
                printingRarity.append(rarity)
                printingLanguange.append(languange)
                image_URL = card.get_attribute("data-card-image-front")
                imageLinks.append(image_URL)
                cardURLs.append(cardURL)
        numTitles = len(setTitles)
        for i in range(0,numTitles):
            url = ''
            if setScrapePrintImageURLs:
                url = imageLinks[i]
            print(f'{i})  {setAbbreviation[i]}  {cardNumbers[i]}  {colored(setTitles[i], "magenta", attrs=["bold"])}  {printingRarity[i]}  {printingLanguange[i]}  {colored(url, "cyan", attrs=["bold"])}')
        if setScrapeInteractive:
            selection = get_input_integer(lowerLimit=0, upperLimit=numTitles)
            url = ''
            if setScrapePrintImageURLs:
                url = imageLinks[selection]
            print(f'Selected [{colored(selection, "green", attrs=["bold"])}]  {colored(cardName, "white", attrs=["bold"])}  {setAbbreviation[selection]}  {cardNumbers[selection]}  {colored(setTitles[selection], "magenta", attrs=["bold"])}  {printingRarity[selection]}  {printingLanguange[selection]}  {colored(url, "cyan", attrs=["bold"])}')
            # assign selection to storage variables
            setname = setTitles[selection]
            setAbbreviation = setAbbreviation[selection]
            cardNumber = cardNumbers[selection]
            cardLanguange = printingLanguange[selection]
            cardRarity = printingRarity[selection]
            image_URL = imageLinks[selection]
            scryfallURL = cardURLs[selection]
    # construct card image name
    img_name = (f'{cardName.lower().translate(punctuationTranslationTable).replace(" ","-")}_{setAbbreviation.lower()}_{cardNumber.lower()}.png')
    # store scraped info
    df.iloc[row,card_set_collumn_number] = setname
    df.iloc[row,set_abbreviation_collumn_number] = setAbbreviation
    df.iloc[row,card_number_collumn_number] = cardNumber
    df.iloc[row,languange_collumn_number] = cardLanguange
    df.iloc[row,rarity_collumn_number] = cardRarity
    # fill empty fields
    if pd.isna(df.iloc[row,card_condition_collumn_number]):       # if condition is NaN
            df.iloc[row,card_condition_collumn_number] = "NM"
    else:
        pass
    if pd.isna(df.iloc[row,copies_collumn_number]):       # if number of copies is NaN
            df.iloc[row,copies_collumn_number] = 1
    else:
        pass
    df.iloc[row,scryfall_url_collumn_number] = scryfallURL
    df.iloc[row,image_name_collumn_number] = img_name
    if setScrapeSaveImage:
        image_destination = os.path.join(path, img_name)
        if os.path.isfile(image_destination):
            pass
        else:
            # scrape image if it does not already exist
            urllib.request.urlretrieve(image_URL, image_destination)

def scrape_Scryfall_Buy_Links(row):
    if not browser.current_url == df.iloc[row,scryfall_url_collumn_number]:
        # navigate to TCG Player link and get price info
        browser.get(df.iloc[row,scryfall_url_collumn_number])
        dwell_time = random.randrange(min_dwell_time, max_dwell_time, 1)
        time.sleep(dwell_time)
    toolboxCollumns = browser.find_elements(By.CLASS_NAME, 'toolbox-column')
    buyCardCollumn = toolboxCollumns[1].find_elements(By.TAG_NAME, 'ul')
    TCGPlayerSection = buyCardCollumn[0].find_elements(By.TAG_NAME, 'li')
    TCGPlayerButtons = TCGPlayerSection[0].find_elements(By.TAG_NAME, 'a')
    TCGPlayerLinks = []
    TCGPlayerLinkNames = []
    for button in TCGPlayerButtons:
        url = button.get_attribute('href')
        TCGPlayerLinks.append(url)
        TCGPlayerLinkNames.append(button.find_element(By.TAG_NAME, 'i').text)
    TCGPlayerProductLinks = []
    for i in range(0,len(TCGPlayerLinks)):
        # split the buy link and save only the until the product information
        url = TCGPlayerLinks[i].split('?')[0]
        TCGPlayerProductLinks.append(url)
    # store the basic card product page (contains non-foil and foil version pricing if they exist)
    url = TCGPlayerProductLinks[0]
    # if the card is foil etched
    if not pd.isna(df.iloc[row,foiling_collumn_number]):       # if card foiling is populated
        if df.iloc[row,foiling_collumn_number] == "FE":
            for i in range(0,len(TCGPlayerLinkNames)):
                if 'etched' in TCGPlayerLinkNames[i]:
                    # if card if foil etched, store the etched version link
                    url = TCGPlayerProductLinks[i]
    return url

def scrape_TCGPlayer(row):
    if debug:
        cprint(f'{url}  :TCG Player start URL', 'blue', attrs=['bold'])
    try:
        # try to find listed median prices for card
        parentElements = browser.find_elements(By.CLASS_NAME, 'price-points__rows')
        for parent in parentElements:
            elementList = parent.find_elements(By.CLASS_NAME, 'price')
            totalElements = len(elementList)
            if totalElements == 3:
                # card printing exists singularly in either foil or nonfoil
                # print(f'Listed Median Price: {elementList[len(elementList)-1].text}')
                valuation = elementList[len(elementList)-1].text
                valuation = float(valuation.replace("$",""))
            elif totalElements == 6:
                # there is a foil and nonfoil printing of the card
                if df.iloc[row,foiling_collumn_number] == "F":
                    valuation = elementList[len(elementList)-1].text
                    valuation = float(valuation.replace("$",""))
                    # print(f'Listed Median Foil Price: {elementList[len(elementList)-1].text}')
                else:
                    valuation = elementList[len(elementList)-2].text
                    valuation = float(valuation.replace("$",""))
                    # print(f'Listed Median Price: {elementList[len(elementList)-2].text}')
        df.iloc[row,price_collumn_number] = valuation  
        if debug:
            cprint(f'TCG Player URL Succeded', 'green', attrs=['bold'])
    except Exception:
        # otherwise update value to 0 and print failure message
        if debug:
            cprint(f'TCG Player URL Failed', 'red', attrs=['bold'])
        valuation = float(0.00)
        df.iloc[row,price_collumn_number] = valuation

def sum_CSV_Prices():
    price_sum = float(0)

    for r in range(1,num_rows):
        if pd.isna(df.iloc[r,price_collumn_number]):       # if rarity is NaN
            price_sum = price_sum + float(0.00)
        else:
            price_sum = price_sum + (int(df.iloc[r,copies_collumn_number]) * float(df.iloc[r,price_collumn_number]))

    print('')
    print(f'{colored(csv_path, "white", attrs=["bold"])} is worth {colored("$", "green", attrs=["bold"])}{colored(round(price_sum, 2), "green", attrs=["bold"])}')   
    print('')

def navigate_and_scrape():
    num_cards = num_rows-1
    for r in range(1,num_rows):
        # If name and set exist, attempt to scrape data
        if pd.isna(df.iloc[r,card_name_collumn_number]):       # if card name is NaN
            pass
        else:
            if pd.isna(df.iloc[r,card_set_collumn_number]):       # if card set is NaN
                # if card name exists but set name does not
                if setScrape:
                    print(f'{r}/{num_cards}: {colored("Searching for:", "white", attrs=["bold"])} [{colored(df.iloc[r,card_name_collumn_number], "red", attrs=["bold"])}]')   
                    scrape_Scryfall(r)
            else:
                if setScrape and setScrapeAllCards:
                    print(f'{r}/{num_cards}: {colored("Searching for:", "white", attrs=["bold"])} [{colored(df.iloc[r,card_name_collumn_number], "green", attrs=["bold"])}]') 
                    scrape_Scryfall(r)
        if setScrape:
                df.iloc[r,tcgp_url_collumn_number] = scrape_Scryfall_Buy_Links(r)
        if priceScrape:
            if not pd.isna(df.iloc[r,tcgp_url_collumn_number]):       # if TCG Player URL exists
                # tcgplayer price extract and store
                browser.get(df.iloc[r,tcgp_url_collumn_number])
                dwell_time = random.randrange(min_dwell_time, max_dwell_time, 1)
                time.sleep(dwell_time)
                scrape_TCGPlayer(r)
                cprint(f'${df.iloc[r,price_collumn_number]}', "green", attrs=["bold"])
            else:
                print('Empty TCG Player Card URL')


if __name__ == "__main__":
    startTime  = datetime.now()
    if setScrapeSaveImage:
        # Make the directory if it does not already exist
        if os.path.isdir(path):
            pass
        else:
            os.mkdir(path)
    last_updated = df.iloc[0,updated_collumn_number].split(' ')[-1]
    print(f'Last Updated {last_updated}')
    print('')
    if setScrape:
        browser = webdriver.Firefox()
        navigate_and_scrape()
        time.sleep(random.randrange(min_dwell_time, max_dwell_time, 1))
        browser.quit()
    else:
        pass
    df.iloc[0,updated_collumn_number] = (f'Updated {startTime.month}-{startTime.day}-{startTime.year}')
    df.to_csv(csv_path, sep=';', header=None, index=None)
    if priceSum:
        sum_CSV_Prices()
    stopTime  = datetime.now()
    delta = stopTime - startTime
    print('')
    # print(f'Total Time Elapsed: {delta.total_seconds()} s')
    print(f'Total Time Elapsed: {delta}')
    print('\n')