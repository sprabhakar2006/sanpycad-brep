# -*- mode: python ; coding: utf-8 -*-
"""
sanpycad.spec -- PyInstaller recipe for the self-contained SanPyCAD
Brep bundle: a CPython interpreter, every library the app needs, and
the app's own files in one folder the user can double-click. Nothing
has to be installed alongside it.

Build it with `python packaging/build_bundle.py` (which fetches the
editor/viewer assets first, then calls PyInstaller on this file)
rather than invoking pyinstaller by hand.

Adapted from the sibling SanPyCAD app's own sanpycad.spec. The one
fundamental difference: this app is B-rep-first (backend/brep.py wraps
build123d/OpenCASCADE), so build123d and its own OCP (OpenCASCADE
Python bindings) dependency are a HARD requirement here, not an
excluded optional extra the way they are in the mesh-based SanPyCAD
app's spec. OCP in particular is a large pybind11-wrapped native
library with many submodules that static analysis can't fully see
into (worse than scipy/skimage/sympy below, which at least are pure
Python once past their own C extensions) -- so rather than hand-list
hiddenimports for it the way the rest of this file does, it is pulled
in with PyInstaller's own collect_all(), the standard approach for a
complex compiled package where an incomplete hand list would produce
a bundle that LOOKS built but fails with an ImportError the first
time a script reaches some rarely-used corner of OCP at runtime.

The one other unusual thing here (shared with the sibling spec):
backend/*.py are NOT frozen as code. They are loader stubs that read
backend/_protected/<name>.enc from a path derived from their own
__file__, so they must stay real files on disk inside the bundle. They
are therefore shipped as DATA, and their module names are excluded so
PyInstaller's own frozen importer can't shadow the on-disk copies at
runtime. Because their real source is encrypted, PyInstaller cannot
scan it for imports either -- so everything those modules import
(other than build123d/OCP, handled above) is listed by hand in
hiddenimports below. Anything missing from that list shows up as an
ImportError on first render, not at build time.
"""
import os
import sys

from PyInstaller.building.datastruct import Tree
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_all

PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))
IS_WINDOWS = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"

# Backend modules shipped as encrypted source + on-disk loader stub.
# Keep in sync with build_protected_backend.py's MODULES list.
PROTECTED_MODULES = [
    "brep", "drawing_layout", "geom_ops", "kernel_breadcrumb",
    "kernel_manager", "kernel_process", "mesh_types", "ocad",
    "python_eval", "server", "step_export",
]
# Plain-source backend files that must also load from disk, so that
# their own __file__-relative paths (backend/_protected/, frontend/
# vendor/) keep resolving the same way they do from source.
BACKEND_LOADED_FROM_DISK = PROTECTED_MODULES + [
    "_crypto_loader", "openscad4", "vendor_assets",
]

# --- what the encrypted backend imports, since it can't be scanned ----
# brep.py reaches for build123d (collected separately below via
# collect_all, along with its OCP dependency). ocad.py -- bundled as
# the opt-in mesh/point-list escape hatch a script can `import ocad`
# for -- and python_eval.py/step_export.py reach for scipy.spatial
# (ConvexHull, cKDTree, Delaunay), scipy.interpolate
# (make_interp_spline), skimage.measure (marching cubes, find_contours,
# approximate_polygon), skimage.draw.polygon and sympy. Those pull in a
# web of internal submodules lazily -- skimage in particular uses
# lazy_loader, so nothing is importable at analysis time -- so whole
# packages are collected rather than named leaves. What is NOT
# collected is the image-I/O stack under skimage.io (OpenCV, Pillow,
# imageio and Qt): excluded below, it is never reached and would
# otherwise roughly triple the download.
hiddenimports = [
    "numpy", "sympy", "pyperclip", "webview",
    "scipy.spatial", "scipy.interpolate", "scipy.ndimage", "scipy.signal",
    "skimage.measure", "skimage.draw", "skimage._shared",
]
for pkg in ("scipy", "skimage", "sympy"):
    hiddenimports += collect_submodules(pkg)
hiddenimports += [
    "ast", "base64", "collections", "contextlib", "datetime", "functools",
    "http.server", "inspect", "io", "json", "math", "multiprocessing",
    "multiprocessing.spawn", "platform", "queue", "re", "shutil", "socket",
    "socketserver", "struct", "subprocess", "tempfile", "threading", "time",
    "traceback", "urllib.request", "warnings", "webbrowser",
    "xml.etree.ElementTree",
]

