try:
    import math
    import gpxpy
    import gpxpy.gpx
except ModuleNotFoundError:
    print("Module Error\n")
    input("Press ENTER to quit")
    exit()


def lineBtwCoords(lat1: float,long1: float,lat2: float,long2: float) -> list:
    """Calculates the Distance and Compass Bearing between two Geo-Coordinates

    Args:
        lat1 (float): Latitude of point 1
        long1 (float): Longitude of point 1
        lat2 (float): Latitude of point 2
        long2 (float):Longitude of point 2

    Returns:
        list: [Distance in feet, Bearing in degrees]
    """    
    lat1 = math.radians(lat1)
    long1 = math.radians(long1)
    lat2 = math.radians(lat2)
    long2 = math.radians(long2)

    latDiff = abs(lat1 - lat2)
    longDiff = (abs(long2 - long1))

    # Bearing
    X = math.sin(long2 - long1) * math.cos(lat2)
    Y = (
        math.cos(lat1) 
         * math.sin(lat2) 
         - math.sin(lat1) 
         * math.cos(lat2) 
         * math.cos(long2 - long1)
         )
    B = math.atan2(X, Y)
    bearing = int(round(((B * 180 / float(math.pi) + 360) % 360), 0))

    # Distance
    a = (
        ((math.sin(latDiff/2))**2) 
         + math.cos(lat1)
         * math.cos(lat2)
         * ((math.sin(longDiff / 2)) ** 2)
         )
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = 20902259.664*c

    distance = int(round(d, 0))
    
    return distance, bearing


gpxfile = f'{input("Input GPX filename: ")}.gpx'
mode = input("Course Mode (wpt,trk): ")
outmd = input("Output Type (txt,csv): ")
output = f'{input("Output TXT filename: ")}.{outmd}'
gpx_file = open(gpxfile, 'r')

gpx = gpxpy.parse(gpx_file)

if mode == "wpt":
    name = []
    lat = []
    long = []

    for waypoint in gpx.waypoints:
        name.append(waypoint.name)
        lat.append(waypoint.latitude)
        long.append(waypoint.longitude)

    if len(lat) != len(long):
        print("File Error: Latitude count does not equal Longitude count")
        input("\nPress ENTER to exit... ")
        exit()
    else:
        pass

    points = len(lat)

    try:
        file = open(output, "x")
        print(f"Creating File {output}.txt...")
    except FileExistsError:
        file = open(output, "w")
        print(f"Could not create {output}.txt: File Already Exists... Overwriting...")

    for i in range(points-1):
        
        distance, bearing = lineBtwCoords(lat[i],long[i],lat[i+1],long[i+1])
        
        print(f"{i+1}. {distance}' at {bearing}°")
        
        if name[i] is None:
            file.write(f"{i+1}. {distance}' at {bearing}°\n")
        else:
            file.write(f"At {name[i]}\n{i+1}. {distance}' at {bearing}°\n")
elif mode == "trk":
    
    txt_lines = []
    
    

    for track in gpx.tracks:
        if outmd == "txt":
            txt_lines.append(f'{track.name}: {((track.length_3d())/1609.34):.02f} mi\n')
        elif outmd == "csv":
            txt_lines.append(f'{track.name},{((track.length_3d())/1609.34):.02f} mi\n')
        name = []
        comment = []
        lat = []
        long = []
        for segment in track.segments:
            for point in segment.points:
                name.append(point.name)
                comment.append(point.comment)
                lat.append(point.latitude)
                long.append(point.longitude)
        

        if len(lat) != len(long):
            print("File Error: Latitude count does not equal Longitude count")
            input("\nPress ENTER to exit... ")
            exit()
        else:
            pass

        points = len(lat)
        
        for i in range(points-1):
        
            distance, bearing = lineBtwCoords(lat[i],long[i],lat[i+1],long[i+1])
            
            #print(f"{i+1}. {distance}' at {bearing}°")
            
            fromtxt = ""
            totxt = ""
            cmttxt = ""
            if name[i] is not None:
                if outmd == "txt":
                    fromtxt = f'From {name[i]}, go '
                elif outmd == "csv":
                    fromtxt = f'{name[i]}'
            if name[i+1] is not None:
                if outmd == "txt":
                    totxt = f' to {name[i+1]}'
                elif outmd == "csv":
                    totxt = f'{name[i+1]}'
            if comment[i] is not None:
                if outmd == "txt":
                    cmttxt = f'\n\t{comment[i]}'
                elif outmd == "csv":
                    cmttxt = f'{comment[i]}'
                    print(cmttxt)
            
            if outmd == "txt":
                txt_lines.append(f'{i+1}. {fromtxt}{distance} ft at {bearing}°{totxt}{cmttxt}\n')
            elif outmd == "csv":
                txt_lines.append(f'{fromtxt},{distance} ft,{bearing}°,{totxt},"{cmttxt}"\n')
            
            
            if i == points-2:
                txt_lines.append("\n\n")

    try:
        file = open(output, "x")
        print(f"Creating File {output}...")
    except FileExistsError:
        file = open(output, "w")
        print(f"Could not create {output}: File Already Exists... Overwriting...")

    for i in range(len(txt_lines)):
        file.write(txt_lines[i])