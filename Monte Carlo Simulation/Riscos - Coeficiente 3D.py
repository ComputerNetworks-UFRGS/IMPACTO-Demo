import math
import numpy as np
import matplotlib.pyplot as plt
import Empresa as E

def melhor_reta(x, y, p):
    n = len(x)
    
    # Calcula as médias de x e y
    x_mean = sum(x[i] * p[i] for i in range(n))
    y_mean = sum(y[i] * p[i] for i in range(n))
    
    # Calcula m
    numerador = sum(p[i]*(x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominador = sum(p[i]*(x[i] - x_mean) ** 2 for i in range(n))
    m = numerador / denominador
    # Calcula b
    b = y_mean - m * x_mean
    
    return m, b

Vs = E.Empresa(0, 0, 0, 0, 0)
Vs.valor = 460000
Vs.coeficiente = 0.82
potencia = 2
f_borrador = 0.5 #entre 0 e 1
NumGraficos = 11

valores = [empresa.get_log_value() for empresa in E.lista]
tentativas = [empresa.percent_try() for empresa in E.lista]
ataques = [empresa.percent_att() for empresa in E.lista]
danos = [empresa.percent_dam() for empresa in E.lista]
coeficientes = [empresa.coeficiente for empresa in E.lista]

pesos = [None] * NumGraficos

coef_tentativas = [None] * NumGraficos
coef_ataques = [None] * NumGraficos
coef_danos = [None] * NumGraficos

A_tentativas = [None] * NumGraficos
B_tentativas = [None] * NumGraficos
A_ataques = [None] * NumGraficos
B_ataques = [None] * NumGraficos
A_danos = [None] * NumGraficos
B_danos = [None] * NumGraficos

tentativas_desvio = [None] * NumGraficos
ataques_desvio = [None] * NumGraficos
danos_desvio = [None] * NumGraficos

coef_tentativas_desvio = [None] * NumGraficos
coef_ataques_desvio = [None] * NumGraficos
coef_danos_desvio = [None] * NumGraficos

A_tentativas_desvio = [None] * NumGraficos
B_tentativas_desvio = [None] * NumGraficos
A_ataques_desvio = [None] * NumGraficos
B_ataques_desvio = [None] * NumGraficos
A_danos_desvio = [None] * NumGraficos
B_danos_desvio = [None] * NumGraficos


for i in range(0,NumGraficos):
    #f_borrador = i/(NumGraficos - 1)
    Vs.coeficiente = i/(NumGraficos - 1)
    #potencia = i
    dist = [abs(empresa.coeficiente - Vs.coeficiente) for empresa in E.lista]
    borrador = sum(coef for coef in dist)/len(dist)

    dist = [math.pow((1-f_borrador)*c+borrador*f_borrador, potencia) for c in dist]
    D = 1 / sum(1/x for x in dist)

    pesos[i] = [(D/c) for c in dist]  # Alterei para criar uma lista ao invés de um gerador

    coef_tentativas[i] = melhor_reta(valores, tentativas, pesos[i])
    coef_ataques[i] = melhor_reta(valores, ataques, pesos[i])
    coef_danos[i] = melhor_reta(valores, danos, pesos[i])

    A_tentativas[i], B_tentativas[i] = coef_tentativas[i]
    A_ataques[i], B_ataques[i] = coef_ataques[i] 
    A_danos[i], B_danos[i] = coef_danos[i] 
    
    print("Equacao de curva de Tentativas: ", A_tentativas[i], " * X + ", B_tentativas[i])
    print("Equacao de curva de Ataques: ", A_ataques[i], " * X + ", B_ataques[i])
    print("Equacao de curva de Danos: ", A_danos[i], " * X + ", B_danos[i])

    tentativas_desvio[i] = [abs(A_tentativas[i] * empresa.get_log_value() + B_tentativas[i] - empresa.percent_try()) for empresa in E.lista] 
    ataques_desvio[i] = [abs(A_ataques[i] * empresa.get_log_value() + B_ataques[i] - empresa.percent_att()) for empresa in E.lista] 
    danos_desvio[i] = [abs(A_danos[i] * empresa.get_log_value() + B_danos[i] - empresa.percent_dam()) for empresa in E.lista] 

    coef_tentativas_desvio[i] = melhor_reta(valores, tentativas_desvio[i], pesos[i])
    coef_ataques_desvio[i] = melhor_reta(valores, ataques_desvio[i], pesos[i])
    coef_danos_desvio [i]= melhor_reta(valores, danos_desvio[i], pesos[i])

    A_tentativas_desvio[i], B_tentativas_desvio[i] = coef_tentativas_desvio[i]
    A_ataques_desvio[i], B_ataques_desvio[i] = coef_ataques_desvio[i]
    A_danos_desvio[i], B_danos_desvio[i] = coef_danos_desvio[i]


x_tentativas = [None] * NumGraficos
y_tentativas = [None] * NumGraficos
y_tentativas_up = [None] * NumGraficos
y_tentativas_down = [None] * NumGraficos                                          


fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

for i in range(0, NumGraficos):
    x_tentativas = np.linspace(min(valores), max(valores), 100)
    y_tentativas = np.polyval(coef_tentativas[i], x_tentativas)
    y_tentativas_up = np.polyval(tuple(x + y for x, y in zip(coef_tentativas[i], coef_tentativas_desvio[i])), x_tentativas)
    y_tentativas_down = np.polyval(tuple(x - y for x, y in zip(coef_tentativas[i], coef_tentativas_desvio[i])), x_tentativas)
    
    max_peso = max(pesos[i])
    ax.scatter(valores, [i/(NumGraficos - 1)]*len(valores), tentativas, alpha=np.array(pesos[i])/max_peso, color='blue')

    Vs.set_media_try(A_tentativas[i] * Vs.get_log_value() + B_tentativas[i])
    ax.scatter(Vs.get_log_value(), i/(NumGraficos - 1), Vs.percent_try(), color='black')
    ax.scatter(Vs.get_log_value(), i/(NumGraficos - 1), Vs.percent_try() + A_tentativas_desvio[i] * Vs.get_log_value() + B_tentativas_desvio[i], color='black')
    ax.scatter(Vs.get_log_value(), i/(NumGraficos - 1), Vs.percent_try() - A_tentativas_desvio[i] * Vs.get_log_value() - B_tentativas_desvio[i], color='black')

    ax.plot(x_tentativas, [i/(NumGraficos - 1)]*len(x_tentativas), y_tentativas, color='blue')
    ax.plot(x_tentativas, [i/(NumGraficos - 1)]*len(x_tentativas), y_tentativas_up, '--', color='royalblue')
    ax.plot(x_tentativas, [i/(NumGraficos - 1)]*len(x_tentativas), y_tentativas_down, '--', color='royalblue')

ax.set_xlabel('Valor da Empresa')
ax.set_ylabel('Coeficiente (0 a 1)')
ax.set_zlabel('Porcentagem de Tentativas')

plt.show()

x_ataques = [None] * NumGraficos
y_ataques = [None] * NumGraficos
y_ataques_up = [None] * NumGraficos
y_ataques_down = [None] * NumGraficos                                         

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

for i in range(0, NumGraficos):
    x_ataques = np.linspace(min(valores), max(valores), 100)
    y_ataques = np.polyval(coef_ataques[i], x_ataques)
    y_ataques_up = np.polyval(tuple(x + y for x, y in zip(coef_ataques[i], coef_ataques_desvio[i])), x_ataques)
    y_ataques_down = np.polyval(tuple(x - y for x, y in zip(coef_ataques[i], coef_ataques_desvio[i])), x_ataques)
    
    max_peso = max(pesos[i])
    ax.scatter(valores, [i/(NumGraficos - 1)]*len(valores), ataques, alpha=np.array(pesos[i])/max_peso, color='red')

    Vs.set_media_try(A_ataques[i] * Vs.get_log_value() + B_ataques[i])
    ax.scatter(Vs.get_log_value(), i/(NumGraficos - 1), Vs.percent_try(), color='black')
    ax.scatter(Vs.get_log_value(), i/(NumGraficos - 1), Vs.percent_try() + A_ataques_desvio[i] * Vs.get_log_value() + B_ataques_desvio[i], color='black')
    ax.scatter(Vs.get_log_value(), i/(NumGraficos - 1), Vs.percent_try() - A_ataques_desvio[i] * Vs.get_log_value() - B_ataques_desvio[i], color='black')

    ax.plot(x_ataques, [i/(NumGraficos - 1)]*len(x_ataques), y_ataques, color='red')
    ax.plot(x_ataques, [i/(NumGraficos - 1)]*len(x_ataques), y_ataques_up, '--', color='lightcoral')
    ax.plot(x_ataques, [i/(NumGraficos - 1)]*len(x_ataques), y_ataques_down, '--', color='lightcoral')

ax.set_xlabel('Valor da Empresa')
ax.set_ylabel('Coeficiente (0 a 1)')
ax.set_zlabel('Porcentagem de Ataques')

plt.show()

x_danos = [None] * NumGraficos
y_danos = [None] * NumGraficos
y_danos_up = [None] * NumGraficos
y_danos_down = [None] * NumGraficos                                         

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

for i in range(0, NumGraficos):
    x_danos = np.linspace(min(valores), max(valores), 100)
    y_danos = np.polyval(coef_danos[i], x_danos)
    y_danos_up = np.polyval(tuple(x + y for x, y in zip(coef_danos[i], coef_danos_desvio[i])), x_danos)
    y_danos_down = np.polyval(tuple(x - y for x, y in zip(coef_danos[i], coef_danos_desvio[i])), x_danos)
    
    max_peso = max(pesos[i])
    ax.scatter(valores, [i/(NumGraficos - 1)]*len(valores), danos, alpha=np.array(pesos[i])/max_peso, color='green')

    Vs.set_media_try(A_danos[i] * Vs.get_log_value() + B_danos[i])
    ax.scatter(Vs.get_log_value(), i/(NumGraficos - 1), Vs.percent_try(), color='black')
    ax.scatter(Vs.get_log_value(), i/(NumGraficos - 1), Vs.percent_try() + A_danos_desvio[i] * Vs.get_log_value() + B_danos_desvio[i], color='black')
    ax.scatter(Vs.get_log_value(), i/(NumGraficos - 1), Vs.percent_try() - A_danos_desvio[i] * Vs.get_log_value() - B_danos_desvio[i], color='black')

    ax.plot(x_danos, [i/(NumGraficos - 1)]*len(x_danos), y_danos, color='green')
    ax.plot(x_danos, [i/(NumGraficos - 1)]*len(x_danos), y_danos_up, '--', color='lightgreen')
    ax.plot(x_danos, [i/(NumGraficos - 1)]*len(x_danos), y_danos_down, '--', color='lightgreen')

ax.set_xlabel('Valor da Empresa')
ax.set_ylabel('Coeficiente (0 a 1)')
ax.set_zlabel('Porcentagem de Danos')

plt.show()