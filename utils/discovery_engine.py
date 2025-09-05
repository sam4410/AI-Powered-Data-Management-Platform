from utils.discovery_formatter import extract_recommendations

def synthesize_discovery_results(all_metadata, all_profiling):
    summaries = []

    for meta, profile in zip(all_metadata, all_profiling):
        table_name = meta.get("table_name", "Unknown")
        summary = [f"### 📌 Synthesis for Table: `{table_name}`"]

        quality_score = profile.get("table_quality_score", 1.0)
        summary.append(f"- 🔍 **Quality Score:** `{quality_score}`")

        row_count = meta.get("row_count")
        col_count = meta.get("column_count")
        summary.append(f"- 📏 **Rows:** {row_count}, **Columns:** {col_count}")

        if quality_score < 0.8:
            summary.append(f"- ⚠️ **Low quality score:** Check columns with quality < 0.8")
            low_quality_cols = [
                col for col, stats in profile.get("column_quality", {}).items()
                if stats.get("quality_score", 1.0) < 0.8
            ]
            if low_quality_cols:
                summary.append(f"  - 🚨 Columns needing review: `{', '.join(low_quality_cols)}`")

        # Constraint issues from metadata/foundation (if available)
        foundation_issues = meta.get("foundation", {}).get("constraint_issues", {})
        if foundation_issues:
            summary.append("- 🛑 **Constraint Violations:**")
            for k, v in foundation_issues.items():
                summary.append(f"  - {k}: {', '.join(v)}")

        summaries.append("\n".join(summary))

    return "\n\n---\n\n".join(summaries)