# Astro Charts SVG

astro_svg is a chart generator based on Kerykeion and Opeanstro.
Like the titles says it prints out SVG file of the chart,
it's very easy to use.

```python
# Install:
>>> pip3 install astro_svg

#Import:
>>> import astrochart_svg as as

# Make the instance:
>>> kanye = as.MakeInstance("Kanye", 1977, 6, 8, 8, 45, "Atlanta", type="Natal")

# Set the output directory for the SVG:
>>> kanye.output_directory = "/Users/{YourName}"

#Generate the SVG:
>>> kanye.makeSVG()


SVG generated successfully!
```

![alt text](https://raw.githubusercontent.com/g-battaglia/birthchartSVG/master/birthchartSVG/template/sample.svg)

```python

>>> first = kr.Calculator("Jack", 1990, 6, 15, 13, 00, "Montichiari")
>>> second = kr.Calculator("Jane", 1991, 6, 11, 21, 00, "Cremona")

 >>> name = MakeInstance(first, chart_type="Transit", second_obj=second)
 >>> name.makeSVG()

```
![alt text](https://raw.githubusercontent.com/g-battaglia/astrochart_SVG/master/sample.svg)


## Documentation

Just like in the exemple, first make an instance and then use the makeSVG() to generate the SVG chart.
The file generated has the name you inserted followed by Chart.svg

## Installation

BirtchartSVG is Python 3 package, make sure you have Python 3 installed on your system.

## Development

You can clone this repository or download a zip file using the right side buttons.
