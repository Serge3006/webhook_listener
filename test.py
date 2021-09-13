import numpy as np

def function(phrase):

    words = phrase.split(" ")

    n_chards_words = []
    for word in words:

        n_chars = len(word)
        n_chards_words.append(n_chars)

    index = np.argmax(n_chards_words)

    return words[index]



frase = "Hola que tal usuario"

print(function(frase))