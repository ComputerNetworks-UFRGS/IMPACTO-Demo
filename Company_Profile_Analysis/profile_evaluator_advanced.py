from collections import Counter
import numpy as np
import math
from dashboard.models import CompanyProfile, CompanyAssets, AnnualRevenue, CybersecuritySpending, AdvancedCompanyProfile, AttackHistory, CyberSecurityData, Region

# ===========================================================================================================================
# =====================================================CONSTANTS=============================================================
# ===========================================================================================================================

# -> variables
malware_flag, phishing_flag, ddos_flag = 1,1,1
valor_medio = 6

# -> sectors
SECTORS = ['Healthcare','Government','Retail','Finance','Education','Entertainment','Technology','Others']
SECTORS_WEIGHTS = [0.3,0.5,0.8,1.25,2.0]

# -> regions
COUNTRIES = ['United States','Brazil','Germany','France','Italy','United Kingdom','China','Japan','Australia','Canada','India','Russia','Ukraine','UAE','Others']
CONTINENT = ['Europe','South America','North America','Africa','Asia','Oceania','EMEA','LATAM','APAC','NA']
Europe = ['Germany', 'France', 'Italy', 'United Kingdom', 'Ukraine']
Middle_East = ['UAE']
Africa = ['South Africa']
Asia = ['China', 'Japan', 'India', 'Russia']
Oceania = ['Australia']
South_America = ['Brazil']
North_America = ['Canada', 'United States']

COUNTRY_WEIGHTS = [0.3,0.5,0.8,1.25,2.0]
CONTINENT_WEIGHTS = [0.3,0.5,0.8,1.25,2.0]

pesos_ataques = [[10,50,10,50,5,50,50,50,5,-30,50,50,10,10,50,50,5,10,50,50,50,50,50,10,10],
                 [10,5,10,50,5,10,10,5,5,-30,50,50,10,10,50,50,5,10,50,50,5,5,50,10,10],
                 [10,5,10,5,50,50,10,5,5,5,5,10,10,50,5,10,50,10,10,5,50,50,5,10,10]]

pesos_att_por_setor = [[1.5,1.25,1],
                       [1.25,1,1.5],
                       [1.25,1.5,1],
                       [1.25,1.5,1],
                       [1.5,1.25,1],
                       [1.25,1,1.5],
                       [1.25,1.5,1],
                       [1.5,1.25,1]]

MIN_RESILIENCE = 0.5
MAX_RESILIENCE = 4.5

# ===========================================================================================================================
# ==============================================COMPLEMENTARY FUNCTIONS======================================================
# ===========================================================================================================================

# working the setup
continent_dict = {}
for country in Europe:
    continent_dict[country] = 'Europe'
for country in Middle_East:
    continent_dict[country] = 'Middle East'
for country in Africa:
    continent_dict[country] = 'Africa'
for country in Asia:
    continent_dict[country] = 'Asia'
for country in Oceania:
    continent_dict[country] = 'Oceania'
for country in South_America:
    continent_dict[country] = 'South America'
for country in North_America:
    continent_dict[country] = 'North America'

