class LuauEmitter:
    def emit(self, ir) -> dict:
        ir_list = ir.events if hasattr(ir, "events") else ir
        return {
            "Types.luau": self._emit_types(ir_list),
            "ClientBridge.luau": self._emit_client(ir_list),
            "ServerBridge.luau": self._emit_server(ir_list),
            "Validators.luau": self._emit_validators(ir_list)
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

    def _emit_validators(self, ir_list) -> str:
        out = ["local Validators = {}"]
        for event in ir_list:
            out.append(f"function Validators.Validate{event.name}(payload)")
            out.append("    if type(payload) ~= 'table' then")
            out.append("        return false")
            out.append("    end")
            for field in event.fields:
                val_name = f"payload.{field.name}"
                is_opt = field.type_ref.is_optional
                is_arr = field.type_ref.is_array
                base_type = field.type_ref.name
                if base_type in ("int", "float"):
                    base_type = "number"

                indent = "    "
                if is_opt:
                    out.append(f"    if {val_name} ~= nil then")
                    indent = "        "

                if is_arr:
                    out.append(f"{indent}if type({val_name}) ~= 'table' then")
                    out.append(f"{indent}    return false")
                    out.append(f"{indent}end")
                    out.append(f"{indent}for _, val in ipairs({val_name}) do")
                    if base_type == "number":
                        out.append(f"{indent}    if type(val) ~= 'number' or val ~= val or val == math.huge or val == -math.huge then")
                    else:
                        out.append(f"{indent}    if type(val) ~= '{base_type}' then")
                    out.append(f"{indent}        return false")
                    out.append(f"{indent}    end")
                    out.append(f"{indent}end")
                else:
                    if base_type == "number":
                        out.append(f"{indent}if type({val_name}) ~= 'number' or {val_name} ~= {val_name} or {val_name} == math.huge or {val_name} == -math.huge then")
                    else:
                        out.append(f"{indent}if type({val_name}) ~= '{base_type}' then")
                    out.append(f"{indent}    return false")
                    out.append(f"{indent}end")

                if is_opt:
                    out.append("    end")
            out.append("    return true")
            out.append("end")
        out.append("return Validators")
        return "\n".join(out)
