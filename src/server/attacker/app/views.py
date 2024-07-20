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


from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from config import *
from .db import *

@require_GET
@cache_control(max_age=60 * 60 * 24 * 365, immutable=True, public=True)
def favicon(request):
    with open("./static/img/favicon.ico", 'rb') as fh:
        response = FileResponse(fh.read())
    if not request: return response
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, HEAD"
    response["Access-Control-Allow-Headers"] = "Authorization, Origin, X-Requested-With, Content-Type, Accept"
    return response

def index(request):
    if MODULE == "hook": response = render(request, "verify.html")
    elif MODULE == "cs": response = render(request, "verify_cs.html")
    else: response = render(request, "verify_mo.html")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, HEAD"
    response["Access-Control-Allow-Headers"] = "Authorization, Origin, X-Requested-With, Content-Type, Accept"
    return response

def images(request):
    response = HttpResponse()
    try:
        if request == None: response.content = "Invalid/Empty Request!"
        else:
            response = FileResponse(open("./static/img/" + request.GET["name"], "rb" ))
            response["Content-Type"] = "image/jpeg"
    except:
        logging.error("Exception occurred in images(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        response.content = "Error!"
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, HEAD"
    response["Access-Control-Allow-Headers"] = "Authorization, Origin, X-Requested-With, Content-Type, Accept"    
    return response

def scripts(request):
    response = HttpResponse()
    try:
        if request == None: response.content = "Invalid/Empty Request!"
        response = FileResponse(open(f"./static/scripts/" + request.GET["name"], "rb"))
        response["Content-Type"] = "application/javascript"
    except:
        logging.error("Exception occurred in scripts(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        response.content = "Error!"  
    return response

def media(request):
    response = HttpResponse()
    try:
        if request == None: response.content = "Invalid/Empty Request!"
        else:
            with open('./static/media/' + request.GET["name"], 'rb') as video_file:
                response = HttpResponse(video_file.read(), content_type='video/mp4')
            response['Content-Disposition'] = 'inline; filename=%s' % request.GET["name"]
    except:
        logging.error("Exception occurred in media(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        response.content = "Error"   
    return response

def prototype_hook_data(request):
    response = HttpResponse()
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, HEAD"
    response["Access-Control-Allow-Headers"] = "Authorization, Origin, X-Requested-With, Content-Type, Accept"  
    try:
        if request == None:
            response.content = "Invalid/Empty Request!"
            return response
        parsed_data = parse_request_data(request)
        if not parsed_data or not isinstance(parsed_data, dict):
            response.content = "Invalid/Empty Request!"
            return response
        response.content = store_prototype_hook_data(parsed_data)
    except:
        logging.error("Exception occurred in prototype_hook_data(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        response.content = "Error" 
    return response

def poll_data(request):
    response = HttpResponse()
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, HEAD"
    response["Access-Control-Allow-Headers"] = "Authorization, Origin, X-Requested-With, Content-Type, Accept"  
    try:
        if request == None:
            response.content = "Invalid/Empty Request!"
            return response
        parsed_data = parse_request_data(request)
        if not parsed_data or not isinstance(parsed_data, dict) or "type"not in parsed_data.keys():
            response.content = "Invalid/Empty Request!"
            return response
        if parsed_data["type"] == "cookies": response.content = store_cookies_data(parsed_data)
        elif parsed_data["type"] == "idb": response.content = store_idb_data(parsed_data)
        elif parsed_data["type"] == "message": response.content = store_message_data(parsed_data)
        elif parsed_data["type"] in ("local", "storage"): response.content = store_storage_data(parsed_data)
        elif parsed_data["type"] == "variable": response.content = store_variable_data(parsed_data)
    except:
        logging.error("Exception occurred in poll_data(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        response.content = "Error"
    return response

def parse_request_data(request):
    data = None
    try:
        data = json.loads(str(request.body.decode('utf-8', errors='ignore').replace("\x00", "").replace("\u0000", "")))
    except:
        try:
            data = json.loads(str(request.body.decode('utf-32', errors='ignore').replace("\x00", "").replace("\u0000", "")))
        except:
            try:
                data = json.loads(str(request.body.decode('utf-8-bom', errors='ignore').replace("\x00", "").replace("\u0000", "")))
            except:
                pass
    return data

def error(request):
    response = HttpResponse()
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, HEAD"
    response["Access-Control-Allow-Headers"] = "Authorization, Origin, X-Requested-With, Content-Type, Accept"  
    try:
        parsed_data = parse_request_data(request)
        if not parsed_data: response.content = 'Error!'
        else: response.content = log_error(parsed_data)
    except:
        logging.error("Exception occurred in error(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        response.content = "Error"
    return response

def sel(request):
    extension_id = ""
    other_extensions = ""
    response = HttpResponse()
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, HEAD"
    response["Access-Control-Allow-Headers"] = "Authorization, Origin, X-Requested-With, Content-Type, Accept"  
    try:
        if "other_extensions" in request.GET:
            other_extensions = request.GET["other_extensions"]
        if extension_id:
            extension_id = request.GET["extension_id"]
            log_extensions_selenium(extension_id, other_extensions)
    except:
        logging.error("Exception occurred in sel(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        response.content = "Error"
    return response