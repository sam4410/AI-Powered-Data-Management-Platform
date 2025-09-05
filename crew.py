"""
crew.py
Crew orchestration for the Agentic Data Management Platform
"""
from crewai.tools import BaseTool
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from crewai import Agent, Task, Crew, Process
from tools.safe_file_read_tool import SafeFileReadTool
from tools.safe_directory_read_tool import SafeDirectoryReadTool
from utils.report_generator import save_report_as_markdown
from utils.data_products_loader import load_data_products_config
from utils.report_templates import create_report_templates
from utils.discovery_engine import synthesize_discovery_results
from utils.path_utils import sanitize_connection_string
from utils.discovery_formatter import extract_json_block, extract_recommendations, wrap_discovery_output, extract_markdown_section
from utils.helpers import setup_logging
from langchain.tools import Tool
from datetime import datetime, timedelta
import sqlite3
import json
import re
from dotenv import load_dotenv
load_dotenv(override=True)

# Import custom tools with error handling
try:
    from tools.database_tools import DatabaseConnectionTool, MetadataExtractionTool
    from tools.data_tools import DataProfilingTool, DataValidationTool
    from tools.analytics_tools import CrewText2SQLTool, ReportGenerationTool
except ImportError as e:
    logging.warning(f"Could not import custom tools: {e}")

from models.data_models import PlatformConfig
from utils.helpers import load_yaml_config

setup_logging(log_level="DEBUG")
logger = logging.getLogger(__name__)
logger.debug("Logging is configured and active.")

