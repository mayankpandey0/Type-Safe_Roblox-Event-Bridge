import argparse
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

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
        run_pipeline(Path(args.schema), Path("out"))
