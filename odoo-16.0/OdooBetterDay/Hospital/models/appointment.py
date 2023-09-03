from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import random


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Appointment"
    _rec_name = 'id'
    _order = 'id desc'

    id = fields.Char(string='ID', tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', ondelete='cascade', tracking=True)
    gender = fields.Selection(related='patient_id.gender')
    appointment_time = fields.Datetime(string='Appointment Time', default=fields.Datetime.now)
    booking_date = fields.Date(string='Booking Date', default=fields.Date.context_today, tracking=True)
    ref = fields.Char(string='Reference', help='Reference from patient records')
    prescription = fields.Html(string='Prescription')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string='Priority')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_consultation', 'In Consultation'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], default='draft', string='Status', required=True, tracking=True)
    doctor_id = fields.Many2one('res.users', string='Doctor', tracking=True)
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines', 'appointment_id', string='Pharmacy Lines')
    hide_sales_price = fields.Boolean(string='Hide Sales Price')
    operation_id = fields.Many2one('hospital.operation', string='Operation', tracking=True)
    progress = fields.Integer(string='Progress', compute='_compute_progress')
    duration = fields.Float(string='Duration', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    #amount_total = fields.Monetary(string='Total', currency_field='currency_id')

    amount_total = fields.Monetary(string='Total', compute='_compute_amount_total', currency_field='currency_id')
    #def _compute_amount_total(self):
    #    for rec in self:
    #        subtotal = self.env['appointment.pharmacy.lines']._compute_price_subtotal()
    #        rec.amount_total += subtotal

    @api.model
    def create(self, vals):
        vals['id'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
        return super(HospitalAppointment, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("You can delete appointment only in draft status !"))
        return super(HospitalAppointment, self).unlink()

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        self.ref = self.patient_id.ref

    def action_notification(self):
        action = self.env.ref('Hospital.action_hospital_patient')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Click to open the patient record'),
                'message': '%s',
                'links': [{
                    'label': self.patient_id.name,
                    'url': f'#action={action.id}&id={self.patient_id.id}&model=hospital.patient',
                }],
                'sticky': False,
            }
        }

    def action_test(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://nguyen-hoang-anh-tu.jimdosite.com'
        }

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_in_consultation(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'in_consultation'

    def action_done(self):
        for rec in self:
            rec.state = 'done'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Done',
                'type': 'rainbow_man',
            }
        }

    def action_cancel(self):
        action = self.env.ref('Hospital.action_cancel_appointment').read()[0]
        return action

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'draft':
                progress = 25
            elif rec.state == 'in_consultation':
                progress = 75
            elif rec.state == 'done':
                progress = 100
            else:
                progress = 0
            rec.progress = progress

    @api.depends('pharmacy_line_ids')
    def _compute_amount_total(self):
        for rec in self:
            amount_total = 0
            for line in rec.pharmacy_line_ids:
                amount_total += line.price_subtotal
            rec.amount_total = amount_total

class AppointmentPharmacyLines(models.Model):
    _name = "appointment.pharmacy.lines"
    _description = "Appointment Pharmacy Lines"

    product_id = fields.Many2one('product.product', required=True)
    price_unit = fields.Float(related='product_id.list_price')
    qty = fields.Integer(string='Quantity')
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment')
    currency_id = fields.Many2one('res.currency', related='appointment_id.currency_id')
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_price_subtotal',
                                     currency_field='currency_id')

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.price_unit = self.product_id.lst_price

    @api.depends('price_unit', 'qty')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.qty
