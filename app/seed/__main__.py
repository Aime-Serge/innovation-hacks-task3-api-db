"""`python -m app.seed --profile default`: build the dataset in-process and report what it holds."""

import argparse
import asyncio
import os
import secrets
import sys

from app.container import build_container
from app.core.config import load_settings
from app.seed import seed


async def main(profile: str) -> int:
    settings = load_settings()
    if settings.is_production:
        print("Refusing to seed: APP_ENV=production.", file=sys.stderr)
        return 1
    given = os.environ.get("SEED_PASSWORD")
    password = given or secrets.token_urlsafe(16)
    result = await seed(build_container(settings), profile, password)
    print(
        f"Seeded profile '{profile}': {result.users} users, {result.projects} projects, "
        f"{result.tasks} tasks, {result.activity} activity items."
    )
    if not given:
        print(f"One-time password for every seeded account: {password}")
    print("The store is in memory. To use this data in a running server, start it with")
    print(f"SEED_PROFILE={profile} (development only).")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load seed data.")
    parser.add_argument("--profile", choices=["default", "empty", "large"], default="default")
    sys.exit(asyncio.run(main(parser.parse_args().profile)))
