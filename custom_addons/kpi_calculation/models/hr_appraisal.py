from datetime import datetime, timedelta
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class HRAppraisal(models.Model):
    _inherit = 'hr.appraisal'
    
    position_id = fields.Many2one('hr.job', string="Job Position",compute="_compute_position_id",store=True)
    total_weighted_score = fields.Float(string="Total Weighted Score",compute="_compute_total_weighted_score",readonly=True)
    appraisal_evaluation = fields.One2many('appraisal.evaluations', 'appraisal_id', string='Evaluation')
    appraisal_evaluation_readonly = fields.Boolean(compute='_compute_readonly_appraisal_evaluation', store=False)

    @api.depends('employee_id')
    def _compute_position_id(self):

        for rec in self:
            rec.position_id=rec.employee_id.job_id.id
    @api.depends('state')
    def _compute_readonly_appraisal_evaluation(self):
        for record in self:
            record.appraisal_evaluation_readonly = record.state in ['done', 'pending']

    
    @api.onchange('position_id')
    def _onchange_position_id(self):
        """Fetch and set appraisal evaluations based on the selected position's KPIs."""
        if not self.position_id:
            self.appraisal_evaluation = [(5, 0, 0)]  # Clear if no position selected
            return
        
        # Find KPI configuration for the selected position
        kpi_position = self.env['kpi.per.position'].search([('position_id', '=', self.position_id.id)], limit=1)
        
        # Clear existing evaluations
        self.appraisal_evaluation = [(5, 0, 0)]
        
        if kpi_position:
            evaluations = []
            for kpi_eval in kpi_position.appraisal_evaluation:
                # Prepare appraisal evaluation data
                evaluations.append((0, 0, {
                    'criteria_description': kpi_eval.criteria_description.id,
                    'weight': kpi_eval.weight,
                    'unit_measurement': kpi_eval.unit_measurement,
                    'target': kpi_eval.target,
                    'min_threshold': kpi_eval.min_threshold,
                    'max_threshold': kpi_eval.max_threshold,
                    'appraisal_id':self.id
                }))
                
            # Set fetched evaluations to the appraisal_evaluation field
            self.appraisal_evaluation = evaluations
    
    @api.depends('appraisal_evaluation.weighted_score')
    def _compute_total_weighted_score(self):
            self.total_weighted_score = sum(rec.weighted_score for rec in self.appraisal_evaluation)
            if self.total_weighted_score>100:
                raise UserError("Total Weight Score must be Less than 100!!")

  
    @api.model
    def generate_appraisals_based_on_kpi(self):
        """Generate appraisals for employees based on their job positions' KPIs."""
        # Fetch the duration after recruitment from settings
        setting = self.env['res.config.settings'].search([], limit=1)
        duration_after_recruitment = setting.duration_after_recruitment

        # Search for all employees with active contracts
        employees = self.env['hr.employee'].search([
            ('contract_ids.state', '=', 'open')
        ])

        for employee in employees:
            # Fetch the hire date from the employee's active contract
            contract = employee.contract_ids.filtered(lambda c: c.state == 'open')
            if not contract:
                continue  # Skip if no active contract

            # Determine the start date for the appraisal based on the last appraisal or hire date
            last_appraisal = self.search([
                ('employee_id', '=', employee.id)
            ], order='create_date desc', limit=1)

            # If a previous appraisal exists, start from the last appraisal date; otherwise, use contract start date
            if last_appraisal:
                appraisal_start_date = last_appraisal.create_date.date()
            else:
                appraisal_start_date = contract.date_start

            # Calculate end date as today
            appraisal_end_date = datetime.today().date()
            
            # Ensure it's time for a new appraisal
            # if appraisal_end_date <= appraisal_start_date + timedelta(days=duration_after_recruitment * 30):
            #     continue  # Skip if it's not time for a new appraisal
            
            job_position = employee.job_id

            # Search for the KPI configuration related to the job position
            kpi_per_position = self.env['kpi.per.position'].search([
                ('position_id', '=', job_position.id)
            ], limit=1)

            if kpi_per_position:
                # Create a new appraisal
                appraisal = self.create({
                    'employee_id': employee.id,
                    'position_id': job_position.id,
                })

                total_weighted_score = 0.0  # Initialize total weighted score

                # Loop through the KPI evaluations and create appraisal evaluations
                _logger.info("################ outside for loop ###################")
                for kpi_evaluation in kpi_per_position.appraisal_evaluation:
                    _logger.info("################ inside for loop ###################")
                    actual_value = self._compute_actual_value(employee, kpi_evaluation, appraisal_start_date, appraisal_end_date)

                    # Calculate achievement percentage
                    achievement_percentage = (actual_value / kpi_evaluation.target * 100) if kpi_evaluation.target else 0.0

                    # Calculate weighted score
                    weighted_score = (achievement_percentage * kpi_evaluation.weight) / 100
                    
                    # Create the appraisal evaluation record
                    self.env['appraisal.evaluations'].create({
                        'criteria_description': kpi_evaluation.criteria_description.id,
                        'actual': actual_value,
                        'weight': kpi_evaluation.weight,
                        'unit_measurement': kpi_evaluation.unit_measurement,
                        'target': kpi_evaluation.target,
                        'min_threshold': kpi_evaluation.min_threshold,
                        'max_threshold': kpi_evaluation.max_threshold,
                        'appraisal_id': appraisal.id,
                        'achievement_percentage': achievement_percentage,
                        'weighted_score': weighted_score,
                    })

                    # Update total weighted score
                    total_weighted_score += weighted_score

                # Set the total weighted score on the appraisal
                appraisal.total_weighted_score = total_weighted_score

    def _compute_actual_value(self, employee, kpi_evaluation, start_date, end_date):
        """Calculate the actual value based on the criteria description within the specified date range."""
        
        _logger.info("############################ _compute_actual_value ##################")
        _logger.info(kpi_evaluation.criteria_description.name)
        if kpi_evaluation.criteria_description.name == 'attendance':
            _logger.info("############################ call the att ##################")
            return self._compute_attendance_value(employee, start_date, end_date)
        elif kpi_evaluation.criteria_description.name == 'average_order_time':
            return self._compute_average_order_time(employee, start_date, end_date)
        return 0.0

    def _compute_attendance_value(self, employee, start_date, end_date):
        """Fetches actual attendance for the given employee from hr.attendance within a specific date range."""
        # Search for attendance records within the specified date range
        _logger.info("############################ called the att ##################")

        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', start_date),
            ('check_out', '<=', end_date)
        ])
        _logger.info("################ the attendances ############")
        _logger.info(attendances)

        # Sum total worked hours within this period
        # actual_attendance = sum(attendance.worked_hours for attendance in attendances)
        return len(attendances)

    def _compute_average_order_time(self, employee, start_date, end_date):
        """Calculate average order time within the specified date range from pos_preparation_display.display."""
        pos_configs = self.env['pos.config'].search([ 
            ('create_date', '>=', start_date),
            ('create_date', '<=', end_date)
            ])
        _logger.info("####################### all pos config ##############")
        _logger.info(pos_configs)
        # Get the IDs of the found pos.config records
        pos_config_ids = pos_configs.mapped('id')
        
        # Search for displays within the date range and matching pos_config_ids
        displays = self.env['pos_preparation_display.display'].search([
            ('pos_config_ids', 'in', pos_config_ids),
           
        ])
        
        # Calculate total average time and count the displays
        total_average_time = sum(display.average_time for display in displays)
        # display_count = len(displays)
        # # Compute average order time
        # average_order_time = total_average_time / display_count if display_count > 0 else 0
        return total_average_time