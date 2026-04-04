/** @odoo-module **/

import { Component, onMounted, useRef, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

function loadLeaflet() {
    if (window.L) {
        return Promise.resolve();
    }
    return new Promise((resolve, reject) => {
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
        link.crossOrigin = "";
        document.head.appendChild(link);
        const script = document.createElement("script");
        script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
        script.crossOrigin = "";
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

export class CampMapDashboard extends Component {
    static props = { ...standardActionServiceProps };
    static template = xml`
        <div class="o_refugee_camp_map p-3" style="height: 100%; min-height: 650px;">
            <h4 class="mb-2">Camp locations &amp; occupancy</h4>
            <p class="text-muted small">Pins use camp GPS. Green = within capacity, red = overcrowded.</p>
            <div t-ref="map" class="border rounded bg-white" style="height: 600px; width: 100%;"/>
        </div>
    `;
    setup() {
        this.orm = useService("orm");
        this.mapRef = useRef("map");
        onMounted(() => this._initMap());
    }
    async _initMap() {
        await loadLeaflet();
        const camps = await this.orm.searchRead(
            "refugee.camp.management",
            [],
            [
                "name",
                "latitude",
                "longitude",
                "current_occupancy",
                "total_capacity",
                "overcrowded_status",
            ]
        );
        const el = this.mapRef.el;
        if (!window.L || !el) {
            return;
        }
        const map = window.L.map(el).setView([20, 20], 3);
        window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap contributors",
        }).addTo(map);
        const coords = [];
        for (const c of camps) {
            if (c.latitude && c.longitude) {
                coords.push([c.latitude, c.longitude]);
                const color = c.overcrowded_status === "overcrowded" ? "red" : "green";
                const cap = c.total_capacity ? ` / ${c.total_capacity}` : "";
                window.L.circleMarker([c.latitude, c.longitude], { color, radius: 9 })
                    .addTo(map)
                    .bindPopup(
                        `<b>${c.name}</b><br/>Occupancy: ${c.current_occupancy}${cap}`
                    );
            }
        }
        if (coords.length) {
            map.fitBounds(window.L.latLngBounds(coords), { padding: [40, 40] });
        }
    }
}

registry.category("actions").add("refugee_crisis_erp.camp_map_dashboard", CampMapDashboard);
