from flask import Flask, jsonify, request
from statistics import mean
import math
import datetime
#from callapi import dados
app = Flask(__name__)

def decaimento(ano, cons):
    return math.exp(-cons * (datetime.datetime.now().year - ano))


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
    print("[ebis, enbis, z, type]")
    [prob, value, type] = request.get_json()
    alpha = 0.001
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
    enbis = ebis - z
    maximo = value*prob
    efetividade = enbis/maximo
    retorno = {
        "ebis": ebis,
        "enbis": enbis,
        "z": z,
        "max": maximo,
        "efic": efetividade,
    }
    return jsonify(retorno)
    
if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)
#print(prob_dados(dados))
    
