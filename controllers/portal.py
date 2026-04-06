# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class RefugeePortal(http.Controller):
    """Optional JSON endpoint for external tools (Leaflet, mobile)."""

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
