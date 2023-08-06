# Luxtronik

python-luxtronik is a library that allow you to interact with a Luxtronik heatpump controller.

## Examples

**Reading values**

```
from luxtronik import Luxtronik

l = Luxtronik('192.168.1.23', 8889)

t_forerun = l.calculations.get("ID_WEB_Temperatur_TVL")

# alternatively get by id:

t_forerun = l.calculations.get(10)

print(t_forerun) # this returns the temperature value of the forerun, 22.7 for example
print(t_forerun.unit) # gives you the unit of the value if known, °C for example

# l.calculations holds measurement values
# check https://github.com/Bouni/luxtronik/blob/master/luxtronik/calculations.py for values you might need

# l.parameters holds parameter values
# check https://github.com/Bouni/luxtronik/blob/master/luxtronik/parameters.py for values you might need

# l.visibilitys holds visibility values, the function of visibilities is not clear at this point
check https://github.com/Bouni/luxtronik/blob/master/luxtronik/visibilities.py for values you might need


```

**Writing values**

```
from luxtronik import Luxtronik

l = Luxtronik('192.168.1.23', 8889)

heating_mode = l.parameters.set("ID_Ba_Hz_akt", "Party")
l.write()

# If you're not sure what values to write, you can get all options:

print(l.parameters.get("ID_Ba_Hz_akt").options) # returns a list of possible values to write, ['Automatic', 'Second heatsource', 'Party', 'Holidays', 'Off'] for example

```

By default a safeguard is enabled that prevents writing of parameters whose purpose is unknown.
You can disable that safeguard by passing `safe=False` to the Luxtronik class.

```
from luxtronik import Luxtronik

l = Luxtronik('192.168.1.23', 8889, safe=False)

```
