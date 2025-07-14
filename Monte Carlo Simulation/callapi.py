import requests

url_gordon_loeb = 'http://localhost:5000/gordon_loeb_optimal/' #parametros: [probabilidade, valor, tipo (1 ou 2)] -> retorna EBIS, ENBIS e valor ótimo de investimento (z)
url_regiao_setor = 'http://localhost:5000/regiao_setor/' #parametros: [prob_região, prob_setor, peso_região] -> retorna união das probabilidades
url_media = 'http://localhost:5000/media/' #parametros: Lista [[dado, ano], [dado, ano], ...] -> retorna média dos dados
url_poisson = 'http://localhost:5000/poisson/' #parametros: probabilidade -> retorna média de ataques esperada no ano

valor_segmento_phishing = 720000
valor_segmento_ddos = 470000
valor_segmento_malware = 1040000

tipo = 2

emea_phishing = [[0.30, 2024], [0.16, 2024]]
emea_ddos = [[0.17, 2024], [0.105, 2022], [0.23, 2024]]
emea_malware = [[0.50, 2024], [0.178, 2024]]

healthcare_phishing = [[0.507, 2022], [0.2, 2024], [0.26, 2023]]
healthcare_ddos = [[0.105, 2022], [0.01, 2022], [0.032, 2024]]
healthcare_malware = [[0.29, 2024], [0.162, 2024]]

peso_regiao_setor = 0.66

# Fazendo a requisição POST para a API Flask
print("Fazendo requisição para a API...")

emea_phishing_media = requests.post(url_media, json=emea_phishing).json()
emea_ddos_media = requests.post(url_media, json=emea_ddos).json()
emea_malware_media = requests.post(url_media, json=emea_malware).json()

print("Probabilidade phishing Emea: ", emea_phishing_media)
print("Probabilidade ddos Emea: ", emea_ddos_media)
print("Probabilidade malware Emea: ", emea_malware_media)

healthcare_phishing_media = requests.post(url_media, json=healthcare_phishing).json()
healthcare_ddos_media = requests.post(url_media, json=healthcare_ddos).json()
healthcare_malware_media = requests.post(url_media, json=healthcare_malware).json()

print("Probabilidade phishing Healthcare: ", healthcare_phishing_media)
print("Probabilidade ddos Healthcare: ", healthcare_ddos_media)
print("Probabilidade malware Healthcare: ", healthcare_malware_media)

regiao_setor_phishing = requests.post(url_regiao_setor, json=[emea_phishing_media, healthcare_phishing_media, peso_regiao_setor]).json()
regiao_setor_ddos = requests.post(url_regiao_setor, json=[emea_ddos_media, healthcare_ddos_media, peso_regiao_setor]).json()
regiao_setor_malware = requests.post(url_regiao_setor, json=[emea_malware_media, healthcare_malware_media, peso_regiao_setor]).json()

print("Probabilidade phishing Healthcare Emea: ", regiao_setor_phishing)
print("Probabilidade ddos Healthcare Emea: ", regiao_setor_ddos)
print("Probabilidade malware Healthcare Emea: ", regiao_setor_malware)

media_phishing = requests.post(url_poisson, json=[regiao_setor_phishing]).json()
media_ddos = requests.post(url_poisson, json=[regiao_setor_ddos]).json()
media_malware = requests.post(url_poisson, json=[regiao_setor_malware]).json()

print("Média de ataques esperados no ano phishing Healthcare Emea: ", media_phishing)
print("Média de ataques esperados no ano ddos Healthcare Emea: ", media_ddos)
print("Média de ataques esperados no ano malware Healthcare Emea: ", media_malware)

gordon_loeb_phishing = requests.post(url_gordon_loeb, json=[regiao_setor_phishing, valor_segmento_phishing, tipo]).json()
gordon_loeb_ddos = requests.post(url_gordon_loeb, json=[regiao_setor_ddos, valor_segmento_ddos, tipo]).json()
gordon_loeb_malware = requests.post(url_gordon_loeb, json=[regiao_setor_malware, valor_segmento_malware, tipo]).json()

print("\n\nGordon-loeb phishing Healthcare Emea:\nEBIS: ", gordon_loeb_phishing["ebis"], "\nENBIS: ", gordon_loeb_phishing["enbis"], "\nInvestimento ótimo: ", gordon_loeb_phishing["z"], "\nPrejuizo atualmente por ano: ", gordon_loeb_phishing["max"], "\nPrejuizo atualmente por ataque: ", gordon_loeb_phishing["max"] / media_phishing, "\nPrejuizo após investimento por ano (contando com custo de investimento): ", gordon_loeb_phishing["max"] - gordon_loeb_phishing["enbis"], "\nEficiência: ", gordon_loeb_phishing["efic"])
print("\n\nGordon-loeb ddos Healthcare Emea:\nEBIS: ", gordon_loeb_ddos["ebis"], "\nENBIS: ", gordon_loeb_ddos["enbis"], "\nInvestimento ótimo: ", gordon_loeb_ddos["z"], "\nPrejuizo atualmente por ano: ", gordon_loeb_ddos["max"], "\nPrejuizo atualmente por ataque: ", gordon_loeb_ddos["max"] / media_ddos, "\nPrejuizo após investimento por ano (contando com custo de investimento): ", gordon_loeb_ddos["max"] - gordon_loeb_ddos["enbis"], "\nEficiência: ", gordon_loeb_ddos["efic"])
print("\n\nGordon-loeb malware Healthcare Emea:\nEBIS: ", gordon_loeb_malware["ebis"], "\nENBIS: ", gordon_loeb_malware["enbis"], "\nInvestimento ótimo: ", gordon_loeb_malware["z"], "\nPrejuizo atualmente por ano: ", gordon_loeb_malware["max"], "\nPrejuizo atualmente por ataque: ", gordon_loeb_malware["max"] / media_malware, "\nPrejuizo após investimento por ano (contando com custo de investimento): ", gordon_loeb_malware["max"] - gordon_loeb_malware["enbis"], "\nEficiência: ", gordon_loeb_malware["efic"])
