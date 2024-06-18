{
	'name': "Sales Validation",
	'version': '1.10',
	'author': "Etta/Zelalem",
	'depends': ['base', 'sale_management','purchase','stock','account_accountant','hr_expense','hr','product'],
	'data': [
		'security/ir.model.access.csv',
		# 'views/assets.xml',
		'views/sales_validation.xml',

	],
	'demo': [
	   
	],
 
	'installable': True,
	'application': True,
	'auto_install': False,
  
}
