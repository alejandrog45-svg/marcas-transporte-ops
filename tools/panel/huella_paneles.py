#!/usr/bin/env python3
"""Huella de los paneles armados (red de seguridad del plan de paridad de Aereostar).

Calcula el SHA-256 de cada panel generado ignorando solo la hora de armado, para comprobar que un
cambio NO alteró el panel de la otra marca. Uso (después de `python tools/panel/build.py`):
    python tools/panel/huella_paneles.py              # imprime las huellas
    python tools/panel/huella_paneles.py --actualizar # guarda tests/golden/huella_paneles.json (solo si el cambio es intencional)
"""
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "tests" / "golden" / "huella_paneles.json"
FILES = {"ubertransfer": "docs/panel_keywords.html", "aereostar": "docs/panel_aereostar.html"}


def huellas():
    out = {}
    for name, rel in FILES.items():
        p = ROOT / rel
        if not p.exists():
            return None
        txt = re.sub(r'"builtAt":"[^"]*"', '"builtAt":""', p.read_text(encoding="utf-8"))
        out[name] = hashlib.sha256(txt.encode("utf-8")).hexdigest()
    return out


if __name__ == "__main__":
    h = huellas()
    if h is None:
        sys.exit("Faltan los paneles generados: ejecuta python tools/panel/build.py")
    if "--actualizar" in sys.argv:
        GOLDEN.write_text(json.dumps(h, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(h, indent=2))
