```markdown
# // CLONE(1)_ARCHIVER_V4

![Python](https://img.shields.io/badge/CORE-PYTHON_3.9+-000000?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/ENGINE-PLAYWRIGHT-D71921?style=for-the-badge&logo=googlechrome&logoColor=white)
![PyQt6](https://img.shields.io/badge/UI_MATRIX-PYQT6-000000?style=for-the-badge&logo=qt&logoColor=white)

SYSTEM_STATUS:   OPERATIONAL
RENDER_ENGINE:   CHROMIUM_HEADLESS
STEALTH_MODE:    ACTIVE (EVASION_LEVEL_3)
OUTPUT_TYPE:     STATIC_HTML + ASSETS


```

---

## // 01_SYSTEM_OVERVIEW

**CLONE(1)** is a high-precision, industrial-grade web archiving tool engineered to replicate modern, dynamic websites locally.

Unlike standard `wget` or `curl` requests, this system utilizes a **Headless Browser Engine** to execute JavaScript, render the DOM, and trigger lazy-loading events before capture. It features a custom "Nothing OS" styled GUI and integrates stealth modules to bypass anti-bot defenses.

### [ CORE_CAPABILITIES ]

> **DEEP ARCHIVAL:** Recursively captures HTML, CSS, Fonts, JS, and Media.
> **DOM RECONSTRUCTION:** Rewrites internal paths for 100% offline compatibility.
> **GHOST PROTOCOL:** Uses `playwright-stealth` to mask automation footprints.
> **LOCAL PREVIEW:** Instant verification via threaded HTTP server.

---

## // 02_ARCHITECTURE_PIPELINE

The system executes a strictly defined extraction sequence:

```text
[ TARGET_URL ] (HTTPS)
       |
       v
[ BROWSER_INJECTION ]
(Playwright Chromium + Stealth Scripts)
       |
       v
[ INTERACTION_PHASE ]
(Auto-Scroll / Lazy-Load Triggering / DOM Expansion)
       |
       v
[ ASSET_PARSING ]
(BeautifulSoup4: Map CSS/JS/IMG Links)
       |
       v
[ DOWNLOAD_THREADING ]
(ThreadPoolExecutor: Parallel Asset Acquisition)
       |
       v
[ DOM_REWRITE ]
(Path Normalization -> ./assets/...)
       |
       v
[ FINAL_OUTPUT ]
(index.html + Local Asset Folder)

```

---

## // 03_INSTALLATION_PROTOCOL

### 1. CLONE_REPOSITORY

```bash
git clone https://github.com/KiarashAkbari/Clone-1.git
cd Clone-1

```

### 2. INJECT_DEPENDENCIES

```bash
# Initialize Virtual Environment (Optional but Recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Core Modules
pip install -r requirements.txt
playwright install

```

### 3. INITIATE_SYSTEM

```bash
python cloner.py

```

---

## // 04_OPERATIONAL_MANUAL

The interface uses a brutalist, high-contrast design optimized for clarity.

### [ CONTROL_MATRIX ]

**1. TARGET_INPUT**

* Enter the full HTTPS URL. The system validates connectivity before initiation.

**2. DESTINATION_NODE**

* Select the root folder. The system will create an isolated `assets` directory inside.

**3. BACKGROUND_MODE (Toggle)**

* **[ON]:** Runs completely invisible (Headless). Faster.
* **[OFF]:** Opens a visible browser window. Useful for debugging interaction scripts.

**4. VISUAL_FEEDBACK**

* **LOGS:** Real-time terminal output of asset acquisition status.
* **PROGRESS:** Linear bar indicating batch download completion.

---

## // 05_FILE_STRUCTURE

```text
/ROOT
├── cloner.py                # [KERNEL] Main Logic & GUI
├── requirements.txt         # Dependency Manifest
├── .gitignore               # Exclusion Rules
│
├── [OUTPUT_FOLDER]/         # Generates upon execution
│   ├── index.html           # Reconstructed Entry Point
│   ├── cookies.json         # Session Data (If captured)
│   └── assets/              # [ASSET_VAULT]
│       ├── style_x89a.css
│       ├── script_b21.js
│       └── image_001.png
│
└── README.md                # System Documentation

```

---

## // 06_STEALTH_MECHANICS

Standard scrapers are easily blocked by WAFs (Web Application Firewalls). **CLONE(1)** implements the following evasion techniques:

| VECTOR | COUNTERMEASURE |
| --- | --- |
| **User-Agent** | Injects legitimate Windows 10 / Chrome headers. |
| **WebDriver** | Masks the `navigator.webdriver` property. |
| **Fingerprint** | Randomizes canvas readout noise. |
| **Behavior** | Simulates human scroll velocity and pauses. |

---

## // 07_ENGINEER_INFO

```text
DEVELOPER:    KIARASH AKBARI
PROJECT:      CLONE(1) // WEB_ARCHIVER
SOURCE:       [github.com/KiarashAkbari](https://github.com/KiarashAkbari)

```

---

## // 08_LEGAL_DISCLAIMER

```text
>> WARNING: EDUCATIONAL_USE_ONLY
>> COMPLIANCE_CHECK: REQUIRED

```

The developer assumes no liability for the misuse of this tool. Users must strictly adhere to:

1. **Robots.txt** policies of target domains.
2. **Copyright Laws** regarding intellectual property.
3. **Terms of Service** of the target infrastructure.

*System Halt.*

```

```
