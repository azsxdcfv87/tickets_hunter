#!/usr/bin/env python3
#encoding=utf-8
import asyncio
import base64
import copy
import json
import os
import platform
import re
import secrets
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime

import tornado
from tornado.web import Application
from tornado.web import StaticFileHandler

import requests
import util

from typing import (
    Dict,
    Any,
    Union,
    Optional,
    Awaitable,
    Tuple,
    List,
    Callable,
    Iterable,
    Generator,
    Type,
    TypeVar,
    cast,
    overload,
)

try:
    import ddddocr
except Exception as exc:
    print(f"[WARNING] ddddocr module not available: {exc}")
    print("[WARNING] OCR captcha auto-solve will be disabled.")

# Get script directory for resource paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CONST_APP_VERSION = "TicketsHunter (2026.04.23)"

CONST_MAXBOT_ANSWER_ONLINE_FILE = "MAXBOT_ONLINE_ANSWER.txt"
CONST_MAXBOT_CONFIG_FILE = "settings.json"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_QUESTION_FILE = "MAXBOT_QUESTION.txt"

CONST_SERVER_PORT = 16888
CONST_AUTH_COOKIE_NAME = "tickets_hunter_token"
CONST_AUTH_HEADER_NAME = "X-Tickets-Hunter-Token"
SERVER_AUTH_TOKEN = secrets.token_urlsafe(32)

CONST_FROM_TOP_TO_BOTTOM = "from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = "from bottom to top"
CONST_CENTER = "center"
CONST_RANDOM = "random"
CONST_SELECT_ORDER_DEFAULT = CONST_RANDOM
CONST_EXCLUDE_DEFAULT = "\"輪椅\",\"身障\",\"身心\",\"障礙\",\"Restricted View\",\"燈柱遮蔽\",\"視線不完整\""
CONST_CAPTCHA_SOUND_FILENAME_DEFAULT = "assets/sounds/ding-dong.wav"
CONST_HOMEPAGE_DEFAULT = "about:blank"

CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"
CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"

CONST_WEBDRIVER_TYPE_NODRIVER = "nodriver"

CONST_SUPPORTED_SITES = ["https://kktix.com"
    ,"https://tixcraft.com (拓元)"
    ,"https://ticketmaster.sg"
    #,"https://ticketmaster.com"
    ,"https://teamear.tixcraft.com/ (添翼)"
    ,"https://www.indievox.com/ (獨立音樂)"
    ,"https://www.famiticket.com.tw (全網)"
    ,"https://ticket.ibon.com.tw/"
    ,"https://kham.com.tw/ (寬宏)"
    ,"https://ticket.com.tw/ (年代)"
    ,"https://tickets.udnfunlife.com/ (udn售票網)"
    ,"https://ticketplus.com.tw/ (遠大)"
    ,"===[香港或南半球的系統]==="
    ,"http://www.urbtix.hk/ (城市)"
    ,"https://www.cityline.com/ (買飛)"
    ,"https://hotshow.hkticketing.com/ (快達票)"
    ,"https://ticketing.galaxymacau.com/ (澳門銀河)"
    ,"http://premier.ticketek.com.au"
    ]

URL_DONATE = 'https://max-everyday.com/about/#donate'
URL_HELP = 'https://max-everyday.com/2018/03/tixcraft-bot/'
URL_RELEASE = 'https://github.com/azsxdcfv87/tickets_hunter/releases'
URL_CHROME_DRIVER = 'https://chromedriver.chromium.org/'
URL_FIREFOX_DRIVER = 'https://github.com/mozilla/geckodriver/releases'
URL_EDGE_DRIVER = 'https://developer.microsoft.com/zh-tw/microsoft-edge/tools/webdriver/'


