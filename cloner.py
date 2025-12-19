import os
import re
import sys
import time
import json
import hashlib
import threading
import socket
import shutil
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

# library checks 
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("ERROR: Playwright not found. Run: pip install playwright && playwright install")
    sys.exit(1)

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
except ImportError:
    print("ERROR: PyQt6 not found. Run: pip install PyQt6")
    sys.exit(1)

# optional stealth module
try:
    from playwright_stealth import stealth_sync
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False

# configuration class 
class AppConfig:
    MAX_WORKERS = 24
    DOWNLOAD_TIMEOUT = 30
    NETWORK_IDLE_SECONDS = 3
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    LAZY_ATTRS = ["data-src", "data-srcset", "data-original", "data-url"]

# utilities 
def safe_filename_from_url(url):
    parsed = urlparse(url)
    path = parsed.path or ""
    if path.endswith("/") or path == "":
        name = "index"
    else:
        name = os.path.basename(path)
    name = name.split("?")[0].split("#")[0]
    if not name:
        name = "file"
    name = re.sub(r"[^0-9A-Za-z._-]", "_", name)
    return name[:200]

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def sha1_of_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def normalize_key(u):
    if not u: return u
    try:
        p = urlparse(u)
        base = p._replace(query="", fragment="").geturl()
        return base.rstrip("/")
    except Exception:
        return u.split("?")[0].split("#")[0].rstrip("/")

