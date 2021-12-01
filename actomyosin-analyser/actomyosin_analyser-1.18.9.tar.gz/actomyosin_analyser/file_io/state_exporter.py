import os.path

import numpy as np

from actomyosin_analyser.analysis.abstract_analyser import AbstractAnalyser


class StateExporter:

    def __init__(self, analyser: AbstractAnalyser):
        self.analyser = analyser
        self._blob_root = os.path.join(self.analyser.blob_root, 'state')

    def export(self, frame: int):
        output_dir = os.path.join(self._blob_root, f'frame_{frame}')
        os.makedirs(output_dir, exist_ok=True)
        self._export_non_filament(output_dir, frame)
        self._export_filaments(output_dir, frame)
        self._export_links(output_dir, frame)

    def _export_non_filament(
            self,
            output_dir: str,
            frame: int
    ):
        coords = self.analyser.get_trajectories_non_filament(minimum_image=True)[frame]
        np.save(os.path.join(output_dir, 'coordinates_non_filament_particles.npy'), coords)

    def _export_filaments(self, output_dir: str, frame: int):
        coords = self.analyser.get_positions_of_filaments_at_frames([frame], minimum_image=True)[0]
        np.save(os.path.join(output_dir, 'coordinates_filaments.npy'), coords)

    def _export_links(self, output_dir: str, frame: int):
        links = self.analyser.get_links(frame)
        np.save(os.path.join(output_dir, 'links.npy'), links)
