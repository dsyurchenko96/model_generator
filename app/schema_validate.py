import argparse
import json
import sys

import jsonschema
import yaml
from model_generator import generate_model


def main(argv: list[str] = None) -> int:
    main_schema_filename = "main_schema.json"
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--json-schema", type=str, required=True, help="Path to JSON Schema"
    )
    parser.add_argument("--out-dir", type=str, default="rest", help="Output directory")

    args = parser.parse_args(argv)
    if args.json_schema == '':
        parser.error('--json-schema is missing required argument')
        return 1

    try:
        with open(main_schema_filename) as main_schema_file, open(
            args.json_schema
        ) as user_schema_file:
            main_schema = json.load(main_schema_file)
            jsonschema.Draft202012Validator.check_schema(main_schema)

            if args.json_schema.endswith(".yaml"):
                user_schema = yaml.safe_load(user_schema_file)
            else:
                user_schema = json.load(user_schema_file)
                user_schema_string = json.dumps(user_schema)
            jsonschema.Draft202012Validator.check_schema(user_schema)

            if is_subset(user_schema, main_schema):
                print(f"{args.json_schema} is a subset of {main_schema_filename}")
                generate_model(user_schema_string, user_schema, args.out_dir)
            else:
                print(f"{args.json_schema} is NOT a subset of {main_schema_filename}")

    except FileNotFoundError as fnf:
        parser.error(f"{fnf.filename} not found")
        return 1
    except json.decoder.JSONDecodeError:
        parser.error(f"{args.json_schema} is not a valid JSON file")
        return 1
    except jsonschema.exceptions.ValidationError as ve:
        parser.error(ve.message)
        return 1

    return 0


def is_subset(user_schema: dict, main_schema: dict) -> bool:
    user_properties = user_schema.get("properties", {})
    main_properties = main_schema.get("properties", {})
    for field in main_properties.keys():
        if field not in user_properties.keys() or (
            field != "configuration"
            and user_properties[field].get("type", "")
            != main_properties[field].get("type")
        ):
            print(f"Field {field} is missing in the schema", file=sys.stderr)
            return False
        elif field in ["kind", "name", "description"] and user_properties[field].get(
            "maxLength", float("inf")
        ) > main_properties[field].get("maxLength"):
            print(f"Max length of field {field} is not valid", file=sys.stderr)
            return False
        elif field == "version" and user_properties[field].get(
            "pattern", ""
        ) != main_properties[field].get("pattern"):
            print("Version pattern is not valid", file=sys.stderr)
            return False

    if user_schema.get("required", []) != main_schema.get(
        "required", None
    ) or user_schema.get("additionalProperties", True) != main_schema.get(
        "additionalProperties", None
    ):
        print("Required fields are not valid", file=sys.stderr)
        return False

    user_config = get_configuration(user_schema)
    main_config = get_configuration(main_schema)
    return validate_configuration(user_config, main_config)


def get_configuration(schema: dict) -> dict:
    config = schema.get("properties", {}).get("configuration", {})
    if "$ref" in config:
        sub_schema = config["$ref"].split("#/definitions/")[-1]
        config = schema["definitions"].get(sub_schema, {})
    return config


def validate_configuration(user_configuration: dict, main_configuration: dict) -> bool:
    main_config_props = main_configuration.get("properties", {})
    user_config_props = user_configuration.get("properties", {})
    for field in main_config_props.keys():
        if field not in user_config_props.keys():
            print(f"Field {field} is missing in the schema configuration")
            return False
        elif user_config_props[field].get("type", "") != main_config_props[field].get(
            "type"
        ):
            print(
                f"Type of field {field} is not a valid type in the schema configuration"
            )
            return False

    if user_configuration.get("required", []) != main_configuration.get(
        "required", None
    ) or user_configuration.get("additionalProperties", True) != main_configuration.get(
        "additionalProperties", None
    ):
        print("Required fields are not valid in the schema configuration")
        return False

    return True


if __name__ == '__main__':
    exit(main())
