import vtk
import math

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
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
WATER_LEVEL = 370.0
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


def readStructuredGrid(filename):
    '''
    Reads the structured grid from the file altitudes.vtk
    :return: vtkStructuredGrid
    '''
    reader = vtk.vtkStructuredGridReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()


def createLUT(range):
    lut = vtk.vtkColorTransferFunction()
    lut.AddRGBPoint(0, 0.513, 0.49, 1)  # Lacs
    lut.AddRGBPoint(1, 0.15, 0.32, 0.14) # Plaines  (vert foncé)
    lut.AddRGBPoint(500, 0.219, 0.71, 0.16) # Plaines (vert clair)
    lut.AddRGBPoint(900, 0.88, 0.72, 0.36) # Terrain escarpé (brun)
    lut.AddRGBPoint(2000, 1, 1, 1)  # Sommets (neige)
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


def main():
    output = readStructuredGrid(VTK_DATASET)
    altitudes_range = output.GetPointData().GetScalars().GetRange()
    lut = createLUT(altitudes_range)

    # Create the mapper
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(output)
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(altitudes_range)

    # Create the Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create Earth sphere
    earth_sphere = vtk.vtkSphereSource()
    earth_sphere.SetRadius(RADIUS_EARTH)
    earth_sphere.SetThetaResolution(100)
    earth_sphere.SetPhiResolution(100)

    # Create Earth sphere mapper
    earth_mapper = vtk.vtkPolyDataMapper()
    earth_mapper.SetInputConnection(earth_sphere.GetOutputPort())

    # Create Earth sphere actor
    earth_actor = vtk.vtkActor()
    earth_actor.SetMapper(earth_mapper)
    earth_actor.GetProperty().SetColor(0.0, 0.5, 1.0)
    earth_actor.GetProperty().SetOpacity(0.5)  # Set Earth opacity

    # Calculate the camera's center of rotation
    center_lat_rad = math.radians(CENTER_LAT)
    center_lon_rad = math.radians(CENTER_LON)

    x_center = RADIUS_EARTH * \
        math.cos(center_lat_rad) * math.sin(center_lon_rad)
    y_center = RADIUS_EARTH * \
        math.cos(center_lat_rad) * math.cos(center_lon_rad)
    z_center = RADIUS_EARTH * math.sin(center_lat_rad)

    # Create the Renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.AddActor(earth_actor)  # Add Earth sphere actor to the renderer
    renderer.SetBackground(0.96, 0.87, 0.70)

    # Set the camera's position, focal point, and view up direction
    camera = renderer.GetActiveCamera()
    camera.SetPosition(x_center, y_center, z_center + RADIUS_EARTH / 2)
    camera.SetFocalPoint(x_center, y_center, z_center)
    camera.SetViewUp(0, 1, 0)

    # Create the RendererWindow
    renderer_window = vtk.vtkRenderWindow()
    renderer_window.SetSize(1000, 1000)
    renderer_window.AddRenderer(renderer)
    renderer_window.SetWindowName('VTK - Labo 2')

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

    renderer.ResetCameraClippingRange()
    renderer_window.Render()

    printImage(renderer_window, "output_level_standard.png")

    printImage(renderer_window, "output_level_370.png")  # TODO

    interactor.Initialize()
    interactor.Start()


if __name__ == '__main__':
    main()
