## Encapsulation : 
The process of Wrapping/Bundling of data and methods into a single unit/package/capsule as class know as Encapsulation  

![](https://scaler.com/topics/images/what-is-encapsulation-in-python-1024x400.webp)

### Why ? 
1. To restrict the access by following the principle of data hiding.
2. Data integrity  --> validate data before it is set, ensuring the object maintains a valid state.
3. Changing the data in the class will not effet the other elements/data outside the class.

### Access Modifiers : 
These are the keywords that determines the accessibility and visibility of class members(methods, data)  
There are 3 types of access modifiers : 

`1.Public:` 
    
    Most accessible  
    Can be accessed from anywhere  
    No encapsulation    

`2._Protected:`  

    Less accessible than public
    Can be accessed within class and derived classes
    Moderate encapsulation

`3.__Private:`  

    Least accessible
    Only accessible within class
    Maximum encapsulation  

![](https://pynative.com/wp-content/uploads/2021/08/python_data_hiding.jpg)


### Access Methods :

`1. Getter Methods:`

- Accessor methods r used 2 retrieve the value of an `instance private variable`.
- Follow the naming convention: getVariableName() or get_variable_name()



`2. Setter Methods:`

- Mutator methods that modify the value of an `instance private variable`
- Follow the naming convention: setVariableName() or set_variable_name()


