import vtk
import sys
import math

# How to use: python txt2vtk.py input.txt output.vtk

sourceFile = sys.argv[1]
destFile = sys.argv[2] if len(sys.argv) > 2 else "output.vtk"

print("Reading file: " + sourceFile)
f = open(sourceFile, "r")

# Read the header information
height, width = [int(x) for x in f.readline().split()]

print("Height: " + str(height))
print("Width: " + str(width))

vtkPoints = vtk.vtkPoints()
vtkScalars = vtk.vtkFloatArray()

# Constants for conversion
RADIUS_EARTH = 6371009.0
DEG_TO_RAD = math.pi / 180.0

min_lat, max_lat = 45.0, 47.5
min_lon, max_lon = 5.0, 7.5

delta_lat_degrees = (max_lat - min_lat) / (height - 1)
delta_lon_degrees = (max_lon - min_lon) / (width - 1)

previousAltitudes = []


def findLakeAltitude(altitude, num):
    if len(previousAltitudes) < num:
        previousAltitudes.append(altitude)
        return
    # use pop
    for i in range(num):
        if previousAltitudes.pop(0) != altitude:
            previousAltitudes.append(altitude)
            return
    print("Found lake at altitude: " + str(altitude))

maxAltitude = 0

for y in range(height):
    for x, zCoord in enumerate(f.readline().split()):
        zCoord = float(zCoord)
        # findLakeAltitude(zCoord, 200) # found 370
        maxAltitude = max(maxAltitude, zCoord)  # found 4783
        vtkScalars.InsertNextValue(zCoord)

        # Latitude and Longitude to Cartesian
        lat = min_lat + y * delta_lat_degrees
        lon = min_lon + x * delta_lon_degrees
        lat_rad = lat * DEG_TO_RAD
        lon_rad = lon * DEG_TO_RAD
        x_coord = RADIUS_EARTH * math.cos(lat_rad) * math.cos(lon_rad)
        y_coord = RADIUS_EARTH * math.cos(lat_rad) * math.sin(lon_rad)
        z_coord = (RADIUS_EARTH + zCoord) * math.sin(lat_rad)

        vtkPoints.InsertNextPoint(x_coord, y_coord, z_coord)

f.close()
print("Max altitude: " + str(maxAltitude))

vtkStructuredGrid = vtk.vtkStructuredGrid()
vtkStructuredGrid.SetDimensions(width, height, 1)
vtkStructuredGrid.SetPoints(vtkPoints)
vtkStructuredGrid.GetPointData().SetScalars(vtkScalars)
vtkStructuredGrid.Modified()

print("Writing file: " + destFile)
writer = vtk.vtkStructuredGridWriter()
writer.SetFileName(destFile)
writer.SetInputData(vtkStructuredGrid)
writer.Write()

print("Done, Have a nice day! XoXo :D")
