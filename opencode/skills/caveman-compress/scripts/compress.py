#!/usr/bin/env python3

import contextlib
import errno
import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import List, Tuple

_IS_WINDOWS = os.name == "nt" or sys.platform == "win32"
_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)

if _IS_WINDOWS:
    import msvcrt
else:
    import fcntl


for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except Exception:
        pass


FENCE_LINE_REGEX = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


FRONTMATTER_REGEX = re.compile(r"\A(---\r?\n.*?\r?\n---\r?\n)(.*)", re.DOTALL)


def split_frontmatter(text: str):
    m = FRONTMATTER_REGEX.match(text)
    if m:
        return m.group(1), m.group(2)
    return "", text


SENSITIVE_BASENAME_REGEX = re.compile(
    r"(?ix)^("
    r"\.env(\..+)?"
    r"|\.netrc"
    r"|credentials(\..+)?"
    r"|secrets?(\..+)?"
    r"|passwords?(\..+)?"
    r"|id_(rsa|dsa|ecdsa|ed25519)(\.pub)?"
    r"|authorized_keys"
    r"|known_hosts"
    r"|.*\.(pem|key|p12|pfx|crt|cer|jks|keystore|asc|gpg)"
    r")$"
)

SENSITIVE_PATH_COMPONENTS = frozenset(
    {
        ".ssh",
        ".aws",
        ".gnupg",
        ".kube",
        ".docker",
        "credential",
        "credentials",
        "secret",
        "secrets",
    }
)

SENSITIVE_NAME_TOKENS = (
    "secret",
    "credential",
    "password",
    "passwd",
    "apikey",
    "accesskey",
    "token",
    "privatekey",
)


def _state_base_dir(kind: str) -> Path:
    if _IS_WINDOWS:
        local_appdata = os.environ.get("LOCALAPPDATA")
        base = (
            Path(local_appdata) if local_appdata else Path.home() / "AppData" / "Local"
        )
    else:
        xdg = os.environ.get("XDG_DATA_HOME")
        base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    return base / "caveman-compress" / kind


def backup_dir_for(filepath: Path) -> Path:
    return _state_base_dir("backups") / filepath.parent.name


LOCK_WAIT_SECONDS = 900
LOCK_POLL_INTERVAL = 1.0


class LockTimeoutError(TimeoutError):
    """Raised when another process holds the compress lock past LOCK_WAIT_SECONDS."""


def lock_path_for(filepath: Path) -> Path:
    resolved = filepath.resolve()
    backup_path = backup_dir_for(resolved) / (resolved.stem + ".original.md")
    digest = hashlib.sha256(str(backup_path).encode("utf-8")).hexdigest()[:16]
    return _state_base_dir("locks") / f"{digest}.lock"


def _try_lock_nonblocking(fd: int) -> None:
    if _IS_WINDOWS:
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        except OSError as e:
            if e.errno != errno.EACCES:
                raise
            raise BlockingIOError(str(e)) from e
    else:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock(fd: int) -> None:
    try:
        if _IS_WINDOWS:
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(fd, fcntl.LOCK_UN)
    except OSError:
        pass


@contextlib.contextmanager
def file_lock(filepath: Path):
    lock_path = lock_path_for(filepath)
    lock_dir = lock_path.parent
    if lock_dir.is_symlink():
        raise OSError(f"Refusing to use lock directory through a symlink: {lock_dir}")
    lock_dir.mkdir(parents=True, exist_ok=True)
    if not _IS_WINDOWS:
        with contextlib.suppress(OSError):
            os.chmod(lock_dir, 0o700)
    if lock_path.is_symlink():
        raise OSError(f"Refusing to open lock file through a symlink: {lock_path}")
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | _O_NOFOLLOW, 0o600)
    try:
        if os.fstat(fd).st_size == 0:
            os.write(fd, b"\0")
        os.lseek(fd, 0, 0)
        deadline = time.monotonic() + LOCK_WAIT_SECONDS
        printed_waiting = False
        while True:
            try:
                _try_lock_nonblocking(fd)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise LockTimeoutError(
                        f"Another caveman-compress run appears to be compressing {filepath} "
                        f"(lock: {lock_path}). Giving up after {LOCK_WAIT_SECONDS}s — retry once "
                        "it finishes."
                    ) from None
                if not printed_waiting:
                    print(
                        f"Waiting for another caveman-compress run to finish with {filepath}...",
                        flush=True,
                    )
                    printed_waiting = True
                time.sleep(LOCK_POLL_INTERVAL)
            except OSError as e:
                if e.errno in (errno.EOPNOTSUPP, errno.ENOSYS):
                    print(
                        f"⚠️ {lock_dir}'s filesystem doesn't support file locking — proceeding without cross-session coordination.",
                        flush=True,
                    )
                    break
                raise
        try:
            yield
        finally:
            _unlock(fd)
    finally:
        os.close(fd)


