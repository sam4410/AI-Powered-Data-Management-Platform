from utils import sqlite_fix
import os
import streamlit as st
from pathlib import Path
from main import run
from models.data_models import PlatformConfig
from crew import DataManagementCrew
from utils.helpers import setup_logging, create_data_products, extract_schema_info
from utils.report_generator import generate_markdown_summary
from utils.er_generator import generate_er_diagram
from utils.quality_utils import analyze_schema_quality
from utils.report_generator import save_report_as_markdown
from utils.report_templates import create_report_templates
from utils.data_products_loader import load_data_products_config
from crewai.crews.crew_output import CrewOutput
from utils.cataloging_formatter import wrap_cataloging_output
from datetime import datetime, timedelta
from PIL import Image
import base64
import yaml
import shutil
import time
import logging
import json
import json.decoder
from collections.abc import Mapping

setup_logging()
logger = logging.getLogger(__name__)

def simplify_result(result: dict) -> list:
    """
    Flattens the agent output to a list of results per table with optional summary.
    Expected input format:
    {
        "discovery": {
            "results": [...],
            "summary": [...]
        }
    }
    Output:
    [
        {
            "table": "table_name",
            "summary": "markdown",
            "result": {
                "metadata": {...},
                "profiling": {...}
            }
        },
        ...
    ]
    """
    if not isinstance(result, dict):
        return []

    results = result.get("results") or result.get("discovery") or []
    summary = result.get("summary")

    # Ensure results is a list
    if isinstance(results, dict):
        results = [results]

    if not isinstance(results, list):
        return []

    for r in results:
        # Only attach summary if missing
        if not r.get("summary") and summary and isinstance(summary, list):
            table = r.get("table")
            table_summary = next((s for s in summary if s.get("table") == table), None)
            if table_summary:
                # Fallback: Add bullet-style summary if rich summary not available
                r["summary"] = "\n".join(f"- {rec}" for rec in table_summary.get("recommendations", []))

    return results

st.set_page_config(
    page_title="Agentic Data Platform",
    page_icon="🧠",
    layout="wide"
)

# logo_path = Path("assets/logo.png")
# if logo_path.exists():
    # st.image(str(logo_path), width=50)
st.title("🧠 Agentic AI Platform for Data Management")
st.markdown("Use the tabs below to learn about the platform, run pipelines, and view results.")

data_products = load_data_products_config()
selected_dp_name = st.selectbox("📦 Select a Data Product", [dp["name"] for dp in data_products])
active_data_product = next(dp for dp in data_products if dp["name"] == selected_dp_name)
if active_data_product:
    st.session_state["active_data_product"] = active_data_product

TAB_OVERVIEW, TAB_AGENTS, TAB_RUN, TAB_RESULTS, TAB_ER_DIAGRAM, TAB_NL_QUERY, TAB_REPORTS, TAB_DOCS = st.tabs([
    "📚 Overview",
    "👥 Agents",
    "▶️ Run Pipeline",
    "📊 Results",
    "🧬 ER Diagram",
    "💬 Ask in Natural Language",
    "📝 Generate Report",
    "📘 Docs"
])

