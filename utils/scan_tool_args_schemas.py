import os
import importlib.util
import inspect
import traceback
from pathlib import Path
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel


def scan_tool_args_schemas(tools_path: Path):
    print(f"🔍 Scanning for tools in the '{tools_path}' directory...\n")

    if not tools_path.exists():
        print(f"❌ Could not find tools directory at: {tools_path}")
        return

    py_files = list(tools_path.rglob("*.py"))
    print(f"📦 Found {len(py_files)} Python file(s) in tools directory.")

    total_tools = 0
    issues = []

    for py_file in py_files:
        module_name = py_file.stem
        try:
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseTool) and obj is not BaseTool:
                        total_tools += 1
                        tool_cls: Type[BaseTool] = obj
                        if not hasattr(tool_cls, "args_schema"):
                            issues.append(f" - {tool_cls.__name__}: ❌ Missing `args_schema`")
                        else:
                            schema = getattr(tool_cls, "args_schema")
                            if not (inspect.isclass(schema) and issubclass(schema, BaseModel)):
                                issues.append(f" - {tool_cls.__name__}: ❌ Invalid `args_schema` (must inherit from BaseModel)")

        except Exception as e:
            issues.append(f" - {module_name}: ❌ Import error: {str(e).strip()}")
            traceback.print_exc()

    print(f"\n🔍 Scanned {total_tools} tool(s).")
    if issues:
        print("⚠️ Issues found:")
        for issue in issues:
            print(issue)
    else:
        print("✅ All tools have valid `args_schema` definitions.")


# CLI entry point
if __name__ == "__main__":
    root = Path(__file__).parent.parent
    tools_dir = root / "tools"
    scan_tool_args_schemas(tools_dir)
