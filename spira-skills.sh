#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
REPO_ROOT="$SCRIPT_DIR"
SKILLS_ROOT="$REPO_ROOT/skills"
ENV_EXAMPLE="$REPO_ROOT/.env.example"

usage() {
  cat <<'EOF'
Usage:
  ./spira-skills.sh list
  ./spira-skills.sh show <skill> [--format path|json]
  ./spira-skills.sh env [--format dotenv|shell]
  ./spira-skills.sh validate
  ./spira-skills.sh link --project <path> --dest <path> [--source <repo-relative-path>] [--force]
EOF
}

require_python() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required." >&2
    exit 1
  fi
}

list_skills() {
  find "$SKILLS_ROOT/business" "$SKILLS_ROOT/dev" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | while IFS= read -r skill_dir; do
    skill_md="$skill_dir/SKILL.md"
    [ -f "$skill_md" ] || continue
    category=$(basename "$(dirname "$skill_dir")")
    slug=$(basename "$skill_dir")
    description=$(python3 - "$skill_md" <<'PY'
import sys
from pathlib import Path

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
if not lines or lines[0].strip() != "---":
    sys.exit(1)
for line in lines[1:]:
    if line.strip() == "---":
        break
    if line.startswith("description:"):
        print(line.split(":", 1)[1].strip().strip('"').strip("'"))
        break
PY
)
    printf '%s/%s\t%s\n' "$category" "$slug" "$description"
  done
}

show_skill() {
  skill_name="$1"
  format="${2:-path}"

  resolved=""
  for candidate in \
    "$SKILLS_ROOT/$skill_name" \
    "$SKILLS_ROOT/business/$skill_name" \
    "$SKILLS_ROOT/dev/$skill_name"
  do
    if [ -f "$candidate/SKILL.md" ]; then
      resolved="$candidate"
      break
    fi
  done

  if [ -z "$resolved" ]; then
    echo "Skill not found: $skill_name" >&2
    exit 1
  fi

  if [ "$format" = "json" ]; then
    python3 - "$resolved" <<'PY'
import json
import sys
from pathlib import Path

skill_dir = Path(sys.argv[1])
skill_md = skill_dir / "SKILL.md"
lines = skill_md.read_text(encoding="utf-8").splitlines()
meta = {}
for line in lines[1:]:
    if line.strip() == "---":
        break
    if ":" in line:
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
relative = skill_dir.relative_to(skill_dir.parents[1])
print(json.dumps({
    "category": relative.parts[0],
    "slug": relative.parts[-1],
    "path": str(skill_dir),
    "name": meta.get("name", ""),
    "description": meta.get("description", ""),
}, ensure_ascii=False, indent=2))
PY
  else
    printf '%s\n' "$resolved"
  fi
}

print_env() {
  format="${1:-dotenv}"
  if [ "$format" = "dotenv" ]; then
    cat "$ENV_EXAMPLE"
    return
  fi

  awk '
    /^[[:space:]]*#/ { next }
    /^[[:space:]]*$/ { next }
    {
      split($0, parts, "=")
      key = parts[1]
      value = substr($0, index($0, "=") + 1)
      printf("export %s=\"%s\"\n", key, value)
    }
  ' "$ENV_EXAMPLE"
}

validate_repo() {
  require_python
  python3 - "$SKILLS_ROOT" <<'PY'
import re
import sys
from pathlib import Path

skills_root = Path(sys.argv[1])
pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
errors = []

def validate_links(markdown_file: Path) -> None:
    text = markdown_file.read_text(encoding="utf-8")
    for target in pattern.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target_path = target.split("#", 1)[0]
        if not target_path:
            continue
        resolved = (markdown_file.parent / target_path).resolve()
        if not resolved.exists():
            errors.append(f"Broken local markdown link: {markdown_file} -> {target}")

for category in ("business", "dev"):
    category_dir = skills_root / category
    if not category_dir.exists():
        continue
    for skill_dir in sorted(path for path in category_dir.iterdir() if path.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"Missing SKILL.md: {skill_dir}")
            continue
        lines = skill_md.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0].strip() != "---":
            errors.append(f"Missing YAML frontmatter start: {skill_md}")
            continue
        meta = {}
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip().strip('"').strip("'")
        if not meta.get("name"):
            errors.append(f"Missing 'name' in {skill_md}")
        if not meta.get("description"):
            errors.append(f"Missing 'description' in {skill_md}")
        validate_links(skill_md)
        references_dir = skill_dir / "references"
        if references_dir.exists():
            for ref_md in sorted(references_dir.rglob("*.md")):
                validate_links(ref_md)

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    sys.exit(1)

print("All skills passed validation.")
PY
}

link_into_project() {
  project=""
  dest=""
  source="skills"
  force="0"

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --project)
        project="$2"
        shift 2
        ;;
      --dest)
        dest="$2"
        shift 2
        ;;
      --source)
        source="$2"
        shift 2
        ;;
      --force)
        force="1"
        shift 1
        ;;
      *)
        echo "Unknown argument: $1" >&2
        usage
        exit 1
        ;;
    esac
  done

  [ -n "$project" ] || { echo "--project is required" >&2; exit 1; }
  [ -n "$dest" ] || { echo "--dest is required" >&2; exit 1; }

  project_dir=$(CDPATH= cd -- "$project" && pwd)
  source_path="$REPO_ROOT/${source#/}"

  if [ ! -e "$source_path" ]; then
    echo "Source path does not exist: $source_path" >&2
    exit 1
  fi

  case "$dest" in
    /*) dest_path="$dest" ;;
    *) dest_path="$project_dir/$dest" ;;
  esac

  dest_parent=$(dirname "$dest_path")
  mkdir -p "$dest_parent"

  if [ -L "$dest_path" ] || [ -e "$dest_path" ]; then
    if [ "$force" != "1" ]; then
      if [ -L "$dest_path" ] && [ "$(readlink "$dest_path")" = "$source_path" ]; then
        echo "Link already exists: $dest_path -> $source_path"
        return
      fi
      echo "Destination already exists: $dest_path" >&2
      echo "Use --force to replace an existing symlink, file, or empty directory." >&2
      exit 1
    fi

    if [ -L "$dest_path" ] || [ -f "$dest_path" ]; then
      rm -f "$dest_path"
    elif [ -d "$dest_path" ]; then
      if [ -n "$(find "$dest_path" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
        echo "Destination exists and is not empty: $dest_path" >&2
        exit 1
      fi
      rmdir "$dest_path"
    else
      rm -rf "$dest_path"
    fi
  fi

  ln -s "$source_path" "$dest_path"
  echo "Linked $dest_path -> $source_path"
}

main() {
  [ "$#" -gt 0 ] || {
    usage
    exit 1
  }

  command="$1"
  shift

  case "$command" in
    list)
      require_python
      list_skills
      ;;
    show)
      require_python
      [ "$#" -ge 1 ] || { echo "show requires a skill name" >&2; exit 1; }
      skill_name="$1"
      shift
      format="path"
      if [ "$#" -ge 2 ] && [ "$1" = "--format" ]; then
        format="$2"
      fi
      show_skill "$skill_name" "$format"
      ;;
    env)
      format="dotenv"
      if [ "$#" -ge 2 ] && [ "$1" = "--format" ]; then
        format="$2"
      fi
      print_env "$format"
      ;;
    validate)
      validate_repo
      ;;
    link)
      link_into_project "$@"
      ;;
    *)
      echo "Unknown command: $command" >&2
      usage
      exit 1
      ;;
  esac
}

main "$@"