# ===========================================================================================================================
# =================================================SECTOR EVALUATOR==========================================================
# ===========================================================================================================================
# evaluate the sector, making the comparison with others sectors
def sector_evaluator(typeattack,sector_company,database):
    sector_points = 1.0
    data_perc = []
    sum_perc, media_perc, sector_perc = 0,5,0
    data_spec = []
    sum_geral = 0

    typeattack_lowercase = typeattack.lower()

    # gathering infos from database
    for data in database:
        #print(f'%%%%%%%%%% {data.prob_a_priori} - {data.prob_marginal} - {data.p_a_given_b}')
        if (data.prob_a_priori == typeattack or data.prob_a_priori == typeattack_lowercase) and data.prob_marginal.capitalize() in SECTORS and data.p_a_given_b != '-':
            sum_geral += float(data.p_a_given_b)
            data_perc.append(float(data.p_a_given_b))
            if data.prob_marginal == sector_company.capitalize():
                #print(f'>>>>>> {data.prob_a_priori} - {data.prob_marginal} - {data.p_a_given_b}')
                data_spec.append(data.p_a_given_b)

    # verifying if there is only one information about sectors
    if len(data_spec) < 1:
        print(f'!Banco de Dados insuficiente para uma análise por setores para o ciberataque {typeattack}.!')
    # calcuting the mean and the standart deviation to compare percentages
    else:
        # evaluating the specific sector
        sum_perc = float(sum(data_spec))
        # mean of the specific sector
        media_perc = sum_perc / len(data_spec)

        # mean of all sectors
        media_general = sum_geral / len(data_perc)
        # stardant variation of all sectors
        stand_deviation = round(np.std(data_perc),2)

        data_perc.sort()
        if media_perc <= float(data_perc[0]):
            sector_points = SECTORS_WEIGHTS[0]
        elif media_perc < media_general-stand_deviation:
            sector_points = SECTORS_WEIGHTS[1]
        elif media_perc >= media_general-stand_deviation and sector_perc <= media_general+stand_deviation:
            sector_points = SECTORS_WEIGHTS[2]
        elif media_perc > media_general+stand_deviation:
            sector_points = SECTORS_WEIGHTS[3]
        elif media_perc >= float(data_perc[-1]):
            sector_points = SECTORS_WEIGHTS[4]

        print(f'Percentage Sector: {media_perc}, Points: {sector_points}, Min: {data_perc[0]}, Max: {data_perc[-1]}')

    return sector_points, round(media_perc,2)

# ===========================================================================================================================
# =================================================REGION EVALUATOR==========================================================
# ===========================================================================================================================

# used to analyze the region of the company in comparison on the world
def region_evaluator(typeattack,country_company,database, continent_dict):
    attack_data_country,attack_data_continent = [],[]
    aux_country, aux_continent = [],[]
    country_points,continent_points = 1.0,1.0
    country_count,continent_count = 0,0
    country_perc,continent_perc = 0,0
    sum_perc_country, sum_perc_continent = 0,0

    typeattack_lower = typeattack.lower()
    continent_company = continent_dict.get(country_company,None)
    
    # gathering the specific data
    for data in database:
        if (data.prob_a_priori == typeattack or data.prob_a_priori == typeattack_lower) and data.prob_marginal in COUNTRIES and data.p_a_given_b != '-':
            attack_data_country.append(data)
            aux_country.append(float(data.p_a_given_b))
        if (data.prob_a_priori == typeattack or data.prob_a_priori == typeattack_lower) and data.prob_marginal in CONTINENT and data.p_a_given_b != '-':
            attack_data_continent.append(data)
            aux_continent.append(float(data.p_a_given_b))

    ### analysis by country
    if len(attack_data_country) < 1:
        print('!Banco de Dados insuficiente para uma análise por países.!')
    else:
        for var in attack_data_country:
            sum_perc_country += float(var.p_a_given_b)
        media_perc_country = sum_perc_country / len(attack_data_country)
        stand_deviation_country = round(np.std(aux_country),2)

        # calculating the chance (mean) of the attack
        for data in attack_data_country:
            if country_company == data.prob_marginal:
                country_perc += float(data.p_a_given_b)
                country_count += 1
        country_perc = country_perc/country_count if country_count!= 0 else 0

        # finding the position of the percentage and giving the score
        aux_country.sort()
        if country_perc <= float(aux_country[0]):
            country_points = COUNTRY_WEIGHTS[0]
        elif country_perc < media_perc_country-stand_deviation_country:
            country_points = COUNTRY_WEIGHTS[1]
        elif country_perc >= media_perc_country-stand_deviation_country and country_perc <= media_perc_country+stand_deviation_country:
            country_points = COUNTRY_WEIGHTS[2]
        elif country_perc > media_perc_country+stand_deviation_country:
            country_points = COUNTRY_WEIGHTS[3]
        elif country_perc >= float(aux_country[len(aux_country)-1]):
            country_points = COUNTRY_WEIGHTS[4]
            
    ### analysis by continent
    if len(attack_data_continent) <= 1:
        print('!Banco de Dados insuficiente para uma análise por continentes.!')
    else:
        for var in attack_data_continent:
            sum_perc_continent += float(var.p_a_given_b)
        media_perc_continent = sum_perc_continent / len(attack_data_continent)
        stand_deviation_continent = round(np.std(aux_continent),2)

        # calculating the chance (mean) of the attack
        for data in attack_data_continent:
            if continent_company == data.prob_marginal:
                continent_perc += float(data.p_a_given_b)
                continent_count += 1
        continent_perc = continent_perc/continent_count if continent_count!=0 else 0

        # finding the position of the percentage and giving the score
        aux_continent.sort()
        if continent_perc <= float(aux_continent[0]):
            continent_points = CONTINENT_WEIGHTS[0]
        elif continent_perc < media_perc_continent-stand_deviation_continent:
            continent_points = CONTINENT_WEIGHTS[1]
        elif continent_perc >= media_perc_continent-stand_deviation_continent and continent_perc <= media_perc_continent+stand_deviation_continent:
            continent_points = CONTINENT_WEIGHTS[2]
        elif continent_perc > media_perc_continent+stand_deviation_continent:
            continent_points = CONTINENT_WEIGHTS[3]
        elif continent_perc >= float(aux_continent[len(aux_continent)-1]):
            continent_points = CONTINENT_WEIGHTS[4]
    
    # final calculation of the region evaluator
    region_points = (country_points + continent_points)/2
    print('Region Points:\t\t', region_points)

    # choosing the percentage based on infos that were gathered
    if country_perc <= 0.0:
        final_perc = continent_perc
    elif continent_perc <= 0.0:
        final_perc = country_perc
    else:
        final_perc = (country_perc+continent_perc)/2

    return region_points, round(final_perc,2)

