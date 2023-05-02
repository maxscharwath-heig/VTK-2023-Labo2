import vtk

#!/usr/bin/env python

# This simple example shows how to do basic rendering and pipeline
# creation.

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

# constants

waterLevel = 370.0
maxAltitude = 4783.0

def readStructuredGrid():
    reader = vtk.vtkStructuredGridReader()
    reader.SetFileName("altitudes.vtk")
    reader.Update()
    return reader.GetOutput()


def createLUT():
    lut = vtk.vtkColorTransferFunction()

    lut.AddRGBPoint(0, 0.513, 0.49, 1) # Lacs
    lut.AddRGBPoint(1, 0.15, 0.32, 0.14)
    lut.AddRGBPoint(500, 0.219, 0.71, 0.16)
    lut.AddRGBPoint(900, 0.88, 0.72, 0.36)
    lut.AddRGBPoint(1600, 1, 1, 1)
    lut.Build()

    return lut


def main():
    output = readStructuredGrid()
    colors = vtkNamedColors()
    lut = createLUT()

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(output)
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(output.GetPointData().GetScalars().GetRange())

    # Create the Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create the Renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d('Wheat'))

    # Create the RendererWindow
    renderer_window = vtk.vtkRenderWindow()
    renderer_window.SetSize(640, 480)
    renderer_window.AddRenderer(renderer)
    renderer_window.SetWindowName('ReadstructuredGrid')

    # Center the window
    screen_size = renderer_window.GetScreenSize()
    window_size = renderer_window.GetSize()

    renderer_window.SetPosition(
        int((screen_size[0] - window_size[0]) / 2),
        int((screen_size[1] - window_size[1]) / 2)
    )

    # Create the RendererWindowInteractor and display the vtk_file
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_window)
    interactor.Initialize()
    interactor.Start()


if __name__ == '__main__':
    main()
