from datamodel_code_generator import InputFileType, DataModelType, generate
from pathlib import Path
from tempfile import TemporaryDirectory


def generate_model(schema_string, schema, output_dir):
    if not Path(output_dir).exists():
        Path(output_dir).mkdir(parents=True)

    kind = schema["properties"]["kind"]["title"]
    output_name = f"{kind}Model.py"
    output = Path(f"{output_dir}/{output_name}")


    generate(
        schema_string,
        input_file_type=InputFileType.JsonSchema,
        input_filename="example.json",
        output=output,
        # set up the output model types
        output_model_type=DataModelType.PydanticBaseModel,
    )
    model: str = output.read_text()
    with open(output, "w") as file:
        file.write(model)




