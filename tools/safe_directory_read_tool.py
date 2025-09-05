import os
from typing import List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SafeDirectoryReadInput(BaseModel):
    path: str = Field(..., description="Path to the directory")
    file_types: Optional[List[str]] = Field(default=None, description="List of file extensions to filter (e.g. ['.csv'])")
    recursive: Optional[bool] = Field(default=False, description="Whether to search recursively")

class SafeDirectoryReadTool(BaseTool):
    name: str = "List files in directory"
    description: str = "A tool that lists files in a directory with optional filtering and recursion"
    args_schema: Type[BaseModel] = SafeDirectoryReadInput
    
    def _run(self, path: str, file_types: Optional[List[str]] = None, recursive: Optional[bool] = False) -> str:
        path = os.path.normpath(path)
        if not path.startswith(os.getcwd()):
            return "❌ Path outside allowed directory"
        try:
            if not os.path.exists(path):
                return f"❌ Path does not exist: {path}"
            if not os.path.isdir(path):
                return f"❌ Path is not a directory: {path}"

            files_found = []
            for root, _, files in os.walk(path):
                for file in files:
                    if not file_types or any(file.endswith(ext) for ext in file_types):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, path)
                        files_found.append(rel_path)

                if not recursive:
                    break

            if not files_found:
                return f"ℹ️ No matching files found in: {path}"

            return "\n".join(files_found)

        except Exception as e:
            return f"❌ Failed to list files in {path}: {str(e)}"