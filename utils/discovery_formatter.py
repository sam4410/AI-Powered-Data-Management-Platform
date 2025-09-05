import re
import json
from typing import Dict, Union, Any, List, Optional

def format_recommendations_table(recs: list[dict]) -> str:
    """
    Convert a list of recommendations into a markdown table.
    Each recommendation must have 'Issue' and 'Suggestion' keys.
    """
    if not isinstance(recs, list) or not recs:
        return "_No recommendations available._"

    try:
        lines = ["| Issue | Suggestion |", "|---|---|"]
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            issue = str(rec.get("Issue", "—")).strip()
            suggestion = str(rec.get("Suggestion", "—")).strip()
            lines.append(f"| {issue or '—'} | {suggestion or '—'} |")
        return "\n".join(lines) if len(lines) > 2 else "_No valid recommendations found._"

    except Exception as e:
        logger.warning(f"Error formatting recommendations table: {e}")
        return "_Error formatting recommendations._"

def highlight_low_quality_columns(profiling: dict) -> str:
    """
    Highlight columns with low quality score (< 0.8) from profiling results.
    Returns a markdown-formatted summary.
    """
    if not isinstance(profiling, dict) or not profiling:
        return ""

    column_profiles = profiling.get("column_profiles", {})
    if not isinstance(column_profiles, dict):
        return ""

    flagged_columns = []

    for col_name, col_data in column_profiles.items():
        if not isinstance(col_data, dict):
            continue

        score = col_data.get("quality_score", 1.0)
        try:
            score = float(score)
        except (ValueError, TypeError):
            continue

        if score < 0.8:
            flagged_columns.append({
                "name": col_name,
                "score": round(score, 3),
                "issues": col_data.get("quality_issues", []),
                "recommendations": col_data.get("recommendations", [])
            })

    # If no issues found
    if not flagged_columns:
        return "\n\n✅ All columns have acceptable data quality (≥ 0.8).\n"

    # Markdown table
    lines = [
        "\n\n❗ **Low Quality Columns (Score < 0.8):**\n",
        "| Column | Quality Score | Recommendations |",
        "|---|---|---|"
    ]

    for col in flagged_columns:
        recs = "; ".join(map(str, col["recommendations"])) if col["recommendations"] else "—"
        lines.append(f"| {col['name']} | {col['score']} | {recs} |")

    return "\n".join(lines)

def format_metadata_table(metadata: dict) -> str:
    """Render a clean markdown table from metadata dictionary."""
    if not isinstance(metadata, dict) or not metadata:
        return "_No metadata available._"

    try:
        basic = metadata.get("basic_info", {})
        relationships = metadata.get("relationships", {})

        rows = [
            ["Table Name", metadata.get("table_name", "N/A")],
            ["Row Count", basic.get("row_count", "N/A")],
            ["Column Count", basic.get("column_count", "N/A")],
            ["Estimated Size (MB)", round(basic.get("estimated_size_mb", 0), 2)],
        ]

        # Primary Keys
        if relationships:
            pk_list = relationships.get("primary_keys", [])
            pk_str = ", ".join(pk_list) if pk_list else "❌ Missing"
            rows.append(["Primary Keys", pk_str])

            # Foreign Keys
            fk_hints = relationships.get("foreign_key_hints", [])
            if isinstance(fk_hints, list) and fk_hints:
                fk_str = ", ".join(
                    f"{fk.get('column', '?')} → {fk.get('references_table', '?')}"
                    for fk in fk_hints if isinstance(fk, dict)
                )
                rows.append(["Foreign Keys", fk_str])
            else:
                rows.append(["Foreign Keys", "None"])

        # Markdown Table Output
        header = "| Property | Value |\n|---|---|"
        body = "\n".join(f"| {k} | {v} |" for k, v in rows)
        return f"{header}\n{body}"

    except Exception as e:
        logger.warning(f"Error rendering metadata table: {e}")
        return "_Error rendering metadata._"
    