def is_sensitive_path(filepath: Path) -> bool:
    name = filepath.name
    if SENSITIVE_BASENAME_REGEX.match(name):
        return True

    normalized_parts = {
        re.sub(r"[_\-\s.]", "", part.lower()) for part in filepath.parts
    }
    if normalized_parts & SENSITIVE_PATH_COMPONENTS:
        return True
    return any(
        token in part for part in normalized_parts for token in SENSITIVE_NAME_TOKENS
    )


def strip_llm_wrapper(text: str) -> str:
    lines = text.split("\n")
    first, last = 0, len(lines) - 1
    while first < len(lines) and not lines[first].strip():
        first += 1
    while last > first and not lines[last].strip():
        last -= 1
    if first >= last:
        return text
    opener = FENCE_LINE_REGEX.match(lines[first])
    closer = FENCE_LINE_REGEX.match(lines[last])
    if not opener or not closer:
        return text
    marker = opener.group(1)

    if closer.group(1)[0] != marker[0] or len(closer.group(1)) < len(marker):
        return text
    if lines[last].strip() != closer.group(1):
        return text

    for line in lines[first + 1 : last]:
        inner = FENCE_LINE_REGEX.match(line)
        if (
            inner
            and inner.group(1)[0] == marker[0]
            and len(inner.group(1)) >= len(marker)
        ):
            return text
    return "\n".join(lines[first + 1 : last])


def write_text_atomic(path: Path, text: str, newline: str = "\n") -> None:
    if newline != "\n":
        text = text.replace("\r\n", "\n").replace("\n", newline)
    write_bytes_atomic(path, text.encode("utf-8"))


def write_bytes_atomic(path: Path, data: bytes) -> None:
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=path.name + ".", suffix=".tmp"
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        if path.exists():
            os.chmod(tmp_path, stat.S_IMODE(path.stat().st_mode))
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except OSError:
            pass
        raise


def read_source(filepath: Path) -> tuple[str, str, bytes]:
    raw = filepath.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(
            f"Refusing to compress {filepath}: not valid UTF-8 "
            f"(byte 0x{raw[e.start]:02x} at offset {e.start}). "
            "Compression rewrites the file in place, and any byte this tool "
            "cannot decode would be destroyed by the round trip. "
            "Convert the file to UTF-8 first."
        ) from None
    crlf = text.count("\r\n")
    newline = "\r\n" if crlf * 2 > text.count("\n") else "\n"
    return text.replace("\r\n", "\n").replace("\r", "\n"), newline, raw


def first_nonblank_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def _write_target(
    filepath: Path, text: str | bytes, backup_path: Path, newline: str = "\n"
) -> None:
    try:
        if isinstance(text, bytes):
            write_bytes_atomic(filepath, text)
        else:
            write_text_atomic(filepath, text, newline)
    except Exception:
        print(
            f"❌ Write to {filepath} failed. Original preserved at backup: {backup_path}"
        )
        raise


from .detect import should_compress
from .validate import validate

MAX_RETRIES = 2


def _is_smaller_than_body(candidate_body: str, body: str) -> bool:
    candidate_len = len(candidate_body.strip())
    body_len = len(body.strip())
    if candidate_len >= body_len:
        print(
            "❌ Compression aborted: output is not smaller than input "
            f"({candidate_len} >= {body_len} chars)."
        )
        return False
    return True


CLAUDE_CALL_TIMEOUT_SECONDS = LOCK_WAIT_SECONDS // (MAX_RETRIES + 1)


