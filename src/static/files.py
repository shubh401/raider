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

from bs4 import BeautifulSoup
from glob import glob

from config import *

def check_file_validity(file_path: str, extension_id: str) -> bool:
    try:
        if os.path.getsize(file_path) > MAX_JS_SIZE:
            return False
        for file_type in JS_BLACKLISTS:
            if file_type in file_path.rsplit("/", 1)[-1].lower():
                return False
    except:
        logging.error("[Files] Error while checking file validity: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    return True

def clean_directories(target_dir: str) -> None:
    try:
        if not os.listdir(target_dir): shutil.rmtree(target_dir)
    except:
        logging.error("[FILES] Error while cleaning extension directories" + ", ".join(traceback.format_exc().split("\n")))

def remove_file(target: str) -> None:
    try:
        os.remove(target)
    except:
        logging.error("[FILES] Error while removing file: " + target + " - " + ", ".join(traceback.format_exc().split("\n")))

def copy_file(source: str, target: str) -> None:
    try:
        shutil.copy(source, target)
    except:
        logging.error("[FILES] Error while copying file: " + source + " - " + ", ".join(traceback.format_exc().split("\n")))

def copy_extension_dir(source_dir: str, target_dir: str, extension_id: str) -> None:
    try:
        if os.path.exists(target_dir + extension_id): return
        shutil.copytree(source_dir + extension_id, target_dir + extension_id)
    except:
        logging.error("[FILES] Error while copying directory for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))

def list_of_files(extension_path: str, extension_id: str) -> list:
    file_list = []
    try:
        for root, dir_names, file_names in os.walk(extension_path + extension_id):
            for file in file_names:
                file_list.append(os.path.join(root, file))
    except:
        logging.error("[FILES] Error while enumerating all the files for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    finally:
        return file_list

def resolve_wildcards(script: str, extension_id: str, source_dir: str):
    relevant_files = []
    try:
        if script.startswith("/") or script.startswith("\\"): script = script[1:]
        if not script.startswith(source_dir):
            script = source_dir + extension_id + "/" + script
        relevant_files = glob(script, recursive=True)
    except:
        logging.error("[FILES] Error while resolving wildcards for:" + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    return relevant_files

def absolute_file_path_from_dir(file_list: list, source_dir: str, extension: str, file: str, extension_id: str) -> str:
    absolute_path = ""
    extension_name = extension
    try:
        if file[0] == '/':
            extension_name = extension_name.split("/", 1)[0]
            file_name = file[1:]
        elif file.startswith("../"):
            while (file.startswith("../")):
                if "/" in extension_name:
                    extension_name = extension_name.rsplit("/", 1)[0]
                file = file[3:]
            file_name = file
        elif file.startswith("./"):
            if "/" in extension_name:
                extension_name = extension_name.rsplit("/", 1)[0]
            file_name = file[2:]
        else:
            file_name = file
        for file_path in file_list:
            if os.path.abspath(os.path.join(source_dir + extension_name, file_name)).lower() == os.path.abspath(file_path.lower()):
                absolute_path = file_path
                break
        if absolute_path == "":
            if file[0] == '/':
                file_name = file[1:]
                extension_name = extension
            elif file.startswith("./"):
                file_name = file[2:]
                extension_name = extension
            for file_path in file_list:
                if os.path.join(source_dir + extension_name, file_name).lower() == file_path.lower():
                    absolute_path = file_path
                    break
    except:
        logging.error("[FILES] Error while resolving absolute path for script for: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    finally:
        return absolute_path

def script_src_from_html(html_path: str, extension_id: str, remove_integrity: bool = True) -> list:
    is_modified = False
    script_srcs = []
    try:
        if html_path is not None and html_path != "":
            html_data = open(html_path, "r", errors='ignore').read()
            parsed_html = BeautifulSoup(html_data, 'html.parser')
            scripts = parsed_html.find_all('script')
            for link in scripts:
                if 'src' in link.attrs:
                    """ If the included scripts contain hashes, the attributes are removed to allow our modifications. """
                    script_srcs.append(link['src'])
                    if remove_integrity and 'integrity' in link.attrs:
                        del link['integrity']
                        is_modified = True
            if is_modified:
                with open(html_path, 'wb') as fh:
                    fh.write(parsed_html.prettify('utf-8'))
    except:
        logging.error("[FILES] Error while extracting scripts paths from the background page for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    finally:
        return script_srcs

def absolute_path_of_scripts(ext_scripts: list, file_list: list, source_dir: str, extension_id: str) -> list:
    scripts_absolute_path = []
    relevant_scripts, filtered_scripts = [], []
    try:
        for script in ext_scripts:
            if ".js#" in script or ".htm#" in script or ".html#" in script:
                script = script.rsplit("#", 1)[0]
            if ".js?" in script or ".htm?" in script or ".html?" in script:
                script = script.split("?", 1)[0]
            if script.endswith("js*"): script = script[:-1]
                
            if (script.endswith("js") or script.endswith("js.map")):
                script_path = absolute_file_path_from_dir(file_list, source_dir, extension_id, script, extension_id)
                if script_path is not None and script_path != "":
                    scripts_absolute_path.append(script_path)
                elif "*" in script:
                    scripts = resolve_wildcards(script, extension_id, source_dir)
                    if scripts: scripts_absolute_path.extend(scripts)
            elif script.endswith("html") or script.endswith("htm"):
                html_path = absolute_file_path_from_dir(file_list, source_dir, extension_id, script, extension_id)
                html_script_src = script_src_from_html(html_path, extension_id)
                if html_script_src is not None and len(html_script_src) > 0:
                    if "/" in script:
                        html_path_dir = "/" + script.rsplit("/", 1)[0]
                    else:
                        html_path_dir = "/"
                    for script_src in html_script_src:
                        if ".js#" in script_src or ".htm#" in script_src or ".html#" in script_src:
                            script_src = script_src.rsplit("#", 1)[0]
                        if ".js?" in script_src or ".htm?" in script_src or ".html?" in script_src:
                            script_src = script_src.split("?", 1)[0]
                        if (not script_src.startswith("http")) and script_src.endswith("js"):
                            script_src_path = absolute_file_path_from_dir(file_list, source_dir, extension_id + html_path_dir, script_src, extension_id)
                            if script_src_path is not None and script_src_path != "":
                                scripts_absolute_path.append(script_src_path)
                            elif "*" in script_src:
                                scripts = resolve_wildcards(script_src, extension_id, source_dir)
                                if scripts: scripts_absolute_path.extend(scripts)
        if scripts_absolute_path:
            for script in scripts_absolute_path:
                if check_file_validity(script, extension_id): relevant_scripts.append(script)
                else: filtered_scripts.append(script)
    except:
        logging.error("[FILES] Error while instrumenting extension:" + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    finally:
        return relevant_scripts, filtered_scripts
