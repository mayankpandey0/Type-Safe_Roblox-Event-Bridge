class GlobalTypeRegistry:
    def __init__(self):
        self.types = {"string": "string", "number": "number"}
        self.events = set()

    def register(self, schema: dict):
        if "types" in schema:
            for k, v in schema["types"].items():
                self.types[k] = v
