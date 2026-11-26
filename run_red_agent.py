
import json
from pathlib import Path

from ai.red_agent import analyze_finding

INPUT_FILE = Path("scanner/normalized-findings.json")
OUTPUT_FILE = Path("scanner/red-agent-results.json")


def run_red_agent():

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    findings = data.get("findings", [])

    if not findings:
        print("No findings available.")
        return

    results = []

    print("\n===== SENTINEL RED AGENT =====")
    print("Total findings:", len(findings))

    for index, finding in enumerate(findings, start=1):

        finding_key = f"{finding.get('plugin_id')}_{index}"

        print(f"\n[{index}/{len(findings)}] Analyzing:")
        print(finding.get("name", "Unknown"))

        try:
            finding_text = json.dumps(
                finding,
                indent=2,
                ensure_ascii=False
            )

            analysis = analyze_finding(finding_text)

            result = {
                "finding_id": finding.get("plugin_id"),
                "finding_key": finding_key,
                "finding_name": finding.get("name"),
                "severity": finding.get("severity"),
                "analysis": analysis,
                "status": "completed"
            }

        except Exception as error:

            result = {
                "finding_id": finding.get("plugin_id"),
                "finding_key": finding_key,
                "finding_name": finding.get("name"),
                "severity": finding.get("severity"),
                "analysis": None,
                "status": "failed",
                "error": str(error)
            }

            print("Analysis failed:", error)

        results.append(result)
        print("Status:", result["status"])

    output_data = {
        "agent": "SENTINEL RED AGENT",
        "total_findings": len(findings),
        "successful": sum(
            1 for item in results
            if item["status"] == "completed"
        ),
        "failed": sum(
            1 for item in results
            if item["status"] == "failed"
        ),
        "results": results
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            output_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n===== RED AGENT SUMMARY =====")
    print("Total:", output_data["total_findings"])
    print("Successful:", output_data["successful"])
    print("Failed:", output_data["failed"])
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    run_red_agent()

