import os
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader


class HTMLGenerator:
    def __init__(
        self,
        url: str = "http://localhost:8083",
        title: str = "HiPSter",
        aladin_lite_version: str = "latest",
    ) -> None:
        """
        Initialize the HTMLGenerator with the URL and title.
        Args:
            url (str): The URL of the HiPS server.
            title (str): The title of the HiPS data.
            aladin_lite_version (str): The version of Aladin Lite to use.
        """
        self.url = url
        self.title = title
        self._aladin_lite_version = aladin_lite_version
        self._image_layers = []

        self._environment = Environment(
            loader=FileSystemLoader(
                os.path.join(os.path.dirname(__file__), "templates")
            )
        )

    @dataclass
    class ImageLayer:
        name: str
        description: str
        url: str
        order: int

    def add_image_layer(self, image_layer: ImageLayer) -> None:
        """Add an image layer to the HTML page.
        Args:
            layer (str): The image layer to add.
        """
        self._image_layers.append(image_layer)

    def generate(self, output_folder: str, project_name: str) -> None:
        """Generate the HTML page for the HiPS data.
        Args:
            output_folder (str): The folder to save the generated HTML page.
            project_name (str): The name of the project.
        """
        template = self._environment.get_template("index.html")
        html = template.render(title=self.title, image_layers=self._image_layers)
        os.makedirs(output_folder, exist_ok=True)
        with open(os.path.join(output_folder, "index.html"), "w") as f:
            f.write(html)
