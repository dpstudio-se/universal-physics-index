import argparse
import glob
import json
import os


def audit_repo():
    report = {
        "critical_conflicts": [],
        "missing_files": [],
        "port_conflicts": [],
        "files_scanned": 0,
    }

    # Check critical files
    critical_files = [
        "plugin.schema.json",
        "config/ports.json",
        ".env.example",
        "ARCHITECTURE.md",
    ]

    for f in critical_files:
        if not os.path.exists(f):
            report["missing_files"].append(f)

    # Port conflict check
    try:
        with open("config/ports.json", encoding="utf-8") as f:
            ports = json.load(f).get("ports", {})
            port_values = list(ports.values())
            if len(port_values) != len(set(port_values)):
                report["port_conflicts"].append("Duplicate ports found in config/ports.json")
    except Exception as e:
        report["critical_conflicts"].append(f"Error reading ports.json: {str(e)}")

    # File scan
    for _path in glob.glob("**/*", recursive=True):
        report["files_scanned"] += 1

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="report.json")
    args = parser.parse_args()

    result = audit_repo()
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Audit complete. Report written to {args.output}")
