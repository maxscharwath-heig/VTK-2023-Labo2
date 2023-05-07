# VTK - Labo 2
# Nicolas Crausaz & Maxime Scharwath
# Main program rendering an topographic map of (a part of) Switzerland

import vtk

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

import constants as cst
import helpers as hlp

# Constants
VTK_DATASET = "altitudes.vtk"

COLORS = {
    'lake': [0.25, 0.41, 0.88],
    'ground': [0.0, 0.6, 0.27],
    'hills': [0.94, 0.85, 0.72],
    'mountains': [0.8, 0.8, 0.8],
    'peaks': [1.0, 1.0, 1.0],
    'earth': [0.0, 0.5, 1.0],
    'background': [0.0, 0.0, 0.2]
}


def read_structured_grid(filename):
    '''
    Read a VTK structured grid from a file
    :param filename: Name of the file to read
    :return: The VTK structured grid
    '''

    reader = vtk.vtkStructuredGridReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()


def create_lut(range, sea_level=0):
    '''
    Create a color lookup table
    :param range: Range of the altitude
    :param sea_level: Altitude of the sea level
    :return: The color lookup table
    '''

    lut = vtk.vtkColorTransferFunction()
    lut.AddRGBPoint(0, *COLORS["lake"])
    lut.AddRGBPoint(sea_level, *COLORS["lake"])
    lut.AddRGBPoint(sea_level + 1, *COLORS["ground"])
    lut.AddRGBPoint(900, *COLORS["hills"])
    lut.AddRGBPoint(2000, *COLORS["mountains"])
    lut.AddRGBPoint(3000, *COLORS["peaks"])
    lut.SetRange(range)
    lut.Build()
    return lut


def print_image(ren_window, filename):
    '''
    Print the content of a VTK render window to a file
    :param ren_window: The VTK render window
    :param filename: The name of the file
    '''
    image_filter = vtk.vtkWindowToImageFilter()
    image_filter.SetInput(ren_window)
    image_filter.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(filename)
    writer.SetInputData(image_filter.GetOutput())
    writer.Write()


def load_texture(filename: str):
    '''
    Load a texture from a file
    :param filename: The name of the file
    :return: The VTK texture
    '''
    reader_factory = vtk.vtkImageReader2Factory()
    texture_file = reader_factory.CreateImageReader2(filename)
    texture_file.SetFileName(filename)
    texture_file.Update()

    texture = vtk.vtkTexture()
    texture.SetInputConnection(texture_file.GetOutputPort())
    texture.InterpolateOn()
    texture.Update()

    return texture


def generate_render(data, lut):
    '''
    Generate a VTK render window
    :param data: The VTK structured grid
    :param lut: The color lookup table
    :return: The VTK render window
    '''
    # Create the mapper and actor for the topographic map
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(data)
    mapper.SetLookupTable(lut)
    topo_map = vtk.vtkActor()
    topo_map.SetMapper(mapper)

    # Create the sphere representing the earth
    earth_sphere = vtk.vtkTexturedSphereSource()
    earth_sphere.SetRadius(cst.RADIUS_EARTH)
    earth_sphere.SetThetaResolution(100)
    earth_sphere.SetPhiResolution(100)

    earth_mapper = vtk.vtkPolyDataMapper()
    earth_mapper.SetInputConnection(earth_sphere.GetOutputPort())

    earth_actor = vtk.vtkActor()
    earth_actor.SetOrientation(0, 87.1, 90)
    earth_actor.SetOrigin(0, 0, 0)
    earth_actor.SetMapper(earth_mapper)
    earth_texture = load_texture("./assets/8k_earth_daymap.png")
    earth_actor.SetTexture(earth_texture)
    earth_actor.GetProperty().SetSpecular(0.5)
    earth_actor.GetProperty().SetSpecularPower(50)

    # Create the renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(topo_map)
    renderer.AddActor(earth_actor)
    renderer.SetBackground(COLORS["background"])

    # Set the camera position and focal
    camera = renderer.GetActiveCamera()
    camera.SetPosition(hlp.spherical_to_cartesian(
        cst.RADIUS_EARTH + cst.CAMERA_DISTANCE, cst.CENTER_LAT, cst.CENTER_LON))

    camera.SetFocalPoint(hlp.spherical_to_cartesian(
        cst.RADIUS_EARTH, cst.CENTER_LAT, cst.CENTER_LON))

    # Create the render window
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

    # Render of the sea level at 370m, to an image
    apocalypse_level = 370.0
    lut = create_lut(altitudes_range, apocalypse_level)
    renderer_window = generate_render(output, lut)
    print_image(renderer_window, "output_level_370.png")

    # Render of the standard sea level, to an image and interactive window
    lut = create_lut(altitudes_range, cst.INTERACTIVE_LEVEL_SEA)
    renderer_window = generate_render(output, lut)
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
