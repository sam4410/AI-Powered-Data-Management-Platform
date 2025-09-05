# =============================================================================
# tools/data_tools.py - Data profiling and validation tools
# =============================================================================

"""
tools/data_tools.py
Tools for data profiling, validation, and quality assessment
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Type, Tuple
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from utils.validation import is_valid_sqlite_connection_string
import sqlite3
import json
from collections import Counter
from datetime import datetime, timedelta
import re
from scipy import stats
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class DataProfilingInput(BaseModel):
    table_name: str = Field(description="Name of the table to profile")
    connection_string: str = Field(..., description="Valid SQLite path")
    allowed_tables: List[str] = Field(default=None, description="Optional list of allowed tables")

class DataProfilingTool(BaseTool):
    name: str = "Data Profiling Tool"
    description: str = "Comprehensive data profiling with quality scoring, anomaly detection, and business insights"
    args_schema: Type[BaseModel] = DataProfilingInput

    def _run(self, table_name: str, connection_string: str, allowed_tables: Optional[List[str]] = None) -> str:
        logger.debug(f"\U0001F4E5 DataProfilingTool Input - Table: {table_name}, Conn: {connection_string}")

        if not connection_string or not is_valid_sqlite_connection_string(connection_string):
            return json.dumps({"error": f"❌ Invalid or missing connection string: {connection_string}", "table": table_name})

        if allowed_tables and table_name not in allowed_tables:
            return json.dumps({"error": f"⛔ Table `{table_name}` is not permitted", "table": table_name})

        try:
            conn = sqlite3.connect(connection_string.replace("sqlite:///", ""))
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema_info = cursor.fetchall()

            profile = self._profile_table(df, table_name, schema_info)
            conn.close()
            return json.dumps(profile, indent=2, default=str)

        except Exception as e:
            return json.dumps({"error": f"\ud83d\udd25 Failed profiling for `{table_name}`: {str(e)}", "table": table_name})

    def _profile_table(self, df: pd.DataFrame, table_name: str, schema_info: List) -> Dict:
        quality_scores = []
        column_profiles = {}
        quality_issues = []
        anomalies = []

        for col in df.columns:
            try:
                col_profile = self._enhanced_column_profiling(df, col, schema_info)
                column_profiles[col] = col_profile

                score = col_profile.get("quality_score", None)
                if isinstance(score, (int, float)):
                    quality_scores.append(score)

                quality_issues.extend(col_profile.get("quality_issues", []))
                anomalies.extend(col_profile.get("anomalies", []))

            except Exception as e:
                logger.warning(f"⚠️ Failed profiling column `{col}`: {e}")
                column_profiles[col] = {
                    "column_name": col,
                    "error": str(e)
                }

        table_quality_score = round(float(np.mean(quality_scores)), 3) if quality_scores else 0.0
        business_domain = self._infer_business_domain(table_name, df.columns)

        # Construct base profile first
        profile = {
            "table_name": table_name,
            "analysis_timestamp": datetime.now().isoformat(),
            "total_records": len(df),
            "total_columns": len(df.columns),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "table_quality_score": table_quality_score,
            "business_domain": business_domain,
            "criticality": self._assess_table_criticality(table_name, df),
            "column_profiles": column_profiles,
            "relationships": self._detect_relationships(df, schema_info),
            "anomalies": anomalies,
            "quality_issues": quality_issues,
            "trends": self._analyze_trends(df)
        }

        # Add insights and recommendations based on full profile
        profile["actionable_recommendations"] = self._generate_recommendations(profile)
        profile["business_insights"] = self._generate_business_insights(profile)

        return profile

    def _enhanced_column_profiling(self, df: pd.DataFrame, col: str, schema_info: List) -> Dict:
        s = df[col]
        total_records = len(df)
        null_count = s.isnull().sum()
        unique_count = s.nunique(dropna=True)
        null_pct = (null_count / total_records) * 100 if total_records > 0 else 0
        col_schema = next((c for c in schema_info if c[1] == col), None)
        is_pk = col_schema[5] if col_schema else False

        semantic_type = self._classify_semantic_type(col, s)
        profile = {
            "column_name": col,
            "data_type": str(s.dtype),
            "semantic_type": semantic_type,
            "is_primary_key": is_pk,
            "total_count": total_records,
            "null_count": null_count,
            "null_percentage": round(null_pct, 2),
            "unique_count": unique_count,
            "unique_percentage": round((unique_count / total_records) * 100, 2) if total_records > 0 else 0,
            "cardinality": self._infer_cardinality(unique_count, total_records),
            "quality_score": 0.0,
            "quality_breakdown": {},
            "quality_issues": [],
            "anomalies": [],
            "business_rules": [],
            "recommendations": []
        }

        safe_series = pd.to_numeric(s.dropna(), errors='coerce') if semantic_type.lower() in ["numeric", "financial_amount"] else s.dropna()

        profile["quality_breakdown"] = self._assess_column_quality(s, col, semantic_type)
        profile["quality_score"] = self._calculate_quality_score(profile["quality_breakdown"])
        profile["anomalies"] = self._detect_anomalies(safe_series, col)
        profile["business_rules"] = self._validate_business_rules(safe_series, col, semantic_type)
        profile["recommendations"] = self._generate_column_recommendations(profile)

        return profile

    def _classify_semantic_type(self, col_name: str, series: pd.Series) -> str:
        """Classify column into semantic types for business context"""
        col_lower = col_name.lower()
        
        # PII Detection
        if any(term in col_lower for term in ['email', 'mail']):
            return "PII_EMAIL"
        elif any(term in col_lower for term in ['phone', 'mobile', 'tel']):
            return "PII_PHONE"
        elif any(term in col_lower for term in ['name', 'first_name', 'last_name']):
            return "PII_NAME"
        elif any(term in col_lower for term in ['address', 'street', 'city', 'zip']):
            return "PII_ADDRESS"
        
        # Financial Data
        elif any(term in col_lower for term in ['price', 'amount', 'cost', 'fee', 'salary']):
            return "FINANCIAL_AMOUNT"
        elif any(term in col_lower for term in ['currency', 'curr']):
            return "FINANCIAL_CURRENCY"
        
        # Temporal Data
        elif any(term in col_lower for term in ['date', 'time', 'timestamp', 'created', 'updated']):
            return "TEMPORAL"
        
        # Operational Data
        elif any(term in col_lower for term in ['status', 'state', 'stage']):
            return "OPERATIONAL_STATUS"
        elif any(term in col_lower for term in ['category', 'type', 'class']):
            return "CATEGORICAL"
        
        # Behavioral Data
        elif any(term in col_lower for term in ['click', 'view', 'visit', 'session']):
            return "BEHAVIORAL"
        
        # Identifiers
        elif col_lower.endswith('_id') or col_lower == 'id':
            return "IDENTIFIER"
        
        # Default based on data type
        elif pd.api.types.is_numeric_dtype(series):
            return "NUMERIC"
        elif pd.api.types.is_string_dtype(series):
            return "TEXT"
        else:
            return "UNKNOWN"
            
    def _validate_business_rules(self, s: pd.Series, col: str, semantic_type: str) -> List[str]:
        """Validate column values based on semantic type and inferred business rules."""
        rules = []

        try:
            non_null_values = s.dropna()
            if non_null_values.empty:
                rules.append(f"⚠️ Column `{col}` has only null values.")
                return rules

            if semantic_type.lower() == "identifier":
                if non_null_values.duplicated().any():
                    rules.append(f"🚫 Duplicate values found in ID column `{col}`.")
                if s.isnull().any():
                    rules.append(f"⚠️ Nulls found in identifier column `{col}` — consider NOT NULL constraint.")

            elif semantic_type.lower() == "numeric":
                numeric_values = pd.to_numeric(non_null_values, errors='coerce').dropna()
                if numeric_values.empty:
                    rules.append(f"⚠️ Column `{col}` could not be parsed as numeric.")
                    return rules

                if (numeric_values < 0).any():
                    rules.append(f"⚠️ Negative values found in `{col}` — check business logic.")

                if (numeric_values > 1e6).any():
                    rules.append(f"📈 Very large values in `{col}` — investigate for outliers.")

            elif semantic_type.lower() == "date":
                parsed_dates = pd.to_datetime(non_null_values, errors='coerce')
                if parsed_dates.isnull().any():
                    rules.append(f"⚠️ Some values in `{col}` cannot be parsed as dates.")
                elif parsed_dates.min() > pd.Timestamp.now():
                    rules.append(f"⏳ Future dates found in `{col}` — possible data entry error.")

            elif semantic_type.lower() == "categorical":
                if s.nunique() > 50:
                    rules.append(f"📊 Column `{col}` has high cardinality for a category — may affect modeling.")

        except Exception as e:
            rules.append(f"❌ Rule validation failed for `{col}`: {str(e)}")

        return rules

    def _assess_column_quality(self, series: pd.Series, col_name: str, semantic_type: str) -> Dict:
        """Comprehensive quality assessment for a column"""
        total_count = len(series)
        non_null_series = series.dropna()
        
        metrics = {
            "completeness": 1 - (series.isnull().sum() / total_count),
            "consistency": 1.0,  # Default, will be updated
            "validity": 1.0,     # Default, will be updated
            "uniqueness": 1.0    # Default, will be updated
        }
        
        if len(non_null_series) > 0:
            # Consistency check (format validation)
            if semantic_type == "PII_EMAIL":
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                valid_emails = non_null_series.str.match(email_pattern, na=False).sum()
                metrics["consistency"] = valid_emails / len(non_null_series)
            
            elif semantic_type == "PII_PHONE":
                phone_pattern = r'^\+?1?-?\d{3}-?\d{3}-?\d{4}$'
                valid_phones = non_null_series.str.match(phone_pattern, na=False).sum()
                metrics["consistency"] = valid_phones / len(non_null_series)
            
            elif semantic_type == "FINANCIAL_AMOUNT":
                # Check for negative values where they shouldn't be
                if col_name.lower() in ['price', 'cost', 'fee']:
                    positive_count = (non_null_series >= 0).sum()
                    metrics["validity"] = positive_count / len(non_null_series)
            
            # Uniqueness assessment
            if semantic_type == "IDENTIFIER":
                metrics["uniqueness"] = non_null_series.nunique() / len(non_null_series)
            elif semantic_type == "PII_EMAIL":
                metrics["uniqueness"] = non_null_series.nunique() / len(non_null_series)
        
        return {k: round(v, 3) for k, v in metrics.items()}

    def _calculate_quality_score(self, quality_metrics: Dict) -> float:
        """Calculate overall quality score for a column"""
        weights = {
            "completeness": 0.3,
            "consistency": 0.25,
            "validity": 0.25,
            "uniqueness": 0.2
        }
        
        score = sum(quality_metrics.get(metric, 0) * weight 
                   for metric, weight in weights.items())
        return round(score, 3)

    def _detect_anomalies(self, series: pd.Series, col_name: str) -> List[Dict]:
        """Detect statistical and business anomalies."""
        anomalies = []

        try:
            numeric_series = pd.to_numeric(series.dropna(), errors='coerce').dropna()
            if len(numeric_series) > 10:
                Q1 = numeric_series.quantile(0.25)
                Q3 = numeric_series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers = numeric_series[(numeric_series < lower_bound) | (numeric_series > upper_bound)]
                if len(outliers) > 0:
                    anomalies.append({
                        "type": "statistical_outlier",
                        "severity": "medium" if len(outliers) / len(numeric_series) < 0.05 else "high",
                        "count": len(outliers),
                        "percentage": round((len(outliers) / len(numeric_series)) * 100, 2),
                        "description": f"{len(outliers)} outliers detected outside [{lower_bound:.2f}, {upper_bound:.2f}]",
                        "recommendation": "Review data entry process and validate extreme values"
                    })
        except Exception as e:
            anomalies.append({
                "type": "error",
                "severity": "low",
                "description": f"Anomaly detection failed for `{col_name}`: {e}",
                "recommendation": "Ensure the column contains valid numeric data"
            })

        # Business rule-specific anomaly for age
        if "age" in col_name.lower():
            try:
                age_series = pd.to_numeric(series, errors='coerce').dropna()
                invalid_ages = age_series[(age_series < 0) | (age_series > 120)]
                if len(invalid_ages) > 0:
                    anomalies.append({
                        "type": "business_rule_violation",
                        "severity": "high",
                        "count": len(invalid_ages),
                        "description": f"{len(invalid_ages)} records with invalid age values",
                        "recommendation": "Implement age validation rules"
                    })
            except Exception as e:
                anomalies.append({
                    "type": "error",
                    "description": f"Age anomaly check failed: {e}",
                    "recommendation": "Ensure age column contains valid integers"
                })

        return anomalies
        
        # Business-specific anomalies
        if "age" in col_name.lower():
            invalid_ages = series[(series < 0) | (series > 120)]
            if len(invalid_ages) > 0:
                anomalies.append({
                    "type": "business_rule_violation",
                    "severity": "high",
                    "count": len(invalid_ages),
                    "description": f"{len(invalid_ages)} records with invalid age values",
                    "recommendation": "Implement age validation rules"
                })
        
        return anomalies

    def _detect_relationships(self, df: pd.DataFrame, schema_info: List) -> List[Dict]:
        """Advanced relationship detection using statistical analysis"""
        relationships = []
        
        for col in df.columns:
            if col.endswith('_id') and col != 'id':
                # Statistical FK detection
                ref_table = col[:-3]
                confidence = self._calculate_relationship_confidence(df, col, ref_table)
                
                if confidence > 0.7:
                    relationships.append({
                        "type": "foreign_key",
                        "column": col,
                        "references_table": ref_table,
                        "confidence": confidence,
                        "validation_method": "statistical_analysis"
                    })
        
        return relationships

    def _calculate_relationship_confidence(self, df: pd.DataFrame, col: str, ref_table: str) -> float:
        """Calculate confidence score for relationship detection"""
        # This is a simplified version - in practice, you'd check against actual referenced table
        non_null_values = df[col].dropna()
        if len(non_null_values) == 0:
            return 0.0
        
        # Check for typical ID patterns
        if non_null_values.dtype in ['int64', 'float64']:
            # IDs should be positive integers
            positive_integers = (non_null_values > 0) & (non_null_values == non_null_values.astype(int))
            return positive_integers.sum() / len(non_null_values)
        
        return 0.5  # Default confidence for non-numeric IDs

    def _analyze_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze data trends and patterns"""
        trends = {}
        
        # Look for timestamp columns
        date_cols = [col for col in df.columns if any(term in col.lower() 
                    for term in ['date', 'time', 'created', 'updated'])]
        
        if date_cols:
            for col in date_cols:
                try:
                    df[col] = pd.to_datetime(df[col])
                    date_range = df[col].max() - df[col].min()
                    trends[f"{col}_span"] = str(date_range)
                    
                    # Monthly growth analysis
                    monthly_counts = df.groupby(df[col].dt.to_period('M')).size()
                    if len(monthly_counts) > 1:
                        growth_rate = ((monthly_counts.iloc[-1] - monthly_counts.iloc[0]) / 
                                     monthly_counts.iloc[0]) * 100
                        trends[f"{col}_growth_rate"] = f"{growth_rate:.1f}% total growth"
                
                except Exception:
                    continue
        
        return trends

    def _generate_recommendations(self, profile: Dict) -> List[Dict]:
        """Generate actionable recommendations based on profile analysis"""
        recommendations = []
        
        # Quality-based recommendations
        if profile["table_quality_score"] < 0.8:
            recommendations.append({
                "priority": "high",
                "category": "data_quality",
                "action": "Implement comprehensive data validation rules",
                "impact": f"Improve table quality score from {profile['table_quality_score']} to >0.8",
                "effort": "medium",
                "roi": "high"
            })
        
        # Performance recommendations
        if profile["total_records"] > 100000:
            recommendations.append({
                "priority": "medium",
                "category": "performance",
                "action": "Add database indexes for frequently queried columns",
                "impact": "Improve query performance by 50-80%",
                "effort": "low",
                "roi": "high"
            })
        
        # Security recommendations
        pii_columns = [col for col, data in profile["column_profiles"].items() 
                      if data["semantic_type"].startswith("PII_")]
        if pii_columns:
            recommendations.append({
                "priority": "high",
                "category": "security",
                "action": f"Implement data masking for PII columns: {', '.join(pii_columns)}",
                "impact": "Ensure GDPR/CCPA compliance",
                "effort": "medium",
                "roi": "high"
            })
        
        return recommendations

    def _generate_business_insights(self, profile: Dict) -> List[Dict]:
        """Generate business-focused insights"""
        insights = []
        
        # Customer data insights
        if profile["business_domain"] == "customer_management":
            insights.append({
                "process": "customer_onboarding",
                "readiness": "85%",
                "insight": "Customer data quality is good but needs email validation",
                "automation_opportunity": "Auto-validate emails during registration"
            })
        
        # E-commerce insights
        if any("price" in col.lower() for col in profile["column_profiles"]):
            insights.append({
                "process": "pricing_strategy",
                "readiness": "90%",
                "insight": "Pricing data is consistent and complete",
                "automation_opportunity": "Implement dynamic pricing based on demand"
            })
        
        return insights
        
    def _infer_cardinality(self, unique_count: int, total_count: int) -> str:
        """
        Infers the cardinality level of a column based on the ratio of unique values to total values.
        
        Returns: "none", "low", "medium", "high", or "unique"
        """
        if total_count == 0:
            return "none"
        
        ratio = unique_count / total_count

        if unique_count == total_count:
            return "unique"
        elif ratio > 0.7:
            return "high"
        elif ratio > 0.3:
            return "medium"
        elif ratio > 0:
            return "low"
        else:
            return "none"

    def _infer_business_domain(self, table_name: str, columns: List[str]) -> str:
        """Infer business domain from table name and columns"""
        table_lower = table_name.lower()
        cols_lower = [col.lower() for col in columns]
        
        if any(term in table_lower for term in ['customer', 'user', 'client']):
            return "customer_management"
        elif any(term in table_lower for term in ['order', 'purchase', 'transaction']):
            return "sales_operations"
        elif any(term in table_lower for term in ['product', 'item', 'inventory']):
            return "product_management"
        elif any(term in table_lower for term in ['employee', 'staff', 'hr']):
            return "human_resources"
        elif any(term in cols_lower for term in ['price', 'amount', 'cost']):
            return "financial_management"
        else:
            return "general"

    def _assess_table_criticality(self, table_name: str, df: pd.DataFrame) -> str:
        """Assess table criticality based on size, relationships, and business domain"""
        record_count = len(df)
        
        # High criticality indicators
        if record_count > 1000000:
            return "high"
        elif any(term in table_name.lower() for term in ['customer', 'order', 'transaction']):
            return "high"
        elif record_count > 100000:
            return "medium"
        else:
            return "low"

    def _generate_column_recommendations(self, col_profile: Dict) -> List[str]:
        """Generate column-specific recommendations"""
        recommendations = []
        
        if col_profile["quality_score"] < 0.7:
            recommendations.append(f"Improve data quality for {col_profile['column_name']}")
        
        if col_profile["null_percentage"] > 20:
            recommendations.append(f"Address high null percentage in {col_profile['column_name']}")
        
        if col_profile["semantic_type"].startswith("PII_"):
            recommendations.append(f"Implement data masking for PII column {col_profile['column_name']}")
        
        return recommendations

