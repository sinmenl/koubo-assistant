#!/usr/bin/env bash
# Installation and update entry only; AGENTS.md and the source skills own behavior.
set -euo pipefail

usage() {
  cat <<'USAGE'
用法：bash scripts/manage.sh install|status|update

install  使用包内安装器注册 koubo-assistant 这一个入口。
status   查看本地版本和入口状态；不联网、不更新。
update   仅从正式 origin 的 main 快进更新，保留个人材料。

首次使用请先 git clone https://github.com/sinmenl/koubo-assistant.git
私有仓库需要当前用户自己的读取权限；不要把他人的凭证写入仓库。
USAGE
}

die() {
  printf '停止：%s\n' "$*" >&2
  exit 1
}

resolve_script_dir() {
  local source_path="${BASH_SOURCE[0]}"
  local parent_dir
  local link_target
  while [[ -L "$source_path" ]]; do
    parent_dir="$(cd -P "$(dirname "$source_path")" && pwd)"
    link_target="$(readlink "$source_path")"
    case "$link_target" in
      /*) source_path="$link_target" ;;
      *) source_path="$parent_dir/$link_target" ;;
    esac
  done
  cd -P "$(dirname "$source_path")" && pwd
}

SCRIPT_DIR="$(resolve_script_dir)"
PROJECT_ROOT="$(cd -P "$SCRIPT_DIR/.." && pwd)"
INSTALLER="$PROJECT_ROOT/skills/dbskill/dbs-install-skill/scripts/install-skill.sh"

check_project() {
  local actual_root
  local origin_url
  command -v git >/dev/null 2>&1 || die "找不到 Git，请先安装 Git 后重新执行。"
  [[ -e "$PROJECT_ROOT/.git" ]] || die "安装目录没有自己的 .git；ZIP 不能持续更新。请在独立目录重新 git clone 正式仓库，不要使用父目录的 Git 仓库。"
  actual_root="$(git -C "$PROJECT_ROOT" rev-parse --show-toplevel 2>/dev/null)" || die "安装目录不是可用的 Git 仓库，请重新克隆。"
  actual_root="$(cd -P "$actual_root" && pwd)"
  [[ "$actual_root" == "$PROJECT_ROOT" ]] || die "检测到其他项目的 Git 根目录，未执行操作。请重新克隆到独立目录。"
  origin_url="$(git -C "$PROJECT_ROOT" config --get-all remote.origin.url || true)"
  case "$origin_url" in
    https://github.com/sinmenl/koubo-assistant|https://github.com/sinmenl/koubo-assistant.git|git@github.com:sinmenl/koubo-assistant|git@github.com:sinmenl/koubo-assistant.git|ssh://git@github.com/sinmenl/koubo-assistant|ssh://git@github.com/sinmenl/koubo-assistant.git) ;;
    *) die "origin 不是 sinmenl/koubo-assistant 的正式 HTTPS/SSH 地址，未执行操作。" ;;
  esac
  [[ -f "$PROJECT_ROOT/AGENTS.md" && -f "$PROJECT_ROOT/SKILL.md" && -f "$INSTALLER" ]] || die "项目入口或包内安装器缺失，请核对克隆是否完整。"
  [[ -f "$PROJECT_ROOT/skills/dbskill/dbs-resonate/SKILL.md" && -f "$PROJECT_ROOT/skills/dbskill/dbs-script-flow/SKILL.md" ]] || die "默认共鸣／衔接检查所需的包内 Don 哥 Skill 缺失，请核对克隆是否完整。"
  grep -Eq '^name:[[:space:]]*koubo-assistant[[:space:]]*$' "$PROJECT_ROOT/SKILL.md" || die "根 SKILL.md 不是 koubo-assistant 入口，未批量安装其他 Skill。"
}

check_shared_entry() {
  local entry="${DBS_INSTALL_HOME:-$HOME}/.agents/skills/koubo-assistant"
  local resolved
  [[ -e "$entry" || -L "$entry" ]] || die "koubo-assistant 公共入口尚未安装，请先执行 install。"
  if [[ -L "$entry" ]]; then
    resolved="$(cd -P "$entry" && pwd)" || die "公共入口已失效，请检查原安装目录。"
    [[ "$resolved" == "$PROJECT_ROOT" ]] || die "公共入口指向其他来源，已保留，未声称安装成功。"
  else
    # The bundled installer verifies Windows Junction targets with PowerShell.
    # A real directory is never a valid managed entry on Unix-like hosts.
    case "${DBS_INSTALL_PLATFORM:-$(uname -s)}" in
      windows|MINGW*|MSYS*|CYGWIN*) [[ -d "$entry" ]] || die "公共入口不是可用目录。" ;;
      *) die "公共入口是真实目录或文件，已保留，未声称安装成功。" ;;
    esac
  fi
}

is_personal_path() {
  local path="$1"
  local component
  case "$path" in
    memory/_README.md|memory/_template.md|style-profiles/_template.md) return 1 ;;
    memory|memory/*|style-profiles|style-profiles/*|inbox|inbox/*|output|output/*|local|local/*|backups|backups/*|backup|backup/*) return 0 ;;
  esac
  # .env files are private at any depth, including a directory with that name.
  while :; do
    component="${path%%/*}"
    case "$component" in .env|.env.*) return 0 ;; esac
    [[ "$path" == */* ]] || break
    path="${path#*/}"
  done
  return 1
}

