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

from zipfile import ZipFile
from config import *

def extract_crx(crx_id: str) -> bool:
    status = False
    try:
        if ".crx" not in crx_id and ".zip" not in crx_id and "tar.gz" not in crx_id:
            shutil.copytree(RAW_EXTENSION_DIR + crx_id, UNZIPPED_DIR + crx_id)
            return True
        if not os.path.exists(RAW_EXTENSION_DIR + crx_id):
            logging.warn("Error!: Package not found for extension: " + crx_id)
            return False
        if "_" in crx_id: new_crx_name = crx_id.split("_", 1)[0]
        else: new_crx_name = crx_id[:-4]
        
        if os.path.exists(UNZIPPED_DIR + new_crx_name): return True
        elif "tar.gz" in crx_id:
            new_crx_name = crx_id[:-7]
            unzip_process = subprocess.Popen(["tar", "-xzf", RAW_EXTENSION_DIR + crx_id, "-C", UNZIPPED_DIR], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            unzip_process.wait(UNZIP_TIMEOUT)
            unzip_output, unzip_error = unzip_process.stdout.read().decode(), unzip_process.stderr.read().decode()
            if "error" in unzip_output.lower() or unzip_error != '':
                status = False
            else: status = True
        else:
            unzip_process = subprocess.Popen(["node", CRX_UNPACKER, RAW_EXTENSION_DIR + crx_id, UNZIPPED_DIR + new_crx_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            unzip_output, unzip_error = unzip_process.stdout.read().decode(), unzip_process.stderr.read().decode()
            if unzip_output == "Error!":
                logging.error("[EXTRACTOR] Error while unzipping crx: " + crx_id)
                status = False
            elif "Does not start with Cr24" in unzip_error:
                status = False
            else: status = True
    except:
        logging.error("[EXTRACTOR] Error while extracting package for extension: " + crx_id + " - " + ", ".join(traceback.format_exc().split("\n")))
        status = False
    return status
        
def extract_xpi(xpi_id: str) -> bool:
    try:
        if not os.path.exists(RAW_EXTENSION_DIR + xpi_id):
            logging.warn("Error!: Package not found for extension: " + xpi_id)
            return False

        if os.path.exists(UNZIPPED_DIR + xpi_id[:-4]): return True
        with ZipFile(RAW_EXTENSION_DIR + xpi_id, 'r') as zip_file:
            os.mkdir(UNZIPPED_DIR + xpi_id[:-4])
            zip_file.extractall(UNZIPPED_DIR + xpi_id[:-4] + "/")
        return True
    except:
        logging.error("[EXTRACTOR] Error while extracting package for extension: " + xpi_id + " - " + ", ".join(traceback.format_exc().split("\n")))
        return False
   
def extract_package(extension_id: str) -> bool:
    if EXTENSION_TYPE == 'chrome':
        return extract_crx(extension_id)
    return extract_xpi(extension_id) 
