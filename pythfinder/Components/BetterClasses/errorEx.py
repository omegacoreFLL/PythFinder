# custom instance-checking method. For easier debugging
# not used in the code

def isType(obj, name, required_types):
    
    if not isinstance(obj, list):
        __throw("obj", list)
    if not isinstance(name, list):
        __throw("name", list)
    if not isinstance(required_types, list):
        __throw("required_types", list)

    length = len(obj)
    if not length == len(name) or not length == len(required_types):
        raise Exception("Not valid array length")

    for i in range(length):
        throw = False

        if not isinstance(name[i], str):
            __throw("name", str)
        elif not isinstance(required_types[i], list):
            if not isinstance(obj[i], required_types[i]):
                throw = True
        else:
            throw = True
            for Type in required_types[i]:
                if isinstance(obj[i], Type):
                    throw = False
            
        if throw:
            __throw(name[i], required_types[i])

def __throw(name, required_types):
    raise Exception("Not a valid ---{0}---. Needed type(s): {1}".format(name, required_types))

    
    
            