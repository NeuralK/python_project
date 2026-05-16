import pickle
import neat

# Así es como recuperás el cerebro que tanto te costó guardar
with open("velocidad_bola.pkl", "rb") as f:
    winner_genome = pickle.load(f)

print("¡Cerebro cargado! Ya podés ponerlo a prueba.")