def format_profiling_table(profiling: dict) -> str:
    """
    Generate a detailed markdown table from profiling results.
    Includes table-level summary and column-level quality metrics.
    """
    if not isinstance(profiling, dict) or not profiling:
        return "_No profiling data available._"

    try:
        # --- Table Summary ---
        summary_rows = [
            ["Total Records", profiling.get("total_records", "N/A")],
            ["Total Columns", profiling.get("total_columns", "N/A")],
            ["Memory Usage (MB)", round(profiling.get("memory_usage_mb", 0), 2)],
            ["Quality Score", profiling.get("table_quality_score", "N/A")],
            ["Business Domain", profiling.get("business_domain", "N/A")],
            ["Criticality", profiling.get("criticality", "N/A")],
        ]

        summary_md = "#### 🔸 Table Summary\n"
        summary_md += "| Metric | Value |\n|---|---|\n"
        summary_md += "\n".join(f"| {k} | {v} |" for k, v in summary_rows)

        # --- Column-Level Profiling ---
        column_profiles = profiling.get("column_profiles", {})
        if isinstance(column_profiles, dict) and column_profiles:
            column_md = "\n\n#### 🔸 Column Quality Metrics\n"
            column_md += "| Column | Type | Quality | Null % | Unique % |\n|---|---|---|---|---|\n"

            for col_name, col_data in column_profiles.items():
                if not isinstance(col_data, dict):
                    continue
                dtype = str(col_data.get("data_type", "N/A"))
                quality = round(col_data.get("quality_score", 0), 3)
                null_pct = round(float(col_data.get("null_percentage", 0)), 2)
                unique_pct = round(float(col_data.get("unique_percentage", 0)), 2)
                column_md += f"| {col_name} | {dtype} | {quality} | {null_pct}% | {unique_pct}% |\n"
        else:
            column_md = "\n\n_Column-level profiling not available._"

        return summary_md + column_md

    except Exception as e:
        logger.warning(f"Error formatting profiling table: {e}")
        return "_Error rendering profiling summary._"

def format_foundation_summary(foundation: dict, as_table: bool = False) -> str:
    """Render foundation diagnostics as bullet list or optional markdown table."""
    if not isinstance(foundation, dict) or not foundation:
        return "_No foundation insights available._"

    def to_table(title: str, rows: list[tuple]) -> str:
        if not rows:
            return ""
        table = [f"**{title}**", "| Property | Value |", "|---|---|"]
        for k, v in rows:
            val = ", ".join(map(str, v)) if isinstance(v, list) else str(v)
            table.append(f"| {k} | {val} |")
        return "\n".join(table)

    lines = []

    # Basic Info
    basic = foundation.get("basic_info", {})
    if basic:
        basic_rows = [
            ("Row Count", basic.get("row_count", "N/A")),
            ("Column Count", basic.get("column_count", "N/A")),
            ("Estimated Size (MB)", round(basic.get("estimated_size_mb", 0), 2)),
        ]
        if as_table:
            lines.append(to_table("Basic Info", basic_rows))
        else:
            lines.extend([
                f"- 🧮 **Row Count:** {basic_rows[0][1]}",
                f"- 🧱 **Column Count:** {basic_rows[1][1]}",
                f"- 💾 **Estimated Size (MB):** {basic_rows[2][1]}"
            ])

    # Relationships
    rel = foundation.get("relationships", {})
    if rel:
        pk = rel.get("primary_keys", [])
        fk = rel.get("foreign_key_hints", [])
        idx = rel.get("indexes", [])

        if as_table:
            lines.append(to_table("Relationships", [
                ("Primary Keys", pk),
                ("Foreign Keys", len(fk)),
                ("Indexes", len(idx))
            ]))
        else:
            lines.append(f"- 🔑 **Primary Keys:** {', '.join(pk) if pk else '❌ Missing'}")
            lines.append(f"- 🔗 **Foreign Keys:** {len(fk)} detected")
            lines.append(f"- 📌 **Indexes:** {len(idx)} defined")

    # Constraint Issues
    constraint_issues = foundation.get("constraint_issues", {})
    if constraint_issues:
        if as_table:
            lines.append(to_table("Constraint Issues", list(constraint_issues.items())))
        else:
            lines.append("- 🚧 **Constraint Issues:**")
            for issue, columns in constraint_issues.items():
                col_str = ", ".join(columns) if isinstance(columns, list) else str(columns)
                lines.append(f"    - {issue}: {col_str}")

    # Naming Violations
    naming_violations = foundation.get("naming_violations", {})
    if naming_violations:
        if as_table:
            lines.append(to_table("Naming Violations", list(naming_violations.items())))
        else:
            lines.append("- 📝 **Naming Violations:**")
            for issue, violations in naming_violations.items():
                violation_str = ", ".join(violations) if isinstance(violations, list) else str(violations)
                lines.append(f"    - {issue}: {violation_str}")

    # Datatype Warnings
    dt_warnings = foundation.get("datatype_warnings", [])
    if dt_warnings:
        if as_table:
            warning_md = "\n".join(f"- ⚠️ {w}" for w in dt_warnings[:5])
            lines.append(f"**Datatype Warnings**\n\n{warning_md}")
        else:
            lines.append("- ⚠️ **Datatype Warnings:**")
            for w in dt_warnings[:3]:
                lines.append(f"    - {w}")
            if len(dt_warnings) > 3:
                lines.append("    - ...")

    # Architecture Findings
    arch_findings = foundation.get("architecture_findings", [])
    if arch_findings:
        if as_table:
            finding_md = "\n".join(f"- 🚨 {f}" for f in arch_findings[:5])
            lines.append(f"**Architectural Findings**\n\n{finding_md}")
        else:
            lines.append("- 🧱 **Architecture Findings:**")
            for f in arch_findings[:3]:
                lines.append(f"    - {f}")
            if len(arch_findings) > 3:
                lines.append("    - ...")

    return "\n\n".join(lines).strip()

