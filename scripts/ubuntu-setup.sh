#!/usr/bin/env bash
# Ubuntu: full purge of Bun/npm globals/OpenCode/omo/oh-my-opencode-slim state, then install and
# configure everything from this repo. Free models only (OpenCode Zen "-free"); no paid accounts.
# Run as your own user (sudo is used for apt only). Never reads ~/.secrets/.env.
#   scripts/ubuntu-setup.sh [--yes] [--dry-run] [--skip-apt]
# Env: FREE_MODELS=id1,id2,id3 (override auto-picked free models), SKIP_BROWSERS=1 (skip Chromium).
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
YES=0 DRY=0 SKIP_APT=0
STATE="$HOME/.local/state/system-config-setup"
CFG="$HOME/.config/opencode"
MARK_BEGIN="# >>> system-config setup >>>"
MARK_END="# <<< system-config setup <<<"

say() { printf '\n== %s\n' "$*"; }
warn() { printf 'WARN: %s\n' "$*" >&2; FAILS+=("$*"); }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
run() { if ((DRY)); then printf '+ %s\n' "$*"; else "$@"; fi; }
FAILS=()

for a in "$@"; do
  case "$a" in
    --yes|-y) YES=1 ;;
    --dry-run) DRY=1 ;;
    --skip-apt) SKIP_APT=1 ;;
    -h|--help) sed -n '2,7p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) die "unknown option: $a" ;;
  esac
done

[[ -n "${HOME:-}" && "$HOME" != "/" ]] || die "HOME is unset or /"
[[ "$(uname -s)" == Linux ]] && grep -qi ubuntu /etc/os-release || die "Ubuntu only"
for f in opencode/opencode.jsonc opencode/oh-my-opencode-slim.jsonc opencode/AGENTS.md opencode/tui.json claude/skills; do
  [[ -e "$REPO/$f" ]] || die "repo file missing: $f"
done

SUDO=""
((EUID == 0)) || SUDO="sudo"

export NPM_CONFIG_PREFIX="$HOME/.local"
export BUN_INSTALL="$HOME/.bun"
export PATH="$HOME/.bun/bin:$HOME/.opencode/bin:$HOME/.local/bin:$PATH"
NPM_ROOT="$HOME/.local/lib/node_modules"

MCP_PKGS=(@playwright/mcp @modelcontextprotocol/server-sequential-thinking agentql-mcp @brightdata/mcp
  @mozilla/firefox-devtools-mcp @colbymchenry/codegraph)
CLI_PKGS=(firecrawl-cli apify-cli @brightdata/cli just-scrape browse)
LSP_PKGS=(typescript typescript-language-server vscode-langservers-extracted bash-language-server basedpyright)

