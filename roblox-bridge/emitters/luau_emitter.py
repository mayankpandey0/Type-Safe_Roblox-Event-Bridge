from typing import List
from core.ir_models import TypeRef

def parse_type_ref(fdata) -> TypeRef:
    is_array = False
    is_optional = False
    type_name = fdata
    if isinstance(fdata, dict):
        type_name = fdata.get("type", "string")
        is_array = fdata.get("array", False)
        is_optional = fdata.get("optional", False)
    elif isinstance(fdata, str) and fdata.endswith("[]"):
        type_name = fdata[:-2]
        is_array = True
    elif isinstance(fdata, str) and fdata.endswith("?"):
        type_name = fdata[:-1]
        is_optional = True
    return TypeRef(name=type_name, is_array=is_array, is_optional=is_optional)

class LuauEmitter:
    def emit(self, ir) -> dict:
        ir_list = ir.events if hasattr(ir, "events") else ir
        types = ir.types if hasattr(ir, "types") else {}
        return {
            "Types.luau": self._emit_types(ir_list),
            "ClientBridge.luau": self._emit_client(ir_list),
            "ServerBridge.luau": self._emit_server(ir_list),
            "Validators.luau": self._emit_validators(ir_list, types)
        }

    def _emit_types(self, ir_list) -> str:
        out = ["--!strict"]
        for event in ir_list:
            out.append(f"export type {event.name}Payload = {{")
            for field in event.fields:
                out.append(f"    {field.name}: {field.type},")
            out.append("}")
        return "\n".join(out)

    def _emit_client(self, ir_list) -> str:
        out = ["--!strict", "local Types = require(script.Parent.Types)", "local ClientBridge = {}"]
        for event in ir_list:
            out.append(f"function ClientBridge.Fire{event.name}(payload: Types.{event.name}Payload)")
            if event.encoding == "dict":
                out.append(f"    Remote:FireServer('{event.name}', payload)")
            out.append("end")
        out.append("return ClientBridge")
        return "\n".join(out)

    def _emit_server(self, ir_list) -> str:
        out = [
            "--!strict",
            "local Types = require(script.Parent.Types)",
            "local Validators = require(script.Parent.Validators)",
            "local ServerBridge = {}"
        ]
        out.append("Remote.OnServerEvent:Connect(function(player, eventName, payload)")
        for event in ir_list:
            out.append(f"    if eventName == '{event.name}' then")
            out.append(f"        if not Validators.Validate{event.name}(payload) then")
            out.append("            return")
            out.append("        end")
            if event.encoding == "dict":
                out.append(f"        if ServerBridge.On{event.name} then")
                out.append(f"            ServerBridge.On{event.name}(player, payload)")
                out.append("        end")
            out.append("    end")
        out.append("end)")
        out.append("return ServerBridge")
        return "\n".join(out)

    def _emit_field_validator_lines(self, type_ref, val_name, indent) -> List[str]:
        out = []
        is_opt = type_ref.is_optional
        is_arr = type_ref.is_array
        base_type = type_ref.name
        if base_type in ("int", "float"):
            base_type = "number"

        current_indent = indent
        if is_opt:
            out.append(f"{indent}if {val_name} ~= nil then")
            current_indent = indent + "    "

        if base_type in ("string", "number", "boolean"):
            if is_arr:
                out.append(f"{current_indent}if type({val_name}) ~= 'table' then")
                out.append(f"{current_indent}    return false")
                out.append(f"{current_indent}end")
                out.append(f"{current_indent}for _, val in ipairs({val_name}) do")
                if base_type == "number":
                    out.append(f"{current_indent}    if type(val) ~= 'number' or val ~= val or val == math.huge or val == -math.huge then")
                else:
                    out.append(f"{current_indent}    if type(val) ~= '{base_type}' then")
                out.append(f"{current_indent}        return false")
                out.append(f"{current_indent}    end")
                out.append(f"{current_indent}end")
            else:
                if base_type == "number":
                    out.append(f"{current_indent}if type({val_name}) ~= 'number' or {val_name} ~= {val_name} or {val_name} == math.huge or {val_name} == -math.huge then")
                else:
                    out.append(f"{current_indent}if type({val_name}) ~= '{base_type}' then")
                out.append(f"{current_indent}    return false")
                out.append(f"{current_indent}end")
        else:
            # Custom registered type
            if is_arr:
                out.append(f"{current_indent}if type({val_name}) ~= 'table' then")
                out.append(f"{current_indent}    return false")
                out.append(f"{current_indent}end")
                out.append(f"{current_indent}for _, val in ipairs({val_name}) do")
                out.append(f"{current_indent}    if not Validators.Validate{base_type}(val) then")
                out.append(f"{current_indent}        return false")
                out.append(f"{current_indent}    end")
                out.append(f"{current_indent}end")
            else:
                out.append(f"{current_indent}if not Validators.Validate{base_type}({val_name}) then")
                out.append(f"{current_indent}    return false")
                out.append(f"{current_indent}end")

        if is_opt:
            out.append(f"{indent}end")
        return out

    def _emit_validators(self, ir_list, types=None) -> str:
        if types is None:
            types = {}
        out = ["local Validators = {}"]

        # Emit validators for custom registered types first
        for type_name, type_def in sorted(types.items()):
            if not isinstance(type_def, dict):
                continue
            kind = type_def.get("type")
            if kind == "enum":
                values = type_def.get("values", [])
                disjunctions = []
                for val in values:
                    if isinstance(val, str):
                        disjunctions.append(f"value == '{val}'")
                    else:
                        disjunctions.append(f"value == {val}")
                cond = " or ".join(disjunctions) if disjunctions else "false"
                out.append(f"function Validators.Validate{type_name}(value)")
                out.append(f"    return {cond}")
                out.append("end")
            elif kind == "object":
                out.append(f"function Validators.Validate{type_name}(value)")
                out.append("    if type(value) ~= 'table' then")
                out.append("        return false")
                out.append("    end")
                fields_data = type_def.get("fields", {})
                for fname, fdata in (fields_data or {}).items():
                    type_ref = parse_type_ref(fdata)
                    val_name = f"value.{fname}"
                    field_lines = self._emit_field_validator_lines(type_ref, val_name, "    ")
                    out.extend(field_lines)
                out.append("    return true")
                out.append("end")

        for event in ir_list:
            out.append(f"function Validators.Validate{event.name}(payload)")
            out.append("    if type(payload) ~= 'table' then")
            out.append("        return false")
            out.append("    end")
            for field in event.fields:
                val_name = f"payload.{field.name}"
                field_lines = self._emit_field_validator_lines(field.type_ref, val_name, "    ")
                out.extend(field_lines)
            out.append("    return true")
            out.append("end")
        out.append("return Validators")
        return "\n".join(out)
