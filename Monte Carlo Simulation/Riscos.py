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

### DEFINIÇÃO DA EMPRESA A SER SIMULADA
Vs = E.Empresa(0, 0, 0, 0, 0)
Vs.valor = 300000
Vs.coeficiente = 0.6

#JOÃO NAO PRECISA ALTERAR AQ EM BAIXO SÓ SE QUISER
potencia = 1
f_borrador = 0.5 #entre 0 e 1

# Extrair os dados das empresas
valores = [empresa.get_log_value() for empresa in E.lista] ##SE FOR TESTAR SEM SER OS VALORES EM LOG ALTERAR AQUI E, SE DESEJAR< NOS PRINTS TAMBÈM
tentativas = [empresa.percent_try() for empresa in E.lista]
ataques = [empresa.percent_att() for empresa in E.lista]
danos = [empresa.percent_dam() for empresa in E.lista]
coeficientes = [empresa.coeficiente for empresa in E.lista]

#Cálculo dos pesos de acordo com o coeficiente
dist = [abs(empresa.coeficiente - Vs.coeficiente) for empresa in E.lista]
borrador = sum(coef for coef in dist)/len(dist)

dist = [math.pow((1-f_borrador)*c+borrador*f_borrador, potencia) for c in dist]
D = 1 / sum(1/x for x in dist)

#Print dos pesos
print("COEFICIENTES: ", borrador, D)
for c in range(len(dist)):
    print("empresa nº ", c+1, " com coeficiente ", E.lista[c].coeficiente, " tem distancia ", dist[c], " e peso de " , 100*D/dist[c],"%")
pesos = [D/c for c in dist]

#Definição das retas de aproximação
coef_tentativas = melhor_reta(valores, tentativas, pesos)
coef_ataques = melhor_reta(valores, ataques, pesos)
coef_danos = melhor_reta(valores, danos, pesos)

A_tentativas, B_tentativas = coef_tentativas
A_ataques, B_ataques = coef_ataques
A_danos, B_danos = coef_danos

print("Equacao de curva de Tentativas: ", A_tentativas, " * X + ", B_tentativas)
print("Equacao de curva de Ataques: ", A_ataques, " * X + ", B_ataques)
print("Equacao de curva de Danos: ", A_danos, " * X + ", B_danos)

#Extrair dados de desvio das empresas
tentativas_desvio = [abs(A_tentativas * empresa.get_log_value() + B_tentativas - empresa.percent_try()) for empresa in E.lista] 
ataques_desvio = [abs(A_ataques * empresa.get_log_value() + B_ataques - empresa.percent_att()) for empresa in E.lista] 
danos_desvio = [abs(A_danos * empresa.get_log_value() + B_danos - empresa.percent_dam()) for empresa in E.lista] 

#Definição das retas de desvio padrão
coef_tentativas_desvio = melhor_reta(valores, tentativas_desvio, pesos)
coef_ataques_desvio = melhor_reta(valores, ataques_desvio, pesos)
coef_danos_desvio = melhor_reta(valores, danos_desvio, pesos)

A_tentativas_desvio, B_tentativas_desvio = coef_tentativas_desvio
A_ataques_desvio, B_ataques_desvio = coef_ataques_desvio
A_danos_desvio, B_danos_desvio = coef_danos_desvio

#Equações das retas
print("Equacao de curva de desvio de Tentativas: ", A_tentativas_desvio, " * X + ", B_tentativas_desvio)
print("Equacao de curva de desvio de Ataques: ", A_ataques_desvio, " * X + ", B_ataques_desvio)
print("Equacao de curva de desvio de Danos: ", A_danos_desvio, " * X + ", B_danos_desvio)

#Médias esperadas para empresa simulada
Vs.set_media_try(A_tentativas*Vs.get_log_value()+ B_tentativas)
Vs.set_media_att(A_ataques*Vs.get_log_value()+ B_ataques)
Vs.set_media_dam(A_danos*Vs.get_log_value()+ B_danos)
print("Média de Tentativas esperada para empresa com valor de ", Vs.valor, ": ",Vs.percent_try(), Vs.tentativas)
print("Média de Ataques esperada para empresa com valor de ", Vs.valor, ": ",Vs.percent_att(), Vs.ataques)
print("Média de Danos esperada para empresa com valor de ", Vs.valor, ": ",Vs.percent_dam(), Vs.danos)

#Desvios esperados para empresa simulada
print("Desvio de Tentativas esperada para empresa com valor de ", Vs.valor, ": ",A_tentativas_desvio*Vs.get_log_value()+ B_tentativas_desvio)
print("Desvio de Ataques esperada para empresa com valor de ", Vs.valor, ": ", A_ataques_desvio*Vs.get_log_value()+ B_ataques_desvio)
print("Desvio de Danos esperada para empresa com valor de ", Vs.valor, ": ", A_danos_desvio*Vs.get_log_value()+ B_danos_desvio)

max_peso = max(pesos)

##### PLOT GRÁFICO TENTATIVAS
x_tentativas = np.linspace(min(valores), max(valores), 100)
y_tentativas = np.polyval(coef_tentativas, x_tentativas) #Reta principal
y_tentativas_up = np.polyval(tuple(x + y for x, y in zip(coef_tentativas, coef_tentativas_desvio)), x_tentativas) #Reta Superior com Desvio 
y_tentativas_down = np.polyval(tuple(x - y for x, y in zip(coef_tentativas, coef_tentativas_desvio)), x_tentativas) #Reta Inferior com Desvio
plt.scatter(valores, tentativas, alpha=np.array(pesos)/max_peso, color='blue') #Pontos do gráfico
#for valor, tentativa, p in zip(valores, tentativas, pesos):
    #plt.text(valor, tentativa-0.025, "{:.2f}%".format(p).split('.')[1], ha='center') #Texto com o peso
