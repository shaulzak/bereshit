# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`bereshit` is a pure-Python 3D game/physics engine (Unity-inspired API) rendered with moderngl. This repository root **is** the `bereshit` package itself: modules use absolute imports like `from bereshit import Vector3` / `from bereshit.Collider import Collider`, so the **parent directory** (`C:\Users\shaul\bereshit`) must be on `sys.path`.

## Commands

```bash
pip install -r requirements.txt          # addons/PPO additionally needs torch (not in requirements.txt)
```

There is no test runner (no pytest/unittest, no asserts). Files under `tests/` are standalone scripts — demo scenes (e.g. `tests/Stacking.py`, `tests/Joints/FixedJoint/drop.py`) that open a render window via `Core.run(...)`, or micro-benchmarks (e.g. `tests/Vector3/dot.py`). Run one from the parent directory so `bereshit` is importable:

```bash
cd .. && PYTHONPATH=. python bereshit/tests/Stacking.py
```

For headless/time-limited runs pass `Core.run(scene, Render=False, MaxTime=<seconds>)`.

Packaging with Nuitka is documented in `nuitka.txt` (shaders dir must be included as data).

## Architecture

**Entry point — `Core.run(...)`**
Builds a `World` from the list of root `Object`s, runs the simulation loop in an asyncio loop on a daemon thread, and runs the renderer (`render.run_renderer`) on the main thread. The two share the `World` object and `Exit`/`Initialize` flag lists. The loop is paced so simulated time tracks wall time × `speed`.

**Object / component model (`Object.py`)**
- `Object` holds transform (`position`, `rotation` Euler, `quaternion`, `size`), `children`, and a `components` dict keyed by class name (duplicates get `_0`, `_1` suffixes; a component's `attach(parent)` may return a custom key).
- Every `Object` auto-gets `Material` and `MeshRander(shape="box")` components.
- `add_component(*components)` returns `self` (chainable) and sets `component.parent` and `component.Active = True`.
- `obj.Rigidbody`, `obj.Camera`, etc. resolve via `__getattr__` → `components[name]`. `get_component` accepts a string name or a class (isinstance match — e.g. `get_component(Collider)` finds a `BoxCollider`).
- Components are plain classes (no required base class). Lifecycle hooks discovered by `hasattr`: `start()` (on add), `Start()` (once, after renderer init), `Update(dt)` (every `scriptRefreshRate` steps, default ~30 Hz), `PhysicsUpdate(dt)` (every tick), plus collider callbacks `OnCollisionEnter/Stay/Exit`, `OnTriggerEnter/Stay/Exit`.

**Physics step (`World.update`)**
1. Script `Update` / `PhysicsUpdate` calls.
2. Only objects with **both** a `Rigidbody` and a `Collider` participate in physics (`get_all_children_physics`).
3. Gravity → broad phase `Collider.sweep_and_prune` → narrow phase `Collider.check_collision` (SAT in `BoxCollider`) → friction + impulse via `Rigidbody` static solvers → `Joint.solve` for `FixedJoint`/`HingeJoint`.
4. Collisions and joints are re-solved `physics_epochs - 1` more times (sequential impulses), then `Rigidbody.integrate(dt)` for non-kinematic bodies; non-physics children follow their physics parent.
- `World.set_static_variables` pushes global state into class attributes (`Rigidbody.Scale`, `Collider.Scale`, `Physics.World`) — `Physics.Raycast`/`RaycastAll` rely on `Physics.World`.

**Rendering (`render.py`, `shaders/`)**
Shading modes `wire`, `solid`, `material preview` are selected on the `Camera` component (`Camera(shading=...)`). Shader files use `.vert` extension for both vertex and fragment stages.

**Addons (`addons/`)**
- `addons/essentials`: reusable components (`CamController`, `FPS_cam`, `PlayerController`, `Shoot`, `debug`) — good examples of how components access `self.parent`, `Physics.RaycastAll`, and the renderer via `self.parent.Camera.render`.
- `addons/PPO`: multi-agent PPO (torch) where `Agent` is a component and many agents share one `Trainer`; examples in `addons/PPO/examples`.

**C++ port (`bereshitCore/`)**
An in-progress C++20 reimplementation of the core (GameObject/Transform/Component, Rigidbody, colliders, joints, World) exposed to Python via pybind11 (`bindings.cpp`). Build per `build.txt`:
```bash
cmake -S . -B build -Dpybind11_DIR="<site-packages>/pybind11/share/cmake/pybind11"
cmake --build build --config Release
```
`bereshitCore/__init__.py` loads the module from `build/Release`. `cbuild.txt` is an alternate CMakeLists that builds `main.cpp` + `test/` as a standalone executable for C++-side tests. The Python engine does not currently depend on it.

## Notes

- `*_old.py`, `temp`, `sadf.py`/`sadf.exe` are scratch/legacy files, not part of the engine.
- `MeshRander` is the (misspelled) mesh renderer class name — keep the spelling; it's used as a component key.
