"""Configuración por variables de entorno. Nada sensible vive en el código."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    site_url: str
    gsc_site: str
    ga4_property_id: str
    google_sa_json: str
    audit_tag: str = ""          # p. ej. "aereostar": separa archivos y alertas de otra marca
    audit_delay: float = 0.0     # segundos de pausa entre páginas (cuidar sitios ajenos)
    audit_max_urls: int = 0      # 0 = sin tope

    @property
    def has_google(self) -> bool:
        return bool(self.google_sa_json)


def load() -> Config:
    site = os.environ.get("SITE_URL", "https://ubertransfer.cl").rstrip("/")
    return Config(
        site_url=site,
        gsc_site=os.environ.get("GSC_SITE", ""),
        ga4_property_id=os.environ.get("GA4_PROPERTY_ID", ""),
        google_sa_json=os.environ.get("GOOGLE_SA_JSON", ""),
        audit_tag=os.environ.get("AUDIT_TAG", "").strip().lower(),
        audit_delay=float(os.environ.get("AUDIT_DELAY", "0") or 0),
        audit_max_urls=int(os.environ.get("AUDIT_MAX_URLS", "0") or 0),
    )
