from collections import Counter
import sys
import csv
import os
import numpy as np

# ===========================================================================================================================
# =====================================================CONSTANTS=============================================================
# ===========================================================================================================================

# -> variables
malware_flag, phishing_flag, ddos_flag = 1,1,1
valor_medio = 6

# -> sectors
SECTORS = ['Healthcare','Government','Retail','Finance','Education','Entertainment','Technology','Others']
SECTORS_WEIGHTS = [1.5,1.25,1,0.75,0.5]

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
COUNTRY_WEIGHTS = [1.5,1.25,1,0.75,0.5]
CONTINENT_WEIGHTS = [1.5,1.25,1,0.75,0.5]

# -> status company
MALWARE_YES = [1.2,1.1,1.2,1,1,1.7,1.7,1.2,1.2,1.1,1.5,1.2,1.2,1.7,1.2,1.7,1.7,1.7,1.1,1.7,1.7,1.7,1.7,1.7,1]
MALWARE_NO = [0.9,0.9,0.9,1,1,0.4,0.4,0.9,0.9,0.9,0.6,0.9,0.9,0.4,0.9,0.4,0.4,0.4,0.9,0.4,0.4,0.4,0.4,0.4,1]
PHISHING_YES = [1.1,1.1,1.2,1,1,1.2,1.1,1.1,1.1,1.1,1.7,1.2,1.2,1.1,1.7,1.2,1.1,1.2,1.1,1.1,1.2,1.2,1.2,1.7,1]
PHISHING_NO = [0.9,0.6,0.9,1,1,0.9,0.9,0.9,0.9,0.9,0.6,0.9,0.9,0.9,0.6,0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.6,1]
DDOS_YES = [1.1,1.1,1.2,1,1,1.7,1.2,1.1,1.1,1.1,1.1,1.7,1.7,1.7,1.1,1.7,1.7,1.7,1.1,1.1,1.7,1.7,1.2,1.7,1]
DDOS_NO = [0.9,0.8,0.8,1,1,0.5,0.8,0.9,0.9,0.9,0.9,0.5,0.5,0.5,0.9,0.5,0.5,0.5,0.9,0.9,0.5,0.5,0.8,0.5,1]

MALWARE_AUTH_FACT = [0.5,0.75,1.2,1.5]
MALWARE_ATT_HIST = [1.5,1.2,1,0.7]
MALWARE_CLOUD = [1,0.8,1.5,0.6]
MALWARE_BACKUP = [1.2,1.25,1.5,1.5]
PHISHING_AUTH_FACT = [0.5,0.75,1.2,1.5]
PHISHING_ATT_HIST = [1.5,1.2,1,0.7]
PHISHING_CLOUD = [0.9,0.7,1.5,0.5]
PHISHING_BACKUP = [1.1,1.2,1.3,1.4]
DDOS_AUTH_FACT = [1,1,1,1]
DDOS_ATT_HIST = [1.5,1.2,1,0.7]
DDOS_CLOUD = [0.8,1,1.5,0.5]
DDOS_BACKUP = [1,1.1,1,1.1]

weight_g1, weight_g2, weight_g3 = 0.56,0.36,0.08

# ===========================================================================================================================
# ==============================================COMPLEMENTARY FUNCTIONS======================================================
# ===========================================================================================================================

def find_sector(company_profile):
    sector = company_profile[0][2]
    print(sector)
    return sector

def find_country(company_profile):
    country = company_profile[0][1]
    print(country)
    return country

# ===========================================================================================================================
# =================================================SECTOR EVALUATOR==========================================================
# ===========================================================================================================================

