import os

from jinja2 import Template

# placeholders = {
#     'model_dir': 'models',
#     'main_model': 'Test',
#     'config_model': 'TestConfig',
#     'kind': 'test',
# }


def generate_router(values: dict[str, str], filename: str, output_dir: str):
    template_directory = os.path.dirname(os.path.abspath(__file__)) + '/../templates'
    with open(f'{template_directory}/router_template.jinja') as f:
        content = f.read()

    template = Template(content)
    rendered_form = template.render(values)

    with open(f'{output_dir}/{filename}Router.py', 'w') as f:
        f.write(rendered_form)
