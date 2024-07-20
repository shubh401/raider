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

from files import absolute_file_path_from_dir, script_src_from_html, list_of_files
from jsoncomment import JsonComment
from typing import Tuple
from config import *

import jstyleson
import jsmin
import ast

def get_manifest(manifest_path: str, extension_id: str) -> Tuple[dict, None]:
    manifest_data = None
    try:
        if not os.path.exists(manifest_path):
            logging.warn("[MANIFEST] Serious issues in manifest for extension: " + extension_id)
            return None
        try:
            manifest = open(manifest_path, "r", encoding='utf-8-sig').read()
        except:
            manifest = open(manifest_path, "rb").read()
        if manifest is not None and manifest != "":
            try:
                manifest_data = json.loads(manifest)
            except:
                try:
                    manifest_data = ast.literal_eval(manifest)
                except:
                    try:
                        json_comment = JsonComment()
                        manifest_data = json_comment.loads(manifest)
                    except:
                        try:
                            manifest_data= jstyleson.loads(manifest)
                        except:
                            try:
                                minified = jsmin(manifest)
                                manifest_data = json.loads(minified)
                            except:
                                try:
                                    manifest = open(manifest_path, "r", encoding='utf-8-sig', errors='ignore').read()
                                    manifest_data = json.loads(manifest)
                                except:
                                    logging.warn("[MANIFEST] Serious issues in manifest for extension: " + extension_id)
                                    return None
        return manifest_data
    except:
        logging.error("[MANIFEST] Error while parsing the manifest for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))

def get_action_popups(manifest: str, extension_id: str):
    action_popups = []
    try:
        if manifest.get("page_action") and isinstance(manifest["page_action"], dict):
            popups = manifest["page_action"].get("default_popup")
            if isinstance(popups, str): action_popups.append(popups)
            elif isinstance(popups, list): action_popups.extend(popups)
        if manifest.get("browser_action") and isinstance(manifest["browser_action"], dict):
            popups = manifest["browser_action"].get("default_popup")
            if isinstance(popups, str): action_popups.append(popups)
            elif isinstance(popups, list): action_popups.extend(popups)
        if manifest.get("action") and isinstance(manifest["action"], dict):
            popups = manifest["action"].get("default_popup")
            if isinstance(popups, str): action_popups.append(popups)
            elif isinstance(popups, list): action_popups.extend(popups)
    except:
        logging.error("[MANIFEST] Error while extracting action popups from the manifest for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    return action_popups

def get_background_scripts(manifest_content: dict, extension_id: str) -> list:
    bg_scripts = []
    try:
        if manifest_content:
            if "background" in manifest_content.keys():
                if type(manifest_content["background"]) is str:
                    bg_scripts.extend(manifest_content["background"])
                    return bg_scripts
                elif type(manifest_content["background"]) is list:
                    for entry in manifest_content["background"]:
                        if isinstance(entry, str): bg_scripts.append(entry)
                        elif isinstance(entry, dict):
                            for key, value in entry.items():
                                if key in ["scripts", "page", "service_worker"]:
                                     bg_scripts.extend(value)
                elif type(manifest_content["background"]) is dict:
                    if "scripts" in manifest_content["background"].keys():
                        if type(manifest_content["background"]["scripts"]) is list:
                            bg_scripts.extend(manifest_content["background"]["scripts"])
                        elif type(manifest_content["background"]["scripts"]) is str:
                            bg_scripts.append(manifest_content["background"]["scripts"])
                    if "page" in manifest_content["background"].keys():
                        if type(manifest_content["background"]["page"]) is list:
                            bg_scripts.extend(manifest_content["background"]["page"])
                        elif type(manifest_content["background"]["page"]) is str:
                            bg_scripts.append(manifest_content["background"]["page"])
                    if "service_worker" in manifest_content["background"].keys():
                        if type(manifest_content["background"]["service_worker"]) is list:
                            bg_scripts.extend(manifest_content["background"]["service_worker"])
                        elif type(manifest_content["background"]["service_worker"]) is str:
                            bg_scripts.append(manifest_content["background"]["service_worker"])
            action_popups = get_action_popups(manifest_content, extension_id)
            if action_popups: bg_scripts.extend(action_popups)
    except:
        logging.error("[MANIFEST] Error while extracting background scripts from the manifest for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    finally:
        return bg_scripts

def get_content_scripts(manifest_content: dict, file_list: str, key: str, sub_key: str, source_dir: str, extension_id: str) -> dict:
    content_scripts = defaultdict(list)
    try:
        prerequisites = [manifest_content, key in manifest_content.keys() and type(manifest_content[key]) == list]
        if all(prerequisites):
            for entry in manifest_content[key]:
                if type(entry) == dict and sub_key in entry.keys() and "matches" in entry.keys():
                    for res in entry[sub_key]:
                        if isinstance(res, str) and ".js" in res and ".json" not in res:
                            content_scripts[res].extend(entry["matches"])
                elif isinstance(entry, str) and ".js" in entry and ".json" not in entry: content_scripts[entry].extend(["<all_urls>"])
                elif isinstance(entry, str) and (".htm" in entry):
                    html_path = absolute_file_path_from_dir(file_list, source_dir, extension_id, entry, extension_id)
                    html_script_src = script_src_from_html(html_path, extension_id)
                    if html_script_src:
                        for script in html_script_src: content_scripts[script].extend(["<all_urls>"])  
    except:
        logging.error("[MANIFEST] Error while extracting content scripts from the manifest for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    finally:
        return content_scripts

def get_resources(manifest_content: dict, file_list: str, key: str, sub_key: str, source_dir: str, extension_id: str) -> Tuple[dict, bool]:
    resources = defaultdict(list)
    is_dynamic_url_found = False
    try:
        war_prerequisites = [manifest_content, key in manifest_content.keys() and type(manifest_content[key]) == list]
        if all(war_prerequisites):
            for entry in manifest_content[key]:
                if type(entry) == dict and sub_key in entry.keys() and "matches" in entry.keys():
                    for res in entry[sub_key]:
                        if isinstance(res, str) and ".js" in res and ".json" not in res:
                            resources[res].extend(entry["matches"])
                        elif isinstance(res, str) and ".htm" in res:
                            html_path = absolute_file_path_from_dir(file_list, source_dir, extension_id, res, extension_id)
                            html_script_src = script_src_from_html(html_path, extension_id)
                            if html_script_src:
                                for script in html_script_src: resources[script].extend(entry["matches"])
                    if "use_dynamic_url" in entry.keys() and entry["use_dynamic_url"]:
                        is_dynamic_url_found = True
                elif isinstance(entry, str) and ".js" in entry and ".json" not in entry: resources[entry].extend(["unknown"])
                elif isinstance(entry, str) and ".htm" in entry:
                    html_path = absolute_file_path_from_dir(file_list, source_dir, extension_id, entry, extension_id)
                    html_script_src = script_src_from_html(html_path, extension_id)
                    if html_script_src:
                        for script in html_script_src: resources[script].extend(["unknown"])  
    except:
        logging.error("[MANIFEST] Error while extracting wars from the manifest for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    finally:
        return resources, is_dynamic_url_found

def has_api_permissions(manifest_content: dict, required_permissions: list, extension_id: str) -> bool:
    try:
        permissions = []
        preliminary_check = [manifest_content, "manifest_version" in manifest_content.keys()]
        if all(preliminary_check):
            if "permissions" in manifest_content.keys():
                permissions = manifest_content["permissions"]
            if any([perm in permissions for perm in required_permissions]):
                for perm in required_permissions:
                    if "optional_permissions" in manifest_content.keys() and perm in manifest_content["optional_permissions"]:
                        manifest_content["optional_permissions"].remove(perm)
                        if "permissions" not in manifest_content.keys(): manifest_content["permissions"] = []
                        manifest_content["permissions"].extend(perm)
                        if not len(manifest_content["optional_permissions"]):
                            del manifest_content["optional_permissions"]
                return True
        return False
    except:
        logging.error("[MANIFEST] Error while checking for relevant permissions for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))

def manifest_v2_host_permissions(manifest_content: dict, extension_id: str) -> list:
    host_permissions = []
    total_permissions  = []
    try:
        if not manifest_content: return []
        if "permissions" in manifest_content.keys() and type(manifest_content["permissions"]) is list:
            total_permissions.extend(manifest_content["permissions"])
        if "optional_permissions" in manifest_content.keys() and type(manifest_content["optional_permissions"]) is list:
            total_permissions.extend(manifest_content["optional_permissions"])
        if isinstance(total_permissions, list):
            for idx in range(0, len(total_permissions)):
                if isinstance(total_permissions[idx], dict):
                    total_permissions[idx] = list(total_permissions[idx].keys())[0]
            host_permissions = list(set(total_permissions) - set(API_PERMISSIONS))
    except:
        logging.error("[MANIFEST] Error while extracting host permissions from manifest for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    finally:
        return host_permissions

def manifest_v3_host_permissions(manifest_content: dict, extension_id: str) -> list:
    host_permissions = []
    total_permissions  = []
    try:
        if manifest_content:
            if "host_permissions" in manifest_content.keys() and type(manifest_content["host_permissions"]) is list:
                total_permissions.extend(manifest_content["host_permissions"])
            if "optional_host_permissions" in manifest_content.keys() and type(manifest_content["optional_host_permissions"]) is list:
                total_permissions.extend(manifest_content["optional_host_permissions"])
            if "permissions" in manifest_content.keys() and type(manifest_content["permissions"]) is list:
                total_permissions.extend(manifest_content["permissions"])
            if "optional_permissions" in manifest_content.keys() and type(manifest_content["optional_permissions"]) is list:
                total_permissions.extend(manifest_content["optional_permissions"])
            if type(total_permissions) == list:
                host_permissions = list(set(total_permissions) - set(API_PERMISSIONS))
    except:
        logging.error("[MANIFEST] Error while extracting host permissions from manifest for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    finally:
        return host_permissions

def update_host_permissions(manifest_content: dict, key: str, sub_key: str, extension_id: str) -> dict:
    try:
        prerequisites = [manifest_content, key in manifest_content.keys() and type(manifest_content[key]) == list]
        if not all(prerequisites): return
        for entry in manifest_content[key]:
            if isinstance(entry, dict) and sub_key in entry.keys() and "matches" in entry.keys():
                for idx in range(0, len(entry["matches"])):
                    if "https" in entry["matches"][idx]:
                        url = entry["matches"][idx].replace('https', 'http')
                        entry["matches"].append(url)
    except:
        logging.error("[MANIFEST] Error while updating host permissions in the manifest for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))

def update_api_permissions(manifest_content: dict, key: str, extension_id: str) -> dict:
    try:
        if key in manifest_content:
            for idx in range(0,len(manifest_content[key])):
                if "https" in manifest_content[key][idx]:
                    manifest_content[key].append(manifest_content[key][idx].replace("https", "http"))
        if key == "host_permissions" and manifest_content["manifest_version"] == 3:
            if "optional_host_permissions" in manifest_content:
                for url in manifest_content["optional_host_permissions"]:
                    new_url = url
                    if "https" in url:
                        new_url = url.replace("https", "http")
                    if "host_permissions" not in manifest_content.keys():
                        manifest_content["host_permissions"] = list(set([url, new_url]))
                    manifest_content["host_permissions"].extend(list(set([url, new_url])))
    except:
        logging.error("[MANIFEST] Error while updating api permissions in the manifest for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
