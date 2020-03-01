import requests as rq
import json
import pandas as pd
import os

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def scapNetworkQuality():
    dfAllProvinces = pd.DataFrame()
    dfListProvincesData = []

    serviceCategory = {
        1: "کاربران تجاری",
        2: "بازی",
        3: "تماس اینترنتی",
        4: "دانلئد حجیم",
        5: "وبگردی"
    }

    for provinceIndex in range(1,32): # for all 31 provinces
        for serviceCategoryIndex in range(1,6): # for all 5 service categories
            print("Collecting data for province index = " + str(provinceIndex) + " and service category index = " + str(
                serviceCategoryIndex))

            formattedProvinceIndex =  "{:02d}".format(provinceIndex) # filling in leading zeroes where necessary

            reqQuery = r"https://195.cra.ir:8098/api/ranking/31/" + \
                        formattedProvinceIndex + "/" + str(serviceCategoryIndex)
            response = rq.get(reqQuery)

            #jprint(response.json())

            strJsonDump = json.dumps(response.json()) # first object needs to be dumped as string
            dfProvinceJson = pd.read_json(strJsonDump) # now pandas can understand it (doesn't accept json object)

            dfProvinceJson['Category'] = serviceCategory[serviceCategoryIndex] # adding the category column manualy to the DF.

            dfListProvincesData.append(dfProvinceJson)

            print("Done for province index = " + str(provinceIndex) + " and service category index = " + str(serviceCategoryIndex))

    dfAllProvinces = pd.concat(dfListProvincesData, axis=0, ignore_index=True)
    return dfAllProvinces

dfAllProvinces = scapNetworkQuality()

absPath = os.path.dirname(os.path.abspath(__file__))
completeFilePath = absPath + r'\Network_Quality_All_Provinces.csv'
dfAllProvinces.to_csv(completeFilePath , index = False, encoding='utf-8-sig')