# ===========================================================================================================================
# =================================================COMPANY EVALUATOR=========================================================
# ===========================================================================================================================
# used to convert company data to list
def company_tech_dimension_to_list(company_profile, att_hist):
    prep_company = []

    if company_profile.updated_inventory == True:
        prep_company.append(1)
    else:
        prep_company.append(0)
    
    if company_profile.backup_maintenance == 'On Site':
        prep_company.append('On Site')
    elif company_profile.backup_maintenance == 'Offsite':
        prep_company.append('Offsite')
    elif company_profile.backup_maintenance == 'Regular':
        prep_company.append('Regular')
    elif company_profile.backup_maintenance == 'Critical':
        prep_company.append('Critical')
    elif company_profile.backup_maintenance == True: # if they didn't find anything
        prep_company.append('Regular')
    else:
        prep_company.append('None')

    if company_profile.risk_prioritization == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    prep_company.append(company_profile.authentication_factors)
    prep_company.append(company_profile.cloud_solution_type)

    if company_profile.it_system_monitoring == True:
        prep_company.append(1)
    else:
        prep_company.append(0)
    
    if company_profile.periodic_system_updates == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.data_encryption_in_storage == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.data_encryption_in_transit == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.vpn_for_remote_access == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.cybersecurity_awareness_and_training == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.documented_response_plan == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.response_plan_update == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.operational_recovery_capacity == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.credentials_maintenance == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.vulnerability_identification == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.network_systems_traffic_monitoring == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.threat_identification_process == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.it_records_presence == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.antivirus == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.firewall == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.intrusion_detection_system == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.endpoint_detection_and_response == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    if company_profile.it_security_team == True:
        prep_company.append(1)
    else:
        prep_company.append(0)

    att_breach, att_malware, att_phishing, att_ddos = 0,0,0,0
    for att in att_hist:
        if att.attack_type == 'Breach':
            att_breach += 1
        elif att.attack_type == 'Malware':
            att_malware += 1
        elif att.attack_type == 'Phishing':
            att_phishing += 1
        elif att.attack_type == 'DDoS':
            att_ddos += 1
    prep_company.append([att_breach, att_malware, att_phishing, att_ddos])

    return prep_company

