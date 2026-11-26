import json
from pathlib import Path
from ai.blue_agent import generate_defense

INPUT_FILE = Path("scanner/normalized-findings.json")
RED_FILE = Path("scanner/red-agent-results.json")
OUTPUT_FILE = Path("scanner/blue-agent-results.json")


def run_blue_agent():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        zap_data = json.load(file)

    with open(RED_FILE, "r", encoding="utf-8") as file:
        red_data = json.load(file)

    red_results = {
        item["finding_id"]: item
        for item in red_data.get("results", [])
    }

    findings = zap_data.get("findings", [])
    blue_results = []

    print("\n===== SENTINEL BLUE AGENT =====")
    print("Total findings:", len(findings))

    for index, finding in enumerate(findings, start=1):
        print(f"\n[{index}/{len(findings)}] Reviewing:")
        print(finding.get("name", "Unknown"))

        try:
            red_result = red_results.get(finding.get("plugin_id"), {})

            if red_result.get("status") != "completed":
                raise ValueError("Red Agent analysis unavailable")

            payload = {
                "scanner_evidence": finding,
                "red_agent_assessment": red_result["analysis"]
            }

            analysis = generate_defense(
                json.dumps(payload, indent=2, ensure_ascii=False)
            )

            result = {
                "finding_id": finding.get("plugin_id"),
                "finding_name": finding.get("name"),
                "blue_agent_recommendation": analysis,
                "status": "completed"
            }

        except Exception as error:
            result = {
                "finding_id": finding.get("plugin_id"),
                "finding_name": finding.get("name"),
                "blue_agent_recommendation": None,
                "status": "failed",
                "error": str(error)
            }
            print("Error:", error)

        blue_results.append(result)
        print("Status:", result["status"])

    output_data = {
        "agent": "SENTINEL BLUE AGENT",
        "total_findings": len(findings),
        "successful": sum(1 for x in blue_results if x["status"] == "completed"),
        "failed": sum(1 for x in blue_results if x["status"] == "failed"),
        "results": blue_results
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4, ensure_ascii=False)

    print("\n===== BLUE AGENT SUMMARY =====")
    print("Successful:", output_data["successful"])
    print("Failed:", output_data["failed"])
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    run_blue_agent()
