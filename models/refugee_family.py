# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RefugeeFamily(models.Model):
    """
    Represents a group of refugee profiles making up a family unit.
    Provides tracking of head of family assignments, computes grouping status 
    (separated, reunited, etc.), and enforces logical constraints across members.
    """
    _name = "refugee.family"
    _description = "Refugee Family Group"
    _order = "name"

    _sql_constraints = [
        (
            "refugee_family_head_profile_unique",
            "unique(head_id)",
            "Each person can only be the head of one family at a time.",
        ),
    ]

    name = fields.Char(string="Family Name / ID", required=True, index=True)
    member_ids = fields.One2many("refugee.profile", "family_id", string="Members")
    # One2one in Odoo = Many2one + unique(head_id); inverse on profile: family_head_of_ids
    head_id = fields.Many2one(
        "refugee.profile",
        string="Head of Family",
        domain="[('family_id', '=', id)]",
        index="btree_not_null",
        copy=False,
        help="At most one head per family; each profile may be head of at most one family (enforced by a unique database constraint).",
    )
    member_count = fields.Integer(compute="_compute_member_stats", string="Member count")
    missing_member_hint = fields.Char(compute="_compute_member_stats")
    camp_id = fields.Many2one("refugee.camp.management", string="Camp")
    status = fields.Selection(
        selection=[
            ("reunited", "Reunited"),
            ("separated", "Partial"),
            ("location_unknown", "Seperated"),
        ],
        default="reunited",
        compute="_compute_family_status",
        store=True,
        readonly=False,
    )
    voluntary_separation = fields.Boolean("Voluntary Separation")
    separation_notes = fields.Text("Separation Notes", help="Reason if voluntary separation")

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides default creation to strictly enforce unique head of family. 
        If a designated head is assigned that already heads another family, 
        they are systematically unlinked from the old family.
        """
        out_vals = []
        for vals in vals_list:
            v = dict(vals)
            if v.get("head_id"):
                conflicts = self.env["refugee.family"].search([("head_id", "=", v["head_id"])])
                if conflicts:
                    conflicts.write({"head_id": False})
            out_vals.append(v)
        records = super().create(out_vals)
        return records

    def write(self, vals):
        """
        Overrides default write to manage head of family bidirectional 
        synchronization, while passing contexts to avoid infinite recursion.
        """
        vals = dict(vals)
        # When profile._sync_family_head updates head_id, skip writing back to profiles
        # (avoids infinite recursion: family.write → profile.write → _sync → family.write).
        skip_profile_pairing = self.env.context.get("refugee_syncing_head_from_profile")
        # unique(head_id): ensure no other family still points at this profile as head
        if "head_id" in vals and vals.get("head_id"):
            conflicts = self.env["refugee.family"].search(
                [("head_id", "=", vals["head_id"]), ("id", "not in", self.ids)]
            )
            if conflicts:
                conflicts.write({"head_id": False})
        if "head_id" in vals and not skip_profile_pairing:
            before = {r: r.head_id for r in self}
        else:
            before = {}
        res = super().write(vals)
        if "head_id" in vals and not skip_profile_pairing:
            for fam in self:
                prev = before.get(fam)
                if prev and prev != fam.head_id:
                    prev.write({"is_head_of_family": False, "is_head_of_household": False})
                if fam.head_id:
                    fam.head_id.write({"is_head_of_family": True, "is_head_of_household": True})
        return res

    @api.depends("member_ids.camp_id", "member_ids.active", "member_ids.deceased")
    def _compute_family_status(self):
        """
        Dynamically computes the geographic integrity of the family unit.
        - 'location_unknown' if any active member's camp is strictly the designated unknown camp.
        - 'reunited' if all known members occupy exactly the same camp.
        - 'separated' if active members are distributed across multiple distinct known camps.
        """
        loc = self.env.ref("refugee_crisis_erp.camp_location_unknown", raise_if_not_found=False)
        for rec in self:
            members = rec.member_ids.filtered(lambda m: m.active and not m.deceased)
            camps = members.mapped("camp_id")
            
            if loc and loc in camps:
                rec.status = "location_unknown"
            elif len(camps) <= 1:
                rec.status = "reunited"
            else:
                rec.status = "separated"

    @api.depends("member_ids", "member_ids.active", "member_ids.deceased", "head_id", "status")
    def _compute_member_stats(self):
        for rec in self:
            living = rec.member_ids.filtered(lambda m: m.active and not m.deceased)
            rec.member_count = len(living)
            if not rec.head_id and rec.member_ids:
                rec.missing_member_hint = "No head of family assigned"
            else:
                rec.missing_member_hint = False
