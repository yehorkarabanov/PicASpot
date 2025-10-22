#!/usr/bin/env bash

# Postgres Backup and Restore Interactive Console

# Ensure we're running under bash (re-exec with bash if not)
if [ -z "${BASH_VERSION-}" ]; then
  if command -v bash >/dev/null 2>&1; then
    exec bash "$0" "$@"
  else
    printf "%b\n" "\n${RED}Error: Bash is required to run this script but was not found in the container.${NC}"
    printf "%b\n" "Use an image with bash (for example: postgis/postgis:18-3.6) or install bash in the container."
    exit 1
  fi
fi

# Detect CRLF line endings that commonly occur when editing on Windows
if grep -q $'\r' "$0" 2>/dev/null; then
  printf "%b\n" "\n${YELLOW}Warning: Detected CRLF (Windows) line endings in %s${NC}" "$0"
  printf "%b\n" "This can cause scripts to fail inside Linux containers. Fix with one of:\n  dos2unix %s\n  sed -i 's/\r$//' %s\nOr configure git: git config core.autocrlf false" "$0" "$0"
  # don't exit; the script might still work if the interpreter ignores CRLFs
fi

# Color palette
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
GRAY='\033[0;90m'
NC='\033[0m'
BOLD='\033[1m'

VERSION="1.3.0"
TIMESTAMP_FMT="%Y%m%d_%H%M%S"
TIMESTAMP() { date +"$TIMESTAMP_FMT"; }

# Configuration (can be overridden by env or docker-compose)
PGHOST=${POSTGRES_HOST:-postgres}
PGPORT=${POSTGRES_PORT_INTERNAL:-5432}
PGUSER=${POSTGRES_USER:-postgres}
PGPASSWORD=${POSTGRES_PASSWORD:-}
DEFAULT_DB=${POSTGRES_DB:-postgres}
BACKUP_DIR=${BACKUP_DIR:-/backup}

if [ -n "${PGPASSWORD}" ]; then
  export PGPASSWORD="${PGPASSWORD}"
fi

# Ensure PGDATABASE (so psql defaults to the configured DB instead of the username)
PGDATABASE=${PGDATABASE:-${DEFAULT_DB}}
export PGDATABASE

mkdir -p "$BACKUP_DIR"

check_cmds() {
  local miss=()
  for c in psql pg_dump pg_dumpall pg_restore gzip tar du find date; do
    if ! command -v "$c" >/dev/null 2>&1; then
      miss+=("$c")
    fi
  done
  if [ ${#miss[@]} -gt 0 ]; then
    printf "%b\n" "${RED}Missing required commands: ${miss[*]}. Ensure the image contains Postgres client tools.${NC}"
    printf "%b\n" "Tip: use the non-alpine image 'postgis/postgis:18-3.6' which includes bash and GNU utils."
    exit 1
  fi
}

check_cmds

# Utilities
clear_screen() { command clear || true; }
divider() { printf "%b\n" "${GRAY}${BOLD}────────────────────────────────────────────────────────${NC}"; }

print_header() {
  clear_screen
  printf "%b\n" ""
  printf "%b\n" "${BLUE}${BOLD}┌─────────────────────────────────────────────┐${NC}"
  printf "%b\n" "${BLUE}${BOLD}│           picASpot Postgres Backup          │${NC}"
  printf "%b\n" "${BLUE}${BOLD}└─────────────────────────────────────────────┘${NC}"
  printf "%b\n" "        ${BOLD}Created by Shevchenko Denys @ LilConsul${NC}"
  printf "%b\n" "                  ${GRAY}Version ${VERSION}${NC}"
  printf "%b\n" ""
}

show_menu() {
  local title="$1"; shift
  local options=("$@")
  local i

  printf "%b\n" "${YELLOW}${BOLD}${title}${NC}\n"
  for i in "${!options[@]}"; do
    idx=$((i+1))
    opt="${options[$i]}"
    case "$opt" in
      *Create*|*backup*|*Dump*|*Drop*) printf "  ${BOLD}%2d.${NC} ${CYAN}%s${NC}\n" "$idx" "$opt" ;;
      *Delete*|*Exit*|*Cancel*) printf "  ${BOLD}%2d.${NC} ${MAGENTA}%s${NC}\n" "$idx" "$opt" ;;
      *Yes*) printf "  ${BOLD}%2d.${NC} ${GREEN}%s${NC}\n" "$idx" "$opt" ;;
      *No*) printf "  ${BOLD}%2d.${NC} ${RED}%s${NC}\n" "$idx" "$opt" ;;
      *) printf "  ${BOLD}%2d.${NC} %s\n" "$idx" "$opt" ;;
    esac
  done

  while true; do
    printf "%b" "\n${YELLOW}Select an option [1-${#options[@]}]:${NC} "
    read -r selection
    if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#options[@]}" ]; then
      return $((selection-1))
    fi
    printf "%b\n" "${RED}Please enter a valid number between 1 and ${#options[@]}${NC}"
  done
}

