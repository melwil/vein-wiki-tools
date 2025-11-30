from jinja2 import Environment, PackageLoader, Template, select_autoescape

env = Environment(
    loader=PackageLoader("vein_wiki_tools", "templates"),
    autoescape=select_autoescape(),
)


async def get_template(template_name: str) -> Template:
    return env.get_template(template_name)
