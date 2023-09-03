from odoo import api, fields, models, _

class PatientTag(models.Model):
    _name = "patient.tag"
    _description = "Patient Tag"

    name = fields.Char(string='Name', tracking=True, required=True, trim=False)

    active = fields.Boolean(string='Active', default=True, copy=False)

    color = fields.Integer(string='Color')

    color_2 = fields.Integer(string='Color 2')

    sequence = fields.Integer(string='Sequence', default=1)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (copy)", self.name)
        default['sequence'] = 10
        return super(PatientTag, self).copy(default)

    _sql_constraints = [
        ('unique_tag_name', 'unique (name)', 'Name must be unique.'),
        ('check_sequence', 'check(sequence > 0)', 'Sequence must be non zero positive number.')
    ]