import csv

pesos = ['0.5','0.75','1','1.25','1.5']

def main():
    with open("pesos.csv", "w") as file:
        csvwriter = csv.writer(file)
        for i in range(len(pesos)):
            for j in range(len(pesos)):
                if i > j:
                    a = [pesos[i],pesos[j]]
                    csvwriter.writerow(a)
    pass


if __name__ == '__main__':
    main()