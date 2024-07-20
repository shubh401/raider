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

from postprocessor import *
from extractor import *
from manifest import *
from utility import *
from config import *
from files import *
from urls import *
from db import *

from tqdm import tqdm

import multiprocessing as mp

class Processor:
    def __init__(self, extension_id):
        self.extension_id = extension_id
        self.is_ns_test_required = False
        self.is_dynamic_url_found = False
        self.perm_bits = [False, False, False, False]
        self.https_hosts_bits = [False, False, False]
        self.bg_absolute_paths, self.bg_filtered_scripts = defaultdict(), []
        self.cs_absolute_paths, self.cs_invocations, self.cs_filtered_scripts, self.cs_hosts = defaultdict(), [], [], []
        self.war_absolute_paths ,self.war_invocations, self.war_filtered_scripts = defaultdict(), [], [] 

    def extract_extension(self):
        try:
            if extract_package(self.extension_id):
                if self.extension_id.endswith(".tar.gz"):
                    self.extension_id = self.extension_id.split(".tar.gz")[0]
                elif '.' in self.extension_id: self.extension_id = self.extension_id[:-4]
                self.file_list = list_of_files(UNZIPPED_DIR, self.extension_id)
                return True
        except:
            logging.error("[PROCESSOR] Error in extract_extension(): " + self.extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
        return False

    def read_manifest(self):
        try:
            self.manifest_content = get_manifest(UNZIPPED_DIR + self.extension_id + "/manifest.json", self.extension_id)
            if not self.manifest_content or "app" in self.manifest_content.keys() or "theme" in self.manifest_content.keys():
                return False
            return True
        except:
            logging.error("[PROCESSOR] Error in read_manifest(): " + self.extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
            return False

    def manifest_urls(self):
        try:
            if "manifest_version" not in self.manifest_content.keys() or self.manifest_content["manifest_version"] == 2:
                manifest_hosts = manifest_v2_host_permissions(self.manifest_content, self.extension_id)
            else: manifest_hosts = manifest_v3_host_permissions(self.manifest_content, self.extension_id)
            manifest_url_dict = preprocess_urls(manifest_hosts, self.extension_id)
            self.manifest_processed_urls = list(manifest_url_dict.values())
            self.https_hosts_bits[0] = is_host_https_only(manifest_url_dict, self.extension_id)
        except:
            logging.error("[PROCESSOR] Error in manifest_urls(): " + self.extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))

    def handle_background_scripts(self):
        try:
            self.bg_scripts = get_background_scripts(self.manifest_content, self.extension_id)
            if self.bg_scripts: self.process_background_scripts()
        except:
            logging.error("[PROCESSOR] Error in handle_background_scripts(): " + self.extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))

    def process_background_scripts(self):
        try:
            if "<all_urls>" in self.manifest_processed_urls:
                for script in self.bg_scripts:
                    bg_absolute_path, filtered = absolute_path_of_scripts([script], self.file_list, UNZIPPED_DIR, self.extension_id)
                    if bg_absolute_path:
                        if script.endswith("htm") or script.endswith("html"):
                            for scr in bg_absolute_path:
                                self.bg_absolute_paths[scr] = scr
                        else: self.bg_absolute_paths[script] = bg_absolute_path
                    elif filtered: self.bg_filtered_scripts.extend(filtered)

                has_storage_perm = has_api_permissions(self.manifest_content, ["storage"], self.extension_id)
                has_storage_perm = has_storage_perm or has_api_permissions(self.manifest_content, ["unlimitedStorage"], self.extension_id)
                has_cookies_perm = has_api_permissions(self.manifest_content, ["cookies"], self.extension_id)
                has_scripting_perm = has_api_permissions(self.manifest_content, ["scripting", "tabs", "activeTab"], self.extension_id)
                has_webRequest_perm = has_api_permissions(self.manifest_content, ["webRequest", "webRequestBlocking", "webRequestAuthProvider", "declarativeNetRequest", "declarativeNetRequestWithHostAccess", "declarativeNetRequestFeedback"], self.extension_id)
                self.perm_bits = [has_cookies_perm, has_scripting_perm, has_storage_perm, has_webRequest_perm]
        except:
            logging.error("[PROCESSOR] Error in process_background_scripts(): " + self.extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    
    def handle_content_scripts(self):
        try:
            self.cs_scripts = get_content_scripts(self.manifest_content, self.file_list, "content_scripts", "js", self.extension_id, UNZIPPED_DIR)
            if self.cs_scripts: 
                self.cs_absolute_paths, self.cs_invocations, self.cs_filtered_scripts, self.https_hosts_bits[1] = self.process_other_scripts(self.cs_scripts, "cs")
        except:
            logging.error("[PROCESSOR] Error in handle_content_scripts(): " + self.extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))

    def process_other_scripts(self, scripts, type=""):
        https_hosts_bit = False
        absolute_paths, invocations, filtered_scripts = {}, [], []
        try:
            for script, hosts in scripts.items():
                processed_hosts_dict = preprocess_urls(hosts, self.extension_id)
                if type == "cs": self.cs_hosts.extend(processed_hosts_dict.values())
                https_hosts_bit = https_hosts_bit or is_host_https_only(processed_hosts_dict, self.extension_id)
                script_absolute_path, filtered = absolute_path_of_scripts([script], self.file_list, UNZIPPED_DIR, self.extension_id)
                if script_absolute_path and ("<all_urls>" in processed_hosts_dict.values() or "unknown" in processed_hosts_dict.values()):
                    absolute_paths[script] = script_absolute_path
                    inv = grep_invocations(script_absolute_path, FINGERPRINTABLE_APIS, self.extension_id)
                    if inv: invocations.extend(inv)
                    else: invocations.extend(["only <all_urls>"])
                elif filtered: filtered_scripts.extend(filtered)
        except:
            logging.error("[PROCESSOR] Error in process_other_scripts(): " + self.extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
        return absolute_paths, invocations, filtered_scripts, https_hosts_bit

    def handle_war_scripts(self):
        try:
            self.war_scripts, self.is_dynamic_url_found = get_resources(self.manifest_content, self.file_list, "web_accessible_resources", "resources", self.extension_id, UNZIPPED_DIR)
            if self.war_scripts:
                self.war_scripts = filter_wars(self.war_scripts, self.cs_hosts, self.manifest_processed_urls, self.perm_bits[2], self.extension_id)
                if self.war_scripts:
                    self.is_ns_test_required = True
                    self.war_absolute_paths, self.war_invocations, self.war_filtered_scripts, self.https_hosts_bits[2] = self.process_other_scripts(self.war_scripts)
        except:
            logging.error("[PROCESSOR] Error in handle_war_scripts(): " + self.extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
        
    def attribute_script_type(self, absolute_paths):
        script_types = defaultdict()
        try:
            bg, cs, war = set(self.bg_scripts), set(self.cs_scripts.keys()), set(self.war_scripts.keys())
            for script in set(bg & cs & war):
                if script in absolute_paths:
                    for scr in absolute_paths[script]: script_types[scr] = Script.CS_BG_WAR.value
                elif "*" not in script: script_types[script] = Script.CS_BG_WAR.value
                bg.remove(script)
                cs.remove(script)
                war.remove(script)

            for script in set(cs & war):
                if script in absolute_paths:
                    for scr in absolute_paths[script]: script_types[scr] = Script.CS_WAR.value
                cs.remove(script)
                war.remove(script)

            for script in set(bg & cs):
                if script in absolute_paths:
                    for scr in absolute_paths[script]: script_types[scr] = Script.CS_BG.value
                bg.remove(script)
                cs.remove(script)

            for script in set(bg & war):
                if script in absolute_paths:
                    for scr in absolute_paths[script]: script_types[scr] = Script.BG_WAR.value
                bg.remove(script)
                war.remove(script)

            for script in set(cs):
                if script in absolute_paths:
                    for scr in absolute_paths[script]: script_types[scr] = Script.CS.value
                cs.remove(script)

            for script in set(war):
                if script in absolute_paths:
                    for scr in absolute_paths[script]:
                        if scr in script_types.keys(): continue
                        script_types[scr] = Script.WAR.value
                war.remove(script)

            for script in set(bg):
                if script in absolute_paths:
                    for scr in absolute_paths[script]:
                        if scr in script_types.keys(): continue
                        script_types[scr] = Script.BG.value
                bg.remove(script)
        except:
            logging.error("[PROCESSOR] Error in attribute_script_type(): " + self.extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
        return script_types

    def start_processing(self):
        invocations = []
        try:
            if not self.extract_extension() or not self.read_manifest():
                return (None, None, None, None, None, None, None, None, None, None)
            self.manifest_urls()
            self.handle_background_scripts()
            self.handle_content_scripts()
            self.handle_war_scripts()

            absolute_paths = self.cs_absolute_paths
            absolute_paths.update(self.war_absolute_paths)
            script_types = self.attribute_script_type(absolute_paths)
            if script_types:
                filtered_scripts = defaultdict()
                filtered_scripts["bg"] = self.bg_filtered_scripts
                filtered_scripts["cs"] = self.cs_filtered_scripts
                filtered_scripts["war"] = self.war_filtered_scripts
                https_bit = self.https_hosts_bits[0] or self.https_hosts_bits[1] or self.https_hosts_bits[2]
                store_extension_state(self.extension_id, script_types, filtered_scripts, https_bit)

            invocations = list(set(self.cs_invocations).union(set(self.war_invocations)))
            if invocations:
                copy_extension_dir(UNZIPPED_DIR, CS_EXTENSIONS_DIR, self.extension_id)
            elif self.cs_absolute_paths and self.cs_filtered_scripts:
                copy_extension_dir(UNZIPPED_DIR, CS_EXTENSIONS_DIR, self.extension_id)
            elif self.war_absolute_paths and self.war_filtered_scripts:
                copy_extension_dir(UNZIPPED_DIR, CS_EXTENSIONS_DIR, self.extension_id)
            elif "<all_urls>" in self.manifest_processed_urls and (self.perm_bits[0] or self.perm_bits[1] or self.perm_bits[3]):
                copy_extension_dir(UNZIPPED_DIR, CS_EXTENSIONS_DIR, self.extension_id)
            elif "<all_urls>" in self.manifest_processed_urls and "devtools_page" in self.manifest_content.keys() and self.manifest_content["devtools_page"] is not None:
                copy_extension_dir(UNZIPPED_DIR, CS_EXTENSIONS_DIR, self.extension_id)
        except:
            logging.error("[PROCESSOR] Error in start_processing(): " + self.extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
        finally:
            return (invocations, self.https_hosts_bits[0], self.https_hosts_bits[1] or self.https_hosts_bits[2], self.perm_bits[0], self.perm_bits[1], self.perm_bits[2],  self.perm_bits[3], self.is_ns_test_required, self.is_dynamic_url_found, self.extension_id)

def start(extension_id):
    try:
        extension_instance = Processor(extension_id)
        return extension_instance.start_processing()
    except:
        logging.error(f"[PROCESSOR] Error while instantiating processor for extension - {extension_id} - ", "; ".join(traceback.format_exc().split("\n")))
    return (None, None, None, None, None, None, None, None)

def initialize_dir() -> None:
    try:
        if not os.path.exists(UNZIPPED_DIR): os.makedirs(UNZIPPED_DIR, exist_ok=True)
        if os.path.exists(CS_EXTENSIONS_DIR): shutil.rmtree(CS_EXTENSIONS_DIR)
        os.mkdir(CS_EXTENSIONS_DIR)
        if os.path.exists(LOGS): shutil.rmtree(LOGS)
        os.mkdir(LOGS)
    except:
        logging.error("[PROCESSOR] Error while initializing directories - ", "; ".join(traceback.format_exc().split("\n")))

def init() -> None:
    content_script_invocations, scripting, cookies, storage, webRequest, cs_https, bg_https = {}, [], [], [], [], [], []
    wars, dyn_urls = [], []
    total_extensions = []
    try:
        total_extensions = os.listdir(RAW_EXTENSION_DIR)
        if len(total_extensions) and create_tables():
            logging.info("Static analysis started!")
            initialize_dir()
            
            with mp.Pool(processes=WORKERS, maxtasksperchild=1) as pool:
                for (cs_invocations, is_bg_host_https, is_cs_host_https, has_cookies_perm, has_scripting_perm, has_storage_perm, has_webRequest_perm, is_ns_test_required, is_dynamic_url_found, extension_id) in tqdm(pool.imap_unordered(start, total_extensions), total=len(total_extensions)):
                    if cs_invocations: content_script_invocations[extension_id] = cs_invocations
                    if has_cookies_perm: cookies.append(extension_id)
                    if has_scripting_perm: scripting.append(extension_id)
                    if has_storage_perm: storage.append(extension_id)
                    if has_webRequest_perm: webRequest.append(extension_id)
                    if is_ns_test_required: wars.append(extension_id)
                    if is_dynamic_url_found: dyn_urls.append(extension_id)
                    if is_bg_host_https: bg_https.append(extension_id)
                    if is_cs_host_https: cs_https.append(extension_id)
                    continue
            
            post_process(content_script_invocations, cookies, scripting, storage, webRequest, wars, dyn_urls, bg_https, cs_https)
            clean_directories(CS_EXTENSIONS_DIR)

            logging.info("Analysis completed!")
    except:
        logging.error("[PROCESSOR] Error at init() :( - " + "; ".join(traceback.format_exc().split("\n")))

if __name__ == "__main__":
    init()