show_spinner() {
  local message="$1"; local pid="$2"
  local spin='⣾⣽⣻⢿⡿⣟⣯⣷'
  local i=0
  local start_time
  start_time=$(date +%s)
  printf "%b " "${CYAN}${message}${NC}"
  while kill -0 "$pid" 2>/dev/null; do
    i=$(( (i+1) % 8 ))
    elapsed=$(( $(date +%s) - start_time ))
    printf "\r%b %s %b%s%b %b(%ds)%b" "${CYAN}${message}${NC}" "" "${YELLOW}" "${spin:$i:1}" "${NC}" "${GRAY}" "$elapsed" "${NC}"
    sleep 0.1
  done
  elapsed=$(( $(date +%s) - start_time ))
  printf "\r%b %s  %b✓%b %b(%ds)%b\n" "${CYAN}${message}${NC}" "" "${GREEN}" "${NC}" "${GRAY}" "$elapsed" "${NC}"
}

show_status() {
  local type="$1"; local message="$2"
  case "$type" in
    success) printf "%b\n" "\n${GREEN}✓ ${message}${NC}" ;;
    error)   printf "%b\n" "\n${RED}✗ ${message}${NC}" ;;
    warning) printf "%b\n" "\n${YELLOW}⚠ ${message}${NC}" ;;
    info)    printf "%b\n" "\n${CYAN}ℹ ${message}${NC}" ;;
    *) printf "%b\n" "${message}" ;;
  esac
}


list_databases() {
  psql -h "$PGHOST" -U "$PGUSER" -p "$PGPORT" -d "$PGDATABASE" -At -c "SELECT datname FROM pg_database WHERE datistemplate = false;" 2>/dev/null
}

# Wait for Postgres to be ready before performing operations
wait_for_db() {
  local timeout=${WAIT_TIMEOUT:-30}
  local start
  start=$(date +%s)
  printf "%b\n" "${CYAN}Waiting for Postgres at ${PGHOST}:${PGPORT}...${NC}"
  while ! PGPASSWORD="${PGPASSWORD:-}" psql -h "$PGHOST" -U "$PGUSER" -p "$PGPORT" -d "$PGDATABASE" -c '\q' >/dev/null 2>&1; do
    if [ $(( $(date +%s) - start )) -ge "$timeout" ]; then
      show_status error "Timed out waiting for Postgres after ${timeout}s"
      return 1
    fi
    printf "."
    sleep 1
  done
  printf "\n"
  show_status success "Postgres is available"
  return 0
}

# Filenames: postgres_backup_YYYYMMDD_HHMMSS(.sql.gz OR _DB.tar.gz)
make_full_backup() {
  # Ensure DB is up
  if ! wait_for_db; then
    return 1
  fi
  local ts
  ts=$(TIMESTAMP)
  local outfile="postgres_backup_${ts}.sql.gz"
  show_status info "Creating full cluster dump -> $outfile"
  (pg_dumpall -h "$PGHOST" -U "$PGUSER" -p "$PGPORT" | gzip >"$BACKUP_DIR/$outfile") &
  pid=$!
  show_spinner "Creating full cluster dump" $pid
  show_status success "Full dump saved to $BACKUP_DIR/$outfile"
}

