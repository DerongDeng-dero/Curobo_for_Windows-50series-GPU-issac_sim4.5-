# Windows + NVIDIA RTX 50-Series + Isaac Sim 4.5+ cuRobo Documentation Reading Order and Overview

## 1. What this document is for

This repository now contains a full documentation set, not just a single installation note.

The current document set is primarily organized for this target combination:

- Windows
- NVIDIA GeForce RTX 50-series GPUs
- Isaac Sim 4.5+
- the `curobo_for_windows` workflow in this repository

The current documents cover:

- installation and repair
- the installable delivery layout
- in-app GUI usage
- custom scene building
- pick/place state machines
- loading a user-provided USD scene into that state machine
- the full repair log and maintenance notes

When the document count grows, two problems appear immediately:

1. the reading order is unclear
2. the purpose of each document is unclear

This file is the main navigation page for the user-facing documentation in this Windows + Isaac Sim + cuRobo workflow.

---

## 2. Recommended reading order

For a fresh setup, read the documents in this order:

(1) [`README.md`](../../README.md)

(2) [`WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.en.md`](./WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.en.md)

(3) [`INSTALLABLE_VERSION_MANUAL.en.md`](./INSTALLABLE_VERSION_MANUAL.en.md)

(4) [`ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.en.md`](./ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.en.md)

(5) [`ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.en.md`](./ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.en.md)

(6) [`ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.en.md`](./ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.en.md)

(7) [`ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md`](./ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md)

(8) [`curobo_isaacsim_windows_full_fix_guide.en.md`](./curobo_isaacsim_windows_full_fix_guide.en.md)

If installation is already complete and only the GUI workflow is needed, start from `(4)`.

For an existing user-provided USD scene, start from `(7)` to attach the pick/place state machine.

For maintenance or upgrade work, read `(3)` and `(8)`.

---

## 3. Recommended paths for different readers

## 3.1 Path A: complete beginner, starting from installation

Read:

- `(1) -> (2) -> (3) -> (4) -> (5) -> (6) -> (7)`

Use this path if:

- this is the first Windows + Isaac Sim + cuRobo setup in the current environment
- this is the first time cuRobo is being used inside Isaac Sim in the current environment
- the safest step-by-step route is preferred

## 3.2 Path B: already installed, only need GUI usage

Read:

- `(1) -> (4) -> (5)`

Use this path if:

- the environment is already healthy
- the goal is to start Isaac Sim Full normally and use cuRobo inside the GUI

## 3.3 Path C: already planning, now want task flow

Read:

- `(5) -> (6)`

Use this path if:

- single-goal motion generation already works
- the next goal is a pick/place state machine

## 3.4 Path D: already have a user-provided USD scene

Read:

- `(5) -> (6) -> (7)`

Use this path if:

- tables, fixtures, bins, blockers, and other USD scene assets already exist
- the goal is to run the state machine inside an authored workcell

## 3.5 Path E: maintainer, debugger, or upgrader

Read:

- `(3) -> (8)`

Use this path if:

- the delivery changes need to be understood
- maintenance, migration, or upgrade work is planned for this setup

---

## 4. Document overview

## (1) [`README.md`](../../README.md)

Role:

- top-level entry point

What it provides:

- the primary documentation links
- the shortest install and demo commands
- the quickest way to find the next document

## (2) [`WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.en.md`](./WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.en.md)

Role:

- full installation and repair tutorial

What it provides:

- the practical Windows + Isaac Sim installation route
- the real reasons the original install path fails
- a stable repair-and-install workflow

## (3) [`INSTALLABLE_VERSION_MANUAL.en.md`](./INSTALLABLE_VERSION_MANUAL.en.md)

Role:

- delivery manual for the installable version

What it provides:

- the purpose of the key scripts and documents
- the structure of the delivered Windows build
- the role of wrappers, smoke tests, demos, and GUI teaching scripts

## (4) [`ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.en.md`](./ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.en.md)

Role:

- beginner guide for in-app GUI usage

What it provides:

- why `selector.bat` is a valid way to start Isaac Sim and still use cuRobo
- the difference between standalone and in-app scripts
- how to run cuRobo from `Isaac Sim Full -> Window -> Script Editor`

## (5) [`ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.en.md`](./ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.en.md)

Role:

- next-step guide for custom robots and scenes

What it provides:

- how to change the robot
- how to change tables and obstacles
- how to keep the cuRobo world synchronized with the GUI scene
- how to evolve from a single-plan demo into a custom scene template

## (6) [`ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.en.md`](./ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.en.md)

Role:

- pick/place state machine and teaching-scene modeling guide

What it provides:

- a full task flow: pregrasp, grasp, close, lift, preplace, place, retreat
- the structure of the teaching state machine
- beginner-friendly scene modeling rules

## (7) [`ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md`](./ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md)

Role:

- guide for attaching the pick/place state machine to a user-provided USD scene

What it provides:

- how to load a user-provided USD scene
- how to define obstacle roots for cuRobo
- how to attach existing pick object / pick target / place target prims
- how to auto-create runtime markers when the authored scene does not have them yet

## (8) [`curobo_isaacsim_windows_full_fix_guide.en.md`](./curobo_isaacsim_windows_full_fix_guide.en.md)

Role:

- full repair log and maintenance guide

What it provides:

- the actual environment background
- the real failure chain and root causes
- the concrete code and script changes
- the engineering conclusions and maintenance notes

---

## 5. Recommended practical workflow

### Step 1: make sure the environment is healthy

Read:

- `(2)`

Run:

```powershell
cd <REPO_ROOT>
.\install_in_isaacsim.bat
.\verify_isaacsim_integration.bat
```

### Step 2: learn the normal GUI workflow

Read:

- `(4)`

Goal:

- understand `selector -> Isaac Sim Full -> Script Editor -> Run`

### Step 3: build a base workcell scene

Read:

- `(5)`

Goal:

- change the robot, goals, obstacles, and world sync path safely

### Step 4: upgrade from single planning to task flow

Read:

- `(6)`

Goal:

- understand the state machine and teaching scene modeling

### Step 5: attach a user-provided USD scene

Read:

- `(7)`

Goal:

- run the state machine against a real authored workcell scene

### Step 6: only then read the deep maintenance history

Read:

- `(3)`
- `(8)`

Goal:

- understand the delivery layout, compatibility layers, and maintenance risks

---

## 6. One-line summary of each document

(1) `README.md`: the top-level entry page.

(2) `WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.en.md`: install, repair, and validate the environment.

(3) `INSTALLABLE_VERSION_MANUAL.en.md`: understand the delivery structure and file roles.

(4) `ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.en.md`: use cuRobo inside a normally started Isaac Sim GUI.

(5) `ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.en.md`: begin building a custom robot and scene workflow.

(6) `ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.en.md`: turn one-shot planning into a pick/place state machine.

(7) `ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md`: attach a user-provided USD scene to the state machine.

(8) `curobo_isaacsim_windows_full_fix_guide.en.md`: deep repair history and maintenance reference.

---

## 7. Short recommendation

If the installation already works and the next goal is task execution in a user-provided scene, the shortest useful reading path is:

- `(4)`
- `(5)`
- `(6)`
- `(7)`

If maintenance or upgrade work is needed later, then add:

- `(3)`
- `(8)`
