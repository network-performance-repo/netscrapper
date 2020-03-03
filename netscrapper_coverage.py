import asyncio
from pyppeteer import launch
import requests as rq
import json
import pandas as pd
import os

global_authorization_token = "nothing yet"

province_lat_long = {
    "GOLESTAN": {'lat': 36.841644, 'long': 54.432922},
    "MAZANDARAN": {'lat': 36.471546, 'long': 52.355087},
    "ARDEBIL": {'lat': 38.2537, 'long': 48.3},
    "EAST AZARBAIJAN": {'lat': 38.489429, 'long': 47.068359},
    "GILAN": {'lat': 37.280834, 'long': 49.583057},
    "QAZVIN": {'lat': 36.269363, 'long': 50.003201},
    "WEST AZARBAIJAN": {'lat': 37.552673, 'long': 45.076046},
    "ZANJAN": {'lat': 36.674339, 'long': 48.484467},
    "KHORASAN JONOBI": {'lat': 32.872379, 'long': 59.221375},
    "KHORASAN RAZAVI": {'lat': 36.310699, 'long': 59.599457},
    "KHORASAN SHOMALI": {'lat': 37.4702, 'long': 57.3143},
    "SEMNAN": {'lat': 35.2256, 'long': 54.4342},
    "HAMEDAN": {'lat': 34.7989, 'long': 48.515},
    "ILAM": {'lat': 33.635, 'long': 46.4153},
    "KERMANSHAH": {'lat': 34.3277, 'long': 47.0778},
    "KORDESTAN": {'lat': 35.3219, 'long': 46.9862},
    "LORESTAN": {'lat': 33.4647, 'long': 48.339},
    "MARKAZI": {'lat': 34.0954, 'long': 49.7013},
    "QOM": {'lat': 34.6416, 'long': 50.8746},
    "CHAHARMAHAL&BAKHTYARI": {'lat': 32.326721, 'long': 50.859081},
    "ESFEHAN": {'lat': 32.661343, 'long': 51.680374},
    "KHUZESTAN": {'lat': 31.318327, 'long': 48.67062},
    "KOHGILUYEH&BOYER AHMAD": {'lat': 30.668383, 'long': 51.587524},
    "YAZD": {'lat': 31.897423, 'long': 54.356857},
    "BUSHEHR": {'lat': 28.9234, 'long': 50.8203},
    "FARS": {'lat': 29.591768, 'long': 52.583698},
    "HORMOZGAN": {'lat': 27.183708, 'long': 56.277447},
    "KERMAN": {'lat': 30.283937, 'long': 57.083363},
    "SISTAN&BALOCHESTAN": {'lat': 29.491021, 'long': 60.859548},
    "ALBORZ": {'lat': 35.855938, 'long': 50.96175},
    "TEHRAN": {'lat': 35.715298, 'long': 51.404343},
}


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def extract_authorization_token(req_url):
    tokens = req_url.split("/")

    authorization_token = tokens[len(tokens)-2]
    print("authorization_token = " + authorization_token)
    return authorization_token


async def handle_request(request):
    global global_authorization_token

    print(request.url)
    if 'areainfo' in request.url:
        global_authorization_token = extract_authorization_token(request.url)

    return await request.continue_()


async def request_async():
    browser = await launch(
        ignoreHTTPSErrors=True,
        args=['--no-sandbox'],
    )

    page = await browser.newPage()

    await page.setRequestInterception(True)
    page.on('request', lambda req: asyncio.ensure_future(handle_request(req)))

    resp = await page.goto("https://netsanjplus.ir/index.html?operatorid=27&serviceid=31")
    await page.waitFor(10000)


def scrapNetworkCoverageForProvince(authorization_token, province, latitude, longitude):

    print("Collecting data for province " + province)

    reqQuery = r"https://gis.cra.ir/craapi.svc/drivetestaggdata/4013/" + str(latitude) +\
               "/" + str(longitude) + "/" + str(latitude) + "/" + str(longitude) + "/" + authorization_token + "/1582710112557"
    response = rq.get(reqQuery)

    jprint(response.json())

    strJsonDump = json.dumps(response.json()) # first object needs to be dumped as string
    dfProvinceJson = pd.read_json(strJsonDump) # now pandas can understand it (doesn't accept json object)

    print(dfProvinceJson)
#    dfProvinceJson['Category'] = serviceCategory[serviceCategoryIndex] # adding the category column manualy to the DF.

    print("Done for province  " + province)

    return dfProvinceJson

def humanizeData(dfProvinceJson):
    result = dfProvinceJson['result']


def scrapNetworkCoverage(authorization_token):
    dfAllProvinces = pd.DataFrame()
    dfListProvincesData = []

    for key in province_lat_long:
        province = key
        lat_long = province_lat_long[key]
        latitude = lat_long['lat']
        longitude = lat_long['long']

        dfProvinceJson = scrapNetworkCoverageForProvince(authorization_token, province, latitude, longitude)

        #dfProvinceJson = humanizeData(dfProvinceJson)
        dfListProvincesData.append(dfProvinceJson)

    dfAllProvinces = pd.concat(dfListProvincesData, axis=0, ignore_index=True)

    return dfAllProvinces


loop = asyncio.get_event_loop()
loop.run_until_complete(request_async())

print("Global authorization_token: " + global_authorization_token)

dfAllProvinces = scrapNetworkCoverage(global_authorization_token)

absPath = os.path.dirname(os.path.abspath(__file__))
completeFilePath = absPath + r'\Network_Coverage_All_Provinces.csv'
dfAllProvinces.to_csv(completeFilePath , index = False, encoding='utf-8-sig')

