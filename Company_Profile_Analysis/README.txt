% FIELDS AND ITS TYPES RECEIVED AS INPUT (LIST OF LISTS):

-> BUSINESS DIMENSION
Name	STRING
Headquarters Country	STRING
Industry Type	SELECTION
Employee Count	INTEGER
Companies Localization	SELECTION
Size	SELECTION
Remote Work Rate (%)	FLOAT
Global Presence	BOOLEAN

-> ECONOMIC DIMENSION
Annual Revenue	HISTORY
Cybersecurity Spending	HISTORY
Company Goods	LIST

-> TECHNICAL DIMENSION
Updated Inventory	BOOLEAN
Backup Maintenance	BOOLEAN
Risk Priorization	BOOLEAN
Authentication Factors	INTEGER
Cloud Solution Type	SELECTION
IT System Monitoring	BOOLEAN
Periodic System Updates	BOOLEAN
Data Encryption in Storage	BOOLEAN
Data Encryption in Transit	BOOLEAN
VPN for Remote Access	BOOLEAN
Cybersecurity Awareness and Training	BOOLEAN
Documented Response Plan	BOOLEAN
Response Plan Update	BOOLEAN
Operational Recovery Capacity	BOOLEAN
Credentials Maintenance	BOOLEAN
Vulnerability Identification	BOOLEAN
Network Systems Traffic Monitoring	BOOLEAN
Threat Identification Process	BOOLEAN
IT Records Presence	BOOLEAN
Antivirus	BOOLEAN
Firewall	BOOLEAN
Intrusion Detection System	BOOLEAN
Endpoint Detection and Response (EDR)	BOOLEAN
IT security team	BOOLEAN
Attack History	HISTORY

% EXAMPLE OF AN INPUT (LIST OF LISTS):
['XYZ','Brazil','Healthcare','500',['Europe','LATAM'],'Medium','12','1']
[{2023:1520000,2022:4200500},{2023:200500,2022:500000},{}]
['1','Critical','1','2','Private','1','0','0','1','0','0','1','0','0','1','0','0','1','0','0','1','0','0','1',{2023: ['malware','DDoS']}]

% SCORING BY IMPORTANCE
####### = 1,5
####### = 1,25
####### = 1
####### = 0,75
####### = 0,5

-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x
-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x
-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x
% LIST OF EVERY SCOPE TO ANALYZE

SECTORS = ['Healthcare','Government','Retail','Finance','Education','Entertainment','Technology','Others']
COUNTRIES = ['United States','Brazil','Germany','France','Italy','United Kingdom','China','Japan','Australia','Canada','India','Russia','Ukraine','UAE','Others']
REGIONS = ['Europe','South America','North America','Africa','Asia','Oceania','EMEA','LATAM','APAC','NA']

Europe = [Germany,France,Italy,United Kingdom,Ukraine]
Middle East = [UAE]
Africa = [South Africa]
Asia = [China,Japan,India,Russia]
Oceania = [Australia]
South America = [Brazil]
North America = [Canada,United States]

-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x
% COMPARISON REGION
WORST = 1.5
WORSE = 1.25
MEDIUM = 1
BETTER = 0.75
BEST = 0.5

-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x
% COMPARISON SECTOR
WORST = 1.5
WORSE = 1.25
MEDIUM = 1
BETTER = 0.75
BEST = 0.5

-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x-x-x-x-x--x-x-x-x
% RANGE OF FINAL SCORE
Critical (>=8)
Dangerous (>=6)
Caution (>=4)
Normal (>=1)
Healthy (>=0)
