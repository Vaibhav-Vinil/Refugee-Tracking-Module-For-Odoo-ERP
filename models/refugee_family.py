# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RefugeeFamily(models.Model):
    _name = "refugee.family"
    _description = "Refugee Family Group"
    _order = "name"

    name = fields.Char(string="Family Name / ID", required=True, index=True)
    member_ids = fields.One2many("refugee.profile", "family_id", string="Members")
    head_id = fields.Many2one(
        "refugee.profile",
        string="Head of Family",
        domain="[('family_id', '=', id)]",
    )
    member_count = fields.Integer(compute="_compute_member_stats", string="Member count")
    missing_member_hint = fields.Char(compute="_compute_member_stats")
    camp_id = fields.Many2one("refugee.camp.management", string="Camp")
    status = fields.Selection(
        selection=[
            ("complete", "Complete"),
            ("separated", "Separated"),
            ("partial", "Partial"),
        ],
        default="complete",
    )

    @api.depends("member_ids", "head_id")
    def _compute_member_stats(self):
        for rec in self:
            rec.member_count = len(rec.member_ids)
            if not rec.head_id and rec.member_ids:
                rec.missing_member_hint = "No head of family assigned"
            elif rec.status == "separated":
                rec.missing_member_hint = "Family reported as separated — verify members"
            else:
                rec.missing_member_hint = False
