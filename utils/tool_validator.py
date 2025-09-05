# utils/tool_validator.py

from typing import Type
from crewai.tools import BaseTool
from pydantic import ValidationError

def validate_tool_args(tool_class: Type[BaseTool], args: dict):
    """
    Validates arguments against a CrewAI tool's defined args_schema.

    Parameters:
    - tool_class: The tool class (not an instance) that inherits from BaseTool.
    - args: The input arguments dictionary to validate.

    Returns:
    - (True, validated_instance): If validation succeeds.
    - (False, error_message): If validation fails.
    """
    try:
        schema_model = tool_class.args_schema
        validated = schema_model(**args)
        return True, validated
    except ValidationError as ve:
        return False, ve.errors()
    except Exception as e:
        return False, str(e)
