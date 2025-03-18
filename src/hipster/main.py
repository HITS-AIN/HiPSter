from jsonargparse import auto_cli

from hipster import HTMLGenerator, Task


def main(
    url: str = "http://localhost:8083",
    title: str = "gaia",
    output_folder: str = "./HiPSter",
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


if __name__ == "__main__":
    auto_cli(main)