def call_claude(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic

            client = anthropic.Anthropic(
                api_key=api_key, timeout=CLAUDE_CALL_TIMEOUT_SECONDS
            )
            msg = client.messages.create(
                model=os.environ.get("CAVEMAN_MODEL", "claude-sonnet-4-5"),
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
            )

            text = next(
                (
                    block.text
                    for block in msg.content
                    if getattr(block, "type", None) == "text"
                ),
                "",
            )
            return strip_llm_wrapper(text.strip())
        except ImportError:
            pass

    claude_bin = shutil.which("claude") or "claude"
    try:
        result = subprocess.run(
            [
                claude_bin,
                "--print",
                "--setting-sources",
                "",
                "--strict-mcp-config",
            ],
            input=prompt,
            text=True,
            capture_output=True,
            check=True,
            encoding="utf-8",
            errors="replace",
            timeout=CLAUDE_CALL_TIMEOUT_SECONDS,
        )
        return strip_llm_wrapper(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Claude call failed:\n{e.stderr}")
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"Claude CLI call timed out after {CLAUDE_CALL_TIMEOUT_SECONDS}s "
            "(stalled network, or an auth prompt with no TTY to answer it)"
        )


def build_compress_prompt(original: str) -> str:
    return f"""
Compress this markdown into caveman format.

STRICT RULES:
- Do NOT modify anything inside ``` code blocks
- Do NOT modify anything inside a 4-space-indented code block either — those are code too, and they are validated
- Do NOT modify anything inside inline backticks
- Preserve ALL URLs exactly
- Preserve ALL headings exactly
- Preserve file paths and commands
- Return ONLY the compressed markdown body — do NOT wrap the entire output in a ```markdown fence or any other fence. Inner code blocks from the original stay as-is; do not add a new outer fence around the whole file.

Only compress natural language.

TEXT:
{original}
"""


def build_fix_prompt(original: str, compressed: str, errors: List[str]) -> str:
    errors_str = "\n".join(f"- {e}" for e in errors)
    return f"""You are fixing a caveman-compressed markdown file. Specific validation errors were found.

CRITICAL RULES:
- DO NOT recompress or rephrase the file
- ONLY fix the listed errors — leave everything else exactly as-is
- The ORIGINAL is provided as reference only (to restore missing content)
- Preserve caveman style in all untouched sections

ERRORS TO FIX:
{errors_str}

HOW TO FIX:
- Missing URL: find it in ORIGINAL, restore it exactly where it belongs in COMPRESSED
- Code block mismatch: find the exact code block in ORIGINAL, restore it in COMPRESSED
- Heading mismatch: restore the exact heading text from ORIGINAL into COMPRESSED
- Do not touch any section not mentioned in the errors

ORIGINAL (reference only):
{original}

COMPRESSED (fix this):
{compressed}

Return ONLY the fixed compressed file. No explanation.
"""


CODE_MARKER_PREFIX = "@@CAVEMAN_PRESERVED_CODE_"
FENCE_OPEN_RE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})(?:[^\r\n]*)$")


