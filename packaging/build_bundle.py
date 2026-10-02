#!/usr/bin/env python3
"""
build_bundle.py -- build the self-contained SanPyCAD Brep bundle for
the machine you run it on. One command, from the project root:

    python packaging/build_bundle.py

It produces dist/SanPyCAD Brep.app (macOS), dist/SanPyCAD Brep/
(Windows and Linux), and a zip of that next to it, ready to attach to
a GitHub release. The result carries its own Python and every
library -- including build123d and its OCP/OpenCASCADE dependency --
so the person who downloads it installs nothing.

PyInstaller cannot cross-compile: a macOS bundle can only be built on
macOS and a Windows one only on Windows. Building both without owning
both machines is what .github/workflows/build-installers.yml is for --
it runs this same script on GitHub's macOS and Windows runners.

Steps:
  1. check the build dependencies are importable
  2. download CodeMirror/Three.js into frontend/vendor/ if missing, so
     the bundle is offline-capable from its very first launch
  3. run PyInstaller against packaging/sanpycad.spec
  4. zip the result
"""
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "packaging" / "sanpycad.spec"
DIST = ROOT / "dist"
BUILD = ROOT / "build"

IS_MAC = sys.platform == "darwin"
IS_WINDOWS = os.name == "nt"

# Imported by the app itself (not by this script) -- checked here so a
# missing one is reported now rather than as a broken bundle later.
# build123d is listed first and is NOT optional here, unlike the
# sibling (mesh-based) SanPyCAD app: this whole app is built on it.
RUNTIME_DEPS = ["build123d", "IPython", "numpy", "scipy", "sympy", "skimage", "webview", "pyperclip"]


def step(msg):
    print(f"\n==> {msg}", flush=True)


def check_deps():
    step("Checking build dependencies")
    # The geometry library uses match statements, so the interpreter
    # that gets frozen into the bundle has to be 3.10 or newer.
    if sys.version_info < (3, 10):
        print(f"  Python {sys.version.split()[0]} is too old -- SanPyCAD Brep needs 3.10+")
        sys.exit(1)
    print(f"  Python {sys.version.split()[0]}  ok")
    missing = []
    try:
        import PyInstaller  # noqa: F401
        print("  PyInstaller  ok")
    except ImportError:
        missing.append("pyinstaller")

    for name in RUNTIME_DEPS:
        try:
            __import__(name)
            print(f"  {name:12} ok")
        except ImportError:
            missing.append({"skimage": "scikit-image", "webview": "pywebview"}.get(name, name))

    if missing:
        print("\nMissing, and the bundle cannot be built without them:")
        print(f"    {sys.executable} -m pip install {' '.join(missing)}")
        sys.exit(1)


def fetch_vendor_assets():
    """Put CodeMirror/Three.js in frontend/vendor/ before freezing.

    The app normally downloads these on its first run, but a bundle
    installed in /Applications or Program Files has nowhere writable
    to put them. Fetching them at build time means the bundle works
    offline from the first launch and never tries to write to itself.
    """
    step("Fetching editor/3D-viewer assets into frontend/vendor/")
    sys.path.insert(0, str(ROOT / "backend"))
    import vendor_assets

    missing = vendor_assets.missing_assets()
    if not missing:
        print("  already present")
        return
    print(f"  {len(missing)} missing, downloading...")
    still_missing = vendor_assets.ensure_vendor_assets(timeout=30)
    if still_missing:
        print(f"\nERROR: {len(still_missing)} asset(s) could not be downloaded:")
        for rel in still_missing:
            print(f"    {rel}")
        print("These are needed for the bundle to work offline. Check the "
              "internet connection and run this script again.")
        sys.exit(1)
    print("  done")


def run_pyinstaller():
    step("Running PyInstaller (this takes a few minutes -- OCP/OpenCASCADE "
         "alone is a large library to collect and copy)")
    for path in (BUILD, DIST):
        if path.exists():
            shutil.rmtree(path)
    # Run through _run_pyinstaller_patched.py rather than `python -m
    # PyInstaller` directly -- it works around a CPython 3.12.0 bug that
    # otherwise corrupts scipy.stats when bundled on that exact Python
    # version, crashing the shipped app with "NameError: name 'obj' is
    # not defined" even though the build itself succeeds. See that
    # file's own docstring for the full story.
    cmd = [sys.executable, str(ROOT / "packaging" / "_run_pyinstaller_patched.py"),
           "--noconfirm", "--clean", str(SPEC)]
    print(f"  {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def sign_macos(app_path):
    """Ad-hoc code-sign the built .app.

    Without this, the app refuses to launch at all on Apple Silicon --
    macOS requires every arm64 executable to carry at least a
    signature, even an unsigned/ad-hoc one, and PyInstaller does not
    sign its own output. This is NOT Apple notarization (still shows
    the "unidentified developer" warning on first launch -- see
    README.md), just enough of a signature for Gatekeeper to allow the
    app to run at all. The CI workflow already did this; it belongs
    here too so a local build (no CI involved) isn't silently broken
    the same way.
    """
    step("Ad-hoc signing (required on Apple Silicon, harmless on Intel)")
    subprocess.run(["codesign", "--force", "--deep", "--sign", "-", str(app_path)], check=True)
    subprocess.run(["codesign", "--verify", "--verbose", str(app_path)], check=True)


def zip_result():
    step("Zipping the bundle")
    tag = "mac" if IS_MAC else ("win" if IS_WINDOWS else "linux")
    if IS_MAC:
        target, zip_path = DIST / "SanPyCAD Brep.app", DIST / f"SanPyCAD-Brep-{tag}.zip"
        sign_macos(target)
        # ditto, not zipfile: it is the only thing that reliably keeps
        # the executable bit and symlinks inside a .app, without which
        # the unzipped app will not launch.
        subprocess.run(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent",
                        str(target), str(zip_path)], check=True)
    else:
        target, zip_path = DIST / "SanPyCAD Brep", DIST / f"SanPyCAD-Brep-{tag}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(target.rglob("*")):
                if path.is_file():
                    zf.write(path, Path("SanPyCAD Brep") / path.relative_to(target))

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  {zip_path.name}  ({size_mb:.0f} MB)")
    return target, zip_path


def main():
    check_deps()
    fetch_vendor_assets()
    run_pyinstaller()
    target, zip_path = zip_result()
    print(f"\nBuilt: {target}")
    print(f"Ship:  {zip_path}")
    if IS_MAC:
        print("\nThis bundle is not notarized by Apple, so the first launch on "
              "another Mac shows an 'unidentified developer' warning: right-click "
              "the app > Open > Open. See README.md.")


if __name__ == "__main__":
    main()
