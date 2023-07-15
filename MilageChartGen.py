try:
    import gpxpy
    import gpxpy.gpx
except ModuleNotFoundError:
    print("Module Error\n")
    input("Press ENTER to quit")
    exit()
    
"""
gpxfile = f'{input("Input GPX filename: ")}.gpx'
mode = input("Course Mode (wpt,trk): ")
outmd = input("Output Type (txt,csv): ")
output = f'{input("Output TXT filename: ")}.{outmd}'
gpx_file = open(gpxfile, 'r')
"""

gpxfile = "JOSM Tracks/PicturedRocksGPX_ELE_AllCampsDet.gpx"

gpx_file = open(gpxfile, 'r')
gpx = gpxpy.parse(gpx_file)


def findSourceSegment(source, legs):
    hits = []
    for segment in legs:
        if source == legs[segment][0].name:
            hits.append(segment)
    return hits


def findNextSegments(srcSegment, legs):
    hits = []
    srcSegmentEnd = [legs[srcSegment][-1].latitude,legs[srcSegment][-1].longitude]
    for segment in legs:
        if srcSegmentEnd == [legs[segment][0].latitude,legs[segment][0].longitude]:
            if legs[srcSegment] == list(reversed(legs[segment])):
                pass
            else:
                hits.append(segment)
    return hits


def checkForEnd(destination, legs, checkSegment):
    for segment in legs:
        if destination == legs[checkSegment][-1].name:
            if [legs[segment][0].latitude,legs[segment][0].longitude] \
                == [legs[checkSegment][0].latitude,legs[checkSegment][0].longitude]:
                    return True
    return False


legs = {}
pois = {}

for track in gpx.tracks:
    points = []
    seg_count = 0
    for segment in track.segments:
        legs[f'{track.name} Seg {seg_count}'] = segment.points
        legs[f'{track.name} Seg {seg_count} Rev'] = list(reversed(segment.points))
        seg_count += 1
        for point in segment.points:
            if point.name is not None and point.name not in pois:
                pois[point.name] = point
                pois[point.name]
    

def pathfind(frompoi, topoi):
    routes = {}
    success = []
    dead = []
    startSegments = findSourceSegment(frompoi, legs)
    for i in range(len(startSegments)):
        routes[i] = [startSegments[i]]
        if checkForEnd(topoi, legs, routes[i][0]):
            success.append(i)
            
    for i in range(int(len(legs))):
        if len(routes) > len(legs)*2:
            break
        for i in range(len(routes)):
            if len(routes)-1 < i:
                break
            if list(routes.keys())[i] not in success or \
            list(routes.keys())[i] not in dead:
                currentRoute = routes[list(routes.keys())[i]][:]
                previousSegment = routes[list(routes.keys())[i]][-1]
                nextSegment = findNextSegments(previousSegment, legs)
                if len(nextSegment) == 0:
                    dead.append(list(routes.keys())[i])
                else:
                    for j in range(len(nextSegment)):
                        newRoute = currentRoute[:]
                        newRoute.append(nextSegment[j])
                        routes[f'{list(routes.keys())[i]}{j}'] = newRoute[:]
                        if checkForEnd(topoi, legs, nextSegment[j]):
                            success.append(f'{list(routes.keys())[i]}{j}')
                        else:
                            pass
                    if  list(routes.keys())[i] not in success:
                        routes.pop(list(routes.keys())[i], None)
                        
    solutions = {}
    pathnum = 0
    for path in success:
        solutions[pathnum] = []
        for step in routes[path]:
            solutions[pathnum].append(step)
        pathnum += 1
    distances = []
    for path in solutions:
        distance = 0
        for step in solutions[path]:
            for track in gpx.tracks:
                if f'{track.name} ' in step:
                    distance += track.length_2d()/1609.344

        distances.append(distance)


    print(f'Dist: {min(distances)} miles \n {solutions[distances.index(min(distances))]}')
                    
                    
pathfind("Munising Falls Visitor Center", "Woodland Park Campground")

"""
pathnum = 0            
for path in success:
    pathnum += 1
    stepcount = 0
    print(f'Solution {pathnum}')
    for step in routes[path]:
        stepcount += 1
        print(f'{stepcount}. {step}')
    print("\n")
        """