#!/bin/python3

def makeType(name, fields):
    
    #TODO validate fields
    #must be an iterable of the types (string, type, bool)

    membersDict = {'fields': fields}

    def repr(instance):
        repr_string = name + "("
        i = 0
        for field in instance.fields:
            if i > 0:
                repr_string += ", "    
            repr_string += field[0] + "=" + str(getattr(instance,field[0]))
            # repr_string += str(field[0]) + ":" + str(field[1]) + ":" + str(field[2])
            i += 1
        repr_string += ")"
        return repr_string
    

    def type_init(self, *args):
        #TODO: initialize with 
        i = 0
        for field in self.fields:
            #TODO: cast to provided type
            #TODO: set to None those that are None
            setattr(self, field[0], args[i] )
            i += 1


    membersDict['__repr__'] = repr
    membersDict['__init__'] = type_init

    return type(name, (), membersDict )

Person = makeType("Person", (('first_name', str),('last_name', str),('id', int)))

print(Person("John", "Doe", 3))