with TAB_OVERVIEW:
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.header("🏢 Platform Purpose")
        st.markdown("""
        This platform leverages CrewAI agents to automate and orchestrate enterprise data management tasks across multiple databases.

        **Key Features:**
        - Multi-phase pipeline: discovery, cataloging, processing, insights
        - Modular agents with domain-specific goals and tools
        - Visual summaries and markdown reports
        - Multi-database execution and upload support
        """)

        st.header("🛠️ Usage Guide")
        st.markdown("""
        1. **Upload SQLite Database(s)** in the 'Run Pipeline' tab.
        2. Select one or more **databases and a phase** to run.
        3. Click **Execute** to launch the agentic pipeline.
        4. View results in **JSON** and **Markdown** formats in the Results tab.
        5. Post database upload and executing **Run Pipeline** Feature, it automatically generates ER Diagram of entire database(s)
        6. Navigate through platform **Ask in Natural Language** feature to query database(s) in natural language
        7. Checkout **Generate Reports** to build pre-defined reports by data products by report category
        """)

        st.header("🔍 What to Expect")
        st.markdown("""
        - Insightful metadata and lineage discovery
        - Data quality checks and observability
        - Phase-wise execution logs with progress tracking
        - Detailed ER Diagram highlighting relational aspect among tables in database
        - Natural language interface for querying results
        - Pre-defined reports falling into segregated data products. For example, Customer 360 Analytics
        """)

        st.header("🚀 Upcoming Enhancements")
        st.markdown("""
        - Multi-agent parallel execution support
        - Role-based dashboards for business and tech teams
        - Export to PDF and real-time email notifications
        - Agent performance and reliability scoring
        """)

    with col_right:
        st.header("🏢 Agents Flow in Architecture")
        flow_img = Path("assets/agent_flow.png")
        if flow_img.exists():
            st.image(str(flow_img), caption="Agent Interaction Flow")

        st.header("📚 Documentation & Tutorials")
        st.markdown("""
        - [Quickstart Guide](https://your-docs-url.com/quickstart)
        - [Understanding Each Phase](https://your-docs-url.com/phases)
        - [Agents and Tools Explained](https://your-docs-url.com/agents)
        - [Troubleshooting and FAQs](https://your-docs-url.com/help)
        """)

with TAB_AGENTS:
    st.header("👨‍💼 Agent Directory")
    agents_yaml = Path("config/agents.yaml")
    if agents_yaml.exists():
        agents_config = yaml.safe_load(agents_yaml.read_text(encoding="utf-8"))
        for agent_key, agent in agents_config.items():
            with st.expander(f"🧠 {agent['role']}"):
                st.markdown(f"**Goal:** {agent['goal']}")
                st.markdown(f"**Backstory:**\n\n{agent['backstory']}")
                st.markdown(f"**Tools:** {', '.join(agent.get('tools', []))}")
    else:
        st.warning("agents.yaml not found")