make_db_backup() {
  # Ensure DB is up
  if ! wait_for_db; then
    return 1
  fi
  local dbname=${1:-}
  if [ -z "$dbname" ]; then
    printf "%b" "Enter database name to dump: "
    read -r dbname
  fi
  if [ -z "$dbname" ]; then
    show_status error "No database specified"
    return 1
  fi
  local ts; ts=$(TIMESTAMP)
  local tmpdir; tmpdir=$(mktemp -d -t pgbackup-XXXXXXXX)
  local dumpfile="$tmpdir/${dbname}.dump"
  local archive="postgres_backup_${dbname}_${ts}.tar.gz"

  show_status info "Dumping database '$dbname' -> $archive"
  (pg_dump -h "$PGHOST" -U "$PGUSER" -p "$PGPORT" -Fc -f "$dumpfile" "$dbname") &
  pid=$!
  show_spinner "Running pg_dump for $dbname" $pid

  (tar -C "$tmpdir" -czf "$BACKUP_DIR/$archive" "$(basename "$dumpfile")") &
  pid=$!
  show_spinner "Compressing dump" $pid

  rm -rf "$tmpdir"
  show_status success "Database dump saved to $BACKUP_DIR/$archive"
}

list_backups() {
  print_header
  printf "%b" "${YELLOW}${BOLD}Available Backups${NC}\n"
  divider
  shopt -s nullglob 2>/dev/null || true
  local files
  files=("$BACKUP_DIR"/postgres_backup_*.tar.gz "$BACKUP_DIR"/postgres_backup_*.sql.gz)
  # Flatten and sort reverse by name safely
  mapfile -t files < <(printf "%s\n" "${files[@]}" | sort -r 2>/dev/null)
  if [ ${#files[@]} -eq 0 ]; then
    show_status info "No backups found."
    divider
    printf "\n${CYAN}Create a backup first to see it listed here.${NC}\n"
    read -r -p "Press Enter to return to main menu..."
    return
  fi

  printf "%b\n" "${BOLD}ID   | Date Created        | Size      | Filename${NC}"
  printf "%b\n" "${BOLD}${GRAY}─────┼─────────────────────┼───────────┼──────────────────${NC}"
  local idx=1
  declare -A MAP
  for f in "${files[@]}"; do
    if [ -f "$f" ]; then
      fname=$(basename "$f")
      size=$(du -h "$f" 2>/dev/null | cut -f1)
      date_part=$(echo "$fname" | sed -n 's/postgres_backup_\([0-9]\{8\}_[0-9]\{6\}\).*/\1/p')
      if [ -z "$date_part" ]; then
        date_part=$(echo "$fname" | sed -n 's/postgres_backup_.*_\([0-9]\{8\}_[0-9]\{6\}\).*/\1/p' || true)
      fi
      if [ -n "$date_part" ]; then
        formatted_date=$(date -d "$(echo $date_part | sed 's/_/ /')" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "$date_part")
      else
        formatted_date="Unknown"
      fi
      printf "%-4s | %-19s | %-9s | %s\n" "$idx" "$formatted_date" "$size" "$fname"
      MAP[$idx]="$fname"
      idx=$((idx+1))
    fi
  done
  divider
  printf "\n${CYAN}Total backups: $((idx-1))${NC}\n\n"

  printf "%b\n" "${BOLD}Options:${NC}"
  printf "  ${CYAN}Enter a backup ID${NC} - View backup details\n"
  printf "  ${MAGENTA}r${NC}              - Return to main menu\n"

  while true; do
    printf "%b" "\n${YELLOW}Enter your choice:${NC} "
    read -r choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -lt "$idx" ]; then
      backup_details "${MAP[$choice]}"
      # After backup_details returns, show the list again
      list_backups
      return
    elif [[ "$choice" =~ ^[rR]$ ]]; then
      break
    else
      printf "%b\n" "${RED}Invalid option. Please enter a valid backup ID or 'r' to return.${NC}"
    fi
  done
}

backup_details() {
  local filename="$1"
  print_header
  printf "%b\n" "${YELLOW}${BOLD}Backup Details${NC}\n"
  divider
  printf "%b\n" "${BOLD}Filename: ${NC}${filename}"
  date_part=$(echo "$filename" | sed -n 's/postgres_backup_\([0-9]\{8\}_[0-9]\{6\}\).*/\1/p' || true)
  if [ -z "$date_part" ]; then
    date_part=$(echo "$filename" | sed -n 's/postgres_backup_.*_\([0-9]\{8\}_[0-9]\{6\}\).*/\1/p' || true)
  fi
  if [ -n "$date_part" ]; then
    formatted_date=$(date -d "$(echo $date_part | sed 's/_/ /')" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "$date_part")
    printf "%b\n" "${BOLD}Created:  ${NC}${formatted_date}"
  fi
  size=$(du -h "$BACKUP_DIR/$filename" 2>/dev/null | cut -f1 || echo "Unknown")
  printf "%b\n" "${BOLD}Size:     ${NC}${size}"
  file_info=$(file "$BACKUP_DIR/$filename" 2>/dev/null || echo "Unknown file type")
  printf "%b\n" "${BOLD}Type:     ${NC}${file_info#*: }"
  divider
  local options=("Restore this backup" "Delete this backup" "Back to backup list")
  show_menu "Available Actions:" "${options[@]}"
  local choice=$?
  case "$choice" in
    0)
      confirm_restore "$filename"
      printf "\n"
      read -r -p "Press Enter to return to backup list..."
      ;;
    1)
      confirm_delete "$filename"
      printf "\n"
      read -r -p "Press Enter to return to backup list..."
      ;;
    2) return ;;
  esac
}

