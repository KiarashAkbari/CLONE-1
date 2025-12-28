# // CLONE(1)_ARCHIVER

![Python](https://img.shields.io/badge/CORE-PYTHON_3.9+-000000?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/ENGINE-HYBRID_SYNC_ASYNC-D71921?style=for-the-badge&logo=googlechrome&logoColor=white)
![PyQt6](https://img.shields.io/badge/UI_MATRIX-PYQT6-000000?style=for-the-badge&logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/DB-SQLITE3_PERSISTENCE-000000?style=for-the-badge&logo=sqlite&logoColor=white)

SYSTEM_STATUS:   OPERATIONAL

RENDER_ENGINE:   CHROMIUM_HEADLESS (HYBRID)

STEALTH_MODE:    ACTIVE (EVASION_LEVEL_4)

OUTPUT_TYPE:     RECURSIVE_SITE_MIRROR + 3D_ASSETS

---

## // 01_SYSTEM_OVERVIEW

**CLONE(1)** is a definitive, industrial-grade web reconnaissance and archiving tool. It has evolved from a single-page cloner into a **Recursive Crawler** capable of replicating entire domain structures.

It utilizes a novel **Hybrid Architecture**:
1.  **Synchronous Browser Core:** For precise, human-like interaction (clicking tabs, expanding menus, triggering lazy loads).
2.  **Asynchronous Download Engine:** For high-velocity, non-blocking asset acquisition using `aiohttp` and `asyncio`.

### [ CORE_CAPABILITIES ]

> **RECURSIVE CRAWLING:** Automatically discovers and archives internal links to mirror the full site structure.
> **DEEP INTERACTION:** Actively clicks `[role="tab"]`, `.load-more`, and triggers scroll events to expose hidden DOM elements.
> **3D ASSET INTERCEPTION:** Embedded engine captures WebGL buffers, textures, `.glb`, and `.gltf` models directly from the GPU stream.
> **STATE PERSISTENCE:** Uses SQLite (`clone_cache.db`) to track progress, allowing pause/resume functionality without re-downloads.
> **ZERO-RAM STREAMING:** Writes data chunks directly to disk, enabling massive archives (50GB+) on low-memory systems.

---

## // 02_ARCHITECTURE_PIPELINE

The system executes a dual-phase extraction sequence:

```text
[ TARGET_URL ]
       |
       v
[ PHASE_1: SYNCHRONOUS_HARVEST ]
(Playwright Sync Thread)
   |-- Human Simulation (Scroll/Click/Expand)
   |-- WebGL Interception
   |-- DOM Serialization
       |
       v
[ SQLITE_STATE_MANAGER ]
(Deduplication & Queue Management)
       |
       v
[ PHASE_2: ASYNCHRONOUS_ENGINE ]
(AsyncIO Event Loop)
   |-- Asset Analysis (CSS/GLTF Recursion)
   |-- High-Concurrency Downloading (64 Threads)
   |-- Path Rewriting (Local Linking)
       |
       v
[ FINAL_OUTPUT ]
(Structured Directories + Offline Site)

```

---

## // 03_INSTALLATION_PROTOCOL

### 1. CLONE_REPOSITORY

```bash
git clone [https://github.com/KiarashAkbari/Clone-1.git](https://github.com/KiarashAkbari/Clone-1.git)
cd Clone-1

```

### 2. INJECT_DEPENDENCIES

```bash
# Initialize Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Core Modules
pip install -r requirements.txt
playwright install chromium

```

*Required Libraries:* `playwright`, `PyQt6`, `aiohttp`, `aiofiles`, `beautifulsoup4`, `playwright-stealth`.

### 3. INITIATE_SYSTEM

```bash
python cloner.py

```

---

## // 04_OPERATIONAL_MANUAL

The interface maintains the signature brutalist, high-contrast design.

### [ CONTROL_MATRIX ]

**1. TARGET_INPUT**

* Enter the entry point URL. The crawler will respect the domain boundary.

**2. DESTINATION_NODE**

* Select the root output folder. Directories will be created automatically based on the URL path structure.

**3. BACKGROUND_MODE**

* **[ON]:** Maximum performance.
* **[OFF]:** Watch the browser interact with the page (useful for verifying tab clicks).

**4. 3D_CAPTURE_MODE**

* Enables the embedded WebGL interception engine. Captures canvas snapshots and raw 3D model files.

---

## // 05_FILE_STRUCTURE

```text
/ROOT
├── cloner.py                # [KERNEL] Hybrid Async/Sync Engine
├── requirements.txt         # Dependency Manifest
├── github_icon.png          # UI Assets
│
├── [OUTPUT_FOLDER]/         # Generates upon execution
│   ├── clone_cache.db       # [SQLITE] State Persistence File
│   ├── cookies.json         # Session Data
│   │
│   ├── assets/              # [GLOBAL_ASSETS] (CSS/JS/Fonts)
│   ├── assets_3d/           # [3D_VAULT] (Models/Textures)
│   │
│   ├── index.html           # Home Page
│   └── about/               # [RECURSIVE_STRUCTURE]
│       └── index.html       # Mirrored Internal Pages
│
└── README.md                # System Documentation

```

---

## // 06_STEALTH_MECHANICS

**CLONE(1)** employs advanced evasion to bypass WAFs during deep crawls:

| VECTOR | COUNTERMEASURE |
| --- | --- |
| **Async Politeness** | Download workers use smart throttling to avoid IP bans. |
| **Hybrid Interaction** | Browser actions are synchronous and randomized, mimicking real user latency. |
| **Navigator Masking** | Overrides `webdriver` flags and injects consistent platform headers. |

---

## // 07_ENGINEER_INFO

```text
LEAD_ENGINEER:    KIARASH AKBARI
PROJECT:          CLONE(1) // WEB_ARCHIVER_V16
CONCEPT:          WITH THE HELP OF MY FRIEND MOHAMMAD RAISI
SOURCE:           [github.com/KiarashAkbari](https://github.com/KiarashAkbari)
```

---

## // 08_LEGAL_DISCLAIMER


```text
>> LICENSE_TYPE: GNU GPLv3 (COPYLEFT)
>> CLOSED_SOURCE_USE: PROHIBITED
>> SOURCE_DISCLOSURE: MANDATORY
```

**[ NOTICE_OF_NON_LIABILITY ]**

The usage of **CLONE(1)** constitutes an agreement that the user assumes all risks associated with its operation.

1. **NO WARRANTIES:** This software is provided "as is," without warranty of any kind, express or implied.
2. **TARGET_COMPLIANCE:** Users are solely responsible for ensuring their actions comply with the **Terms of Service**, **Robots.txt**, and **Privacy Policies** of any target URL.
3. **DATA_SOVEREIGNTY:** The developer disclaims all responsibility for intellectual property violations, server strain, or data misuse resulting from the deployment of this tool.

**[ ETHICAL_DIRECTIVE ]**

> Do not deploy against government infrastructure, financial institutions, or non-consenting private networks.

*System Halt.*

```

```
