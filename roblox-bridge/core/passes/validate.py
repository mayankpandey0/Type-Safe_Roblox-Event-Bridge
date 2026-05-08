class ValidatePass:
    def execute(self, ir_list, registry):
        for event in ir_list:
            if event.name in registry.events:
                raise ValueError(f"Duplicate event name: {event.name}")
            registry.events.add(event.name)
            for field in event.fields:
                if field.type not in registry.types:
                    raise ValueError(f"Missing type reference: {field.type}")
