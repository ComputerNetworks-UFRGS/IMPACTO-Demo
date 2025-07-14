import pycountry
from django.utils.translation import get_language, gettext_lazy as _
from typing import List, Dict

COUNTRY_TRANSLATIONS = {
    'Brasil': 'Brazil',
    'Estados Unidos': 'United States',
    'Reino Unido': 'United Kingdom',
    'Alemanha': 'Germany',
    'França': 'France',
    'Itália': 'Italy',
    'Espanha': 'Spain',
    'Índia': 'India',
    'Afeganistão': 'Afghanistan',
    'África do Sul': 'South Africa',
    'Albânia': 'Albania',
    'Andorra': 'Andorra',
    'Angola': 'Angola',
    'Antígua e Barbuda': 'Antigua and Barbuda',
    'Arábia Saudita': 'Saudi Arabia',
    'Argélia': 'Algeria',
    'Argentina': 'Argentina',
    'Armênia': 'Armenia',
    'Austrália': 'Australia',
    'Áustria': 'Austria',
    'Azerbaijão': 'Azerbaijan',
    'Bahamas': 'Bahamas',
    'Bangladesh': 'Bangladesh',
    'Barbados': 'Barbados',
    'Bahrein': 'Bahrain',
    'Bélgica': 'Belgium',
    'Belize': 'Belize',
    'Benin': 'Benin',
    'Bielorrússia': 'Belarus',
    'Bolívia': 'Bolivia',
    'Bósnia e Herzegovina': 'Bosnia and Herzegovina',
    'Botswana': 'Botswana',
    'Brunei': 'Brunei',
    'Bulgária': 'Bulgaria',
    'Burkina Faso': 'Burkina Faso',
    'Burundi': 'Burundi',
    'Butão': 'Bhutan',
    'Cabo Verde': 'Cape Verde',
    'Camarões': 'Cameroon',
    'Camboja': 'Cambodia',
    'Canadá': 'Canada',
    'Catar': 'Qatar',
    'Cazaquistão': 'Kazakhstan',
    'Chade': 'Chad',
    'Chile': 'Chile',
    'Chipre': 'Cyprus',
    'Colômbia': 'Colombia',
    'Comores': 'Comoros',
    'Congo': 'Congo',
    'Coreia do Norte': 'North Korea',
    'Coreia do Sul': 'South Korea',
    'Costa do Marfim': 'Ivory Coast',
    'Costa Rica': 'Costa Rica',
    'Croácia': 'Croatia',
    'Cuba': 'Cuba',
    'Dinamarca': 'Denmark',
    'Dominica': 'Dominica',
    'Egito': 'Egypt',
    'El Salvador': 'El Salvador',
    'Emirados Árabes Unidos': 'United Arab Emirates',
    'Equador': 'Ecuador',
    'Eritreia': 'Eritrea',
    'Eslováquia': 'Slovakia',
    'Eslovênia': 'Slovenia',
    'Estônia': 'Estonia',
    'Eswatini': 'Eswatini',
    'Etiópia': 'Ethiopia',
    'Fiji': 'Fiji',
    'Filipinas': 'Philippines',
    'Finlândia': 'Finland',
    'Gabão': 'Gabon',
    'Gâmbia': 'Gambia',
    'Gana': 'Ghana',
    'Geórgia': 'Georgia',
    'Granada': 'Grenada',
    'Grécia': 'Greece',
    'Guatemala': 'Guatemala',
    'Guiana': 'Guyana',
    'Guiné': 'Guinea',
    'Guiné-Bissau': 'Guinea-Bissau',
    'Guiné Equatorial': 'Equatorial Guinea',
    'Haiti': 'Haiti',
    'Honduras': 'Honduras',
    'Hungria': 'Hungary',
    'Iêmen': 'Yemen',
    'Ilhas Marshall': 'Marshall Islands',
    'Ilhas Salomão': 'Solomon Islands',
    'Indonésia': 'Indonesia',
    'Irã': 'Iran',
    'Iraque': 'Iraq',
    'Irlanda': 'Ireland',
    'Islândia': 'Iceland',
    'Israel': 'Israel',
    'Jamaica': 'Jamaica',
    'Japão': 'Japan',
    'Jordânia': 'Jordan',
    'Kiribati': 'Kiribati',
    'Kosovo': 'Kosovo',
    'Kuwait': 'Kuwait',
    'Laos': 'Laos',
    'Lesoto': 'Lesotho',
    'Letônia': 'Latvia',
    'Líbano': 'Lebanon',
    'Libéria': 'Liberia',
    'Líbia': 'Libya',
    'Liechtenstein': 'Liechtenstein',
    'Lituânia': 'Lithuania',
    'Luxemburgo': 'Luxembourg',
    'Macedônia do Norte': 'North Macedonia',
    'Madagascar': 'Madagascar',
    'Malásia': 'Malaysia',
    'Malawi': 'Malawi',
    'Maldivas': 'Maldives',
    'Mali': 'Mali',
    'Malta': 'Malta',
    'Marrocos': 'Morocco',
    'Maurício': 'Mauritius',
    'Mauritânia': 'Mauritania',
    'México': 'Mexico',
    'Mianmar': 'Myanmar',
    'Micronésia': 'Micronesia',
    'Moçambique': 'Mozambique',
    'Moldávia': 'Moldova',
    'Mônaco': 'Monaco',
    'Mongólia': 'Mongolia',
    'Montenegro': 'Montenegro',
    'Namíbia': 'Namibia',
    'Nauru': 'Nauru',
    'Nepal': 'Nepal',
    'Nicarágua': 'Nicaragua',
    'Níger': 'Niger',
    'Nigéria': 'Nigeria',
    'Noruega': 'Norway',
    'Nova Zelândia': 'New Zealand',
    'Omã': 'Oman',
    'Países Baixos': 'Netherlands',
    'Paquistão': 'Pakistan',
    'Palau': 'Palau',
    'Panamá': 'Panama',
    'Papua-Nova Guiné': 'Papua New Guinea',
    'Paraguai': 'Paraguay',
    'Peru': 'Peru',
    'Polônia': 'Poland',
    'Portugal': 'Portugal',
    'Quênia': 'Kenya',
    'Quirguistão': 'Kyrgyzstan',
    'República Centro-Africana': 'Central African Republic',
    'República Checa': 'Czech Republic',
    'República Dominicana': 'Dominican Republic',
    'Romênia': 'Romania',
    'Ruanda': 'Rwanda',
    'Rússia': 'Russia',
    'Samoa': 'Samoa',
    'San Marino': 'San Marino',
    'Santa Lúcia': 'Saint Lucia',
    'São Cristóvão e Nevis': 'Saint Kitts and Nevis',
    'São Tomé e Príncipe': 'São Tomé and Príncipe',
    'São Vicente e Granadinas': 'Saint Vincent and the Grenadines',
    'Seicheles': 'Seychelles',
    'Senegal': 'Senegal',
    'Serra Leoa': 'Sierra Leone',
    'Sérvia': 'Serbia',
    'Singapura': 'Singapore',
    'Síria': 'Syria',
    'Somália': 'Somalia',
    'Sri Lanka': 'Sri Lanka',
    'Sudão': 'Sudan',
    'Sudão do Sul': 'South Sudan',
    'Suécia': 'Sweden',
    'Suíça': 'Switzerland',
    'Suriname': 'Suriname',
    'Tailândia': 'Thailand',
    'Taiwan': 'Taiwan',
    'Tajiquistão': 'Tajikistan',
    'Tanzânia': 'Tanzania',
    'Timor-Leste': 'Timor-Leste',
    'Togo': 'Togo',
    'Tonga': 'Tonga',
    'Trinidad e Tobago': 'Trinidad and Tobago',
    'Tunísia': 'Tunisia',
    'Turcomenistão': 'Turkmenistan',
    'Turquia': 'Turkey',
    'Tuvalu': 'Tuvalu',
    'Ucrânia': 'Ukraine',
    'Uganda': 'Uganda',
    'Uruguai': 'Uruguay',
    'Uzbequistão': 'Uzbekistan',
    'Vanuatu': 'Vanuatu',
    'Vaticano': 'Vatican City',
    'Venezuela': 'Venezuela',
    'Vietnã': 'Vietnam',
    'Zâmbia': 'Zambia',
    'Zimbábue': 'Zimbabwe',
    'República Democrática do Congo': 'Democratic Republic of the Congo',
}

