from django.db.models import Avg, Count
from .models import CyberSecurityData
from .continents import CONTINENTS
from decimal import Decimal
from django.utils.translation import gettext as _

ATTACK_TYPES_TRANSLATION = {
    'ddos': _('DDoS'),
    'malware': _('Malware'),
    'phishing': _('Phishing'),
    'ransomware': _('Ransomware')
}

def calcular_media_probabilidades_por_ataque_e_continente():
    resultados = {}

    tipos_de_ataque = ['ddos', 'malware', 'phishing', 'ransomware']

    for continente, paises in CONTINENTS.items():
        resultados[continente] = {
            'attack_types': [],
            'risks': [],
            'counts': []
        }

        paises_e_continente = paises + [continente]

        for ataque in tipos_de_ataque:
            agregados = CyberSecurityData.objects.filter(
                prob_marginal__in=paises_e_continente,
                prob_a_priori=ataque
            ).aggregate(
                media_p_a_given_b=Avg('p_a_given_b'),
                count_p_a_given_b=Count('p_a_given_b')
            )

            resultados[continente]['attack_types'].append(str(ATTACK_TYPES_TRANSLATION[ataque]))
            resultados[continente]['risks'].append(agregados['media_p_a_given_b'])
            resultados[continente]['counts'].append(agregados['count_p_a_given_b'])

    return resultados

def calcular_media_probabilidades_por_ataque_e_setor():
    resultados = {}

    tipos_de_ataque = ['ddos', 'malware', 'phishing', 'ransomware']
    
    setores = [
        'Healthcare',
        'Government',
        'Retail',
        'Finance',
        'Education',
        'Entertainment',
        'Technology',
        'Others'
    ]

    for setor in setores:
        resultados[setor] = {
            'attack_types': [],
            'risks': [],
            'counts': []
        }

        for ataque in tipos_de_ataque:
            agregados = CyberSecurityData.objects.filter(
                prob_marginal=setor,
                prob_a_priori=ataque
            ).aggregate(
                media_p_a_given_b=Avg('p_a_given_b'),
                count_p_a_given_b=Count('p_a_given_b')
            )

            resultados[setor]['attack_types'].append(str(ATTACK_TYPES_TRANSLATION[ataque]))
            resultados[setor]['risks'].append(agregados['media_p_a_given_b'])
            resultados[setor]['counts'].append(agregados['count_p_a_given_b'])

    return resultados