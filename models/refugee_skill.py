# -*- coding: utf-8 -*-

from odoo import fields, models


class RefugeeSkill(models.Model):
    _name = "refugee.skill"
    _description = "Refugee Skill Tag"

    name = fields.Char(required=True, translate=True)
    category = fields.Selection(
        selection=[
            ("medical", "Medical"),
            ("education", "Education"),
            ("labor", "Labor"),
            ("logistics", "Logistics"),
        ],
        default="labor",
        required=True,
    )
