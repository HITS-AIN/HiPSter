#!/usr/bin/env python3

from jsonargparse import ArgumentParser

from hipster import HTMLGenerator, Task


def main():
    """
    Main function to generate HiPS data.
    """

    parser = ArgumentParser(description="Generate HiPS representation.")

    parser.add_class_arguments(HTMLGenerator, "html")
    parser.add_argument("--tasks", type=list[Task], default=[])
    parser.add_argument("--root_path", type=str, default="./HiPSter")
    parser.add_argument("--only_html", action="store_true", default=False)
    parser.add_argument("--config", action="config")
    parser.add_argument(
        "--verbose", "-v", default=0, action="count", help="Print level."
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing files."
    )

    cfg = parser.parse_args()
    html = HTMLGenerator(**cfg.html.as_dict())
    # tasks = parser.instantiate_classes(cfg.tasks)

    # if cfg.verbose:
    #     print("Tasks:")
    #     for task in tasks:
    #         print(f"  - {task.__class__.__name__}")

    # for task in tasks:
    #     task.root_path = cfg.root_path
    #     task.register(html)
    #     if not cfg.only_html:
    #         task.execute()

    html.generate(cfg.root_path)


if __name__ == "__main__":
    main()
