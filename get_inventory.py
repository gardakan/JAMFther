import pandas as pd
from selenium import webdriver
from urllib import request
import os
import re

# Filepath::Sheet::Columns
fp = "/Users/john.tamm-buckle/Documents/CompAVTech/JAMF/Inventory2021/Inventory_2021_summer.xlsx"
sheetName = "Unique_Items"
cols = ["Asset_Inventory", "Computers", "iPads", "Misc"]

# Load Excel file
invFrame = pd.read_excel(fp, sheet_name=sheetName, usecols="A:D")

# Set up ChromeDriver
op = webdriver.ChromeOptions()
op.add_argument('headless')
driver = webdriver.Chrome(
    '/Users/john.tamm-buckle/Documents/scripts/ChromeDriver/chromedriver', options=op)
succounter = 0


# Image downloader
def getImgFromGoogle(i, invType):
    global succounter
    typedir = '/Users/john.tamm-buckle/Documents/CompAVTech/DatabaseImages/' + invType + '/'
    if not os.path.exists(typedir):
        os.mkdir(typedir, mode=0o777)
    imgdir = typedir + i
    if not os.path.exists(imgdir):
        os.mkdir(imgdir, mode=0o777)

    counter = 0
    driver.get('https://www.google.com/imghp?hl=en&ogbl')
    search_box = driver.find_element_by_name('q')
    search_box.send_keys(i)
    search_box.submit()
    for j in driver.find_elements_by_xpath("//img[@class='rg_i Q4LuWd']"):
        src = j.get_attribute('src')
        try:
            src.index('data:image/jpeg;base64,')
        except AttributeError:
            continue
        except ValueError:
            continue
        else:
            print(src)
            with request.urlopen(src) as response:
                imgdata = response.read()
            counter = counter + 1
            try:
                with open(os.path.join(imgdir, i + "_" + str(counter) + ".jpeg"), "wb") as File:
                    File.write(imgdata)
                    succounter = succounter + 1
            except ValueError:
                print("Unable to get image")
            else:
                print("Got one!")
        if counter > 4:
            break


def main():

    for col in cols:
        for index, row in invFrame.iterrows():
            if type(row[col]) is str:
                getImgFromGoogle(re.sub(r'/', '_', row[col]), col)
                # print(row[col])

    print(succounter)
    driver.quit()


main()
