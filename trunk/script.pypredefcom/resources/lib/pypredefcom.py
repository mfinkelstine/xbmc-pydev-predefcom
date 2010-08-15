'''
Created on Jul 31, 2010

@author: jim
'''

import inspect
import os
import re

oneindent = "    "

def visiblename(name, all=None):
    """Decide whether to show documentation on a variable."""
    # Certain special names are redundant.
    if name in ['__builtins__', '__doc__', '__file__', '__path__',
                '__module__', '__name__', 'Helper' ]: return 0
    # Private names are hidden, but special names are displayed.
    if name.startswith('__') and name.endswith('__'): return 1
    if all is not None:
        # only document that which the programmer exported in __all__
        return name in all
    else:
        return not name.startswith('_')
    
def ensuredir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

docquote = '''"""'''
quote = '''"'''

def displayDocLine(f,object, indent = ""):
    try:
        docline = object.__doc__
    except AttributeError:
        return
    
    if docline is None or len(docline) == 0:
        return
    lines = docline.splitlines()

    prefix = indent + docquote    
    for line in lines:
        f.write(prefix + line + "\n")
        prefix = indent
    f.write( indent + docquote + '\n\n')
    
def myformatvalue(object):
    """Format an argument default value as text."""
    return '=' + repr(object)

    
def displayMethod(f, method, indent = ""):
    name = method.__name__
    f.write (indent + "def " + name)
    
    try:
#    if inspect.isfunction(method):
        args, varargs, varkw, defaults = inspect.getargspec(method)
        argspec = inspect.formatargspec(
            args, varargs, varkw, defaults, formatvalue=myformatvalue)
        if name == '<lambda>':
            argspec = argspec[1:-1] # remove parentheses
#    else:
#        argspec = '(...)'
    except TypeError:
        argspec = '(*args)'
        
    f.write (argspec + ":\n")

    
    displayDocLine(f,method,indent + oneindent)
    
def displayClass(f, clazz, indent = ""):
    name = clazz.__name__
    all = dir(clazz)
    f.write (indent + "class " + name + ":\n" )
    displayDocLine(f, clazz, indent + oneindent)
    
    parts = inspect.getmembers(clazz)
        
    for key, value in parts:
        if visiblename(key,all):
#            if inspect.isclass(value):
#                displayClass(f,value, indent + oneindent)
            if lookslikeamethod(value):
                displayMethod(f,value,indent + oneindent)
            else:
                otherpart(f,key,value,indent + oneindent)
    f.write("\n\n")

def otherpart(f, key, value, indent = ""):
#    f.write( indent +  "other part:" + key + ", " + str(value) + " --- of type --->(" + str(type(value)) + ")\n")
    print( indent +  "other part:" + key + ", " + str(value) + " --- of type --->(" + str(type(value)) + ")\n")
    print( indent + oneindent + str(inspect.getmembers(value)))
    return

def lookslikeamethod(object):
    if inspect.isfunction(object) or inspect.ismethod(object) or inspect.isbuiltin(object) or inspect.ismethoddescriptor(object):
        return True
    return False

def lookslikeattribute(object):
    if type(object) is int or type(object) is str or type(object) is bool:
        return True
    
def displayAttribute(f, key, value, indent = ""):
    mytype = re.sub("^<type '", "", repr(type(value)), 1)
    mytype = re.sub("'>$", "", mytype, 1)
    
    f.write( indent + key + " = " +  mytype + "\n")
    return

def pypredefmodule(f, module):
    """Produce PyDev Predefined Completions for a module."""
    
    print ("writing to file " + str(f))
    
    name = module.__name__ # ignore the passed-in name
    try:
        all = object.__all__
    except AttributeError:
        all = None
    
    displayDocLine(f, module)

    parts = inspect.getmembers(module)
    
    for key, value in parts:
        if visiblename(key, all):
            if inspect.isclass(value):
                displayClass(f,value)
            elif lookslikeamethod(value):
                displayMethod(f,value)
            elif lookslikeattribute(value):
                displayAttribute(f,key,value)
            else:
                otherpart(f,key,value)
    
    
    
    