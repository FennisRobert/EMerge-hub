#!/usr/bin/env python3
"""
build_site.py
==============

Builds the static "EMerge Template Explorer" website: a single-page app
with a category tree, template previews, and source code viewer (with
copy-to-clipboard) for every implemented template in Templates/.

It reads the exact same sources as generate_gallery.py (Templates/ folder
structure + Templates/checklist.md), but instead of rendering markdown it
emits a static site into an output directory:

    <output>/
      index.html, style.css, app.js   (copied verbatim from webapp/)
      data.json                       (generated: all template metadata + code)
      assets/<TEMPLATE-ID>.png        (generated: copied preview images)

That output directory is deployable as-is to GitHub Pages (see
.github/workflows/deploy-pages.yml, which runs this script on every push).

Usage
-----
    python build_site.py
    python build_site.py --templates-dir Templates --webapp-dir webapp --output _site
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

ID_RE = re.compile(r"^([A-Za-z]+-[A-Za-z]+-\d+[a-zA-Z]?)(?:_.*)?$")
DIVIDER_RE = re.compile(r"^#\s*[-=]{10,}\s*$")
LICENSE_MARKERS = ("copyright", "gnu general public license", "free software foundation")
IMAGE_NAME = "geo.png"
PLOT_IMAGE_NAME = "plot.png"

# Shown separately at the bottom of the home page leaderboard instead of
# competing for a top-10 spot.
LEAD_DEVELOPER = "Robert Fennis"

# Used to build "View on GitHub" / "Download repository" links.
REPO_OWNER = "FennisRobert"
REPO_NAME = "EMerge-hub"
REPO_BRANCH = "main"


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #
@dataclass
class Row:
    id: str
    name: str
    feed: str = ""
    notes: str = ""
    v28: bool = False
    v30: bool = False
    contributor: str = ""


@dataclass
class Subsection:
    title: str
    rows: list = field(default_factory=list)


@dataclass
class Section:
    title: str
    subsections: list = field(default_factory=list)


@dataclass
class ModelFolder:
    id: str
    path: Path
    image: Path | None = None
    plot_image: Path | None = None
    py_files: list = field(default_factory=list)
    description: str | None = None


# --------------------------------------------------------------------------- #
# checklist.md parsing (same format as generate_gallery.py)
# --------------------------------------------------------------------------- #
def parse_checklist(path: Path) -> list:
    if not path.exists():
        return []

    sections = []
    current_section = None
    current_sub = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()

        if line.startswith("## "):
            current_section = Section(title=line[3:].strip())
            sections.append(current_section)
            current_sub = None
            continue

        if line.startswith("### "):
            current_sub = Subsection(title=line[4:].strip())
            if current_section is None:
                current_section = Section(title="Other")
                sections.append(current_section)
            current_section.subsections.append(current_sub)
            continue

        if not line.startswith("|"):
            continue

        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 7:
            continue
        if cols[0].lower() in ("id", "") or set(cols[0]) <= {"-", ":"}:
            continue

        row_id = cols[0].strip("`").strip()
        if not row_id:
            continue

        name = cols[1].strip("*").strip()
        feed = cols[2]
        notes = cols[3]
        v28 = "[x]" in cols[4].lower()
        v30 = "[x]" in cols[5].lower()
        contributor = cols[6]

        row = Row(id=row_id, name=name, feed=feed, notes=notes,
                  v28=v28, v30=v30, contributor=contributor)

        if current_sub is None:
            current_sub = Subsection(title="Other")
            if current_section is None:
                current_section = Section(title="Other")
                sections.append(current_section)
            current_section.subsections.append(current_sub)

        current_sub.rows.append(row)

    return sections


# --------------------------------------------------------------------------- #
# Templates/ directory scanning
# --------------------------------------------------------------------------- #
def extract_description(py_path: Path) -> str | None:
    try:
        lines = py_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None

    header_end = len(lines)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            header_end = i
            break
    header = lines[:header_end]

    divider_idxs = [i for i, l in enumerate(header) if DIVIDER_RE.match(l)]
    candidates = []
    for start, end in zip(divider_idxs, divider_idxs[1:]):
        block = header[start + 1:end]
        text_lines = []
        for l in block:
            l = l.strip()
            if l == "#":
                text_lines.append("")
                continue
            if l.startswith("#"):
                text_lines.append(l.lstrip("#").strip())
        text = "\n".join(text_lines).strip("\n")
        if not text.strip():
            continue
        lowered = text.lower()
        if any(marker in lowered for marker in LICENSE_MARKERS):
            continue
        candidates.append(text)

    if not candidates:
        return None
    best = re.sub(r"\n{3,}", "\n\n", candidates[0])
    return best.strip()


def label_for_py(p: Path) -> str:
    name = p.name.lower()
    if "3p0" in name or "3.0" in name or "_3." in name:
        return "v3.0"
    if "2p8" in name or "2.8" in name or "_2." in name:
        return "v2.8"
    return p.stem.replace("_", " ")


def sort_key_for_py(p: Path) -> tuple:
    label = label_for_py(p)
    order = {"v3.0": 0, "v2.8": 1}
    return (order.get(label, 2), p.name.lower())


def scan_templates(templates_dir: Path) -> dict:
    models = {}

    for path in sorted(templates_dir.rglob("*")):
        if not path.is_dir():
            continue
        if path.name.startswith("_"):
            continue
        m = ID_RE.match(path.name)
        if not m:
            continue
        model_id = m.group(1).upper()

        images = sorted(path.rglob(IMAGE_NAME))
        plot_images = sorted(path.rglob(PLOT_IMAGE_NAME))
        py_files = sorted((p for p in path.rglob("*.py")), key=sort_key_for_py)

        model = ModelFolder(
            id=model_id,
            path=path,
            image=images[0] if images else None,
            plot_image=plot_images[0] if plot_images else None,
            py_files=py_files,
        )
        if py_files:
            model.description = extract_description(py_files[0])

        existing = models.get(model_id)
        if existing is None or (existing.image is None and model.image is not None):
            models[model_id] = model

    return models


def fallback_sections(models: dict, templates_dir: Path) -> list:
    groups = {}
    for model_id, model in models.items():
        rel = model.path.relative_to(templates_dir).parts
        domain = rel[0] if len(rel) > 0 else "Other"
        category = rel[1] if len(rel) > 1 else "Other"
        row = Row(id=model_id, name=model.path.name.split("_", 1)[-1].replace("_", " "))
        groups.setdefault((domain, category), []).append(row)

    sections = {}
    for (domain, category), rows in sorted(groups.items()):
        section = sections.setdefault(domain, Section(title=domain))
        sub = Subsection(title=f"{domain}/{category}", rows=sorted(rows, key=lambda r: r.id))
        section.subsections.append(sub)
    return list(sections.values())


def normalize_contributor(name: str) -> str:
    name = name.strip()
    name = re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()  # drop "(Claude)"-style notes
    return name


def compute_leaderboard(data: dict) -> dict:
    counts: dict[str, int] = {}
    for section in data["sections"]:
        for sub in section["subsections"]:
            for t in sub["templates"]:
                raw = (t.get("contributor") or "").strip()
                if not raw:
                    continue
                for part in re.split(r"[,/&]| and ", raw):
                    name = normalize_contributor(part)
                    if name:
                        counts[name] = counts.get(name, 0) + 1

    lead_count = counts.pop(LEAD_DEVELOPER, 0)
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].lower()))
    top = [{"name": n, "count": c} for n, c in ranked[:10]]
    return {
        "top": top,
        "lead": {"name": LEAD_DEVELOPER, "count": lead_count},
    }


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_data(sections: list, models: dict) -> dict:
    out_sections = []
    total_rows = 0
    implemented = 0
    with_image = 0

    for section in sections:
        out_subs = []
        for sub in section.subsections:
            out_templates = []
            for row in sub.rows:
                total_rows += 1
                model = models.get(row.id)
                if model is None:
                    continue
                implemented += 1

                files = []
                for p in model.py_files:
                    try:
                        code = p.read_text(encoding="utf-8", errors="ignore")
                    except OSError:
                        continue
                    files.append({
                        "label": label_for_py(p),
                        "filename": p.name,
                        "path": p.as_posix(),
                        "code": code,
                    })

                image_rel = f"assets/{row.id}.png" if model.image else None
                if model.image:
                    with_image += 1

                plot_rel = f"assets/{row.id}-plot.png" if model.plot_image else None

                out_templates.append({
                    "id": row.id,
                    "name": row.name or model.path.name.split("_", 1)[-1].replace("_", " "),
                    "feed": row.feed,
                    "notes": row.notes,
                    "contributor": row.contributor,
                    "v28": row.v28,
                    "v30": row.v30,
                    "description": model.description or row.notes,
                    "image": image_rel,
                    "plot": plot_rel,
                    "files": files,
                })
            if out_templates:
                out_subs.append({"title": sub.title, "templates": out_templates})
        if out_subs:
            out_sections.append({"title": section.title, "subsections": out_subs})

    return {
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": {
            "owner": REPO_OWNER,
            "name": REPO_NAME,
            "branch": REPO_BRANCH,
        },
        "stats": {
            "implemented": implemented,
            "total": total_rows,
            "with_image": with_image,
        },
        "sections": out_sections,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--templates-dir", default="Templates")
    parser.add_argument("--checklist", default=None)
    parser.add_argument("--webapp-dir", default="webapp")
    parser.add_argument("--output", default="_site")
    args = parser.parse_args()

    templates_dir = Path(args.templates_dir)
    if not templates_dir.exists():
        raise SystemExit(f"Templates directory not found: {templates_dir}")

    webapp_dir = Path(args.webapp_dir)
    if not webapp_dir.exists():
        raise SystemExit(f"Webapp directory not found: {webapp_dir}")

    checklist_path = Path(args.checklist) if args.checklist else templates_dir / "checklist.md"

    models = scan_templates(templates_dir)
    sections = parse_checklist(checklist_path)
    if not sections:
        print(f"[info] Could not parse {checklist_path}, falling back to folder-based grouping.")
        sections = fallback_sections(models, templates_dir)

    data = build_data(sections, models)
    data["leaderboard"] = compute_leaderboard(data)

    out_dir = Path(args.output)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    # Copy the hand-authored app shell verbatim.
    for item in webapp_dir.iterdir():
        dest = out_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # Copy preview images.
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    for section in data["sections"]:
        for sub in section["subsections"]:
            for t in sub["templates"]:
                model = models[t["id"]]
                if t["image"]:
                    shutil.copy2(model.image, assets_dir / f"{t['id']}.png")
                if t["plot"]:
                    shutil.copy2(model.plot_image, assets_dir / f"{t['id']}-plot.png")

    (out_dir / "data.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(f"[ok] Built site into {out_dir} "
          f"({data['stats']['implemented']}/{data['stats']['total']} templates, "
          f"{data['stats']['with_image']} with preview images)")


if __name__ == "__main__":
    main()
