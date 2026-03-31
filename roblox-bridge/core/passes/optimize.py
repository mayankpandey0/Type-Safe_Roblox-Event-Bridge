class OptimizePass:
    def execute(self, ir_list):
        for event in ir_list:
            event.encoding = "dict"
