# RouteUtils

This python library define some useful functions to work with geo routes and coordinates.

## Prerequisites :heavy_check_mark:

* [Python3](https://www.python.org/download/releases/3.0/)


## Installing :zap:

    pip install routeutils

## Functions

##### isPointOnRoute
Calculates whether a point is within a route considering a margin between the point and the route.

The route must be a list of lists, in the GeoJson format, [longitude, latitude],
    ex: \[[-24.234123, -50.123321], [-24.234123, -50.123321], [-24.234123, -50.123321]].

<strong>latitude</strong>: latitude of the testing point.

<strong>longitude</strong>: longitude of the testing point.

<strong>route</strong>: the route being tested.

<strong>margin</strong>: The margin, in meters, to be considered between the point and the route
    to decide if the point is within the route (usually related to GPS inaccuracy). Default value 10 meters.
    
<strong>return</strong>: true if the point is within the route considering the given margin, otherwise false.

###### Example of usage :rocket:

    from routeutils import routeanalyser

    latitude = -30.033233564203634
    longitude = -51.21691256761551

    route = [
          [
            -51.22019290924072,
            -30.03246262969342
          ],
          ...
          [
            -51.21572434902191,
            -30.033475060527536
          ]
        ]
        
    margin = 10

    isInsideRoute = routeanalyser.isPointInsideRoute(latitude=latitude,
                                                    longitude=longitude,
                                                    route=route,
                                                    margin=margin)

## Credits

Developed at [ Techlab Klabin ](https://techlab.klabin.com.br/)