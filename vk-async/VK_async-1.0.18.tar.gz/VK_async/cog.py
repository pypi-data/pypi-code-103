

class Cog:
    def __init__(self):
        self.commands = []

    def command(self, name):
        def decorator(fn):
            new_command = {
                'execute': fn,
                'name': name
            }
            def wrapper(ctx):
                fn(ctx)
            self.commands.append(new_command)
            return wrapper
        return decorator