Vs.set_media_try(A_tentativas * Vs.get_log_value() + B_tentativas)
plt.scatter(Vs.get_log_value(), Vs.percent_try(), color='black') #Ponto Médio esperado para empresa simulada
plt.scatter(Vs.get_log_value(), Vs.percent_try() + A_tentativas_desvio * Vs.get_log_value() + B_tentativas_desvio, color='black') #Ponto Médio esperado para empresa simulada com Desvio Superior
plt.scatter(Vs.get_log_value(), Vs.percent_try() - A_tentativas_desvio * Vs.get_log_value() - B_tentativas_desvio, color='black') #Ponto Médio esperado para empresa simulada com Desvio Inferior
plt.plot(x_tentativas, y_tentativas, color='blue')
plt.plot(x_tentativas, y_tentativas_up, '--', color='royalblue')
plt.plot(x_tentativas, y_tentativas_down, '--', color='royalblue')

plt.ylabel('Porcentagem de Tentativas')
plt.xlabel('Valor da Empresa')
plt.title('Pontos das Empresas')
plt.show()

##### PLOT GRÁFICO ATAQUES
x_ataques = np.linspace(min(valores), max(valores), 100)
y_ataques = np.polyval(coef_ataques, x_ataques) #Reta principal
y_ataques_up = np.polyval(tuple(x + y for x, y in zip(coef_ataques, coef_ataques_desvio)), x_ataques) #Reta Superior com Desvio 
y_ataques_down = np.polyval(tuple(x - y for x, y in zip(coef_ataques, coef_ataques_desvio)), x_ataques) #Reta Inferior com Desvio
plt.scatter(valores, ataques, alpha=np.array(pesos)/max_peso, color='red') #Pontos do gráfico
#for valor, ataque, p in zip(valores, ataques, pesos):
    #plt.text(valor, ataque-0.025, "{:.2f}%".format(p).split('.')[1], ha='center') #Texto com o peso
Vs.set_media_att(A_ataques * Vs.get_log_value() + B_ataques)
plt.scatter(Vs.get_log_value(), Vs.percent_att(), color='black') #Ponto Médio esperado para empresa simulada
plt.scatter(Vs.get_log_value(), Vs.percent_att() + A_ataques_desvio * Vs.get_log_value() + B_ataques_desvio, color='black') #Ponto Médio esperado para empresa simulada com Desvio Superior
plt.scatter(Vs.get_log_value(), Vs.percent_att() - A_ataques_desvio * Vs.get_log_value() - B_ataques_desvio, color='black') #Ponto Médio esperado para empresa simulada com Desvio Inferior
plt.plot(x_ataques, y_ataques, color='red')
plt.plot(x_ataques, y_ataques_up, '--', color='lightcoral')
plt.plot(x_ataques, y_ataques_down, '--', color='lightcoral')

plt.ylabel('Porcentagem de Ataques')
plt.xlabel('Valor da Empresa')
plt.title('Pontos das Empresas')
plt.show()

##### PLOT GRÁFICO DANOS
x_danos = np.linspace(min(valores), max(valores), 100)
y_danos = np.polyval(coef_danos, x_danos) #Reta principal
y_danos_up = np.polyval(tuple(x + y for x, y in zip(coef_danos, coef_danos_desvio)), x_danos) #Reta Superior com Desvio 
y_danos_down = np.polyval(tuple(x - y for x, y in zip(coef_danos, coef_danos_desvio)), x_danos) #Reta Inferior com Desvio
plt.scatter(valores, danos, alpha=np.array(pesos)/max_peso, color='green') #Pontos do gráfico
#for valor, dano, p in zip(valores, danos, pesos):
    #plt.text(valor, dano-0.025, "{:.2f}%".format(p).split('.')[1], ha='center') #Texto com o peso
Vs.set_media_dam(A_danos * Vs.get_log_value() + B_danos)
plt.scatter(Vs.get_log_value(), Vs.percent_dam(), color='black') #Ponto Médio esperado para empresa simulada
plt.scatter(Vs.get_log_value(), Vs.percent_dam() + A_danos_desvio * Vs.get_log_value() + B_danos_desvio, color='black') #Ponto Médio esperado para empresa simulada com Desvio Superior
plt.scatter(Vs.get_log_value(), Vs.percent_dam() - A_danos_desvio * Vs.get_log_value() - B_danos_desvio, color='black') #Ponto Médio esperado para empresa simulada com Desvio Inferior
plt.plot(x_danos, y_danos, color='green')
plt.plot(x_danos, y_danos_up, '--', color='lightgreen')
plt.plot(x_danos, y_danos_down, '--', color='lightgreen')

plt.ylabel('Porcentagem de Danos')
plt.xlabel('Valor da Empresa')
plt.title('Pontos das Empresas')
plt.show()

t = 0
a = 0
d = 0
REPS_MONTEC = 100000000
print("SIMULAÇÃO DE MONTECARLO:")
for i in range(1, 1 + REPS_MONTEC):
    t1, a1, d1 = Vs.amostra_montecarlo()
    t += t1
    a += a1
    d += d1
    if i % (REPS_MONTEC/10) == 0:
        print(10*i / (REPS_MONTEC/10), "%")
print(t/REPS_MONTEC, a/REPS_MONTEC, d/REPS_MONTEC)
print(Vs.tentativas, Vs.ataques, Vs.danos)
