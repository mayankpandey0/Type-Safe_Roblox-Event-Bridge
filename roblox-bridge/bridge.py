import argparse
import sys
import yaml
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.registry import GlobalTypeRegistry
from core.compiler import build_ir
from core.passes.validate import ValidatePass
from core.passes.optimize import OptimizePass
from emitters.luau_emitter import LuauEmitter

def run_pipeline(schema_path: Path, out_dir: Path):
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    registry = GlobalTypeRegistry()
    registry.register(schema)

    ir = build_ir(registry, schema)
    
    ValidatePass().execute(ir, registry)
    OptimizePass().execute(ir)

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
