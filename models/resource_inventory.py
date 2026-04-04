# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RefugeeResourceInventory(models.Model):
    _name = "refugee.resource.inventory"
    _description = "Camp Resource Inventory"
    _inherit = ["mail.thread"]

    name = fields.Char(required=True)
    resource_type = fields.Selection(
        selection=[
            ("food", "Food"),
            ("medical", "Medical"),
            ("water", "Water"),
            ("other", "Other"),
        ],
        default="food",
        required=True,
    )
    quantity_available = fields.Float(default=0.0)
    expiry_date = fields.Date()
    camp_id = fields.Many2one("refugee.camp.management", required=True, ondelete="cascade")
    stock_ratio = fields.Float(
        string="Stock Level",
        compute="_compute_stock_ratio",
    )

    @api.depends("quantity_available")
    def _compute_stock_ratio(self):
        for rec in self:
            # Simple demo scale: ratio capped at 1.0 for progressbar (assume 1000 units = full)
            rec.stock_ratio = min(1.0, (rec.quantity_available or 0.0) / 1000.0)

    @api.model
    def _cron_check_low_stock(self):
        threshold = float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("refugee_crisis_erp.low_stock_threshold", "10")
        )
        low = self.search([("quantity_available", "<", threshold)])
        for rec in low:
            rec.message_post(
                body="Low stock alert: %s is below the configured threshold (%.1f)."
                % (rec.name, threshold)
            )
