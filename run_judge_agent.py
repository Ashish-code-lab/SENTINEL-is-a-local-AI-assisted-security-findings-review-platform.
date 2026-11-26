
import json
from pathlib import Path
from ai.judge_agent import judge_finding

INPUT_FILE = Path("scanner/normalized-findings.json")
RED_FILE = Path("scanner/red-agent-results.json")
BLUE_FILE = Path("scanner/blue-agent-results.json")
OUTPUT_FILE = Path("scanner/judge-agent-results.json")


def run_judge_agent():

    with open(INPUT_FILE, encoding="utf-8") as f:
        zap_data = json.load(f)

    with open(RED_FILE, encoding="utf-8") as f:
        red_data = json.load(f)

    with open(BLUE_FILE, encoding="utf-8") as f:
        blue_data = json.load(f)

    findings = zap_data.get("findings", [])
    red_list = red_data.get("results", [])
    blue_list = blue_data.get("results", [])

    # Match by unique key, with index fallback for older files
    red_results = {
        item.get("finding_key", f"{item.get('finding_id')}_{i}"): item
        for i, item in enumerate(red_list, start=1)
    }

    blue_results = {
        item.get("finding_key", f"{item.get('finding_id')}_{i}"): item
        for i, item in enumerate(blue_list, start=1)
    }

    judge_results = []

    print("\n===== SENTINEL JUDGE AGENT =====")
    print("Total findings:", len(findings))

    for index, finding in enumerate(findings, start=1):

        finding_id = finding.get("plugin_id")
        finding_key = f"{finding_id}_{index}"

        print(f"\n[{index}/{len(findings)}] {finding.get('name')}")

        try:
            red = red_results.get(finding_key, {})
            blue = blue_results.get(finding_key, {})

            if red.get("status") != "completed":
                raise ValueError("Red Agent report unavailable")

            if blue.get("status") != "completed":
                raise ValueError("Blue Agent report unavailable")

            verdict = judge_finding(
                json.dumps(finding, indent=2, ensure_ascii=False),
                red.get("analysis", ""),
                blue.get("blue_agent_recommendation", "")
            )

            result = {
                "finding_id": finding_id,
                "finding_key": finding_key,
                "finding_name": finding.get("name"),
                "judge_verdict": verdict,
                "status": "completed"
            }

        except Exception as error:
            result = {
                "finding_id": finding_id,
                "finding_key": finding_key,
                "finding_name": finding.get("name"),
                "judge_verdict": None,
                "status": "failed",
                "error": str(error)
            }
            print("Error:", error)

        judge_results.append(result)
        print("Status:", result["status"])

    output_data = {
        "agent": "SENTINEL JUDGE AGENT",
        "total_findings": len(findings),
        "successful": sum(
            x["status"] == "completed" for x in judge_results
        ),
        "failed": sum(
            x["status"] == "failed" for x in judge_results
        ),
        "results": judge_results
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    print("\n===== JUDGE AGENT SUMMARY =====")
    print("Total:", output_data["total_findings"])
    print("Successful:", output_data["successful"])
    print("Failed:", output_data["failed"])
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    run_judge_agent()
