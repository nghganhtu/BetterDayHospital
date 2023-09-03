{
    'name': 'BETTERDAY',
    'author': 'Joseph Nguyen',
    'summary': 'A module help to manage your mental hospital in reservation!',
    'depends': ['mail', 'product'],

    'data': [
        'security/ir.model.access.csv',
        'data/patient_tag_data.xml',
        'data/patient.tag.csv',
        'data/sequence_appointment_data.xml',
        'data/sequence_patient_data.xml',
        'wizard/cancel_appointment.xml',
        'views/menu.xml',
        'views/patient.xml',
        'views/female_patient.xml',
        'views/appointment.xml',
        'views/patient_tag.xml',
        'views/playground.xml',
        'views/res_config_settings_views.xml',
        'views/operations.xml',
    ]
}