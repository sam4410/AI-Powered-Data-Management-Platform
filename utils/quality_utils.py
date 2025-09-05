def analyze_schema_quality(schema_info: dict) -> dict:
    missing_fields = []
    type_issues = []
    pk_fk_violations = []

    for table, meta in schema_info.items():
        for col in meta.get("columns", []):
            if not col.get("type"):
                missing_fields.append(f"{table}.{col['name']}")

        # Detect if PK/FK are properly typed (e.g., TEXT/INTEGER mismatch)
        if "foreign_keys" in meta:
            for fk in meta["foreign_keys"]:
                fk_target = fk.get("to_table")
                if fk_target not in schema_info:
                    pk_fk_violations.append(f"{table} → {fk_target} (Missing target table)")

    return {
        "missing_fields": missing_fields,
        "type_issues": type_issues,
        "pk_fk_violations": pk_fk_violations
    }
