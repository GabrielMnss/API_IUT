import os
import tensorflow
import numpy as np
import pandas as pd
import tensorflow_hub as hub

module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
model = hub.load(module_url)
print("module %s loaded" % module_url)


def embed(input):
    return model(input)


def verifyForOpenQuestions(str1, str2):
    message_embeddings_ = embed([str1, str2])
    print("ia response coeff", np.inner(message_embeddings_, message_embeddings_)[0][1])
    return np.inner(message_embeddings_, message_embeddings_)[0][1] > 0.75