def extract_process_mapping_sections(raw_md: str) -> str:
    """
    Attempt to extract key elements from a free-form process mapping output using heuristics.
    Converts loosely structured content into a formatted markdown block.
    """
    try:
        business_processes = re.findall(r"\*\*Customer.*?\*\*: (.*?)\n", raw_md, re.DOTALL)
        recommendations = re.findall(r"(?i)(?:-|\*)\s+(?:recommendation[s]?:)?(.*)", raw_md)
        dependencies = re.findall(r"dependenc(?:y|ies).*?:\s*(.*?)\n", raw_md, re.IGNORECASE)
        bottlenecks = re.findall(r"(?:risk|issue|problem).*?:\s*(.*?)\n", raw_md, re.IGNORECASE)

        bp_str = ", ".join(bp.strip() for bp in business_processes) or "N/A"
        dep_str = ", ".join(dependencies) or "N/A"
        bottle_str = ", ".join(bottlenecks) or "None noted"
        recs = "\n".join(f"  - {r.strip()}" for r in recommendations if len(r.strip()) > 5) or "  - None provided"

        return f"""### 🔄 Process Mapping
Table: `customers`
- 🔄 Business Processes: {bp_str}
- 🔗 Dependencies: {dep_str}
- 🛠 Bottlenecks: {bottle_str}
- 💡 Recommendations:
{recs}
"""
    except Exception as e:
        logger.warning(f"Process mapping extraction failed: {e}")
        return ""

def wrap_discovery_output(
    table_name: str,
    metadata: dict,
    profiling: dict,
    recommendations: list,
    foundation: dict = None,
    process_analysis: str = "",
    ai_recommendations: str = ""
) -> str:
    """
    Render full discovery markdown summary for a single table.
    Ensures each component is safely rendered and formatted, even with partial or malformed inputs.
    """

    # Defensive normalization
    metadata = metadata if isinstance(metadata, dict) else {}
    profiling = profiling if isinstance(profiling, dict) else {}
    foundation = foundation if isinstance(foundation, dict) else {}
    recommendations = recommendations if isinstance(recommendations, list) else []

    # --- Metadata Summary ---
    try:
        metadata_md = format_metadata_table(metadata)
    except Exception as e:
        logger.warning(f"Failed to format metadata for {table_name}: {e}")
        metadata_md = "_No metadata available._"

    # --- Profiling Summary ---
    try:
        profiling_md = format_profiling_table(profiling)
    except Exception as e:
        logger.warning(f"Failed to format profiling for {table_name}: {e}")
        profiling_md = "_No profiling data available._"

    # --- Recommendations ---
    try:
        if callable(globals().get("format_recommendations_table")) and recommendations:
            recommendations_md = format_recommendations_table(recommendations)
        elif recommendations:
            recommendations_md = "\n".join(f"- {r}" for r in recommendations)
        else:
            recommendations_md = "_No valid recommendations found._"
    except Exception as e:
        logger.warning(f"Failed to format recommendations for {table_name}: {e}")
        recommendations_md = "_No valid recommendations found._"

    # --- Foundation Assessment ---
    try:
        foundation_md = f"\n### 🧱 Foundation Assessment\n{format_foundation_summary(foundation)}" if foundation else ""
    except Exception as e:
        logger.warning(f"Failed to format foundation assessment for {table_name}: {e}")
        foundation_md = ""

    # --- Process Understanding ---
    try:
        if process_analysis:
            try:
                if "Table:" in process_analysis and "Business Processes" in process_analysis:
                    process_md = f"\n{process_analysis.strip()}"
                else:
                    process_md = f"\n{extract_process_mapping_sections(process_analysis)}"
            except Exception as e:
                logger.warning(f"Failed to format process mapping for {table_name}: {e}")
                process_md = ""
        else:
            process_md = ""
    except Exception as e:
        logger.warning(f"Failed to format process mapping for {table_name}: {e}")
        process_md = ""

    # --- AI Recommendations ---
    try:
        ai_md = f"\n### 🧠 AI Recommendations\n{ai_recommendations.strip()}" if ai_recommendations else ""
    except Exception as e:
        logger.warning(f"Failed to format AI recommendations for {table_name}: {e}")
        ai_md = ""

    # --- Final Markdown Block ---
    return f"""
## 📁 Table: `{table_name}`

### 🔍 Metadata Summary
{metadata_md}

### 📊 Profiling Summary
{profiling_md}

### ✅ Recommendations
{recommendations_md}
{foundation_md}
{process_md}
{ai_md}
""".strip()

