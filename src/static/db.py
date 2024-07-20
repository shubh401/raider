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

from config import *
import psycopg2

def create_tables() -> bool:
    try:
        connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cursor = connection.cursor()
        cursor.execute("START TRANSACTION;")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS extension_state (id SERIAL PRIMARY KEY, extension_id VARCHAR(32), script VARCHAR(2048), script_type INT, is_hosts_https_only BOOL DEFAULT FALSE, is_analyzed BOOL DEFAULT FALSE, test_status SMALLINT DEFAULT 0, skipped BOOL DEFAULT FALSE, dataset VARCHAR(32) NOT NULL, tstamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS extension_state_ext_dat_test_status ON extension_state(extension_id, dataset, is_analyzed, test_status);")
        cursor.execute(f"DELETE FROM extension_state WHERE dataset = '{DATASET}';")
        cursor.execute("COMMIT;")
        connection.close()
        return True
    except:
        logging.error("[CONNECTOR] Error while creating tables: " + ", ".join(traceback.format_exc().split("\n")))
        return False

def store_extension_state(extension_id: str, extension_data: dict, filtered_scripts: list, is_hosts_https_only: bool) -> None:
    params = []
    try:
        if not extension_data: return
        for script, script_type in extension_data.items():
            if not script.startswith(UNZIPPED_DIR): script = UNZIPPED_DIR + extension_id + "/" + script
            params.append((extension_id, script, script_type, is_hosts_https_only, False, 0, DATASET, False))
        for script_type, scripts in filtered_scripts.items():
            if script_type == "cs": type = -1
            elif script_type == "bg": type = -2
            elif script_type == "war": type = -4
            for script in scripts:
                params.append((extension_id, script, type, is_hosts_https_only, False, 0, DATASET, True))
        if not params: return
        query = f""" INSERT INTO extension_state (extension_id, script, script_type, is_hosts_https_only, is_analyzed, test_status, dataset, skipped) VALUES (%s,%s,%s,%s,%s,%s,%s,%s); """
        connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cursor = connection.cursor()
        cursor.execute("START TRANSACTION;")
        cursor.executemany(query, params)
        cursor.execute("COMMIT;")
        connection.close()
    except:
        logging.error("[CONNECTOR] Error while storing jalangi state for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