def get_default_config():
    config_dict={}

    config_dict["homepage"] = CONST_HOMEPAGE_DEFAULT
    config_dict["browser"] = "chrome"
    config_dict["language"] = "English"
    config_dict["ticket_number"] = 2
    config_dict["refresh_datetime"] = ""

    config_dict["ocr_captcha"] = {}
    config_dict["ocr_captcha"]["enable"] = True
    config_dict["ocr_captcha"]["beta"] = True
    config_dict["ocr_captcha"]["force_submit"] = True
    config_dict["ocr_captcha"]["image_source"] = CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS
    config_dict["ocr_captcha"]["use_universal"] = True
    config_dict["ocr_captcha"]["path"] = "assets/model/universal"
    config_dict["webdriver_type"] = CONST_WEBDRIVER_TYPE_NODRIVER

    config_dict["date_auto_select"] = {}
    config_dict["date_auto_select"]["enable"] = True
    config_dict["date_auto_select"]["date_keyword"] = ""
    config_dict["date_auto_select"]["mode"] = CONST_SELECT_ORDER_DEFAULT

    config_dict["area_auto_select"] = {}
    config_dict["area_auto_select"]["enable"] = True
    config_dict["area_auto_select"]["mode"] = CONST_SELECT_ORDER_DEFAULT
    config_dict["area_auto_select"]["area_keyword"] = ""
    config_dict["keyword_exclude"] = CONST_EXCLUDE_DEFAULT

    config_dict['kktix']={}
    config_dict["kktix"]["auto_press_next_step_button"] = True
    config_dict["kktix"]["auto_fill_ticket_number"] = True
    config_dict["kktix"]["max_dwell_time"] = 90

    config_dict['cityline']={}

    config_dict['tixcraft']={}
    config_dict["tixcraft"]["pass_date_is_sold_out"] = True
    config_dict["tixcraft"]["auto_reload_coming_soon_page"] = True


    # Contact information
    config_dict['contact']={}
    config_dict["contact"]["real_name"] = ""
    config_dict["contact"]["phone"] = ""
    config_dict["contact"]["credit_card_prefix"] = ""

    # Accounts section (cookies, accounts, passwords)
    config_dict['accounts']={}
    config_dict["accounts"]["tixcraft_sid"] = ""
    config_dict["accounts"]["ibonqware"] = ""
    config_dict["accounts"]["funone_session_cookie"] = ""
    config_dict["accounts"]["fansigo_cookie"] = ""
    config_dict["accounts"]["fansigo_account"] = ""
    config_dict["accounts"]["fansigo_password"] = ""
    config_dict["accounts"]["facebook_account"] = ""
    config_dict["accounts"]["kktix_account"] = ""
    config_dict["accounts"]["fami_account"] = ""
    config_dict["accounts"]["cityline_account"] = ""
    config_dict["accounts"]["urbtix_account"] = ""
    config_dict["accounts"]["hkticketing_account"] = ""
    config_dict["accounts"]["kham_account"] = ""
    config_dict["accounts"]["ticket_account"] = ""
    config_dict["accounts"]["udn_account"] = ""
    config_dict["accounts"]["ticketplus_account"] = ""

    config_dict["accounts"]["facebook_password"] = ""
    config_dict["accounts"]["kktix_password"] = ""
    config_dict["accounts"]["fami_password"] = ""
    config_dict["accounts"]["urbtix_password"] = ""
    config_dict["accounts"]["cityline_password"] = ""
    config_dict["accounts"]["hkticketing_password"] = ""
    config_dict["accounts"]["kham_password"] = ""
    config_dict["accounts"]["ticket_password"] = ""
    config_dict["accounts"]["udn_password"] = ""
    config_dict["accounts"]["ticketplus_password"] = ""

    # Advanced settings (non-credential settings only)
    config_dict['advanced']={}

    config_dict['advanced']['play_sound']={}
    config_dict["advanced"]["play_sound"]["ticket"] = True
    config_dict["advanced"]["play_sound"]["order"] = True
    config_dict["advanced"]["play_sound"]["filename"] = CONST_CAPTCHA_SOUND_FILENAME_DEFAULT

    config_dict["advanced"]["disable_adjacent_seat"] = False
    config_dict["advanced"]["hide_some_image"] = False
    config_dict["advanced"]["block_facebook_network"] = False

    config_dict["advanced"]["headless"] = False
    config_dict["advanced"]["verbose"] = False
    config_dict["advanced"]["show_timestamp"] = False
    config_dict["advanced"]["auto_guess_options"] = False
    config_dict["advanced"]["user_guess_string"] = ""
    config_dict["advanced"]["discount_code"] = ""

    # Server port for settings web interface (Issue #156)
    config_dict["advanced"]["server_port"] = CONST_SERVER_PORT
    # remote_url will be dynamically generated based on server_port
    config_dict["advanced"]["remote_url"] = ""

    config_dict["advanced"]["auto_reload_page_interval"] = 5
    config_dict["advanced"]["auto_reload_overheat_count"] = 4
    config_dict["advanced"]["auto_reload_overheat_cd"] = 1.0
    config_dict["advanced"]["reset_browser_interval"] = 0
    config_dict["advanced"]["proxy_server_port"] = ""
    config_dict["advanced"]["window_size"] = "600,1024"

    config_dict["advanced"]["idle_keyword"] = ""
    config_dict["advanced"]["resume_keyword"] = ""
    config_dict["advanced"]["idle_keyword_second"] = ""
    config_dict["advanced"]["resume_keyword_second"] = ""

    config_dict["advanced"]["discord_webhook_url"] = ""
    config_dict["advanced"]["discord_message"] = ""
    config_dict["advanced"]["telegram_bot_token"] = ""
    config_dict["advanced"]["telegram_chat_id"] = ""
    config_dict["advanced"]["telegram_message"] = ""

    # Keyword priority fallback (Feature 003)
    config_dict["date_auto_fallback"] = False  # default: strict mode (avoid unwanted purchases)
    config_dict["area_auto_fallback"] = False  # default: strict mode (avoid unwanted purchases)

    return config_dict