confirm_restore() {
  local filename="$1"
  print_header
  printf "%b\n" "${RED}${BOLD} WARNING: Database Restore  ${NC}\n"
  divider
  printf "%b\n" "${RED}${BOLD}This operation may overwrite existing data!${NC}"
  printf "%b\n" "You are about to restore: ${BOLD}$filename${NC}"
  divider
  local options=("Yes, restore this backup (overwrites current data)" "No, cancel operation (return to backup details)")
  show_menu "Please confirm:" "${options[@]}"
  local choice=$?
  if [ $choice -eq 0 ]; then
    restore_backup "$filename"
  fi
  # Return in either case - let backup_details handle re-display if needed
}

confirm_delete() {
  local filename="$1"
  print_header
  printf "%b\n" "${RED}${BOLD} WARNING: Delete Backup  ${NC}\n"
  divider
  printf "%b\n" "${RED}${BOLD}This will permanently delete the backup file!${NC}"
  printf "%b\n" "You are about to delete: ${BOLD}$filename${NC}"
  divider
  local options=("Yes, delete this backup permanently" "No, cancel operation (return to backup details)")
  show_menu "Please confirm:" "${options[@]}"
  local choice=$?
  if [ $choice -eq 0 ]; then
    rm -f "$BACKUP_DIR/$filename"
    show_status success "Backup deleted successfully!"
    sleep 1
  fi
  # Return in either case - let caller handle navigation
}

restore_backup() {
  # Ensure DB is up
  if ! wait_for_db; then
    return 1
  fi
  local filename="$1"
  print_header
  printf "%b\n" "${YELLOW}${BOLD}Restoring Database from Backup${NC}\n"
  divider
  if [ ! -f "$BACKUP_DIR/$filename" ]; then
    show_status error "Backup file $BACKUP_DIR/$filename not found"
    sleep 2
    return
  fi

  # Decide type
  case "$filename" in
    *.sql.gz)
      printf "%b\n" "${CYAN}This will execute SQL against the server. Continue? (y/N)${NC}"
      read -r CONF
      if [ "$CONF" != "y" ]; then
        show_status info "Canceled"
        return
      fi
      (gunzip -c "$BACKUP_DIR/$filename" | psql -h "$PGHOST" -U "$PGUSER" -p "$PGPORT" -d "$PGDATABASE") &
      pid=$!
      show_spinner "Restoring SQL via psql" $pid
      show_status success "Restore completed"
      ;;
    *.tar.gz)
      # assume archive contains a .dump file
      local tmpdir
      tmpdir=$(mktemp -d -t pgrestore-XXXXXXXX)
      (tar -xzf "$BACKUP_DIR/$filename" -C "$tmpdir") &
      pid=$!
      show_spinner "Extracting archive" $pid
      # find dump file
      dumpfile=$(find "$tmpdir" -type f -name "*.dump" -print -quit || true)
      if [ -z "$dumpfile" ]; then
        show_status error "No .dump file found inside archive"
        rm -rf "$tmpdir"
        return
      fi
      printf "%b" "Enter target database name for restore (existing DB will be modified): "
      read -r targetdb
      if [ -z "$targetdb" ]; then
        show_status error "No target database supplied"
        rm -rf "$tmpdir"
        return
      fi
      printf "%b\n" "${YELLOW}This will run pg_restore with --clean to remove conflicting objects. Continue? (y/N)${NC}"
      read -r CONF
      if [ "$CONF" != "y" ]; then
        show_status info "Canceled"
        rm -rf "$tmpdir"
        return
      fi
      (pg_restore -h "$PGHOST" -U "$PGUSER" -p "$PGPORT" -d "$targetdb" -c "$dumpfile") &
      pid=$!
      show_spinner "Running pg_restore" $pid
      rm -rf "$tmpdir"
      show_status success "Restore completed"
      ;;
    *)
      show_status error "Unknown backup format. Supported: .sql.gz, .tar.gz (containing .dump)"
      ;;
  esac
}

