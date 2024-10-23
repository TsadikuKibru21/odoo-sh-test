{
    "name": "Point Of Sale - Change Payments",
    "summary": "Allow cashier to change order payments, as long as"
    " the session is not closed.",
    "category": "Point Of Sale",
    "author": "Melkam Zeyede",
    "depends": ["point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/view_pos_payment_change_wizard.xml",
        # "views/view_pos_config.xml",
        "views/view_pos_order.xml",
    ],
    "installable": True,
}
