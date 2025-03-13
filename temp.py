#!/usr/bin/env python

def foo(a, b, **args):
    print(a)
    print(b)
    print(args)

foo(1, 2, args=(4, 5, 6))

