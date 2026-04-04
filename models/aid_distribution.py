# -*- coding: utf-8 -*-

from odoo import fields, models


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
