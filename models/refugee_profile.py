# -*- coding: utf-8 -*-

import base64
import hashlib
import io
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class RefugeeProfile(models.Model):
    """
    Central demographic, logistical, and health data for every refugee.
    Governs their lifecycle (journey_stage), family interactions, and skills.
    Coordinates tightly with family, logistics, and resource models.
    """
    _name = "refugee.profile"
    _description = "Refugee Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "refugee_id, name"

    name = fields.Char(string="Full Name", required=True, tracking=True)
    family_name = fields.Char(string="Family Surname", tracking=True, index=True)
    refugee_id = fields.Char(
        string="Refugee ID",
        copy=False,
        readonly=True,
        index=True,
    )
    id_card_photo = fields.Image(string="ID Photo", max_width=1920, max_height=1920)
    qr_code = fields.Binary(string="QR Code", compute="_compute_qr_code", attachment=False)
    fingerprint_hash = fields.Char(
        string="Biometric Hash (simulated)",
        compute="_compute_fingerprint_hash",
        store=True,
        readonly=True,
    )

    gender = fields.Selection(
        selection=[("male", "Male"), ("female", "Female"), ("other", "Other / Unspecified")],
        tracking=True,
    )
    date_of_birth = fields.Date(string="Date of Birth", tracking=True)
    age = fields.Integer(compute="_compute_age", store=True)
    nationality_id = fields.Many2one("res.country", string="Nationality")
    languages_spoken_ids = fields.Many2many("res.lang", string="Languages Spoken")

    family_id = fields.Many2one("refugee.family", string="Family", ondelete="set null", tracking=True)
    family_head_of_ids = fields.One2many(
        "refugee.family",
        "head_id",
        string="Family as head of",
        help="One-to-one link: at most one family may have this profile as head (see unique constraint on family.head_id).",
    )
    family_status = fields.Selection(
        related="family_id.status",
        string="Family location category",
        readonly=True,
    )
    is_head_of_household = fields.Boolean(string="Head of Household")
    is_head_of_family = fields.Boolean(string="Head of Family")
    camp_id = fields.Many2one(
        "refugee.camp.management",
        string="Current Camp / Shelter",
        tracking=True,
        index=True,
    )

    skill_ids = fields.Many2many("refugee.skill", string="Skills")
    assigned_role_id = fields.Many2one(
        "refugee.camp.role",
        string="Assigned Role",
        domain="['&', ('camp_id', '=', camp_id), '|', ('capacity', '=', 0), ('has_capacity', '=', True)]",
        tracking=True,
    )

    user_id = fields.Many2one('res.users', string='Related User Account', compute='_compute_user_id', store=True)
    is_my_camp_profile = fields.Boolean(compute='_compute_is_my_camp_profile', string='Is in my camp', search='_search_is_my_camp_profile')

    @api.depends('name')
    def _compute_user_id(self):
        for profile in self:
            user = self.env['res.users'].search([('refugee_profile_id', '=', profile.id)], limit=1)
            profile.user_id = user.id if user else False

    def _compute_is_my_camp_profile(self):
        for rec in self:
            rec.is_my_camp_profile = (rec.camp_id == self.env.user.refugee_profile_id.camp_id)

    def _search_is_my_camp_profile(self, operator, value):
        profile = self.env.user.refugee_profile_id
        camp_id = profile.camp_id.id if profile and profile.camp_id else False
        if value and operator == '=' and camp_id:
            return [('camp_id', '=', camp_id)]
        return []


    id_number = fields.Char(string="Legacy ID / Paper ID")
    journey_stage = fields.Selection(
        selection=[
            ("draft", "Border intake"),
            ("vetting", "Vetting"),
            ("medical", "Medical"),
            ("assigned", "Assigned"),
            ("integrated", "Relocated / Integrated"),
        ],
        default="draft",
        tracking=True,
        group_expand=True,
    )


    vulnerability_level = fields.Selection(
        selection=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        default="low",
        tracking=True,
    )
    kanban_color = fields.Integer(
        string="Color Index",
        compute="_compute_kanban_color",
    )

    is_unaccompanied_minor = fields.Boolean()
    medical_conditions = fields.Text()
    requires_urgent_care = fields.Boolean(tracking=True)
    health_status = fields.Selection(
        selection=[
            ("unknown", "Unknown"),
            ("stable", "Stable"),
            ("needs_followup", "Needs Follow-up"),
            ("critical", "Critical"),
        ],
        default="unknown",
    )
    deceased = fields.Boolean(string="Deceased", default=False)

    active = fields.Boolean(default=True)

    aid_line_ids = fields.One2many("refugee.aid.distribution", "refugee_id", string="Aid Lines")
    aid_count = fields.Integer(compute="_compute_counts")
    family_member_count = fields.Integer(compute="_compute_counts")

    @api.model
    def _location_unknown_camp(self):
        return self.env.ref("refugee_crisis_erp.camp_location_unknown", raise_if_not_found=False)

    @api.model
    def get_family_head_change_prompt(self, profile_id=0, family_id=0, profile_name=""):
        """Used by the UI to confirm replacing the family head (public for RPC)."""
        Family = self.env["refugee.family"]
        profile_id = int(profile_id or 0)
        family_id = int(family_id or 0)
        new_name = (profile_name or "").strip()
        family = Family.browse()
        if profile_id:
            profile = self.browse(profile_id)
            if profile.exists():
                family = profile.family_id
                new_name = profile.name or new_name
        elif family_id:
            family = Family.browse(family_id)
        if not family or not family.exists():
            return {"need_confirm": False}
        head = family.head_id
        if not head:
            return {"need_confirm": False}
        if profile_id and head.id == profile_id:
            return {"need_confirm": False}
        return {
            "need_confirm": True,
            "message": _(
                "You are changing the head of the family from %(old)s to %(new)s. "
                "Are you sure you want to proceed?"
            )
            % {"old": head.name, "new": new_name or _("(new member)")},
        }

    @api.constrains("camp_id", "family_id")
    def _check_family_location_unknown_camp(self):
        pass  # removed constraint to allow setting other camps when found

    @api.depends("date_of_birth")
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if not rec.date_of_birth:
                rec.age = 0
                continue
            born = rec.date_of_birth
            rec.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    @api.depends("refugee_id", "name")
    def _compute_fingerprint_hash(self):
        for rec in self:
            raw = f"{rec.refugee_id or ''}|{rec.name or ''}".encode("utf-8")
            rec.fingerprint_hash = hashlib.sha256(raw).hexdigest()

    def _get_public_form_url(self):
        self.ensure_one()
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "").rstrip("/")
        if not base:
            base = "http://localhost:8069"
        return f"{base}/web#id={self.id}&model=refugee.profile&view_type=form"

    @api.depends("refugee_id", "name")
    def _compute_qr_code(self):
        try:
            import qrcode
        except ImportError:
            _logger.warning("python qrcode package not installed; QR codes will be empty.")
            for rec in self:
                rec.qr_code = False
            return
        for rec in self:
            if not rec.id:
                rec.qr_code = False
                continue
            url = rec._get_public_form_url()
            img = qrcode.make(url)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            rec.qr_code = base64.b64encode(buf.getvalue())

    @api.depends("vulnerability_level")
    def _compute_kanban_color(self):
        color_map = {"low": 0, "medium": 2, "high": 8, "critical": 9}
        for rec in self:
            rec.kanban_color = color_map.get(rec.vulnerability_level, 0)

    @api.depends(
        "family_id",
        "aid_line_ids",
        "family_id.member_ids",
        "family_id.member_ids.active",
        "family_id.member_ids.deceased",
    )
    def _compute_counts(self):
        for rec in self:
            rec.aid_count = len(rec.aid_line_ids)
            if rec.family_id:
                rec.family_member_count = len(
                    rec.family_id.member_ids.filtered(
                        lambda m: m.active and not m.deceased
                    )
                )
            else:
                rec.family_member_count = 0

    @api.model_create_multi
    def create(self, vals_list):
        """
        Extends creation heavily to support:
        1. Implicit Family Linking: Creates a new family on the fly if a family_name is passed but no ID.
        2. Sequence matching for automatic ID generation.
        3. Cascading changes across sibling family members.
        4. Invoking Medical coordinators if user flags critical status on creation.
        """
        Family = self.env["refugee.family"]
        out_vals = []
        for vals in vals_list:
            vals = dict(vals)
            if vals.get("family_name") and not vals.get("family_id"):
                family = Family.search([("name", "=", vals["family_name"])], limit=1)
                if not family:
                    family = Family.create({"name": vals["family_name"]})
                vals["family_id"] = family.id

            if not vals.get("refugee_id"):
                vals["refugee_id"] = self.env["ir.sequence"].next_by_code("refugee.profile.id")
            if vals.get("deceased"):
                vals["assigned_role_id"] = False
                vals["is_head_of_family"] = False
                vals["is_head_of_household"] = False
            out_vals.append(vals)
        records = super().create(out_vals)
        records._sync_family_head()
        for rec in records:
            if rec.requires_urgent_care:
                rec._notify_medical_coordinators()
        return records

    def write(self, vals):
        """
        Intercepts field updates to recompute implicit structures.
        If a refugee becomes deceased, forces promotion of a new family head. 
        Synchronizes head logic to guarantee isolation of head responsibilities globally.
        Triggers emergency notification if health statuses shift to critical.
        """
        vals = dict(vals)
        notify_candidates = self.env["refugee.profile"]
        if vals.get("requires_urgent_care"):
            notify_candidates = self.filtered(lambda r: not r.requires_urgent_care)

        if vals.get("family_name") and not vals.get("family_id") and not self.mapped("family_id"):
            Family = self.env["refugee.family"]
            family = Family.search([("name", "=", vals["family_name"])], limit=1)
            if not family:
                family = Family.create({"name": vals["family_name"]})
            vals["family_id"] = family.id

        needs_head_successor = self.env["refugee.profile"]
        if vals.get("deceased") is True:
            for rec in self:
                if not rec.deceased and rec.family_id and (
                    rec.is_head_of_family
                    or rec.is_head_of_household
                    or rec.family_id.head_id == rec
                ):
                    needs_head_successor |= rec
            vals["assigned_role_id"] = False
            vals["is_head_of_family"] = False
            vals["is_head_of_household"] = False



        res = super().write(vals)
        for rec in needs_head_successor:
            rec._promote_oldest_family_head()
        if any(
            k in vals
            for k in ("is_head_of_family", "family_id", "is_head_of_household", "deceased")
        ):
            self._sync_family_head()
        if vals.get("requires_urgent_care"):
            for rec in notify_candidates:
                if rec.requires_urgent_care:
                    rec._notify_medical_coordinators()
        return res

    def _notify_medical_coordinators(self):
        self.ensure_one()
        group = self.env.ref("refugee_crisis_erp.group_refugee_medical", raise_if_not_found=False)
        if not group or not group.user_ids:
            return
        body = _("Refugee %s (%s) requires urgent medical attention.") % (
            self.name,
            self.refugee_id or "",
        )
        Mail = self.env["mail.mail"].sudo()
        company = self.env.company
        email_from = company.email_formatted or company.email or self.env.user.email
        for user in group.user_ids:
            email = user.partner_id.email
            if not email:
                continue
            Mail.create(
                {
                    "subject": _("Urgent care: %s") % self.name,
                    "body_html": f"<p>{body}</p>",
                    "email_to": email,
                    "email_from": email_from,
                }
            ).send()

    def _sync_family_head(self):
        """
        Guarantees that when a profile becomes marked as head of family, all other valid family 
        members are stripped of the status to preserve logical unique database invariants.
        """
        for rec in self:
            if not rec.family_id or rec.deceased:
                continue
            if rec.is_head_of_family or rec.is_head_of_household:
                others = rec.family_id.member_ids - rec
                others = others.filtered(lambda m: m.active and not m.deceased)
                if others:
                    others.write({"is_head_of_family": False, "is_head_of_household": False})
                fam = rec.family_id
                if fam.head_id != rec:
                    fam.with_context(refugee_syncing_head_from_profile=True).write(
                        {"head_id": rec.id}
                    )

    def _promote_oldest_family_head(self):
        self.ensure_one()
        fam = self.family_id
        if not fam:
            return
        living = fam.member_ids.filtered(lambda m: m.active and not m.deceased)
        if not living:
            fam.with_context(refugee_syncing_head_from_profile=True).write({"head_id": False})
            return
        far_future = fields.Date.from_string("2099-12-31")

        def sort_key(m):
            return (m.date_of_birth or far_future, m.id)

        successor = min(living, key=sort_key)
        successor.write({"is_head_of_family": True, "is_head_of_household": True})

    @api.onchange("family_id")
    def _onchange_family_id_location_unknown(self):
        pass  # removed to prevent resetting the camp_id back to unknown

    def action_open_family_members(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Family Members",
            "res_model": "refugee.profile",
            "view_mode": "list,form",
            "domain": [("family_id", "=", self.family_id.id)] if self.family_id else [("id", "=", False)],
        }

    def action_open_aid(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Aid Received",
            "res_model": "refugee.aid.distribution",
            "view_mode": "list,form",
            "domain": [("refugee_id", "=", self.id)],
            "context": {"default_refugee_id": self.id},
        }

    def action_auto_assign_roles(self):
        """
        Matches profiles dynamically based on their attached skill models to open camp roles.
        If their subsets of skills overlap requirements and there's role capacity, automatically slots them.
        """
        """Match skills to camp roles with free capacity."""
        Role = self.env["refugee.camp.role"]
        assigned = 0
        for refugee in self:
            if refugee.deceased or not refugee.active:
                continue
            if not refugee.camp_id or refugee.assigned_role_id:
                continue
            roles = Role.search([("camp_id", "=", refugee.camp_id.id)])
            for role in roles:
                if role.capacity and role.assigned_count >= role.capacity:
                    continue
                if not role.required_skill_ids:
                    continue
                needed = set(role.required_skill_ids.ids)
                have = set(refugee.skill_ids.ids)
                if needed.issubset(have):
                    refugee.assigned_role_id = role
                    assigned += 1
                    break
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Role assignment",
                "message": f"Assigned roles for {assigned} profile(s).",
                "type": "success",
                "sticky": False,
            },
        }

    @api.onchange("skill_ids", "camp_id")
    def _onchange_suggest_role(self):
        if self.deceased or not self.camp_id or not self.skill_ids:
            return
        roles = self.env["refugee.camp.role"].search(
            [("camp_id", "=", self.camp_id.id)]
        )
        have = set(self.skill_ids.ids)
        for role in roles:
            needed = set(role.required_skill_ids.ids)
            if needed and needed.issubset(have) and (
                not role.capacity or role.assigned_count < role.capacity
            ):
                self.assigned_role_id = role
                break
