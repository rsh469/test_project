# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Tea Flavor Aggregator.
Build:  pyinstaller tea_aggregator.spec
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_all, copy_metadata

block_cipher = None

# ── Collect data files from key packages ─────────────────────────────────────

datas = []

# Package metadata (needed by importlib.metadata / pkg_resources)
for pkg in [
    "streamlit", "altair", "plotly", "pandas", "numpy", "matplotlib",
    "Pillow", "wordcloud", "beautifulsoup4", "lxml", "requests",
    "tornado", "click", "packaging", "pyarrow", "pydeck",
    "validators", "watchdog", "toml", "gitpython",
]:
    try:
        datas += copy_metadata(pkg)
    except Exception:
        pass  # skip packages that don't have dist-info

# Our own source files
datas += [
    ("app.py",        "."),
    ("scrapers.py",   "."),
    ("aggregator.py", "."),
    ("taxonomy.py",   "."),
]

# Streamlit — needs its full tree (static/, components/, etc.)
datas += collect_data_files("streamlit", include_py_files=False)

# Altair schemas and vega datasets
datas += collect_data_files("altair")
datas += collect_data_files("vega_datasets")

# Plotly static assets
datas += collect_data_files("plotly")

# Matplotlib mpl-data (fonts, styles, etc.)
datas += collect_data_files("matplotlib")

# Pandas data
datas += collect_data_files("pandas")

# Wordcloud bundled fonts
datas += collect_data_files("wordcloud")

# Pillow
datas += collect_data_files("PIL")

# BeautifulSoup
datas += collect_data_files("bs4")

# Trafilatura
datas += collect_data_files("trafilatura", include_py_files=False)

# ── Hidden imports ────────────────────────────────────────────────────────────

hiddenimports = [
    # Streamlit internals
    "streamlit.web.bootstrap",
    "streamlit.web.server",
    "streamlit.web.cli",
    "streamlit.runtime",
    "streamlit.runtime.scriptrunner",
    "streamlit.runtime.caching",
    "streamlit.runtime.legacy_caching",
    "streamlit.components.v1",
    "streamlit.source_util",
    "streamlit.logger",
    "streamlit.config",
    "streamlit.util",
    # Altair / Vega
    "altair",
    "vega_datasets",
    "toolz",
    "cytoolz",
    # Plotly
    "plotly.graph_objects",
    "plotly.express",
    "plotly.io",
    "plotly.subplots",
    # Data
    "pandas",
    "pandas._libs.tslibs.np_datetime",
    "pandas._libs.tslibs.nattype",
    "pandas._libs.tslibs.timedeltas",
    "pandas._libs.tslibs.timestamps",
    "numpy",
    "numpy.core._methods",
    "numpy.lib.format",
    # Viz
    "matplotlib",
    "matplotlib.backends.backend_agg",
    "PIL",
    "PIL.Image",
    "wordcloud",
    # Scraping
    "bs4",
    "lxml",
    "lxml.etree",
    "lxml._elementpath",
    "requests",
    "urllib3",
    "certifi",
    "charset_normalizer",
    # Other
    "langdetect",
    "praw",
    "trafilatura",
    "click",
    "tornado",
    "packaging",
    "importlib_metadata",
    "pyarrow",
    "tzdata",
    "gitpython",
    "pympler",
    "validators",
    "watchdog",
    "toml",
]

# ── Analysis ──────────────────────────────────────────────────────────────────

a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=["hooks"],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "IPython",
        "jupyter",
        "notebook",
        "scipy",
        "sklearn",
        "tensorflow",
        "torch",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # onedir mode (more reliable)
    name="tea-flavor-aggregator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,                   # show terminal so user sees server log
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="tea-flavor-aggregator",
)
