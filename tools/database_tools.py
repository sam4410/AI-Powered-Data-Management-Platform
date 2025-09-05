# =============================================================================
# tools/database_tools.py - Database connectivity and operations
# =============================================================================

"""
tools/database_tools.py
Database tools for connectivity and metadata operations
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3
import re
import json
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from utils.validation import is_valid_sqlite_connection_string

logger = logging.getLogger(__name__)

class DatabaseConnectionInput(BaseModel):
    """Input schema for database connection"""
    connection_string: str = Field(..., description="Valid SQLite path. Passed from platform, e.g., 'sqlite:///uploaded_dbs/ecommerce_db.db'")
    query: Optional[str] = Field(default=None, description="SQL query to execute")

class DatabaseConnectionTool(BaseTool):
    """Tool for database connection and query execution"""
    name: str = "Database Connection Tool"
    description: str = "Connect to database and execute queries for data analysis"
    args_schema: Type[BaseModel] = DatabaseConnectionInput
    
    def _run(self, connection_string: str, query: Optional[str] = None, **kwargs) -> str:
        """Execute database operations"""
        if not is_valid_sqlite_connection_string(connection_string):
            return f"❌ Invalid connection string: {connection_string}. Must be sqlite:///uploaded_dbs/<name>.db"
        try:
            # Handle case where parameters might be passed as a single argument
            if isinstance(connection_string, dict):
                query = connection_string.get('query')
                connection_string = connection_string.get('connection_string')
            
            if not connection_string:
                return "Error: connection_string is required"
            
            conn = sqlite3.connect(connection_string.replace("sqlite:///", ""))
            
            if query:
                df = pd.read_sql_query(query, conn)
                result = f"Query executed successfully. Results:\n{df.to_string()}"
                logger.info(f"Database query executed: {query}")
            else:
                # Get table information
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                result = f"Available tables: {[table[0] for table in tables]}"
                logger.info("Retrieved database schema information")
            
            conn.close()
            return result
            
        except Exception as e:
            error_msg = f"Database operation failed: {str(e)}"
            logger.error(error_msg)
            return error_msg

class MetadataExtractionInput(BaseModel):
    table_name: str = Field(description="Name of the table to extract metadata from")
    connection_string: str = Field(..., description="Valid SQLite path. Passed from platform, e.g., 'sqlite:///uploaded_dbs/ecommerce_db.db'")
    allowed_tables: List[str] = Field(default=None, description="Optional list of allowed tables")
    include_sample_data: Optional[bool] = Field(default=True, description="Whether to include sample data analysis")
    max_sample_size: int = Field(default=10000, description="Maximum number of rows to sample for analysis")

class MetadataExtractionTool(BaseTool):
    name: str = "Metadata Extraction Tool"
    description: str = "Extract comprehensive metadata, perform data quality assessment, and provide actionable insights for database optimization"
    args_schema: Type[BaseModel] = MetadataExtractionInput

    def _run(self, table_name: str, connection_string: str, allowed_tables: Optional[List[str]] = None, 
             include_sample_data: bool = True, max_sample_size: int = 10000) -> str:
        logger.debug(f"📥 MetadataExtractionTool Input - Table: {table_name}, Conn: {connection_string}")
        
        if not connection_string:
            return json.dumps({
                "error": "❌ Connection string missing from input. Please provide a valid 'sqlite:///' path.",
                "table": table_name
            })

        if allowed_tables and table_name not in allowed_tables:
            return json.dumps({
                "error": f"⛔ Table `{table_name}` is not allowed",
                "table": table_name
            })

        if not is_valid_sqlite_connection_string(connection_string):
            return json.dumps({
                "error": f"❌ Invalid connection string: {connection_string}. Must be sqlite:///databases/<name>.db",
                "table": table_name
            })

        try:
            conn = sqlite3.connect(connection_string.replace("sqlite:///", ""))
            cursor = conn.cursor()

            # Initialize metadata structure
            metadata = {
                "table_name": table_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "basic_info": {},
                "columns": [],
                "relationships": {
                    "primary_keys": [],
                    "foreign_key_hints": [],
                    "indexes": []
                },
                "data_quality": {
                    "issues": [],
                    "warnings": [],
                    "quality_score": 0
                },
                "business_insights": {
                    "potential_use_cases": [],
                    "data_maturity_level": "",
                    "automation_readiness": ""
                },
                "recommendations": {
                    "immediate_actions": [],
                    "schema_improvements": [],
                    "performance_optimizations": [],
                    "governance_actions": []
                }
            }

            # Basic table information
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema = cursor.fetchall()
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Get table creation SQL for analysis
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            create_sql = cursor.fetchone()
            
            metadata["basic_info"] = {
                "row_count": row_count,
                "column_count": len(schema),
                "estimated_size_mb": self._estimate_table_size(cursor, table_name),
                "creation_sql": create_sql[0] if create_sql else None
            }

            # Load sample data for analysis
            if include_sample_data and row_count > 0:
                sample_size = min(max_sample_size, row_count)
                df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {sample_size}", conn)
                metadata["basic_info"]["sample_size"] = sample_size
                metadata["basic_info"]["sample_percentage"] = (sample_size / row_count) * 100 if row_count > 0 else 0
            else:
                df = pd.DataFrame()

            # Analyze each column
            quality_issues = []
            quality_score = 100
            
            for col in schema:
                col_id, name, dtype, not_null, default_val, is_pk = col
                col_meta = self._analyze_column(name, dtype, not_null, default_val, is_pk, df, quality_issues)
                metadata["columns"].append(col_meta)
                
                if is_pk:
                    metadata["relationships"]["primary_keys"].append(name)

            # Enhanced relationship detection
            metadata["relationships"]["foreign_key_hints"] = self._detect_foreign_keys(schema, cursor)
            metadata["relationships"]["indexes"] = self._get_indexes(cursor, table_name)

            # Data quality assessment
            metadata["data_quality"] = self._assess_data_quality(schema, df, quality_issues, row_count)

            # Business insights
            metadata["business_insights"] = self._generate_business_insights(schema, df, table_name, row_count)

            # Generate comprehensive recommendations
            metadata["recommendations"] = self._generate_recommendations(
                schema, df, table_name, row_count, metadata["data_quality"], 
                metadata["relationships"], quality_issues
            )

            conn.close()
            return json.dumps(metadata, indent=2)

        except Exception as e:
            return json.dumps({
                "error": f"❌ Metadata extraction failed: {str(e)}",
                "table": table_name,
                "timestamp": datetime.now().isoformat()
            })

    def _analyze_column(self, name: str, dtype: str, not_null: bool, default_val: Any, 
                       is_pk: bool, df: pd.DataFrame, quality_issues: List[Dict]) -> Dict:
        """Comprehensive column analysis"""
        col_meta = {
            "name": name,
            "type": dtype,
            "nullable": not not_null,
            "default": default_val,
            "is_primary_key": is_pk,
            "statistics": {},
            "quality_metrics": {},
            "patterns": {},
            "suggestions": []
        }

        if not df.empty and name in df.columns:
            series = df[name]
            
            # Basic statistics
            col_meta["statistics"] = {
                "null_count": series.isnull().sum(),
                "null_percentage": (series.isnull().sum() / len(series)) * 100,
                "unique_count": series.nunique(),
                "unique_percentage": (series.nunique() / len(series)) * 100 if len(series) > 0 else 0
            }

            # Data type specific analysis
            if series.dtype in ['int64', 'float64']:
                col_meta["statistics"].update({
                    "min": series.min(),
                    "max": series.max(),
                    "mean": series.mean(),
                    "std": series.std()
                })
            elif series.dtype == 'object':
                col_meta["statistics"].update({
                    "avg_length": series.str.len().mean() if not series.empty else 0,
                    "max_length": series.str.len().max() if not series.empty else 0
                })

            # Pattern detection
            col_meta["patterns"] = self._detect_patterns(series, name)

            # Quality assessment
            col_meta["quality_metrics"] = self._assess_column_quality(series, name, dtype, not_null)

            # Column-specific suggestions
            col_meta["suggestions"] = self._generate_column_suggestions(series, name, dtype, not_null, is_pk)

        return col_meta

    def _detect_patterns(self, series: pd.Series, col_name: str) -> Dict:
        """Detect common data patterns"""
        patterns = {
            "is_email": False,
            "is_phone": False,
            "is_url": False,
            "is_date_string": False,
            "is_json": False,
            "is_categorical": False,
            "has_consistent_format": False
        }

        if series.dtype == 'object' and not series.empty:
            sample_values = series.dropna().head(100).astype(str)
            
            # Email pattern
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            patterns["is_email"] = sample_values.str.match(email_pattern).mean() > 0.8

            # Phone pattern
            phone_pattern = r'^\+?[\d\s\-\(\)]{10,}$'
            patterns["is_phone"] = sample_values.str.match(phone_pattern).mean() > 0.8

            # URL pattern
            url_pattern = r'^https?://[^\s]+$'
            patterns["is_url"] = sample_values.str.match(url_pattern).mean() > 0.8

            # Date string pattern
            try:
                pd.to_datetime(sample_values.head(10), errors='coerce')
                patterns["is_date_string"] = True
            except:
                patterns["is_date_string"] = False

            # JSON pattern
            json_count = 0
            for val in sample_values.head(10):
                try:
                    json.loads(val)
                    json_count += 1
                except:
                    pass
            patterns["is_json"] = json_count / len(sample_values.head(10)) > 0.8

            # Categorical detection
            unique_ratio = series.nunique() / len(series)
            patterns["is_categorical"] = unique_ratio < 0.1 and series.nunique() < 50

        return patterns

    def _assess_column_quality(self, series: pd.Series, col_name: str, dtype: str, not_null: bool) -> Dict:
        """Assess data quality for a specific column"""
        quality = {
            "completeness_score": 0,
            "consistency_score": 0,
            "validity_score": 0,
            "overall_score": 0,
            "issues": []
        }

        if not series.empty:
            # Completeness
            null_ratio = series.isnull().sum() / len(series)
            quality["completeness_score"] = max(0, 100 - (null_ratio * 100))

            # Consistency (format consistency)
            if series.dtype == 'object':
                lengths = series.str.len()
                length_variance = lengths.var() if not lengths.empty else 0
                quality["consistency_score"] = max(0, 100 - min(length_variance, 100))
            else:
                quality["consistency_score"] = 90  # Numeric types are generally consistent

            # Validity (domain-specific validation)
            quality["validity_score"] = 95  # Default, can be enhanced with domain rules

            # Overall score
            quality["overall_score"] = (
                quality["completeness_score"] * 0.4 +
                quality["consistency_score"] * 0.3 +
                quality["validity_score"] * 0.3
            )

            # Identify issues
            if null_ratio > 0.1:
                quality["issues"].append(f"High null rate: {null_ratio:.1%}")
            if series.nunique() == 1:
                quality["issues"].append("Column has only one unique value")
            if series.dtype == 'object' and series.str.len().max() > 1000:
                quality["issues"].append("Very long text values detected")

        return quality

    def _generate_column_suggestions(self, series: pd.Series, col_name: str, dtype: str, 
                                   not_null: bool, is_pk: bool) -> List[str]:
        """Generate actionable suggestions for column improvements"""
        suggestions = []

        if not series.empty:
            # Null handling suggestions
            if series.isnull().sum() > 0 and not not_null:
                suggestions.append(f"🔧 Consider adding NOT NULL constraint or default value")

            # Data type optimization
            if dtype == 'TEXT' and series.dtype == 'object':
                max_len = series.str.len().max() if not series.empty else 0
                if max_len < 255:
                    suggestions.append(f"📊 Consider VARCHAR({max_len + 50}) instead of TEXT for better performance")

            # Indexing suggestions
            if series.nunique() / len(series) > 0.8 and not is_pk:
                suggestions.append("🚀 High cardinality - consider adding index for query performance")

            # Enum suggestions
            if series.nunique() < 10 and len(series) > 100:
                suggestions.append("📋 Low cardinality - consider ENUM or lookup table")

            # Validation suggestions
            if col_name.endswith('_email') and not self._detect_patterns(series, col_name)['is_email']:
                suggestions.append("✅ Add email format validation")

        return suggestions

    def _detect_foreign_keys(self, schema: List, cursor) -> List[Dict]:
        """Enhanced foreign key detection"""
        fk_hints = []
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        for col in schema:
            col_id, name, dtype, not_null, default_val, is_pk = col
            
            if name.endswith('_id') and not is_pk:
                # Try to find matching table
                potential_table = name[:-3]  # Remove '_id'
                confidence = "low"
                
                if potential_table in all_tables:
                    confidence = "high"
                elif f"{potential_table}s" in all_tables:
                    potential_table = f"{potential_table}s"
                    confidence = "medium"
                elif potential_table.rstrip('s') in all_tables:
                    potential_table = potential_table.rstrip('s')
                    confidence = "medium"
                
                fk_hints.append({
                    "column": name,
                    "referenced_table": potential_table,
                    "confidence": confidence,
                    "suggestion": f"Verify relationship with {potential_table} table"
                })
        
        return fk_hints

    def _get_indexes(self, cursor, table_name: str) -> List[Dict]:
        """Get existing indexes for the table"""
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = []
        for index_info in cursor.fetchall():
            cursor.execute(f"PRAGMA index_info({index_info[1]})")
            columns = [col[2] for col in cursor.fetchall()]
            indexes.append({
                "name": index_info[1],
                "unique": bool(index_info[2]),
                "columns": columns
            })
        return indexes

    def _estimate_table_size(self, cursor, table_name: str) -> float:
        """Estimate table size in MB"""
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Rough estimation based on column types
            estimated_row_size = 0
            for col in columns:
                col_type = col[2].upper()
                if 'INT' in col_type:
                    estimated_row_size += 8
                elif 'REAL' in col_type or 'FLOAT' in col_type:
                    estimated_row_size += 8
                elif 'TEXT' in col_type or 'VARCHAR' in col_type:
                    estimated_row_size += 50  # Average text field size
                else:
                    estimated_row_size += 20  # Default
            
            return (row_count * estimated_row_size) / (1024 * 1024)  # Convert to MB
        except:
            return 0

    def _assess_data_quality(self, schema: List, df: pd.DataFrame, quality_issues: List, 
                           row_count: int) -> Dict:
        """Comprehensive data quality assessment"""
        quality = {
            "overall_score": 0,
            "completeness_score": 0,
            "consistency_score": 0,
            "validity_score": 0,
            "issues": [],
            "warnings": [],
            "metrics": {}
        }

        if not df.empty:
            # Completeness assessment
            total_cells = len(df) * len(df.columns)
            null_cells = df.isnull().sum().sum()
            completeness = ((total_cells - null_cells) / total_cells) * 100
            quality["completeness_score"] = completeness

            # Consistency assessment (placeholder - can be enhanced)
            quality["consistency_score"] = 85

            # Validity assessment (placeholder - can be enhanced)
            quality["validity_score"] = 90

            # Overall score
            quality["overall_score"] = (
                quality["completeness_score"] * 0.4 +
                quality["consistency_score"] * 0.3 +
                quality["validity_score"] * 0.3
            )

            # Identify critical issues
            if completeness < 80:
                quality["issues"].append("🚨 Low data completeness - significant missing values")
            if row_count == 0:
                quality["issues"].append("🚨 Empty table - no data available")
            if len(df.columns) > 50:
                quality["warnings"].append("⚠️ Wide table - consider normalization")

        return quality

    def _generate_business_insights(self, schema: List, df: pd.DataFrame, table_name: str, 
                                  row_count: int) -> Dict:
        """Generate business-focused insights"""
        insights = {
            "potential_use_cases": [],
            "data_maturity_level": "",
            "automation_readiness": "",
            "business_value": "",
            "critical_dependencies": []
        }

        # Infer use cases based on table name and structure
        table_lower = table_name.lower()
        column_names = [col[1].lower() for col in schema]

        if any(word in table_lower for word in ['user', 'customer', 'client']):
            insights["potential_use_cases"].extend([
                "Customer relationship management",
                "User behavior analysis",
                "Personalization and segmentation"
            ])

        if any(word in table_lower for word in ['order', 'transaction', 'sale']):
            insights["potential_use_cases"].extend([
                "Sales analytics and forecasting",
                "Revenue tracking",
                "Customer lifetime value analysis"
            ])

        if any(word in table_lower for word in ['product', 'inventory', 'item']):
            insights["potential_use_cases"].extend([
                "Inventory management",
                "Product performance analysis",
                "Demand forecasting"
            ])

        # Assess data maturity
        has_timestamps = any('timestamp' in col or 'date' in col or 'time' in col for col in column_names)
        has_ids = any('id' in col for col in column_names)
        has_status = any('status' in col or 'state' in col for col in column_names)

        if has_timestamps and has_ids and has_status and row_count > 1000:
            insights["data_maturity_level"] = "High - Well-structured with temporal data"
        elif has_ids and row_count > 100:
            insights["data_maturity_level"] = "Medium - Basic structure in place"
        else:
            insights["data_maturity_level"] = "Low - Requires significant improvement"

        # Automation readiness
        if row_count > 10000 and has_timestamps:
            insights["automation_readiness"] = "High - Ready for automated processing"
        elif row_count > 1000:
            insights["automation_readiness"] = "Medium - Some automation possible"
        else:
            insights["automation_readiness"] = "Low - Manual processing required"

        return insights

    def _generate_recommendations(self, schema: List, df: pd.DataFrame, table_name: str, 
                                row_count: int, data_quality: Dict, relationships: Dict, 
                                quality_issues: List) -> Dict:
        """Generate comprehensive, actionable recommendations"""
        recommendations = {
            "immediate_actions": [],
            "schema_improvements": [],
            "performance_optimizations": [],
            "governance_actions": [],
            "business_enablement": []
        }

        # Immediate actions
        if data_quality["overall_score"] < 70:
            recommendations["immediate_actions"].append(
                "🚨 CRITICAL: Address data quality issues before proceeding with analytics"
            )

        if not relationships["primary_keys"]:
            recommendations["immediate_actions"].append(
                "🔑 URGENT: Add primary key to ensure data integrity"
            )

        if row_count == 0:
            recommendations["immediate_actions"].append(
                "📊 URGENT: Investigate why table is empty - check data pipeline"
            )

        # Schema improvements
        nullable_count = sum(1 for col in schema if not col[3])  # not_null is col[3]
        if nullable_count > len(schema) * 0.7:
            recommendations["schema_improvements"].append(
                "🔧 Review nullable columns - add NOT NULL constraints where appropriate"
            )

        if not relationships["foreign_key_hints"]:
            recommendations["schema_improvements"].append(
                "🔗 Consider adding foreign key constraints to ensure referential integrity"
            )

        # Performance optimizations
        if row_count > 10000:
            recommendations["performance_optimizations"].append(
                "⚡ Consider adding indexes on frequently queried columns"
            )

        if not relationships["indexes"]:
            recommendations["performance_optimizations"].append(
                "📈 No indexes detected - add indexes to improve query performance"
            )

        # Governance actions
        text_columns = [col[1] for col in schema if 'TEXT' in col[2].upper()]
        if len(text_columns) > 3:
            recommendations["governance_actions"].append(
                "📋 Many text columns detected - implement data validation rules"
            )

        recommendations["governance_actions"].append(
            "📝 Document table purpose and column definitions for team reference"
        )

        # Business enablement
        if row_count > 1000:
            recommendations["business_enablement"].append(
                "📊 Table has sufficient data volume for analytics - consider dashboard creation"
            )

        if any('timestamp' in col[1].lower() or 'date' in col[1].lower() for col in schema):
            recommendations["business_enablement"].append(
                "📅 Temporal data available - enable time-series analysis and trend reporting"
            )

        return recommendations
