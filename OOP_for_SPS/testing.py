import shapely
from shapely import LineString, Point, Polygon
from Obstacles import Obstacles
point = Point(0, 0)
#print(shapely.distance(Point(10, 0), point))
#print(shapely.distance(LineString([(1, 1), (1, -1)]), point))
#print(shapely.distance(Polygon([(3, 0), (5, 0), (5, 5), (3, 5), (3, 0)]), point))
#print(shapely.distance(Point(), point))
#print(shapely.distance(None, point))


locationTx=[0.0,262]
locationRx=[746,1106]
obstacles = Obstacles()
print(obstacles.getObsaclesLossess(locationTx,locationRx))