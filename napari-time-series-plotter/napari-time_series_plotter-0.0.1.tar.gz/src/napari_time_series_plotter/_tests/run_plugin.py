import napari
from src.napari_time_series_plotter._dock_widget import *

viewer = napari.Viewer()
layerselector = LayerSelector(viewer)
plotter = VoxelPlotter(viewer)
viewer.window.add_dock_widget(plotter, name='Voxel Plotter', area='right')
viewer.window.add_dock_widget(layerselector, name='Layer Selector', area='right')

test_arr1 = np.random.randint(500, size=(10, 10, 10, 10, 10))
test_arr2 = np.random.randint(1000, size=(100, 10, 130, 140))
test_arr3 = np.random.randint(1000, 2000, size=(100, 40, 60))
test_arr4 = np.random.randint(-1000, 0, size=(100, 100))

viewer.add_image(test_arr1, name='5D')
viewer.add_image(test_arr2, name='4D')
viewer.add_image(test_arr3, name='3D')
viewer.add_image(test_arr4, name='2D')

napari.run()
