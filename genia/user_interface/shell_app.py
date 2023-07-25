import cmd


class ShellApp(cmd.Cmd):
    def __init__(self, provider):
        super().__init__()
        self.provider = provider

    prompt = "# "

    def default(self, line):
        msg = self.provider.process_message(line)
        print(msg)
