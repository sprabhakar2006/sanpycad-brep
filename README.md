# SanPyCAD Brep

The **B-rep-first copy of SanPyCAD**: unlike the mesh-based SanPyCAD apps
(everything there ends up as triangle soup), every shape here is a real
boundary-representation (B-rep) solid -- exact analytic/NURBS surfaces,
exact booleans, real fillets -- built on
[build123d](https://build123d.readthedocs.io/), a Python CAD library on
top of OpenCASCADE Technology (OCCT), the same open-source B-rep kernel
FreeCAD itself uses. There is no mesh/triangle-soup geometry engine
anywhere in this app: no OpenSCAD-text-DSL mode, no mesh CSG, no mesh
import. Its window title, launcher filenames, and log files are all
labeled "SanPyCAD Brep" specifically so it's never confused with the
mesh-based SanPyCAD apps if you have more than one installed side by
side.

The 3D viewer still renders triangles -- that's all WebGL can ever draw
-- but they're a disposable tessellation generated just for display; the
actual model stays exact B-rep the whole time.

It opens as its own application window (via `pywebview`), not "a web app
you have to navigate to" -- under the hood it runs a small local backend
(plain Python, no Flask) and a 3D viewer, but you just double-click a
shortcut (or run one command) and a window opens.

## Install

Grab the build for your machine from the
[latest release](../../releases/latest), unzip it, and open it. Each
download carries its own Python and every library it needs, including
`build123d` and its OCP/OpenCASCADE engine -- nothing to `pip install`,
no Python required on the machine that runs it.

| Platform | Download | Open it |
|---|---|---|
| macOS (Apple Silicon) | `SanPyCAD-Brep-mac-arm64.zip` | double-click `SanPyCAD Brep.app` |
| Windows 10/11 (x64) | `SanPyCAD-Brep-win-x64.zip` | open the folder, double-click `SanPyCAD Brep.exe` |

**First launch on macOS** shows "SanPyCAD Brep cannot be opened because
the developer cannot be verified" -- the app is not notarized by Apple.
Right-click the app → **Open** → **Open**, once. Every launch after
that is a normal double-click.

**First launch on Windows** may show a SmartScreen banner for the same
reason: **More info** → **Run anyway**.

Prefer to build and run it from source yourself? See
[Building the bundle](#building-the-bundle) below, or just run
`python3 app.py` after `pip install numpy build123d pywebview`.

## Run it

Either way, a window titled "SanPyCAD Brep" opens: a code editor on the
left, a live 3D viewport on the right. Write a script, press **Render**
(or Ctrl/Cmd+Enter), and it draws the model.

**Internet access:** SanPyCAD Brep's code editor and 3D viewer are
built on CodeMirror and Three.js. The very first time you run the app,
it quietly downloads its own copy of those (into `frontend/vendor/`) in
the background so every launch after that needs zero internet access --
the app is fully usable immediately either way (it falls back to
loading those from a CDN live if the local copies aren't there yet).
If you're setting this up on a machine with no internet access at all,
run it once on a machine that does have internet first, then copy the
whole project folder (including the now-populated `frontend/vendor/`)
over. (This is separate from `build123d` itself, which does need to be
`pip install`ed with internet access at least once, same as any other
Python package.)

Either way, a window titled "SanPyCAD Brep" opens: a code editor on the
left, a live 3D viewport on the right. Write a script, press **Render**
(or Ctrl/Cmd+Enter), and it draws the model. The **Export** dropdown
saves the current scene as STL, OBJ, SVG, or DXF (labeled honestly
rather than as "DWG" -- true .dwg is AutoCAD's proprietary binary
format and needs a paid SDK to write; DXF is the open interchange
format AutoCAD and every other major CAD tool reads natively). STL/OBJ/
DXF are *tessellated* exports -- for exact B-rep STEP/BREP export, call
`export_step()`/`export_brep()` directly in your script (see below);
there's no toolbar button for that yet.

The reverse direction works too: `import_step("part.step")`/
`import_brep("part.brep")` read a file back in as a real B-rep Shape
(build123d's own importers) -- a part made elsewhere, or one this app
itself wrote out earlier -- and hand back something every other
function here treats like any other shape: `union()`/`difference()` it
against new geometry, `fillet()`/`chamfer()` its edges, or `split()` it
with a `plane()` for a cutaway/cross-section view of what's inside
(see `examples/21_import_and_section_step_library.py` for a working
example that imports several .step files and shows each one with a
quarter-section cut away).

No toolbar button for import either yet -- it's script-only for now,
same as STEP/BREP export.

SVG is different from the other three: it's a real multi-view
**engineering drawing**, not a tessellated mesh dump -- FRONT/TOP/RIGHT/
ISO views of the shown shape(s), computed with genuine hidden-line-
removal on the actual B-rep geometry (OCCT's HLRBRep_Algo, via
build123d's `Shape.project_to_viewport()`), laid out on one bordered
sheet with a title block; edges hidden behind the surface from a given
view draw dashed, visible edges solid, the standard drafting
convention. Both need the shown shape(s) to be genuine B-rep (brep.py's
own cube()/sphere()/etc, not the raw ocad mesh-bridge escape
hatch) -- there's no HLR to compute otherwise. Scriptable directly too,
if you want the file written without going through the toolbar at all:
`export_drawing_svg(shape, "part_drawing.svg", part_name="Bracket")`
(see `technical_drawing_views()`'s own docstring in `brep.py` for the
lower-level version that returns raw view data instead of a finished
SVG, and for what's honestly still unverified about this against a
real build123d install -- HLR-based drawings are new here).

The toolbar's own **Drawing** button opens something more than a flat
file, though: an interactive 2D Drawing tab (swapping out the 3D
viewport, same window) showing those same 4 views live, where you can
click to add real, measured dimensions before downloading -- pick a
tool (Linear, Radius/&#8960;, Angle, or Center Distance), then click
points/circles/edges on the drawing:
- **Linear** -- click 2 points (snaps to the nearest edge endpoint) for
  a straight-line distance dimension.
- **Radius/&#8960;** -- click a circular edge/hole for a radius +
  diameter callout.
- **Angle** -- click 2 straight edges for the angle between them.
- **Center Distance** -- click 2 circular edges/holes for the distance
  between their centers (e.g. bolt-hole spacing).

Every dimension is computed in the part's own real-world units (not
screen pixels) by fitting a circle to a clicked hole's own sampled
points, or measuring directly between real coordinates -- accurate
regardless of how zoomed in the drawing looks. Click an existing
dimension (with the Select tool) to highlight it, then **Delete** (or
press Delete/Backspace) to remove it; **Clear All** removes every
dimension on the sheet. **Download SVG** saves the sheet exactly as
shown, dimensions included -- there's no separate "bake in the
dimensions" step, since they're already real SVG elements in what gets
downloaded.

The drawing sheet is zoomable and pannable -- scroll to zoom in on a
small feature so you can click its exact point/edge/circle, or use the
&minus;/+/Fit buttons in the bottom-right corner; middle-mouse-drag (or
hold Space and left-drag) to pan around. Any dimension you've already
placed can be repositioned with the Select tool by just dragging it --
the witness/extension lines stay anchored to the real geometry point
they measure, only the offset/label position moves, same as dragging a
dimension in a real drafting tool.

The **Views** button in the Drawing tab's own toolbar adds more views
to the sheet beyond the fixed FRONT/TOP/RIGHT/ISO 4:
- **Add View** (in the main toolbar, above the 3D viewport) captures
  whatever orientation you've orbited the 3D view to as a new named
  view on the sheet -- rotate the model to whatever angle actually
  shows what you need, click Add View, then open (or return to) the
  Drawing tab to see it added alongside the standard 4.
- **Section views** (inside the Views panel) cut the part at a plane
  you choose -- pick an axis (X/Y/Z), an offset along it, and which
  side to keep -- and add a new view looking straight at the freshly
  exposed cut face, instead of always the same 4 uncut outside views.
  A cutting plane that misses the part entirely (or a multi-body
  assembly where it misses one piece) reports that in the sheet
  itself rather than failing silently. Section views aren't cross-
  hatched yet (a real drafting section fills the cut material with
  diagonal hatch lines) -- this shows the cut outline only, no fill.

Both custom and section views live only in the Drawing tab's own
session state, same as the dimensions -- they aren't saved with your
`.py` script, and adding/removing one rebuilds the whole sheet (which
clears any dimensions already placed -- you'll be asked to confirm
first if you have any).

Note that Export is about the *rendered geometry* (STL/OBJ/etc.), not
the script that produced it. To save your actual design so you can
close SanPyCAD Brep and reopen it later, use **Save** (writes to
whatever file you last saved to/opened from -- a native Save dialog the
very first time), **Save As** (always prompts for a new file), or
**Open** (loads a previously saved `.py` script back into the editor).
Ctrl/Cmd+S is the same as clicking Save. This writes plain `.py` text
files -- ordinary source code, openable in any text editor, not a
proprietary format.

The **Examples** dropdown in the toolbar has a few starter scripts (see
`examples/` below). The **Orthographic** checkbox switches the 3D
viewport between perspective and orthographic (no vanishing-point
distortion) projection, keeping your current view. Rotate/zoom/pan stop
exactly where you release them -- no drift/momentum to fight when
lining up a precise view. The **Axes** checkbox toggles a small colored
X/Y/Z cross through the origin plus a small orientation indicator in
the viewport's lower-left corner. The **Edges** checkbox outlines every
triangle edge of the *display tessellation* -- handy for a rough sense
of the surface, but this is the viewer's triangle mesh, not the B-rep
model's real edges/faces (see `show_edges()` below for that). The
**View** dropdown snaps the camera to a standard angle -- Top, Bottom,
Front, Back, Left, Right, or Diagonal -- keeping your current zoom/pan.
**Fit** re-centers and zooms the camera to frame the current model. The
editor pane and the 3D viewport are resizable -- drag the thin bar
between them (and the one between the editor and the console panel).
The **Measure** dropdown (Off/Vertices/Edges) lets you click on the
model to measure it: in **Vertices** mode, clicking snaps to the
nearest corner of whatever face you click, and once two are picked
shows the distance between them; in **Edges** mode, clicking selects a
whole edge, and once two are picked shows each edge's length, the angle
between them, and the shortest distance between them. In the editor,
brackets/quotes auto-close as you type, and (JupyterLab-style) **Tab**
brings up autocomplete when you're mid-identifier (every function
brep.py exposes, plus whatever identifiers you've already typed) and
otherwise indents as normal -- it matches anywhere in the name, not
just the start. **Shift+Tab** on a function name shows its signature
and docstring in a popup. The toolbar's **📖 Reference** button opens a
searchable browser over that same documentation. The **Wrap** checkbox
toggles line-wrapping in the editor. Next to it, the **A− / 13.5px /
A+** control changes the editor's font size (Jupyter/VS-Code-style) --
click the buttons, or use Ctrl/Cmd+= to grow it, Ctrl/Cmd+- to shrink
it, and Ctrl/Cmd+0 (or double-click the size readout) to reset back to
default; the size is remembered between launches.

## Writing a script

Plain Python, calling brep.py's functions directly:

```python
a = cube([20, 20, 10], center=True)
b = cylinder(r=6, h=20, center=True)
show(difference(a, b))
```

`cube()`/`box()`/`cylinder()`/`sphere()`/`circle()`/`square()`/
`polygon()`/`translate()`/`rotate()`/`rot()`/`mirror()`/`scale()`/
`linear_extrude()`/`rotate_extrude()`/`sweep_sec2path()`/`offset()`/
`union()`/`difference()`/`intersection()`/`hull()`/`fillet()`/
`chamfer()` all build/combine real build123d B-rep solids -- see
`examples/` for one focused script per group of these. `turtle2d()`/
`turtle3d()` turn a list of relative offsets into absolute points
(handy for building a `polygon()` outline or a `sweep_sec2path()` path
by hand); `cr2dt()`/`cr3dt()` do the same but round each corner with a
fillet arc of a per-point radius, for a rounded-rectangle-style
profile or a pre-rounded sweep path. `offset(shape, amount)` grows
(positive) or shrinks (negative) a 2D profile's outline, or shells a
3D solid into a hollow shape (optionally leaving some faces open via
`openings=`) -- a thin wrapper around build123d's own native
`offset()`, the same "lean on OCCT rather than hand-roll it"
reasoning as `sweep_sec2path()`. `volume(shape)`
returns the shape's exact enclosed volume (computed by OCCT, not a
discretized estimate). `to_mesh(shape)` tessellates a shape into `[V,
F]` (the same convention used throughout this project's mesh apps, if
you ever need that form).

On top of that, brep.py has a growing **core point-list/vector-math
toolkit** ported from ocad.py (the mesh-based SanPyCAD apps'
underlying library, which has ~580 functions of this kind in total --
this first batch covers ~36 of the most broadly useful ones, reimplemented
from scratch as plain Python, not ported line-for-line): arcs and circles
through 2 or 3 points (`arc_2p`/`cir_2p`/`arc_3p`/`cir_3p`/`cp_3p`/
`arc_2p_3d`), line/vector math (`l_len`/`l_lenv`/`mid_point`/
`line_as_vector`/`line_as_unit_vector`/`seg`/`flip`), angles and
intersections (`ang3points`/`ang_2lineccw`/`ang_2linecw`/`i_p2d`/
`distanceOfPointFromLine`/`perpendicularProjectionOfPointOnLine`),
mirroring and rotating point lists (`mirror_point`/`mirror_line`/
`rot2d`), a circle-to-circle tangent line (`tcct`), a single-corner
fillet (`fillet3points`), cleanup/sorting (`remove_extra_points`/
`min_d_points`/`sort_points`), a 2D convex hull (`convex_hull`),
plane/normal math (`normal_vector`/`equation_of_plane`), bounding
boxes/centroids (`bb`/`bb2d`/`cog`), and Bezier/B-spline curves
(`bezier`/`bspline_open`/`bspline_closed`) -- see
`examples/10_core_toolkit.py` and each function's own docstring
(Shift+Tab) for details. A handful of related functions (path/polygon
offset, line-circle fillets, the more exotic derived-curve smoothers)
need more careful follow-up work and aren't ported yet.

`points(pts, d=0.5, shape="cube")` drops a small marker at every point
in a bare 2D/3D point list -- for checking where a curve's control
points or a hand-built path's points actually land before/after
extruding or sweeping it -- and `p_line3d(path, d=1, rec=0, closed=0)`
turns a bare 3D point list straight into a tube/rope solid (capsule
segments fused end to end, real B-rep), no sweep_sec2path()-style 2D-
section-and-path setup needed. Both are ocad.py's own points()/
p_line3d() modules, ported -- see `examples/12_points_pline3d.py`.

A third batch rounds out the core-geometry side of ocad.py:
`plane(normal, size, intercept)` (a flat reference Face at any
orientation), `sinewave()`/`cosinewave()` (2D point lists tracing a
sine/cosine curve), `loft(*sections)` (a solid blended smoothly
through a stack of positioned 2D cross-sections -- build123d's own
native loft, real B-rep, not a stack of thin slices), `helix(radius,
pitch, turns)` (an exact helical curve -- feed it to
`sweep_sec2path()` for a coil spring or screw thread),
`interp_spline(points, closed)` (a curve that passes EXACTLY through
every given point, unlike `bezier()`/`bspline_open()`), `s_int1(points,
closed)` (every point where a closed point-list loop crosses itself),
`tangent_arc(a, b, radius, side)` (an arc tangent to two
circles/lines -- covers ocad.py's whole two_cir_tarc()/
fillet_line_circle() family in one call via build123d's native
ConstrainedArcs), and `project_curve_on_face(curve, target,
direction)` (exact B-rep projection of a curve onto a surface, not a
nearest-point search over a triangulated approximation). See
`examples/13_planes_and_waves.py`, `14_loft_and_helix.py`, and
`15_intersections_and_tangent_arcs.py`.

Not every ocad.py function in this family made the cut.
`concave_hull()` was attempted and dropped -- a naive point-list
algorithm turned out to be genuinely unreliable (verified wrong on a
simple test case), and getting it right needs more careful work than
was worth doing on faith. `wrap_around()`/wrap-a-profile-around-an-
arbitrary-path and `prism()`/`swp_prism_h()`-style stacked-offset-
section building were also left out, but not because they're missing
capability -- their whole job is already covered better by
`sweep_sec2path()` and `loft()`, both real B-rep the whole way, so
every real-world example below that would have used them uses one of
those instead. `o_solid()`/`surround()` are still genuinely unported.
`honeycomb(r, n1, n2)` (a hex-grid of cell outlines) and
`point_in_polygon(point, poly)` (ray-casting containment test) *were*
added, once the real-world examples below turned out to need them --
see `examples/17_honeycomb.py`.

The real-world part examples (`16` through `37` below) cover bolts,
flanges, a lamp, a ball bearing, a coil spring, knots, a drill bit, a
cam, a bottle, a handling trolley, and more -- ported from
ocad.py's real-world project files. Two things were left out on
purpose: `car_seat`, and the marching-cubes/hand-rolled-fillet cluster
(13 files that all reduce to "just call the real `fillet()`/
`chamfer()` here instead" -- nothing new to build). `car_seat` WAS
ported once (`23_car_seat_mesh_style.py`), but was later removed:
organic freeform surfacing built up from raw point-list interpolation
(`mixed_wire()`/`cap_wire()`/`loft()`-stitched patches, no shared
topology by construction) fights OCCT's exact-topology requirements
too much to be worth keeping as a bundled example -- the mesh-based
SanPyCAD app's real-OpenSCAD/CGAL boolean pipeline is the better fit
for this specific kind of shape. See that app's own car_seat example
instead. Ask if you want the fillet cluster pursued.

Call **`show(x)`** on whatever shape(s) you want drawn in the app (if a
script has exactly one shape-like variable and never calls `show()`,
that one is shown automatically). `color(x, "red", alpha=0.5)` tags a
shape with a color for display -- apply it *last*, right before
`show()`, since (like `show()`) it tessellates the shape for the
viewer, so anything returned from `color()` can no longer be fed to
`volume()`/`fillet()`/`chamfer()`/`export_step()`/further booleans.
`print()` and `echo()` both show up in the console panel.

To measure a shape: **`volume(x)`** (exact enclosed volume) and
**`area(x)`** (total surface area, every face summed) are both plain
build123d properties exposed as functions. **`bb(x)`** gives its
bounding-box size `[w, h, d]` -- works on a real B-rep shape now, not
just a point list (use `x.bounding_box()` directly, build123d's own
method, if you need `.min`/`.max`/`.center()` too, not just the
overall size). **`projected_area(x, direction)`** is different from
`area()` -- it's the "shadow" area `x` would cast looking straight
along `direction` (e.g. `[0, 0, -1]` from above), built on the same
hidden-line-removal the engineering-drawing feature uses, correctly
netting out any holes visible from that direction (a flange's bolt
holes, a pipe viewed down its axis) rather than just measuring the
outer boundary.

In the editor, any bare expression on its own line gets its value
echoed to the console panel, the same way a Jupyter cell auto-displays
whatever you type -- so `len(a)`, `volume(a)`, `type(a)`, or any other
one-off check can just be typed on its own line without wrapping it in
`print()`/`echo()`. (`None` and shape values are quietly skipped so
this doesn't spam the console with the `show(x)` calls you already
have.)

**Variables persist between runs, Jupyter-style.** The app keeps a
kernel-like namespace alive across Render clicks: whatever your script
assigns is still there the next time you press Render, even if you've
since commented out the line that computed it -- compute something
heavy once, then comment that line out and keep iterating on everything
downstream of it without paying for the heavy part again. The toolbar
shows a **N vars in memory** indicator (hover it to see which names),
and a **Reset Memory** button next to it clears everything -- the
equivalent of restarting a Jupyter kernel.

This app runs your script with a plain Python `exec()` -- no sandboxing
beyond that, same trust level as running it in your own notebook.

### Manually selecting edges for fillet()/chamfer()

`shape.edges()` returns every edge of `shape` as a real build123d
`ShapeList`, with the library's own selector API available directly --
`.filter_by(Axis.Z)`, `.sort_by(Axis.Z)`, `.filter_by(GeomType.CIRCLE)`,
plain indexing/slicing, etc (`from build123d import Axis` at the top of
your script). `fillet(shape, edges, radius)`/`chamfer(shape, edges,
length)` take that selection straight in. Since the viewer's own vertex
picker only sees the *display tessellation*, not the real B-rep
topology, there's no click-an-edge-in-3D tool -- use `show_edges(edges)`
instead: it turns a selection into a visible "beaded string" of small
spheres following each edge's curve, so you can `show()` it (in a
different color/alpha) to confirm a selector picked the right edges
*before* committing to a `fillet()`/`chamfer()` call. See
`examples/04_fillets_and_chamfers.py`.

## Examples

`examples/` previously bundled a full set of built-in demo/reference
scripts (one per capability, plus a batch of real-world ported parts).
That whole bundled set has been cleared out so this is a clean slate
for your own scripts. The two files still there
(`38_mirror_surface_demo.py`, `41_ocad_bridge_fillet.py`) are kept
because you wrote their content yourself; everything else was deleted.
Note that several docstrings/sections elsewhere in this README (and in
brep.py's own function docstrings) still cross-reference the old
`examples/NN_*.py` filenames by name -- those references are now
stale/dangling, not links to files that still exist.

## Known limitations

- `linear_extrude(twist=..., scale=...)` (a helical/tapered extrude) is
  not implemented -- build123d's own `extrude()` has no direct
  equivalent; that shape needs a loft between rotated/scaled copies of
  the profile, or a genuine helical sweep. Calling it with a non-default
  `twist`/`scale` raises a clear error rather than silently extruding
  straight.
- `hull()` is exact for shapes made only of flat faces (boxes, unions of
  boxes, etc), but only an approximation (accurate to the default
  tessellation tolerance) for anything with curved faces (`cylinder()`,
  `sphere()`, a `fillet()`ed edge) -- see its own docstring.
- `sweep_sec2path()` calls build123d's own native `sweep()` directly,
  with `transition="round"` by default -- OCCT joins corners with a
  rounded fillet-like surface, which is what makes a sharp-cornered
  `path3d` produce valid geometry (build123d's own default,
  `transition="transformed"`, is a flat mitered joint that's prone to
  self-intersecting on a genuinely sharp corner). Try
  `transition="right_corner"` or `"transformed"` if `"round"` doesn't
  look right for a given path. `path3d` can also be a filled 2D shape
  (`circle()`/`square()`/`polygon()`) -- its boundary is used
  automatically (`sweep_sec2path(circle(2), circle(15))` is a torus) --
  but only reliably for a shape with a single boundary; anything with
  holes/multiple boundaries needs its own explicit Wire/Edge instead.
  `mirror=`/`orientation=` are "try it, look at the result, adjust"
  knobs, not something computed automatically -- see the function's own
  docstring for why (and for the two earlier, now-abandoned fix
  attempts -- a hand-rolled segment-extrude-and-union approach -- that a
  real user's bug reports against a real build123d install walked this
  function through before landing here).
- No STEP/BREP export button in the toolbar yet -- call
  `export_step()`/`export_brep()` directly in your script for now (see
  `examples/05_export.py`). The Export dropdown's STL/OBJ/DXF are all
  tessellated exports; SVG is the one exception -- a real hidden-line-
  removed engineering drawing computed straight from the B-rep shape,
  not a tessellation (see above).
- No mesh/STL import -- there's no B-rep equivalent of "reconstruct
  exact analytic surfaces from an arbitrary triangle mesh," so this
  isn't a gap that can be closed the same way the mesh SanPyCAD apps'
  `import()` works.

## Building the bundle

The `SanPyCAD Brep.app` / `SanPyCAD Brep.vbs` launchers above still
need Python and `build123d` installed on the machine that runs them --
fine for development, but not something to hand someone who just wants
to double-click an app. `packaging/build_bundle.py` produces a truly
self-contained bundle instead, with Python, build123d, OCP/OpenCASCADE
and every other dependency frozen inside it:

```bash
pip install build123d pyinstaller
python packaging/build_bundle.py
```

This produces `dist/SanPyCAD Brep.app` (macOS) or `dist/SanPyCAD Brep/`
(Windows, Linux) plus a zip of it. Because OCP/OpenCASCADE is a large
native library, this build takes noticeably longer than a typical
PyInstaller app -- that's expected.

PyInstaller cannot cross-compile, so each platform's bundle has to be
built on that platform. `.github/workflows/build-installers.yml` runs
this same script on GitHub's macOS and Windows runners: push a `v*` tag
and the finished bundles are attached to a release automatically, or
start it by hand from the **Actions** tab.

Where the frozen app keeps its files:

| | macOS | Windows |
|---|---|---|
| Log | `~/Library/Application Support/SanPyCAD Brep` | `%APPDATA%\SanPyCAD Brep` |

`SanPyCAD-Brep.log` in that folder holds the console output of the
last session -- the first place to look if something misbehaves. (The
frozen build has no `sanpycad_config.json`/`imports/` the way the
sibling mesh-based SanPyCAD app does -- this app has no OpenSCAD path
to remember and no bare-filename `import()`.)

## Project layout

```
SanPyCAD Brep.app/         <- double-click this to launch (macOS)
Fix Mac Security Warning.command  <- run once after unzipping, before first launch (macOS)
SanPyCAD Brep.vbs          <- double-click this to launch (Windows)
run_sanpycad_brep.bat      <- backup Windows launcher (visible console; use if .vbs is blocked)
app.py                     <- what the launchers above run; also runnable directly
backend/
  brep.py                  <- the B-rep layer: primitives/transforms/booleans/fillets/export, on build123d
  mesh_types.py             <- the display-only Mesh container (tessellation + color, for the viewer)
  python_eval.py            <- runs scripts (exec + show/color/echo helpers), see its module docstring
  vendor_assets.py          <- downloads CodeMirror/Three.js into frontend/vendor/ once, for offline use
  server.py                 <- stdlib HTTP server (routes: /, /status, /render, /export/stl, /examples)
frontend/
  index.html                <- code editor (CodeMirror) + 3D viewer (Three.js), single file
  vendor/                   <- local copies of CodeMirror/Three.js (downloaded on first run; see above)
examples/
  *.py                      <- one focused example per capability, see above
```

If you'd rather run it as a plain local web page (e.g. to open it in a
regular browser tab yourself, or host it for someone else on your
network), you can skip `app.py` and run `python3 backend/server.py`
directly, then open the printed `http://127.0.0.1:8743/` URL.