# used to verify how much prepared is the company against cyberattacks (company's resilience)
def company_evaluator(typeattack,company_profile, att_hist):
    company_points = 1
    sum_points = 0
    sum_weights = 0

    prep_company = company_tech_dimension_to_list(company_profile, att_hist)
    desl_att = 0
    
    if typeattack == 'malware':
        desl_att = 0
    elif typeattack == 'phishing':
        desl_att = 1
    elif typeattack == 'DDoS':
        desl_att = 2
    
    peso_att = pesos_ataques[desl_att]

    print(f'Company Industry Type: {company_profile.industry_type}')
    for i in range(len(prep_company)):
        if (type(prep_company[i]) == int and prep_company[i] >= 1) or type(prep_company[i]) == str:
            sum_points += peso_att[i]
        sum_weights += abs(peso_att[i])

    final_score = MIN_RESILIENCE + MAX_RESILIENCE*(sum_points/sum_weights)
    
    company_points = round(final_score,2)
    print("Company Preparation:\t", company_points)
    return company_points

# ===========================================================================================================================
# =====================================================IMPORTS===============================================================
# ===========================================================================================================================

# based on company's resilience for a type of attack, calculate the chance of attack success
def attack_success(chance_att, prep_company):
    return round(chance_att,2)

# main
def risk_analysis_advanced(database, company_profile, attack_history):
    bg_color = 0x000000
    text_score = ''
    insights_pos, insights_neg = [],[]

    # finding infos
    #print('INFOS\n\n', company_profile)
    sector_company = company_profile.industry_type
    #print(sector_company)
    country_company = company_profile.headquarters_country

    # evaluation
    print('\nMALWARE')
    malware_sector, malware_sector_perc = sector_evaluator('malware',sector_company,database)
    malware_region, malware_reg_perc = region_evaluator('malware',country_company,database,continent_dict)
    malware_resilience = round(company_evaluator('malware',company_profile,attack_history),2)
    malware_prep = round(1/malware_resilience,2)
    malware = round(min(valor_medio * malware_sector * malware_region * malware_prep,10),2)
    malware_att_succ = attack_success(malware_sector_perc, malware_resilience) if malware_sector_perc else attack_success(malware_reg_perc, malware_resilience)
    
    print("\nPHISHING")
    phishing_sector, phishing_sector_perc = sector_evaluator('phishing',sector_company,database)
    phishing_region, phishing_reg_perc = region_evaluator('phishing',country_company,database,continent_dict)
    phishing_resilience = round(company_evaluator('phishing',company_profile,attack_history),2)
    phishing_prep = round(1/phishing_resilience,2)
    phishing = round(min(valor_medio * phishing_sector * phishing_region * phishing_prep,10),2)
    phishing_att_succ = attack_success(phishing_sector_perc, phishing_resilience) if phishing_sector_perc else attack_success(phishing_reg_perc, phishing_resilience)

    print('\nDDoS')
    ddos_sector, ddos_sector_perc = sector_evaluator('DDoS',sector_company,database)
    ddos_region, ddos_reg_perc = region_evaluator('DDoS',country_company,database,continent_dict)
    ddos_resilience = round(company_evaluator('DDoS',company_profile,attack_history),2)
    ddos_prep = round(1/ddos_resilience,2)
    ddos = round(min(valor_medio * ddos_sector * ddos_region * ddos_prep,10),2)
    ddos_att_succ = attack_success(ddos_sector_perc, ddos_resilience) if ddos_sector_perc else attack_success(ddos_reg_perc, ddos_resilience)

    peso_do_setor = 0
    setores_lower = [s.lower() for s in SECTORS]
    if sector_company.lower() in setores_lower:
        idx = setores_lower.index(sector_company.lower())
        peso_do_setor = pesos_att_por_setor[idx]
    else:
        peso_do_setor = pesos_att_por_setor[-1]

    formula = (malware*peso_do_setor[0] + phishing*peso_do_setor[1] + ddos*peso_do_setor[2])/(sum(peso_do_setor))

    # based on final_score, we decide the text_score
    final_score = round(min(formula,10),2)
    print("\nCompany's final score: " + str(final_score))
    if final_score >= 8:
        text_score = "Critical"
    elif final_score >= 6:
        text_score = "Dangerous"
    elif final_score >= 3:
        text_score = "Caution"
    elif final_score >= 1:
        text_score = "Normal"
    else:
        text_score = "Healthy"

    return final_score, text_score, malware_region, malware_sector, malware_resilience, malware, phishing_region, phishing_sector, phishing_resilience, phishing, ddos_region, ddos_sector, ddos_resilience, ddos, insights_pos, insights_neg, malware_att_succ, phishing_att_succ, ddos_att_succ