# ---------------------------------------------------------------- purge
purge() {
  say "Purge plan"
  local -a paths=(
    "$HOME/.bun" "$HOME/.opencode" "$HOME/.omo" "$HOME/.agents" "$HOME/.npm" "$HOME/.npm-global"
    "$HOME/.local/lib/node_modules" "$HOME/.cache/bun" "$HOME/.cache/node" "$HOME/.cache/ms-playwright"
    "$HOME/.firefox-devtools-mcp"
  )
  local base pat
  for base in "$HOME/.config" "$HOME/.local/share" "$HOME/.local/state" "$HOME/.cache"; do
    for pat in 'opencode*' 'oh-my-opencode*' 'omo' '.omo' 'cortexkit*' 'magic-context*' 'slkiser*'; do
      while IFS= read -r -d '' p; do
        [[ "$p" == "$STATE"* ]] || paths+=("$p")
      done < <(find "$base" -maxdepth 1 -iname "$pat" -print0 2>/dev/null)
    done
  done
  for p in "$HOME"/.local/bin/{opencode,opencode2,bun,bunx,github-mcp-server,codegraph,firefox-devtools-mcp,agentql-mcp,tvly,firecrawl,apify,brightdata,bdata,just-scrape,browse,tsc,tsserver,typescript-language-server,vscode-json-language-server,bash-language-server,basedpyright,basedpyright-langserver}; do
    [[ -e "$p" || -L "$p" ]] && paths+=("$p")
  done
  local -a existing=()
  for p in "${paths[@]}"; do [[ -e "$p" || -L "$p" ]] && existing+=("$p"); done
  printf '  %s\n' "${existing[@]:-<nothing to remove>}"
  printf '  (kept: ~/.secrets/.env, ~/.claude, ~/.npmrc, system node/apt packages; %s is backed up and restored)\n' "$CFG/secrets"

  if ((!YES && !DRY)); then
    [[ -t 0 || -r /dev/tty ]] || die "not a terminal: pass --yes"
    local ans; read -r -p "Type 'purge' to delete the above: " ans </dev/tty
    [[ "$ans" == purge ]] || die "aborted"
  fi

  say "Stop running processes"
  run pkill -u "$(id -u)" -x opencode || true
  run pkill -u "$(id -u)" -x opencode2 || true

  say "Back up secrets (never read)"
  if [[ -d "$CFG/secrets" ]]; then
    run mkdir -p "$STATE"; run chmod 700 "$STATE"
    run rm -rf "$STATE/secrets"; run cp -a "$CFG/secrets" "$STATE/secrets"
  fi

  say "Uninstall npm globals (user prefix)"
  if command -v npm >/dev/null; then
    run npm uninstall -g "${MCP_PKGS[@]}" "${CLI_PKGS[@]}" "${LSP_PKGS[@]}" firecrawl-mcp oh-my-opencode-slim || true
  fi
  command -v uv >/dev/null && run uv tool uninstall tavily-cli scrapegraph-mcp 2>/dev/null || true

  say "Delete"
  ((${#existing[@]})) && run rm -rf -- "${existing[@]}"

  say "Clean shell startup files (backup: *.bak-setup)"
  local rc
  for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile" "$HOME/.bash_profile"; do
    [[ -f "$rc" ]] || continue
    run cp -a "$rc" "$rc.bak-setup"
    run sed -i -e "/$MARK_BEGIN/,/$MARK_END/d" \
      -e '/^# bun$/d' -e '/BUN_INSTALL/d' -e '/\.bun\/bin/d' -e '/\.opencode\/bin/d' \
      -e '/^# opencode/Id' -e '/OPENCODE_/d' -e '/OH_MY_OPENCODE/d' "$rc"
  done
}

# ---------------------------------------------------------------- install
install_system() {
  say "System packages"
  if ((SKIP_APT)); then
    echo "skipped (--skip-apt)"
  else
    run $SUDO apt-get update -y
    run $SUDO apt-get install -y curl ca-certificates unzip git jq python3 tmux ripgrep
    if ! command -v node >/dev/null || (( $(node -p 'process.versions.node.split(".")[0]') < 22 )); then
      run bash -c "curl -fsSL https://deb.nodesource.com/setup_22.x | $SUDO -E bash -"
      run $SUDO apt-get install -y nodejs
    fi
  fi
  ((DRY)) || { command -v node >/dev/null && command -v npm >/dev/null && command -v python3 >/dev/null \
    && command -v curl >/dev/null && command -v jq >/dev/null || die "need node>=22, npm, python3, curl, jq"; }
}

install_tools() {
  say "Bun"
  run bash -c 'curl -fsSL https://bun.sh/install | bash'
  say "OpenCode v2"
  run bash -c 'curl -fsSL https://opencode.ai/v2/install | bash -s -- --no-modify-path'
  say "uv"
  run bash -c 'curl -LsSf https://astral.sh/uv/install.sh | UV_NO_MODIFY_PATH=1 sh'

  say "Shell PATH block"
  local rc
  for rc in "$HOME/.bashrc"; do
    run bash -c "printf '%s\n' '$MARK_BEGIN' 'export BUN_INSTALL=\"\$HOME/.bun\"' \
'export PATH=\"\$HOME/.bun/bin:\$HOME/.opencode/bin:\$HOME/.local/bin:\$PATH\"' '$MARK_END' >> '$rc'"
  done

  say "npm globals (MCP servers, vendor CLIs, language servers) -> ~/.local"
  local pkg
  for pkg in "${MCP_PKGS[@]}" "${CLI_PKGS[@]}" "${LSP_PKGS[@]}"; do
    run npm install -g "$pkg@latest" || warn "npm install failed: $pkg"
  done
  run uv tool install --upgrade tavily-cli || warn "uv tool install failed: tavily-cli"
  if grep -q '"scrapegraph-mcp"' "$REPO/opencode/opencode.jsonc"; then
    run uv tool install --upgrade scrapegraph-mcp || warn "uv tool install failed: scrapegraph-mcp"
  fi

  say "github-mcp-server"
  local arch; case "$(uname -m)" in x86_64) arch=x86_64 ;; aarch64|arm64) arch=arm64 ;; *) arch="" ;; esac
  if [[ -n "$arch" ]]; then
    run bash -c "mkdir -p '$HOME/.local/bin' && curl -fsSL https://github.com/github/github-mcp-server/releases/latest/download/github-mcp-server_Linux_${arch}.tar.gz \
| tar -xz -C '$HOME/.local/bin' github-mcp-server" || warn "github-mcp-server download failed"
  else
    warn "github-mcp-server: unsupported arch $(uname -m)"
  fi

  if [[ -z "${SKIP_BROWSERS:-}" ]]; then
    say "Chromium for Playwright MCP"
    run npx -y playwright@latest install chromium || warn "playwright chromium install failed"
    ((SKIP_APT)) || run $SUDO env "PATH=$PATH" npx -y playwright@latest install-deps chromium || warn "playwright deps failed"
  fi

  say "oh-my-opencode-slim"
  run bunx oh-my-opencode-slim@latest install --no-tui --companion=no --background-subagents=yes \
    --background-subagents-target="$HOME/.bashrc" --preset=opencode-go --reset || warn "slim installer failed"
}

