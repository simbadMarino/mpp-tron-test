#!/usr/bin/env python3
"""Requirements <-> test case traceability check.

Usage:
  python tools/trace.py              # report to stdout
  python tools/trace.py --write      # also write traceability.md
  python tools/trace.py --strict     # exit 1 if any open requirement is uncovered

Conventions
  requirements/*.md : "## <ID> <title>" headings with "- Key: value" lines.
                    Only IDs with the tracked prefix (SYS-) count for coverage and
                    appear in the matrix. Other IDs (BASE-, EVM-, SES-) are reference
                    extracts of the upstream drafts: they are read only to check that
                    each one is carried by exactly one tracked requirement through its
                    "- Source:" line, or is listed on a "Not carried: ID, ID" line.
  tests/**        : any line containing "Covers: ID, ID" (case-insensitive).
                    In .md files a "## TC-nnn title" heading names the test case;
                    in other files (code comments) the test is "file:line".
  Files in tests/ whose name starts with "_" are ignored.
Exit code 1 on unknown requirement IDs referenced by tests (always), and with
--strict also on uncovered open requirements, on tests that reference a reference
ID instead of a SYS ID, and on source-map inconsistencies.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ID = r"[A-Z]+-\d+"
TRACKED = "SYS-"   # prefix of the requirements that tests must cover

def parse_requirements(rdir):
    """Return (all requirements by ID, IDs declared as not carried)."""
    reqs, cur, not_carried = {}, None, set()
    for path in sorted(rdir.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            nc = re.search(r"Not carried:\s*(.*)$", line)
            if nc:
                not_carried.update(re.findall(ID, nc[1]))
            m = re.match(rf"^## ({ID})\s+(.*)$", line)
            if m:
                if m[1] in reqs:
                    print(f"WARNING: duplicate requirement ID {m[1]} in {path.name}", file=sys.stderr)
                cur = {"id": m[1], "title": m[2].strip(), "status": "open", "doc": path.stem,
                       "level": "", "role": "", "layer": "", "tron": "", "spec": ""}
                reqs[m[1]] = cur
            elif cur:
                kv = re.match(r"^- (\w+): (.*)$", line)
                if kv:
                    key = kv[1].lower()
                    cur["layer" if key == "verification" else key] = kv[2].strip()
    return reqs, not_carried

def check_sources(tracked, reference, not_carried):
    """Each reference ID is carried by exactly one tracked requirement (or declared not carried)."""
    carried, problems = {}, []
    for r in tracked.values():
        for rid in re.findall(ID, r.get("source", "")):
            carried.setdefault(rid, []).append(r["id"])
    for rid, by in sorted(carried.items()):
        if rid not in reference:
            problems.append(f"  {rid}  named in Source of {', '.join(by)} but not found in the reference files")
        elif len(by) > 1:
            problems.append(f"  {rid}  carried by more than one requirement: {', '.join(by)}")
        if rid in not_carried:
            problems.append(f"  {rid}  listed as not carried but named in Source of {', '.join(by)}")
    for rid in reference:
        if rid not in carried and rid not in not_carried:
            problems.append(f"  {rid}  not carried by any {TRACKED}xxx requirement")
    return carried, problems

def parse_tests(tdir):
    links = []  # (test_ref, req_id, status)
    for f in sorted(tdir.rglob("*")):
        if not f.is_file() or f.name.startswith("_"):
            continue
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        rel = f.relative_to(ROOT)
        tc, status = None, ""
        for n, line in enumerate(lines, 1):
            h = re.match(r"^## (TC-\d+)\b", line)
            if h:
                tc, status = h[1], ""
            s = re.match(r"^Status:\s*(\S+)", line)
            if s:
                status = s[1]
            c = re.search(r"covers:\s*(.*)$", line, re.I)
            if c:
                ref = f"{tc} ({rel.name})" if (f.suffix == ".md" and tc) else f"{rel}:{n}"
                for rid in re.findall(ID, c[1]):
                    links.append((ref, rid, status))
    return links

def main():
    write, strict = "--write" in sys.argv, "--strict" in sys.argv
    allreqs, not_carried = parse_requirements(ROOT / "requirements")
    reqs = {i: r for i, r in allreqs.items() if i.startswith(TRACKED)}
    reference = {i: r for i, r in allreqs.items() if not i.startswith(TRACKED)}
    carried, source_problems = check_sources(reqs, reference, not_carried)
    links = parse_tests(ROOT / "tests")

    cover = {rid: [] for rid in reqs}
    unknown, untracked = {}, {}
    for ref, rid, st in links:
        if rid in cover:
            cover[rid].append(ref)
        elif rid in reference:
            untracked.setdefault(rid, []).append(ref)
        else:
            unknown.setdefault(rid, []).append(ref)

    active = [r for r in reqs.values() if not r["status"].lower().startswith("n/a")]
    gaps = [r for r in active if not cover[r["id"]]]
    covered = len(active) - len(gaps)

    lines = [f"{TRACKED.rstrip('-')} requirements: {len(reqs)} total, {len(active)} active, "
             f"{covered} covered, {len(gaps)} uncovered "
             f"({(100*covered//len(active)) if active else 0}%)"]
    if gaps:
        lines.append("\nUncovered (open):")
        lines += [f"  {r['id']}  {r['title']}  [{r['layer'] or '-'}]" for r in gaps]
    if untracked:
        lines.append(f"\nTests referencing reference IDs (not counted; use the {TRACKED}xxx requirement instead):")
        lines += [f"  {rid}  <- {', '.join(refs)}  -> use {', '.join(carried.get(rid, ['?']))}"
                  for rid, refs in sorted(untracked.items())]
    if source_problems:
        lines.append("\nSource map inconsistencies:")
        lines += source_problems
    if unknown:
        lines.append("\nUnknown requirement IDs referenced by tests:")
        lines += [f"  {rid}  <- {', '.join(refs)}" for rid, refs in sorted(unknown.items())]
    print("\n".join(lines))

    if write:
        md = ["# Traceability matrix", "", "_Generated by `tools/trace.py --write`. Do not edit by hand._", "",
              f"**{covered}/{len(active)} active requirements covered**", "",
              "| Requirement | Title | Level | Role | Verification | TRON | Req status | Covered by |",
              "|---|---|---|---|---|---|---|---|"]
        for r in reqs.values():
            by = "<br>".join(cover[r["id"]]) or "**GAP**"
            md.append(f"| {r['id']} | {r['title']} | {r['level'] or '-'} | {r['role'] or '-'} | "
                      f"{r['layer'] or '-'} | {r['tron'] or '-'} | {r['status']} | {by} |")
        (ROOT / "traceability.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        print("\nWrote traceability.md")

    if unknown or (strict and (gaps or untracked or source_problems)):
        sys.exit(1)

if __name__ == "__main__":
    main()
