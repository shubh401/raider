# Copyright (C) 2024 Shubham Agarwal, CISPA.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from collections import defaultdict
from copy import deepcopy
from enums import Script

import subprocess
import traceback
import logging
import shutil
import json
import os

DATASET = os.getenv("DATASET")
WORKERS = int(os.getenv("WORKERS", 1))
EXTENSION_TYPE = os.getenv("EXTENSION_TYPE")

LOGS = f"./logs/static/{DATASET}_metadata/"
RAW_EXTENSION_DIR = f"./datasets/{DATASET}/"
UNZIPPED_DIR = f"./datasets/unzipped/{DATASET}/"
CS_EXTENSIONS_DIR = f"./datasets/unzipped/{DATASET}_filtered/"
API_PERMISSIONS = json.loads(open("./helpers/api_permissions.json", "r").read())

SCRIPT_INJECTION_APIS = ["registerContentScripts", "updateContentScripts", "executeScript"]
COOKIE_APIS = ["cookies.get", "cookies.getall", "cookies.getallcookiestores", "cookies.remove", "cookies.set", "cookies.onchanged"]
FINGERPRINTABLE_APIS = ["document.cookie", "indexedDB", "idb", "localStorage.setItem", "localStorage.getItem", "localStorage[", "localStorage.", "sessionStorage.", "sessionStorage.setItem", "sessionStorage.getItem", "sessionStorage[", "window.addEventListener", "addEventListener", "window.postMessage", "postMessage", "createElement('script')", 'createElement("script")', "appendChild"]
HEADER_APIS = ["onBeforeSendHeaders", "onHeadersReceived", "updateDynamicRules", "updateStaticRules"]

MAX_JS_SIZE = 30000000
JS_BLACKLISTS = ["node_modules", 'jquery', 'angular', 'fontawesome', 'bootstrap', "react-dom", "socker.io", "vue", "jsencrypt", "mathjs", "sugar", "react", "lodash", "unidecode", "scc1t2", "ace-builds/src/theme-", "ace-builds/src/snippets/", "ace/src/theme-", "ace/src/snippets/", "ace/theme-", "ace/snippets/", "languages/", "locales/", "/ptk/packages/"]

CRX_UNPACKER = "./helpers/unpack_crx.js"
JS_PARSER = "./helpers/js_parser.js"
FILE_PATH_SUBSTITUTE = "*://127.0.0.1:9000"
UNZIP_TIMEOUT = 600

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DB_PASS = os.getenv("DB_PASS")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    filename=f"./logs/static/{DATASET}_static.log",
    filemode="a+"
)
logging.getLogger("urllib3").setLevel(logging.ERROR)