def extract_recommendations(metadata: dict, profiling: dict) -> list:
    recs = []
    
    columns = metadata.get("columns", []) if isinstance(metadata, dict) else []
    profiles = profiling.get("column_profiles", []) if isinstance(profiling, dict) else []

    if not isinstance(columns, list) or not isinstance(profiles, list):
        recs.append("⚠️ Metadata or profiling input is invalid.")
        return recs

    col_types = {col["name"]: col.get("type", "").upper() for col in columns if "name" in col}
    pk_names = {col["name"] for col in columns if col.get("is_primary_key")}
    
    for profile in profiles:
        col = profile.get("column")
        if not col:
            continue

        q_score = profile.get("quality", 1.0)
        null_pct = profile.get("null_percent", 0.0)
        unique_pct = profile.get("unique_percent", 0.0)
        avg_len = profile.get("average_length", 0)
        dtype = col_types.get(col, profile.get("type", "")).upper()

        # 🔹 Missing NOT NULL
        if null_pct > 0.5:
            recs.append(f"Consider enforcing NOT NULL on column `{col}` to improve integrity (currently {null_pct:.1%} nulls).")

        # 🔹 Poor quality
        if q_score < 0.8:
            recs.append(f"Column `{col}` has low quality score ({q_score:.2f}); consider cleansing or auditing.")

        # 🔹 Candidate for indexing
        if 0.8 < unique_pct < 1.0 and dtype.startswith("INT"):
            recs.append(f"Column `{col}` may benefit from indexing due to high uniqueness ({unique_pct:.1%}).")

        # 🔹 Suspicious text fields
        if dtype in ["TEXT", "VARCHAR", "OBJECT"]:
            if avg_len > 100:
                recs.append(f"Column `{col}` contains long text (avg {avg_len} chars); consider truncating or storing externally.")

        # 🔹 PII Detection
        pii_keywords = ["email", "phone", "address", "name", "dob"]
        if any(pii in col.lower() for pii in pii_keywords):
            recs.append(f"Column `{col}` likely contains PII — consider masking or encrypting for compliance.")

    if not pk_names:
        recs.append("Primary key is missing — define one to ensure entity uniqueness.")

    return list(set(recs))

def extract_json_block(text: str) -> Union[Dict, str]:
    try:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            block = match.group(0)
            return json.loads(block)
    except Exception as e:
        print(f"⚠️ Failed to extract JSON block: {e}")

    return {}

def extract_markdown_section(md_text: str) -> str:
    """
    Extracts markdown content that includes table-wise business process mapping,
    starting with '### Table:' headings.
    """
    if not isinstance(md_text, str):
        return ""

    lines = md_text.strip().splitlines()
    relevant_lines = []

    capture = False
    for line in lines:
        if line.strip().startswith("### Table:"):
            capture = True
        if capture:
            relevant_lines.append(line)

    return "\n".join(relevant_lines).strip()