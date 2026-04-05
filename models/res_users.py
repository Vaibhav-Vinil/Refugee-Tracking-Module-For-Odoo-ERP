from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    refugee_profile_id = fields.Many2one(
        'refugee.profile',
        string='Linked Refugee Profile',
        help='The physical refugee profile connected to this login account.'
    )
    volunteer_id = fields.Many2one(
        'refugee.volunteer',
        string='Linked Volunteer Profile',
        help='The physical volunteer profile connected to this login account.'
    )

    @property
    def SELF_READABLE_FIELDS(self):
        """Allow users to read their own refugee/volunteer profile link,
        which is required for ir.rule domain evaluation."""
        return super().SELF_READABLE_FIELDS + [
            'refugee_profile_id',
            'volunteer_id',
        ]
