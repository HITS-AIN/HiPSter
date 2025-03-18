from jinja2 import Environment, FileSystemLoader

title = "Gaia DR3"

environment = Environment(loader=FileSystemLoader("./aladin-lite/templates"))
template = environment.get_template("index.html")

html = template.render(
    title=title,
    aladin_lite_version="latest",
    hips_server_url="http://localhost:8083",
    hips_server_name="Gaia DR3",
    hips_server_description="Gaia DR3 HiPS server",
)
with open("index.html", "w") as f:
    f.write(html)
