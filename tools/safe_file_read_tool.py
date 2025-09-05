# tools/safe_file_read_tool.py

from crewai_tools import FileReadTool
from typing import Optional, Type
from pydantic import BaseModel, Field


class SafeFileReadInput(BaseModel):
    file_path: str = Field(..., description="Path to the file")
    line_count: Optional[int] = Field(default=None, description="Number of lines to read from the file")


class SafeFileReadTool(FileReadTool):
    name: str = "Read a file's content"
    description: str = "A tool that reads the content of a file. Provide 'file_path'. Optionally use 'line_count'."
    # args_schema: Type[BaseModel] = SafeFileReadInput
    args_schema: Type[BaseModel] = SafeFileReadInput

    def _run(self, file_path: str, line_count: Optional[int] = None) -> str:
        # Normalize line_count if passed as a string (for robustness)
        if isinstance(line_count, str):
            if line_count.strip().lower() in ["none", ""]:
                line_count = None
            elif line_count.isdigit():
                line_count = int(line_count)
            else:
                raise ValueError(f"Invalid value for line_count: {line_count}")

        return super()._run(file_path=file_path, line_count=line_count)