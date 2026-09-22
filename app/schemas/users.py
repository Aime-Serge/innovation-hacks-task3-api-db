from typing import Annotated, ClassVar, Literal
from uuid import UUID

from pydantic import Field, StringConstraints, model_validator

from app.domain.enums import Role, Theme
from app.domain.models import User
from app.schemas.base import (
    CLEAN,
    ApiModel,
    AvatarUrl,
    Email,
    Name,
    OutModel,
    PatchModel,
    SearchText,
    TimestampedOut,
)
from app.schemas.common import ListQuery, sort_param

# Passwords are never trimmed: whitespace is part of the secret.
Password = Annotated[
    str, StringConstraints(min_length=12, max_length=128, strip_whitespace=False, pattern=CLEAN)
]
PersonName = Annotated[str, StringConstraints(min_length=1, max_length=60, pattern=CLEAN)]
CountryCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2}$")]


class RegistrationProfile(ApiModel):
    """The professional details captured by the final Task 4 registration flow."""

    discipline: Literal[
        "backend",
        "frontend",
        "full_stack",
        "mobile",
        "devops_cloud",
        "data_ai",
        "security",
        "qa",
        "other",
    ]
    seniority: Literal["student_intern", "junior", "mid", "senior", "lead_or_above"]
    employment_status: Literal["employed", "freelance", "student", "between_roles"]
    company_name: (
        Annotated[str, StringConstraints(min_length=1, max_length=120, pattern=CLEAN)] | None
    ) = None
    job_title: (
        Annotated[str, StringConstraints(min_length=1, max_length=100, pattern=CLEAN)] | None
    ) = None
    country: CountryCode
    city: Annotated[str, StringConstraints(min_length=1, max_length=80, pattern=CLEAN)] | None = (
        None
    )
    time_zone: Annotated[str, StringConstraints(min_length=1, max_length=64, pattern=CLEAN)]
    terms_accepted: bool
    age_confirmed: bool

    @model_validator(mode="after")
    def _working_people_have_work_details(self) -> "RegistrationProfile":
        if self.employment_status in {"employed", "freelance"} and (
            self.company_name is None or self.job_title is None
        ):
            raise ValueError("companyName and jobTitle are required when employed or freelancing.")
        if not self.terms_accepted or not self.age_confirmed:
            raise ValueError("Accept the terms and confirm the minimum age.")
        return self


class Preferences(OutModel):
    theme: Theme = Theme.SYSTEM


class UserCreate(ApiModel):
    # Retain the Task 3 `name` payload while allowing a Task 4-compatible complete registration.
    name: Name | None = Field(default=None, examples=["Ada Lovelace"])
    given_name: PersonName | None = None
    family_name: PersonName | None = None
    email: Email = Field(examples=["ada@example.com"])
    password: Password = Field(description="12 to 128 characters, not equal to the email.")
    avatar_url: AvatarUrl | None = None
    profile: RegistrationProfile | None = None
    preferences: Preferences | None = None
    role: Role | None = Field(
        default=None, description="developer or lead; defaults to developer when omitted."
    )

    @model_validator(mode="after")
    def _registration_shape(self) -> "UserCreate":
        rich = (
            self.profile is not None or self.given_name is not None or self.family_name is not None
        )
        if rich and (self.given_name is None or self.family_name is None or self.profile is None):
            raise ValueError("givenName, familyName and profile must be provided together.")
        if not rich and self.name is None:
            raise ValueError("name is required for a legacy registration.")
        return self


class UserUpdate(PatchModel):
    nullable: ClassVar[frozenset[str]] = frozenset({"avatar_url"})

    name: Name | None = None
    avatar_url: AvatarUrl | None = None
    preferences: Preferences | None = None
    role: Role | None = Field(default=None, description="Only a lead may change a role.")


class UserOut(TimestampedOut):
    id: UUID
    name: str
    given_name: str | None
    family_name: str | None
    email: str
    role: Role
    avatar_url: str | None
    profile: RegistrationProfile | None
    preferences: Preferences

    @classmethod
    def of(cls, user: User) -> "UserOut":
        return cls(
            id=user.id,
            name=user.name,
            given_name=user.given_name,
            family_name=user.family_name,
            email=user.email,
            role=user.role,
            avatar_url=user.avatar_url,
            profile=(
                RegistrationProfile.model_validate(user.profile)
                if user.profile is not None
                else None
            ),
            preferences=Preferences(theme=user.theme),
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UserListQuery(ListQuery):
    sort_fields: ClassVar[tuple[str, ...]] = ("name", "email", "createdAt")
    sort: str | None = sort_param(*sort_fields)
    q: SearchText | None = None
    role: Role | None = None
