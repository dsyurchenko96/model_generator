from pathlib import Path

from app.models.main_model import MainModel


def generate_main_schema(filename: str = "schemas/main_schema.json"):
    main_model_schema = MainModel.schema_json(indent=2)
    if not Path(filename).parent.is_dir():
        Path(filename).parent.mkdir(parents=True)
    with open(filename, "w") as f:
        f.write(main_model_schema)


if __name__ == '__main__':
    generate_main_schema()
