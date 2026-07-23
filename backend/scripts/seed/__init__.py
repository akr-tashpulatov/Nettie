"""Idempotent database seeders.

Run an individual seeder:

    uv run python -m scripts.seed.users
    uv run python -m scripts.seed.services
    uv run python -m scripts.seed.tariffs

Or run all of them in dependency order (services → tariffs, users):

    uv run python -m scripts.seed
"""
