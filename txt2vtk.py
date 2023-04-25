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

vtkScalars = vtk.vtkFloatArray()
for y in range(height):
    for x, zCoord in enumerate(f.readline().split()):
        vtkPoints.InsertNextPoint(x, y, float(zCoord) / 50)
        vtkScalars.InsertNextValue(float(zCoord))
f.close()

# En plus de la géométrie, il faut associer un attribut scalaire aux points de la structure qui stocke l'altitude et permettra de la colorier dans l'affichage. Cela se fait via la méthode getPointData() du dataset, qui retourne un vtkPointData dont on utilise la méthode setScalars().




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
