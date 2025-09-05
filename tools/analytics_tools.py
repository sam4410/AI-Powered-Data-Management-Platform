from crewai.tools import BaseTool
from typing import Dict, List, Any, Type
from pydantic import BaseModel, Field
import json
import logging
import re
import sqlite3
from pathlib import Path
from openai import OpenAI
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Input schema with proper Pydantic v2 configuration
class Text2SQLInput(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    
    natural_language_query: str = Field(description="Natural language query to convert to SQL")
    schema_info: Dict[str, Any] = Field(description="Database schema information")
    db_files: List[Dict[str, str]] = Field(description="List of database files")

# Helper function moved to module level for proper scope
def is_valid_sql(sql: str, schema_info: Dict[str, Any]) -> bool:
    """Validate if SQL references only tables present in schema"""
    if not sql or not schema_info:
        return False
        
    # Extract table names from SQL
    tables_in_sql = set(re.findall(r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE))
    tables_in_sql.update(re.findall(r"\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE))
    
    # Handle both dict and list schema formats
    if isinstance(schema_info, dict):
        # For qualified table names (db.table), extract just the table name
        valid_tables = set()
        for table_key in schema_info.keys():
            if '.' in table_key:
                # Extract table name from qualified name (e.g., customer_db.customers -> customers)
                table_name = table_key.split('.')[-1]
                valid_tables.add(table_name.lower())
            else:
                valid_tables.add(table_key.lower())
    elif isinstance(schema_info, list):
        valid_tables = set()
        for table in schema_info:
            table_name = table.get("table_name") or table.get("name")
            if table_name:
                valid_tables.add(table_name.lower())
    else:
        return False
    
    logger.debug(f"Tables in SQL: {tables_in_sql}")
    logger.debug(f"Valid tables: {valid_tables}")
    
    return all(t.lower() in valid_tables for t in tables_in_sql)

# Corrected Tool Definition
class CrewText2SQLTool(BaseTool):
    name: str = "Text to SQL Tool"
    description: str = "Convert NL query into SQL and get the answer"
    args_schema: Type[BaseModel] = Text2SQLInput

    def serialize_schema(self, schema_info: Any) -> str:
        """
        Convert schema_info into a strict textual representation
        to be used in the prompt. Supports both dict and list format.
        """
        lines = []

        # Case 1: If schema_info is a dict with qualified table names (db.table format)
        if isinstance(schema_info, dict):
            for table_name, metadata in schema_info.items():
                columns = metadata.get("columns", [])
                
                # Handle both simple and complex column formats
                column_list = []
                for col in columns:
                    if isinstance(col, dict):
                        col_name = col.get('name', '')
                        col_type = col.get('type', 'TEXT')
                        column_list.append(f"{col_name} ({col_type})")
                    else:
                        column_list.append(str(col))
                
                column_str = ", ".join(column_list)
                
                # Extract just the table name for SQL (remove db prefix)
                display_name = table_name.split('.')[-1] if '.' in table_name else table_name
                
                lines.append(f"Table: {display_name}\nColumns: {column_str}")
                
                # Add foreign key info if available
                fks = metadata.get("foreign_keys", [])
                if fks:
                    fk_info = []
                    for fk in fks:
                        fk_info.append(f"{fk['from']} -> {fk['to_table']}.{fk['to_column']}")
                    lines.append(f"Foreign Keys: {', '.join(fk_info)}")

        # Case 2: If schema_info is a list of tables
        elif isinstance(schema_info, list):
            for table in schema_info:
                table_name = table.get("table_name") or table.get("name")
                columns = table.get("columns", [])
                if not table_name:
                    continue
                column_list = ", ".join(
                    [f"{col['name']} ({col.get('type', 'TEXT')})" for col in columns]
                )
                lines.append(f"Table: {table_name}\nColumns: {column_list}")

        else:
            raise ValueError("schema_info must be a list or dict")

        return "\n\n".join(lines)

    def execute_sql_across_dbs(self, sql: str, db_files: list) -> list:
        """Execute SQL across multiple databases"""
        if not db_files:
            return [{"error": "No database files provided for execution."}]
        
        if not sql or not sql.strip():
            return [{"error": "Empty SQL query provided for execution."}]
    
        conn = None
        try:
            main_db_path = Path(db_files[0]["path"]).resolve()
            
            # Check if database file exists
            if not main_db_path.exists():
                return [{"error": f"Database file not found: {main_db_path}"}]
            
            conn = sqlite3.connect(str(main_db_path))
            cursor = conn.cursor()
    
            # Attach additional databases if provided
            attached_aliases = set(["main"])
            attached_paths = {str(main_db_path)}  # Track already attached paths
            for idx, db in enumerate(db_files[1:], start=1):
                db_path = Path(db["path"]).resolve()
                if str(db_path) in attached_paths:
                    continue  # Skip if already attached
                if not db_path.exists():
                    logger.warning(f"Database file not found: {db_path}")
                    continue
                    
                alias = db_path.stem
                if alias in attached_aliases:
                    alias = f"{alias}_{idx}"
                attached_aliases.add(alias)
                attached_paths.add(str(db_path))
                cursor.execute(f"ATTACH DATABASE '{db_path}' AS {alias}")

            logger.info(f"🔍 Executing SQL:\n{sql}")
            cursor.execute(sql)
    
            # Check if this query returns results
            if cursor.description is None:
                return [{"message": "Query executed successfully, but no results returned."}]
    
            rows = cursor.fetchall()
            headers = [desc[0] for desc in cursor.description]
            return [dict(zip(headers, row)) for row in rows]
    
        except sqlite3.Error as e:
            logger.error(f"SQLite Error: {e}")
            return [{"error": f"Database error: {str(e)}", "query": sql}]
        except Exception as e:
            logger.error(f"SQL Execution Error: {e}")
            return [{"error": str(e), "query": sql}]
        finally:
            if conn:
                conn.close()

    def _run(self, natural_language_query: str, schema_info: Dict[str, Any], db_files: List[Dict[str, str]], **kwargs) -> str:
        """
        Execute the text-to-SQL conversion process
        
        Args:
            natural_language_query: The natural language query to convert
            schema_info: Database schema information (dict or list format)
            db_files: List of database files to execute queries against
            
        Returns:
            JSON string containing the generated SQL, explanation, and results
        """
        try:
            question = natural_language_query

            # Debug logging
            logger.info(f"🔍 Processing query: {question}")
            logger.info(f"🔍 Schema info type: {type(schema_info)}")
            logger.info(f"🔍 Schema info keys: {list(schema_info.keys()) if isinstance(schema_info, dict) else 'Not a dict'}")

            # Ensure schema_info is parsed if passed as a JSON string
            if isinstance(schema_info, str):
                try:
                    schema_info = json.loads(schema_info)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in schema_info: {e}")

            # Validate inputs
            if not question or not question.strip():
                raise ValueError("Missing or empty natural_language_query")
            
            if not schema_info:
                raise ValueError("Missing schema_info")

            # Serialize schema for prompt
            schema_str = self.serialize_schema(schema_info)
            logger.info(f"🔍 Serialized schema:\n{schema_str}")

            # Create prompt with better instructions
            prompt = f"""
You are an expert SQL generator. Convert the natural language query into a valid SQL query.

## Natural Language Query:
{question}

## Available Database Schema:
{schema_str}

## Important Instructions:
- Use ONLY the tables and columns listed in the schema above
- For qualified table names (like customer_db.customers), use just the table name (customers) in your SQL
- Generate syntactically correct SQLite SQL
- Focus on the specific question asked
- If you need to filter by a specific value, use appropriate WHERE clauses

## Response Format (JSON only):
```json
{{
  "generated_sql": "SELECT ... FROM ... WHERE ...",
  "explanation": "Clear explanation of what the query does"
}}
```

Generate the SQL query now:
"""

            # Call OpenAI API
            try:
                client = OpenAI()
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=1000
                )

                llm_output = response.choices[0].message.content.strip()
                logger.debug(f"[GPT-4o Output]\n{llm_output}")

            except Exception as e:
                raise ValueError(f"OpenAI API error: {e}")

            # Parse JSON response with better error handling
            try:
                match = re.search(r"```json\s*(.*?)```", llm_output, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(1))
                else:
                    parsed = json.loads(llm_output)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response: {e}")
                logger.error(f"Raw output: {llm_output}")
                raise ValueError(f"Failed to parse LLM response as JSON: {e}")

            sql = parsed.get("generated_sql")
            explanation = parsed.get("explanation", "")
            
            if not sql:
                raise ValueError("No SQL generated by LLM")

            # Add original query to response
            parsed["original_query"] = question

            # Validate and execute SQL if database files are provided
            if db_files:
                # Debug: Show what we're validating
                logger.info(f"🔍 Validating SQL: {sql}")
                logger.info(f"🔍 Available schema tables: {list(schema_info.keys())}")
                
                # Validate SQL (but don't fail if invalid - let database handle it)
                is_valid = is_valid_sql(sql, schema_info)
                logger.info(f"🔍 SQL validation result: {is_valid}")
                
                if not is_valid:
                    logger.warning("Generated SQL may reference unknown tables")
                    parsed["warning"] = "Generated SQL may reference unknown tables"
                    
                    # Extract table names for debugging
                    tables_in_sql = set(re.findall(r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE))
                    tables_in_sql.update(re.findall(r"\bjoin\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE))
                    
                    logger.warning(f"Tables in SQL: {tables_in_sql}")
                    
                    # Get valid table names for comparison
                    valid_tables = set()
                    for table_key in schema_info.keys():
                        if '.' in table_key:
                            table_name = table_key.split('.')[-1]
                            valid_tables.add(table_name.lower())
                        else:
                            valid_tables.add(table_key.lower())
                    
                    logger.warning(f"Valid tables: {valid_tables}")
                
                # Execute SQL (let database handle validation)
                parsed["query_result"] = self.execute_sql_across_dbs(sql, db_files)
            else:
                parsed["query_result"] = []

            return json.dumps(parsed, indent=2)

        except Exception as e:
            logger.exception("GPT-4o NL2SQL failed")
            error_response = {
                "error": str(e),
                "query": natural_language_query,
                "schema_available": bool(schema_info),
                "schema_keys": list(schema_info.keys()) if isinstance(schema_info, dict) else None
            }
            return json.dumps(error_response, indent=2)


class ReportGenerationInput(BaseModel):
    """Input schema for report generation"""
    report_type: str = Field(description="Type of report to generate")
    data_source: str = Field(description="Database path or connection string")
    parameters: Dict[str, Any] = Field(description="Report parameters and filters", default_factory=dict)


class ReportGenerationTool(BaseTool):
    """Enhanced tool for generating comprehensive reports with real database queries"""
    name: str = "Report Generation Tool"
    description: str = "Generate comprehensive reports with real data from SQLite databases"
    args_schema: type[BaseModel] = ReportGenerationInput
    
    report_templates: Dict[str, List[Dict[str, Any]]] = {}
    data_product_reports: Dict[str, List[str]] = {}

    # Add __init__ to inject fields correctly
    def __init__(self, report_templates=None, data_product_reports=None, **kwargs):
        super().__init__(**kwargs)
        self.report_templates = report_templates or {}
        self.data_product_reports = data_product_reports or {}
    
    def _load_report_templates(self) -> Dict[str, Any]:
        """Load report templates from JSON file"""
        try:
            template_path = Path("sample_reports.json")
            if template_path.exists():
                with open(template_path, "r", encoding="utf-8") as f:
                    templates = json.load(f)
                    return {t["name"]: t for t in templates}
            return {}
        except Exception as e:
            logger.warning(f"Could not load report templates: {e}")
            return {}
    
    def _connect_to_database(self, db_path: str) -> sqlite3.Connection:
        """Create database connection"""
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
            
    def _execute_query(self, conn, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            cursor = conn.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(limit)
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.warning(f"Failed to execute query: {e}")
            return []
            
    def safe_execute_query(self, conn: sqlite3.Connection, query: str, required_tables: set, data_sources: List[str]) -> List[Dict[str, Any]]:
        """Execute a query only if all required tables are present in data_sources"""
        if required_tables.issubset(set(data_sources)):
            return self._execute_query(conn, query)
        else:
            missing = required_tables - set(data_sources)
            logger.warning(f"Skipping query due to missing tables: {missing}")
            return []
            
    def _load_data_product_reports(self) -> Dict[str, List[str]]:
        """Build mapping of Data Product name -> list of report names"""
        try:
            path = Path("ecommerce_data_products.json")
            if not path.exists():
                logger.warning("ecommerce_data_products.json not found.")
                return {}

            with open(path, "r", encoding="utf-8") as f:
                data_products = json.load(f)

            report_map = {
                dp["name"]: [r.lower().replace(" ", "_") for r in dp.get("report_suite", [])]
                for dp in data_products if "name" in dp
            }

            logger.info(f"Loaded report suites for {len(report_map)} data products.")
            return report_map

        except Exception as e:
            logger.error(f"Error loading data product reports: {e}")
            return {}
    
    def _create_error_report(self, error_message: str) -> Dict[str, Any]:
        """Create error report when generation fails"""
        return {
            "report_title": "Report Generation Error",
            "generation_date": datetime.now().strftime("%B %d, %Y"),
            "error": error_message,
            "data_summary": {
                "summary": "Report generation failed due to an error.",
                "metrics": {},
                "queries_executed": []
            },
            "sections": [
                {
                    "title": "Error Details",
                    "content": error_message
                }
            ],
            "recommendations": [
                "Check database connection and permissions",
                "Verify report parameters are correct",
                "Review error logs for detailed information"
            ],
            "conclusion": "Report generation requires troubleshooting before proceeding."
        }
        
    def _extract_tables_from_query(self, query: str) -> set:
        """Basic SQL parser to extract table names from query"""
        import re
        matches = re.findall(r'\bFROM\s+(\w+)\b|\bJOIN\s+(\w+)\b', query, re.IGNORECASE)
        return set([m[0] or m[1] for m in matches])
    
    def _run(self, report_type: str, data_source: str, parameters: Dict[str, Any] = None) -> str:
        try:
            if not parameters:
                parameters = {}

            parameters["data_source"] = data_source
            data_sources = parameters.get("data_sources", [])
            data_product = parameters.get("data_product")

            # Normalize report type
            normalized_type = report_type.lower().strip().replace(" ", "_").replace("&", "and").replace("-", "_")

            # Check if report_type is allowed for this data product
            allowed_names = self.data_product_reports.get(data_product, [])

            # Find all template types matching allowed names
            allowed_types = [
                tpl.get("type")
                for tpl in self.report_templates.get(data_product, [])
                if tpl.get("name") in allowed_names
            ]

            if normalized_type not in allowed_types:
                logger.warning(f"{report_type} not in selected data product suite.")
                return json.dumps(self._create_error_report(
                    f"⚠️ Report '{report_type}' is not part of the '{data_product}' suite."
                ), indent=2)
                
            logger.debug(f"[LOOKUP] Normalized type: {normalized_type}")
            logger.debug(f"[LOOKUP] Available types: {[tpl.get('type') for tpl_list in self.report_templates.values() for tpl in tpl_list]}")
                
            # Find matching report template
            report_template = next(
                (tpl for tpl_list in self.report_templates.values() for tpl in tpl_list
                 if tpl.get("type", "").lower().replace(" ", "_").replace("&", "and").replace("-", "_") == normalized_type),
                None
            )

            if not report_template:
                return json.dumps(self._create_error_report(
                    f"⚠️ Report template '{report_type}' not found."
                ), indent=2)

            # Connect to database
            conn = self._connect_to_database(data_source)

            skipped_sections = []
            sections = []
            queries = report_template.get("queries", [])
            visualizations = report_template.get("visualizations", [])

            for idx, query in enumerate(queries):
                required_tables = self._extract_tables_from_query(query)
                if not required_tables.issubset(set(data_sources)):
                    logger.info(f"Skipping query {idx+1} due to missing tables: {required_tables - set(data_sources)}")
                    skipped_sections.append(f"Query {idx+1}")
                    continue

                results = self._execute_query(conn, query)
                if not results:
                    skipped_sections.append(f"Query {idx+1}")
                    continue

                sections.append({
                    "title": f"Section {idx+1}",
                    "content": results,
                    "visualization": visualizations[idx] if idx < len(visualizations) else None
                })

            conn.close()

            # Final report object
            report = {
                "report_title": report_template.get("name", "Untitled Report"),
                "generation_date": datetime.now().strftime("%B %d, %Y"),
                "data_source": data_source,
                "period": f"Last {parameters.get('days_back', 30)} days",
                "data_summary": {
                    "summary": report_template.get("description", "Data insights report."),
                    "metrics": {},
                    "queries_executed": queries
                },
                "sections": sections,
                "recommendations": report_template.get("recommendations", []),
                "conclusion": report_template.get("conclusion", "No conclusion available.")
            }

            if skipped_sections:
                report["sections"].append({
                    "title": "⚠️ Sections Skipped",
                    "content": {
                        "reason": "Some queries could not be executed due to missing tables or no data.",
                        "skipped_sections": skipped_sections
                    }
                })
                report["conclusion"] += " Some sections were skipped due to restricted access or missing data."

            return json.dumps(report, indent=2)

        except Exception as e:
            error_msg = f"❌ Report generation failed: {str(e)}"
            logger.error(error_msg)
            return json.dumps(self._create_error_report(error_msg), indent=2)