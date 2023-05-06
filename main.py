import vtk
import math

import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkWindowToImageFilter
)

from vtkmodules.vtkIOImage import (
    vtkPNGWriter,
)

# Constants
# Define the wished sea level when using the interactive window
INTERACTIVE_LEVEL_SEA = 0
RADIUS_EARTH = 6371009.0

# Latitude of zone to display
LAT_MIN = 45
LAT_MAX = 47.5

# Longitude of zone to display
LON_MIN = 5
LON_MAX = 7.5

CENTER_LAT = (LAT_MIN + LAT_MAX) / 2
CENTER_LON = (LON_MIN + LON_MAX) / 2

VTK_DATASET = "altitudes.vtk"

CAMERA_DISTANCE = 300000

# colors
colors = {
    'lake': [0.25, 0.41, 0.88],
    'ground': [0.0, 0.6, 0.27],
    'hills': [0.94, 0.85, 0.72],
    'mountains': [0.8, 0.8, 0.8],
    'peaks': [1.0, 1.0, 1.0],
    'earth': [0.0, 0.5, 1.0],
    'background': [0.96, 0.87, 0.70],
}


def spherical_to_cartesian(radius: float, latitude: float, longitude: float):
    '''
    Translate spherical coordinate to cartesian coordinate
    '''
    radians = [math.radians(latitude), math.radians(longitude)]

    x = radius * math.sin(radians[0]) * math.sin(radians[1])
    y = radius * math.cos(radians[0])
    z = radius * math.sin(radians[0]) * math.cos(radians[1])
    return x, y, z


def readStructuredGrid(filename):
    '''
    Reads the structured grid from the file altitudes.vtk
    :return: vtkStructuredGrid
    '''
    reader = vtk.vtkStructuredGridReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()


def createLUT(range, sea_level=0):
    lut = vtk.vtkColorTransferFunction()
    lut.AddRGBPoint(0, *colors["lake"])  # Lacs (bottom)
    lut.AddRGBPoint(sea_level, *colors["lake"])  # Lacs (surface)
    lut.AddRGBPoint(sea_level + 1, *colors["ground"])  # Plaines
    lut.AddRGBPoint(900, *colors["hills"])  # Terrain escarpé (brun)
    lut.AddRGBPoint(2000, *colors["mountains"])  # Haute montagne (neige)
    lut.AddRGBPoint(3000, *colors["peaks"])  # Pics, sommets (neige)
    lut.SetRange(range)
    lut.Build()
    return lut


def printImage(ren_window, filename):
    '''
    Prints the image of the vtkRenderWindow in a file with given filename
    :param ren_window: vtkRenderWindow
    :param filename: string
    '''
    image_filter = vtk.vtkWindowToImageFilter()
    image_filter.SetInput(ren_window)
    image_filter.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(filename)
    writer.SetInputData(image_filter.GetOutput())
    writer.Write()


def generateRender(data, lut):
    '''
    Generates a render window from a structured grid and a lookup table
    '''
    # Create the mapper
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(data)
    mapper.SetLookupTable(lut)

    # Create the Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create Earth sphere
    earth_sphere = vtk.vtkSphereSource()
    earth_sphere.SetCenter(0.0, 0.0, 0.0)
    earth_sphere.SetRadius(RADIUS_EARTH)
    earth_sphere.SetThetaResolution(100)
    earth_sphere.SetPhiResolution(100)

    # Create Earth sphere mapper
    earth_mapper = vtk.vtkPolyDataMapper()
    earth_mapper.SetInputConnection(earth_sphere.GetOutputPort())

    # Create Earth sphere actor
    earth_actor = vtk.vtkActor()
    earth_actor.SetMapper(earth_mapper)
    earth_actor.GetProperty().SetColor(colors["earth"])
    earth_actor.GetProperty().SetOpacity(0.9)

    # Create the Renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.AddActor(earth_actor)
    renderer.SetBackground(colors["background"])

    # Calculate & set camera position
    camera = renderer.GetActiveCamera()
    camera.SetPosition(spherical_to_cartesian(
        RADIUS_EARTH + CAMERA_DISTANCE, CENTER_LAT, CENTER_LON))

    camera.SetFocalPoint(spherical_to_cartesian(
        RADIUS_EARTH, CENTER_LAT, CENTER_LON))

    camera.SetViewUp(0, 0, -1)

    # Create the RendererWindow
    renderer_window = vtk.vtkRenderWindow()
    renderer_window.SetSize(1000, 1200)
    renderer_window.AddRenderer(renderer)
    renderer_window.SetWindowName('VTK - Labo 2')

    renderer.ResetCameraClippingRange()

    return renderer_window


def main():
    output = readStructuredGrid(VTK_DATASET)
    altitudes_range = output.GetPointData().GetScalars().GetRange()
    #
    # Render of the sea level at 370m, to an image
    #
    apocalypse_level = 370.0
    lut = createLUT(altitudes_range, apocalypse_level)
    renderer_window = generateRender(output, lut)
    printImage(renderer_window, "output_level_370.png")

    #
    # Render of the standard sea level, to an image and to an interactive window
    #
    lut = createLUT(altitudes_range, INTERACTIVE_LEVEL_SEA)
    renderer_window = generateRender(output, lut)
    printImage(renderer_window, "output_level_standard.png")

    # Center the window on the screen
    screen_size = renderer_window.GetScreenSize()
    window_size = renderer_window.GetSize()
    renderer_window.SetPosition(
        int((screen_size[0] - window_size[0]) / 2),
        int((screen_size[1] - window_size[1]) / 2)
    )

    # Create the RendererWindowInteractor and render the scene
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_window)
    renderer_window.Render()
    interactor.Initialize()
    interactor.Start()


if __name__ == '__main__':
    main()
