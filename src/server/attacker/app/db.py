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


from psycopg_pool import ConnectionPool
from config import *

CONNECTION_POOL = ConnectionPool(conninfo=CONNECTION_INFO, min_size=5, max_size=10, timeout=30)

def store_storage_data(storage_data):
    try:
        visit = -1
        extension_id = str(storage_data["extensionId"])
        stage, url, script = None, None, None
        if "visit" in storage_data.keys(): visit = storage_data["visit"]
        if "stage" in storage_data.keys(): stage = storage_data["stage"]
        if "url" in storage_data.keys(): url = storage_data["url"]
        if "script" in storage_data.keys(): script = storage_data["script"]
        query = f"INSERT INTO storage_log_{TABLE_SUFFIX}(extension_id, script, storage, type, data, visit, dataset, store, stage, url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
        with CONNECTION_POOL.connection() as connection:
            connection.execute(query, (extension_id, script, json.dumps(storage_data["type"]), "poll", json.dumps(storage_data["data"]), visit, DATASET, EXTENSION_TYPE, stage, url))
        return "Ok!"
    except:
        logging.error("[DB] Exception occurred in store_storage_data(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        return "Error!"

def store_cookies_data(cookie_data):
    try:
        visit = -1
        extension_id = str(cookie_data["extensionId"])
        stage, url, script = None, None, None
        if "visit" in cookie_data.keys(): visit = cookie_data["visit"]
        if "stage" in cookie_data.keys(): stage = cookie_data["stage"]
        if "url" in cookie_data.keys(): url = cookie_data["url"]
        if "script" in cookie_data.keys(): script = cookie_data["script"]
        query = f"INSERT INTO cookies_log_{TABLE_SUFFIX}(extension_id, script, type, data, visit, dataset, store, stage, url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
        with CONNECTION_POOL.connection() as connection:
            connection.execute(query, (extension_id, script, "poll", json.dumps(cookie_data["data"]), visit, DATASET, EXTENSION_TYPE, stage, url))
        return "Ok!"
    except:
        logging.error("[DB] Exception occurred in store_cookies_data(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        return "Error!"

def store_idb_data(idb_data):
    try:
        visit = -1
        extension_id = str(idb_data["extensionId"])
        script, stage, url, property, arguments, results = None, None, None, None, None, None
        if "visit" in idb_data.keys(): visit = idb_data["visit"]
        if "script" in idb_data.keys(): script = idb_data["script"]
        if "stage" in idb_data.keys(): stage = idb_data["stage"]
        if "url" in idb_data.keys(): url = idb_data["url"]
        if "property" in idb_data.keys(): property = json.dumps(idb_data["property"])
        if "arguments" in idb_data.keys(): arguments = json.dumps(idb_data["arguments"])
        if "results" in idb_data.keys(): results = json.dumps(idb_data["results"])
        elif "data" in idb_data.keys(): results = json.dumps(idb_data["data"])
        query = f"INSERT INTO idb_log_{TABLE_SUFFIX}(extension_id, script, property, arguments, results, visit, dataset, store, stage, url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
        with CONNECTION_POOL.connection() as connection:
            connection.execute(query, (extension_id, script, property, arguments, results, visit, DATASET, EXTENSION_TYPE, stage, url))
        return "Ok!"
    except:
        logging.error("[DB] Exception occurred in store_idb_data(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        return "Error!"

def store_event_data(event_data):
    try:
        visit = -1
        extension_id = str(event_data["extensionId"])
        script = ""
        options = ""
        event, data = None, None
        if "visit" in event_data.keys(): visit = event_data["visit"]
        if "event" in event_data.keys(): event = event_data["event"]
        if "script" in event_data.keys(): script = event_data["script"]
        if "data" in event_data.keys(): data = json.dumps(event_data["data"])
        if "options" in event_data.keys(): options = json.dumps(event_data["options"])
        query = f"INSERT INTO event_log_{TABLE_SUFFIX}(extension_id, script, event, options, data, visit, dataset, store) VALUES(%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
        with CONNECTION_POOL.connection() as connection:
            connection.execute(query, (extension_id, script, event, options, data, visit, DATASET, EXTENSION_TYPE))
        return "Ok!"
    except:
        logging.error("[DB] Exception occurred in store_event_data(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        return "Error!"

def store_message_data(message_data):
    try:
        extension_id = str(message_data["extensionId"])
        script = ""
        visit = -1
        stage, url, message, source, target, origin = None, None, None, None, None, None
        if "visit" in message_data.keys(): visit = message_data["visit"]
        if "stage" in message_data.keys(): stage = message_data["stage"]
        if "url" in message_data.keys(): url = message_data["url"]
        if "script" in message_data.keys(): script = message_data["script"]
        if "message" in message_data.keys(): message = message_data["message"]
        if "source" in message_data.keys(): source = message_data["source"]
        if "target" in message_data.keys(): target = message_data["target"]
        if "origin" in message_data.keys(): origin = message_data["origin"]
        data = {"source": source, "target": target, "origin": origin}
        query = f"INSERT INTO message_log_{TABLE_SUFFIX}(extension_id, script, message, data, visit, dataset, store, stage, url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
        with CONNECTION_POOL.connection() as connection:
            connection.execute(query, (extension_id, script, json.dumps(message), json.dumps(data), visit, DATASET, EXTENSION_TYPE, stage, url))
        return "Ok!"
    except:
        logging.error("[DB] Exception occurred in store_message_data(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        return "Error!"
    
def store_variable_data(variable_data):
    try:
        extension_id = str(variable_data["extensionId"])
        if not extension_id or extension_id == 'None': return "Ok!"
        script = ""
        visit = -1
        stage, url, variables = None, None, None
        if "visit" in variable_data.keys(): visit = variable_data["visit"]
        if "stage" in variable_data.keys(): stage = variable_data["stage"]
        if "url" in variable_data.keys(): url = variable_data["url"]
        if "script" in variable_data.keys(): script = variable_data["script"]
        if "data" in variable_data.keys() and "variables" in variable_data["data"].keys(): variables = variable_data["data"]["variables"]
        if not variables: return "Ok!"
        query = f"INSERT INTO variable_log_{TABLE_SUFFIX}(extension_id, script, variables, visit, dataset, store, stage, url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
        with CONNECTION_POOL.connection() as connection:
            connection.execute(query, (extension_id, script, json.dumps(variables), visit, DATASET, EXTENSION_TYPE, stage, url))
        return "Ok!"
    except:
        logging.error("[DB] Exception occurred in store_variable_data(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        return "Error!"

def store_prototype_hook_data(prototype_data):
    try:
        if prototype_data["type"] == "variable" and "data" in prototype_data.keys(): return store_variable_data(prototype_data)
        extension_id = str(prototype_data["extensionId"])
        if not extension_id or extension_id == 'None': return "Ok!"
        url = str(prototype_data["url"])
        api = str(prototype_data["type"])
        visit = -1
        
        data, arguments, caller, caller_data, caller_name, stacktrace = None, None, None, None, None, None
        if "data" in prototype_data.keys():
            if api in ('cookies', 'localStorage', 'sessionStorage'):
                if "type" in prototype_data["data"].keys():
                    api = prototype_data["data"]["type"]
            if "visit" in prototype_data.keys(): visit = prototype_data["visit"]
            if "dis" in prototype_data["data"].keys():
                data = json.dumps(prototype_data["data"]["dis"])
            if "arguments" in prototype_data["data"].keys():
                arguments = json.dumps(prototype_data["data"]["arguments"])
            if "caller" in prototype_data["data"].keys():
                caller = json.dumps(prototype_data["data"]["caller"])
            if "callerData" in prototype_data["data"].keys():
                caller_data = json.dumps(prototype_data["data"]["callerData"])
            if "callerName" in prototype_data["data"].keys():
                caller_name = json.dumps(prototype_data["data"]["callerName"])
            if "stacktrace" in prototype_data["data"].keys():
                stacktrace = json.dumps(prototype_data["data"]["stacktrace"])
        arguments_md5 = "%s_%s" % (api, hashlib.md5(str(arguments).encode()).hexdigest())
        arguments_data_md5 = "%s_%s_%s" % (
            api, hashlib.md5(str(arguments).encode()).hexdigest(), hashlib.md5(str(data).encode()).hexdigest())
        caller_data_md5 = "%s_%s" % (api, hashlib.md5(str(caller_data).encode()).hexdigest())
        stack_trace_md5 = "%s_%s" % (api, hashlib.md5(str(stacktrace).encode()).hexdigest())
        query = f"""INSERT INTO prototype_hook_log_{TABLE_SUFFIX}
        (extension_id, url, api, data, arguments, caller, caller_name, caller_data, stacktrace, stack_trace_md5, 
        arguments_md5, arguments_data_md5, caller_data_md5, dataset, visit, store) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;"""
        with CONNECTION_POOL.connection() as connection:
            connection.execute(query, (extension_id, url, api, data, arguments, caller, caller_name, caller_data,
                                       stacktrace, stack_trace_md5, arguments_md5, arguments_data_md5, caller_data_md5,
                                       DATASET, visit, EXTENSION_TYPE))
        return "Ok!"
    except:
        logging.error("[DB] Exception occurred in store_prototype_hook_data(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        return "Error!"

def log_error(data):
    try:
        extension_id = str(data["extensionId"])
        if not extension_id or extension_id == 'None': return "Ok!"
        visit = str(data["visit"])
        error = str(data["error"])
        query = f"INSERT INTO errors_{MODULE}_{TABLE_SUFFIX}(extension_id, dataset, error, visit, store) VALUES(%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;"
        with CONNECTION_POOL.connection() as connection:
            connection.execute(query, (extension_id, DATASET, error, visit, EXTENSION_TYPE))
        return "Ok!"
    except:
        logging.error("[DB] Exception occurred in log_error(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        return "Error!"
 
def log_extensions_selenium(extension_id, other_extensions):
    try:
        if isinstance(other_extensions, str):
            other_extensions = json.dumps(other_extensions.split(","))
        query = f"INSERT INTO record_sel_{MODULE}_{TABLE_SUFFIX}(extension_id, other_extensions, dataset) VALUES(%s, %s, %s) ON CONFLICT DO NOTHING;"
        with CONNECTION_POOL.connection() as connection:
            connection.execute(query, (extension_id, other_extensions, DATASET))
        return "Ok!"
    except:
        logging.error("[DB] Exception occurred in log_extensions_selenium(): %s\n" % "-".join(traceback.format_exc().split("\n")))
        return "Error!"
