import asyncio
from pyppeteer import launch
from pyppeteer import input
import json
from pyppeteer import element_handle
import pandas as pd
import os

serviceCategory = {
    1: "کاربران تجاری",
    2: "بازی",
    3: "تماس اینترنتی",
    4: "دانلئد حجیم",
    5: "وبگردی"
}

province_address = {
    "GOLESTAN": 'گرگان،ملل،خ. ملل متحد،خ. آلوچه باغ،ک. کلیسا',
    "MAZANDARAN": 'ساری،خ قارن،خ. قارن،خ. قارن ۱۱',
    "ARDEBIL": 'اردبیل،پیر شمس الدین،خ. اوچدکان،مسیر پیاده رو اوچدکان',
    "EAST AZARBAIJAN": 'تبریز،منطقه سه،مقصودیه،بلوار هفده شهریور،خ. حاج نایب',
    "GILAN": 'رشت،باقرآباد‎‎،مسیر پیاده رو سعدی،خ. اقتصاد',
    "QAZVIN": 'قزوین،سرتک،بلوار شمالی،خ. دهخدا،خ. مسکن یک،ک. مسکن سه شرقی',
    "WEST AZARBAIJAN": 'ارومیه، مدنی،خ. سرداران',
    "ZANJAN": 'زنجان،خیابان امام،ک. فصاحتی، نزدیک بلوار امام خمینی',
    "KHORASAN JONOBI": 'بیرجند،بلوار پاسداران،خ. مدرس هجده',
    "KHORASAN RAZAVI": 'مشهد،قرنی،بلوار مجد،خ. محجوب',
    "KHORASAN SHOMALI": 'بجنورد،سبزه میدان،بلوار طالقانی،خ. میرزا رضای کرمانی،خ. حسن ترکانلو',
    "SEMNAN": 'سمنان،خ. مدنی،خ. فداکار شمالی',
    "HAMEDAN": 'همدان،بابا طاهر،خ. چهارباغ خواجه رشید،خ. رستمی،خ. سیدا',
    "ILAM": 'ایلام،۱۴ دستگاه،خ. آیت الله حیدری،ک. ساده میری',
    "KERMANSHAH": 'کرمانشاه،خ. فهمیده،خ. شریعتی',
    "KORDESTAN": 'سنندج،پاسداران،بلوار کردستان،ک. حکمت',
    "LORESTAN": 'خرم آباد،آزادی،خ. شهید صارمیان،خ. باغ دختران',
    "MARKAZI": 'اراک،بازار،عباس آباد،خ. رجایی،ک. واعظ زاده،خ. آیت الله امامی',
    "QOM": 'قم،جوی شهر،خ. فاطمی،خ. هجده،ک. دانش',
    "CHAHARMAHAL&BAKHTYARI": 'شهرکرد،خ. ملت،ک. ۵۳',
    "ESFEHAN": 'اصفهان،سرچشمه،خ. ابن سینا،خ. دردشت،خ. نم نبات',
    "KHUZESTAN": 'اهواز،نادری،بلوار زند،ک. گلبهار',
    "KOHGILUYEH&BOYER AHMAD": 'یاسوج،تل زالی،خ. معاد،خ. جوانمردان شرقی',
    "YAZD": 'یزد،سردوراه،خ. خطیبی، نبش خ. وکیل',
    "BUSHEHR": 'بوشهر،سنگی شرقی،بلوار بهشت صادق،خ. توحید،خ. شبنم پنج',
    "FARS": 'شیراز،منطقه هشت،سنگ سیاه،م. احمدی،خ. هفت پیچ،ک. ابطحی',
    "HORMOZGAN": 'بندرعباس،چهارباغ،بلوار امام خمینی،خ. ماهان',
    "KERMAN": 'کرمان،بل جهاد بین خ مفتح و خ بهشتی',
    "SISTAN&BALOCHESTAN": 'زاهدان،خ. خرمشهر ۳۵، نبش بلوار خرمشهر',
    "ALBORZ": 'کرج،اسلام آباد،خ. برغان،خ. دکتر همایون',
    "TEHRAN": 'تهران،خ. انقلاب بین چهارراه ولیعصر تا دانشگاه',
}


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

async def handle_request(request):

    #print(request.url)

    return await request.continue_()

