"""El chequeo de seguridad del repo debe pasar siempre (ver tools/check_seguridad.py)."""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _cargar():
    s = importlib.util.spec_from_file_location("check_seguridad", ROOT / "tools" / "check_seguridad.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def test_repo_sin_secretos_ni_datos_en_claro():
    assert _cargar().chequear() == []


def test_detecta_un_token_falso(tmp_path, monkeypatch):
    m = _cargar()
    falso = "ghp_" + "A" * 36
    import re
    assert re.search(m.PATRONES["token de GitHub"], falso)
    assert re.search(m.PATRONES["clave privada"], "-----BEGIN PRIVATE KEY-----")
