import re
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

def format_as_bullet_points(text: str) -> str:
    """Converts multiline text into markdown bullet points."""
    lines = text.strip().splitlines()
    bullets = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("-") or line.startswith("•"):
            bullets.append(f"{line}")
        elif line.startswith("*"):
            bullets.append(f"- {line[1:].strip()}")
        else:
            bullets.append(f"- {line}")
    return "\n".join(bullets)

def extract_clean_markdown(text: str) -> str:
    """
    Extract markdown content from LLM responses, removing 'Final Answer:' and code fences.
    """
    # Remove 'Final Answer:' if present
    text = re.sub(r"Final Answer:\s*", "", text, flags=re.IGNORECASE)

    # Remove code fences if present
    text = re.sub(r"^```[a-z]*\n", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"\n```$", "", text.strip(), flags=re.IGNORECASE)

    return text.strip()
    
def format_metadata_validation(validation_summary: Dict[str, Any], issues_found: List[Dict[str, Any]]) -> str:
    md = ["\n**📋 Validation Summary:**\n"]
    md.append("| Column | Completeness | Unique Values | Duplicates |")
    md.append("|--------|--------------|----------------|------------|")
    for col, stats in validation_summary.items():
        md.append(f"| {col} | {stats.get('completeness', '-'):0.2f} | {stats.get('unique_values', '-')} | {stats.get('duplicates', '-')} |")

    if issues_found:
        md.append("\n**⚠️ Issues Found:**")
        for issue in issues_found:
            md.append(f"- Column `{issue['column']}`: {issue['issue']} (Value: `{issue.get('value')}`, Threshold: `{issue.get('threshold')}`)")

    return "\n".join(md)

def wrap_cataloging_output(
    table_name: str,
    db_url: str,
    lineage: str = "",
    validation: str = "",
    integration: str = ""
) -> str:
    """
    Formats the cataloging phase output for a single table and database into markdown.
    """
    parts = [f"### 📌 Table: `{table_name}` (DB: `{db_url}`)"]

    if lineage:
        parts.append("#### 🔁 Data Lineage")
        parts.append(lineage.strip())

    if validation:
        parts.append("#### 🧪 Metadata Validation")
        parts.append(validation.strip())

    if integration:
        parts.append("#### 🔗 Data Integration Strategy")
        parts.append(integration.strip())

    return "\n\n".join(parts)

