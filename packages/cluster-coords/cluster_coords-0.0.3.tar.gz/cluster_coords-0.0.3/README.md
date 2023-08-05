# Cluster Coordinates

Given a longitude, and latitude, cluster_coords will create a new latitude and longitude randomly placing it anywhere between 5 and 25 meters from the original longitude and latitude. This is helpful when adding points to a map, you don't want to add a point directly on top of another point, so this module helps you create a cluster.

```python
from cluster_coords import RandomCoord

coords = RandomCoord(<lomgitude>,<latitude>).randomize_coords()
new_lat = coords.lat
new_lng = coords.lng
```

# Installation
```pip install cluster_coords```

```python
[sonnyparlin@localhost cluster_coords]$ python
Python 3.9.1 (default, Jan 20 2021, 00:00:00) 
[GCC 10.2.1 20201125 (Red Hat 10.2.1-9)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from cluster_coords import RandomCoord
>>> coords = RandomCoord(-87,40).randomize_coords()
>>> coords.lng
-86.9997771932092
>>> coords.lat
40.00013474729262
```

Code borrowed from Stack Exchange answer: [here](https://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters), answer by [haakon-d](https://gis.stackexchange.com/users/260/haakon-d).
