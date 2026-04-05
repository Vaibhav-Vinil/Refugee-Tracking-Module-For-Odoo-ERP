# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RefugeeCampManagement(models.Model):
    _name = "refugee.camp.management"
    _description = "Camp / Shelter Location"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, translate=True)

    def _compute_display_name(self):
        super()._compute_display_name()
        for rec in self:
            if rec.name == 'Location Unknown':
                rec.display_name = '𝗟𝗼𝗰𝗮𝘁𝗶𝗼𝗻 𝗨𝗻𝗸𝗻𝗼𝘄𝗻'
            else:
                rec.display_name = rec.name

    location_label = fields.Char(string="Address / Area")
    total_capacity = fields.Integer(string="Total Capacity", default=0)
    current_occupancy = fields.Integer(
        compute="_compute_occupancy_metrics",
        store=True,
        string="Current Occupancy",
    )
    latitude = fields.Float(digits=(10, 7), string="Latitude")
    longitude = fields.Float(digits=(10, 7), string="Longitude")
    overcrowded_status = fields.Selection(
        selection=[
            ("normal", "Normal"),
            ("overcrowded", "Overcrowded"),
        ],
        compute="_compute_occupancy_metrics",
        store=True,
    )
    refugee_ids = fields.One2many("refugee.profile", "camp_id", string="Refugees")
    resource_ids = fields.One2many("refugee.resource.inventory", "camp_id", string="Resources")

    @api.depends("refugee_ids", "refugee_ids.active", "refugee_ids.deceased", "total_capacity")
    def _compute_occupancy_metrics(self):
        for rec in self:
            count = len(
                rec.refugee_ids.filtered(lambda p: p.active and not p.deceased)
            )
            rec.current_occupancy = count
            if rec.total_capacity and count > rec.total_capacity:
                rec.overcrowded_status = "overcrowded"
            else:
                rec.overcrowded_status = "normal"
