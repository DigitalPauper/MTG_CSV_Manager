# MTG_CSV_Manager

This project was focused on building a living CSV document of a Magic: the Gathering collection. 

Leveraging Selenium and Pandas, this script pulls card names and scrapes all information about the user specified cards and appends it to the file. 

The user set bool at the program start set the program to either scrape only newly added cards, all enteries, simply update the existing pricing information, and/or sum the gathered price information of the collection.  

CSV files need to be ';' seperated and a title line structured with the collumn names below. 
Card Name;Card Set;Set Abbreviation;Card Number;Foil;Languange;Rarity;Card Condition;Copies;Price;Image Name;Scryfall URL;TCGP URL;Updated
