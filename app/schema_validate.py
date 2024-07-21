import sys


def is_subset(user_schema: dict, main_schema: dict) -> bool:
    if not validate_properties(user_schema, main_schema) or not validate_required_field(user_schema, main_schema):
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


def validate_properties(user_schema: dict, main_schema: dict) -> bool:
    user_properties = user_schema.get("properties", {})
    main_properties = main_schema.get("properties", {})
    for field in main_properties.keys():
        if field not in user_properties.keys() or (
            field != "configuration" and user_properties[field].get("type", "") != main_properties[field].get("type")
        ):
            print(f"Field '{field}' is missing in the schema.", file=sys.stderr)
            return False
        elif field in ["kind", "name", "description"] and (
            user_properties[field].get("maxLength", float("inf")) > main_properties[field].get("maxLength")
            or user_properties[field].get("minLength", 0) > main_properties[field].get("maxLength")
        ):
            print(f"Length of field '{field}' is not valid.", file=sys.stderr)
            return False
        elif field == "version" and user_properties[field].get("pattern", "") != main_properties[field].get("pattern"):
            print("Version pattern is not valid.", file=sys.stderr)
            return False

    return True


def validate_required_field(user_schema: dict, main_schema: dict) -> bool:
    if user_schema.get("required", []) != main_schema.get("required", None) or user_schema.get(
        "additionalProperties", True
    ) != main_schema.get("additionalProperties", None):
        print("Required fields of the user schema are not valid.", file=sys.stderr)
        return False
    return True


def validate_configuration(user_configuration: dict, main_configuration: dict) -> bool:
    main_config_props = main_configuration.get("properties", {})
    user_config_props = user_configuration.get("properties", {})
    for field in main_config_props.keys():
        if field not in user_config_props.keys():
            print(f"Field '{field}' is missing in the schema configuration.")
            return False
        elif user_config_props[field].get("type", "") != main_config_props[field].get("type"):
            print(f"Type of field '{field}' is not a valid type in the schema configuration.")
            return False

    return validate_required_field(user_configuration, main_configuration)
