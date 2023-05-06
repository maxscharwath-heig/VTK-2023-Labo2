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


def is_lake(points, x, y, threshold=1e-6, neighbor_range=2):
    z = points[y][x][2]

    neighbor_count = 0
    total_height = 0

    for i in range(-neighbor_range, neighbor_range + 1):
        for j in range(-neighbor_range, neighbor_range + 1):
            if i == 0 and j == 0:
                continue

            nx, ny = x + i, y + j

            if 0 <= nx < width and 0 <= ny < height:
                neighbor_count += 1
                total_height += points[ny][nx][2]

    average_height = total_height / neighbor_count

    return abs(z - average_height) <= threshold


maxAltitude = 0

points = []

for y in range(height):
    points.append([])
    for x, z in enumerate(f.readline().split()):
        points[y].append((x, y, float(z)))

for line in points:
    for x, y, z in line:
        maxAltitude = max(maxAltitude, z)
        vtkScalars.InsertNextValue(z if not is_lake(points, x, y) else 0)

        lat = min_lat + y * delta_lat_degrees
        lon = min_lon + x * delta_lon_degrees
        lat_rad = lat * DEG_TO_RAD
        lon_rad = lon * DEG_TO_RAD
        radius = RADIUS_EARTH + z
        x_coord = radius * math.cos(lat_rad) * math.sin(lon_rad)
        y_coord = radius * math.cos(lat_rad) * math.cos(lon_rad)
        z_coord = radius * math.sin(lat_rad)

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