with TAB_RUN:
    st.header("▶️ Run Pipeline Phase")
    
    if "uploaded_dbs" not in st.session_state:
        st.session_state["uploaded_dbs"] = []

    uploaded_files = st.file_uploader("Upload SQLite DBs", accept_multiple_files=True, type=["db"])
    upload_dir = Path("uploaded_dbs")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    db_paths = []
    
    if uploaded_files:
        for f in uploaded_files:
            save_path = upload_dir / f.name
            with open(save_path, "wb") as out:
                out.write(f.read())
            if save_path.suffix == ".db":
                full_path = save_path.resolve()
                
                # Check if already uploaded to avoid duplicates
                if not any(db["path"] == str(full_path) for db in st.session_state["uploaded_dbs"]):
                    st.session_state["uploaded_dbs"].append({
                        "name": f.name,
                        "path": str(full_path),
                        "connection_string": f"sqlite:///{full_path}"
                    })
        # Save to session state
        st.success(f"Uploaded {len(uploaded_files)} database(s).")
        
    if st.session_state["uploaded_dbs"]:
        st.markdown("### 📂 Uploaded Databases:")
        for db in st.session_state["uploaded_dbs"]:
            st.write(f"- {db['name']} ({db['path']})")
        
    if st.button("🔄 Reset Uploaded Databases"):
        st.session_state["uploaded_dbs"] = []
        shutil.rmtree("uploaded_dbs", ignore_errors=True)
        st.success("Uploaded DBs reset.")

    db_name_to_info = {db["name"]: db for db in st.session_state.get("uploaded_dbs", [])}
    selected_db_names = st.multiselect("📂 Select Databases", list(db_name_to_info.keys()), default=list(db_name_to_info.keys()))
    selected_dbs = [db_name_to_info[name]["connection_string"] for name in selected_db_names]
    
    selected_phase = st.selectbox("Select Phase", ["All", "Discovery", "Cataloging", "Processing", "Insights"])

    if st.button("🚀 Execute"):
        with st.spinner("Running agentic pipeline..."):
            if not selected_dbs:
                st.error("❌ No valid database selected.")
                st.stop()
            
            # ⚠️ Clear previous summary every time
            summary_path = Path("results/results_summary.md")
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            summary_path.write_text("# Platform Results Summary\n\n", encoding="utf-8")

            config = PlatformConfig()
            config.database_urls = selected_dbs

            crew = DataManagementCrew(config)
            active_product = st.session_state.get("active_data_product", {})
            inputs = {
                "data_product": active_product,
                "config": config.to_dict()
            }

            phases = ["discovery", "cataloging", "processing", "insights"] if selected_phase == "All" else [selected_phase.lower()]
            results = {}
            
            for db in selected_dbs:
                config.database_urls = [db]
                db_label = Path(db.split("///")[-1]).name
                db_results = {}
                
                for p in phases:
                    st.subheader(f"⏳ Running {p.title()} Phase for {db_label}")
                    progress = st.progress(0)
                    for i in range(5):
                        time.sleep(0.1)
                        progress.progress((i + 1) * 20)

                    # === Discovery Phase ===
                    if p == "discovery":
                        discovery_result = crew.run_data_discovery(inputs)
                        db_results["discovery"] = simplify_result(discovery_result)

                        # Store discovery metadata/profiling to pass to cataloging
                        discovery_outputs = discovery_result.get("results", [])
                        metadata_all = [r["result"]["metadata"] for r in discovery_outputs if "result" in r]
                        profiling_all = [r["result"]["profiling"] for r in discovery_outputs if "result" in r]

                        # Attach to inputs for cataloging
                        inputs["discovery_outputs"] = {
                            "metadata": metadata_all,
                            "profiling": profiling_all
                        }

                    # === Cataloging Phase ===
                    elif p == "cataloging":
                        # Use existing discovery outputs if available
                        if "discovery_outputs" not in inputs:
                            st.warning("⚠️ Discovery outputs not found. Cataloging will run independently.")
                        
                        cataloging_result = crew.run_data_cataloging(inputs)
                        st.write("Raw Cataloging Result:", cataloging_result)
                        logger.debug(f"[DEBUG] cataloging_result type: {type(cataloging_result)}")
                        logger.debug(f"[DEBUG] cataloging_result: {cataloging_result}")
                        
                        if isinstance(cataloging_result, list):
                            cataloging_result = cataloging_result[0] if cataloging_result else {}
                        db_results["cataloging"] = simplify_result(cataloging_result)

                        cataloging_md = wrap_cataloging_output(
                            table_name=db_result.get("table_name", "unknown"),
                            db_url=db_url,
                            lineage=db_result.get("lineage", ""),
                            validation=db_result.get("validation", ""),
                            integration=db_result.get("integration", "")
                        )

                        if not cataloging_md.strip():
                            logger.warning("⚠️ Cataloging markdown is empty. Nothing will be written.")
                            st.warning("⚠️ Cataloging phase completed, but no markdown output was generated.")
                        else:
                            try:
                                summary_path = Path("results/results_summary.md")
                                with summary_path.open("a", encoding="utf-8") as f:
                                    f.write("## 🗂️ Cataloging Phase\n\n")
                                    f.write(cataloging_md + "\n")
                                logger.info("✅ Cataloging summary appended to results_summary.md successfully.")
                            except Exception as e:
                                logger.error(f"❌ Failed to write cataloging markdown: {e}")
                                st.error("❌ Could not append cataloging results to the summary markdown file.")

                    # === Processing and Insights (no change) ===
                    else:
                        result = crew.run(phase=p, inputs=inputs)
                        db_results[p] = simplify_result(result)

                results[db_label] = db_results
                
        # After all phases run for all databases:
        with open("results/platform_execution_results.json", "w") as f:
            json.dump(results, f, indent=2)

        # ✅ Set this always, even if only one phase was run
        st.session_state["last_result"] = results

        # ✅ Generate summary markdown if needed
        summary_path = Path("results/results_summary.md")
        if summary_path.exists():
            st.success("✅ Pipeline execution complete")
            st.json(results)
        else:
            st.warning("⚠️ No summary markdown was generated. Check phase output.")

