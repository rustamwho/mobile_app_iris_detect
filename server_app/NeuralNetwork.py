import numpy as np
import math as m

synapses_hidden = 2 * np.random.random((2, 3)) - 1
synapses_output = 2 * np.random.random((3, 1)) - 1


def Learn():
    synapses_hidden = 2 * np.random.random((2, 3)) - 1
    synapses_output = 2 * np.random.random((3, 1)) - 1
    array = []
    with open("LearningSample.txt") as file:
        array = [row.strip().split("\t") for row in file]
    arrayX = []
    arrayY = []
    print(array)
    for (i, value1, value2) in array:
        arrayX.append([float(i), float(value1)])
        arrayY.append(int(value2))

    arrayX = arrayX / np.amax(arrayX, axis=0)

    arrayX = arrayX.T
    for j in range(20000):
        l0 = arrayX
        # Входной слой ( 2 входа )
        l1 = 1 / (1 + np.exp(-(l0.dot(synapses_hidden))))
        # Скрытый слой ( 3 скрытых нейрона )
        l2 = 1 / (1 + np.exp(-(l1.dot(synapses_output))))
        # Выходной слой ( 1 выходной нейрон )
        l2_delta = (arrayY - l2) * (l2 * (1 - l2))
        # вычисляем ошибку и используем дельта-правило
        l1_delta = l2_delta.dot(synapses_output.T) * (l1 * (1 - l1))
        # получаем ошибку на скрытом слое и используем дельта-правило
        synapses_output += l1.T.dot(l2_delta)
        # корректируем веса
        synapses_hidden += l0.T.dot(l1_delta)
        # корректируем веса от входов к скрытым нейронам
    print(l2, arrayY)


def neuralNetwork(a, b):
    inputs = np.array([a, b])
    l1 = 1 / (1 + np.exp(-(inputs.dot(synapses_hidden))))
    l2 = 1 / (1 + np.exp(-(l1.dot(synapses_output))))
    L = a
    d = b
    normalD = 5 - 3 * m.tanh(0.4 * m.log10(L))
    if (d > normalD - 1.7) & (d < normalD + 1.7):
        return "Нормальное ФС"
    else:
        return str(d) + str(L) + "Есть отклонения"
