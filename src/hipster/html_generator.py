import os

from jinja2 import Environment, FileSystemLoader


class HTMLGenerator:
    def __init__(
        self,
        url: str = "http://localhost:8083",
        title: str = "HiPSter",
        output_folder: str = "./HiPSter",
        aladin_lite_version: str = "latest",
    ):
        """
        Initialize the HTMLGenerator with the URL and title.
        Args:
            url (str): The URL of the HiPS server.
            title (str): The title of the HiPS data.
            aladin_lite_version (str): The version of Aladin Lite to use.
        """
        self.url = url
        self.title = title
        self.output_folder = output_folder
        self.aladin_lite_version = aladin_lite_version

        environment = Environment(
            loader=FileSystemLoader(
                os.path.join(os.path.dirname(__file__), "templates")
            )
        )
        template = environment.get_template("index.html")
        self.html = template.render(title=title)

    def generate(self):
        os.makedirs(self.output_folder, exist_ok=True)
        with open(os.path.join(self.output_folder, "index.html"), "w") as f:
            f.write(self.html)