def sector_evaluator(typeattack,sector_company,database):
    sector_points = 1
    data_sector, data_perc = [],[]
    sum_perc, media_perc, sector_perc, sector_count = 0,0,0,0

    for data in database:
        if data[0] == typeattack and data[1] in SECTORS and data[2] != '-':
            data_sector.append(data)
            data_perc.append(float(data[2]))

    if len(data_sector) <= 1:
        print('Banco de Dados insuficiente para uma análise por setores.')
    else:
        for var in data_sector:
            sum_perc += float(var[2])
        media_perc = sum_perc / len(data_sector)
        stand_deviation = round(np.std(data_perc),2)

        # calculating the chance of the attack
        for data in data_sector:
            sector_perc += float(data[2])
            sector_count += 1
        sector_perc = sector_perc/sector_count if sector_count!= 0 else 0

        data_perc.sort()
        if sector_perc <= float(data_sector[0][2]):
            sector_points = SECTORS_WEIGHTS[0]
        elif sector_perc < media_perc-stand_deviation:
            sector_points = SECTORS_WEIGHTS[1]
        elif sector_perc >= media_perc-stand_deviation and sector_perc <= media_perc+stand_deviation:
            sector_points = SECTORS_WEIGHTS[2]
        elif sector_perc > media_perc+stand_deviation:
            sector_points = SECTORS_WEIGHTS[3]
        elif sector_perc >= float(data_sector[len(data_sector)-1][2]):
            sector_points = SECTORS_WEIGHTS[4]

    print("\nSector Points:\t\t", sector_points)
    return sector_points

# ===========================================================================================================================
# =================================================REGION EVALUATOR==========================================================
# ===========================================================================================================================

# used to analyze the region of the company in comparison on the world
def region_evaluator(typeattack,country_company,database, continent_dict):
    attack_data_country,attack_data_continent = [],[]
    aux_country, aux_continent = [],[]
    country_points,continent_points = 1,1
    country_count,continent_count = 0,0
    country_perc,continent_perc = 0,0
    sum_perc_country, sum_perc_continent = 0,0

    continent_company = continent_dict.get(country_company,country_company)
    
    # gathering the specific data
    for data in database:
        #print(data)
        if data[0] == typeattack and data[1] in COUNTRIES and data[2] != '-':
            attack_data_country.append(data)
            aux_country.append(float(data[2]))
        if data[0] == typeattack and data[1] in CONTINENT and data[2] != '-':
            attack_data_continent.append(data)
            aux_continent.append(float(data[2]))

    #print(len(attack_data_country))
    #print(len(attack_data_continent))

    # analysis per country
    if len(attack_data_country) <= 1:
        print('Banco de Dados insuficiente para uma análise por países.')
    else:
        for var in attack_data_country:
            sum_perc_country += float(var[2])
        media_perc_country = sum_perc_country / len(attack_data_country)
        stand_deviation_country = round(np.std(aux_country),2)

        # calculating the chance of the attack
        for data in attack_data_country:
            if country_company == data[1]:
                country_perc += float(data[2])
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

        #print("Country Points:\t\t", country_points)
            
    # analysis per continent
    if len(attack_data_continent) <= 1:
        print('Banco de Dados insuficiente para uma análise por continentes.')
    else:
        for var in attack_data_continent:
            sum_perc_continent += float(var[2])
        media_perc_continent = sum_perc_continent / len(attack_data_continent)
        stand_deviation_continent = round(np.std(aux_continent),2)

        # calculating the chance of the attack
        for data in attack_data_continent:
            if continent_company == data[1]:
                continent_perc += float(data[2])
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

        #print("Continent Points:\t", continent_points)
    
    # wait = input("Pausa...")
    # final calculation of the region evaluator
    region_points = (country_points + continent_points)/2
    print('Region Points:\t\t', region_points)
    return region_points

# ===========================================================================================================================
# =================================================COMPANY EVALUATOR=========================================================
# ===========================================================================================================================