check_incoming_paths() {
  local target_commit="$1"
  local upstream_path
  local local_path
  local local_path_count=0
  local -a local_paths
  local_paths=()

  # Both streams contain files/symlinks, use NUL delimiters for arbitrary names.
  while IFS= read -r -d '' local_path; do
    local_paths[$local_path_count]="$local_path"
    local_path_count=$((local_path_count + 1))
  done < <(git -C "$PROJECT_ROOT" ls-files --others --exclude-standard -z)
  while IFS= read -r -d '' local_path; do
    local_paths[$local_path_count]="$local_path"
    local_path_count=$((local_path_count + 1))
  done < <(git -C "$PROJECT_ROOT" ls-files --others --ignored --exclude-standard -z)

  while IFS= read -r -d '' upstream_path; do
    if is_personal_path "$upstream_path"; then
      printf '停止：远端开始跟踪个人材料路径：%q\n' "$upstream_path" >&2
      return 1
    fi
    if [[ "$local_path_count" -gt 0 ]]; then
      for local_path in "${local_paths[@]}"; do
        if [[ "$upstream_path" == "$local_path" || "$upstream_path" == "$local_path/"* || "$local_path" == "$upstream_path/"* ]]; then
          printf '停止：远端路径 %q 与本地未跟踪／忽略路径 %q 冲突，个人文件未改动。\n' "$upstream_path" "$local_path" >&2
          return 1
        fi
      done
    fi
  done < <(git -C "$PROJECT_ROOT" ls-tree -r --name-only -z "$target_commit")
}

update_project() {
  local branch
  local before
  local target
  branch="$(git -C "$PROJECT_ROOT" symbolic-ref --quiet --short HEAD || true)"
  [[ "$branch" == main ]] || die "当前不在 main 分支，未更新。请先保留并处理当前分支工作。"
  git -C "$PROJECT_ROOT" diff --quiet --ignore-submodules=none -- || die "受跟踪文件有本地修改，未更新；请先自行处理，脚本不会覆盖或暂存。"
  git -C "$PROJECT_ROOT" diff --cached --quiet --ignore-submodules=none -- || die "存在已暂存的本地修改，未更新；请先自行处理。"
  before="$(git -C "$PROJECT_ROOT" rev-parse --verify HEAD)"

  printf '正在获取 origin/main；本地个人材料不会上传。\n'
  git -C "$PROJECT_ROOT" -c submodule.recurse=false fetch --no-tags --no-recurse-submodules origin refs/heads/main:refs/remotes/origin/main || die "获取失败。私有仓库请检查当前账号的读取权限和网络；本地文件未更新。"
  target="$(git -C "$PROJECT_ROOT" rev-parse --verify 'refs/remotes/origin/main^{commit}')" || die "远端 main 不存在，未更新。"
  if ! git -C "$PROJECT_ROOT" merge-base --is-ancestor "$before" "$target"; then
    die "本地 main 有未发布提交、已分叉或远端历史发生变化，无法快进；未更新，不自动合并、重置或清理。"
  fi

  check_incoming_paths "$target" || return 1
  if [[ "$before" == "$target" ]]; then
    printf '已是所获取 origin/main 的最新版本：%s\n' "$before"
    return 0
  fi

  git -C "$PROJECT_ROOT" -c merge.autoStash=false -c submodule.recurse=false merge --ff-only --no-overwrite-ignore "$target" || die "快进更新未完成；请查看 Git 报告，脚本未执行重置、清理或暂存。"
  printf '更新完成：%s → %s\n' "$before" "$(git -C "$PROJECT_ROOT" rev-parse HEAD)"
  printf '个人材料保留在原路径；已有入口仍指向同一安装目录，无需重新链接。\n'
}

main() {
  local action="${1:-}"
  [[ $# -eq 1 ]] || { usage; exit 1; }
  case "$action" in
    -h|--help|help) usage; return 0 ;;
    install|status|update) ;;
    *) usage; exit 1 ;;
  esac
  check_project
  case "$action" in
    install)
      bash "$INSTALLER" link "$PROJECT_ROOT"
      check_shared_entry
      ;;
    status)
      printf '安装目录：%s\n' "$PROJECT_ROOT"
      printf '本地版本：%s\n' "$(git -C "$PROJECT_ROOT" rev-parse HEAD)"
      printf '当前分支：%s\n' "$(git -C "$PROJECT_ROOT" symbolic-ref --quiet --short HEAD || printf 'detached HEAD')"
      check_shared_entry
      bash "$INSTALLER" status "$PROJECT_ROOT"
      ;;
    update) update_project ;;
  esac
}

main "$@"
