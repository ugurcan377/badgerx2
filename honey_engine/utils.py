from itertools import zip_longest
import math

from numpy import array
from numpy.linalg import norm


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def tf_idf(tf, df, N):
    return (1 + math.log10(tf)) * math.log10(N / df)


def normalize(vector, element):
    vector = array(vector)
    return element / norm(vector)

