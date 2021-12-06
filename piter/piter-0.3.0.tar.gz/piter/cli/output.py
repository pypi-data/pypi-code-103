import typer


def log(message, environment_name="", script=""):
    typer.echo(f"[piter][{environment_name}][{script}]{message}")


def success(message, environment="", script=""):
    log(
        f"[{typer.style('SUCCESS', bold=True, fg=typer.colors.GREEN)}] - {message}",
        environment,
        script,
    )


def error(message, environment="", script=""):
    log(
        f"[{typer.style('ERROR', bold=True, fg=typer.colors.RED)}] - {message}",
        environment,
        script,
    )


def warning(message, environment="", script=""):
    log(
        f"[{typer.style('WARNING', bold=True, fg=typer.colors.YELLOW)}] - {message}",
        environment,
        script,
    )


def info(message, environment="", script=""):
    log(
        f"[{typer.style('INFO', bold=True, fg=typer.colors.BLUE)}] - {message}",
        environment,
        script,
    )


def path(path):
    return typer.style(path, italic=True)


def environment(name):
    return typer.style(name, bold=True)


def dependency(name):
    return typer.style(name, italic=True)


def script(name):
    return typer.style(name, italic=True)
