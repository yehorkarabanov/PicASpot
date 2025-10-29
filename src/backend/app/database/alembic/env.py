import asyncio
from logging.config import fileConfig
from typing import Any

from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.database.base import Base
from app.settings import settings

# Import all models here for autogenerate to detect them
from app.user.models import User  # noqa: F401
from app.area.models import Area  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def include_object(
    object: Any,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: Any
) -> bool:
    """
    Exclude PostGIS system tables and schemas from Alembic autogeneration.
    This prevents Alembic from trying to drop PostGIS extension tables.
    """
    # Exclude PostGIS Tiger Geocoder tables
    if type_ == "table":
        # List of PostGIS system tables to exclude
        postgis_tables = [
            'spatial_ref_sys',
            'geocode_settings',
            'geocode_settings_default',
            'pagc_gaz',
            'pagc_lex',
            'pagc_rules',
            'addr',
            'addrfeat',
            'bg',
            'county',
            'county_lookup',
            'countysub_lookup',
            'cousub',
            'direction_lookup',
            'edges',
            'faces',
            'featnames',
            'place',
            'place_lookup',
            'secondary_unit_lookup',
            'state',
            'state_lookup',
            'street_type_lookup',
            'tabblock',
            'tabblock20',
            'tract',
            'zcta5',
            'zip_lookup',
            'zip_lookup_all',
            'zip_lookup_base',
            'zip_state',
            'zip_state_loc',
            'loader_lookuptables',
            'loader_platform',
            'loader_variables',
            'topology',
            'layer',
        ]
        if name in postgis_tables:
            return False

    # Exclude PostGIS schemas
    if hasattr(object, 'schema') and object.schema in ['tiger', 'tiger_data', 'topology']:
        return False

    # Use GeoAlchemy2's include_object for geometry-related filtering
    return alembic_helpers.include_object(object, name, type_, reflected, compare_to)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        process_revision_directives=alembic_helpers.writer,
        render_item=alembic_helpers.render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
        process_revision_directives=alembic_helpers.writer,
        render_item=alembic_helpers.render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
