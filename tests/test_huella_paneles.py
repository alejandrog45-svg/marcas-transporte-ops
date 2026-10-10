import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "tools" / "panel"))
import huella_paneles  # noqa: E402


def test_ubertransfer_no_cambia_con_el_trabajo_de_aereostar():
    """Regla antirretroceso: el panel de UberTransfer debe salir idéntico mientras se trabaja en Aereostar.
    Se compara contra la huella guardada; si el cambio es intencional, actualizarla con --actualizar y documentarlo."""
    actual = huella_paneles.huellas()
    if actual is None:
        pytest.skip("paneles no armados (docs/ es generado); ejecutar tools/panel/build.py")
    golden = json.loads(huella_paneles.GOLDEN.read_text(encoding="utf-8"))
    assert actual["ubertransfer"] == golden["ubertransfer"]