class DataManagementCrew:
    """Main crew orchestrator for data management operations"""
    logger.debug("DataManagementCrew initialized")
    
    def __init__(self, config: Optional[PlatformConfig] = None):
        self.config = config or self._get_default_config()
        self.agents_config = self._load_agents_config()
        self.tasks_config = self._load_tasks_config()
        self.tools = self._initialize_tools()
    
    def _get_default_config(self) -> PlatformConfig:
        """Get default configuration if none provided"""
        try:
            return PlatformConfig()
        except Exception as e:
            logger.warning(f"Could not load default config: {e}")
            return None
    
    def _load_agents_config(self) -> Dict[str, Any]:
        """Load agents configuration with fallback"""
        try:
            return load_yaml_config("config/agents.yaml")
        except Exception as e:
            logger.warning(f"Could not load agents config: {e}")
            return self._get_default_agents_config()
    
    def _load_tasks_config(self) -> Dict[str, Any]:
        """Load tasks configuration with fallback"""
        try:
            return load_yaml_config("config/tasks.yaml")
        except Exception as e:
            logger.warning(f"Could not load tasks config: {e}")
            return self._get_default_tasks_config()
        
    def _initialize_tools(self) -> Dict[str, Any]:
        tools = {}

        try:
            tools.update({
                "file_read": SafeFileReadTool(),
                "directory_search": SafeDirectoryReadTool()
            })
            logger.debug("Basic tools initialized")
        except Exception as e:
            logger.error(f"Error initializing basic tools: {e}")

        try:
            text2sql_tool = CrewText2SQLTool()
            report_templates = create_report_templates()
            data_products = load_data_products_config()
            data_product_reports = {
                dp["name"]: dp["report_suite"]
                for dp in data_products
            }

            report_generation_tool = ReportGenerationTool(
                report_templates=report_templates,
                data_product_reports=data_product_reports
            )

            tools.update({
                "database_connection": DatabaseConnectionTool(),
                "metadata_extraction": MetadataExtractionTool(),
                "data_profiling": DataProfilingTool(),
                "data_validation": DataValidationTool(),
                "text2sql": text2sql_tool,
                "report_generation": report_generation_tool
            })
            logger.debug(f"Custom tools initialized: {list(tools.keys())}")
        except Exception as e:
            logger.warning(f"Custom tools not available: {e}")

        return tools
    
    def _create_agent_from_config(self, agent_name: str) -> Agent:
        """Create agent from configuration"""
        try:
            agent_config = self.agents_config[agent_name]
            
            # Get tools for this agent
            agent_tools = []
            for tool_name in agent_config.get("tools", []):
                if tool_name in self.tools:
                    agent_tools.append(self.tools[tool_name])
                else:
                    logger.warning(f"Tool '{tool_name}' not found in self.tools and will be skipped for agent '{agent_name}'")
            
            # If no tools available, use basic tools
            if not agent_tools and self.tools:
                agent_tools = [self.tools.get("file_read"), self.tools.get("directory_search")]
                agent_tools = [tool for tool in agent_tools if tool is not None]
            
            return Agent(
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=agent_config["backstory"],
                tools=agent_tools,
                verbose=agent_config.get("verbose", True),
                allow_delegation=agent_config.get("allow_delegation", False)
            )
        except Exception as e:
            logger.error(f"Error creating agent {agent_name}: {e}")
            # Return a basic agent as fallback
            return Agent(
                role=f"Generic {agent_name.replace('_', ' ').title()}",
                goal="Perform data management tasks",
                backstory="I am a data management specialist.",
                tools=[],  # No tools to avoid validation errors
                verbose=True,
                allow_delegation=False
            )
    
    def _create_task_from_config(self, task_name: str, agent: Agent, inputs: Dict[str, Any]) -> Task:
        """Create task from configuration"""
        try:
            task_config = self.tasks_config[task_name]
            
            # Format description with inputs - handle missing keys gracefully
            description = task_config["description"]
            try:
                description = description.format(**inputs)
            except (KeyError, ValueError) as e:
                logger.warning(f"Could not format task description for {task_name}: {e}")
                # Use description as-is if formatting fails
            
            return Task(
                description=description,
                agent=agent,
                expected_output=task_config["expected_output"],
                output_file=task_config["output_file"]
            )
        except Exception as e:
            logger.error(f"Error creating task {task_name}: {e}")
            # Return a basic task as fallback
            return Task(
                description=f"Perform {task_name.replace('_', ' ')} task with given inputs: {inputs}",
                agent=agent,
                expected_output="Completed task results and analysis"
            )
    
    def run_data_discovery(self, inputs: Dict[str, Any] = None) -> Any:
        logger.info("Initializing Data Discovery...")
        if inputs is None:
            inputs = {}

        data_product = inputs.get("data_product", {})
        data_sources = data_product.get("data_sources", [])

        results = []
        all_metadata = []
        all_profiling = []

        summary_path = Path("results/results_summary.md")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        if not summary_path.exists() or summary_path.read_text(encoding="utf-8").strip() == "":
            summary_path.write_text("# Platform Results Summary\n\n", encoding="utf-8")

        with summary_path.open("a", encoding="utf-8") as f:
            f.write("## 🔎 Discovery Phase\n\n")

        for db_url in self.config.database_urls:
            db_url = sanitize_connection_string(db_url)
            if not db_url:
                logger.warning(f"Skipping invalid connection string: {db_url}")
                continue

            logger.info(f"Running discovery for DB: {db_url}")

            for table_name in data_sources:
                logger.info(f"Executing for table: {table_name}")
                metadata = {}
                profiling = {}
                foundation_parsed = {}
                process_analysis = ""
                recommendation_md = ""
                formatted_md = ""

                db_inputs = {
                    **inputs,
                    "config": {**inputs.get("config", {}), "database_url": db_url},
                    "connection_string": db_url,
                    "table_name": table_name,
                    "allowed_tables": [table_name],
                    "include_sample_data": False,
                    "max_sample_size": 1000
                }

                try:
                    # --- Step 1: Research Agent ---
                    research_agent = self._create_agent_from_config("data_research_agent")
                    research_task = self._create_task_from_config("data_research_task", research_agent, db_inputs)
                    research_crew = Crew(agents=[research_agent], tasks=[research_task], process=Process.sequential, verbose=True)
                    research_result = research_crew.kickoff()
                    research_raw_result = research_result.get("raw") if isinstance(research_result, dict) else str(research_result)
                    logger.debug(f"Raw research agent result (first 1K chars):\n{research_raw_result[:1000]}")

                    parsed_result = extract_json_block(research_raw_result)
                    if isinstance(parsed_result, str):
                        try:
                            parsed_result = json.loads(parsed_result)
                        except Exception as e:
                            logger.error(f"Failed to parse JSON from research result: {e}")
                            parsed_result = {}

                    metadata = parsed_result.get("metadata", {}) if isinstance(parsed_result, dict) else {}
                    profiling = parsed_result.get("profiling", {}) if isinstance(parsed_result, dict) else {}

                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except Exception:
                            logger.warning(f"Metadata is not valid JSON for {table_name}.")
                            metadata = {}

                    if isinstance(profiling, str):
                        try:
                            profiling = json.loads(profiling)
                        except Exception:
                            logger.warning(f"Profiling is not valid JSON for {table_name}.")
                            profiling = {}

                    # --- Step 2: Foundation Setup Agent ---
                    foundation_agent = self._create_agent_from_config("data_foundation_setup_agent")
                    foundation_task = self._create_task_from_config("foundation_setup_task", foundation_agent, db_inputs)
                    foundation_crew = Crew(agents=[foundation_agent], tasks=[foundation_task], process=Process.sequential, verbose=True)
                    foundation_result = foundation_crew.kickoff()
                    foundation_raw_result = foundation_result.get("raw") if isinstance(foundation_result, dict) else str(foundation_result)
                    logger.debug(f"Raw foundation agent result (first 1K chars):\n{foundation_raw_result[:1000]}")

                    try:
                        foundation_parsed = extract_json_block(foundation_raw_result)
                        if isinstance(foundation_parsed, str):
                            foundation_parsed = json.loads(foundation_parsed)
                        if isinstance(foundation_parsed, dict):
                            foundation_table_data = foundation_parsed.get(table_name) or foundation_parsed.get(table_name.lower())
                            if isinstance(foundation_table_data, dict):
                                foundation_parsed = foundation_table_data
                    except Exception as e:
                        logger.warning(f"Could not parse foundation setup result for {table_name}: {e}")
                        foundation_parsed = {}

                    # --- Step 3: Process Understanding Agent ---
                    process_inputs = {
                        **inputs,
                        "config": db_inputs.get("config", {}),
                        "connection_string": db_url,
                        "table_name": table_name,
                        "allowed_tables": data_sources,
                        "data_sources": data_sources,
                        "metadata": metadata,
                        "profiling": profiling
                    }

                    process_agent = self._create_agent_from_config("process_understanding_agent")
                    process_task = self._create_task_from_config("process_understanding_task", process_agent, process_inputs)
                    process_crew = Crew(agents=[process_agent], tasks=[process_task], process=Process.sequential, verbose=True)
                    process_result = process_crew.kickoff()
                    logger.debug(f"[process_understanding] Raw result:\n{process_result}")
                    process_raw_result = process_result.get("raw") if isinstance(process_result, dict) else str(process_result)
                    logger.debug(f"Raw process agent result (first 1K chars):\n{process_raw_result[:1000]}")

                    try:
                        if isinstance(process_raw_result, str) and "### 🔄 Process Mapping" in process_raw_result:
                            process_analysis = extract_markdown_section(process_raw_result)
                        elif isinstance(process_raw_result, str):
                            logger.warning("Expected markdown header missing. Using full output as fallback.")
                            process_analysis = process_raw_result.strip()
                        else:
                            process_analysis = ""
                    except Exception as e:
                        logger.warning(f"Could not parse process understanding result for {table_name}: {e}")
                        process_analysis = ""

                    # --- Step 4: Governance Recommendations ---
                    try:
                        governance_agent = self._create_agent_from_config("data_governance_recommender_agent")
                        rec_inputs = {
                            **db_inputs,
                            "metadata": metadata,
                            "profiling": profiling,
                            "foundation": foundation_parsed
                        }
                        rec_task = self._create_task_from_config("data_recommendation_task", governance_agent, rec_inputs)
                        rec_crew = Crew(agents=[governance_agent], tasks=[rec_task], process=Process.sequential, verbose=True)
                        rec_result = rec_crew.kickoff()
                        recommendation_md = rec_result.get("raw") if isinstance(rec_result, dict) else str(rec_result)
                        logger.debug(f"AI Governance Recommendations:\n{recommendation_md[:1000]}")
                    except Exception as e:
                        logger.warning(f"Could not generate governance recommendations for table {table_name}: {e}")
                        recommendation_md = ""

                    # --- Step 5: Markdown Output ---
                    try:
                        rule_based_recs = extract_recommendations(metadata or {}, profiling or [])
                        ai_recommendations_md = recommendation_md.strip() if isinstance(recommendation_md, str) else ""

                        formatted_md = wrap_discovery_output(
                            table_name=table_name,
                            metadata=metadata,
                            profiling=profiling,
                            recommendations=rule_based_recs,
                            foundation=foundation_parsed,
                            process_analysis=process_analysis,
                            ai_recommendations=ai_recommendations_md
                        )

                        with summary_path.open("a", encoding="utf-8") as f:
                            f.write(formatted_md + "\n\n")

                        results.append({
                            "db": db_url,
                            "table": table_name,
                            "result": {
                                "metadata": metadata,
                                "profiling": profiling
                            },
                            "summary": formatted_md,
                            "recommendations": rule_based_recs
                        })

                        if metadata:
                            all_metadata.append(metadata)
                        if profiling:
                            all_profiling.append(profiling)

                    except Exception as e:
                        logger.error(f"Failed to format/save discovery output for {table_name}: {e}")
                        results.append({
                            "db": db_url,
                            "table": table_name,
                            "error": str(e),
                            "result": {
                                "metadata": {},
                                "profiling": {}
                            },
                            "summary": ""
                        })

                except Exception as e:
                    logger.error(f"Error processing table {table_name}: {e}")
                    results.append({
                        "db": db_url,
                        "table": table_name,
                        "error": str(e),
                        "result": {
                            "metadata": {},
                            "profiling": {}
                        },
                        "summary": ""
                    })

        # Final synthesis
        try:
            if all_metadata or all_profiling:
                from utils.discovery_engine import synthesize_discovery_results
                final_summary = synthesize_discovery_results(all_metadata, all_profiling)
                logger.info("Final discovery synthesis complete.")
                return {"results": results, "summary": final_summary}
            else:
                logger.warning("No metadata or profiling outputs found for final synthesis.")
                return {"results": results}
        except Exception as e:
            logger.error(f"Final synthesis failed: {e}")
            return {"results": results}
    
    def run_data_cataloging(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info("Initializing Multi-DB Data Cataloging...")
        if inputs is None:
            inputs = {}

        data_product = inputs.get("data_product", {})
        data_sources = data_product.get("data_sources", [])
        results = []

        summary_path = Path("results/results_summary.md")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        if not summary_path.exists() or summary_path.read_text(encoding="utf-8").strip() == "":
            summary_path.write_text("# Platform Results Summary\n\n", encoding="utf-8")

        with summary_path.open("a", encoding="utf-8") as f:
            f.write("## 🗂️ Cataloging Phase\n\n")

        for db_url in self.config.database_urls:
            db_url = sanitize_connection_string(db_url)
            if not db_url:
                logger.warning(f"Skipping invalid connection string: {db_url}")
                continue

            logger.info(f"Running cataloging for DB: {db_url}")

            for table_name in data_sources:
                logger.info(f"Cataloging for table: {table_name}")

                db_inputs = {
                    **inputs,
                    "config": {**inputs.get("config", {}), "database_url": db_url},
                    "connection_string": db_url,
                    "table_name": table_name,
                    "allowed_tables": [table_name],
                    "include_sample_data": False,
                    "max_sample_size": 1000
                }

                try:
                    # Create agents
                    lineage_agent = self._create_agent_from_config("data_lineage_agent")
                    metadata_agent = self._create_agent_from_config("metadata_validation_agent")
                    integration_agent = self._create_agent_from_config("data_integration_agent")

                    # Create tasks
                    lineage_task = self._create_task_from_config("data_lineage_task", lineage_agent, db_inputs)
                    metadata_task = self._create_task_from_config("metadata_validation_task", metadata_agent, db_inputs)
                    integration_task = self._create_task_from_config("data_integration_task", integration_agent, db_inputs)

                    # Run crew
                    crew = Crew(
                        agents=[lineage_agent, metadata_agent, integration_agent],
                        tasks=[lineage_task, metadata_task, integration_task],
                        process=Process.sequential,
                        verbose=True
                    )

                    result = crew.kickoff()

                    if isinstance(result, dict):
                        lineage_result = result.get("lineage", "")
                        validation_result = result.get("validation", "")
                        integration_result = result.get("integration", "")
                    elif hasattr(result, "raw_output") and isinstance(result.raw_output, list):
                        lineage_result = result.raw_output[0] if len(result.raw_output) > 0 else ""
                        validation_result = result.raw_output[1] if len(result.raw_output) > 1 else ""
                        integration_result = result.raw_output[2] if len(result.raw_output) > 2 else ""
                    else:
                        lineage_result = validation_result = integration_result = ""

                    # Format Markdown output
                    try:
                        summary_md = wrap_cataloging_output(
                            table_name=table_name,
                            lineage=lineage_result,
                            validation=validation_result,
                            integration=integration_result
                        )

                        with summary_path.open("a", encoding="utf-8") as f:
                            f.write(summary_md + "\n\n")

                    except Exception as e:
                        logger.warning(f"⚠️ Failed to write markdown for table {table_name}: {e}")
                        summary_md = ""

                    results.append({
                        "db": db_url,
                        "table": table_name,
                        "lineage": lineage_result,
                        "validation": validation_result,
                        "integration": integration_result,
                        "summary": summary_md
                    })

                except Exception as e:
                    logger.error(f"❌ Error in cataloging for {db_url}, table {table_name}: {e}")
                    results.append({
                        "db": db_url,
                        "table": table_name,
                        "lineage": "",
                        "validation": "",
                        "integration": "",
                        "summary": "",
                        "error": str(e)
                    })

        return {"results": results}
    
    def run_data_processing(self, inputs: Dict[str, Any] = None) -> Any:
        logger.info("Initializing Data Processing...")
        if inputs is None:
            inputs = {}
            
        data_product = inputs.get("data_product", {})
        data_sources = data_product.get("data_sources", [])
        
        results = []
        for db_url in self.config.database_urls:
            logger.info(f"Running processing for DB: {db_url}")
            
            db_inputs = {
                **inputs,
                "config": {**inputs.get("config", {}), "database_url": db_url},
                "data_sources": data_sources  # ✅ Inject filter
            }
        
            try:
                # Create agents
                quality_agent = self._create_agent_from_config("data_quality_agent")
                observability_agent = self._create_agent_from_config("data_observability_agent")
                performance_agent = self._create_agent_from_config("performance_tuning_agent")
                
                # Create tasks
                quality_task = self._create_task_from_config("data_quality_task", quality_agent, db_inputs)
                observability_task = self._create_task_from_config("data_observability_task", observability_agent, db_inputs)
                performance_task = self._create_task_from_config("performance_tuning_task", performance_agent, db_inputs)
                
                # Create and run crew
                crew = Crew(
                    agents=[quality_agent, observability_agent, performance_agent],
                    tasks=[quality_task, observability_task, performance_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                db_result = crew.kickoff()
                results.append({"db": db_url, "result": db_result})
            except Exception as e:
                logger.error(f"Error in data processing for {db_url}: {e}")
                results.append({"db": db_url, "error": str(e)})
        return results
    
    def run_insights_generation(self, inputs: Dict[str, Any] = None) -> Any:
        logger.info("Initializing Insight Generation...")
        if inputs is None:
            inputs = {}
            
        data_product = inputs.get("data_product", {})
        data_sources = data_product.get("data_sources", [])
            
        results = []
        for db_url in self.config.database_urls:
            logger.info(f"Running processing for DB: {db_url}")
            
            db_inputs = {
                **inputs,
                "config": {**inputs.get("config", {}), "database_url": db_url},
                "data_sources": data_sources  # ✅ Inject filter
            }
        
            try:
                # Create agents
                text2sql_agent = self._create_agent_from_config("text2sql_agent")
                caching_agent = self._create_agent_from_config("caching_agent")
                reports_agent = self._create_agent_from_config("reports_generation_agent")
                
                # Create tasks
                text2sql_task = self._create_task_from_config("text2sql_task", text2sql_agent, db_inputs)
                caching_task = self._create_task_from_config("caching_task", caching_agent, db_inputs)
                reports_task = self._create_task_from_config("reports_generation_task", reports_agent, db_inputs)
                
                # Create and run crew
                crew = Crew(
                    agents=[text2sql_agent, caching_agent, reports_agent],
                    tasks=[text2sql_task, caching_task, reports_task],
                    process=Process.sequential,
                    verbose=True
                )
                
                db_result = crew.kickoff()
                results.append({"db": db_url, "result": db_result})
            except Exception as e:
                logger.error(f"Error in data processing for {db_url}: {e}")
                results.append({"db": db_url, "error": str(e)})
        return results
        
    def run(self, phase: str = "discovery", inputs: Dict[str, Any] = None) -> Any:
        """
        Main run method that can execute different phases
        This is the method that main.py will call
        """
        logger.info(f"Starting Data Management Crew - Phase: {phase}")

        if inputs is None:
            inputs = {}

        # CLEANUP: Remove old summary markdowns before fresh run
        summary_files = [
            "discovery_summary.md",
            "cataloging_summary.md",
            "processing_summary.md",
            "insights_summary.md",
            "results_summary.md"
        ]
        for name in summary_files:
            path = Path("results") / name
            if path.exists():
                logger.debug(f"🧹 Removing old summary file: {path}")
                path.unlink()

        # 🚀 Run selected phase
        phase_methods = {
            "discovery": self.run_data_discovery,
            "cataloging": self.run_data_cataloging,
            "processing": self.run_data_processing,
            "insights": self.run_insights_generation
        }

        method = phase_methods.get(phase.lower(), self.run_data_discovery)
        result = method(inputs)

        # 🧩 Generate combined summary only if any phase summary exists
        combined_summary = ""
        for name in ["discovery", "cataloging", "processing", "insights"]:
            path = Path(f"results/{name}_summary.md")
            if path.exists():
                combined_summary += f"# {name.title()} Phase\n\n"
                combined_summary += path.read_text(encoding="utf-8") + "\n\n"

        if combined_summary.strip():
            Path("results/results_summary.md").write_text(combined_summary, encoding="utf-8")

        return result
    
    def process_natural_language_query(self, query: str, db_infos: List[Dict[str, str]], schema_info: dict = None) -> Any:
        """Use text2sql agent to convert a natural query into SQL, execute and return results"""
        try:
            if not schema_info:
                try:
                    logger.info("📦 Auto-extracting schema_info from DB files...")
                    schema_info = extract_schema_info(db_infos[0]["path"])
                    logger.info(f"Extracted schema for tables: {list(schema_info.keys())}")
                except Exception as e:
                    logger.error(f"Failed to auto-extract schema_info: {e}")
                    return {"error": f"Failed to extract schema_info: {e}", "query": query}

            text2sql_agent = self._create_agent_from_config("text2sql_agent")
            available_tables = "\n".join(f"- {table}" for table in schema_info.keys())

            query_task = Task(
                description=f"""
    You are a SQL expert agent. Your task is to convert the user's natural language question into a valid SQL query.

    ## Question:
    {query}

    ## Available Database Schema:
    {self._format_schema_for_agent(schema_info)}

    ## Available tables
    {available_tables}

    ## Instructions:
    - Use only the schema and database files already provided via inputs.
    - You MUST invoke the `Text to SQL Tool` to answer.
    - You MUST fully qualify table names using the format: `database_name.table_name`(e.g., `customer_db.customers`, `transaction_logs.transactions`)
    - Do NOT guess table names or columns — use only tables listed in the provided schema_info.
    - Ensure correct joins by checking foreign key relationships in the schema.
    - Only process tables listed in `data_sources`
    - Do not profile or validate other tables

    You MUST use the Text to SQL Tool to generate the SQL query.
                """,
                agent=text2sql_agent,
                expected_output="SQL query with explanation and results",
                tools=[self.tools["text2sql"]]
            )

            crew = Crew(
                agents=[text2sql_agent],
                tasks=[query_task],
                process=Process.sequential,
                verbose=False
            )

            logger.info("Running Text2SQL crew...")
            agent_output = crew.kickoff()

            if not hasattr(agent_output, 'result') or not agent_output.result:
                logger.info("🔧 Agent didn't generate proper output, calling tool directly...")
                text2sql_tool = self.tools["text2sql"]
                tool_result = text2sql_tool._run(
                    natural_language_query=query,
                    schema_info=schema_info,
                    db_files=db_infos
                )
                try:
                    parsed_result = json.loads(tool_result)
                    return {
                        "original_query": query,
                        "generated_sql": parsed_result.get("generated_sql", ""),
                        "raw_tool_sql": parsed_result.get("generated_sql", ""),
                        "explanation": parsed_result.get("explanation", ""),
                        "query_result": parsed_result.get("query_result", []),
                        "schema": schema_info
                    }
                except json.JSONDecodeError:
                    return {"error": "Failed to parse tool output", "raw_output": tool_result}

            output_text = getattr(agent_output, "result", str(agent_output)).strip()
            logger.debug(f"[Text2SQL Raw Output]\n{output_text}")

            try:
                match = re.search(r"```json\s*(\{.*?\})\s*```", output_text, re.DOTALL | re.IGNORECASE)
                parsed_result = json.loads(match.group(1).strip()) if match else json.loads(output_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse agent output: {e}")
                return {"error": f"Failed to parse agent output: {e}", "raw_output": output_text}

            # 🛠️ Extract SQL block from Final Answer
            generated_sql = ""
            raw_tool_sql = parsed_result.get("generated_sql", "")
            explanation = parsed_result.get("explanation", "")

            sql_match = re.search(r"```sql\s*(.*?)\s*```", output_text, re.DOTALL | re.IGNORECASE)
            if sql_match:
                generated_sql = sql_match.group(1).strip()
            elif raw_tool_sql:
                generated_sql = raw_tool_sql

            if generated_sql and generated_sql.strip():
                if not self._validate_sql_tables(generated_sql, schema_info):
                    return {
                        "error": "Generated SQL references unknown tables",
                        "generated_sql": generated_sql,
                        "available_tables": list(schema_info.keys())
                    }

                text2sql_tool = CrewText2SQLTool()
                result_data = text2sql_tool.execute_sql_across_dbs(generated_sql, db_infos)

                return {
                    "original_query": query,
                    "generated_sql": generated_sql,
                    # "raw_tool_sql": raw_tool_sql,
                    "explanation": explanation,
                    "query_result": result_data,
                    "schema": schema_info
                }
            else:
                return {
                    "error": "No SQL generated",
                    "explanation": explanation,
                    "schema": schema_info
                }

        except Exception as e:
            logger.exception("Error processing natural language query")
            return {"error": str(e), "query": query}
            
    def _format_schema_for_agent(self, schema_info: dict) -> str:
        """Format schema info for display in agent prompt"""
        formatted = []
        for table_name, table_info in schema_info.items():
            columns = table_info.get("columns", [])
            column_list = ", ".join([f"{col['name']} ({col['type']})" for col in columns])
            formatted.append(f"Table: {table_name}\nColumns: {column_list}")
        return "\n\n".join(formatted)
        
    def _validate_sql_tables(self, sql: str, schema_info: dict) -> bool:
        """Validate that SQL only references tables in schema"""
        # Extract table names from SQL
        tables_in_sql = set()
        
        # Find tables after FROM
        from_matches = re.findall(r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_.]*)", sql, re.IGNORECASE)
        tables_in_sql.update(from_matches)
        
        # Find tables after JOIN
        join_matches = re.findall(r"\bjoin\s+([a-zA-Z_][a-zA-Z0-9_.]*)", sql, re.IGNORECASE)
        tables_in_sql.update(join_matches)
        
        # Check if all tables exist in schema
        schema_tables = set(schema_info.keys())
        
        for table in tables_in_sql:
            # Handle both qualified (db.table) and unqualified (table) names
            if table not in schema_tables:
                # Try to find a match with any prefix
                found = False
                for schema_table in schema_tables:
                    if schema_table.endswith(f".{table}"):
                        found = True
                        break
                if not found:
                    return False
        
        return True
    
    
    def generate_report(self, report_config: Dict[str, Any]) -> Any:
        try:
            report_type = report_config.get("type", "sales_report")
            parameters = report_config.get("parameters", {})
            data_source = report_config.get("data_source", "unknown")
            data_sources = report_config.get("data_sources", [])

            parameters["data_sources"] = data_sources

            reports_agent = Agent(
                role="Data Analyst & Report Generator",
                goal="Generate accurate, data-driven reports from real database queries",
                backstory="""You are an expert data analyst who specializes in creating 
                comprehensive business reports. You have direct access to database tools 
                and can execute SQL queries to extract meaningful insights.""",
                tools=[self.tools["report_generation"]],
                verbose=True,
                allow_delegation=False
            )

            report_task = Task(
                description=f"""
                Generate a comprehensive {report_type} report using real database data.

                **Requirements:**
                - Report Type: {report_type}
                - Data Source: {data_source}
                - Parameters: {json.dumps(parameters, indent=2)}

                **Instructions:**
                1. Execute the Report Generation Tool with the provided parameters
                2. Only use tables listed in the following allowed list:
                {json.dumps(data_sources, indent=2)}
                3. Do not access or profile tables outside this list
                4. Return a structured JSON report with results, summaries, and insights
                """,
                agent=reports_agent,
                expected_output="Complete JSON report with real database data and insights",
                tools=[self.tools["report_generation"]]
            )

            crew = Crew(
                agents=[reports_agent],
                tasks=[report_task],
                process=Process.sequential,
                verbose=True
            )

            return crew.kickoff()
            
            # Parse and return the result
            if hasattr(result, 'raw') and result.raw:
                try:
                    # Try to extract JSON from the result
                    raw_content = result.raw
                    if isinstance(raw_content, str):
                        # Look for JSON in the response
                        import re
                        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
                        if json_match:
                            json_content = json_match.group()
                            parsed_result = json.loads(json_content)
                            return type('ReportResult', (), {
                                'raw': json.dumps(parsed_result, indent=2),
                                'json_dict': parsed_result
                            })()
                    
                    return result
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.warning(f"Could not parse JSON from result: {e}")
                    return result
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                "error": str(e), 
                "report_config": report_config,
                "timestamp": datetime.now().isoformat()
            }
