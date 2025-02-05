#!/usr/bin/env python

import pickle

keys = ['1.00', '2.00', '3.00']
vals = [[[i, 2*i] for i in range(10)], [[2*i, 3*i] for i in range(10)], [[3*i, 4*i] for i in range(10)]]
data = {k: v for k, v in zip(keys, vals)}

with open('tmp.pkl', 'wb') as file:
    pickle.dump(data, file)