def read_last_url_from_file():
    app_root = util.get_app_root()
    last_url_filepath = os.path.join(app_root, CONST_MAXBOT_LAST_URL_FILE)
    text = ""
    if os.path.exists(last_url_filepath):
        try:
            with open(last_url_filepath, "r", encoding="utf-8") as text_file:
                text = text_file.readline().strip()
        except Exception as e:
            print(f"[ERROR] Failed to read last_url from {last_url_filepath}: {e}")
    return text

def migrate_config(config_dict):
    """Migrate old config structure to new structure."""
    if config_dict is None:
        return config_dict
    if not isinstance(config_dict, dict):
        return get_default_config()

    for section in ["advanced", "accounts", "ocr_captcha"]:
        if section in config_dict and not isinstance(config_dict[section], dict):
            config_dict[section] = {}

    # Migrate ocr_model_path from advanced to ocr_captcha.path
    if "advanced" in config_dict and "ocr_model_path" in config_dict["advanced"]:
        if "ocr_captcha" not in config_dict:
            config_dict["ocr_captcha"] = {}
        if "path" not in config_dict["ocr_captcha"]:
            config_dict["ocr_captcha"]["path"] = config_dict["advanced"]["ocr_model_path"]
        del config_dict["advanced"]["ocr_model_path"]

    # Ensure ocr_captcha.path exists
    if "ocr_captcha" in config_dict and "path" not in config_dict["ocr_captcha"]:
        config_dict["ocr_captcha"]["path"] = "assets/model/universal"

    # Migrate server_port: ensure old config has this field (Issue #156)
    if "advanced" in config_dict:
        if "server_port" not in config_dict["advanced"]:
            config_dict["advanced"]["server_port"] = CONST_SERVER_PORT

    # Migrate discount_code from accounts to advanced
    if "accounts" in config_dict and "discount_code" in config_dict["accounts"]:
        if "advanced" not in config_dict:
            config_dict["advanced"] = {}
        # Only migrate if advanced.discount_code doesn't exist or is empty
        if "discount_code" not in config_dict["advanced"] or not config_dict["advanced"]["discount_code"]:
            config_dict["advanced"]["discount_code"] = config_dict["accounts"]["discount_code"]
        del config_dict["accounts"]["discount_code"]

    # Ensure advanced.discount_code exists
    if "advanced" in config_dict and "discount_code" not in config_dict["advanced"]:
        config_dict["advanced"]["discount_code"] = ""

    # Ensure all default fields exist (fills missing keys from new versions)
    default = get_default_config()
    for section in ["advanced", "kktix", "tixcraft", "date_auto_select", "area_auto_select", "ocr_captcha", "contact", "accounts", "cityline"]:
        if section in default:
            if section not in config_dict or not isinstance(config_dict[section], dict):
                config_dict[section] = dict(default[section])
            else:
                for key, value in default[section].items():
                    if key not in config_dict[section]:
                        config_dict[section][key] = value

    # Top-level scalar fields (auto-fill any missing non-section keys)
    dict_sections = {k for k, v in default.items() if isinstance(v, dict)}
    for key, value in default.items():
        if key not in dict_sections and key not in config_dict:
            config_dict[key] = value

    return config_dict

def _coerce_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value) if value is not None else default

def _coerce_int(value, default=0, min_value=None, max_value=None):
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = default
    if min_value is not None:
        value = max(min_value, value)
    if max_value is not None:
        value = min(max_value, value)
    return value

def _coerce_float(value, default=0.0, min_value=None, max_value=None):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = default
    if min_value is not None:
        value = max(min_value, value)
    if max_value is not None:
        value = min(max_value, value)
    return value

def _coerce_string(value, default=""):
    if value is None:
        return default
    return str(value)

def _coerce_by_default(value, default):
    if isinstance(default, bool):
        return _coerce_bool(value, default)
    if isinstance(default, int) and not isinstance(default, bool):
        return _coerce_int(value, default)
    if isinstance(default, float):
        return _coerce_float(value, default)
    if isinstance(default, str):
        return _coerce_string(value, default)
    if isinstance(default, dict):
        return sanitize_config_section(value, default)
    return value

