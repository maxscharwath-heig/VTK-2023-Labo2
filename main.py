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
INTERACTIVE_LEVEL_SEA = 0
RADIUS_EARTH = 6371009.0

CENTER_LAT = 46.25
CENTER_LON = 6.25

VTK_DATASET = "altitudes.vtk"

CAMERA_DISTANCE = 300000

colors = {
    'lake': [0.25, 0.41, 0.88],
    'ground': [0.0, 0.6, 0.27],
    'hills': [0.94, 0.85, 0.72],
    'mountains': [0.8, 0.8, 0.8],
    'peaks': [1.0, 1.0, 1.0],
    'earth': [0.0, 0.5, 1.0],
    'background': [0.0, 0.0, 0.2]
}


def spherical_to_cartesian(radius: float, latitude: float, longitude: float):
    radians = [math.radians(latitude), math.radians(longitude)]

    x = radius * math.sin(radians[0]) * math.sin(radians[1])
    y = radius * math.cos(radians[0])
    z = radius * math.sin(radians[0]) * math.cos(radians[1])
    return x, y, z


def read_structured_grid(filename):
    reader = vtk.vtkStructuredGridReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()


def create_lut(range, sea_level=0):
    lut = vtk.vtkColorTransferFunction()
    lut.AddRGBPoint(0, *colors["lake"])
    lut.AddRGBPoint(sea_level, *colors["lake"])
    lut.AddRGBPoint(sea_level + 1, *colors["ground"])
    lut.AddRGBPoint(900, *colors["hills"])
    lut.AddRGBPoint(2000, *colors["mountains"])
    lut.AddRGBPoint(3000, *colors["peaks"])
    lut.SetRange(range)
    lut.Build()
    return lut


def print_image(ren_window, filename):
    image_filter = vtk.vtkWindowToImageFilter()
    image_filter.SetInput(ren_window)
    image_filter.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(filename)
    writer.SetInputData(image_filter.GetOutput())
    writer.Write()


def load_texture(filename: str):
    reader_factory = vtk.vtkImageReader2Factory()
    texture_file = reader_factory.CreateImageReader2(filename)
    texture_file.SetFileName(filename)
    texture_file.Update()

    texture = vtk.vtkTexture()
    texture.SetInputConnection(texture_file.GetOutputPort())
    texture.InterpolateOn()
    texture.Update()

    return texture


def generate_render(data, lut, earth_texture):
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(data)
    mapper.SetLookupTable(lut)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    earth_sphere = vtk.vtkTexturedSphereSource()
    earth_sphere.SetRadius(RADIUS_EARTH)
    earth_sphere.SetThetaResolution(100)
    earth_sphere.SetPhiResolution(100)

    earth_mapper = vtk.vtkPolyDataMapper()
    earth_mapper.SetInputConnection(earth_sphere.GetOutputPort())

    earth_actor = vtk.vtkActor()
    earth_actor.SetOrientation(0, 87.1, 90)
    earth_actor.SetOrigin(0, 0, 0)
    earth_actor.SetMapper(earth_mapper)
    earth_actor.SetTexture(earth_texture)
    earth_actor.GetProperty().SetSpecular(0.5)
    earth_actor.GetProperty().SetSpecularPower(50)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.AddActor(earth_actor)
    renderer.SetBackground(colors["background"])

    camera = renderer.GetActiveCamera()
    camera.SetPosition(spherical_to_cartesian(
        RADIUS_EARTH + CAMERA_DISTANCE, CENTER_LAT, CENTER_LON))

    camera.SetFocalPoint(spherical_to_cartesian(
        RADIUS_EARTH, CENTER_LAT, CENTER_LON))

    camera.SetViewUp(0, 0, -1)

    renderer_window = vtk.vtkRenderWindow()
    renderer_window.SetSize(1000, 1200)
    renderer_window.AddRenderer(renderer)
    renderer_window.SetWindowName('VTK - Labo 2')

    renderer.ResetCameraClippingRange()

    return renderer_window


class TimerCallback(vtk.vtkCommand):
    def __init__(self, actor, renderer_window):
        self.actor = actor
        self.renderer_window = renderer_window

    def Execute(self, caller, event, calldata):
        self.actor.RotateZ(0.1)  # Adjust the rotation speed here
        self.renderer_window.Render()


def main():
    output = read_structured_grid(VTK_DATASET)
    altitudes_range = output.GetPointData().GetScalars().GetRange()

    apocalypse_level = 370.0
    lut = create_lut(altitudes_range, apocalypse_level)
    earth_texture = load_texture("./assets/8k_earth_daymap.png")
    renderer_window = generate_render(output, lut, earth_texture)
    print_image(renderer_window, "output_level_370.png")

    lut = create_lut(altitudes_range, INTERACTIVE_LEVEL_SEA)
    renderer_window = generate_render(output, lut, earth_texture)
    print_image(renderer_window, "output_level_standard.png")

    screen_size = renderer_window.GetScreenSize()
    window_size = renderer_window.GetSize()
    renderer_window.SetPosition(
        int((screen_size[0] - window_size[0]) / 2),
        int((screen_size[1] - window_size[1]) / 2)
    )

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
    interactor.SetRenderWindow(renderer_window)
    renderer_window.Render()
    interactor.Initialize()
    interactor.Start()


if __name__ == '__main__':
    main()
