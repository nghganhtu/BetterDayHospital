from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    cancel_days = fields.Integer(string='Cancel Days', config_parameter='Hospital.cancel_day')