# used to verify how much prepared is the company against cyberattacks
def company_evaluator(typeattack,company_profile):
    company_points = 1
    item_g1 = [0,6,7,10,11,12,14,19,20,21,22,23]
    item_g2 = [2,5,8,13,15,16,17,18]
    item_g3 = [9]
    sum_g1, sum_g2, sum_g3 = 0,0,0

    prep_company = company_profile[2]

    # gathering the attack histories
    att_malware, att_phishing, att_ddos = 0,0,0
    for key, value in prep_company[-1].items():
        if isinstance(value, list):
            for att in value:
                if att == 'malware' or att == 'ransomware':
                    att_malware += 1
                elif att == 'phishing':
                    att_phishing += 1
                elif att == 'DDoS':
                    att_ddos += 1
        else:
            if value == 'malware' or value == 'ransomware':
                att_malware += 1
            elif value == 'phishing':
                att_phishing += 1
            elif value == 'DDoS':
                att_ddos += 1

    # gathering info of cloud solutions
    cloud_items = []
    if isinstance(prep_company[4], list):
        for i in prep_company[4]:
            if i == 'Private':
                cloud_items.append(0)
            elif i == 'Public':
                cloud_items.append(1)
            elif i == 'Hybrid':
                cloud_items.append(2)
            elif i == 'None':
                cloud_items.append(3)
    else:
        if prep_company[4] == 'Private':
            cloud_items.append(0)
        elif prep_company[4] == 'Public':
            cloud_items.append(1)
        elif prep_company[4] == 'Hybrid':
            cloud_items.append(2)
        elif prep_company[4] == 'None':
            cloud_items.append(3)

    if typeattack == 'malware':
        # GROUP - SECURITY PREVENTING
        for i in range(len(item_g1)):
            if prep_company[item_g1[i]] == '1':
                sum_g1 = sum_g1 + MALWARE_YES[item_g1[i]]
            else:
                sum_g1 = sum_g1 + MALWARE_NO[item_g1[i]]
        # backup
        if prep_company[1] == 'On Site':
            sum_g1 = sum_g1 + MALWARE_BACKUP[0]
        elif prep_company[1] == 'Offsite':
            sum_g1 = sum_g1 + MALWARE_BACKUP[1]
        elif prep_company[1] == 'Regular':
            sum_g1 = sum_g1 + MALWARE_BACKUP[2]
        elif prep_company[1] == 'Critical':
            sum_g1 = sum_g1 + MALWARE_BACKUP[3]
        # auth factor
        if int(prep_company[3]) == 0:
            sum_g1 = sum_g1 + MALWARE_AUTH_FACT[0]
        elif int(prep_company[3]) == 1:
            sum_g1 = sum_g1 + MALWARE_AUTH_FACT[1]
        elif int(prep_company[3]) == 2:
            sum_g1 = sum_g1 + MALWARE_AUTH_FACT[2]
        if int(prep_company[3]) > 2:
            sum_g1 = sum_g1 + MALWARE_AUTH_FACT[3]

        # GROUP - SECURITY MONITORING
        for i in range(len(item_g2)):
            if prep_company[item_g2[i]] == '1':
                sum_g2 = sum_g2 + MALWARE_YES[item_g2[i]]
            else:
                sum_g2 = sum_g2 + MALWARE_NO[item_g2[i]]
        # att history
        if att_malware == 0:
            sum_g1 = sum_g1 + MALWARE_ATT_HIST[0]
        elif att_malware == 1:
            sum_g1 = sum_g1 + MALWARE_ATT_HIST[1]
        elif att_malware == 2:
            sum_g1 = sum_g1 + MALWARE_ATT_HIST[2]
        if att_malware > 2:
            sum_g1 = sum_g1 + MALWARE_ATT_HIST[3]

        # GROUP - ORGANIZATION SETUP
        for i in range(len(item_g3)):
            if prep_company[item_g3[i]] == '1':
                sum_g3 = sum_g3 + MALWARE_YES[item_g3[i]]
            else:
                sum_g3 = sum_g3 + MALWARE_NO[item_g3[i]]
        # cloud
        for cld in cloud_items:
            sum_g3 += MALWARE_CLOUD[cld]

        # FINAL DEFINITION
        sum_g1 = sum_g1 / len(item_g1)
        sum_g2 = sum_g2 / len(item_g2)
        sum_g3 = sum_g3 / len(item_g3)
        company_points = weight_g1*sum_g1 + weight_g2*sum_g2 + weight_g3*sum_g3
    elif typeattack == 'phishing':
        # GROUP - SECURITY PREVENTING
        for i in range(len(item_g1)):
            if prep_company[item_g1[i]] == '1':
                sum_g1 = sum_g1 + PHISHING_YES[item_g1[i]]
            else:
                sum_g1 = sum_g1 + PHISHING_NO[item_g1[i]]
        # backup
        if prep_company[1] == 'On Site':
            sum_g1 = sum_g1 + PHISHING_BACKUP[0]
        elif prep_company[1] == 'Offsite':
            sum_g1 = sum_g1 + PHISHING_BACKUP[1]
        elif prep_company[1] == 'Regular':
            sum_g1 = sum_g1 + PHISHING_BACKUP[2]
        elif prep_company[1] == 'Critical':
            sum_g1 = sum_g1 + PHISHING_BACKUP[3]
        # auth factor
        if int(prep_company[3]) == 0:
            sum_g1 = sum_g1 + PHISHING_AUTH_FACT[0]
        elif int(prep_company[3]) == 1:
            sum_g1 = sum_g1 + PHISHING_AUTH_FACT[1]
        elif int(prep_company[3]) == 2:
            sum_g1 = sum_g1 + PHISHING_AUTH_FACT[2]
        if int(prep_company[3]) > 2:
            sum_g1 = sum_g1 + PHISHING_AUTH_FACT[3]

        # GROUP - SECURITY MONITORING
        for i in range(len(item_g2)):
            if prep_company[item_g2[i]] == '1':
                sum_g2 = sum_g2 + PHISHING_YES[item_g2[i]]
            else:
                sum_g2 = sum_g2 + PHISHING_NO[item_g2[i]]
        # att history
        if att_phishing == 0:
            sum_g1 = sum_g1 + PHISHING_ATT_HIST[0]
        elif att_phishing == 1:
            sum_g1 = sum_g1 + PHISHING_ATT_HIST[1]
        elif att_phishing == 2:
            sum_g1 = sum_g1 + PHISHING_ATT_HIST[2]
        if att_phishing > 2:
            sum_g1 = sum_g1 + PHISHING_ATT_HIST[3]

        # GROUP - ORGANIZATION SETUP
        for i in range(len(item_g3)):
            if prep_company[item_g3[i]] == '1':
                sum_g3 = sum_g3 + PHISHING_YES[item_g3[i]]
            else:
                sum_g3 = sum_g3 + PHISHING_NO[item_g3[i]]
        # cloud
        for cld in cloud_items:
            sum_g3 += PHISHING_CLOUD[cld]

        # FINAL DEFINITION
        sum_g1 = sum_g1 / len(item_g1)
        sum_g2 = sum_g2 / len(item_g2)
        sum_g3 = sum_g3 / len(item_g3)
        company_points = weight_g1*sum_g1 + weight_g2*sum_g2 + weight_g3*sum_g3
    elif typeattack == 'DDoS':
        # GROUP - SECURITY PREVENTING
        for i in range(len(item_g1)):
            if prep_company[item_g1[i]] == '1':
                sum_g1 = sum_g1 + DDOS_YES[item_g1[i]]
            else:
                sum_g1 = sum_g1 + DDOS_NO[item_g1[i]]
        # backup
        if prep_company[1] == 'On Site':
            sum_g1 = sum_g1 + DDOS_BACKUP[0]
        elif prep_company[1] == 'Offsite':
            sum_g1 = sum_g1 + DDOS_BACKUP[1]
        elif prep_company[1] == 'Regular':
            sum_g1 = sum_g1 + DDOS_BACKUP[2]
        elif prep_company[1] == 'Critical':
            sum_g1 = sum_g1 + DDOS_BACKUP[3]
        # auth factor
        if int(prep_company[3]) == 0:
            sum_g1 = sum_g1 + DDOS_AUTH_FACT[0]
        elif int(prep_company[3]) == 1:
            sum_g1 = sum_g1 + DDOS_AUTH_FACT[1]
        elif int(prep_company[3]) == 2:
            sum_g1 = sum_g1 + DDOS_AUTH_FACT[2]
        if int(prep_company[3]) > 2:
            sum_g1 = sum_g1 + DDOS_AUTH_FACT[3]

        # GROUP - SECURITY MONITORING
        for i in range(len(item_g2)):
            if prep_company[item_g2[i]] == '1':
                sum_g2 = sum_g2 + DDOS_YES[item_g2[i]]
            else:
                sum_g2 = sum_g2 + DDOS_NO[item_g2[i]]
        # att history
        if att_ddos == 0:
            sum_g1 = sum_g1 + DDOS_ATT_HIST[0]
        elif att_ddos == 1:
            sum_g1 = sum_g1 + DDOS_ATT_HIST[1]
        elif att_ddos == 2:
            sum_g1 = sum_g1 + DDOS_ATT_HIST[2]
        if att_ddos > 2:
            sum_g1 = sum_g1 + DDOS_ATT_HIST[3]

        # GROUP - ORGANIZATION SETUP
        for i in range(len(item_g3)):
            if prep_company[item_g3[i]] == '1':
                sum_g3 = sum_g3 + DDOS_YES[item_g3[i]]
            else:
                sum_g3 = sum_g3 + DDOS_NO[item_g3[i]]
        # cloud
        for cld in cloud_items:
            sum_g3 += DDOS_CLOUD[cld]

        # FINAL DEFINITION
        sum_g1 = sum_g1 / len(item_g1)
        sum_g2 = sum_g2 / len(item_g2)
        sum_g3 = sum_g3 / len(item_g3)
        company_points = weight_g1*sum_g1 + weight_g2*sum_g2 + weight_g3*sum_g3
    else:
        print('Type of attack not identified.')

    company_points = round(company_points,2)    
    print("Company Preparation:\t", company_points)
    return company_points