with TAB_RESULTS:
    st.header("📊 Results Summary")
    json_path = Path("results/platform_execution_results.json")
    md_path = Path("results/results_summary.md")

    if json_path.exists():
        try:
            result_data = json.loads(json_path.read_text())
            st.subheader("📝 Markdown Summary")
            if md_path.exists():
                st.markdown(md_path.read_text(encoding="utf-8"), unsafe_allow_html=True)
            else:
                st.info("Summary not available.")
        except json.decoder.JSONDecodeError:
            st.error("❌ The results JSON file is corrupted or incomplete. Please re-run the pipeline.")
    else:
        st.info("No summary generated yet.")
        
    if md_path.exists():
        with open(md_path, "rb") as f:
            st.download_button(
                label="📥 Download Markdown Summary",
                data=f,
                file_name="results_summary.md",
                mime="text/markdown"
            )

with TAB_ER_DIAGRAM:
    st.header("🧬 Entity-Relationship Diagram")

    schema_info = st.session_state.get("last_schema_info", {})
    db_infos = st.session_state.get("last_db_infos", [])

    if not schema_info:
        st.warning("Please run a pipeline or NL query to extract schema first.")
    else:
        try:
            dot = generate_er_diagram(schema_info)

            # Render in Streamlit
            st.graphviz_chart(dot.source)
            
            # Prepare output paths
            output_dir = Path("results")
            output_file = output_dir / "er_diagram"
            
            # Ensure 'results/' is a directory
            if output_file.exists() and output_file.is_file():
                os.remove(output_file)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Render diagram to PNG
            dot.render(filename=output_file.stem, directory=output_dir, format="png", cleanup=True)

            # Download button
            png_path = output_file.with_suffix(".png")
            if png_path.exists():
                with open(png_path, "rb") as f:
                    st.download_button("📥 Download Diagram", f, file_name="er_diagram.png", mime="image/png", key="er_diagram_btn")
            else:
                st.error("❌ Diagram image was not created as expected.")

        except Exception as e:
            st.error(f"❌ Failed to generate ER diagram: {e}")

with TAB_NL_QUERY:
    st.header("💬 Ask a Question in Natural Language")

    # Step 1: Check uploaded databases
    uploaded_dbs = st.session_state.get("uploaded_dbs", [])

    if not uploaded_dbs:
        st.warning("Please upload a database first in the 'Run Pipeline' tab.")
    else:
        # Step 2: Let user select DBs
        selected_db_names = st.multiselect(
            "📂 Select Database(s) for Querying",
            [db["name"] for db in uploaded_dbs],
            default=[db["name"] for db in uploaded_dbs]
        )

        selected_dbs = [db for db in uploaded_dbs if db["name"] in selected_db_names]

        # Step 3: Build schema and db_infos with deduplication
        combined_schema = {}
        db_infos = []
        seen_paths = set()

        for db in selected_dbs:
            abs_path = str(Path(db["path"]).resolve())
            if abs_path in seen_paths:
                continue  # Avoid duplicates

            alias = Path(abs_path).stem
            try:
                partial_schema = extract_schema_info(abs_path, db_alias=alias)
                combined_schema.update(partial_schema)
            except Exception as e:
                st.error(f"❌ Error extracting schema from {db['name']}: {e}")
                logger.error(f"Schema extraction failed for {db['name']}: {e}")
                continue

            db_infos.append({"name": db["name"], "path": abs_path})
            seen_paths.add(abs_path)

        # ✅ Save for ER Diagram tab
        st.session_state["last_schema_info"] = combined_schema
        st.session_state["last_db_infos"] = db_infos

        # Step 4: Preview Schema
        with st.expander("🧬 Preview Database Schema"):
            for table, meta in combined_schema.items():
                col_names = ", ".join([col["name"] for col in meta["columns"]])
                st.markdown(f"**{table}**: {col_names}")

        # Step 5: Accept NL query
        user_query = st.text_input("🔍 Enter your natural language question")

        if st.button("🚀 Run Query"):
            with st.spinner("Running query through the agent..."):
                config = PlatformConfig()
                crew = DataManagementCrew(config)

                if not combined_schema:
                    st.error("❌ No schema could be extracted from the selected databases.")
                    st.stop()

                result = crew.process_natural_language_query(
                    query=user_query,
                    db_infos=db_infos,
                    schema_info=combined_schema
                )

                try:
                    result_obj = json.loads(result) if isinstance(result, str) else result
                    sql = result_obj.get("generated_sql") or result_obj.get("raw_tool_sql") or "-- not found"

                    if sql == "-- not found":
                        raise ValueError("SQL not parsed")

                    left, right = st.columns(2)
                    with left:
                        st.subheader("🧠 Generated SQL")
                        st.code(sql, language="sql")

                    with right:
                        st.subheader("📊 Explanation & Output")
                        st.markdown(result_obj.get("explanation", ""))

                        if "query_result" in result_obj:
                            st.markdown("**📈 Query Output:**")
                            st.dataframe(result_obj["query_result"])
                        else:
                            st.info("No results returned from SQL execution.")

                    st.json(result_obj)

                except Exception as e:
                    st.warning("⚠️ No SQL generated or tool failed.")
                    st.text(str(result))

