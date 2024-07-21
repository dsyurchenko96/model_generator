import json
from pathlib import Path

from datamodel_code_generator import DataModelType, InputFileType, generate
from jsonschema.exceptions import ValidationError


def generate_model(schema: dict, filename: str, output_dir: str):
    schema_string = json.dumps(schema)
    kind = schema.get("properties", {}).get("kind", {}).get("title", "")
    if not kind:
        raise ValidationError(f"Kind is not defined in '{filename}', check the schema for validity.")
    output_name = f"{kind}Model.py"
    output = Path(f"{output_dir}/{output_name}")

    generate(
        schema_string,
        input_file_type=InputFileType.JsonSchema,
        input_filename=filename,
        output=output,
        output_model_type=DataModelType.PydanticBaseModel,
    )
    model: str = output.read_text()
    with open(output, "w") as file:
        file.write(model)
    print(f"Generated model '{output}'")