# network layer (asset downloader) 
class AssetDownloader:
    def __init__(self, output_folder, logger=None):
        self.output_folder = output_folder
        self.asset_folder = os.path.join(output_folder, "assets")
        ensure_dir(self.asset_folder)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": AppConfig.USER_AGENT})
        self.logger = logger or (lambda s: None)
        self.seen_urls = set()
        self.hash_index = {}
        self.lock = threading.Lock()

    def log(self, msg):
        self.logger(msg)

    def download_one(self, url):
        try:
            if not url or url.startswith("data:"): return None
            
            with self.lock:
                if url in self.seen_urls: return None
                self.seen_urls.add(url)

            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"): return None

            filename = safe_filename_from_url(url)
            candidate = os.path.join(self.asset_folder, filename)
            
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(candidate):
                candidate = os.path.join(self.asset_folder, f"{base}_{counter}{ext}")
                counter += 1

            r = self.session.get(url, stream=True, timeout=AppConfig.DOWNLOAD_TIMEOUT)
            r.raise_for_status()
            
            with open(candidate, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

            file_hash = sha1_of_file(candidate)
            
            with self.lock:
                if file_hash in self.hash_index:
                    existing_rel = self.hash_index[file_hash]
                    try: os.remove(candidate)
                    except: pass
                    return existing_rel
                else:
                    ext2 = os.path.splitext(candidate)[1]
                    stable_name = f"{file_hash[:12]}{ext2}"
                    stable_path = os.path.join(self.asset_folder, stable_name)
                    
                    try: os.replace(candidate, stable_path)
                    except OSError:
                        shutil.move(candidate, stable_path)
                        
                    rel_path = os.path.relpath(stable_path, self.output_folder).replace("\\", "/")
                    self.hash_index[file_hash] = rel_path
                    return rel_path

        except Exception as e:
            return None

    def download_batch(self, urls, progress_callback=None):
        results = {}
        urls = [u for u in urls if u and u.startswith("http")]
        
        with ThreadPoolExecutor(max_workers=AppConfig.MAX_WORKERS) as executor:
            future_map = {executor.submit(self.download_one, u): u for u in urls}
            for future in as_completed(future_map):
                url = future_map[future]
                try:
                    local_path = future.result()
                    results[url] = local_path
                    if progress_callback:
                        progress_callback(url, local_path)
                except Exception:
                    results[url] = None
        return results

# logic layer (cloner engine) 
class ClonerEngine(QtCore.QObject):
    log_signal = QtCore.pyqtSignal(str)
    progress_signal = QtCore.pyqtSignal(int)
    finished_signal = QtCore.pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    def log(self, msg):
        self.log_signal.emit(f"{msg}")

    def stop(self):
        self._stop_event.set()

    def extract_css_urls(self, css_text, base_url):
        urls = set()
        for m in re.finditer(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", css_text, re.IGNORECASE):
            urls.add(urljoin(base_url, m.group(1).strip()))
        for m in re.finditer(r"@import\s+['\"]([^'\"]+)['\"]", css_text, re.IGNORECASE):
            urls.add(urljoin(base_url, m.group(1).strip()))
        return urls

    def parse_html_assets(self, html, base_url):
        soup = BeautifulSoup(html, "html.parser")
        urls = set()
        tag_map = {
            "img": ["src", "srcset", "data-src", "data-srcset"],
            "script": ["src"],
            "link": ["href"],
            "video": ["src", "poster"],
            "audio": ["src"],
            "source": ["src", "srcset"],
            "iframe": ["src"]
        }
        for tag, attrs in tag_map.items():
            for node in soup.find_all(tag):
                for attr in attrs:
                    val = node.get(attr)
                    if not val: continue
                    if "srcset" in attr:
                        parts = [p.strip().split(" ")[0] for p in val.split(",") if p.strip()]
                        for p in parts: urls.add(urljoin(base_url, p))
                    else:
                        urls.add(urljoin(base_url, val))
        for node in soup.find_all(style=True):
            urls.update(self.extract_css_urls(node['style'], base_url))
        for node in soup.find_all("style"):
            if node.string: urls.update(self.extract_css_urls(node.string, base_url))
        return urls

    def run_clone(self, start_url, output_folder, headless=False):
        try:
            ensure_dir(output_folder)
            downloader = AssetDownloader(output_folder, logger=self.log)
            self._stop_event.clear()
            
            self.log(f"// SYSTEM_INIT: HEADLESS={str(headless).upper()}")
            
            network_urls = set()
            def handle_request(req):
                if req.url.startswith("http"):
                    network_urls.add(req.url)

            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=headless,
                    args=["--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
                )
                context = browser.new_context(
                    user_agent=AppConfig.USER_AGENT,
                    viewport={"width": 1920, "height": 1080}
                )
                
                # cookies
                cookie_file = os.path.join(output_folder, "cookies.json")
                if os.path.exists(cookie_file):
                    try:
                        with open(cookie_file, 'r') as f:
                            context.add_cookies(json.load(f))
                        self.log("[ AUTH: COOKIES_LOADED ]")
                    except Exception: pass

                page = context.new_page()
                if HAS_STEALTH: stealth_sync(page)
                page.on("request", handle_request)

                self.log(f">> NAVIGATING: {start_url}")
                try:
                    page.goto(start_url, wait_until="domcontentloaded", timeout=60000)
                except PlaywrightTimeoutError:
                    self.log("[ WARN: TIMEOUT_DETECTED ]")

                self.log("... SCROLL_SEQUENCE_ACTIVE")
                try:
                    for _ in range(5):
                        page.evaluate("window.scrollBy(0, document.body.scrollHeight / 5)")
                        time.sleep(0.5)
                    page.evaluate("""() => {
                        document.querySelectorAll('img[data-src], source[data-srcset]').forEach(el => {
                            if(el.dataset.src) el.src = el.dataset.src;
                            if(el.dataset.srcset) el.srcset = el.dataset.srcset;
                        });
                    }""")
                    time.sleep(2)
                except Exception: pass

                page_html = page.content()
                context.close()
                browser.close()

            if self._stop_event.is_set():
                self.finished_signal.emit(False, "PROCESS_TERMINATED")
                return

            self.log("// PARSING_ASSETS")
            html_assets = self.parse_html_assets(page_html, start_url)
            all_candidates = network_urls.union(html_assets)
            valid_urls = [u for u in all_candidates if u.startswith("http")]
            self.log(f">> TARGETS: {len(valid_urls)}")

            total = len(valid_urls)
            downloaded_count = 0
            
            def progress(url, local_path):
                nonlocal downloaded_count
                downloaded_count += 1
                pct = int((downloaded_count / total) * 100)
                self.progress_signal.emit(pct)
                if local_path:
                    self.log(f"ACQUIRED: {os.path.basename(local_path)}")
            
            results = downloader.download_batch(valid_urls, progress)

            url_map = {}
            for orig, local in results.items():
                if local: url_map[normalize_key(orig)] = local

            self.log("// REWRITING_DOM")
            soup = BeautifulSoup(page_html, "html.parser")
            
            def get_replacement(original_url):
                if not original_url: return None
                full_url = urljoin(start_url, original_url)
                norm = normalize_key(full_url)
                return url_map.get(norm)

            rewrite_targets = {
                "img": ["src", "data-src"], "link": ["href"], "script": ["src"],
                "source": ["src", "srcset"], "video": ["src", "poster"], "iframe": ["src"]
            }

            for tag, attrs in rewrite_targets.items():
                for node in soup.find_all(tag):
                    for attr in attrs:
                        val = node.get(attr)
                        if val:
                            local = get_replacement(val)
                            if local: node[attr] = local

            for img in soup.find_all("img"):
                if img.get("data-src") and not img.get("src"):
                    local = get_replacement(img.get("data-src"))
                    if local:
                        img['src'] = local
                        del img['data-src']

            index_path = os.path.join(output_folder, "index.html")
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(str(soup))

            self.log(">> OPERATION_SUCCESSFUL")
            self.finished_signal.emit(True, output_folder)

        except Exception as e:
            self.log(f"!! CRITICAL_FAILURE: {e}")
            self.finished_signal.emit(False, str(e))

# presentation layer 
class PreviewServer(threading.Thread):
    def __init__(self, folder, port=8000, logger=None):
        super().__init__(daemon=True)
        self.folder = folder
        self.port = port
        self.logger = logger
        self.httpd = None

    def run(self):
        try:
            os.chdir(self.folder)
            self.httpd = ThreadingHTTPServer(('127.0.0.1', self.port), SimpleHTTPRequestHandler)
            if self.logger: self.logger(f"PREVIEW_ONLINE: http://127.0.0.1:{self.port}")
            self.httpd.serve_forever()
        except Exception: pass

    def stop(self):
        if self.httpd: self.httpd.shutdown()

# GUI layer 
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = ClonerEngine()
        self.preview_server = None
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.setWindowTitle("CLONE(1)")
        self.resize(900, 800)
        self.apply_nothing_theme()

        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(0)

        # 1. header
        header = QtWidgets.QLabel("CLONER // VER 4.0")
        header.setObjectName("header")
        main_layout.addWidget(header)
        
        sep = QtWidgets.QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        main_layout.addWidget(sep)
        main_layout.addSpacing(30)

        # 2. input matrix
        form_layout = QtWidgets.QVBoxLayout()
        form_layout.setSpacing(20)

        # URL
        lbl_url = QtWidgets.QLabel("( TARGET )")
        self.txt_url = QtWidgets.QLineEdit()
        self.txt_url.setPlaceholderText("https://")
        form_layout.addWidget(lbl_url)
        form_layout.addWidget(self.txt_url)

        # folder
        lbl_folder = QtWidgets.QLabel("( DESTINATION )")
        folder_box = QtWidgets.QHBoxLayout()
        folder_box.setSpacing(-1)
        
        self.txt_folder = QtWidgets.QLineEdit()
        self.txt_folder.setPlaceholderText("ROOT/OUTPUT")
        
        btn_browse = QtWidgets.QPushButton("::")
        btn_browse.setFixedWidth(50)
        btn_browse.clicked.connect(self.browse_folder)
        
        folder_box.addWidget(self.txt_folder)
        folder_box.addWidget(btn_browse)
        
        form_layout.addWidget(lbl_folder)
        form_layout.addLayout(folder_box)

        # options
        self.chk_headless = QtWidgets.QCheckBox("BACKGROUND_MODE")
        self.chk_headless.setChecked(True)
        form_layout.addWidget(self.chk_headless)

        main_layout.addLayout(form_layout)
        main_layout.addSpacing(40)

        # 3. controls
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(15)

        self.btn_start = QtWidgets.QPushButton("INITIATE")
        self.btn_start.setObjectName("btn_primary")
        self.btn_start.setFixedHeight(50)

        self.btn_stop = QtWidgets.QPushButton("STOP")
        self.btn_stop.setObjectName("btn_danger")
        self.btn_stop.setFixedHeight(50)
        self.btn_stop.setEnabled(False)

        self.btn_preview = QtWidgets.QPushButton("VIEW")
        self.btn_preview.setObjectName("btn_outline")
        self.btn_preview.setFixedHeight(50)
        self.btn_preview.setEnabled(False)

        btn_layout.addWidget(self.btn_start, 2)
        btn_layout.addWidget(self.btn_stop, 1)
        btn_layout.addWidget(self.btn_preview, 1)
        main_layout.addLayout(btn_layout)
        
        main_layout.addSpacing(30)

        # 4. feedback
        self.progress = QtWidgets.QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        main_layout.addWidget(self.progress)
        
        main_layout.addSpacing(15)

        self.txt_log = QtWidgets.QPlainTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setPlainText("SYSTEM_READY...")
        main_layout.addWidget(self.txt_log)

        # 5. FOOTER 
        main_layout.addSpacing(20)
        
        sep2 = QtWidgets.QFrame()
        sep2.setObjectName("separator")
        sep2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        main_layout.addWidget(sep2)
        main_layout.addSpacing(15)
        
        footer_layout = QtWidgets.QHBoxLayout()
        
        
        lbl_dev = QtWidgets.QLabel()
        lbl_dev.setObjectName("footer_text")
        lbl_dev.setOpenExternalLinks(True)
        lbl_dev.setText(
            'DEV: <a href="https://github.com/KiarashAkbari" style="color: #D71921; text-decoration: none; font-weight: bold;">Kiarash Akbari</a> '
            '// <a href="https://github.com/KiarashAkbari" style="color: #D71921; text-decoration: none; font-weight: bold;">GitHub</a>'
        )
        
        # info label
        lbl_info = QtWidgets.QLabel("VER: 4.1 // [ EDUCATIONAL_USE_ONLY ]")
        lbl_info.setObjectName("footer_text")
        lbl_info.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        footer_layout.addWidget(lbl_dev)
        footer_layout.addStretch()
        footer_layout.addWidget(lbl_info)
        
        main_layout.addLayout(footer_layout)

        # connect
        self.btn_start.clicked.connect(self.start_process)
        self.btn_stop.clicked.connect(self.stop_process)
        self.btn_preview.clicked.connect(self.open_preview)

    def apply_nothing_theme(self):
        
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                selection-background-color: #D71921;
                selection-color: #ffffff;
            }
            
            /* Text */
            QLabel#header {
                font-size: 24px;
                letter-spacing: 2px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            
            /* Footer text default white */
            QLabel#footer_text {
                font-size: 15px;
                color: #ffffff; 
            }
            
            /* Dotted Line */
            QFrame#separator {
                border: none;
                border-bottom: 2px dotted #444444;
            }

            /* Inputs */
            QLineEdit {
                background-color: #000000;
                border: 2px solid #333333;
                color: #ffffff;
                padding: 15px;
                border-radius: 0px;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #ffffff;
            }

            /* Buttons */
            QPushButton {
                border-radius: 0px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton#btn_primary {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #ffffff;
            }
            QPushButton#btn_primary:hover {
                background-color: #D71921; /* Nothing Red */
                border: 2px solid #D71921;
                color: #ffffff;
            }
            
            QPushButton#btn_danger {
                background-color: #000000;
                color: #D71921;
                border: 2px dotted #D71921;
            }
            QPushButton#btn_danger:hover {
                background-color: #D71921;
                color: #ffffff;
                border: 2px solid #D71921;
            }
            
            QPushButton#btn_outline {
                background-color: #000000;
                color: #ffffff;
                border: 2px dotted #ffffff;
            }
            QPushButton#btn_outline:hover {
                background-color: #333333;
            }
            
            QPushButton:disabled {
                border: 2px dotted #333333;
                color: #333333;
                background-color: #000000;
            }

            /* Checkbox */
            QCheckBox {
                spacing: 10px;
                color: #888888;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #333333;
                background-color: #000000;
            }
            QCheckBox::indicator:checked {
                background-color: #D71921;
                border: 2px solid #D71921;
            }

            /* Progress */
            QProgressBar {
                background-color: #111111;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #D71921;
            }

            /* Logs */
            QPlainTextEdit {
                background-color: #000000;
                border: none;
                border-top: 2px dotted #333333;
                color: #888888;
                font-size: 12px;
                padding-top: 15px;
            }
        """)

    def connect_signals(self):
        self.engine.log_signal.connect(self.append_log)
        self.engine.progress_signal.connect(self.progress.setValue)
        self.engine.finished_signal.connect(self.on_finished)

    def browse_folder(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "SELECT_DIR")
        if path:
            self.txt_folder.setText(path)

    def append_log(self, text):
        self.txt_log.appendPlainText(text)

    def start_process(self):
        url = self.txt_url.text().strip()
        folder = self.txt_folder.text().strip()
        headless = self.chk_headless.isChecked()

        if not url or not folder:
            QtWidgets.QMessageBox.warning(self, "ERR_INPUT", "MISSING_DATA")
            return

        self.txt_log.clear()
        self.progress.setValue(0)
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_preview.setEnabled(False)

        t = threading.Thread(target=self.engine.run_clone, args=(url, folder, headless), daemon=True)
        t.start()

    def stop_process(self):
        self.engine.stop()
        self.append_log("// HALT_SIGNAL_SENT")
        self.btn_stop.setEnabled(False)

    def on_finished(self, success, result):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        if success:
            QtWidgets.QMessageBox.information(self, "SUCCESS", "PROCESS_COMPLETE")
            self.start_preview_server(result)
        else:
            QtWidgets.QMessageBox.critical(self, "FAILURE", f"ERR: {result}")

    def start_preview_server(self, folder):
        if self.preview_server: self.preview_server.stop()
        port = 8000
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                break
            except OSError: port += 1
        
        self.preview_server = PreviewServer(folder, port, self.append_log)
        self.preview_server.start()
        self.preview_url = f"http://127.0.0.1:{port}"
        self.btn_preview.setEnabled(True)

    def open_preview(self):
        import webbrowser
        if hasattr(self, 'preview_url'):
            webbrowser.open(self.preview_url)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
