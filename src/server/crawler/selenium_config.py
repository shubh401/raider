from copy import deepcopy
from datetime import date

import traceback
import argparse
import aiohttp
import asyncio
import logging
import shutil
import json
import sys
import os

MODULE = os.getenv("MODULE")
DATASET = os.getenv("DATASET")
EXTENSION_TYPE = os.getenv("EXTENSION_TYPE")
MAX_RETRIES = 10
TMP_DIR = "/tmp/"
MULTI_TEST_TYPE = os.getenv("MULTI_TEST_TYPE")
ATTACKERURL = f"https://testserver.com:11000/"
TABLE_SUFFIX = date.today().strftime("%Y%m%d")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    filename=f"./logs/dynamic/{TABLE_SUFFIX}/{DATASET}_runtime.log",
    filemode="a+"
)
logging.getLogger("urllib3").setLevel(logging.ERROR)

CHROME_EXTENSION_DIR, FIREFOX_EXTENSION_DIR = None, None
CHROME_EXTENSION_DIR = f"/root/datasets/{DATASET}/"
FIREFOX_EXTENSION_DIR = f"/root/datasets/{DATASET}/"
CRAWL_TIMEOUT = 60
NAVIGATION_TIMEOUT = 30
WAIT_TIMEOUT = 10
VIEWPORT_SIZE = { "width": 1920, "height": 1080 }

CHROME_LAUNCH_ARGS = {
    "headless": False,
    "timeout": 30000,
    "ignoreHTTPSErrors": True,
    "args": [
        '--headless=new',
        '--disable-gpu',        
        '--no-sandbox',
        '--no-zygote',
        '--no-first-run',
        '--start-maximized',
        '--disable-dev-shm-usage',
        '--ignore-certificate-errors',
        '--allow-running-insecure-content',
        '--ignore-certificate-errors-spki-list',
        f"--unsafely-treat-insecure-origin-as-secure=http://testserver.com:11000/",
        '--allow-future-manifest-version',
        '--allow-legacy-extension-manifests',
    ]
}

FIREFOX_LAUNCH_ARGS = {
    "headless": False,
    "timeout": 30000,
    "ignoreHTTPSErrors": True,
    "args": [
        '--no-sandbox',
        '--no-zygote',
        '--no-first-run',
        '--start-maximized',
        '--disable-infobars',
        '--disable-dev-shm-usage',
        '--disable-setuid-sandbox',
        '--ignore-certificate-errors',
        '--disable-software-rasterizer',
        '--allow-running-insecure-content',
        '--ignore-certificate-errors-spki-list',
        f"--unsafely-treat-insecure-origin-as-secure=http://testserver.com:11000/",
        '--disable-gpu',
        '--allow-future-manifest-version',
        '--allow-legacy-extension-manifests',
    ],
    "firefoxUserPrefs": {
        'devtools.debugger.remote-enabled': True,
        'devtools.debugger.prompt-connection': False,
    },
}

URL_COMBINATIONS = [
    "http://testserver.com:11000/verify/",
    "http://testserver.com:11000/verify/carnus/",
    "https://testserver.com:11010/verify/",
    "https://testserver.com:11010/verify/carnus/"
]
