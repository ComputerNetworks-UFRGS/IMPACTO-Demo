import math
import random

class Empresa:
    def __init__(self, valor, tentativas, ataques, danos, coef):
        self.valor = valor ## Valor da empresa
        self.tentativas = tentativas ## Nº de tentativas de ataque
        self.ataques = ataques ## Nº de ataques que ocorreram
        self.danos = danos ## Nº de vezes que o dano ocorreu
        self.coeficiente = coef ## Coeficiete de segurança da empresa, variando de 0 a 1
        
    ### Essa equação simula o comportamento de uma simulação de montecarlo dada da seguinte maneira
    
    ### Sabendo que uma empresa tem probabilidade T de ocorrer uma ou mais tentativas de ataques, a probabilidade esperada para
    ### ocorrer N ataques é de (1-T)*T^N
    
    ### Caso houvessem infinitas simulações randômicas de tentativa de ataque o gráfico teria um comportamento suave
    ### Essa função tem como objetivo simular esse comportamento suave sem necessidade de processamento:
    ### Imaginando que infinitas simulações fossem feitas, caso elas fossem colocadas em ordem de quantas tentativas de ataque ocorreram
    ### e depois definidas em um espectro de de 0 a 1 em vez de 0 a infinito ela teria esse comportamento.
    
    ### Dado um X indo de 0 a 1, essa função retorna o numero de tentativas de ataques de cibersegurança que a simulação, na posição X ordenada
    ###  de 0 a 1, teria dado a probabilidade de ocorrer pelo menos uma tentativa de ataque
    
    ### Caso desejas buscar médias esperadas, é possível testar N pontos divididos igualmente no intervalor de [0,1[ (não adicionar 1 na simulação
    ### pois esse é o caso de ocorrer infinitas tentativas) e então calcular o que desejar
    def func_try(self, X):
        return math.floor(math.log(1-X, self.percent_try()))
    
    ### Essa equação apresenta o mesmo comportamento da anterior mas agora retorna o número de Ataques que realmente ocorrem dada a probabilidade
    ### de ocorrer ao menos uma tentativa de ataque e a probabilidade do ataque ser efetivo
    def func_att(self, X):
        return math.floor(math.log(1-X, self.percent_att()*self.percent_try()/(1-self.percent_try()*(1-self.percent_att()))))
        
    ### Essa equação apresenta o mesmo comportamento da anterior mas agora retorna o número de ocorrências do dano que deseja ser simulado dada a probabilidade
    ### de ocorrer ao menos uma tentativa de ataque, a probabilidade do ataque ser efetivo e a probabilidade de, caso o ataque ocorra, qual a probabilidade
    ### daquele dano específico ocorrer
    def func_dam(self, X):
        return math.floor(math.log(1-X, self.percent_dam()*self.percent_att()*self.percent_try()/(1-self.percent_try()*(1-self.percent_dam()*self.percent_att()))))
        
    ### Retorna valor da empresa
    def get_value(self):
        return self.valor
    
    ### Retorna Log do valor da empresa
    def get_log_value(self):
        return math.log(self.valor)
        
    ### Considera o numero de tentativas de ataque que a empresa sofreu e retorna a probabilidade de ocorrer ao menos uma tentativa de ataque, considerando 
    ### que esse número dado pela empresa seja a média
    def percent_try(self):
        return 1-(1/(self.tentativas+1))
    
    ### Considera o numero de tentativas de ataque que a empresa sofreu e de ataques que ocorreram realmente e retorna a probabilidade de ocorrer ao menos um ataque, considerando que esses números 
    ### dados pela empresa sejam a média
    def percent_att(self):
        if self.percent_try() <= 0: ## Arrumar isso
            return 0
        return  (1 - self.percent_try())*self.ataques/self.percent_try()
    
    ### Considera o numero de tentativas de ataque que a empresa sofreu, de ataques que ocorreram realmente e de vezes que tal dano ocorreu e retorna a probabilidade de ocorrer ao menos uma vez esse dano
    ### caso ocorra um ataque, considerando que esses números dados pela empresa sejam a média
    def percent_dam(self):
        if self.percent_att() <= 0: ## Arrumar isso
            return 0
        return  (self.danos/self.percent_try() - self.danos)/self.percent_att()
    
    ### AS FUNCOES "SET" A SEGUIR DEVEM SER CRIADAS NA ORDEM TRY -> ATT -> DAM POIS UMA DEPENDE DA ANTERIOR PRA DAR O VALOR CORRETO!!!

    ### Seta um número de tentativas de ataques que a empresa sofreu como a média de tentativas de ataques esperados pela simulação de montecarlo
    def set_media_try(self, T):
        self.tentativas = 1/(1-T)-1
        
    ### Seta um número de ataques que a empresa sofreu como a média de ataques esperados pela simulação de montecarlo
    def set_media_att(self, A):
        self.ataques = 1/(1-(A*self.percent_try()/(1-self.percent_try()*(1-A))))-1
    
    ### Seta um número de ocorrencias do dano que a empresa sofreu como a média de ocorrencias do dano esperados pela simulação de montecarlo
    def set_media_dam(self, D):
        self.danos = self.ataques * D

    ### Retorna clone da empresa
    def clone(self):
        return Empresa(self.valor, self.tentativas, self.ataques, self.danos, self.coeficiente)
        
    def amostra_montecarlo(self):
        tentativas = 0
        ataques = 0
        danos = 0
        precision = 100000000
        if random.randint(0, precision) < precision * self.percent_try():
            tentativas += 1
            if random.randint(0, precision) < precision * self.percent_att():
                ataques += 1
                if random.randint(0, precision) < precision * self.percent_dam():
                    danos +=1
            ttemp, atemp, dtemp = self.amostra_montecarlo()
            tentativas += ttemp
            ataques += atemp
            danos += dtemp
        return tentativas, ataques, danos


