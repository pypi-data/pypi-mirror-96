from edc_constants.constants import OTHER

from edc_list_data import PreloadData

list_data = {
    "edc_list_data.antibiotic": [
        ("amoxicillin_ampicillin", "Amoxicillin/Ampicillin"),
        ("ceftriaxone", "Ceftriaxone"),
        ("ciprofloxacin", "Ciprofloxacin"),
        ("doxycycline", "Doxycycline"),
        ("erythromycin", "Erythromycin"),
        ("flucloxacillin", "Flucloxacillin"),
        ("gentamicin", "Gentamicin"),
        (OTHER, "Other, specify"),
    ],
    "edc_list_data.neurological": [
        ("focal_neurologic_deficit", "Focal neurologic deficit"),
        ("meningism", "Meningism"),
        ("papilloedema", " Papilloedema"),
        ("CN_III_palsy", "Cranial Nerve III palsy"),
        ("CN_IV_palsy", "Cranial Nerve IV palsy"),
        ("CN_VIII_palsy", "Cranial Nerve VIII palsy"),
        ("CN_VII_palsy", "Cranial Nerve VII palsy"),
        ("CN_VI_palsy", "Cranial Nerve VI palsy"),
        (OTHER, "Other CN palsy"),
    ],
    "edc_list_data.significantnewdiagnosis": [
        ("bacteraemia", "Bacteraemia"),
        ("bacterial_pneumonia", "Bacterial pneumonia"),
        ("diarrhoeal_wasting", "Diarrhoeal wasting"),
        ("kaposi_sarcoma", "Kaposi’s sarcoma"),
        ("malaria", "Malaria"),
        ("tb_extra_pulmonary", "TB extra-pulmonary"),
        ("tb_pulmonary", "TB pulmonary"),
        (OTHER, "Other, please specify:"),
    ],
    "edc_list_data.symptom": [
        ("double_vision", "Double vision"),
        ("behaviour_change", "Behaviour change"),
        ("confusion", "Confusion"),
        ("cough", "Cough"),
        ("drowsiness", "Drowsiness"),
        ("fever", "Fever"),
        ("focal_weakness", "Focal weakness"),
        ("headache", "Headache"),
        ("hearing_loss", "Hearing loss"),
        ("nausea", "Nausea"),
        ("seizures_gt_72", "Seizures (72 hrs - 1 mo)"),
        ("seizures_lt_72 hrs", "Seizures (<72 hrs)"),
        ("shortness_of_breath", "Shortness of breath"),
        ("skin_lesions", "Skin lesions"),
        ("visual_loss", "Visual loss"),
        ("vomiting", "Vomiting"),
        ("weight_loss", "Weight loss"),
    ],
}


# preload_data = PreloadData(list_data=list_data)
