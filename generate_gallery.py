#!/usr/bin/env python3
"""
generate_template_gallery.py
=============================

Regenerates TEMPLATE_GALLERY.md: a visual, browsable overview of every
EMerge simulation template in the Templates/ directory, grouped the same
way Templates/checklist.md is grouped (technology > sub-category).

How it works
------------
1. Parses Templates/checklist.md for the curated metadata table
   (ID, name, feed strategy, notes, v2.8/v3.0 status, contributor).
   This is the primary source of truth for names/descriptions.
2. Walks the Templates/ directory looking for folders whose name starts
   with a template ID (e.g. "PCB-ANT-01_PIFA" -> id "PCB-ANT-01"), and
   records the geo.png preview image (if any) and the .py template
   file(s) in that folder.
3. For each matched .py file, pulls the free-text description out of the
   commented header block (the block of text between two "# ---...---"
   or "# ===...===" divider lines that is NOT the license block).
4. Renders everything into TEMPLATE_GALLERY.md as an image gallery,
   grouped by section/sub-section, with a "not implemented yet" list at
   the end pulled straight from the checklist so the gallery doubles as
   a contribution guide.

If checklist.md is missing, malformed, or renamed, the script falls back
to grouping purely by folder structure (Templates/<domain>/<category>/...)
so it never just crashes on you.

Usage
-----
    python generate_template_gallery.py
    python generate_template_gallery.py --templates-dir Templates --output TEMPLATE_GALLERY.md
    python generate_template_gallery.py --no-missing   # skip the "not yet built" section

Re-run this any time you add/rename a template folder or update checklist.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path

ID_RE = re.compile(r"^([A-Za-z]+-[A-Za-z]+-\d+[a-zA-Z]?)(?:_.*)?$")
DIVIDER_RE = re.compile(r"^#\s*[-=]{10,}\s*$")
LICENSE_MARKERS = ("copyright", "gnu general public license", "free software foundation")
IMAGE_NAME = "geo.png"


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
    rows: list[Row] = field(default_factory=list)


@dataclass
class Section:
    title: str
    subsections: list[Subsection] = field(default_factory=list)


@dataclass
class ModelFolder:
    id: str
    path: Path
    image: Path | None = None
    py_files: list[Path] = field(default_factory=list)
    description: str | None = None


# --------------------------------------------------------------------------- #
# checklist.md parsing
# --------------------------------------------------------------------------- #
def parse_checklist(path: Path) -> list[Section]:
    if not path.exists():
        return []

    sections: list[Section] = []
    current_section: Section | None = None
    current_sub: Subsection | None = None

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
            continue  # header / separator row

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
    """Pull the free-text description out of a template's header comment
    block: the first '#'-delimited block (bounded by long ---- or ==== rows)
    that is NOT the GPL license notice."""
    try:
        lines = py_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None

    # Only look at the header, i.e. before the first import/code line.
    header_end = len(lines)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            header_end = i
            break
    header = lines[:header_end]

    divider_idxs = [i for i, l in enumerate(header) if DIVIDER_RE.match(l)]
    candidates: list[str] = []
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
    # collapse runs of blank lines
    best = re.sub(r"\n{3,}", "\n\n", candidates[0])
    return best.strip()


def pick_primary_py(py_files: list[Path]) -> Path | None:
    if not py_files:
        return None
    def score(p: Path) -> tuple:
        name = p.name.lower()
        is_v3 = ("3p0" in name) or ("3.0" in name) or ("_3." in name)
        return (0 if is_v3 else 1, name)
    return sorted(py_files, key=score)[0]


def scan_templates(templates_dir: Path) -> dict[str, ModelFolder]:
    models: dict[str, ModelFolder] = {}

    for path in sorted(templates_dir.rglob("*")):
        if not path.is_dir():
            continue
        if path.name.startswith("_"):
            continue  # scaffolding dirs like _template_dir
        m = ID_RE.match(path.name)
        if not m:
            continue
        model_id = m.group(1).upper()

        images = sorted(path.rglob(IMAGE_NAME))
        py_files = sorted(p for p in path.rglob("*.py"))

        model = ModelFolder(
            id=model_id,
            path=path,
            image=images[0] if images else None,
            py_files=py_files,
        )
        primary = pick_primary_py(py_files)
        if primary is not None:
            model.description = extract_description(primary)

        # If the same ID appears twice (shouldn't normally happen), keep
        # whichever copy actually has a preview image.
        existing = models.get(model_id)
        if existing is None or (existing.image is None and model.image is not None):
            models[model_id] = model

    return models


# --------------------------------------------------------------------------- #
# Fallback grouping when checklist.md isn't usable
# --------------------------------------------------------------------------- #
def fallback_sections(models: dict[str, ModelFolder], templates_dir: Path) -> list[Section]:
    groups: dict[tuple[str, str], list[Row]] = {}
    for model_id, model in models.items():
        rel = model.path.relative_to(templates_dir).parts
        domain = rel[0] if len(rel) > 0 else "Other"
        category = rel[1] if len(rel) > 1 else "Other"
        row = Row(id=model_id, name=model.path.name.split("_", 1)[-1].replace("_", " "))
        groups.setdefault((domain, category), []).append(row)

    sections: dict[str, Section] = {}
    for (domain, category), rows in sorted(groups.items()):
        section = sections.setdefault(domain, Section(title=domain))
        sub = Subsection(title=f"{domain}/{category}", rows=sorted(rows, key=lambda r: r.id))
        section.subsections.append(sub)
    return list(sections.values())


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def slugify(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s


def status_badge(row: Row) -> str:
    v28 = "✅ 2.8" if row.v28 else "⬜ 2.8"
    v30 = "✅ 3.0" if row.v30 else "⬜ 3.0"
    return f"{v28} &nbsp;·&nbsp; {v30}"


def render_card(row: Row, model: ModelFolder | None, templates_dir_name: str) -> str:
    label = f"{row.id} · {row.name}" if row.name else row.id
    lines = ['<td align="center" width="33%">']

    if model and model.image:
        img_rel = model.image.as_posix()
        folder_rel = model.path.as_posix()
        lines.append(f'<a href="{folder_rel}"><img src="{img_rel}" width="230"/></a><br/>')
    else:
        lines.append("<sub><i>(no preview image yet)</i></sub><br/>")

    lines.append(f"<b>{label}</b><br/>")
    notes = row.notes or (model.description.splitlines()[0] if model and model.description else "")
    if notes:
        notes = notes.replace("|", "\\|")
        lines.append(f"<sub>{notes}</sub><br/>")
    if row.feed:
        lines.append(f"<sub>Feed: {row.feed}</sub><br/>")
    lines.append(f"<sub>{status_badge(row)}")
    if row.contributor:
        lines.append(f" &nbsp;·&nbsp; {row.contributor}")
    lines.append("</sub>")
    lines.append("</td>")
    return "\n".join(lines)


def render_grid(rows: list[Row], models: dict[str, ModelFolder], templates_dir_name: str,
                 cols: int = 3) -> str:
    cells = [render_card(row, models.get(row.id), templates_dir_name) for row in rows]
    out = ['<table>']
    for i in range(0, len(cells), cols):
        out.append("<tr>")
        out.extend(cells[i:i + cols])
        # pad the row so the table stays aligned
        for _ in range(cols - len(cells[i:i + cols])):
            out.append('<td width="33%"></td>')
        out.append("</tr>")
    out.append("</table>")
    return "\n".join(out)


def build_markdown(sections: list[Section], models: dict[str, ModelFolder],
                    templates_dir: Path, include_missing: bool = True) -> str:
    templates_dir_name = templates_dir.name
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    total_rows = sum(len(sub.rows) for sec in sections for sub in sec.subsections)
    built_rows = [r for sec in sections for sub in sec.subsections for r in sub.rows if r.id in models]
    with_image = [r for r in built_rows if models[r.id].image]

    out: list[str] = []
    out.append("# EMerge Template Gallery")
    out.append("")
    out.append(f"_Auto-generated on {now} by `generate_template_gallery.py` — do not edit by hand,"
                f" re-run the script instead._")
    out.append("")
    out.append(f"**{len(with_image)}** templates with a preview image, "
                f"**{len(built_rows)}** implemented in total, out of "
                f"**{total_rows}** catalogued in `{templates_dir.name}/checklist.md`.")
    out.append("")

    # Table of contents
    out.append("## Contents")
    out.append("")
    for section in sections:
        out.append(f"- [{section.title}](#{slugify(section.title)})")
        for sub in section.subsections:
            out.append(f"  - [{sub.title}](#{slugify(sub.title)})")
    if include_missing:
        out.append("- [Not yet implemented](#not-yet-implemented)")
    out.append("")
    out.append("---")
    out.append("")

    missing_rows: list[Row] = []

    for section in sections:
        out.append(f"## {section.title}")
        out.append("")
        for sub in section.subsections:
            visual_rows = [r for r in sub.rows if r.id in models and models[r.id].image]
            text_only_rows = [r for r in sub.rows if r.id in models and not models[r.id].image]
            not_built = [r for r in sub.rows if r.id not in models]
            missing_rows.extend(not_built)

            out.append(f"### {sub.title}")
            out.append("")
            if visual_rows:
                out.append(render_grid(visual_rows, models, templates_dir_name))
                out.append("")
            if text_only_rows:
                out.append("<details>")
                out.append("<summary>Implemented, preview image not committed yet"
                            f" ({len(text_only_rows)})</summary>")
                out.append("")
                out.append("| ID | Name | Notes | v2.8 | v3.0 | Contributor |")
                out.append("|---|---|---|---|---|---|")
                for r in text_only_rows:
                    out.append(f"| `{r.id}` | {r.name} | {r.notes} | "
                               f"{'✅' if r.v28 else ''} | {'✅' if r.v30 else ''} | {r.contributor} |")
                out.append("")
                out.append("</details>")
                out.append("")
            if not visual_rows and not text_only_rows:
                out.append("_Nothing implemented yet in this category — see below._")
                out.append("")

    if include_missing and missing_rows:
        out.append("---")
        out.append("")
        out.append("## Not yet implemented")
        out.append("")
        out.append("Planned templates from `checklist.md` with no matching folder under "
                    f"`{templates_dir.name}/` yet. Want to contribute one? Pick an ID below.")
        out.append("")
        out.append("| ID | Name | Feed Strategy | Notes |")
        out.append("|---|---|---|---|")
        for r in missing_rows:
            out.append(f"| `{r.id}` | {r.name} | {r.feed} | {r.notes} |")
        out.append("")

    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--templates-dir", default="Templates",
                         help="Path to the Templates directory (default: Templates)")
    parser.add_argument("--checklist", default=None,
                         help="Path to checklist.md (default: <templates-dir>/checklist.md)")
    parser.add_argument("--output", default="TEMPLATE_GALLERY.md",
                         help="Output markdown file (default: TEMPLATE_GALLERY.md)")
    parser.add_argument("--no-missing", action="store_true",
                         help="Don't include the 'not yet implemented' section")
    args = parser.parse_args()

    templates_dir = Path(args.templates_dir)
    if not templates_dir.exists():
        raise SystemExit(f"Templates directory not found: {templates_dir}")

    checklist_path = Path(args.checklist) if args.checklist else templates_dir / "checklist.md"

    models = scan_templates(templates_dir)
    sections = parse_checklist(checklist_path)

    if not sections:
        print(f"[info] Could not parse {checklist_path}, falling back to folder-based grouping.")
        sections = fallback_sections(models, templates_dir)

    markdown = build_markdown(sections, models, templates_dir,
                               include_missing=not args.no_missing)

    out_path = Path(args.output)
    out_path.write_text(markdown, encoding="utf-8")
    print(f"[ok] Wrote {out_path} "
          f"({sum(len(s.subsections) for s in sections)} subsections, {len(models)} model folders found)")


if __name__ == "__main__":
    main()