async def handle_response(response):
    lastTwoChars = response.url[-2:]
    if lastTwoChars == '/1' or lastTwoChars == '/2' or lastTwoChars == '/3' or lastTwoChars == '/4' \
            or lastTwoChars == '/5':
        response_text = await response.text()
        print(response.url, response_text)
        dfProvinceCategoryJson = pd.read_json(response_text) # now pandas can understand it (doesn't accept json object)
        serviceCategoryIndex = int(lastTwoChars[-1:])  # extracting the index only
        dfProvinceCategoryJson['Category'] = serviceCategory[serviceCategoryIndex] # adding the category column manualy to the DF.
        #print(dfProvinceCategoryJson)
        dfListProvincesCategoriesData.append(dfProvinceCategoryJson)

    #return await response.continue_()

#async def retryTillNoException():

async def main():
    #browser = await launch()
    browser = await launch(
        ignoreHTTPSErrors=True,
        args=['--no-sandbox'],
    )
    page = await browser.newPage()

    await page.setRequestInterception(True)
    page.on('request', lambda req: asyncio.ensure_future(handle_request(req)))
    page.on('response', lambda res: asyncio.ensure_future(handle_response(res)))

    await page.goto('https://netsanjplus.ir/index.html?operatorid=27&serviceid=31')
    print('started')
    await page.waitFor(10000)

    for key in province_address:
        print('Getting quality data for the province : ', key, '...')

        address = province_address[key]
        province_completed = False
        while not province_completed:
            #try:
            # await page.waitForSelector(selector=r'i[class="fad fa-edit"]')
            # await page.click(selector=r'i[class="fad fa-edit"]')

            #await page.waitForSelector(selector=r'#root > div > div.right-panel > div > div.report-summarize > div.report-summarize--flex > div.report-summarize-actions > button.button.button-primary.report-summarize-button > span')
            await page.waitFor(1000)
            await page.click(
                selector=r'#root > div > div.right-panel > div > div.report-summarize > div.report-summarize--flex > div.report-summarize-actions > button.button.button-primary.report-summarize-button > span')

            # await page.waitForSelector(selector=r'i[class="large-icon fal fa-times"]')
            # await page.click(selector=r'i[class="large-icon fal fa-times"]')
            #await page.waitForSelector(selector=r'#root > div > div.right-panel > div > div.search > div > div > button:nth-child(4) > i')
            await page.waitFor(1000)
            await page.click(
                selector=r'#root > div > div.right-panel > div > div.search > div > div > button:nth-child(4) > i')

            #await page.waitForSelector(selector=r'input[class="searchbox--input pm-search-input"]')
            await page.waitFor(1000)
            await page.focus(selector=r'input[class="searchbox--input pm-search-input"]')
            await page.type(selector=r'input[class="searchbox--input pm-search-input"]'
                            , text=address)

            keyboard: input.Keyboard = page.keyboard
            await keyboard.press(key='Enter')

            #await page.waitForSelector(selector=r'#root > div > div.right-panel > div > div.actions-layout > button')
            await page.waitFor(3000)
            await page.click(selector=r'#root > div > div.right-panel > div > div.actions-layout > button')
            # await page.click(selector=r'i[class="fa fa-file-chart-line small-icon pl5"]')

            # await page.click(selector=r'button[class="button button-primary"]')
            # await page.waitForSelector(selector='i[class="fal fa-globe smaller-icon"]')
            # await page.click(selector='i[class="fal fa-globe smaller-icon"]')
            # await page.waitForSelector(selector='#root > div > div.right-panel > div > div.tab > div:nth-child(3) > div')
            await page.waitFor(5000)
            #await page.waitForSelector(selector='#root > div > div.right-panel > div > div.tab > div:nth-child(3)')
            #await page.click(selector='#root > div > div.right-panel > div > div.tab > div:nth-child(3) > div')
            await page.click(selector='#root > div > div.right-panel > div > div.tab > div:nth-child(3)')

            # await page.click(selector='i[class="fal fa-globe smaller-icon"]')

            # await page.waitForSelector(selector=r'i[class="fal internet-quality--icon-webrank smaller-icon"]')
            # #    await page.click(selector=r'i[class="fal internet-quality--icon-webrank smaller-icon"]')
            # await page.hover(selector=r'i[class="fal internet-quality--icon-downloadrank smaller-icon"]')
            # await page.focus(selector=r'i[class="fal internet-quality--icon-downloadrank smaller-icon"]')
            # await page.click(selector=r'i[class="fal internet-quality--icon-downloadrank smaller-icon"]')
            # await page.waitFor(1000)
            # element: element_handle.ElementHandle = await page.querySelector(
            #     selector=r'i[class="fal internet-quality--icon-downloadrank smaller-icon"]')
            # await element.click()
            await page.waitFor(500)

            await page.waitForSelector(selector=r'#root > div > div.right-panel > div > div.scroll-layout.report-content.report-internet-quality > div:nth-child(2) > div.content-box--content > div.tab.--count5 > div.tab-content.--focused > div')
            await page.click(
                selector='#root > div > div.right-panel > div > div.scroll-layout.report-content.report-internet-quality > div:nth-child(2) > div.content-box--content > div.tab.--count5 > div:nth-child(3) > div')
            await page.waitFor(500)
            # await page.screenshot({'path': 'netsanj-gaming.png'})

            await page.waitForSelector(selector=r'#root > div > div.right-panel > div > div.scroll-layout.report-content.report-internet-quality > div:nth-child(2) > div.content-box--content > div.tab.--count5 > div:nth-child(4) > div')
            await page.click(
                selector='#root > div > div.right-panel > div > div.scroll-layout.report-content.report-internet-quality > div:nth-child(2) > div.content-box--content > div.tab.--count5 > div:nth-child(4) > div')
            await page.waitFor(500)
            # await page.screenshot({'path': 'netsanj-voip.png'})

            await page.waitForSelector(selector=r'#root > div > div.right-panel > div > div.scroll-layout.report-content.report-internet-quality > div:nth-child(2) > div.content-box--content > div.tab.--count5 > div:nth-child(5) > div')
            await page.click(
                selector='#root > div > div.right-panel > div > div.scroll-layout.report-content.report-internet-quality > div:nth-child(2) > div.content-box--content > div.tab.--count5 > div:nth-child(5) > div')
            await page.waitFor(500)
            # await page.screenshot({'path': 'netsanj-download.png'})

            await page.waitForSelector(selector=r'#root > div > div.right-panel > div > div.scroll-layout.report-content.report-internet-quality > div:nth-child(2) > div.content-box--content > div.tab.--count5 > div:nth-child(6) > div')
            await page.click(
                selector='#root > div > div.right-panel > div > div.scroll-layout.report-content.report-internet-quality > div:nth-child(2) > div.content-box--content > div.tab.--count5 > div:nth-child(6) > div')
            await page.waitFor(500)
            # await page.screenshot({'path': 'netsanj-web.png'})

            # await page.waitForSelector(selector=r'#root > div > div.right-panel > div > div.scroll-layout.report-content.report-internet-quality > div:nth-child(2) > div.content-box--content > div.tab.--count5 > div:nth-child(2) > div')
            # await page.click(selector='#root > div > div.right-panel > div > div.scroll-layout.report-content.report-internet-quality > div:nth-child(2) > div.content-box--content > div.tab.--count5 > div:nth-child(2) > div')
            # await page.waitFor(500)
            # await page.screenshot({'path': 'netsanj-b2b.png'})

            province_completed = True
            # except:
            #     print('An Exception occurred when trying to get the data for the province : ', key, ', retrying...')

    print('Now concatenating all...')

    dfAllProvinces = pd.concat(dfListProvincesCategoriesData, axis=0, ignore_index=True)

    print('Finished concatenating all:')
    print(dfAllProvinces)

    absPath = os.path.dirname(os.path.abspath(__file__))
    completeFilePath = absPath + r'\Internet_Quality_All_Provinces.csv'
    dfAllProvinces.to_csv(completeFilePath, index=False, encoding='utf-8-sig')

    await page.waitFor(2000)

    print('finished')
    await browser.close()


dfAllProvinces = pd.DataFrame()
dfListProvincesCategoriesData = []

#asyncio.get_event_loop().run_until_complete(main('همدان،خیابان تختی،بلوار چهارباغ دکتر مفتح،بلوار شهدا'))
#asyncio.get_event_loop().run_until_complete(main('زاهدان،گلستان،بلوار امام خمینی،بلوار امیرالمومنین'))
#asyncio.get_event_loop().run_until_complete(main('تبریز،منطقه سه،مقصودیه،بلوار هفده شهریور،خ. حاج نایب'))
asyncio.get_event_loop().run_until_complete(main())



