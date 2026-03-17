#!/usr/bin/env python3
"""Render a competitive report HTML from a fixture JSON file."""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "competitive_report.html"


def build_rows(data: dict) -> dict:
    """Return strength_rows and gap_rows lists from fixture data."""
    checks = data["checks"]
    num_competitors = len(data["competitors"])

    strength_rows = []
    gap_rows = []

    for check in checks:
        buyer = check["buyer_status"]
        comp_statuses = check["competitor_statuses"]

        competitors_failing = sum(
            1 for s in comp_statuses if s in ("fail", "partial")
        )
        competitors_passing = sum(1 for s in comp_statuses if s == "pass")
        competitors_better = sum(
            1
            for s in comp_statuses
            if (buyer == "fail" and s in ("pass", "partial"))
            or (buyer == "partial" and s == "pass")
        )

        row_base = {
            "id": check["id"],
            "name": check["name"],
            "description": check["description"],
            "buyer_status": buyer,
        }

        # Strength: buyer passes AND at least one competitor fails or partial
        if buyer == "pass" and competitors_failing > 0:
            strength_rows.append(
                {**row_base, "competitors_failing": competitors_failing}
            )

        # Gap: buyer fails or partial AND at least one competitor is better
        if buyer in ("fail", "partial") and competitors_better > 0:
            gap_rows.append(
                {**row_base, "competitors_passing": competitors_passing}
            )

    # Sort strengths by competitors_failing descending (biggest advantage first)
    strength_rows.sort(key=lambda r: r["competitors_failing"], reverse=True)

    # Sort gaps: fail first, then partial
    severity = {"fail": 0, "partial": 1}
    gap_rows.sort(key=lambda r: severity.get(r["buyer_status"], 2))

    return {"strength_rows": strength_rows, "gap_rows": gap_rows}


def render_strength_row(row: dict, num_competitors: int) -> str:
    return (
        f'<div class="cr-row">'
        f'<div class="cr-check-name">{row["name"]}'
        f'<span class="cr-check-id">{row["id"]}</span>'
        f'<small>{row["description"]}</small></div>'
        f'<div class="cr-status">'
        f'<span class="status-pill pass">PASS</span></div>'
        f'<div class="cr-comp-note">'
        f'{row["competitors_failing"]} of {num_competitors} competitors '
        f'fail or partial this</div>'
        f'</div>'
    )


def render_gap_row(row: dict, num_competitors: int) -> str:
    status = row["buyer_status"]
    pill_class = "fail" if status == "fail" else "partial"
    pill_label = status.upper()
    return (
        f'<div class="cr-row">'
        f'<div class="cr-check-name">{row["name"]}'
        f'<span class="cr-check-id">{row["id"]}</span>'
        f'<small>{row["description"]}</small></div>'
        f'<div class="cr-status">'
        f'<span class="status-pill {pill_class}">{pill_label}</span></div>'
        f'<div class="cr-comp-note">'
        f'{row["competitors_passing"]} of {num_competitors} competitors '
        f'pass this</div>'
        f'</div>'
    )


def render(fixture_path: str, output_path: str | None = None) -> str:
    with open(fixture_path) as f:
        data = json.load(f)

    template = TEMPLATE.read_text()
    rows = build_rows(data)
    num_competitors = len(data["competitors"])

    strength_html = "\n".join(
        render_strength_row(r, num_competitors) for r in rows["strength_rows"]
    )
    gap_html = "\n".join(
        render_gap_row(r, num_competitors) for r in rows["gap_rows"]
    )

    # Build competitor header pills
    comp_pills = "".join(
        f'<span class="cr-comp-pill">{c["name"]}</span>'
        for c in data["competitors"]
    )

    html = (
        template
        .replace("{{buyer_name}}", data["buyer"]["name"])
        .replace("{{buyer_domain}}", data["buyer"]["domain"])
        .replace("{{buyer_city}}", data["buyer"]["city"])
        .replace("{{buyer_score}}", str(data["buyer"]["score"]))
        .replace("{{competitor_pills}}", comp_pills)
        .replace("{{strength_rows}}", strength_html)
        .replace("{{gap_rows}}", gap_html)
        .replace("{{num_strengths}}", str(len(rows["strength_rows"])))
        .replace("{{num_gaps}}", str(len(rows["gap_rows"])))
    )

    out = pathlib.Path(output_path) if output_path else ROOT / "competitive_report_output.html"
    out.write_text(html)
    print(f"Rendered to {out} ({len(html):,} bytes)")
    print(f"  Strengths: {len(rows['strength_rows'])}  Gaps: {len(rows['gap_rows'])}")
    return str(out)


if __name__ == "__main__":
    fixture = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "fixtures" / "competitive_normal.json")
    output = sys.argv[2] if len(sys.argv) > 2 else None
    render(fixture, output)
