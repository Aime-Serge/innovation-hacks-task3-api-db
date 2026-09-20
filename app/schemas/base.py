"""Shared schema base: camelCase, unknown fields rejected, strings trimmed (FR-225, TH-205)."""

from datetime import date, datetime
from typing import Annotated, ClassVar, Self
from urllib.parse import urlparse

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    GetJsonSchemaHandler,
    StringConstraints,
    model_validator,
)
from pydantic.alias_generators import to_camel
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

# Not blank: at least one character no engine treats as whitespace. The class is spelled out
# because Python trims \x1c-\x1f and \x85 while ECMA regexes do not call them whitespace.
NOT_BLANK = r"[^\s\x1c-\x1f\x85]"
# Stated in the schema too, so the document never promises what trimming would then reject.
Name = Annotated[str, StringConstraints(min_length=1, max_length=80, pattern=NOT_BLANK)]
Title = Annotated[str, StringConstraints(min_length=1, max_length=120, pattern=NOT_BLANK)]
SearchText = Annotated[str, StringConstraints(max_length=100)]


def _https_only(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Must be an https URL.")
    return value


# The host is ASCII in the pattern so the schema never promises a URL the parser would refuse.
_HTTPS_PATTERN = (
    r"^https://[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?(:[0-9]{1,5})?([/?#][^ \t\r\n]*)?$"
)
HttpsUrl = Annotated[
    str, StringConstraints(max_length=2048, pattern=_HTTPS_PATTERN), AfterValidator(_https_only)
]

# Whitespace is spelled out as a character class: `\\s` means different things to the Rust regex
# engine and to the ECMA engines that read the schema; a fuzzer found addresses they disagree on.
# A pragmatic address check, stated identically in the schema and the validator (ADR-222): the
# stricter library check also refuses reserved domains such as `.test` that the schema allows.
EMAIL_PATTERN = r"^[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+$"
Email = Annotated[str, StringConstraints(max_length=254, pattern=EMAIL_PATTERN, to_lower=True)]


def _iso_string(value: object) -> object:
    """Dates arrive as `YYYY-MM-DD` strings only; pydantic would also accept a Unix timestamp."""
    if not isinstance(value, str):
        raise ValueError("Must be an ISO 8601 date string (YYYY-MM-DD).")
    return value


IsoDate = Annotated[date, BeforeValidator(_iso_string)]


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_alias=True,
        validate_by_name=False,
        extra="forbid",
        str_strip_whitespace=True,
    )


class OutModel(ApiModel):
    """Responses are built from Python field names, so both spellings are accepted here.

    Requests stay strict: `ApiModel` accepts only the camelCase alias.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_alias=True,
        validate_by_name=True,
        extra="forbid",
        str_strip_whitespace=False,
    )


class PatchModel(ApiModel):
    """A partial update: at least one field, and only nullable fields may be null."""

    nullable: ClassVar[frozenset[str]] = frozenset()

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Document the truth: at least one field, and null only where it is allowed."""
        schema = handler.resolve_ref_schema(handler(core_schema))
        schema["minProperties"] = 1
        for name, info in cls.model_fields.items():
            prop = schema.get("properties", {}).get(info.alias or name)
            if prop is None or name in cls.nullable or "anyOf" not in prop:
                continue
            options = [o for o in prop["anyOf"] if o != {"type": "null"}]
            prop.pop("anyOf")
            prop.update(options[0] if len(options) == 1 else {"anyOf": options})
        return schema

    @model_validator(mode="after")
    def _check_fields(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to change.")
        for name in self.model_fields_set:
            if getattr(self, name) is None and name not in self.nullable:
                raise ValueError(f"{name} may not be null.")
        return self


class TimestampedOut(OutModel):
    created_at: datetime = Field(description="UTC, ISO 8601, ends in Z.")
    updated_at: datetime = Field(description="UTC, ISO 8601, ends in Z.")
