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
    quantity_required = fields.Float(default=100.0)
    expiry_date = fields.Date()
    camp_id = fields.Many2one("refugee.camp.management", required=True, ondelete="cascade")
    stock_ratio = fields.Float(
        string="Stock Level",
        compute="_compute_stock_ratio",
        store=True,
    )

    @api.depends("quantity_available", "quantity_required")
    def _compute_stock_ratio(self):
        for rec in self:
            if rec.quantity_required:
                rec.stock_ratio = min(1.0, rec.quantity_available / rec.quantity_required)
            else:
                rec.stock_ratio = 1.0

    def write(self, vals):
        res = super().write(vals)
        if "quantity_available" in vals:
            for rec in self:
                if rec.quantity_required > 0 and rec.quantity_available < (rec.quantity_required * 0.2):
                    # Check if already a pending task to prevent spam
                    existing_task = self.env["refugee.logistics.task"].search([
                        ("resource_id", "=", rec.id),
                        ("status", "in", ["todo", "in_progress"])
                    ], limit=1)
                    if not existing_task:
                        task_vals = {
                            "name": f"Emergency Resupply: {rec.name}",
                            "task_type": "delivery",
                            "priority": "3",
                            "resource_id": rec.id,
                            "destination": rec.camp_id.name,
                        }
                        self.env["refugee.logistics.task"].create(task_vals)
        return res

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