# ---------------------------------------------------------------- configure
configure() {
  say "Restore secrets"
  run mkdir -p "$CFG/secrets"; run chmod 700 "$CFG/secrets"
  [[ -d "$STATE/secrets" ]] && run cp -an "$STATE/secrets/." "$CFG/secrets/"

  say "AGENTS.md, tui.json, skills"
  run mkdir -p "$CFG" "$HOME/.claude/skills" "$CFG/skills"
  run cp -f "$REPO/opencode/AGENTS.md" "$CFG/AGENTS.md"
  run cp -f "$REPO/opencode/tui.json" "$CFG/tui.json"
  run cp -a "$REPO/claude/skills/." "$HOME/.claude/skills/"
  local d
  for d in "$HOME"/.claude/skills/*/; do
    [[ -d "$d" ]] && run ln -sfn "${d%/}" "$CFG/skills/$(basename "$d")"
  done

  say "opencode.jsonc and oh-my-opencode-slim.jsonc (free models, Linux paths, MCPs with keys only)"
  ((DRY)) && { echo "+ python3 transform"; return; }
  python3 - "$REPO" "$HOME" "$NPM_ROOT" "$CFG" <<'PY'
import json, os, re, shutil, sys, urllib.request

repo, home, npm_root, cfg_dir = sys.argv[1:5]


def load_jsonc(path):
    s = open(path, encoding="utf-8").read()
    out, i, n, in_str = [], 0, len(s), False
    while i < n:
        c = s[i]
        if in_str:
            out.append(c)
            if c == "\\":
                out.append(s[i + 1]); i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True; out.append(c)
        elif s.startswith("//", i):
            while i < n and s[i] != "\n":
                i += 1
            continue
        elif s.startswith("/*", i):
            i = s.index("*/", i) + 2
            continue
        else:
            out.append(c)
        i += 1
    return json.loads(re.sub(r",(\s*[}\]])", r"\1", "".join(out)))


PREFER = ["muse-spark-1.3-contributor-free", "deepseek-v4-flash-free", "kimi-k2.5-free",
          "big-pickle", "glm-5-free", "minimax-m3-free", "qwen3.6-plus-free"]


def free_models():
    env = os.environ.get("FREE_MODELS")
    if env:
        return [m.strip() for m in env.split(",") if m.strip()]
    try:
        req = urllib.request.Request("https://models.dev/api.json", headers={"User-Agent": "curl/8"})
        models = json.load(urllib.request.urlopen(req, timeout=60))["opencode"]["models"]
    except Exception as exc:
        sys.exit(f"cannot list free models ({exc}); set FREE_MODELS=id1,id2,id3")
    free = {k: v for k, v in models.items()
            if (v.get("cost") or {}).get("input") == 0 and (v.get("cost") or {}).get("output") == 0}
    rest = sorted((k for k in free if k not in PREFER), key=lambda k: -(free[k].get("limit") or {}).get("context", 0))
    return [k for k in PREFER if k in free] + rest


ids = free_models()
if not ids:
    sys.exit("no free models found")
M = ["opencode/" + ids[i % len(ids)] for i in range(3)]
print("free models:", ", ".join(M))

# ---- opencode.jsonc
cfg = load_jsonc(f"{repo}/opencode/opencode.jsonc")
cfg.pop("shell", None)
cfg.pop("providers", None)
cfg["model"] = cfg["small_model"] = M[0]
for name, agent in cfg.get("agents", {}).items():
    if "model" in agent:
        agent["model"] = M[1] if name == "plan" else M[0]

firefox = shutil.which("firefox") or shutil.which("firefox-esr")
SUBS = [("C:/Users/Lance/AppData/Roaming/npm/node_modules", npm_root),
        ("C:\\Users\\Lance\\.local\\bin\\github-mcp-server.exe", f"{home}/.local/bin/github-mcp-server"),
        ("C:/Users/Lance/.firefox-devtools-mcp/profile/firefox_devtools_mcp_profile", f"{home}/.firefox-devtools-mcp/profile"),
        ("C:/Program Files/Mozilla Firefox/firefox.exe", firefox or "")]


def walk(o):
    if isinstance(o, str):
        for a, b in SUBS:
            o = o.replace(a, b)
        return o
    if isinstance(o, list):
        return [walk(x) for x in o]
    if isinstance(o, dict):
        return {k: walk(v) for k, v in o.items()}
    return o


kept, skipped = {}, []
for name, server in cfg["mcp"]["servers"].items():
    server = walk(server)
    text = json.dumps(server)
    if "C:" in text or ".exe" in text or '""' in text:
        skipped.append((name, "Windows-only or Firefox not installed")); continue
    need = re.findall(r"secrets/([\w-]+)\}", text)
    missing = [n for n in need
               if not (os.path.isfile(f"{cfg_dir}/secrets/{n}") and os.path.getsize(f"{cfg_dir}/secrets/{n}") > 0)]
    if missing:
        skipped.append((name, f"needs a free-plan key in ~/.config/opencode/secrets/{missing[0]}")); continue
    kept[name] = server
cfg["mcp"]["servers"] = kept

lsp = cfg.get("lsp", {})
for key in ("csharp", "powershell"):
    lsp.pop(key, None)
if "pyright" in lsp:
    lsp["pyright"]["command"] = ["basedpyright-langserver", "--stdio"]

os.makedirs(cfg_dir, exist_ok=True)
json.dump(cfg, open(f"{cfg_dir}/opencode.jsonc", "w", encoding="utf-8"), indent=2)

# ---- oh-my-opencode-slim.jsonc
slim = load_jsonc(f"{repo}/opencode/oh-my-opencode-slim.jsonc")
chain = [{"id": m} for m in M]


def remodel(o):
    if isinstance(o, dict):
        if isinstance(o.get("model"), list):
            o["model"] = [dict(c) for c in chain]
        for v in o.values():
            remodel(v)
    elif isinstance(o, list):
        for v in o:
            remodel(v)


remodel(slim)
presets = slim.get("presets", {})
if "opencode-go" in presets:
    presets["opencode-free"] = presets.pop("opencode-go")
slim["preset"] = "opencode-free"
conc = slim.get("backgroundJobs", {}).get("concurrency", {})
if "providerConcurrency" in conc:
    conc["providerConcurrency"] = {"opencode": 4}
json.dump(slim, open(f"{cfg_dir}/oh-my-opencode-slim.jsonc", "w", encoding="utf-8"), indent=2)

print("MCP enabled:", ", ".join(kept) or "none")
for name, why in skipped:
    print(f"MCP skipped: {name} ({why})")
PY
}

verify() {
  say "Verify"
  ((DRY)) && return 0
  opencode --version || warn "opencode not on PATH"
  bun --version || warn "bun not on PATH"
  timeout 120 bunx oh-my-opencode-slim@latest doctor || warn "slim doctor reported problems"
  timeout 120 opencode mcp list || warn "opencode mcp list failed"
  if ((${#FAILS[@]})); then
    printf '\nDone with %d warning(s):\n' "${#FAILS[@]}"; printf '  - %s\n' "${FAILS[@]}"
  else
    printf '\nDone. Open a new terminal (or: source ~/.bashrc), then run: opencode\n'
  fi
}

purge
install_system
install_tools
configure
verify
