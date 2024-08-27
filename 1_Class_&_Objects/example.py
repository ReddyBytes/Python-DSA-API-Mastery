# Defining a class
class House:
    def __init__(self,price):  # constuctor or init method
                               # price is the parameter which can varies dynamically or we can set default value as below 

        self.price=price    # Instance Attribute
                            # self.price is the attribute to the class , price is the parameter

        self.price=500000   # 500000 is the value  to the attribute. 
                            # when we assign a value to attribute we can omit this parameter from constructot 

#my_house=House(3)  # my_house is variable/instance/object , if we pass any values inside () those are arguments
                  

#print(my_house)   # to print the object
#print(my_house.price)  # It prints the price 

##############################################################################

# Class with no arguments passing 

class Backpack:

    def __init__(self):
        self.items=[]
        #print(self.items)           # to access attributes inside a class use self.<attribute name>

my_backpack = Backpack()
#print(my_backpack.items)          # to access attributes outside a class use <object>.<attribute name>
#print(Backpack.items)              # this will give an attribute error because we cann't access instance attributes outside a class using classname
##############################################################################

# Class with 1 argument passing
class Circle:

    def __init__(self, radius):
        #print(self)
        self.radius=radius

my_circle=Circle(5)                 # here we didn't pass self value because self value is auto assign by the python as memory location.
                                    # to check the value of self uncomment print(self) line in the init method 

#############################################################################

# Class with 2 argument passing

class Rectangle:

    def __init__(self, length, breadth):
        self.length=length
        self.breadth=breadth

my_rectangle=Rectangle(5, 2)    # default argument passing
my_rectangle=Rectangle(breadth=2, length=5)   # keyword argument passing 

#print(my_rectangle.breadth)


############################################################################

# default arguments passing
class Laptop:
    
    def __init__(self, price, brand="HP"):    # default argument passing & these default param always at last position otherwise gives an error
    #def __init__(self, brand="HP", price):     # wrong syntax
        self.brand=brand
        self.price=price

my_lap=Laptop(10000)                     # this object assigns the above default parameter, brand as HP
my_lap2=Laptop(10000, "DELL")              # this object overwrites the default parameter and assign brand as DELL
my_lap3=Laptop("DELL",20002)    # no error but assign as price=DELL, brand=20002

# print(my_lap.brand)
# print(my_lap2.brand)


#####################################################################################

# Iterate over instances

class Player:

    def __init__(self, x, y):
        self.x=x
        self.y=y

player1=Player(2, 5)
player2=Player(6, 8)
player3=Player(11,44)

players=[player1, player2, player3]

# for player in players:
#     print(f"x:{player.x}, y:{player.y}")


#####################################################################################

# Updating the instance attributes/variables

class Car:

    def __init__(self, color):
        self.color=color
        self.brand=["Hyundai", "Tata", "Mahindra"]


# my_car=Car("BLUE")
# print(my_car.color)

# print("changing car color")
# my_car.color="RED"
# print(my_car.color)

# my_car1=Car("Yellow")
# print(my_car1.brand[1])
# print("updating the car brands")
# my_car1.brand[1]=["RR", "Audi"]
# print(my_car1.brand)


#####################################################################################

# Deleting an instance attibute

class Dog:

    def __init__(self, name, breed):
        self.name=name
        self.breed=breed

my_dog=Dog("Snoopy", "Russian")
#print(my_dog.name)
#print("deleting a dog attribute name")
#del my_dog.name

#print(my_dog.name)


####################################################################################

# CLASS Attribute

####################################################################################
class Human:

    species="Homo sapiens"   # class attribute "outside of all methods "
    id=1

    def __init__(self, name, age):
        self.id=Human.id          # Accessing Class attribute inside the method 
        self.name=name
        self.age=age

        Human.id+=1             # incrementing the class attribute

# print(Human.species)    # Accessing class attributes <classname>.<variable name>

human1=Human("saran",22)
# human2=Human("rahul",25)

# print(Human.id) 
# print(human2.id)
print(human1.species)  # we can access class attributes using object/instance name also outside of the class
                        # bcz every method can access class attributes
