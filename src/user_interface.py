from rich.console import Console

console = Console()


def render_title():
    console.print(
        "[bold green]Welcome to conda 🐍 debug knowledge base!",
        justify="center",
    )


def render_result(result):
    pass


if __name__ == "__main__":
    render_title()