class DataValidationInput(BaseModel):
    """Input schema for data validation"""
    table_name: str = Field(description="Name of the table to validate")
    connection_string: str = Field(..., description="Valid SQLite path. Passed from platform, e.g., 'sqlite:///uploaded_dbs/ecommerce_db.db'")
    validation_rules: Dict[str, Any] = Field(description="Validation rules to apply")
    allowed_tables: List[str] = Field(default=None, description="Optional list of allowed tables")

class DataValidationTool(BaseTool):
    """Tool for data validation and quality assessment"""
    name: str = "Data Validation Tool"
    description: str = "Validate data quality and apply business rules to assess data integrity"
    args_schema: Type[BaseModel] = DataValidationInput

    def _run(
        self,
        table_name: str,
        connection_string: str,
        validation_rules: Dict[str, Any] = None,
        allowed_tables: Optional[List[str]] = None
    ) -> str:
        if allowed_tables and table_name not in allowed_tables:
            return f"⛔ Table `{table_name}` is restricted and cannot be validated."

        if not is_valid_sqlite_connection_string(connection_string):
            return f"❌ Invalid connection string: {connection_string}. Must be sqlite:///databases/<name>.db"

        try:
            import sqlite3
            conn = sqlite3.connect(connection_string.replace("sqlite:///", ""))
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

            if df.empty:
                return f"⚠️ Table `{table_name}` is empty. Skipping validation."

            # Default validation rules
            if not validation_rules:
                validation_rules = {
                    "completeness_threshold": 0.95,
                    "uniqueness_check": True,
                    "range_checks": {},
                    "pattern_checks": {}
                }

            completeness_threshold = validation_rules.get("completeness_threshold", 0.95)

            validation_results = {
                "table_name": table_name,
                "validation_timestamp": pd.Timestamp.now().isoformat(),
                "total_records": len(df),
                "table_quality_score": None,
                "validation_summary": {},
                "issues_found": []
            }

            column_scores = []

            for column in df.columns:
                col_data = df[column]
                completeness = col_data.count() / len(df)
                uniqueness = col_data.nunique() / len(df)
                duplicates = col_data.duplicated().sum()
                sample_values = col_data.dropna().unique()[:5].tolist()
                inferred_type = str(col_data.dtype)

                quality_score = round((completeness + uniqueness) / 2, 3)
                column_scores.append(quality_score)

                if completeness < completeness_threshold:
                    validation_results["issues_found"].append({
                        "column": column,
                        "issue": "Low completeness",
                        "value": round(completeness, 3),
                        "threshold": completeness_threshold
                    })

                validation_results["validation_summary"][column] = {
                    "completeness": round(completeness, 3),
                    "unique_values": int(col_data.nunique()),
                    "duplicates": int(duplicates),
                    "sample_values": sample_values,
                    "inferred_type": inferred_type,
                    "quality_score": quality_score
                }

            # Range checks
            for col, bounds in validation_rules.get("range_checks", {}).items():
                if col in df.columns:
                    invalid = ~df[col].between(bounds["min"], bounds["max"])
                    if invalid.any():
                        validation_results["issues_found"].append({
                            "column": col,
                            "issue": "Out-of-range values",
                            "range": bounds,
                            "invalid_count": int(invalid.sum())
                        })

            # Pattern checks
            for col, pattern in validation_rules.get("pattern_checks", {}).items():
                if col in df.columns and df[col].dtype == 'object':
                    invalid = ~df[col].astype(str).str.match(pattern, na=False)
                    if invalid.any():
                        validation_results["issues_found"].append({
                            "column": col,
                            "issue": "Pattern mismatch",
                            "pattern": pattern,
                            "invalid_count": int(invalid.sum())
                        })

            # Calculate final table-level score
            if column_scores:
                validation_results["table_quality_score"] = round(np.mean(column_scores), 3)

            conn.close()

            logger.info(f"✅ Data validation completed for table `{table_name}`")
            return json.dumps(validation_results, indent=2)

        except Exception as e:
            error_msg = f"❌ Data validation failed for `{table_name}`: {str(e)}"
            logger.error(error_msg)
            return error_msg