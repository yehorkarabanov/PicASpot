Postgres Backup Manager (interactive)

This folder contains an interactive, menu-driven Postgres backup and restore manager designed to run inside the project's `backup` container.

Files
- `backup.sh`: Interactive + CLI script. Run inside the `backup` container.

Features
- Create full cluster dumps (pg_dumpall -> compressed .sql.gz)
- Create single-database dumps (pg_dump -> custom .dump archived to .tar.gz)
- List, inspect, restore, and delete backups from an easy interactive UI
- CLI flags for automation: `backup`, `list`, `restore <file>`, `cleanup`
- Colorful, spinner-driven UI inspired by the provided Mongo script

How it works
- The `backup` service in `docker-compose.yaml` mounts this folder at `/backup` and the host `./backups` to `/backups` in the container.
- The script expects standard Postgres client tools to be available in the image (psql, pg_dump, pg_dumpall, pg_restore, gzip, tar). The `postgis/postgis` image already includes these.
- Backups are written to `/backups` (host: `./backups`).

Run it (from repository root, Windows cmd.exe)

1) Run the interactive manager:

```cmd
docker exec -it backup /backup/backup.sh
```

CLI / Direct Commands
- Create a new backup (interactive create menu):

```cmd
docker compose exec backup /backup/backup.sh backup
```

- Create a specific DB dump non-interactively:

```cmd
docker compose exec backup /backup/backup.sh backup mydatabase
```

- List existing backups (non-interactive):

```cmd
docker compose exec backup /backup/backup.sh list
```

- Restore from a backup (non-interactive):

```cmd
docker compose exec backup /backup/backup.sh restore postgres_backup_mydb_20250101_120000.tar.gz
```

- Cleanup (interactive prompt):

```cmd
docker compose exec backup /backup/backup.sh cleanup
```

Backup location and filename conventions
- Container path: `/backups`
- Host path (project root): `./backups` (the compose service mounts this)
- Filenames:
  - Full cluster dumps: `postgres_backup_YYYYMMDD_HHMMSS.sql.gz`
  - Single-db dumps: `postgres_backup_<DBNAME>_YYYYMMDD_HHMMSS.tar.gz` (contains a single .dump file)

Environment variables (read from the container environment, typically via `.env` used by docker-compose)
- `POSTGRES_HOST` -> PGHOST (default: `postgres`)
- `POSTGRES_PORT_INTERNAL` -> PGPORT (default: `5432`)
- `POSTGRES_USER` -> PGUSER (default: `postgres`)
- `POSTGRES_PASSWORD` -> used as PGPASSWORD if `PGPASSWORD` not already set
- `POSTGRES_DB` -> DEFAULT_DB (default: `postgres`)
- `BACKUP_DIR` -> override backup directory inside container (default: `/backups`)

Notes and safety
- Restores can overwrite existing data. The script prompts before any destructive operation.
- The script will check for required commands and exit with a helpful message if any are missing.
- Keep your `.env` secure (it contains DB credentials used by the container).

Non-interactive automation
- The script supports CLI arguments so it can be used from scheduled jobs or CI:
  - `backup` (optionally with DB name)
  - `list`
  - `restore <file>`
  - `cleanup`

Example non-interactive scheduled command (host cron or CI):
- Run a full cluster dump and keep it on the host `./backups` (example run from host):

```cmd
docker compose exec backup /backup/backup.sh backup
```

Troubleshooting
- If a required command is missing, make sure the container image contains Postgres client tools.
- If a write fails, verify permissions on the host `./backups` directory.
- If the script cannot connect, ensure the Postgres container is running and the env vars are correct.

Next steps / optional improvements
- Add optional S3/remote upload and optional GPG encryption for backups
- Add automatic rotation policy and retention rules (non-interactive CLI friendly)
- Add a small smoke-test to verify backup integrity after creation

Credits
Created by Shevchenko Denys @ LilConsul
