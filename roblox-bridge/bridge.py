import argparse
import sys
import yaml
from pathlib import Path

# Resolve absolute path to the project root
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.append(str(project_root / "roblox-bridge"))

from core.compiler import Compiler
from emitters.luau_emitter import LuauEmitter

def run_pipeline(schema_path: Path, out_dir: Path):
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    compiler = Compiler()
    ir = compiler.compile_schema(schema)

    emitter = LuauEmitter()
    files = emitter.emit(ir)

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        with open(out_dir / name, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--schema", default="schemas/test.yaml")
    args = parser.parse_args()
    
    if args.command == "generate":
        schema_path = Path(args.schema)
        if not schema_path.is_absolute():
            schema_path = project_root / schema_path
            
        out_dir = Path("out")
        if not out_dir.is_absolute():
            out_dir = project_root / out_dir
            
        run_pipeline(schema_path, out_dir)
