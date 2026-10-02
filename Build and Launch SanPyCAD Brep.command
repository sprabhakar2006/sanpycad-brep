#!/bin/bash
# Double-click this file to build and launch SanPyCAD Brep. No Terminal
# typing required -- everything happens automatically, in a clean,
# isolated virtual environment (so nothing else installed on this
# Mac can interfere). If something goes wrong, this window stays
# open with the error on screen instead of disappearing.
#
# Note: this app bundles build123d/OCP (the OpenCASCADE B-rep engine),
# which is a much larger download and a slower build than the plain
# SanPyCAD app -- the first run can take 5-10 minutes. Later runs are
# fast because the environment and dependencies are kept in place.
set -uo pipefail
cd "$(dirname "$0")"

echo "=== SanPyCAD Brep one-click build ==="
echo

VENV_DIR=".build_venv"

fail() {
  echo
  echo "!!! FAILED: $1"
  echo
  read -p "Press Enter to close this window..."
  exit 1
}

PYTHON_BIN="$(command -v python3)"
if [ -z "$PYTHON_BIN" ]; then
  fail "python3 not found. Install Python 3.10+ from python.org (tick \"Add Python to PATH\" on Windows; on Mac it's on PATH automatically), then double-click this file again."
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating a clean, isolated Python environment (first run only, about a minute)..."
  "$PYTHON_BIN" -m venv "$VENV_DIR" || fail "Could not create the virtual environment"
fi

source "$VENV_DIR/bin/activate" || fail "Could not activate the virtual environment"

echo "Installing/checking dependencies (build123d is a large download the first time -- please be patient)..."
pip install --quiet --upgrade pip || fail "pip upgrade failed"
pip install --quiet numpy "scipy==1.13.1" sympy scikit-image pywebview pyperclip pyinstaller build123d ipython || fail "Dependency install failed -- check your internet connection"

echo
echo "Closing any already-running copy of SanPyCAD Brep..."
# Without this, re-running this script while an earlier launch is still
# open leaves the old one running and starts a second, independent copy
# on top of it -- do that a few times (e.g. while testing a fix) and you
# end up with several duplicate processes/Dock icons for what looks like
# one app. pkill -f matches on the full command line, so this only
# targets this app's own built binary, not SanPyCAD (the other app) or
# anything else.
pkill -f "dist/SanPyCAD Brep.app/Contents/MacOS/SanPyCAD Brep" 2>/dev/null || true
sleep 1

echo
echo "Cleaning up any previous build..."
rm -rf dist build

echo
echo "Building the app (this takes several minutes the first time -- please wait)..."
python packaging/build_bundle.py || fail "Build failed -- see the error above. Copy it and send it back for help."

echo
echo "=== Build succeeded. Launching SanPyCAD Brep... ==="
rm -f launch_debug.log
nohup "dist/SanPyCAD Brep.app/Contents/MacOS/SanPyCAD Brep" > launch_debug.log 2>&1 &
APP_PID=$!
disown
# Give the app a few seconds to either settle into its window or crash.
# Checking just once right away is what caused false "it's running" reports
# in the past (the app can still crash a second or two after this point,
# or the process can look alive for a moment while it's actually failing
# to open a window) -- polling a few times, and treating any traceback
# that shows up in the log as a real failure even if the process is still
# technically alive, catches both of those cases.
SUCCESS=0
for i in 1 2 3 4 5 6; do
  sleep 1
  if ! kill -0 "$APP_PID" 2>/dev/null; then
    break
  fi
  if grep -qi "Traceback (most recent call last)" launch_debug.log 2>/dev/null; then
    break
  fi
done
if kill -0 "$APP_PID" 2>/dev/null && ! grep -qi "Traceback (most recent call last)" launch_debug.log 2>/dev/null; then
  SUCCESS=1
fi

if [ "$SUCCESS" = "1" ]; then
  echo
  echo "All done! SanPyCAD Brep is running. You can close this window --"
  echo "the app stays open on its own."
else
  echo
  echo "!!! SanPyCAD Brep quit unexpectedly or failed to start. Its output:"
  echo
  cat launch_debug.log
  fail "SanPyCAD Brep did not start correctly -- see the output above (also saved to launch_debug.log). Copy it and send it back for help."
fi
read -p "Press Enter to close..."
