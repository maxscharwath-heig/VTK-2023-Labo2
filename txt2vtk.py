import vtk
import sys
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

for y in range(height):
    for x, zCoord in enumerate(f.readline().split()):
        vtkPoints.InsertNextPoint(x, y, int(zCoord))
f.close()

vtkStructuredGrid = vtk.vtkStructuredGrid()
vtkStructuredGrid.SetDimensions(width, height, 1)
vtkStructuredGrid.SetPoints(vtkPoints)
vtkStructuredGrid.Modified()

print("Writing file: " + destFile)
writer = vtk.vtkStructuredGridWriter()
writer.SetFileName(destFile)
writer.SetInputData(vtkStructuredGrid)
writer.Write()

print("Done, Have a nice day! XoXo :D")




