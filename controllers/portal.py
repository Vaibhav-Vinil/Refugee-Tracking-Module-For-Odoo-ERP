# -*- coding: utf-8 -*-

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LibreTranslate configuration
# Multiple free public instances in priority order. The first that responds
# wins. No API key is required for these public instances.
# ---------------------------------------------------------------------------
LIBRETRANSLATE_INSTANCES = [
    "https://translate.argosopentech.com",
    "https://translate.terraprint.co",
    "https://translate.fedilab.app",
    "https://libretranslate.pussthecat.org",
]

# Hardcoded fallback language list — used when ALL instances are unreachable.
# Covers the most common languages relevant to refugee/humanitarian contexts.
FALLBACK_LANGUAGES = [
    {"code": "ar", "name": "Arabic"},
    {"code": "zh", "name": "Chinese"},
    {"code": "cs", "name": "Czech"},
    {"code": "nl", "name": "Dutch"},
    {"code": "en", "name": "English"},
    {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"},
    {"code": "el", "name": "Greek"},
    {"code": "hi", "name": "Hindi"},
    {"code": "hu", "name": "Hungarian"},
    {"code": "id", "name": "Indonesian"},
    {"code": "ga", "name": "Irish"},
    {"code": "it", "name": "Italian"},
    {"code": "ja", "name": "Japanese"},
    {"code": "ko", "name": "Korean"},
    {"code": "fa", "name": "Persian"},
    {"code": "pl", "name": "Polish"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "ro", "name": "Romanian"},
    {"code": "ru", "name": "Russian"},
    {"code": "es", "name": "Spanish"},
    {"code": "sv", "name": "Swedish"},
    {"code": "tr", "name": "Turkish"},
    {"code": "uk", "name": "Ukrainian"},
    {"code": "ur", "name": "Urdu"},
    {"code": "vi", "name": "Vietnamese"},
]

_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "OnwardsERP/1.0 (refugee aid system)",
}


def _try_instances(path, post_data=None, timeout=12):
    """
    Attempts the given LibreTranslate API path against each configured
    instance in order. Returns (response_data_dict, None) on success or
    (None, last_error_string) if all instances fail.
    Validates that the response is actually JSON.
    """
    last_error = "No instances configured"
    for base in LIBRETRANSLATE_INSTANCES:
        url = base.rstrip("/") + path
        try:
            headers = dict(_HEADERS)
            if post_data:
                req = urllib.request.Request(url, data=post_data, headers=headers, method="POST")
            else:
                req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw_data = resp.read()
                try:
                    data = json.loads(raw_data.decode("utf-8"))
                    # Additional check for instances returning HTML error pages with 200 OK
                    if not isinstance(data, (list, dict)):
                        raise ValueError("Response is not a JSON object/list")
                    return data, None
                except (json.JSONDecodeError, ValueError) as e:
                    _logger.warning("Instance %s returned invalid JSON: %s...", base, raw_data[:100])
                    last_error = f"Invalid JSON from {base}"
                    continue
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            last_error = body or f"HTTP {exc.code} from {base}"
            _logger.warning("LibreTranslate instance %s returned HTTP %s: %s", base, exc.code, body[:200])
        except Exception as exc:
            last_error = str(exc)
            _logger.warning("LibreTranslate instance %s unreachable: %s", base, exc)
    return None, last_error


class RefugeePortal(http.Controller):
    """JSON/HTTP endpoints for external tools (Leaflet map, mobile) and the in-app translator."""

    # -------------------------------------------------------------------------
    # Camp locations endpoint — consumed by OWL Leaflet dashboard
    # -------------------------------------------------------------------------

    @http.route("/refugee_crisis_erp/camp_locations", type="jsonrpc", auth="user")
    def camp_locations(self):
        """
        API endpoint that fetches core logistical and geographical metadata
        for all active camps. Typically consumed by the OWL Leaflet dashboard.
        """
        camps = request.env["refugee.camp.management"].search_read(
            [],
            ["name", "latitude", "longitude", "current_occupancy", "total_capacity", "overcrowded_status"],
        )
        return {"camps": camps}

    # -------------------------------------------------------------------------
    # LibreTranslate proxy endpoints
    # -------------------------------------------------------------------------

    @http.route(
        "/refugee_crisis_erp/translate/languages",
        type="jsonrpc",
        auth="user",
    )
    def translate_languages(self):
        """
        Returns the list of supported translation languages from LibreTranslate.
        Tries multiple public instances in order. If all fail, returns a
        hardcoded fallback list so the UI still works offline.
        """
        data, error = _try_instances("/languages")
        if data:
            return data
        _logger.warning("All LibreTranslate instances failed for /languages (%s); using fallback.", error)
        return FALLBACK_LANGUAGES

    @http.route(
        "/refugee_crisis_erp/translate",
        type="jsonrpc",
        auth="user",
    )
    def translate(self, q="", source="auto", target="en", **kw):
        """
        Proxies a translation request to LibreTranslate.
        Parameters received automatically from JSON-RPC payload.
        Returns dict: {"translatedText": "..."} or {"error": "..."}
        """
        q = (q or "").strip()
        if not q:
            return {"error": "Nothing to translate."}

        post_data = json.dumps({
            "q": q,
            "source": source or "auto",
            "target": target or "en",
            "format": "text",
        }).encode("utf-8")

        data, error = _try_instances("/translate", post_data=post_data)
        if data:
            return data
        return {"error": f"Translation service unavailable: {error}"}