def translate_country_to_english(country_name):
    if get_language() == 'pt-br':
        return COUNTRY_TRANSLATIONS.get(country_name, country_name)
    return country_name

def translate_country_to_portuguese(country_name_en):
    """
    Traduz o nome do país de inglês para português
    """
    if get_language() == 'pt-br':
        # Cria um dicionário reverso para traduzir de inglês para português
        reverse_translations = {v: k for k, v in COUNTRY_TRANSLATIONS.items()}
        return reverse_translations.get(country_name_en, country_name_en)
    return country_name_en

def validate_and_translate_country(country_name):
    # Tenta validar o nome original
    try:
        pycountry.countries.search_fuzzy(country_name)[0]
        return country_name
    except LookupError:
        pass

    # Se estiver em português, tenta traduzir e validar
    if get_language() == 'pt-br':
        english_name = COUNTRY_TRANSLATIONS.get(country_name)
        if english_name:
            try:
                pycountry.countries.search_fuzzy(english_name)[0]
                return english_name
            except LookupError:
                pass

    # Se chegou aqui, não foi possível validar ou traduzir
    raise ValueError(_("Invalid country name. Please enter a valid country. If you are using portuguese, please try to enter the country name in English if is not working correctly."))


def get_tech_dimension_table(advanced_company_profile) -> List[Dict]:
    """
    Gera a tabela de dimensão técnica a partir dos campos do AdvancedCompanyProfile.
    
    Retorna uma lista de dicionários, onde cada dicionário representa uma defesa técnica.
    """
    tech_dimensions_mapping = [
        {
            'name': _("Updated Inventory"),
            'confidentiality': True,
            'integrity': False,
            'availability': False,
            'field': 'updated_inventory'
        },
        {
            'name': _("Backup Maintenance"),
            'confidentiality': False,
            'integrity': True,
            'availability': True,
            'field': 'backup_maintenance'
        },
        {
            'name': _("Risk Prioritization"),
            'confidentiality': True,
            'integrity': True,
            'availability': False,
            'field': 'risk_prioritization'
        },
        {
            'name': _("Authentication Factors"),
            'confidentiality': True,
            'integrity': True,
            'availability': False,
            'field': 'authentication_factors'
        },
        {
            'name': _("Cloud Solution Type"),
            'confidentiality': True,
            'integrity': False,
            'availability': True,
            'field': 'cloud_solution_type'
        },
        {
            'name': _("IT System Monitoring"),
            'confidentiality': False,
            'integrity': True,
            'availability': True,
            'field': 'it_system_monitoring'
        },
        {
            'name': _("Periodic System Updates"),
            'confidentiality': False,
            'integrity': True,
            'availability': True,
            'field': 'periodic_system_updates'
        },
        {
            'name': _("Data Encryption in Storage"),
            'confidentiality': True,
            'integrity': True,
            'availability': False,
            'field': 'data_encryption_in_storage'
        },
        {
            'name': _("Data Encryption in Transit"),
            'confidentiality': True,
            'integrity': True,
            'availability': False,
            'field': 'data_encryption_in_transit'
        },
        {
            'name': _("VPN for Remote Access"),
            'confidentiality': True,
            'integrity': False,
            'availability': True,
            'field': 'vpn_for_remote_access'
        },
        {
            'name': _("Cybersecurity Awareness and Training"),
            'confidentiality': True,
            'integrity': True,
            'availability': False,
            'field': 'cybersecurity_awareness_and_training'
        },
        {
            'name': _("Documented Response Plan"),
            'confidentiality': False,
            'integrity': True,
            'availability': True,
            'field': 'documented_response_plan'
        },
        {
            'name': _("Response Plan Update"),
            'confidentiality': False,
            'integrity': True,
            'availability': True,
            'field': 'response_plan_update'
        },
        {
            'name': _("Operational Recovery Capacity"),
            'confidentiality': False,
            'integrity': False,
            'availability': True,
            'field': 'operational_recovery_capacity'
        },
        {
            'name': _("Credentials Maintenance"),
            'confidentiality': True,
            'integrity': True,
            'availability': False,
            'field': 'credentials_maintenance'
        },
        {
            'name': _("Vulnerability Identification"),
            'confidentiality': True,
            'integrity': True,
            'availability': False,
            'field': 'vulnerability_identification'
        },
        {
            'name': _("Network Systems Traffic Monitoring"),
            'confidentiality': True,
            'integrity': True,
            'availability': True,
            'field': 'network_systems_traffic_monitoring'
        },
        {
            'name': _("Threat Identification Process"),
            'confidentiality': True,
            'integrity': True,
            'availability': True,
            'field': 'threat_identification_process'
        },
        {
            'name': _("IT Records Presence"),
            'confidentiality': False,
            'integrity': True,
            'availability': False,
            'field': 'it_records_presence'
        },
        {
            'name': _("Antivirus"),
            'confidentiality': True,
            'integrity': True,
            'availability': False,
            'field': 'antivirus'
        },
        {
            'name': _("Firewall"),
            'confidentiality': True,
            'integrity': True,
            'availability': False,
            'field': 'firewall'
        },
        {
            'name': _("Intrusion Detection System (IDS)"),
            'confidentiality': True,
            'integrity': True,
            'availability': False,
            'field': 'intrusion_detection_system'
        },
        {
            'name': _("Endpoint Detection and Response (EDR)"),
            'confidentiality': True,
            'integrity': True,
            'availability': False,
            'field': 'endpoint_detection_and_response'
        },
        {
            'name': _("IT Security Team"),
            'confidentiality': True,
            'integrity': True,
            'availability': True,
            'field': 'it_security_team'
        },
    ]
    tech_dimension_table = []
    
    for defense in tech_dimensions_mapping:
        field_name = defense['field']
        
        # Verifica se o campo existe no modelo
        if hasattr(advanced_company_profile, field_name):
            field_value = getattr(advanced_company_profile, field_name)
            
            # Determina se a defesa está habilitada
            if isinstance(field_value, bool):
                enabled = field_value
            elif isinstance(field_value, str):
                # Para campos de escolha, como 'cloud_solution_type'
                enabled = field_value.lower() != 'none'
            elif isinstance(field_value, (int, float)):
                # Para campos numéricos, como 'authentication_factors'
                enabled = field_value > 0
            else:
                enabled = False  # Tipo não reconhecido
            
        else:
            # Campo não encontrado no modelo
            enabled = False
        
        tech_dimension_table.append({
            'name': defense['name'],
            'confidentiality': defense['confidentiality'],
            'integrity': defense['integrity'],
            'availability': defense['availability'],
            'enabled': enabled,
        })
    
    return tech_dimension_table