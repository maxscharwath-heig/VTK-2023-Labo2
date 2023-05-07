# VTK - Labo 2
# Nicolas Crausaz & Maxime Scharwath
# Program reading a .txt file containing altitudes and converting it to a .vtk file
# as a structured grid

import vtk
import sys
import constants as cst
import helpers as hlp

# How to use: python txt2vtk.py input.txt output.vtk


def main():
    # Input file should be specified as the first argument
    if len(sys.argv) == 1:
        print("ERROR: No input file specified")
        return

    sourceFile = sys.argv[1]
    if not sourceFile.endswith(".txt"):
        print("ERROR: Input file must be a .txt file")
        return

    # If no output file is specified, use "output.vtk"
    destFile = sys.argv[2] if len(sys.argv) > 2 else "output.vtk"

    print("Reading file: " + sourceFile)
    f = open(sourceFile, "r")

    # Read the header information
    height, width = [int(x) for x in f.readline().split()]

    print("Height: " + str(height))
    print("Width: " + str(width))

    vtkPoints = vtk.vtkPoints()
    vtkScalars = vtk.vtkFloatArray()

    delta_lat_degrees = (cst.MAX_LAT - cst.MIN_LAT) / (height - 1)
    delta_lon_degrees = (cst.MAX_LON - cst.MIN_LON) / (width - 1)

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

            lat = cst.MIN_LAT + y * delta_lat_degrees
            lon = cst.MIN_LON + x * delta_lon_degrees

            x, y, z = hlp.spherical_to_cartesian(
                cst.RADIUS_EARTH + z, lat, lon)

            vtkPoints.InsertNextPoint(x, y, z)

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


if __name__ == '__main__':
    main()
