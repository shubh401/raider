from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium_firefox_config import *

URL = None
VISIT = None
EXTENSION_ID = ""

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
        driver.get('about:addons')
        driver.execute_script('document.getElementsByTagName("button")[1].click();')
        driver.save_screenshot(f"./screenshots_{TABLE_SUFFIX}/{EXTENSION_ID}_{VISIT}.png")
        return True
    except:
        logging.error(f""" Error while loading or detecting extension: {EXTENSION_ID} : %s.\n""" % '; '.join(str(traceback.format_exc()).split('\n')))
    return False

async def get_browser_context():
    global EXTENSION_ID
    browser = None
    try:
        launch_arg = deepcopy(FIREFOX_LAUNCH_ARGS)

        options = Options()
        options.add_argument("--headless")
        options.add_argument(f"--user-data-dir=/mnt/tmp/{EXTENSION_ID}")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
        for arg in launch_arg["args"]: options.add_argument(arg)
        options.accept_insecure_certs = True
        
        browser = webdriver.Firefox(options=options)
        browser.install_addon(FIREFOX_EXTENSION_DIR + EXTENSION_ID + ".xpi")
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
                if os.path.exists(TMP_DIR + EXTENSION_ID):
                    shutil.rmtree(TMP_DIR + EXTENSION_ID)

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
    global VISIT
    global URL
    global EXTENSION_ID

    try:
        parser = argparse.ArgumentParser(description='Crawler Runtime Args')
        parser._action_groups.pop()
        required_args = parser.add_argument_group('Required arguments')
        required_args.add_argument("-e", "--extension_id", help="Please provide the actual extension id under test.", required=True, type=str)
        required_args.add_argument("-v", "--visit", help="Please provide the visit id under test.", required=True, type=str)
        required_args.add_argument("-u", "--url", help="Please provide the test URL endpoint.", required=True, type=str)
        args = parser.parse_args()

        VISIT = args.visit
        URL = args.url
        EXTENSION_ID = args.extension_id
    except:
        logging.error(f""" Invalid arguments passed! : %s.\n""" % '; '.join(str(traceback.format_exc()).split('\n')))
        sys.exit(1)

async def init():
    try:
        await parse_arguments()
        await execute_crawl()
        if os.path.exists(TMP_DIR + EXTENSION_ID):
            shutil.rmtree(TMP_DIR + EXTENSION_ID)
    except: logging.error(f""" Error in init() for extension: {EXTENSION_ID} : %s.\n""" % '; '.join(str(traceback.format_exc()).split('\n')))

async def main():
    await init()

asyncio.run(main())
