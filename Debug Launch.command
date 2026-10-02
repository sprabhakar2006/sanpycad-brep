#!/bin/bash
# Diagnostic helper (not part of the shipped bundle): runs the already-built
# dist/SanPyCAD Brep.app directly, capturing its output to launch_debug.log,
# without rebuilding. Used to see the real crash reason instead of a silent
# vanish when launched via Finder/open.
cd "$(dirname "$0")"
rm -f launch_debug.log
"dist/SanPyCAD Brep.app/Contents/MacOS/SanPyCAD Brep" > launch_debug.log 2>&1 &
APP_PID=$!
sleep 5
if kill -0 "$APP_PID" 2>/dev/null; then
  echo "RUNNING (pid $APP_PID)"
else
  echo "QUIT -- output follows:"
  cat launch_debug.log
fi
read -p "Press Enter to close..."
