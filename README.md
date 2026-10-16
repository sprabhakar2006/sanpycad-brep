<div align="center">

# SanPyCAD Brep

**Script exact, fillet-ready solids in Python — real B-rep geometry on OpenCASCADE, exported as true STEP.**

[![Download](https://img.shields.io/github/v/release/sprabhakar2006/sanpycad-brep?label=download&color=2ea44f)](https://github.com/sprabhakar2006/sanpycad-brep/releases/latest)
![Platforms](https://img.shields.io/badge/platform-macOS%20(Apple%20Silicon)%20%7C%20Windows-0a7bbb)
[![Kernel: build123d / OCCT](https://img.shields.io/badge/kernel-build123d%20%2F%20OpenCASCADE-6f42c1)](https://build123d.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Video tutorials](https://img.shields.io/badge/YouTube-video%20tutorials-red?logo=youtube&logoColor=white)](https://www.youtube.com/@sanjeevprabhakar3837/videos)

[Download](#download) · [First part](#your-first-part) · [Video tutorials](#video-tutorials) · [Features](#features) · [Function guide (PDF)](brep_function_reference_guide.pdf) · [SanPyCAD](https://github.com/sprabhakar2006/SanPyCAD)

<a href="https://www.youtube.com/watch?v=PIlZxFOpFlg">
  <img src="https://i.ytimg.com/vi/PIlZxFOpFlg/maxresdefault.jpg" width="820" alt="SanPyCAD Brep: a filleted 3-way pipe flange next to the script that built it">
</a>

<sub>Click the screenshot to watch this 3-way flange get modeled and filleted.</sub>

</div>

---

SanPyCAD Brep is the precision sibling of [SanPyCAD](https://github.com/sprabhakar2006/SanPyCAD). Every shape you script is a **boundary-representation (B-rep) solid** with exact analytic and NURBS surfaces — the same kind of geometry FreeCAD, SolidWorks and Fusion work with. That means:

- **Fillet or chamfer the edges you pick.** Click them in the 3D view and the app writes the code.
- **Exact booleans, volumes and areas**, computed by the OpenCASCADE kernel rather than estimated from triangles.
- **True STEP files** that open in any CAD program as real faces and edges, ready for further design or machining.
- **Engineering drawings** with genuine hidden-line removal and dimensions you can click to place.

It's built on [build123d](https://build123d.readthedocs.io/), a Python CAD library on top of OpenCASCADE Technology (OCCT). The 3D view draws a light tessellation for display, but the model itself stays exact throughout.

## Download

| Platform | Download | Open it |
|---|---|---|
| macOS (Apple Silicon) | [**SanPyCAD-Brep-mac-arm64.zip**](https://github.com/sprabhakar2006/sanpycad-brep/releases/latest/download/SanPyCAD-Brep-mac-arm64.zip) | unzip, double-click `SanPyCAD Brep.app` |
| Windows 10/11 (x64) | [**SanPyCAD-Brep-win-x64.zip**](https://github.com/sprabhakar2006/sanpycad-brep/releases/latest/download/SanPyCAD-Brep-win-x64.zip) | unzip, open the folder, double-click `SanPyCAD Brep.exe` |

Each download carries its own Python, build123d and OpenCASCADE, so there's nothing else to install. All builds are on the [releases page](https://github.com/sprabhakar2006/sanpycad-brep/releases).

> **First launch.** The app isn't signed by Apple or Microsoft yet, so the first launch shows a warning.
> **macOS:** right-click `SanPyCAD Brep.app` → **Open** → **Open** (once only).
> **Windows:** on the SmartScreen banner, click **More info** → **Run anyway**.

> **Intel Mac or Linux?** There's no prebuilt bundle yet; [run it from source](#run-from-source) instead.

Install [SanPyCAD](https://github.com/sprabhakar2006/SanPyCAD) alongside it to use the **Send to SanPyCAD Brep** button described below.

## Your first part

Paste this into the editor and press **Render** (or <kbd>Ctrl</kbd>/<kbd>Cmd</kbd>+<kbd>Enter</kbd>):

```python
import os

a = cube([30, 30, 10], center=True)
b = cylinder(r=8, h=20, center=True)
part = a - b                                   # difference(a, b) works too

e1 = [part.edges()[i] for i in [0, 1, 2, 3]]   # Pick Edges/Faces writes this line for you
part = fillet(part, e1, 2)

show(part)
export_step(part, os.path.expanduser("~/part.step"))   # exact B-rep STEP in your home folder
```

You rarely type edge numbers yourself. Click **📌 Pick Edges/Faces**, click the edges you want rounded in the 3D view, and insert the list into your script; the app can write the `fillet()` line too. Open `part.step` in FreeCAD, SolidWorks or Fusion and it arrives as real faces and edges, not a mesh.

## Video tutorials

Each video is a real modeling session recorded in the app. Full list on the [YouTube channel](https://www.youtube.com/@sanjeevprabhakar3837/videos).

<table>
<tr>
<td width="33%" align="center"><a href="https://www.youtube.com/watch?v=SPKultV9bKk"><img src="https://i.ytimg.com/vi/SPKultV9bKk/mqdefault.jpg" alt="B-rep examples"></a><br><b>A wave-topped block</b><br><sub>Surface from waves → split → fillet · 8:37</sub></td>
<td width="33%" align="center"><a href="https://www.youtube.com/watch?v=DT0h065ckUQ"><img src="https://i.ytimg.com/vi/DT0h065ckUQ/mqdefault.jpg" alt="Wall hanger"></a><br><b>A wall hook</b><br><sub>Split, fillet, and fillet_by_offset · 6:24</sub></td>
<td width="33%" align="center"><a href="https://www.youtube.com/watch?v=39AwMCFxXTk"><img src="https://i.ytimg.com/vi/39AwMCFxXTk/mqdefault.jpg" alt="Complex filleting"></a><br><b>Complex fillets</b><br><sub>Where fillet() can't, then checked in FreeCAD · 7:17</sub></td>
</tr>
<tr>
<td align="center"><a href="https://www.youtube.com/watch?v=PIlZxFOpFlg"><img src="https://i.ytimg.com/vi/PIlZxFOpFlg/mqdefault.jpg" alt="3-way flange"></a><br><b>A 3-way pipe flange</b><br><sub>SanPyCAD → Brep → filleted joints · 45:41</sub></td>
<td align="center"><a href="https://www.youtube.com/watch?v=qufJeuZysAg"><img src="https://i.ytimg.com/vi/qufJeuZysAg/mqdefault.jpg" alt="Modeling a cap"></a><br><b>A cap with bosses</b><br><sub>Sketch → SanPyCAD → Brep · 25:41</sub></td>
<td align="center"><a href="https://www.youtube.com/watch?v=ct66tVg_1JU"><img src="https://i.ytimg.com/vi/ct66tVg_1JU/mqdefault.jpg" alt="Bracket model"></a><br><b>A clamp bracket</b><br><sub>Sketch → SanPyCAD → Brep · 10:10</sub></td>
</tr>
<tr>
<td align="center"><a href="https://www.youtube.com/watch?v=XH54RntgQ9c"><img src="https://i.ytimg.com/vi/XH54RntgQ9c/mqdefault.jpg" alt="Creating threads"></a><br><b>Threads</b><br><sub>STEP import, booleans, fillets · 20:27</sub></td>
<td align="center"><a href="https://www.youtube.com/watch?v=OGjPWL4bfWg"><img src="https://i.ytimg.com/vi/OGjPWL4bfWg/mqdefault.jpg" alt="The 2D sketcher"></a><br><b>The 2D sketcher</b><br><sub>Shared by both apps · 13:30</sub></td>
<td align="center"><a href="https://www.youtube.com/watch?v=F-FGGaWq4m0"><img src="https://i.ytimg.com/vi/F-FGGaWq4m0/mqdefault.jpg" alt="Installing on Windows"></a><br><b>Installing on Windows</b><br><sub>Download to first render · 7:01</sub></td>
</tr>
</table>

## Working with SanPyCAD

The tutorials usually move a part between the two apps:

```
2D Sketch  ──►  SanPyCAD (shape it: sweeps, waves, point-driven forms)
                     │
                     │  ⇨ Send to SanPyCAD Brep
                     ▼
               SanPyCAD Brep (finish it: booleans, fillets, drawings, STEP)
```

- **Send to SanPyCAD Brep** (in SanPyCAD) hands the current shapes to a running SanPyCAD Brep window, or opens one, where they arrive as real B-rep solids. The Variables panel lets you choose which variables are sent and what each becomes.
- **⇆ Exchange** (in SanPyCAD Brep) ports a whole SanPyCAD script by prefixing its ocad calls with `o.`.
- The complete ocad library is available inside SanPyCAD Brep scripts as `o`, and `swp()`, `swp_c()` and `swp_surf()` turn ocad-style point lists into B-rep solids and surfaces.
- `import_step()` brings in a part from SanPyCAD's STEP export, or from any other CAD program.

| | **[SanPyCAD](https://github.com/sprabhakar2006/SanPyCAD)** | **SanPyCAD Brep** (this repo) |
|---|---|---|
| Geometry | triangle mesh, built from point lists | exact B-rep (analytic and NURBS surfaces) |
| Engine | ocad library + manifold3d | build123d on OpenCASCADE |
| Strong at | freeform and organic shapes, sweeps, wraps, waves | mechanical parts, fillets and chamfers on picked edges, CAD-ready STEP |
| Script style | Python or OpenSCAD-style | Python |

## Features

### Nearly 200 B-rep functions
Every function is documented in the [function guide (PDF)](brep_function_reference_guide.pdf) and in the app's **📖 Reference** browser. They cover:

| Area | Examples |
|---|---|
| Solids and profiles | `cube`, `cylinder`, `sphere`, `circle`, `polygon`, `turtle2d`, `cr2dt` (rounded-corner outlines), `honeycomb` |
| Curves | `arc_3p`, `tangent_arc`, `bezier`, `bspline_open`, `interp_spline`, `helix`, `sinewave` |
| Building solids | `linear_extrude`, `rotate_extrude`, `prism`, `sweep_sec2path`, `loft`, `p_line3d`, `solid_line_vector` |
| Booleans | `union`, `difference`, `intersection`, `hull`, `split`, and the `+`, `-`, `&` operators |
| Fillets and chamfers | `fillet`, `chamfer`, `max_fillet_radius`, `fillet_by_offset`, `loft_fillet`, `show_edges` |
| Offsets and shells | `offset`, `offset_3d`, `offset_shell`, `offset_face` |
| Planes and surfaces | `plane`, `plane_from_equation`, `mirror_surface`, `project_curve_on_face`, `shell_from_faces` |
| Measurement | `volume`, `area`, `bb`, `projected_area` |
| Files and drawings | `export_step`, `export_brep`, `import_step`, `import_brep`, `export_drawing_svg` |

### Fillets that work on real models
- **Pick Edges/Faces:** hover over the model to see each edge's or face's real index, click to collect them, and insert the list into your script ready for `fillet()`, `chamfer()` or `offset()`.
- `max_fillet_radius(shape, edges)` finds the largest radius a set of edges will accept, and `show_edges(edges)` draws a selection so you can confirm it before filleting.
- When OpenCASCADE can't fillet a tricky junction, `fillet_by_offset()` and `loft_fillet()` build the blend another way ([see it used](https://www.youtube.com/watch?v=DT0h065ckUQ)).

### Engineering drawings
The **Drawing** tab lays out FRONT, TOP, RIGHT and ISO views computed with true hidden-line removal on the B-rep, with hidden edges dashed and a title block. Click to add real dimensions (linear, radius/⌀, angle, centre distance), capture any orbited angle with **Add View**, add section views along X, Y or Z, then download as SVG or PDF. `export_drawing_svg()` does the same from a script.

### A 2D sketcher, on its own or on a face
The same sketcher as SanPyCAD: lines, arcs, tangent arcs, rounded and chamfered corners, offset, trim, mirror, arrays, B-splines, text to outlines, DXF/SVG import and image tracing. **Send to SanPyCAD Brep** places the profile in your script as a variable. **Sketch on Face** opens the sketcher aligned to any face you click on the model.

### A notebook-style kernel you can always interrupt
- Variables persist between renders, Jupyter-style, so slow steps only run once.
- Scripts run in a separate kernel process. **Stop / Restart Kernel** interrupts a render that's stuck and starts clean.
- The **Variables** panel previews any variable as a line or points in the 3D view.
- <kbd>Tab</kbd> completion, <kbd>Shift</kbd>+<kbd>Tab</kbd> docs, Find and Replace, adjustable editor font size, and a bare expression on its own line prints its value.

### Measure and dimension in 3D
Measure distances and angles between vertices and edges, or use **Dimension** to place permanent labelled dimensions on vertices, hole and shaft centres, edges and faces. **Display…** adjusts how finely curved surfaces are drawn on screen; it never affects export or the model itself.

### Files
- **Toolbar export:** STL, OBJ, DXF (tessellated), and SVG (a full engineering drawing).
- **From a script:** `export_step()` / `export_brep()` write exact B-rep (wrap several shapes in `group(a, b, ...)` to write them as one assembly file); `import_step()` / `import_brep()` read a file back in as a real solid you can cut, split and fillet.
- **Save:** scripts are plain `.py` text.

## Examples

The **Examples…** dropdown includes `drill.py` (helical flutes cut with `p_line3d`), `tap.py` (a thread profile swept along a helix and cut from a cylinder) and `hollow_cylinder_with_star.py` (a star cut-out through a tube, with filleted edges). Each one's sketched profiles are stored next to it in a `.sketch.json` file. The [videos](#video-tutorials) walk through larger parts step by step.

## Known limitations

- No toolbar buttons for STEP/BREP import or export yet; use `export_step()`, `export_brep()`, `import_step()` and `import_brep()` in your script.
- No mesh (STL) import. A triangle mesh can't be turned back into exact surfaces.
- `linear_extrude()` doesn't support `twist` or `scale`; use `loft()` or `sweep_sec2path()` for those shapes.
- `hull()` is exact for flat-faced shapes and approximate for curved ones.
- Section views in drawings aren't cross-hatched yet, and drawing views and dimensions aren't saved with the script.
- Builds aren't signed or notarized yet, hence the first-launch warnings.

## Run from source

For development, or on an Intel Mac or Linux:

```bash
git clone https://github.com/sprabhakar2006/sanpycad-brep.git
cd sanpycad-brep
pip install numpy build123d ipython pywebview
pip install scipy sympy scikit-image manifold3d     # only needed for the ocad bridge (o.*)
python app.py
```

Requires Python 3.10 or newer. Without `pywebview` the app opens in your default browser instead of its own window.

<details>
<summary><b>Building the downloadable bundle</b></summary>

```bash
pip install build123d pyinstaller
python packaging/build_bundle.py
```

This produces `dist/SanPyCAD Brep.app` (macOS) or `dist/SanPyCAD Brep/` (Windows, Linux), plus a zip, with Python, build123d, OpenCASCADE and every other dependency inside. OpenCASCADE is a large native library, so the build takes noticeably longer than SanPyCAD's.

PyInstaller can't cross-compile, so build each platform on that platform. Pushing a `v*` tag runs `.github/workflows/build-installers.yml` on GitHub's macOS and Windows runners and attaches both zips to the release.

The packaged app writes its log, `SanPyCAD-Brep.log`, to `~/Library/Application Support/SanPyCAD Brep` on macOS and `%APPDATA%\SanPyCAD Brep` on Windows. It's the first place to look if something misbehaves.

</details>

## Documentation

- **[Function guide (PDF)](brep_function_reference_guide.pdf)** — every B-rep function with its signature and notes, grouped by category
- **📖 Reference** button in the app — searchable docs for both the B-rep functions and the ocad bridge
- **[YouTube channel](https://www.youtube.com/@sanjeevprabhakar3837/videos)** — step-by-step modeling sessions

## Credits

Created by **Sanjeev Prabhakar**, who also wrote the ocad geometry library behind [SanPyCAD](https://github.com/sprabhakar2006/SanPyCAD).

Built on [build123d](https://build123d.readthedocs.io/) and [OpenCASCADE Technology](https://dev.opencascade.org/), with [CodeMirror](https://codemirror.net/) and [Three.js](https://threejs.org/).

## License

[MIT](LICENSE)
