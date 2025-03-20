import os

from jinja2 import Environment, FileSystemLoader


class HTMLGenerator:
    def __init__(
        self,
        url: str = "http://localhost:8083",
        title: str = "HiPSter",
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
        self.aladin_lite_version = aladin_lite_version

        self._environment = Environment(
            loader=FileSystemLoader(
                os.path.join(os.path.dirname(__file__), "templates")
            )
        )

    def generate(self, output_folder: str, project_name: str):
        """Generate the HTML page for the HiPS data.
        Args:
            output_folder (str): The folder to save the generated HTML page.
            project_name (str): The name of the project.
        """
        template = self._environment.get_template("index.html")
        html = template.render(title=self.title)
        os.makedirs(output_folder, exist_ok=True)
        with open(os.path.join(output_folder, "index.html"), "w") as f:
            f.write(html)
