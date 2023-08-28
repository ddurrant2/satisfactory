from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import re
from selenium.webdriver.common.action_chains import ActionChains
import json
from datetime import date
 
#Does not cover byproducts
#does not cover redundant items (eg. crude oil)

def Main():
    #Create browser and accept cookies
    driver = webdriver.Chrome()
    chosenURL = 'https://satisfactory.wiki.gg/wiki/Category:Items'
    driver.get(chosenURL)
    sleep(2)
    try:
        driver.find_element(By.XPATH, '//span[contains(text(), "OK")]/ancestor::button').click()
    except:
        print("No cookie window found.")

    #build blacklist
    blacklistSites = ['https://satisfactory.wiki.gg/wiki/Category:Equipment', 'https://satisfactory.wiki.gg/wiki/Category:Ores']
    blacklist = ["Bacon Agaric", "Paleberry", "Beryl Nut"]
    for site in blacklistSites:
        driver.get(site)
        sleep(5)
        blacklistItems = driver.find_elements(By.XPATH, '//h2[contains(text(), "Pages in category")]/following-sibling::div//a')
        for x in blacklistItems:
            blacklist.append(x.text)
        sleep(2)

    #Establish masterDict
    todaysDate = str(date.today())
    masterDict = {}
    masterDict["createdBy"] = "ddurrant2"
    masterDict["lastUpdated"] = todaysDate
    masterDict["totalItems"] = 0
    masterDict["results"] = []
    
    #For items, fluids
    scrapePages = ['https://satisfactory.wiki.gg/wiki/Category:Items', 'https://satisfactory.wiki.gg/wiki/Category:Fluids']

    for page in scrapePages:
            #Access items page
        driver.get(page)
        sleep(2)

        #Get strings of all items
        aTags = driver.find_elements(By.XPATH, '//h2[contains(text(), "Pages in category")]/following-sibling::div//a')
        aTagStrings = []
        for x in aTags:
            if x.text not in blacklist:
                aTagStrings.append(x.text)
        
        #Go through all non-blacklisted items
        for a in range(len(aTagStrings)): #len(aTagStrings)
            itemDict = {}
            print("---------------------------------------------------------------------------")
            print(f'Item is {aTagStrings[a]}:')
            
            #Redundant, should never be needed
            if aTagStrings[a] not in blacklist:
                itemDict["Name:"] = aTagStrings[a]
                
                #click the link
                nextItemElement = driver.find_element(By.XPATH, f'//h2[contains(text(), "Pages in category")]/following-sibling::div//a[contains(text(), "{aTagStrings[a]}")]')
                actions = ActionChains(driver)
                actions.move_to_element(nextItemElement).perform()
                nextItemElement.click()
                #if recipes:
                try:
                    sleep(2)
                    recipesXpath = '(//h2[contains(., "Obtaining")]/following-sibling::h2[contains(., "Usage")]/preceding-sibling::table[contains(., "Recipe")])[1]//tbody//tr'
                    recipes = driver.find_elements(By.XPATH, recipesXpath)
                    print(f"Recipes available: {len(recipes)}")
                    recipeList = []

                    #Get each recipe
                    for h in range(len(recipes)):
                        recipeDict = {}
                        recipeDict["Input"] = []
                        ingredients = driver.find_elements(By.XPATH, f'(//h2[contains(., "Obtaining")]/following-sibling::h2[contains(., "Usage")]/preceding-sibling::table[contains(., "Recipe")])[1]//tbody//tr[{h+1}]/td[2]//span[2]')
                        quantities = driver.find_elements(By.XPATH, f'(//h2[contains(., "Obtaining")]/following-sibling::h2[contains(., "Usage")]/preceding-sibling::table[contains(., "Recipe")])[1]//tbody//tr[{h+1}]/td[2]//span[last()]')
                        print(f"Recipe {h+1}:")
                        print("Output: ")
                        recipeDict["Output"] = driver.find_element(By.XPATH, f'(//h2[contains(., "Obtaining")]/following-sibling::h2[contains(., "Usage")]/preceding-sibling::table[contains(., "Recipe")])[1]//tbody//tr[{h+1}]/td[4]//span[contains(text(), "{aTagStrings[a]}")]/following-sibling::span[last()]').text.removesuffix(" / min")
                        print(recipeDict["Output"])

                        #Get all ingredients and quantities per recipe
                        for i in range(len(ingredients)):
                            ingredientDict = {}
                            ingredientDict["Name"] = ingredients[i].text
                            ingredientDict["QuantityPerMin"] = quantities[i].text.removesuffix(" / min")
                            print(f'\t{ingredientDict["Name"]}:{ingredientDict["QuantityPerMin"]}')
                            recipeDict["Input"].append(ingredientDict)

                        #add the recipe to the list of recipes for this item
                        recipeList.append(recipeDict)

                    #add the list of recipes to the item
                    itemDict["Recipes"] = recipeList
                        
                except:
                    print("No crafting available")
                
                #only add if recipes exist
                if len(recipeList) > 0:
                    masterDict["results"].append(itemDict)
                else:
                    print("No recipes - not writing to list")
                
                #return to root page
                driver.get(page)
                sleep(2)

            else:
                print("Blacklisted item. Somehow. You shouldn't be here...")

    #Document the total number of items harvested
    masterDict["totalItems"] = len(masterDict["results"])
    sleep(2)
    driver.quit()

    #convert to JSON and save
    with open("items.json", "w") as outfile:
        json.dump(masterDict, outfile)

if __name__ == "__main__":
    Main()