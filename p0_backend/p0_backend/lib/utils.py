def log_string(string) -> str:
    return str(string).replace("<", "\\<")


def nop(*_, **__):
    pass


def nop_decorator(*_, **__):
    return nop