def mask_code_blocks(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    if CODE_MARKER_PREFIX in text:
        raise ValueError("Input contains reserved Caveman code-preservation marker")
    lines = text.splitlines(keepends=True)
    out: List[str] = []
    blocks: List[Tuple[str, str]] = []
    i = 0
    while i < len(lines):
        line_without_newline = lines[i].rstrip("\r\n")
        fence = FENCE_OPEN_RE.match(line_without_newline)
        indented = bool(line_without_newline) and (
            line_without_newline.startswith("    ")
            or line_without_newline.startswith("\t")
        )
        if not fence and not indented:
            out.append(lines[i])
            i += 1
            continue

        start = i
        if fence:
            fence_run = fence.group(1)
            close_re = re.compile(
                rf"^[ ]{{0,3}}{re.escape(fence_run[0])}{{{len(fence_run)},}}[ \t]*$"
            )
            i += 1
            while i < len(lines):
                if close_re.match(lines[i].rstrip("\r\n")):
                    i += 1
                    break
                i += 1
        else:
            i += 1
            while i < len(lines):
                candidate = lines[i].rstrip("\r\n")
                if (
                    not candidate
                    or candidate.startswith("    ")
                    or candidate.startswith("\t")
                ):
                    i += 1
                    continue
                break

        block = "".join(lines[start:i])
        marker = f"{CODE_MARKER_PREFIX}{len(blocks)}_{hashlib.sha256(block.encode('utf-8')).hexdigest()[:16]}@@"
        blocks.append((marker, block))
        newline = (
            "\r\n" if block.endswith("\r\n") else "\n" if block.endswith("\n") else ""
        )
        out.append(marker + newline)
    return "".join(out), blocks


def restore_code_blocks(text: str, blocks: List[Tuple[str, str]]) -> str:
    restored = text
    for marker, block in blocks:
        if restored.count(marker) != 1:
            raise ValueError(
                f"Claude changed preserved code marker {marker}; refusing to write"
            )

        if marker + "\r\n" in restored:
            restored = restored.replace(marker + "\r\n", block, 1)
        elif marker + "\n" in restored:
            restored = restored.replace(marker + "\n", block, 1)
        else:
            restored = restored.replace(marker, block, 1)
    if CODE_MARKER_PREFIX in restored:
        raise ValueError("Claude returned an unknown Caveman code-preservation marker")
    return restored


def compress_file(filepath: Path) -> bool:

    filepath = filepath.resolve()

    MAX_FILE_SIZE = 500_000

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if filepath.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large to compress safely (max 500KB): {filepath}")

    if is_sensitive_path(filepath):
        raise ValueError(
            f"Refusing to compress {filepath}: filename looks sensitive "
            "(credentials, keys, secrets, or known private paths). "
            "Compression sends file contents to the Anthropic API. "
            "Rename the file if this is a false positive."
        )

    with file_lock(filepath):
        return _compress_file_locked(filepath)


def _compress_file_locked(filepath: Path) -> bool:
    print(f"Processing: {filepath}")

    if not should_compress(filepath):
        print("Skipping (not natural language)")
        return False

    original_text, newline, original_raw = read_source(filepath)

    backup_dir = backup_dir_for(filepath)
    backup_path = backup_dir / (filepath.stem + ".original.md")

    if not original_text.strip():
        print("❌ Refusing to compress: file is empty or whitespace-only.")
        return False

    if backup_path.exists():
        print(f"⚠️ Backup file already exists: {backup_path}")
        print("The original backup may contain important content.")
        print(
            "Aborting to prevent data loss. Please remove or rename the backup file if you want to proceed."
        )
        return False

    frontmatter, body = split_frontmatter(original_text)
    if frontmatter:
        print(
            f"Detected YAML frontmatter ({len(frontmatter)} chars) — preserving verbatim"
        )

    if not body.strip():
        print("❌ Refusing to compress: body is empty after frontmatter removal.")
        return False

    print("Compressing with Claude...")
    masked_body, code_blocks = mask_code_blocks(body)
    masked_compressed = call_claude(build_compress_prompt(masked_body))
    try:
        compressed_body = restore_code_blocks(masked_compressed, code_blocks)
    except ValueError as error:
        print(f"❌ Compression aborted: {error}")
        print("   Original file is untouched (no backup created).")
        return False

    if compressed_body is None or not compressed_body.strip():
        print("❌ Compression aborted: Claude returned an empty response.")
        print("   Original file is untouched (no backup created).")
        return False

    if compressed_body.strip() == body.strip():
        print("❌ Compression aborted: output is identical to input.")
        print(
            "   Likely causes: Claude refused, returned the prompt verbatim, or the file is"
        )
        print(
            "   already in caveman form. Original file is untouched (no backup created)."
        )
        return False

    if not _is_smaller_than_body(compressed_body, body):
        print("   Original file is untouched (no backup created).")
        return False

    compressed = frontmatter + compressed_body

    backup_dir.mkdir(parents=True, exist_ok=True)
    write_bytes_atomic(backup_path, original_raw)
    if backup_path.read_bytes() != original_raw:
        print(f"❌ Backup write verification failed: {backup_path}")
        print(
            "   In-memory original differs from on-disk backup. Aborting before touching the input file."
        )
        try:
            backup_path.unlink()
        except OSError:
            pass
        return False

    staging_path = filepath.with_name(filepath.name + ".caveman-staged")
    for attempt in range(MAX_RETRIES):
        print(f"\nValidation attempt {attempt + 1}")

        _write_target(staging_path, compressed, backup_path, newline)
        result = validate(backup_path, staging_path)

        if result.is_valid:
            print("Validation passed")
            _write_target(filepath, compressed, backup_path, newline)
            staging_path.unlink(missing_ok=True)
            return True

        print("❌ Validation failed:")
        for err in result.errors:
            print(f"   - {err}")

        if attempt == MAX_RETRIES - 1:
            staging_path.unlink(missing_ok=True)
            backup_path.unlink(missing_ok=True)
            print("Failed after retries: original left untouched")
            return False

        print("Fixing with Claude...")
        fixed = call_claude(build_fix_prompt(original_text, compressed, result.errors))

        if fixed is None or not fixed.strip():
            print("❌ Fix attempt aborted: Claude returned an empty response.")
            print("   Skipping this attempt.")
            continue

        anchor = first_nonblank_line(original_text)
        if anchor.startswith(("---", "#")) and first_nonblank_line(fixed) != anchor:
            print(
                "❌ Fix attempt aborted: output does not start with the original's first line."
            )
            print("   Possible preamble leak. Skipping this attempt.")
            continue

        _, fixed_body = split_frontmatter(fixed)
        if not _is_smaller_than_body(fixed_body, body):
            print("   Skipping this attempt.")
            continue

        compressed = fixed

    return False
