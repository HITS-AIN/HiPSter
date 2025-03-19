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


if __name__ == "__main__":
    auto_cli(main)
