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

def group_extensions_per_api(invocation_data: dict, data_type: str) -> dict:
    grouped_api_data = defaultdict(list)
    try:
        with open(f"{LOGS}{data_type}_invocations.json", "w") as fh:
            json.dump(invocation_data, fh, indent = 4)
        for extension_id, invocations in invocation_data.items():
            for api in invocations:
                grouped_api_data[api].append(extension_id)
            
        if grouped_api_data:
            with open(f"{LOGS}{data_type}_api_data.json", "w") as fh:
                json.dump(grouped_api_data, fh, indent = 4)
    except:
        logging.error("[POST-PROCESSOR] Error while grouping invocations data" + ", ".join(traceback.format_exc().split("\n")))
    return

def handle_other_data(data: list, file_name: str) -> None:
    try:
        if data:
            with open(f"{LOGS}{file_name}.json", "w") as fh:
                json.dump(data, fh, indent = 4)
    except:
        logging.error("[POST-PROCESSOR] Error while handling header analysis data" + ", ".join(traceback.format_exc().split("\n")))

def post_process(content_script_invocations: dict, cookies: list, scripting: list, storage: list, webRequest: list, wars: list, dyn_urls: list, bg_https: list, cs_https: list) -> None:
    try:
        print("Post-processing data storage in progress, please do not terminate the program!")
        group_extensions_per_api(content_script_invocations, "cs")
        handle_other_data(cookies, "cookies_perm")
        handle_other_data(scripting, "scripting_perm")
        handle_other_data(webRequest, "webRequest_perm")
        handle_other_data(storage, "storage_perm")
        handle_other_data(wars, "wars")
        handle_other_data(dyn_urls, "war_dyn_urls")
        handle_other_data(bg_https, "https_bg")
        handle_other_data(cs_https, "https_cs")
    except:
        logging.error("[POSTPROCESSOR] Error in post_process(): " + ", ".join(traceback.format_exc().split("\n")))