datas = collect_data_files("sympy")
binaries = []

# build123d + its OCP (OpenCASCADE Python bindings) dependency -- see
# this file's own docstring for why collect_all() rather than a hand
# list. OCP in particular ships its own compiled extension modules and
# shared libraries (the actual OpenCASCADE/OCCT libs), which is what
# the `binaries` half of collect_all() is for; a plain hiddenimports
# entry would miss those entirely and the bundle would fail to even
# import build123d.
#
# lib3mf is a separate top-level package (not a submodule of OCP) that
# build123d reaches for its own native dylib (lib3mf/lib3mf.dylib) at
# runtime, outside of any Python import PyInstaller's static analysis
# can see -- so without collecting it explicitly here too, the bundle
# builds and even imports build123d successfully, but throws
# "ImportError: The required binary .../lib3mf.dylib could not be
# found" the first time a script actually exercises brep.py.
for pkg in ("build123d", "OCP", "lib3mf"):
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports

a = Analysis(
    [os.path.join(PROJECT_ROOT, "app.py")],
    pathex=[PROJECT_ROOT, os.path.join(PROJECT_ROOT, "packaging")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[os.path.join(PROJECT_ROOT, "packaging", "runtime_hook_scipy.py")],
    excludes=BACKEND_LOADED_FROM_DISK + [
        # The rest arrive as incidental dependencies of scipy/skimage/
        # sympy and are never reached at runtime; cv2, Pillow, imageio
        # and Qt alone are ~350 MB. Unlike the sibling SanPyCAD app's
        # spec, build123d/OCP are deliberately NOT in this list -- see
        # the docstring above.
        #
        # IPython is ALSO deliberately not excluded here, unlike the
        # sibling SanPyCAD spec this file was adapted from: build123d's
        # own topology/shape_core.py does an unconditional top-level
        # `from IPython.lib.pretty import ...`, so excluding it produces
        # a bundle that imports fine at analysis time but throws
        # "ModuleNotFoundError: No module named 'IPython'" the first
        # time a script actually calls brep.py (which imports
        # build123d). This bit twice before being tracked down to this
        # excludes list -- pip installing ipython into the build venv
        # is not enough on its own, since PyInstaller still drops it
        # from the bundle if it is named here.
        "jupyter", "notebook", "pytest", "pandas",
    ],
    noarchive=False,
)

# The app's own files, copied in as data (see the module docstring).
a.datas += Tree(os.path.join(PROJECT_ROOT, "backend"), prefix="backend",
                excludes=["__pycache__", "_protected_src", "*.pyc"])
a.datas += Tree(os.path.join(PROJECT_ROOT, "frontend"), prefix="frontend",
                excludes=["__pycache__", "*.pyc"])
a.datas += Tree(os.path.join(PROJECT_ROOT, "examples"), prefix="examples",
                excludes=["__pycache__", "*.pyc"])
a.datas += Tree(os.path.join(PROJECT_ROOT, "packaging"), prefix="packaging",
                excludes=["__pycache__", "*.pyc", "*.spec", "build_bundle.py",
                          "entitlements.plist"])

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SanPyCAD Brep",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # console=False everywhere: this is a windowed app. On Windows that
    # is what stops a black terminal opening behind the app window.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=IS_MAC,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="SanPyCAD Brep",
)

if IS_MAC:
    app = BUNDLE(
        coll,
        name="SanPyCAD Brep.app",
        icon=None,
        # Distinct from the sibling SanPyCAD app's com.sanpycad.app so
        # macOS treats these as two different apps (separate Dock
        # identity, separate Application Support folder, installable
        # side by side) rather than one app overwriting the other.
        bundle_identifier="com.sanpycadbrep.app",
        info_plist={
            "CFBundleName": "SanPyCAD Brep",
            "CFBundleDisplayName": "SanPyCAD Brep",
            "CFBundleShortVersionString": os.environ.get("SANPYCAD_BREP_VERSION", "1.0.0"),
            "CFBundleVersion": os.environ.get("SANPYCAD_BREP_VERSION", "1.0.0"),
            "NSHighResolutionCapable": True,
            # Without this the app window opens behind other windows and
            # the app gets no Dock icon on some macOS versions.
            "LSBackgroundOnly": False,
            "NSRequiresAquaSystemAppearance": False,
        },
    )
