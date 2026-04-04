# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RefugeeAidDistribution(models.Model):
    _name = "refugee.aid.distribution"
    _description = "Aid Distribution Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    refugee_id = fields.Many2one(
        "refugee.profile",
        required=True,
        ondelete="restrict",
        index=True,
    )
    resource_id = fields.Many2one(
        "refugee.resource.inventory",
        string="Resource",
        ondelete="restrict",
    )
    distributed_by_id = fields.Many2one(
        "refugee.volunteer",
        string="Distributed By",
        ondelete="set null",
    )
    quantity = fields.Float(default=1.0)
    date = fields.Datetime(default=fields.Datetime.now)
    status = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("delivered", "Delivered"),
        ],
        default="delivered",
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.status == "delivered" and rec.resource_id:
                rec.resource_id.quantity_available -= rec.quantity
        return records

    def write(self, vals):
        # Optional: handle transition to "delivered"
        for rec in self:
            old_status = rec.status
            if vals.get("status") == "delivered" and old_status != "delivered":
                if rec.resource_id:
                    rec.resource_id.quantity_available -= rec.quantity
        return super().write(vals)
