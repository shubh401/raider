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
from datetime import date
import traceback
import logging
import hashlib
import json
import os

MODULE = os.getenv("MODULE")
DATASET = os.getenv("DATASET")
EXTENSION_TYPE = os.getenv("EXTENSION_TYPE")

TABLE_SUFFIX = date.today().strftime("%d%m%Y")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DB_PASS = os.getenv("DB_PASS")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    filename=f"./logs/dynamic/{DATASET}_server.log",
    filemode="a+"
)
logging.getLogger("urllib3").setLevel(logging.ERROR)

CONNECTION_INFO = f'hostaddr={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASS} sslmode=disable'

TEST_URL = "testserver.com"