cleanup_backups() {
  print_header
  printf "%b\n" "${YELLOW}${BOLD}Cleanup Old Backups${NC}\n"
  divider
  printf "%b" "Remove backups older than how many days? (default 30): "
  read -r DAYS
  DAYS=${DAYS:-30}
  printf "%b\n" "${YELLOW}This will delete files older than $DAYS days from $BACKUP_DIR. Continue? (y/N)${NC}"
  read -r CONF
  if [ "$CONF" != "y" ]; then
    show_status info "Canceled"
    printf "\n"
    read -r -p "Press Enter to return to main menu..."
    return
  fi
  find "$BACKUP_DIR" -type f -mtime +"$DAYS" -print -delete || show_status info "No files removed or command failed"
  show_status success "Cleanup finished"
  printf "\n"
  read -r -p "Press Enter to return to main menu..."
}

# Interactive create flow
create_backup_interactive() {
  print_header
  local options=("Full cluster dump (pg_dumpall -> .sql.gz)" "Single database dump (pg_dump -> .tar.gz)" "Back to main menu")
  show_menu "Create Backup" "${options[@]}"
  local choice=$?
  case "$choice" in
    0) make_full_backup; printf "\n"; read -r -p "Press Enter to return to main menu..." ;;
    1) make_db_backup; printf "\n"; read -r -p "Press Enter to return to main menu..." ;;
    2) return ;;
  esac
}

main_menu() {
  check_cmds
  while true; do
    print_header
    printf "%b\n" "${GREEN}Connected to host:${NC} ${PGHOST} ${GREEN}port:${NC} ${PGPORT} ${GREEN}user:${NC} ${PGUSER}\n"
    local options=(
      "Create a new backup"
      "View/Manage existing backups"
      "Cleanup old backups"
      "Exit"
      )
    show_menu "Main Menu" "${options[@]}"
    local choice=$?
    case "$choice" in
      0) create_backup_interactive ;;
      1) list_backups ;;
      2) cleanup_backups ;;
      3) clear_screen; printf "\n${BLUE}┌─────────────────────────────────────────────┐${NC}\n"; printf "${BLUE}│        Thank you for using Hell-App         │${NC}\n"; printf "${BLUE}│         Postgres Backup Manager             │${NC}\n"; printf "${BLUE}└─────────────────────────────────────────────┘${NC}\n\n"; exit 0 ;;
    esac
  done
}

# CLI mode
if [ "$#" -gt 0 ]; then
  cmd="$1"
  case "$cmd" in
    backup)
      # backup [dbname] -> if provided, db backup; else interactive
      if [ -n "${2-}" ]; then
        make_db_backup "$2"
      else
        create_backup_interactive
      fi
      ;;
    list)
      list_backups
      ;;
    restore)
      if [ -z "${2-}" ]; then
        printf "%b\n" "Usage: $0 restore <backup-file>"
        exit 1
      fi
      restore_backup "$2"
      ;;
    cleanup)
      cleanup_backups
      ;;
    *)
      printf "%b\n" "Usage: $0 {backup [dbname]|list|restore <file>|cleanup}"
      exit 1
      ;;
  esac
  exit 0
fi

# Default: start interactive menu
main_menu

exit 0
