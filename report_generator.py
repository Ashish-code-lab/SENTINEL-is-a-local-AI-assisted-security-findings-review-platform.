
import json
import html
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILES = {
    "zap": BASE_DIR / "normalized-findings.json",
    "red": BASE_DIR / "red-agent-results.json",
    "blue": BASE_DIR / "blue-agent-results.json",
    "judge": BASE_DIR / "judge-agent-results.json",
}

OUTPUT_FILE = BASE_DIR / "sentinel-security-report.html"


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def safe(value):
    return html.escape(str(value if value is not None else "Not provided"))


def generate_report():

    zap = load_json(INPUT_FILES["zap"])
    red = load_json(INPUT_FILES["red"])
    blue = load_json(INPUT_FILES["blue"])
    judge = load_json(INPUT_FILES["judge"])

    findings = zap.get("findings", [])

    # Match results by unique finding key.
    red_map = {
        item.get("finding_key"): item
        for item in red.get("results", [])
        if item.get("finding_key")
    }

    blue_map = {
        item.get("finding_key"): item
        for item in blue.get("results", [])
        if item.get("finding_key")
    }

    judge_map = {
        item.get("finding_key"): item
        for item in judge.get("results", [])
        if item.get("finding_key")
    }

    severity_order = [
        "Critical", "High", "Medium", "Low", "Informational"
    ]

    severity_counts = {
        severity: sum(
            1 for item in findings
            if item.get("severity") == severity
        )
        for severity in severity_order
    }

    cards = ""
    matched = 0

    for index, finding in enumerate(findings, start=1):

        fid = finding.get("plugin_id")
        finding_key = f"{fid}_{index}"

        red_item = red_map.get(finding_key, {})
        blue_item = blue_map.get(finding_key, {})
        judge_item = judge_map.get(finding_key, {})

        if red_item and blue_item and judge_item:
            matched += 1

        instances = "".join(
            f"<li>{safe(instance.get('url'))}</li>"
            for instance in finding.get("instances", [])
        ) or "<li>No affected URLs provided</li>"

        cards += f"""
        <section class="finding">
            <h2>{safe(finding.get('name'))}</h2>

            <p><b>Finding Key:</b> {safe(finding_key)}</p>
            <p><b>Plugin ID:</b> {safe(fid)}</p>
            <p><b>Scanner Severity:</b> {safe(finding.get('severity'))}</p>
            <p><b>ZAP Confidence:</b> {safe(finding.get('confidence'))}</p>

            <p><b>Description:</b><br>
            {safe(finding.get('description'))}</p>

            <h3>Affected URLs</h3>
            <ul>{instances}</ul>

            <h3>Red Agent — Analysis</h3>
            <pre>{safe(red_item.get('analysis', 'Result unavailable'))}</pre>

            <h3>Blue Agent — Recommendations</h3>
            <pre>{safe(blue_item.get('blue_agent_recommendation', 'Result unavailable'))}</pre>

            <h3>Judge Agent — Assessment</h3>
            <pre>{safe(judge_item.get('judge_verdict', 'Result unavailable'))}</pre>

            <h3>OWASP ZAP Suggested Solution</h3>
            <pre>{safe(finding.get('solution'))}</pre>
        </section>
        """

    summary = "".join(
        f"<div class='stat'><b>{severity}</b>"
        f"<strong>{count}</strong></div>"
        for severity, count in severity_counts.items()
    )

    html_report = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>SENTINEL Security Assessment</title>

        <style>
            body {{
                margin: 0;
                padding: 30px;
                background: #0b1120;
                color: #e5e7eb;
                font-family: Arial, sans-serif;
            }}

            .container {{
                max-width: 1100px;
                margin: auto;
            }}

            header {{
                padding: 30px;
                background: #111c32;
                border-radius: 12px;
                border-left: 5px solid #38bdf8;
            }}

            h1, h2 {{ color: #38bdf8; }}
            h3 {{ color: #a5b4fc; }}

            .summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 15px;
                margin: 25px 0;
            }}

            .stat, .finding {{
                background: #111c32;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #26364f;
            }}

            .stat strong {{
                display: block;
                font-size: 28px;
                margin-top: 10px;
            }}

            .finding {{
                margin-bottom: 25px;
                overflow-wrap: anywhere;
            }}

            pre {{
                white-space: pre-wrap;
                overflow-wrap: anywhere;
                background: #080e1a;
                padding: 15px;
                border-radius: 8px;
                line-height: 1.6;
            }}

            .note {{
                color: #fbbf24;
                line-height: 1.6;
            }}

            button {{
                padding: 12px 20px;
                background: #0284c7;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
            }}

            @media print {{
                body {{ background: white; color: black; }}
                .finding, header, .stat {{
                    background: white;
                    color: black;
                    border: 1px solid #ccc;
                    break-inside: avoid;
                }}
                button {{ display: none; }}
                h1, h2, h3 {{ color: black; }}
                pre {{ background: #f2f2f2; color: black; }}
            }}
        </style>
    </head>

    <body>
    <div class="container">

        <header>
            <h1>SENTINEL</h1>
            <h2>AI-Powered Security Assessment Report</h2>

            <p>Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}</p>
            <p>Total Scanner Findings: {len(findings)}</p>
            <p>Fully Matched Agent Results: {matched}/{len(findings)}</p>

            <p class="note">
                AI assessments are advisory and require independent
                verification. Scanner severity does not establish
                exploitability. Successful agent execution does not
                establish assessment accuracy.
            </p>

            <button onclick="window.print()">Print / Save as PDF</button>
        </header>

        <h2>Severity Summary</h2>
        <div class="summary">{summary}</div>

        <h2>Detailed Security Findings</h2>
        {cards}

        <footer>
            <p>SENTINEL | AI Cybersecurity Assessment Platform</p>
            <p>Generated using OWASP ZAP and SENTINEL AI agents.</p>
        </footer>

    </div>
    </body>
    </html>
    """

    OUTPUT_FILE.write_text(html_report, encoding="utf-8")

    print("\n===== SENTINEL REPORT GENERATOR =====")
    print("Total findings:", len(findings))
    print("Fully matched:", matched)
    print("Missing agent matches:", len(findings) - matched)
    print("Report saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    generate_report()