# ===========================================================================================================================
# =======================================================MAIN================================================================
# ===========================================================================================================================
# receive args and calculate the company's final score
def main():
    company_profile = []
    if os.path.exists(sys.argv[1]):
        arquivo_entrada = sys.argv[1]
    else:
        print('O arquivo \''+sys.argv[1]+'\' não existe no diretório')
        return

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

    # working with the company profile
    with open(arquivo_entrada, 'r') as file:
        for line in file:
            current_list = eval(line.strip())
            company_profile.append(current_list)

    # working with the database
    with open("gt-impacto_dadosnt.csv", "r") as csvfile:
        database = list(csv.reader(csvfile))
    database = database[1:]

    # finding infos
    sector_company = find_sector(company_profile)
    country_company = find_country(company_profile)

    # evaluation
    print('\nMALWARE')
    malware = valor_medio * sector_evaluator('malware',sector_company,database) * region_evaluator('malware',country_company,database,continent_dict) * (1/company_evaluator('malware',company_profile))
    print("\nPHISHING")
    phishing = valor_medio * sector_evaluator('phishing',sector_company,database) * region_evaluator('phishing',country_company,database,continent_dict) * (1/company_evaluator('phishing',company_profile))
    print('\nDDoS')
    ddos = valor_medio * sector_evaluator('DDoS',sector_company,database) * region_evaluator('DDoS',country_company,database,continent_dict) * (1/company_evaluator('DDoS',company_profile))
    formula = (malware*malware_flag + phishing*phishing_flag + ddos*ddos_flag)/(malware_flag+phishing_flag+ddos_flag)

    # giving feedback
    final_score = min(formula,10)
    final_score = round(final_score,2)
    print("\nCompany's final score: " + str(final_score))
    if final_score >= 8:
        print("Situation of the Company: Critical")
    elif final_score >= 6:
        print("Situation of the Company: Dangerous")
    elif final_score >= 3:
        print("Situation of the Company: Caution")
    elif final_score >= 1:
        print("Situation of the Company: Normal")
    else:
        print("Situation of the Company: Healthy")
    pass

# ===========================================================================================================================
# ===========================================================================================================================
# ===========================================================================================================================
if __name__ == '__main__':
    main()