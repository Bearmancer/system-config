import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import switch_api_key as sk  # noqa: E402


def test_write_is_atomic_replace_and_leaves_no_temp(tmp_path, monkeypatch):
    sk.write_secret(tmp_path, "exa", "old")
    replaced = []
    real = sk.os.replace

    def spy(a, b):
        replaced.append((Path(a).parent, Path(b)))
        real(a, b)

    monkeypatch.setattr(sk.os, "replace", spy)
    sk.write_secret(tmp_path, "exa", "new")
    assert replaced == [(tmp_path, tmp_path / "exa")]
    assert (tmp_path / "exa").read_text() == "new"
    assert [p.name for p in tmp_path.iterdir()] == ["exa"]


def test_failed_write_keeps_existing_file(tmp_path, monkeypatch):
    sk.write_secret(tmp_path, "exa", "old")

    def boom(a, b):
        raise OSError("boom")

    monkeypatch.setattr(sk.os, "replace", boom)
    with pytest.raises(OSError):
        sk.write_secret(tmp_path, "exa", "new")
    assert (tmp_path / "exa").read_text() == "old"
    assert [p.name for p in tmp_path.iterdir()] == ["exa"]


def test_materialize_creates_missing_from_active_key(tmp_path, monkeypatch):
    monkeypatch.setattr(sk, "get_active_value", lambda env_var: "ACTIVE")
    assert sk.materialize_secret({}, "tavily", tmp_path / "s") == "tavily: created"
    assert (tmp_path / "s" / "tavily").read_text() == "ACTIVE"


def test_materialize_falls_back_to_first_pool_account(tmp_path, monkeypatch):
    monkeypatch.setattr(sk, "get_active_value", lambda env_var: None)
    dotenv = {"B_EXA_API_KEY": "kb", "A_EXA_API_KEY": "ka"}
    sk.materialize_secret(dotenv, "exa", tmp_path)
    assert (tmp_path / "exa").read_text() == "ka"


def test_materialize_never_overwrites_existing(tmp_path, monkeypatch):
    monkeypatch.setattr(sk, "get_active_value", lambda env_var: "ACTIVE")
    (tmp_path / "exa").write_text("keep")
    assert sk.materialize_secret({}, "exa", tmp_path) == "exa: exists"
    assert (tmp_path / "exa").read_text() == "keep"


def test_materialize_without_any_key_creates_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(sk, "get_active_value", lambda env_var: None)
    with pytest.raises(ValueError):
        sk.materialize_secret({}, "exa", tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_materialize_dry_run_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(sk, "get_active_value", lambda env_var: "ACTIVE")
    out = sk.materialize_secret({}, "exa", tmp_path / "s", dry_run=True)
    assert "WHATIF" in out
    assert not (tmp_path / "s").exists()


def test_materialize_cli_honors_dry_run(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("A_EXA_API_KEY=ka\n")
    secrets = tmp_path / "secrets"
    monkeypatch.setattr(sk, "get_active_value", lambda v: "ka")
    monkeypatch.setattr(
        sys,
        "argv",
        ["x", "--service", "exa", "--materialize", "--dry-run", "--env-path", str(env), "--secrets-dir", str(secrets)],
    )
    with pytest.raises(SystemExit) as e:
        sk.main()
    assert e.value.code == 0
    assert not secrets.exists()


def test_next_writes_file_never_deletes_others(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("A_EXA_API_KEY=ka\nB_EXA_API_KEY=kb\n")
    secrets = tmp_path / "secrets"
    secrets.mkdir()
    (secrets / "tavily").write_text("t")
    monkeypatch.setattr(sk, "get_active_value", lambda v: "ka")
    monkeypatch.setattr(sk, "_set_user_env_var", lambda n, v: None)
    monkeypatch.setattr(sk, "_broadcast_env_change", lambda: None)
    monkeypatch.setattr(
        sys,
        "argv",
        ["x", "--service", "exa", "--next", "--env-path", str(env), "--secrets-dir", str(secrets)],
    )
    sk.main()
    assert (secrets / "exa").read_text() == "kb"
    assert (secrets / "tavily").read_text() == "t"
