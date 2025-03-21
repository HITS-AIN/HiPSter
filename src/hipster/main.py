#!/usr/bin/env python3

from jsonargparse import auto_cli

from hipster import HTMLGenerator, Task


def main(
    html: HTMLGenerator = HTMLGenerator(),
    tasks: list[Task] = [],
    root_path: str = "./HiPSter",
    only_html: bool = False,
):
    """
    Main function to generate HiPS data.

    Args:
        html (HTMLGenerator): An instance of HTMLGenerator to create the HTML page.
        tasks (list[Task]): A list of tasks to perform.
        root_path (str): The root path for the output folder.
        only_html (bool): If True, only generate the HTML page without executing tasks.
    """
    for task in tasks:
        task.root_path = root_path
        task.register(html)
        if not only_html:
            task.execute()

    html.generate(root_path)


def main_cli():
    """
    Command line interface for the main function.
    """
    auto_cli(main, parser_mode="omegaconf")


if __name__ == "__main__":
    main_cli()