lista = []
### DADOS FICTICIOS PARA TESTE DE SIMULAÇÕES
empresa = Empresa(220000, 4, 3, 1, 0.5)
lista.append(empresa.clone())
empresa = Empresa(80000, 2, 1, 0, 0.3)
lista.append(empresa.clone())
empresa = Empresa(50000, 1, 0, 0, 0.3)
lista.append(empresa.clone())
empresa = Empresa(360000, 3, 1, 0, 0.4)
lista.append(empresa.clone())
empresa = Empresa(850000, 7, 4, 1, 0.7)
lista.append(empresa.clone())
empresa = Empresa(1420000, 12, 3, 1, 0.6)
lista.append(empresa.clone())
empresa = Empresa(1880000, 16, 9, 2, 0.8)
lista.append(empresa.clone())
empresa = Empresa(980000, 14, 8, 6, 0.2)
lista.append(empresa.clone())
empresa = Empresa(580000, 3, 2, 1, 0.5)
lista.append(empresa.clone())
empresa = Empresa(320000, 2, 2, 0, 0.9)
lista.append(empresa.clone())
empresa = Empresa(1750000, 8, 5, 2, 0.7)
lista.append(empresa.clone())
empresa = Empresa(1630000, 10, 6, 5, 0.1)
lista.append(empresa.clone())
empresa = Empresa(1980000, 12, 4, 1, 0.3)
lista.append(empresa.clone())

empresa = Empresa(470000, 0, 0, 0, 0.7)
empresa.set_media_try(0.67)
empresa.set_media_att(0.74)
empresa.set_media_dam(0.81)
lista.append(empresa.clone())
empresa = Empresa(2210000, 0, 0, 0, 0.4)
empresa.set_media_try(0.93)
empresa.set_media_att(0.48)
empresa.set_media_dam(0.44)
lista.append(empresa.clone())
empresa = Empresa(1150000, 0, 0, 0, 0.9)
empresa.set_media_try(0.87)
empresa.set_media_att(0.33)
empresa.set_media_dam(0.12)
lista.append(empresa.clone())
empresa = Empresa(1520000, 0, 0, 0, 0.6)
empresa.set_media_try(0.91)
empresa.set_media_att(0.27)
empresa.set_media_dam(0.96)
lista.append(empresa.clone())
empresa = Empresa(980000, 0, 0, 0, 0.8)
empresa.set_media_try(0.76)
empresa.set_media_att(0.94)
empresa.set_media_dam(0.75)
lista.append(empresa.clone())