def sanitize_config_section(source_section, default_section):
    source_section = source_section if isinstance(source_section, dict) else {}
    result = copy.deepcopy(default_section)
    for key, default_value in default_section.items():
        if key in source_section:
            result[key] = _coerce_by_default(source_section[key], default_value)
    return result

def sanitize_config_for_save(config_dict):
    """Normalize user-submitted settings before writing them to disk."""
    if not isinstance(config_dict, dict):
        raise ValueError("settings payload must be a JSON object")

    default = get_default_config()
    migrated = migrate_config(copy.deepcopy(config_dict))
    result = copy.deepcopy(default)

    for key, default_value in default.items():
        if key in migrated:
            result[key] = _coerce_by_default(migrated[key], default_value)

    result["ticket_number"] = _coerce_int(result.get("ticket_number"), default["ticket_number"], 1, 99)

    advanced = result["advanced"]
    advanced["server_port"] = _coerce_int(
        advanced.get("server_port"),
        CONST_SERVER_PORT,
        1024,
        65535,
    )
    advanced["auto_reload_page_interval"] = _coerce_float(
        advanced.get("auto_reload_page_interval"),
        default["advanced"]["auto_reload_page_interval"],
        0.1,
        3600.0,
    )
    advanced["auto_reload_overheat_count"] = _coerce_int(
        advanced.get("auto_reload_overheat_count"),
        default["advanced"]["auto_reload_overheat_count"],
        1,
        1000,
    )
    advanced["auto_reload_overheat_cd"] = _coerce_float(
        advanced.get("auto_reload_overheat_cd"),
        default["advanced"]["auto_reload_overheat_cd"],
        0.0,
        3600.0,
    )
    advanced["reset_browser_interval"] = _coerce_int(
        advanced.get("reset_browser_interval"),
        default["advanced"]["reset_browser_interval"],
        0,
        86400,
    )

    if result["kktix"]["max_dwell_time"] > 0 and result["kktix"]["max_dwell_time"] < 15:
        result["kktix"]["max_dwell_time"] = 15
    if advanced["reset_browser_interval"] > 0 and advanced["reset_browser_interval"] < 20:
        advanced["reset_browser_interval"] = 20

    window_size = advanced.get("window_size", "")
    if window_size and not re.match(r"^\d{2,5},\d{2,5}(,\d{1,3})?$", window_size):
        advanced["window_size"] = default["advanced"]["window_size"]

    if ".cityline.com" in result.get("homepage", ""):
        result["webdriver_type"] = CONST_WEBDRIVER_TYPE_NODRIVER

    return result

def load_json():
    app_root = util.get_app_root()

    # overwrite config path.
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    config_dict = None
    if os.path.isfile(config_filepath):
        try:
            with open(config_filepath, encoding='utf-8') as json_data:
                config_dict = json.load(json_data)
        except Exception as e:
            print(f"[ERROR] Failed to load {config_filepath}: {e}")
            print("[ERROR] Settings file may be corrupted. Using default settings.")
            config_dict = get_default_config()
    else:
        config_dict = get_default_config()

    # Apply migrations for backward compatibility
    config_dict = migrate_config(config_dict)

    return config_filepath, config_dict

def reset_json():
    app_root = util.get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)
    if os.path.exists(str(config_filepath)):
        try:
            os.unlink(str(config_filepath))
        except Exception as exc:
            print(exc)
            pass

    config_dict = get_default_config()
    return config_filepath, config_dict

def maxbot_idle():
    app_root = util.get_app_root()
    idle_filepath = os.path.join(app_root, CONST_MAXBOT_INT28_FILE)
    try:
        with open(idle_filepath, "w") as text_file:
            text_file.write("")
    except Exception as e:
        print(f"[ERROR] Failed to create idle file: {e}")

def maxbot_resume():
    app_root = util.get_app_root()
    idle_filepath = os.path.join(app_root, CONST_MAXBOT_INT28_FILE)
    for i in range(3):
         util.force_remove_file(idle_filepath)

def launch_maxbot():
    global launch_counter
    if "launch_counter" in globals():
        launch_counter += 1
    else:
        launch_counter = 0

    config_filepath, config_dict = load_json()

    script_name = "nodriver_tixcraft"

    window_size = config_dict["advanced"]["window_size"]
    if len(window_size) > 0:
        if "," in window_size:
            size_array = window_size.split(",")
            target_width = int(size_array[0])
            target_left = target_width * launch_counter
            #print("target_left:", target_left)
            if target_left >= 1440:
                launch_counter = 0
            window_size = window_size + "," + str(launch_counter)
            #print("window_size:", window_size)

    threading.Thread(target=util.launch_maxbot, args=(script_name,"","","","",window_size,)).start()

