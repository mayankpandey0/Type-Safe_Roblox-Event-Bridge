import json
import logging
from typing import Dict, Any, List
from .registry import TypeRegistry
from .ir_models import SchemaIR, EventIR
from .passes.normalize import NormalizePass
from .passes.validate import ValidatePass
from .passes.optimize import OptimizePass

class Compiler:
    def __init__(self):
        self.registry = TypeRegistry()
        self.normalize_pass = NormalizePass(self.registry)
        self.validate_pass = ValidatePass(self.registry)
        self.optimize_pass = OptimizePass(self.registry)
        
    def compile_schema(self, schema: Dict[str, Any]) -> SchemaIR:
        """
        Processes a raw schema dictionary into an optimized SchemaIR.
        Applies registry population, normalization, validation, and optimization passes.
        """
        # 1. Register distinct types (enums, objects) ahead of normalization
        for type_name, type_def in schema.get("types", {}).items():
             self.registry.register_type(type_name, type_def)
             
        # Resolve and detect cycles immediately
        for type_name in schema.get("types", {}).keys():
             self.registry.resolve_type(type_name)

        # 2. Normalize events directly to generic IR, resolving refs
        ir_list = self.normalize_pass.execute(schema)

        # 3. Validate semantic rules on IR
        ir_list = self.validate_pass.execute(ir_list)

        # 4. Optimize IR memory layouts / wire formats
        ir_list = self.optimize_pass.execute(ir_list)

        return SchemaIR(
             version=schema.get("version", "1.0.0"),
             types=self.registry.types,
             events=ir_list
        )
