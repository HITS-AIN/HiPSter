#!/usr/bin/env python3

from jsonargparse import auto_cli

from hipster import HTMLGenerator, Task


def main(
    html: HTMLGenerator = HTMLGenerator(),
    tasks: list[Task] = [],
):
    """
    Main function to generate HiPS data.

    Args:
        url (str): The URL of the HiPS server.
        title (str): The title of the HiPS data.
        output_folder (str): The folder to save the generated HiPS data.
        tasks (list[Task]): A list of tasks to perform.
    """

    for task in tasks:
        task.execute()

    html.generate()


def main_cli():
    """
    Command line interface for the main function.
    """
    auto_cli(main)


if __name__ == "__main__":
    main_cli()
