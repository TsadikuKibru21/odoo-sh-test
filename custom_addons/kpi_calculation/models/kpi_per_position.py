from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class KpiPerPosition(models.Model):
    _name = 'kpi.per.position'
    _description = 'KPI Per Position'

    name = fields.Char(string="Name", required=True)
    position_id = fields.Many2one('hr.job', string="Job Position", required=True)
    appraisal_evaluation=fields.One2many('appraisal.evaluation','kpi_per_position',string='Evaluation')

class AppraisalCriteria(models.Model):
    _name='appraisal.criteria'

    name=fields.Char(string='Criteria')


class AppraisalEvaluation(models.Model):
    _name = 'appraisal.evaluation'
    _description = 'Appraisal Evaluation'


    criteria_description = fields.Many2one(
            'appraisal.criteria',
            string="Criteria Description",
            required=True,  
            help="Select the criteria for the report"
        )
    weight = fields.Float(string="Weight", required=True)
    unit_measurement = fields.Char(string="Unit of Measurement")
    target = fields.Float(string="Target Value")
    min_threshold = fields.Float(string="Minimum Threshold")
    max_threshold = fields.Float(string="Maximum Threshold")

    kpi_per_position = fields.Many2one('kpi.per.position', string='KPI Per Position', ondelete='cascade')
    
    @api.constrains('weight', 'kpi_per_position')
    def check_weight(self):
        for record in self:
            total_weight = sum(record.kpi_per_position.appraisal_evaluation.mapped('weight'))
            if total_weight > 100:
                raise UserError(_("The total weight for all evaluations should not exceed 100."))




