import argparse
import json
import jsonschema
import yaml
import sys
from pprint import pprint

def main(argv: list[str] = None) -> int:
    main_schema_filename = "user_schema1.json"
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

            jsonschema.validate(user_schema, main_schema)

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

# def is_subset(user_schema, main_schema) -> bool:


if __name__ == '__main__':
    exit(main())
