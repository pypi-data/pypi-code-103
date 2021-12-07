from timewarpy import datasets


def test_load_energy_data():
    assert datasets.load_energy_data().shape == (19735, 29)
