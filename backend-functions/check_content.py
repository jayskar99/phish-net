# use ai/ml model to do basic check of body content
from sentence_transformers import SentenceTransformer
import numpy as np
import pygad
import pandas as pd
import json
import sqlite3

embedder = SentenceTransformer('all-MiniLM-L6-v2')
texts = []
labels = np.array([])
int_labels = np.array([])
best_weights = []
X = []

# database connection
def connect_db():
    conn = sqlite3.connect("phish.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def train_check_content():
    """
    Uses PyGAD genetic algorithm to develop classification for phishing emails

    Returns:
        best_weights: array of best model weights
    """
    global best_weights
    global texts
    global labels
    global int_labels
    global X
    df = pd.read_csv("Phishing_validation_emails.csv")
    texts = df["Email Text"].values
    labels = df["Email Type"].values
    labels = np.array(labels)
    for label in labels:
        np.append(int_labels, 1 if label == "Phishing Email" else 0)

    X = embedder.encode(texts)
    num_features = X.shape[1]

    ga = pygad.GA(
        num_generations=1000,
        sol_per_pop=40,
        num_parents_mating=10,
        num_genes=num_features,
        mutation_percent_genes=10,
        fitness_func=fitness_func
    )
    print('Starting training')
    ga.run()
    print('Training finished')
    best_weights = ga.best_solution()[0]
    

    return best_weights

def check_content(text):
    '''
    Classifies the ctext entry as a Phising or Safe Email
    '''
    v = embedder.encode([text])
    return "Phishing Email" if v @ best_weights >= 0 else "Safe Email"

def fitness_func(instance, solution, idx):
    '''
    Function that determines how well an individual chromosome in the genetic algorithm classifies the text
    '''
    global int_labels
    global X
    w = np.array(solution)
    logits = X @ w
    preds = (logits >= 0).astype(int)
    return np.mean(preds == int_labels)

train_check_content()
num_correct = 0
num_total = len(texts)
for i in range(num_total):
    result = check_content(texts[i])
    # print(f'{result} (expected {labels[i]})')
    num_correct += 1 if result == labels[i] else 0

print(f'Correctly classified {num_correct} / {num_total} ({num_correct/num_total}) emails')
