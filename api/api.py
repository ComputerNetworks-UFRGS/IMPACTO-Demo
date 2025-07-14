
from flask import Flask, jsonify, request
from statistics import mean
import math
import datetime
app = Flask(__name__)

def decaimento(ano, cons):
    return math.exp(-cons * (datetime.datetime.now().year - ano))

@app.route('/', methods=['GET'])
def working_api():
    return jsonify(True)

@app.route('/poisson/', methods=['POST'])
def media_poisson():
    [prob] = request.get_json()
    return jsonify(-math.log(1-prob))

@app.route('/media/', methods=['POST'])
def media_dados():
    data = request.get_json()
    cons_decaim = 0 # (entre 0 e 1)
    sum_media = 0
    sum_pesos = 0
    for valor, ano in data:
        dec = decaimento(ano, cons_decaim)
        sum_media += valor * dec
        sum_pesos += dec
    if sum_pesos == 0:
        return jsonify(0)
    return jsonify(sum_media/sum_pesos)

@app.route('/regiao_setor/', methods=['POST'])
def regiao_setor():
    data = request.get_json()
    media = data[0] * data[2] + data[1] * (1 - data[2])
    return jsonify(media)
    
@app.route('/gordon_loeb_optimal/', methods=['POST'])
def gordon_loeb_optimal():
    [prob, value, type, seg, alpha] = request.get_json()
    match type:
        case 1:
            z = value*(math.sqrt(prob*alpha) - alpha)
            ebis = (prob-prob/(1+z/(value*alpha)))*value
        case 2:
            z = value*(math.sqrt(prob*alpha) - alpha/2)
            ebis = (prob-prob/(0.5+z/(value*alpha)))*value
        case _:
            z = 0
            ebis = 0
    if ebis < 0:
        ebis = 0
    enbis = ebis - z

    ###calcular intervalo invariável
    seg_enbis = enbis*(1-seg)
    a = 1/(value*alpha)
    b = (0.5 - prob/alpha + seg_enbis/(value*alpha))
    c = (prob*value + seg_enbis)/2
    delta = b**2 - 4*a*c
    if delta < 0:
        delta = 0
    seg_min = (-b - delta**(1/2)) / (2*a)
    seg_max = (-b + delta**(1/2)) / (2*a)
    b = 0.5 - prob / alpha
    c = prob * value / 2
    delta = b**2 - 4*a*c
    if delta < 0:
        delta = 0
    zero_graph = (-b - delta**(1/2)) / (2*a)
    ###calcular intervalo invariável
    maximo = value*prob
    efetividade = enbis/maximo
    retorno = {
        "ebis": ebis,
        "enbis": enbis,
        "z": z,
        "max": maximo,
        "efic": efetividade,
        "seg_min": seg_min,
        "seg_max": seg_max,
        "seg_enbis": seg_enbis,
        "seg": 100*seg,
        "zero_graph": zero_graph
    }
    return jsonify(retorno)

@app.route('/enbis/', methods=['POST'])
def enbis_func():
    [prob, value, alpha] = request.get_json()

    f = f"({prob} - {prob} / (0.5 + x / ({value} * {alpha}))) * {value}"
    return jsonify(f)

@app.route('/gordon_loeb/', methods=['POST'])
def gordon_loeb():
    [prob, value, z, type, alpha] = request.get_json()
    match type:
        case 1:
            ebis = (prob-prob/(1+z/(value*alpha)))*value
        case 2:
            ebis = (prob-prob/(0.5+z/(value*alpha)))*value
        case _:
            ebis = 0
    if ebis < 0:
        ebis = 0
    enbis = ebis - z
    maximo = value*prob
    efetividade = enbis/maximo
    retorno = {
        "ebis": ebis,
        "enbis": enbis,
        "max": maximo,
        "efic": efetividade,
        "z": z
    }
    return jsonify(retorno)
@app.route('/impact/', methods=['POST'])
def impacto():
    [direct, indirect] = request.get_json()
    pesoD = 0.35
    pesoI = 0.65
    if direct == "Alto":
        d = 0.75
    elif direct == "Medio":
        d = 0.5
    elif direct == "Baixo":
        d = 0.25
        
    if indirect == "Alto":
        i = 0.75
    elif indirect == "Medio":
        i = 0.5
    elif indirect == "Baixo":
        i = 0.25
    impacto = pesoD * d + pesoI * i
    return jsonify(impacto)

@app.route('/impact_setting/', methods=['POST'])
def impact_setting():
    [item, attack] = request.get_json()
    dir = "Medio"
    ind = "Medio"
    if item == "server":
        if attack.lower() == "malware":
            dir = "Alto"
        elif attack.lower() == "ddos":
            ind = "Alto"

    elif item == "database":
        if attack.lower() == "malware":
            dir = "Alto"
            ind = "Alto"
        elif attack.lower() == "phishing":
            ind = "Alto"

    elif item == "website":
        if attack.lower() == "malware":
            dir = "Alto"
            ind = "Alto"
        elif attack.lower() == "phishing":
            ind = "Alto"
        elif attack.lower() == "ddos":
            dir = "Alto"
            ind = "Alto"
    print(attack, item, dir, ind)
    return jsonify([dir, ind])
    
if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)