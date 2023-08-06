""" Schema Tester """
from functools import reduce
from typing import Any, Callable, Dict, List, Optional, Union, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.response import Response

from openapi_tester import type_declarations as td
from openapi_tester.constants import (
    INIT_ERROR,
    UNDOCUMENTED_SCHEMA_SECTION_ERROR,
    VALIDATE_ANY_OF_ERROR,
    VALIDATE_EXCESS_RESPONSE_KEY_ERROR,
    VALIDATE_MISSING_RESPONSE_KEY_ERROR,
    VALIDATE_NONE_ERROR,
    VALIDATE_ONE_OF_ERROR,
    VALIDATE_WRITE_ONLY_RESPONSE_KEY_ERROR,
)
from openapi_tester.exceptions import DocumentationError, UndocumentedSchemaSectionError
from openapi_tester.loaders import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader
from openapi_tester.utils import combine_sub_schemas, merge_objects
from openapi_tester.validators import (
    validate_enum,
    validate_format,
    validate_max_items,
    validate_max_length,
    validate_max_properties,
    validate_maximum,
    validate_min_items,
    validate_min_length,
    validate_min_properties,
    validate_minimum,
    validate_multiple_of,
    validate_pattern,
    validate_type,
    validate_unique_items,
)


class SchemaTester:
    """ Schema Tester: this is the base class of the library. """

    loader: Union[StaticSchemaLoader, DrfSpectacularSchemaLoader, DrfYasgSchemaLoader]
    validators: List[Callable[[dict, Any], Optional[str]]]

    def __init__(
        self,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
        schema_file_path: Optional[str] = None,
        validators: Optional[List[Callable[[dict, Any], Optional[str]]]] = None,
        field_key_map: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Iterates through an OpenAPI schema object and API response to check that they match at every level.

        :param case_tester: An optional callable that validates schema and response keys
        :param ignore_case: An optional list of keys for the case_tester to ignore
        :schema_file_path: The file path to an OpenAPI yaml or json file. Only passed when using a static schema loader
        :raises: openapi_tester.exceptions.DocumentationError or ImproperlyConfigured
        """
        self.case_tester = case_tester
        self.ignore_case = ignore_case or []
        self.validators = validators or []

        if schema_file_path is not None:
            self.loader = StaticSchemaLoader(schema_file_path, field_key_map=field_key_map)
        elif "drf_spectacular" in settings.INSTALLED_APPS:
            self.loader = DrfSpectacularSchemaLoader(field_key_map=field_key_map)
        elif "drf_yasg" in settings.INSTALLED_APPS:
            self.loader = DrfYasgSchemaLoader(field_key_map=field_key_map)
        else:
            raise ImproperlyConfigured(INIT_ERROR)

    @staticmethod
    def get_key_value(schema: dict, key: str, error_addon: str = "") -> dict:
        """
        Returns the value of a given key
        """
        try:
            return schema[key]
        except KeyError as e:
            raise UndocumentedSchemaSectionError(
                UNDOCUMENTED_SCHEMA_SECTION_ERROR.format(key=key, error_addon=error_addon)
            ) from e

    @staticmethod
    def get_status_code(schema: dict, status_code: Union[str, int], error_addon: str = "") -> dict:
        """
        Returns the status code section of a schema, handles both str and int status codes
        """
        if str(status_code) in schema:
            return schema[str(status_code)]
        if int(status_code) in schema:
            return schema[int(status_code)]
        raise UndocumentedSchemaSectionError(
            UNDOCUMENTED_SCHEMA_SECTION_ERROR.format(key=status_code, error_addon=error_addon)
        )

    @staticmethod
    def get_schema_type(schema: dict) -> Optional[str]:
        if "type" in schema:
            return schema["type"]
        if "properties" in schema or "additionalProperties" in schema:
            return "object"
        return None

    def get_response_schema_section(self, response: td.Response) -> Dict[str, Any]:
        """
        Fetches the response section of a schema, wrt. the route, method, status code, and schema version.

        :param response: DRF Response Instance
        :return dict
        """
        schema = self.loader.get_schema()
        response_method = response.request["REQUEST_METHOD"].lower()
        parameterized_path, _ = self.loader.resolve_path(response.request["PATH_INFO"], method=response_method)
        paths_object = self.get_key_value(schema, "paths")

        route_object = self.get_key_value(
            paths_object,
            parameterized_path,
            f"\n\nUndocumented route {parameterized_path}.\n\nDocumented routes: " + "\n\t• ".join(paths_object.keys()),
        )

        method_object = self.get_key_value(
            route_object,
            response_method,
            f"\n\nUndocumented method: {response_method}.\n\nDocumented methods: {[method.lower() for method in route_object.keys() if method.lower() != 'parameters']}.",
        )

        responses_object = self.get_key_value(method_object, "responses")
        status_code_object = self.get_status_code(
            responses_object,
            response.status_code,
            f"\n\nUndocumented status code: {response.status_code}.\n\nDocumented status codes: {list(responses_object.keys())}. ",
        )

        if "openapi" not in schema:
            # openapi 2.0, i.e. "swagger" has a different structure than openapi 3.0 status sub-schemas
            return self.get_key_value(status_code_object, "schema")
        content_object = self.get_key_value(
            status_code_object,
            "content",
            f"\n\nNo content documented for method: {response_method}, path: {parameterized_path}",
        )
        json_object = self.get_key_value(
            content_object,
            "application/json",
            f"\n\nNo `application/json` responses documented for method: {response_method}, path: {parameterized_path}",
        )
        return self.get_key_value(json_object, "schema")

    def handle_all_of(self, schema_section: dict, data: Any, reference: str, **kwargs: Any) -> None:
        all_of = schema_section.pop("allOf")
        self.test_schema_section(
            schema_section={**schema_section, **combine_sub_schemas(all_of)},
            data=data,
            reference=f"{reference}.allOf",
            **kwargs,
        )

    def handle_one_of(self, schema_section: dict, data: Any, reference: str, **kwargs: Any):
        matches = 0
        for option in schema_section["oneOf"]:
            try:
                self.test_schema_section(schema_section=option, data=data, reference=f"{reference}.oneOf", **kwargs)
                matches += 1
            except DocumentationError:
                continue
        if matches != 1:
            raise DocumentationError(f"{VALIDATE_ONE_OF_ERROR.format(matches=matches)}\n\nReference: {reference}.oneOf")

    def handle_any_of(self, schema_section: dict, data: Any, reference: str, **kwargs: Any):
        any_of: List[Dict[str, Any]] = schema_section.get("anyOf", [])
        combined_sub_schemas = map(
            lambda index: reduce(lambda x, y: combine_sub_schemas([x, y]), any_of[index:]),
            range(len(any_of)),
        )

        for schema in [*any_of, *combined_sub_schemas]:
            try:
                self.test_schema_section(schema_section=schema, data=data, reference=f"{reference}.anyOf", **kwargs)
                return
            except DocumentationError:
                continue
        raise DocumentationError(f"{VALIDATE_ANY_OF_ERROR}\n\nReference: {reference}.anyOf")

    @staticmethod
    def test_is_nullable(schema_item: dict) -> bool:
        """
        Checks if the item is nullable.

        OpenAPI 3 ref: https://swagger.io/docs/specification/data-models/data-types/#null
        OpenApi 2 ref: https://help.apiary.io/api_101/swagger-extensions/

        :param schema_item: schema item
        :return: whether or not the item can be None
        """
        openapi_schema_3_nullable = "nullable"
        swagger_2_nullable = "x-nullable"
        return any(
            nullable_key in schema_item and schema_item[nullable_key]
            for nullable_key in [openapi_schema_3_nullable, swagger_2_nullable]
        )

    def test_key_casing(
        self,
        key: str,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
    ) -> None:
        tester = case_tester or getattr(self, "case_tester", None)
        ignore_case = [*self.ignore_case, *(ignore_case or [])]
        if tester and key not in ignore_case:
            tester(key)

    def test_schema_section(
        self,
        schema_section: dict,
        data: Any,
        reference: str = "init",
        validators: Optional[List[Callable[[dict, dict], Optional[str]]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        This method orchestrates the testing of a schema section
        """
        if data is None:
            if self.test_is_nullable(schema_section):
                # If data is None and nullable, we return early
                return
            raise DocumentationError(
                f"{VALIDATE_NONE_ERROR}\n\n"
                f"Reference: {reference}\n\n"
                f"Hint: Return a valid type, or document the value as nullable"
            )

        if "oneOf" in schema_section:
            if schema_section["oneOf"] and all(item.get("enum") for item in schema_section["oneOf"]):
                # handle the way drf-spectacular is doing enums
                one_of = schema_section.pop("oneOf")
                schema_section = {**schema_section, **merge_objects(one_of)}
            else:
                self.handle_one_of(schema_section=schema_section, data=data, reference=reference, **kwargs)
                return
        if "allOf" in schema_section:
            self.handle_all_of(schema_section=schema_section, data=data, reference=reference, **kwargs)
            return
        if "anyOf" in schema_section:
            self.handle_any_of(schema_section=schema_section, data=data, reference=reference, **kwargs)
            return

        schema_section_type = self.get_schema_type(schema_section)
        if not schema_section_type:
            return
        combined_validators = cast(
            List[Callable],
            [
                validate_type,
                validate_format,
                validate_pattern,
                validate_multiple_of,
                validate_minimum,
                validate_maximum,
                validate_unique_items,
                validate_min_length,
                validate_max_length,
                validate_min_items,
                validate_max_items,
                validate_max_properties,
                validate_min_properties,
                validate_enum,
                *self.validators,
                *(validators or []),
            ],
        )
        for validator in combined_validators:
            error = validator(schema_section, data)
            if error:
                raise DocumentationError(f"\n\n{error}\n\nReference: {reference}")

        if schema_section_type == "object":
            self.test_openapi_object(schema_section=schema_section, data=data, reference=reference, **kwargs)
        elif schema_section_type == "array":
            self.test_openapi_array(schema_section=schema_section, data=data, reference=reference, **kwargs)

    def test_openapi_object(
        self,
        schema_section: dict,
        data: dict,
        reference: str,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
    ) -> None:
        """
        1. Validate that casing is correct for both response and schema
        2. Check if any required key is missing from the response
        3. Check if any response key is not in the schema
        4. Validate sub-schema/nested data
        """

        properties = schema_section.get("properties", {})
        write_only_properties = [key for key in properties.keys() if properties[key].get("writeOnly")]
        required_keys = [key for key in schema_section.get("required", []) if key not in write_only_properties]
        response_keys = data.keys()
        additional_properties: Optional[Union[bool, dict]] = schema_section.get("additionalProperties")
        if not properties and isinstance(additional_properties, dict):
            properties = additional_properties
        for key in properties.keys():
            self.test_key_casing(key, case_tester, ignore_case)
            if key in required_keys and key not in response_keys:
                raise DocumentationError(
                    f"{VALIDATE_MISSING_RESPONSE_KEY_ERROR.format(missing_key=key)}\n\nReference: {reference}."
                    f"object:key:{key}\n\nHint: Remove the key from your"
                    f" OpenAPI docs, or include it in your API response"
                )
        for key in response_keys:
            self.test_key_casing(key, case_tester, ignore_case)
            key_in_additional_properties = isinstance(additional_properties, dict) and key in additional_properties
            additional_properties_allowed = additional_properties is True
            if key not in properties and not key_in_additional_properties and not additional_properties_allowed:
                raise DocumentationError(
                    f"{VALIDATE_EXCESS_RESPONSE_KEY_ERROR.format(excess_key=key)}\n\nReference: {reference}.object:key:"
                    f"{key}\n\nHint: Remove the key from your API response, or include it in your OpenAPI docs"
                )
            if key in write_only_properties:
                raise DocumentationError(
                    f"{VALIDATE_WRITE_ONLY_RESPONSE_KEY_ERROR.format(write_only_key=key)}\n\nReference: {reference}"
                    f".object:key:{key}\n\nHint: Remove the key from your API response, or remove the "
                    f'"WriteOnly" restriction'
                )
        for key, value in data.items():
            self.test_schema_section(
                schema_section=properties[key],
                data=value,
                reference=f"{reference}.object:key:{key}",
                case_tester=case_tester,
                ignore_case=ignore_case,
            )

    def test_openapi_array(self, schema_section: dict, data: dict, reference: str, **kwargs: Any) -> None:
        for datum in data:
            self.test_schema_section(
                # the items keyword is required in arrays
                schema_section=schema_section["items"],
                data=datum,
                reference=f"{reference}.array.item",
                **kwargs,
            )

    def validate_response(
        self,
        response: Response,
        case_tester: Optional[Callable[[str], None]] = None,
        ignore_case: Optional[List[str]] = None,
        validators: Optional[List[Callable[[dict, Any], Optional[str]]]] = None,
    ):
        """
        Verifies that an OpenAPI schema definition matches an API response.

        :param response: The HTTP response
        :param case_tester: Optional Callable that checks a string's casing
        :param ignore_case: Optional list of keys to ignore in case testing
        :param validators: Optional list of validator functions
        :raises: ``openapi_tester.exceptions.DocumentationError`` for inconsistencies in the API response and schema.
                 ``openapi_tester.exceptions.CaseError`` for case errors.
        """
        response_schema = self.get_response_schema_section(response)
        self.test_schema_section(
            schema_section=response_schema,
            data=response.json(),
            case_tester=case_tester or self.case_tester,
            ignore_case=ignore_case,
            validators=validators,
        )
