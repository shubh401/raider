from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium_config import *

URL = None
VISIT = None
EXTENSION_ID = ""
OTHER_EXTENSIONS = None

async def send_data(extensions_list):
    try:
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.request(method="POST", url= f"http://testserver.com:11000/verify/sel", data=json.dumps({"extension_id": EXTENSION_ID, "other_extensions": extensions_list}), connector=connector) as _:
            pass
    except:
        logging.error(f""" Error while sending execution data while testing for extension: {EXTENSION_ID} : %s.\n""" % '; '.
join(str(traceback.format_exc()).split('\n')))

async def browse(browser, url):
    try:
        browser.get(url)
        await asyncio.sleep(WAIT_TIMEOUT)
        try: browser.get("about:blank")
        except: pass
    except:
        raise Exception(f"""Couldn't successfully visit for extension: {EXTENSION_ID}.""")

async def detect_extension(driver):
    try:
        driver.get('chrome://extensions')
        try:
            driver.save_screenshot(f"./screenshots_{TABLE_SUFFIX}/{EXTENSION_ID}_{VISIT}.png")
        except: pass
        extensions_list = driver.execute_script('''return [...document.querySelectorAll('body > extensions-manager')[0]
                                                .shadowRoot.querySelector('#items-list')
                                                .shadowRoot.querySelectorAll('extensions-item')].map(elem => elem.id);''')
        try: await send_data(extensions_list)
        except: pass
        if len(extensions_list) > 0: return True
    except:
        logging.error(f""" Error while loading or detecting extension: {EXTENSION_ID} : %s.\n""" % '; '.join(str(traceback.format_exc()).split('\n')))
    return False

async def get_browser_context():
    browser = None
    try:
        launch_arg = deepcopy(CHROME_LAUNCH_ARGS)
        
        options = Options()
        options.add_argument(f"--user-data-dir=/mnt/tmp/{EXTENSION_ID}")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
        options.add_extension(CHROME_EXTENSION_DIR + EXTENSION_ID + ".crx")
        for extension in OTHER_EXTENSIONS:
            options.add_extension(CHROME_EXTENSION_DIR + extension + ".crx")
        for arg in launch_arg["args"]: options.add_argument(arg)

        options.page_load_strategy = 'eager'
        options.accept_insecure_certs = True
        browser = webdriver.Chrome(options=options)
        browser.set_window_size(1920, 1080)
        browser.set_page_load_timeout(CRAWL_TIMEOUT)
        if browser and not await detect_extension(browser):
            browser.close()
            browser = None
    except:
        logging.error(f""" Error while instantiating browser context for extension: {EXTENSION_ID} : %s.\n""" % '; '.join(str(traceback.format_exc()).split('\n')))
    return browser

async def execute_crawl():
    retrial = 0
    try:
        while True:
            try:
                target_dir = os.path.join(TMP_DIR, EXTENSION_ID)
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)

                # Browse on second visit to avoid unnecessary popups whenever possible.
                browser = await get_browser_context()
                if not browser: raise Exception(f"Context could not be created successfuly for extension: {EXTENSION_ID}")
                for url in URL_COMBINATIONS:
                    await browse(browser, f"{url}?&visit={VISIT}&extensionId={EXTENSION_ID}&browser=chrome&dataset={DATASET}")
                browser.quit()
                break
            except:
                if browser: browser.quit()
                if retrial < MAX_RETRIES: retrial += 1
                else:
                    logging.error(f"""Couldn't succesfully visit for extension: {EXTENSION_ID} : %s.\n""" % '; '.join(str(traceback.format_exc()).split('\n')))
                    break
        if browser: browser.quit()
    except: logging.error(f""" Error while executing crawl for extension: {EXTENSION_ID} : %s.\n""" % '; '.join(str(traceback.format_exc()).split('\n')))

async def parse_arguments():
    global DATASET
    global VISIT
    global URL
    global EXTENSION_ID
    global OTHER_EXTENSIONS

    try:
        parser = argparse.ArgumentParser(description='Crawler Runtime Args')
        parser._action_groups.pop()
        required_args = parser.add_argument_group('Required arguments')
        required_args.add_argument("-e", "--extension_id", help="Please provide the actual extension id under test.", required=True, type=str)
        required_args.add_argument("-v", "--visit", help="Please provide the visit id under test.", required=True, type=str)
        required_args.add_argument("-u", "--url", help="Please provide the test URL endpoint.", required=True, type=str)
        required_args.add_argument("-o", "--others", help="Please provide the list of other extensions for multi-test.", required=True, type=str)
        required_args.add_argument("-d", "--dataset", help="Please provide the corresponding dataset for the extension uner test.", required=True, type=str)
        args = parser.parse_args()

        DATASET = args.dataset
        VISIT = args.visit
        URL = args.url
        EXTENSION_ID = args.extension_id
        OTHER_EXTENSIONS = json.loads(args.others)
    except:
        logging.error(f""" Invalid arguments passed! : %s.\n""" % '; '.join(str(traceback.format_exc()).split('\n')))
        sys.exit(1)

async def init():
    try:
        await parse_arguments()
        await execute_crawl()
        if os.path.exists(TMP_DIR + EXTENSION_ID):
            try: os.system(f"rm -rf {TMP_DIR + EXTENSION_ID}")
            except: pass
    except: logging.error(f""" Error in init() for extension: {EXTENSION_ID} : %s.\n""" % '; '.join(str(traceback.format_exc()).split('\n')))

async def main():
    await init()

asyncio.run(main())
