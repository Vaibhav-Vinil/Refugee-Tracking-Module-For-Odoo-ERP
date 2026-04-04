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
    quantity_available = fields.Integer(string="Quantity Available", default=0)
    quantity_required = fields.Integer(string="Quantity Required", default=100)
    expiry_date = fields.Date()
    camp_id = fields.Many2one("refugee.camp.management", required=True, ondelete="cascade")
    stock_ratio = fields.Float(
        string="Stock fill (%)",
        compute="_compute_stock_ratio",
        store=True,
        digits=(16, 2),
        help="Percentage of required quantity currently available (can exceed 100% if overstocked).",
    )

    @api.depends("quantity_available", "quantity_required")
    def _compute_stock_ratio(self):
        for rec in self:
            req = rec.quantity_required
            if req:
                rec.stock_ratio = (rec.quantity_available / req) * 100.0
            else:
                rec.stock_ratio = 100.0

    def write(self, vals):
        res = super().write(vals)
        if "quantity_available" in vals:
            for rec in self:
                threshold = max(1, (rec.quantity_required * 20) // 100) if rec.quantity_required else 0
                if rec.quantity_required > 0 and rec.quantity_available < threshold:
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
        threshold = int(
            float(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("refugee_crisis_erp.low_stock_threshold", "10")
            )
        )
        low = self.search([("quantity_available", "<", threshold)])
        for rec in low:
            rec.message_post(
                body="Low stock alert: %s is below the configured threshold (%s)."
                % (rec.name, threshold)
            )
