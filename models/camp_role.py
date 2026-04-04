# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RefugeeCampRole(models.Model):
    _name = "refugee.camp.role"
    _description = "Camp Role / Job"

    name = fields.Char(required=True, translate=True)
    camp_id = fields.Many2one("refugee.camp.management", required=True, ondelete="cascade")
    required_skill_ids = fields.Many2many("refugee.skill", string="Required Skills")
    capacity = fields.Integer(default=1)
    assigned_profile_ids = fields.One2many("refugee.profile", "assigned_role_id", string="Assigned")
    assigned_count = fields.Integer(compute="_compute_assigned_count", store=True)
    has_capacity = fields.Boolean(compute="_compute_assigned_count", store=True)

    @api.depends(
        "assigned_profile_ids",
        "assigned_profile_ids.active",
        "assigned_profile_ids.deceased",
        "capacity",
    )
    def _compute_assigned_count(self):
        for role in self:
            assigned = role.assigned_profile_ids.filtered(
                lambda p: p.active and not p.deceased
            )
            role.assigned_count = len(assigned)
            role.has_capacity = role.assigned_count < role.capacity
