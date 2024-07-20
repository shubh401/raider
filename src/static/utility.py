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

from files import absolute_file_path_from_dir, list_of_files
from config import *

import jsbeautifier
import retirejs

def grep_invocations(script_path_list: list, target_apis: list, extension_id: str) -> list:
    invocations = []
    try:
        for script_path in script_path_list:
            if isinstance(script_path, list): script_path = script_path[0]
            parser_process = subprocess.Popen(["node", JS_PARSER, script_path], stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
            script_data = parser_process.stdout.read().decode().strip().lower()
            if script_data is None or script_data == "":
                return invocations
            for api in target_apis:
                if api.lower() in script_data:
                    invocations.append(api)
    except:
        logging.error("[UTILITY] Error in grep_invocations(): " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    finally:
        return invocations

def merge_scripts(scripts: str, source_dir: str, target_file: str, extension_id: str) -> None:
    try:
        if scripts:
            if os.path.exists(source_dir + extension_id + "/" + target_file):
                os.remove(source_dir + extension_id + "/" + target_file)
            file_list = list_of_files(source_dir + extension_id, extension_id)
            with open(source_dir + extension_id + "/" + target_file, "w") as nfh:
                for script in scripts:
                    absolute_path = script
                    if script and not script.startswith(source_dir):
                        absolute_path = absolute_file_path_from_dir(file_list, source_dir, extension_id, script, extension_id)
                    if absolute_path != "":
                        data = open(absolute_path, 'r', errors='ignore').read()
                        data = jsbeautifier.beautify(data)
                        nfh.write(data)
                nfh.close()
    except:
        logging.error("[UTILITY] Error in merge_scripts(): " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))

def detect_libraries(scripts: list, extension_id: str) -> list:
    try:
        idx = 0
        while True:
            if scripts is None or idx >= len(scripts):
                break
            elif len(retirejs.scan_filename(scripts[idx])) or "jquery" in scripts[idx]:
                del scripts[idx]
            else:
                idx += 1
                continue
    except:
        logging.error("[UTILITY] Error while detecting libraries for script:" + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))

def filter_wars(war_scripts, cs_hosts, manifest_processed_urls, has_scripting_perm, extension_id):
    wars = deepcopy(war_scripts)
    try:
        if "<all_urls>" in manifest_processed_urls and has_scripting_perm:
            return war_scripts
        if "<all_urls>" in cs_hosts:
            return war_scripts
        for script, hosts in wars.items():
            if "unknown" in hosts: del war_scripts[script]
    except:
        logging.error("[UTILITY] Error while filtering unnecssary WAR scripts:" + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    return war_scripts