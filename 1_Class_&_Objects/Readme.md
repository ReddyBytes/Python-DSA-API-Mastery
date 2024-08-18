## Class
Class is a Blueprint/Plan to create objects which encapsulates both data(Attributes) and methods(functions).  
From the class we can create multiple objects  

`Object :` An instance of class. Encapsulates both attributes and methodsand serves an runtime for the OOPs env   

`Naming convention for classes:`  Pascal case or upper camel case    
Ex :  `C`amel, `L`owe`C`ase, `B`ack`P`ack  

Class has two parts  
1. __Header :__  --> 1st line of the class, specifies the name of the class and specifies the inheriting class.  
    `class <ClassName>:`
2. __Body :__  Contains the elements of a blueprint including Attributes , Methods  

Elements in a class:  
1. Class Attributes
2. __ init __
3. Other method


`Instance Attributes :`  A variable/data/properties/fields that belongs to a particular object. Attributes can have unique values for each instance.  

Bag1: {colour: blue, weight: 2kg, cost: 1000, capacity: 20L}  
Bag2: {colour: black, weight: 1kg, cost: 500, capacity: 10L}  
Bag3: {colour: green, weight: 3kg, cost: 1500, capacity: 30L}


### Special Methods: 

`__init__()` Method [OR]  `Constuctor`  
A special method used to define the initial state of the object. And this is called automatically when the instace/object is created.  

### self
 self is the default keyword which always reffers to the current instance of the class.
