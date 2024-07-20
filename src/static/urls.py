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

import tldextract

def process_scheme(url: str, extension_id: str):
    try:
        if url.startswith('file') or url.startswith('ftp') or url.startswith('urn'):
            return None
        if url.startswith('http://') or url.startswith('https://') or url.startswith("*://"):
            scheme, host = url.split('://', 1)
            return (scheme, host)
    except:
        logging.error("[URL NORMALIZER] Error while processing URL scheme for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    
def process_host(url: str, extension_id: str):
    host, path, extracted_host = None, None, None
    try:
        if "/" in url:
            host, path = url.split("/", 1)
        else:
            host = url
        try:
            tld_extractor = tldextract.TLDExtract(fallback_to_snapshot=True, include_psl_private_domains=True, cache_dir="/tmp/tldextract/cache/")
            extracted_host = tld_extractor(host)
        except:
            logging.error("[URL NORMALIZER] Error while extracting host for: " + host + " - " + ", ".join(traceback.format_exc().split("\n")))
        return (extracted_host, path)
    except:
        logging.error("[URL NORMALIZER] Error while processing URL host for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    
def process_path(path: str, extension_id: str):
    try:
        if path in ["", "*", None]:
            path = ""
        else:
            while path.startswith("*/"):
                path = path.split("*/", 1)[1]
            if path.startswith("*"):
                path = path.split("*", 1)[1]    
            if path.endswith("*"):
                path = path.split("*")[0]
            if path.endswith("*/"):
                path = path.split("*/")[0]
            if "/*/" in path:
                while "/*/" in path:
                    path = path.replace("/*/", "/")
        return path
    except:
        logging.error("[URL NORMALIZER] Error while processing URL path for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
        return None

def combine_url_components(scheme: str, host: str, path: str, extension_id: str):
    processed_url, domain = "", ""
    try:
        if scheme in ["", "*"] and host.subdomain == "" and host.domain == '*' and path in [None, "", "*", "/*"]:
            return "<all_urls>"
        if scheme == '*':
            scheme = "http"
        if host.subdomain in ["*", ""] and host.domain != "*":
            if host.domain.lower() == 'whatsapp':
                domain = "web." + host.domain + "."
            else:
                domain = "www." + host.domain + "."
            if host.suffix != "":
                domain += host.suffix
            else:
                domain += "com"
        elif host.subdomain == "" and host.domain == "*":
            domain = FILE_PATH_SUBSTITUTE[4:-1]
        elif host.subdomain != "" and host.domain != "":
            if host.subdomain.startswith('*.'):
                domain = host.subdomain[2:] + "." + host.domain + "."
            else:
                domain = host.subdomain + "." + host.domain + "."
            if host.suffix != "":
                domain += host.suffix
            else:
                domain += "com"
        if path not in [None, "", "*", "/*"]:
            if path.startswith("."):
                path = "/test" + path
            else:
                path = "/" + path
        else:
            path = "/"
        processed_url = scheme + "://" + domain + path
        return processed_url
    except:
        logging.error("[URL NORMALIZER] Error while combining URL components for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
        return processed_url
    
def preprocess_urls(hosts: list, extension_id: str):
    extracted_urls = defaultdict(str)
    try:
        for url in hosts:
            if type(url) is str and url not in [
                "BinaryExpression", "MemberExpression", "CallExpression",
                "LogicalExpression", "Identifier", "app", "dns"
            ]:
                if url.startswith("file://") or url.startswith("ws:") or url.startswith("wss:") \
                        or url.startswith("chrome://favicon") or url.startswith("chrome-extension:") \
                        or "127.0.0.1" in url or "localhost" in url:
                    continue
                if url in [
                        "*://*/", "*://*/*", "*://*/*/", "*://*/*/*",
                        "*://*/*/*/*", "http://*/*/", "https://*/*/",
                        "http://*/*", "https://*/*", "http://*/", "https://*/",
                        "<all_urls>", "unknown", "http://*/**", "https://*/**"
                ]:
                    extracted_urls[url] = "<all_urls>"
                else:
                    scheme, host, path, extracted_url = "", "", "", ""
                    scheme = process_scheme(url, extension_id)
                    if scheme is not None:
                        host = process_host(scheme[1], extension_id)
                        if host is not None:
                            path = process_path(host[1], extension_id)
                            if scheme[0] and host[0] and path is not None:
                                extracted_url = combine_url_components(scheme[0], host[0], path, extension_id)
                                extracted_urls[url] = extracted_url
    except:
        logging.error("[URL NORMALIZER] Error while preprocessing URLs for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    finally:
        return extracted_urls

def is_host_https_only(processed_urls, extension_id):
    is_host_only_https = True
    try:
        if "<all_urls>" not in list(processed_urls.values()): return False
        if not processed_urls: return False
        for actual_url, processed_url in processed_urls.items():
            if processed_url == "<all_urls>":
                if "https" not in actual_url:
                    is_host_only_https = False
                    break
    except:
        logging.error("[URL NORMALIZER] Error while checking https permissions for extension: " + extension_id + " - " + ", ".join(traceback.format_exc().split("\n")))
    return is_host_only_https