with TAB_REPORTS:
    st.header("📈 Automated Report Generation")
    st.markdown("""
    Generate actionable, professional-grade reports using your uploaded databases and agentic analysis.
    """)

    # 1. Load report templates once
    from utils.report_templates import create_report_templates
    all_templates = create_report_templates()

    # 2. Identify active data product and its report suite
    active_dp = st.session_state.get("active_data_product", {})
    report_suite_names = active_dp.get("report_suite", [])
    selected_data_product = active_dp.get("name", "N/A")
    data_sources = active_dp.get("data_sources", [])
    st.info(f"📦 Active Data Product: **{selected_data_product}**")

    # 3. Match report_suite names to templates from report_templates
    available_templates = all_templates.get(selected_data_product, [])
    filtered_templates = [tpl for tpl in available_templates if tpl["name"] in report_suite_names]

    if not filtered_templates:
        st.warning("⚠️ No matching report templates found for this data product.")
        
        # Experimental fallback if no templates found
        st.markdown("---")
        st.subheader("🧪 Experimental: Direct Report Generator")

        if not active_dp:
            st.warning("Please select a Data Product to proceed.")
            st.stop()

        report_suite = active_dp.get("report_suite", [])
        selected_report = st.selectbox("📊 Select Report Type", report_suite)
        db_path = st.text_input("🔌 Enter SQLite DB Path", "ecommerce_db.db")
        days_back = st.slider("📅 Days Back", 7, 90, 30)

        logger.debug(f"[TAB_REPORTS] Experimental run for report_type={selected_report}, data_product={active_dp.get('name')}")

        if st.button("🧪 Run Direct Report"):
            with st.spinner("Generating report..."):
                from tools.analytics_tools import ReportGenerationTool
                report_tool = ReportGenerationTool()

                result_json = report_tool._run(
                    report_type=selected_report,
                    data_source=db_path,
                    parameters={
                        "days_back": days_back,
                        "data_sources": data_sources,
                        "data_product": active_dp.get("name")
                    }
                )

                try:
                    report = json.loads(result_json)
                except json.JSONDecodeError:
                    st.error("❌ Failed to parse report JSON.")
                    st.text(result_json)
                    st.stop()

                st.subheader(f"📄 {report['report_title']}")
                st.markdown(f"🕒 Generated on: {report['generation_date']}")
                st.markdown(f"🗂️ Database: `{report['data_source']}`")
                st.markdown(f"📅 Period: {report.get('period', 'N/A')}")

                st.markdown("## 📌 Summary")
                st.markdown(report["data_summary"].get("summary", "No summary provided."))

                for section in report.get("sections", []):
                    st.markdown(f"### 🔹 {section.get('title', 'Untitled Section')}")
                    st.json(section.get("content", {}))

                if report.get("recommendations"):
                    st.markdown("## ✅ Recommendations")
                    for r in report["recommendations"]:
                        st.markdown(f"- {r}")

                st.markdown("## 🔚 Conclusion")
                st.markdown(report.get("conclusion", "No conclusion provided."))

        st.stop()

    # 4. Standard Flow Using Matched Templates
    selected_template = st.selectbox("📄 Select a report template", [r["name"] for r in filtered_templates])
    selected = next((r for r in filtered_templates if r["name"] == selected_template), None)

    with st.expander("⚙️ Optional Parameters"):
        param_period = st.text_input("Period (e.g., last_30_days)", value="last_30_days")
        try:
            days_back = int(param_period.replace("last_", "").replace("_days", ""))
        except:
            days_back = 30

        parameters = {
            "template": selected["name"],
            "days_back": days_back,
            "include_products": True,
            "include_segments": True,
            **selected.get("parameters", {})
        }

    if st.button("🚀 Generate Report"):
        if "uploaded_dbs" not in st.session_state or not st.session_state["uploaded_dbs"]:
            st.warning("Please upload databases in the 'Run Pipeline' tab before generating reports.")
            st.stop()

        db_paths = [db["path"] for db in st.session_state["uploaded_dbs"]]
        data_source = db_paths[0]  # First uploaded DB

        # Build config for crew agent execution
        report_config = {
            "type": selected.get("type", selected["name"].lower().replace(" ", "_")),
            "data_source": data_source,
            "parameters": {
                "queries": selected.get("queries", []),
                "visualizations": selected.get("visualizations", []),
                **parameters,
                "data_product": selected_data_product
            },
            "data_sources": data_sources
        }

        from crew import DataManagementCrew
        crew = DataManagementCrew()

        with st.spinner("Generating report..."):
            report_output = crew.generate_report(report_config=report_config)

            with st.expander("📋 Raw JSON Output"):
                st.text(report_output.raw if hasattr(report_output, "raw") else str(report_output))

            if isinstance(report_output, dict) and "error" in report_output:
                st.error(f"❌ Report generation failed: {report_output['error']}")
                st.json(report_output)
                st.stop()

            if hasattr(report_output, "json_dict") and report_output.json_dict:
                report_data = report_output.json_dict
            elif hasattr(report_output, "raw") and report_output.raw.strip():
                try:
                    report_data = json.loads(report_output.raw.strip())
                except json.JSONDecodeError:
                    st.warning("⚠️ Report output is not JSON. Rendering as Markdown fallback.")
                    st.markdown(report_output.raw)
                    st.stop()
            else:
                st.error("❌ Unexpected or empty CrewOutput")
                st.stop()

            # Ensure fallback values
            report_data["data_source"] = report_data.get("data_source", data_source)
            report_data["generation_date"] = report_data.get("generation_date", datetime.now().strftime("%B %d, %Y"))
            report_data["report_title"] = report_data.get("report_title", selected["name"])

            from utils.report_generator import save_report_as_markdown
            output_file = f"results/{report_config['type']}_report.md"
            md_path = save_report_as_markdown(report_data, output_path=output_file)

            st.success("✅ Report generated successfully!")
            with open(md_path, "r", encoding="utf-8") as f:
                st.markdown(f.read())

            with open(md_path, "rb") as f:
                st.download_button("📥 Download Report", f, file_name=Path(md_path).name, mime="text/markdown", key="report_download")

with TAB_DOCS:
    st.header("📘 Embedded Documentation")
    doc_options = ["Quickstart", "Pipeline Phases", "Agent Directory", "Troubleshooting"]
    selected_doc = st.selectbox("Choose a documentation section:", doc_options)

    doc_path_map = {
        "Quickstart": "docs/quickstart.md",
        "Pipeline Phases": "docs/phases.md",
        "Agent Directory": "docs/agents.md",
        "Troubleshooting": "docs/troubleshooting.md"
    }
    doc_path = Path(doc_path_map[selected_doc])
    if doc_path.exists():
        st.markdown(doc_path.read_text(encoding="utf-8"))
    else:
        st.warning(f"Documentation file not found: {doc_path}")
