# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RefugeeResourceInventory(models.Model):
    """
    Tracks inventory of essential resources bound to a specific physical camp.
    Automatically flags low-stock conditions and initiates logistics resupply tasks.
    """
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
    expiry_not_applicable = fields.Boolean(string="Expiry Not Applicable", default=False)
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
        """
        Computes the ratio of current available stock versus required stock.
        Used visually to display stock health in progress bars.
        """
        for rec in self:
            req = rec.quantity_required
            if req:
                rec.stock_ratio = (rec.quantity_available / req) * 100.0
            else:
                rec.stock_ratio = 100.0

    def write(self, vals):
        """
        Extends the standard write operation to monitor inventory drops.
        If stock slips below 20% of required amounts, automatically creates a high-priority 
        logistics task demanding emergency resupply, circumventing manual monitoring.
        """
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
                            "task_type": "delivery",
                            "priority": "3",
                            "resource_id": rec.id,
                            "camp_id": rec.camp_id.id,
                            "destination": rec.camp_id.name,
                            "notes": f"Emergency Resupply: {rec.name} is critically low.",
                        }
                        self.env["refugee.logistics.task"].create(task_vals)
        return res

    @api.model
    def _cron_check_low_stock(self):
        """
        Cron scheduled action that scans inventory systematically for critically low levels 
        and posts an alert into the chatter so administrators are notified in real-time.
        """
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