# ===========================================================================================================================
# =================================================EXTRA FUNCTIONS===========================================================
# ===========================================================================================================================

# return in that sector, which is the percentage of each type of attack
def region_percentage(database):
    chart, medias, count = [0,0,0], [0,0,0], [0,0,0]
    media_geral = 0

    for data in database:
        media_geral += float(data.p_a_given_b)
        #print(data.prob_a_priori)
        if data.prob_a_priori == 'malware':
            medias[0] += float(data.p_a_given_b)
            count[0] += 1
        elif data.prob_a_priori == 'phishing':
            medias[1] += float(data.p_a_given_b)
            count[1] += 1
        elif data.prob_a_priori == 'DDoS':
            medias[2] += float(data.p_a_given_b)
            count[2] += 1

    media_geral = media_geral / len(database) if len(database) else 0

    if media_geral:
        chart = [round(medias[0]/count[0] if count[0] else media_geral,2),
                round(medias[1]/count[1] if count[1] else media_geral,2),
                round(medias[2]/count[2] if count[2] else media_geral,2)]
    else:
        chart = [round(medias[0]/count[0] if count[0] else 0,2),
                round(medias[1]/count[1] if count[1] else 0,2),
                round(medias[2]/count[2] if count[2] else 0,2)]

    return chart

def final_table_technical_dimension(company_profile, attack_history):
    company_status = []

    if company_profile.updated_inventory == True:
        company_status.append(True)
    else:
        company_status.append(False)
    
    if company_profile.backup_maintenance == 'On Site' or company_profile.backup_maintenance == 'Offsite' or company_profile.backup_maintenance == 'Regular' or company_profile.backup_maintenance == 'Critical':
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.risk_prioritization == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.authentication_factors > 1:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.cloud_solution_type == 'lan' or company_profile.cloud_solution_type == 'wan':
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.it_system_monitoring == True:
        company_status.append(True)
    else:
        company_status.append(False)
    
    if company_profile.periodic_system_updates == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.data_encryption_in_storage == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.data_encryption_in_transit == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.vpn_for_remote_access == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.cybersecurity_awareness_and_training == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.documented_response_plan == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.response_plan_update == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.operational_recovery_capacity == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.credentials_maintenance == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.vulnerability_identification == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.network_systems_traffic_monitoring == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.threat_identification_process == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.it_records_presence == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.antivirus == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.firewall == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.intrusion_detection_system == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.endpoint_detection_and_response == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if company_profile.it_security_team == True:
        company_status.append(True)
    else:
        company_status.append(False)

    if len(attack_history) > 0:
        company_status.append(True)
    else:
        company_status.append(False)

    return company_status
