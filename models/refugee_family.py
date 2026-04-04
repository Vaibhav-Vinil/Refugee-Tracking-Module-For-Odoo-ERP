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
            ("location_unknown", "Location unknown/Missing"),
        ],
        default="complete",
        compute="_compute_family_status",
        store=True,
        readonly=False,
    )

    @api.depends("member_ids.camp_id", "member_ids.active", "member_ids.deceased")
    def _compute_family_status(self):
        for rec in self:
            if rec.status in ("separated", "location_unknown"):
                continue  # Keep manual override
            members = rec.member_ids.filtered(lambda m: m.active and not m.deceased)
            if not members:
                rec.status = "complete"
                continue
            camps = members.mapped("camp_id")
            if len(camps) <= 1:
                rec.status = "complete"
            else:
                rec.status = "partial"


    @api.depends("member_ids", "member_ids.active", "member_ids.deceased", "head_id", "status")
    def _compute_member_stats(self):
        for rec in self:
            living = rec.member_ids.filtered(lambda m: m.active and not m.deceased)
            rec.member_count = len(living)
            if not rec.head_id and rec.member_ids:
                rec.missing_member_hint = "No head of family assigned"
            elif rec.status == "separated":
                rec.missing_member_hint = "Family reported as separated — verify members"
            else:
                rec.missing_member_hint = False
