from odoo import models, fields, api

class RefugeeResourceRequest(models.Model):
    _name = 'refugee.resource.request'
    _description = 'Camp Resource Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Request Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    resource_id = fields.Many2one('refugee.resource.inventory', string='Requested Resource', required=True, tracking=True)
    camp_id = fields.Many2one(
        'refugee.camp.management', 
        string='Target Camp', 
        required=True, 
        tracking=True, 
        default=lambda self: self.env.user.refugee_profile_id.camp_id.id
    )
    quantity = fields.Integer(string='Quantity Requested', required=True, default=1, tracking=True)
    status = fields.Selection([
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('denied', 'Denied')
    ], string='Status', default='pending', tracking=True)
    notes = fields.Text(string='Notes / Justification')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('refugee.resource.request') or 'New'
        return super().create(vals_list)

    def action_approve(self):
        for req in self:
            if req.status == 'pending':
                req.status = 'approved'
                # Auto-create a logistics task for this approved request
                self.env['refugee.logistics.task'].create({
                    'resource_id': req.resource_id.id,
                    'camp_id': req.camp_id.id,
                    'quantity': req.quantity,
                    'task_type': 'delivery',
                    'priority': '2',
                    'destination': req.camp_id.name,
                    'request_id': req.id,
                    'notes': req.notes or '',
                    'status': 'todo',
                })
        return True

    def action_deny(self):
        for req in self:
            if req.status == 'pending':
                req.status = 'denied'
        return True
