try:
    import math
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


def pathfind(frompoi, topoi):
    if frompoi == topoi:
        return {'Distance': 0, 'Path': None} 
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
                        if nextSegment[j] in routes[list(routes.keys())[i]]:
                            break
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
                    distance += track.length_3d()/1609.344

        distances.append(distance)
        
    return {'Distance': min(distances), 
            'Path': solutions[distances.index(min(distances))]}
   

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

unsortedPoiNames = []
unsortedPoiLocs = []
for poi in pois:
    unsortedPoiNames.append(pois[poi].name)
    unsortedPoiLocs.append(pois[poi].longitude)

sortedPoiLocs = sorted(unsortedPoiLocs)
sortedPoiNames = []
for locs in sortedPoiLocs:
    sortedPoiNames.append(unsortedPoiNames[unsortedPoiLocs.index(locs)])

print("Writing to file...")
totalToDo = len(pois) ** 2
totalDone = 0
with open("MilageChart.csv", "w") as csv:
    topline = ["",]
    for frompoi in sortedPoiNames:
        topline.append(frompoi)
    for cell in topline:
        csv.write(f'{cell},')
    csv.write("\n")
    for frompoi in sortedPoiNames:
        csv.write(f'{frompoi},')
        timemode = 0
        for topoi in sortedPoiNames:
            distance = pathfind(frompoi, topoi)["Distance"]
            if timemode == 0:
                if distance == 0:
                    timemode = 1
                csv.write(f'{distance},')
                
            else:
                # time = distance / speed
                # speed is affected by 2.5% per degree in slope
                avgSpeed = 2.5  #mph
                elevationChange = (pois[topoi].elevation - pois[frompoi].elevation)/1609.344
                slope = math.degrees(math.atan2(elevationChange,distance))
                percentChange = 2.5 * slope
                newSpeed = ((avgSpeed*percentChange)/100)+avgSpeed
                time = distance / newSpeed
                csv.write(f'{time},')
                
            totalDone += 1
            print(f'[{"█"*int(((totalDone/totalToDo)*10))}{"-"*int((10-((totalDone/totalToDo)*10)))}] {(totalDone/totalToDo)*100:.02f}%   ', end="\r")
        csv.write("\n")
        
        
    print("[██████████] Done!        ")