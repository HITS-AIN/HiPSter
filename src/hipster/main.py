#!/usr/bin/env python3

from jsonargparse import ArgumentParser

from hipster import HTMLGenerator, Task


def main():
    """
    Main function to generate HiPS data.

    Args:
        html (HTMLGenerator): An instance of HTMLGenerator to create the HTML page.
        tasks (list[Task]): A list of tasks to perform.
        root_path (str): The root path for the output folder.
        only_html (bool): If True, only generate the HTML page without executing tasks.
    """

    parser = ArgumentParser(description="Generate HiPS representation.")

    parser.add_class_arguments(HTMLGenerator, "html")
    parser.add_argument("--tasks", type=list[Task], default=[])
    parser.add_argument("--root_path", type=str, default="./HiPSter")
    parser.add_argument("--only_html", type=bool, default=False)
    parser.add_argument("--config", action="config")

    cfg = parser.parse_args()
    html = HTMLGenerator(**cfg.html.as_dict())
    tasks = parser.instantiate_classes(cfg.tasks)

    for task in tasks:
        task.root_path = cfg.root_path
        task.register(html)
        if not cfg.only_html:
            task.execute()

    html.generate(cfg.root_path)


if __name__ == "__main__":
    main()