class AppraisalEvaluations(models.Model):
    _name = 'appraisal.evaluations'
    _description = 'Appraisal Evaluation'


    criteria_description = fields.Many2one(
            'appraisal.criteria',
            string="Criteria Description",
            required=True,  
            help="Select the criteria for the report"
        ) 
    actual = fields.Float(string="Actual", required=True)

    weight = fields.Float(string="Weight", required=True)
    unit_measurement = fields.Char(string="Unit of Measurement")
    target = fields.Float(string="Target Value")
    min_threshold = fields.Float(string="Minimum Threshold")
    max_threshold = fields.Float(string="Maximum Threshold")
    # actual = fields.Float(string="Actual Performance")
    achievement_percentage = fields.Float(
        string="Achievement (%)", compute="_compute_achievement_percentage", store=True)
    weighted_score = fields.Float(
        string="Weighted Score", compute="_compute_weighted_score", store=True)
    # total_weighted_score = fields.Float(
    #     string="Total Weighted Score", compute="_compute_total_weighted_score", store=True)
    # kpi_per_position = fields.Many2one('kpi.per.position', string='KPI Per Position', ondelete='cascade')
    
    appraisal_id = fields.Many2one('hr.appraisal', string='Appraisal', ondelete='cascade')


    # @api.onchange('actual')
    # def _onchange_actual(self):

    #     _logger.info("######################## _onchange_actual ##########")
    #     for rec in self:
    #         rec.achievement_percentage=(rec.actual/rec.target)*100
    #         _logger.info(rec.achievement_percentage)
    #         _logger.info(rec.actual)
    #         _logger.info(rec.target)


    @api.depends('actual', 'target')
    def _compute_achievement_percentage(self):
        _logger.info("######################## _compute_achievement_percentage ##########")
        for rec in self:
            if rec.target!=0:
                rec.achievement_percentage=(rec.actual/rec.target)*100
                _logger.info(rec.achievement_percentage)
                _logger.info(rec.actual)
                _logger.info(rec.target)

    @api.depends('achievement_percentage', 'weight')
    def _compute_weighted_score(self):
        _logger.info("######################## _compute_weighted_score ##########")

        for rec in self:
            if rec.weight!=0:
                rec.weighted_score=(rec.achievement_percentage*rec.weight)/100
                _logger.info(rec.weighted_score)
                _logger.info(rec.achievement_percentage)
                _logger.info(rec.weight)


    # @api.constrains('criteria_description', 'appraisal_id')
    # def check_criteria_and_fetch_weight(self):
    #     """ Check if criteria exists in KPI per position, and set weight if found """
    #     for record in self:
    #         # Search for the KPI configuration based on the position
    #         kpi_per_position = self.env['kpi.per.position'].search([
    #             ('position_id', '=', record.appraisal_id.position_id.id),
    #         ], limit=1)

    #         if not kpi_per_position:
    #             raise UserError(_("No KPI configuration found for the selected position."))

    #         # Check if the criteria exist in KPI per position
    #         kpi_criteria = kpi_per_position.appraisal_evaluation.filtered(
    #             lambda ev: ev.criteria_description == record.criteria_description)

    #         if not kpi_criteria:
    #             raise UserError(_(
    #                 "The criteria '{}' is not configured in KPI for the position '{}'."
    #             ).format(record.criteria_description.name, record.appraisal_id.position_id.name))

    #         # Set the weight from KPI per position to appraisal evaluation
    #         record.weight = kpi_criteria.weight

    #         # Calculate actual value based on `hr.attendance` data if criteria is attendance
    #         if record.criteria_description.name == 'attendance':
    #             record.actual = self._compute_actual_attendance(record.appraisal_id.position_id)
            
    #         elif record.criteria_description.name == 'average_order_time':
    #             record.actual = self._compute_average_order_time(record.appraisal_id.position_id)


    # def _compute_actual_attendance(self, position):
    #     """ Fetches actual attendance for the given position from hr.attendance """
    #     attendances = self.env['hr.attendance'].search([
    #         ('employee_id.job_id', '=', position.id)
    #     ])
    #     # Example: Sum total attendance days or hours
    #     actual_attendance = sum(attendance.worked_hours for attendance in attendances)
    #     return actual_attendance

    
    # def _compute_average_order_time(self, position):
    #     """ Calculate average order time over the last 6 months from pos_preparation_display.display """
    #     six_months_ago = datetime.today() - timedelta(days=6 * 30)
    #     today = datetime.today()
        
    #     # Retrieve `display` records within the last six months
    #     displays = self.env['pos_preparation_display.display'].search([])

    #     total_average_time = 0
    #     display_count = 0

    #     for display in displays:
    #         # Check if the display's `pos_config_id` has a creation date within the last six months
    #         pos_config = self.env['pos.config'].search([
    #             ('id', '=', display.pos_config_id.id),
    #             ('create_date', '>=', six_months_ago),
    #             ('create_date', '<=', today),
    #         ], limit=1)

    #         if pos_config:
    #             # Only sum `average_time` for displays within the specified date range
    #             total_average_time += display.average_time
    #             display_count += 1

    #     # Calculate the average if there are valid displays
    #     average_order_time = total_average_time / display_count if display_count > 0 else 0

    #     return average_order_time


    
    # @api.depends('actual', 'target')
    # def _compute_achievement_percentage(self):
    #     for record in self:
    #         if record.target:
    #             record.achievement_percentage = (record.actual / record.target) * 100

    # @api.depends('achievement_percentage', 'weight')
    # def _compute_weighted_score(self):
    #     for record in self:
    #         record.weighted_score = (record.achievement_percentage * record.weight) / 100

    # @api.depends('weighted_score')
    # def _compute_total_weighted_score(self):
    #     for record in self:
    #         total_score = self.kpi_per_position.search([('position_id', '=', record.position_id.id)])
    #         record.total_weighted_score = sum(total.weighted_score for total in total_score)
    
    # def fetch_attendance_data(self):
    #     for record in self:
    #         attendance_records = self.env['hr.attendance'].search([
    #             ('employee_id.job_id', '=', record.position_id.id),
    #             ('check_in', '>=', start_date),
    #             ('check_out', '<=', end_date)
    #         ])
    #         record.actual = len(attendance_records)  