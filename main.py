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


def readStructuredGrid():
    reader = vtk.vtkStructuredGridReader()
    reader.SetFileName("altitudes.vtk")
    reader.Update()
    return reader.GetOutput()


def createLUT():
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfColors(256)
    lut.SetHueRange(0.0, 0.667)
    lut.SetSaturationRange(1.0, 1.0)  # Définir la plage de saturation
    lut.SetValueRange(0.2, 1.0)  # Définir la plage de valeur
    lut.SetAlphaRange(1.0, 1.0)
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