def change_maxbot_status_by_keyword():
    config_filepath, config_dict = load_json()

    system_clock_data = datetime.now()
    current_time = system_clock_data.strftime('%H:%M:%S')
    #print('Current Time is:', current_time)
    #print("idle_keyword", config_dict["advanced"]["idle_keyword"])
    if len(config_dict["advanced"]["idle_keyword"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["idle_keyword"], current_time)
        if is_matched:
            #print("match to idle:", current_time)
            maxbot_idle()
    #print("resume_keyword", config_dict["advanced"]["resume_keyword"])
    if len(config_dict["advanced"]["resume_keyword"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["resume_keyword"], current_time)
        if is_matched:
            #print("match to resume:", current_time)
            maxbot_resume()
    
    current_time = system_clock_data.strftime('%S')
    if len(config_dict["advanced"]["idle_keyword_second"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["idle_keyword_second"], current_time)
        if is_matched:
            #print("match to idle:", current_time)
            maxbot_idle()
    if len(config_dict["advanced"]["resume_keyword_second"]) > 0:
        is_matched =  util.is_text_match_keyword(config_dict["advanced"]["resume_keyword_second"], current_time)
        if is_matched:
            #print("match to resume:", current_time)
            maxbot_resume()

def clean_tmp_file():
    app_root = util.get_app_root()
    remove_file_list = [CONST_MAXBOT_LAST_URL_FILE
        ,CONST_MAXBOT_INT28_FILE
        ,CONST_MAXBOT_ANSWER_ONLINE_FILE
        ,CONST_MAXBOT_QUESTION_FILE
    ]
    for filename in remove_file_list:
         filepath = os.path.join(app_root, filename)
         util.force_remove_file(filepath)

    Root_Dir = util.get_app_root()
    target_folder = os.listdir(Root_Dir)
    for item in target_folder:
        if item.endswith(".tmp"):
            try:
                os.remove(os.path.join(Root_Dir, item))
            except Exception as e:
                print(f"[WARNING] Failed to remove {item}: {e}")

def set_auth_cookie(handler):
    handler.set_cookie(
        CONST_AUTH_COOKIE_NAME,
        SERVER_AUTH_TOKEN,
        httponly=False,
        samesite="Strict",
    )

def get_request_hostname(host):
    host = (host or "").strip()
    if host.startswith("["):
        end = host.find("]")
        return host[1:end] if end > 0 else host
    if ":" in host:
        return host.rsplit(":", 1)[0]
    return host

def is_local_hostname(hostname):
    hostname = (hostname or "").lower()
    return hostname in ("localhost", "::1") or hostname.startswith("127.")

def is_same_origin_header(origin, request_host):
    if not origin:
        return True
    from urllib.parse import urlparse
    try:
        parsed = urlparse(origin)
    except Exception:
        return False
    return parsed.scheme == "http" and get_request_hostname(parsed.netloc) == get_request_hostname(request_host)

class SecureAPIHandler(tornado.web.RequestHandler):
    """Local-only API handler with same-origin token checks."""

    def set_default_headers(self):
        self.set_header("Cache-Control", "no-store")

    def prepare(self):
        set_auth_cookie(self)
        if not is_local_hostname(get_request_hostname(self.request.host)):
            self.set_status(403)
            self.finish({"error": {"message": "local access only", "code": 4030}})
            return

        if not is_same_origin_header(self.request.headers.get("Origin"), self.request.host):
            self.set_status(403)
            self.finish({"error": {"message": "invalid origin", "code": 4031}})
            return

        header_token = self.request.headers.get(CONST_AUTH_HEADER_NAME, "")
        cookie_token = self.get_cookie(CONST_AUTH_COOKIE_NAME, "")
        if not (
            secrets.compare_digest(header_token, SERVER_AUTH_TOKEN)
            and secrets.compare_digest(cookie_token, SERVER_AUTH_TOKEN)
        ):
            self.set_status(403)
            self.finish({"error": {"message": "invalid local token", "code": 4032}})

    def options(self):
        self.set_status(204)
        self.finish()

class NoCacheStaticFileHandler(StaticFileHandler):
    """Custom StaticFileHandler that prevents caching of settings.html"""
    def set_extra_headers(self, path):
        set_auth_cookie(self)
        # Disable caching only for settings.html to prevent stale UI issues
        if path == 'settings.html':
            self.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.set_header('Pragma', 'no-cache')
            self.set_header('Expires', '0')

class QuestionHandler(SecureAPIHandler):
    def get(self):
        """Read MAXBOT_QUESTION.txt and return its content"""
        question_text = ""
        question_file = os.path.join(SCRIPT_DIR, CONST_MAXBOT_QUESTION_FILE)

        # Check if file exists
        if os.path.exists(question_file):
            try:
                with open(question_file, "r", encoding="utf-8") as f:
                    question_text = f.read().strip()
            except Exception as e:
                print(f"Error reading question file: {e}")

        # Return JSON response
        self.write({
            "exists": os.path.exists(question_file),
            "question": question_text
        })

class VersionHandler(SecureAPIHandler):
    def get(self):
        self.write({"version":self.application.version})

class ShutdownHandler(SecureAPIHandler):
    def get(self):
        global GLOBAL_SERVER_SHUTDOWN
        GLOBAL_SERVER_SHUTDOWN = True
        self.write({"showdown": GLOBAL_SERVER_SHUTDOWN})

class StatusHandler(SecureAPIHandler):
    def get(self):
        is_paused = False
        app_root = util.get_app_root()
        idle_filepath = os.path.join(app_root, CONST_MAXBOT_INT28_FILE)
        if os.path.exists(idle_filepath):
            is_paused = True
        url = read_last_url_from_file()
        self.write({"status": not is_paused, "last_url": url})

class PauseHandler(SecureAPIHandler):
    def get(self):
        maxbot_idle()
        self.write({"pause": True})

class ResumeHandler(SecureAPIHandler):
    def get(self):
        maxbot_resume()
        self.write({"resume": True})

class RunHandler(SecureAPIHandler):
    def get(self):
        print('run button pressed.')
        launch_maxbot()
        self.write({"run": True})

class LoadJsonHandler(SecureAPIHandler):
    def get(self):
        config_filepath, config_dict = load_json()

        # Dynamically generate remote_url based on server_port (Issue #156)
        server_port = config_dict.get("advanced", {}).get("server_port", CONST_SERVER_PORT)
        if not isinstance(server_port, int) or server_port < 1024 or server_port > 65535:
            server_port = CONST_SERVER_PORT
        config_dict["advanced"]["remote_url"] = f'"http://127.0.0.1:{server_port}/"'

        self.write(config_dict)

class ResetJsonHandler(SecureAPIHandler):
    def get(self):
        config_filepath, config_dict = reset_json()
        if util.save_json(config_dict, config_filepath):
            self.write(config_dict)
        else:
            self.set_status(500)
            self.write({"error": {"message": "failed to save default settings", "code": 1500}})

class SaveJsonHandler(SecureAPIHandler):
    def post(self):
        _body = None
        is_pass_check = True
        error_message = ""
        error_code = 0

        if is_pass_check:
            is_pass_check = False
            try :
                _body = json.loads(self.request.body)
                is_pass_check = True
            except Exception:
                error_message = "wrong json format"
                error_code = 1002
                pass

        if is_pass_check:
            try:
                app_root = util.get_app_root()
                config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)
                config_dict = sanitize_config_for_save(_body)
                if not util.save_json(config_dict, config_filepath):
                    self.set_status(500)
                    self.write(dict(error=dict(message="failed to save settings", code=1500)))
                    self.finish()
                    return
            except Exception as exc:
                self.set_status(400)
                self.write(dict(error=dict(message=str(exc), code=1003)))
                self.finish()
                return

        if not is_pass_check:
            self.set_status(401)
            self.write(dict(error=dict(message=error_message,code=error_code)))

        self.finish()

class SendkeyHandler(SecureAPIHandler):
    def post(self):
        _body = None
        is_pass_check = True
        errorMessage = ""
        errorCode = 0

        if is_pass_check:
            is_pass_check = False
            try :
                _body = json.loads(self.request.body)
                is_pass_check = True
            except Exception:
                errorMessage = "wrong json format"
                errorCode = 1001
                pass

        if is_pass_check:
            app_root = util.get_app_root()
            if "token" in _body:
                token = str(_body["token"])
                if re.fullmatch(r"[A-Za-z0-9_-]{1,80}", token):
                    tmp_file = token + ".tmp"
                    config_filepath = os.path.abspath(os.path.join(app_root, tmp_file))
                    app_root_abs = os.path.abspath(app_root)
                    if config_filepath.startswith(app_root_abs + os.sep):
                        util.save_json(_body, config_filepath)
                else:
                    self.set_status(400)
                    self.write({"return": False, "error": "invalid token"})
                    return

        self.write({"return": True})

class TestDiscordWebhookHandler(SecureAPIHandler):
    ALLOWED_HOSTS = ("discord.com", "discordapp.com")

    def post(self):
        try:
            body = json.loads(self.request.body)
        except Exception:
            self.write({"success": False, "message": "wrong json format"})
            return

        webhook_url = body.get("webhook_url", "").strip()
        if not webhook_url:
            self.write({"success": False, "message": "webhook URL is empty"})
            return

        from urllib.parse import urlparse
        try:
            parsed = urlparse(webhook_url)
        except Exception:
            self.write({"success": False, "message": "invalid URL format"})
            return

        if parsed.scheme != "https":
            self.write({"success": False, "message": "only HTTPS URLs are allowed"})
            return

        if not any(parsed.netloc == host or parsed.netloc.endswith("." + host) for host in self.ALLOWED_HOSTS):
            self.write({"success": False, "message": "only Discord webhook URLs are allowed"})
            return

        if not parsed.path.startswith("/api/webhooks/"):
            self.write({"success": False, "message": "invalid Discord webhook URL format"})
            return

        _, config_dict = load_json()
        debug = util.create_debug_logger(config_dict)

        custom_message = body.get("custom_message", "").strip()
        content = custom_message if custom_message else "[Test] Tickets Hunter webhook test successful!"
        payload = {
            "content": content,
            "username": "Tickets Hunter"
        }
        try:
            response = requests.post(webhook_url, json=payload, timeout=5.0)
            if response.status_code in (200, 204):
                debug.log("[Discord Webhook] Test OK")
                self.write({"success": True, "message": "ok"})
            else:
                debug.log("[Discord Webhook] Test failed: HTTP %d" % response.status_code)
                self.write({"success": False, "message": "HTTP %d" % response.status_code})
        except Exception as exc:
            debug.log("[Discord Webhook] Test failed: %s" % str(exc))
            self.write({"success": False, "message": str(exc)})

class TestTelegramHandler(SecureAPIHandler):
    def post(self):
        try:
            body = json.loads(self.request.body)
        except Exception:
            self.write({"success": False, "message": "wrong json format"})
            return

        bot_token = body.get("bot_token", "").strip()
        chat_id = body.get("chat_id", "").strip()

        if not bot_token:
            self.write({"success": False, "message": "Bot Token is empty"})
            return

        import re
        if not re.match(r'^\d+:[A-Za-z0-9_-]+$', bot_token):
            self.write({"success": False, "message": "Bot Token format invalid"})
            return

        if not chat_id:
            self.write({"success": False, "message": "Chat ID is empty"})
            return

        chat_ids = [cid.strip() for cid in chat_id.split(",") if cid.strip()]
        if not chat_ids:
            self.write({"success": False, "message": "Chat ID is empty"})
            return

        invalid_ids = [cid for cid in chat_ids if not re.match(r'^-?\d+$', cid)]
        if invalid_ids:
            self.write({"success": False, "message": "Chat ID format invalid: %s" % ", ".join(invalid_ids)})
            return

        _, config_dict = load_json()
        debug = util.create_debug_logger(config_dict)

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        custom_message = body.get("custom_message", "").strip()
        text = custom_message if custom_message else "[Test] Tickets Hunter Telegram test successful!"
        errors = []
        ok_count = 0
        for cid in chat_ids:
            try:
                payload = {"chat_id": cid, "text": text}
                response = requests.post(url, json=payload, timeout=5.0)
                result = response.json()
                if response.status_code == 200 and result.get("ok", False):
                    ok_count += 1
                else:
                    desc = result.get("description", "HTTP %d" % response.status_code)
                    errors.append(f"{cid}: {desc}")
            except (requests.RequestException, ValueError) as exc:
                safe_msg = str(exc).replace(bot_token, "***") if bot_token else str(exc)
                errors.append(f"{cid}: {safe_msg}")

        if ok_count == len(chat_ids):
            debug.log("[Telegram] Test OK (%d chat(s))" % ok_count)
            self.write({"success": True, "message": "ok"})
        elif ok_count > 0:
            debug.log("[Telegram] Test partial: %d/%d OK" % (ok_count, len(chat_ids)))
            self.write({"success": True, "message": "%d/%d OK, errors: %s" % (ok_count, len(chat_ids), "; ".join(errors))})
        else:
            msg = "; ".join(errors)
            debug.log("[Telegram] Test failed: %s" % msg)
            self.write({"success": False, "message": msg})

class OcrHandler(SecureAPIHandler):
    def get(self):
        self.write({"answer": "1234"})

    def post(self):
        _body = None
        is_pass_check = True
        errorMessage = ""
        errorCode = 0

        if is_pass_check:
            is_pass_check = False
            try :
                _body = json.loads(self.request.body)
                is_pass_check = True
            except Exception:
                errorMessage = "wrong json format"
                errorCode = 1001
                pass

        img_base64 = None
        image_data = ""
        if is_pass_check:
            if 'image_data' in _body:
                image_data = _body['image_data']
                if len(image_data) > 0:
                    img_base64 = base64.b64decode(image_data)
            else:
                errorMessage = "image_data not exist"
                errorCode = 1002

        #print("is_pass_check:", is_pass_check)
        #print("errorMessage:", errorMessage)
        #print("errorCode:", errorCode)
        ocr_answer = ""
        if not img_base64 is None:
            try:
                ocr_answer = self.application.ocr.classification(img_base64)
                print("ocr_answer:", ocr_answer)
            except Exception as exc:
                pass

        self.write({"answer": ocr_answer})

class QueryHandler(SecureAPIHandler):
    def format_config_keyword_for_json(self, user_input):
        if len(user_input) > 0:
            # Remove any existing quotes first
            user_input = user_input.replace('"', '').replace("'", '')

            # Add quotes to each keyword
            # Use semicolon as the ONLY delimiter (Issue #23)
            if util.CONST_KEYWORD_DELIMITER in user_input:
                items = user_input.split(util.CONST_KEYWORD_DELIMITER)
                user_input = ','.join([f'"{item.strip()}"' for item in items if item.strip()])
            else:
                user_input = f'"{user_input.strip()}"'
        return user_input

    def compose_as_json(self, user_input):
        user_input = self.format_config_keyword_for_json(user_input)
        return "{\"data\":[%s]}" % user_input

    def get(self):
        global txt_answer_value
        answer_text = ""
        try:
            answer_text = txt_answer_value.get().strip()
        except Exception as exc:
            pass
        answer_text_output = self.compose_as_json(answer_text)
        #print("answer_text_output:", answer_text_output)
        self.write(answer_text_output)

async def main_server():
    ocr = None
    try:
        ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
    except Exception as exc:
        print(exc)
        pass

    app = Application([
        ("/version", VersionHandler),
        ("/shutdown", ShutdownHandler),
        ("/sendkey", SendkeyHandler),

        # status api
        ("/status", StatusHandler),
        ("/pause", PauseHandler),
        ("/resume", ResumeHandler),
        ("/run", RunHandler),
        
        # json api
        ("/load", LoadJsonHandler),
        ("/save", SaveJsonHandler),
        ("/reset", ResetJsonHandler),

        ("/test_discord_webhook", TestDiscordWebhookHandler),
        ("/test_telegram", TestTelegramHandler),
        ("/ocr", OcrHandler),
        ("/query", QueryHandler),
        ("/question", QuestionHandler),
        ('/(.*)', NoCacheStaticFileHandler, {"path": os.path.join(SCRIPT_DIR, 'www')}),
    ])
    app.ocr = ocr;
    app.version = CONST_APP_VERSION;

    # Get server_port from config, fallback to default (Issue #156)
    _, config_dict = load_json()
    server_port = config_dict.get("advanced", {}).get("server_port", CONST_SERVER_PORT)

    # Validate port range
    if not isinstance(server_port, int) or server_port < 1024 or server_port > 65535:
        print(f"[WARNING] Invalid server_port: {server_port}, using default: {CONST_SERVER_PORT}")
        server_port = CONST_SERVER_PORT

    app.listen(server_port, address="127.0.0.1")
    print("server running on port:", server_port)

    url = "http://127.0.0.1:" + str(server_port) + "/settings.html"
    print("goto url:", url)
    webbrowser.open_new(url)
    await asyncio.Event().wait()

def get_server_port():
    """Get server port from config file, fallback to default."""
    _, config_dict = load_json()
    server_port = config_dict.get("advanced", {}).get("server_port", CONST_SERVER_PORT)
    if not isinstance(server_port, int) or server_port < 1024 or server_port > 65535:
        server_port = CONST_SERVER_PORT
    return server_port

def web_server():
    server_port = get_server_port()
    is_port_binded = util.is_connectable(server_port)
    #print("is_port_binded:", is_port_binded)
    if not is_port_binded:
        asyncio.run(main_server())
    else:
        print("port:", server_port, " is in used.")

def settgins_gui_timer():
    while True:
        change_maxbot_status_by_keyword()
        time.sleep(0.4)
        if GLOBAL_SERVER_SHUTDOWN:
            break

if __name__ == "__main__":
    global GLOBAL_SERVER_SHUTDOWN
    GLOBAL_SERVER_SHUTDOWN = False
    
    threading.Thread(target=settgins_gui_timer, daemon=True).start()
    threading.Thread(target=web_server, daemon=True).start()
    
    clean_tmp_file()

    print("To exit web server press Ctrl + C.")
    while True:
        time.sleep(0.4)
        if GLOBAL_SERVER_SHUTDOWN:
            break
    print("Bye bye, see you next time.")
