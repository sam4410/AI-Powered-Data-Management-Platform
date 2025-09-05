from graphviz import Digraph

def infer_foreign_keys(schema_info: dict) -> dict:
    for table_name, meta in schema_info.items():
        fk_candidates = []
        for col in meta.get("columns", []):
            col_name = col["name"]
            if col_name.endswith("_id") and str(col.get("primary_key", False)).lower() != "true":
                ref_base = col_name[:-3]
                for candidate_table in schema_info:
                    if candidate_table.endswith(f".{ref_base}") or candidate_table.endswith(f".{ref_base}s"):
                        target_cols = [c["name"] for c in schema_info[candidate_table]["columns"]]
                        if col_name in target_cols or "id" in target_cols or f"{ref_base}_id" in target_cols:
                            fk_candidates.append({
                                "from": col_name,
                                "to_table": candidate_table.split('.')[-1],
                                "to_column": col_name
                            })
                            break
        if "foreign_keys" not in meta:
            meta["foreign_keys"] = []
        meta["foreign_keys"].extend(fk_candidates)
    return schema_info

def generate_er_diagram(schema_info: dict) -> Digraph:
    schema_info = infer_foreign_keys(schema_info)

    dot = Digraph(format='png')
    dot.attr(rankdir='LR', ranksep='1.2', nodesep='1.0', fontsize='12')
    dot.attr('node', shape='record', style='filled', fillcolor='lightyellow')

    db_subgraphs = {}  # Group tables by DB
    table_nodes = {}

    for table_name, table_meta in schema_info.items():
        db_prefix = table_name.split('.')[0]
        short_table = table_name.split('.')[-1]
        fields = []

        fk_columns = {fk['from'] for fk in table_meta.get("foreign_keys", [])}

        for col in table_meta['columns']:
            col_name = col['name']
            col_type = col['type']
            icon = ""
            if str(col.get('primary_key', False)).lower() == "true":
                icon = "🔑"
            elif col_name in fk_columns:
                icon = "🔗"
            col_line = f"{col_name} : {col_type} {icon}".strip()
            fields.append(col_line)

        label = f"{short_table}|{{" + '|'.join(fields) + "}}"

        if db_prefix not in db_subgraphs:
            db_subgraphs[db_prefix] = Digraph(name=f"cluster_{db_prefix}")
            db_subgraphs[db_prefix].attr(label=db_prefix, style='filled', color='lightblue')

        db_subgraphs[db_prefix].node(table_name, label=f"{{{label}}}", shape="record")
        table_nodes[table_name] = table_name

    # Add all subgraphs to main graph
    for subgraph in db_subgraphs.values():
        dot.subgraph(subgraph)

    # Add foreign key edges
    for table_name, table_meta in schema_info.items():
        for fk in table_meta.get("foreign_keys", []):
            to_table = fk.get("to_table")
            to_table_full = next((t for t in schema_info if t.endswith(f".{to_table}")), None)
            if to_table_full:
                dot.edge(
                    table_name,
                    to_table_full,
                    label=f"{fk['from']} → {fk['to_column']} (1:N)",
                    fontsize="10",
                    color="gray",
                    arrowhead="normal"
                )
                
    # Group relationships and metadata per database
    db_relationships = {}  # db_prefix -> list of relationships
    db_stats = {}          # db_prefix -> (table_count, fk_count)

    for table_name, table_meta in schema_info.items():
        db_prefix = table_name.split('.')[0]
        short_table = table_name.split('.')[-1]
        db_relationships.setdefault(db_prefix, [])
        db_stats.setdefault(db_prefix, {"tables": 0, "fks": 0})
        db_stats[db_prefix]["tables"] += 1

        for fk in table_meta.get("foreign_keys", []):
            rel = f"{short_table} → {fk['to_table']} via {fk['from']}"
            db_relationships[db_prefix].append(rel)
            db_stats[db_prefix]["fks"] += 1

    # Add a summary note per database
    for db_prefix, relationships in db_relationships.items():
        stats = db_stats[db_prefix]
        summary_lines = [
            f"📦 Database: {db_prefix}",
            f"📊 Tables: {stats['tables']} | 🔗 Foreign Keys: {stats['fks']}",
            "🧩 Relationships:"
        ] + [f"- {r}" for r in relationships]

        summary_label = "\\l".join(summary_lines) + "\\l"

        # Create subgraph for summary to isolate layout
        legend_graph = Digraph(name=f"cluster_{db_prefix}_summary")
        legend_graph.attr(label=f"{db_prefix} Summary", style="filled,dashed", color="gray95")
        legend_graph.attr('node', fontcolor='black', fontname='Courier New')
        legend_graph.node(f"{db_prefix}_legend", label=summary_label, shape="note", fontsize="10",
                          style="filled", fillcolor="lightgray", fontname="monospace")
        dot.subgraph(legend_graph)

        # Optional dotted edge to anchor legend visually
        any_table = next((t for t in schema_info if t.startswith(f"{db_prefix}.")), None)
        if any_table:
            dot.edge(f"{db_prefix}_legend", any_table, style="dotted", arrowhead="none")
    
    return dot
