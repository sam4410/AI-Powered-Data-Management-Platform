from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any, Union

def generate_markdown_summary(json_path: str, output_path: str = "results/results_summary.md") -> str:
    """Generate a markdown summary report from platform_execution_results.json"""
    if not Path(json_path).exists():
        return "❌ Results JSON not found."

    with open(json_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    if not isinstance(results, dict):
        raise ValueError("❌ Unexpected results structure: expected dict.")

    lines = [
        "# 📊 Agentic Data Platform Execution Summary",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]

    for db_name, phases in results.items():
        lines.append(f"## 🗄️ Database: `{db_name}`")
        for phase_name, phase_result in phases.items():
            lines.append(f"### 🔹 Phase: `{phase_name.title()}`")

            # If phase result is a list of table outputs (like discovery, cataloging, etc.)
            if isinstance(phase_result, list):
                for entry in phase_result:
                    table = entry.get("table", "unknown")
                    lines.append(f"#### 📋 Table: `{table}`")

                    summary = entry.get("summary")
                    if summary:
                        lines.append(summary.strip())
                    else:
                        lines.append("_No summary available._")
            else:
                lines.append(f"⚠️ Unexpected result format in phase `{phase_name}`.")
            lines.append("---")

    # Save markdown
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_text = "\n".join(lines)

    with output_path.open("w", encoding="utf-8") as f:
        f.write(markdown_text)

    return str(output_path)

def format_section(title: str, content: Union[str, Dict, list]) -> str:
    md = f"\n## {title}\n"
    if isinstance(content, str):
        md += f"\n{content}\n"
    elif isinstance(content, dict):
        for k, v in content.items():
            if isinstance(v, (int, float, str)):
                md += f"- **{k.replace('_', ' ').title()}**: {v}\n"
            elif isinstance(v, list):
                md += f"- **{k.replace('_', ' ').title()}**:\n"
                for item in v:
                    md += f"  - {item}\n"
    elif isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                md += "- " + ", ".join([f"**{k}**: {v}" for k, v in item.items()]) + "\n"
            else:
                md += f"- {item}\n"
    else:
        md += f"\n{str(content)}\n"
    return md

def save_report_as_markdown(report_data: Dict[str, Any], output_path: Union[str, Path]) -> str:
    md = f"# 📝 {report_data.get('report_title', 'Report')}\n"
    md += f"**Generated:** {report_data.get('generation_date', '')}\n"
    md += f"\n**Data Source:** `{report_data.get('data_source', '')}`\n"

    # Data Summary
    summary = report_data.get("data_summary", {})
    if isinstance(summary, dict):
        md += "\n## Executive Summary\n"
        md += f"\n{summary.get('summary', '')}\n"
        metrics = summary.get("metrics", {})
        if metrics:
            md += "\n### Key Metrics\n"
            for k, v in metrics.items():
                md += f"- **{k.replace('_', ' ').title()}**: {v}\n"
    elif isinstance(summary, str):
        md += "\n## Executive Summary\n"
        md += f"\n{summary}\n"

    # Sections
    for section in report_data.get("sections", []):
        title = section.get("title", "Section")
        content = section.get("content", "")
        md += format_section(title, content)

    # Recommendations
    if "recommendations" in report_data:
        md += format_section("Recommendations", report_data["recommendations"])

    # Conclusion
    if "conclusion" in report_data:
        md += format_section("Conclusion", report_data["conclusion"])

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(md.strip(), encoding="utf-8")
    return str(path)