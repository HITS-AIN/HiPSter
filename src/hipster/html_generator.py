from jinja2 import Environment, FileSystemLoader


class HTMLGenerator:
    def __init__(self, url, title, aladin_lite_version="latest"):
        """
        Initialize the HTMLGenerator with the URL and title.
        Args:
            url (str): The URL of the HiPS server.
            title (str): The title of the HiPS data.
            aladin_lite_version (str): The version of Aladin Lite to use.
        """
        self.title = title
        self.url = url
        self.aladin_lite_version = aladin_lite_version

        environment = Environment(loader=FileSystemLoader("./templates"))
        template = environment.get_template("index.html")
        self.html = template.render(title=title)

    def generate(self):
        with open("index.html", "w") as f:
            f.write(self.html)
