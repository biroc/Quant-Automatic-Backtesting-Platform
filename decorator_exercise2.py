#!/usr/bin/python
# -*- coding: utf-8 -*-

# Date Oc2 26 2016
# @Author Dawei Wang

###################################
#####Python Decorator Exercise#####

'''
function exercise

'''
def foo(bar):
    return bar + 1


print(foo(2) == 3)
print "\n"

print "Function in Pyhon is First Class Object; " \
      "proving by following example"

def foo(bar):
    return bar + 1

print(foo)
print(foo(2))
print(type(foo))


def call_foo_with_arg(foo, arg):
    return foo(arg)

print(call_foo_with_arg(foo, 3))

####Nested Function####
def parent():
    print("Printing from the parent() function.")

    def first_child():
        return "Printing from the first_child() function."

    def second_child():
        return "Printing from the second_child() function."

    print(first_child())
    print(second_child())

parent()

###############Decorator#################

###Put simply, decorators wrap a function,
### modifying its behavior.
print "\n"

def my_decorator(some_function):

    def wrapper():

        print("Something is happening before some_function() is called.")

        some_function()

        print("Something is happening after some_function() is called.")

    return wrapper


def just_some_function():
    print("Wheee!")

###Without Decorator
just_some_function = my_decorator(just_some_function)

just_some_function()

###With Decorator
print "\n"
print "same output with decorator"
print "\n"

@my_decorator
def just_some_function():
    print("Wheee!")
just_some_function()
