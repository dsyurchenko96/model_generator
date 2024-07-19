import argparse
import json
import jsonschema
import yaml
import sys
from pprint import pprint

from main_schema_gen import semver_regex
from model_generator import generate_model


def main(argv: list[str] = None) -> int:
    main_schema_filename = "main_schema.json"
    parser = argparse.ArgumentParser()

    parser.add_argument("--json-schema", type=str, required=True, help="Path to JSON Schema")
    parser.add_argument("--out-dir", type=str, default="rest", help="Output directory")

    args = parser.parse_args(argv)
    # print(args)
    if args.json_schema == '':
        parser.error('--json-schema is missing required argument')
        return 1

    try:
        with open(main_schema_filename, "r") as main_schema_file, open(args.json_schema, "r") as user_schema_file:
            main_schema = json.load(main_schema_file)
            # print(validator)
            if args.json_schema.endswith(".yaml"):
                user_schema = yaml.safe_load(user_schema_file)
                # json.dump(json_schema, sys.stdout, indent=2)
            else:
                user_schema = json.load(user_schema_file)
                user_schema_string = json.dumps(user_schema)

            if validate_subset(user_schema):
                print(f"{args.json_schema} is a subset of {main_schema_filename}")
                generate_model(user_schema_string, user_schema, args.out_dir)
            else:
                print(f"{args.json_schema} is NOT a subset of {main_schema_filename}")

    except FileNotFoundError as fnf:
        parser.error(f"{fnf.filename} not found")
        return 1
    except json.decoder.JSONDecodeError as jde:
        parser.error(f"{args.json_schema} is not a valid JSON file")
        return 1
    except jsonschema.exceptions.ValidationError as ve:
        parser.error(ve.message)
        return 1

    return 0


def validate_subset(user_schema) -> bool:
    max_field_lengths = {
        "kind": 32,
        "name": 128,
        "description": 4096,
    }
    properties = user_schema["properties"]
    for field, length in max_field_lengths.items():
        if field not in properties \
                or length > properties[field]["maxLength"] \
                or properties[field]["type"] != "string":
            print(f"Field {field} is not a valid field in the schema")
            return False

    if "version" not in properties \
            or "pattern" not in properties["version"] \
            or properties["version"]["pattern"] != semver_regex \
            or properties["version"]["type"] != "string":
        print(f"Field version is not a valid field in the schema")
        return False

    if user_schema["required"] != ["kind", "name", "description", "version", "configuration"] \
            or user_schema["additionalProperties"] is not False:
        print(f"Field configuration is not a valid field in the schema")
        return False

    if "configuration" not in properties:
        return False

    config = properties["configuration"]
    if "$ref" in config:
        sub_schema = config["$ref"].split("#/definitions/")[-1]
        if sub_schema not in user_schema["definitions"]:
            print(f"Field {sub_schema} is not a valid field in the schema definitions")
            return False
        config = user_schema["definitions"][sub_schema]

    return validate_configuration(config)


def validate_configuration(configuration: dict) -> bool:

    for spec in ["specification", "settings"]:
        if spec not in configuration["properties"] \
                or configuration["properties"][spec]["type"] != "object"\
                or spec not in configuration["required"]:
            return False

    return configuration["additionalProperties"] is False


if __name__ == '__main__':
    exit(main())
