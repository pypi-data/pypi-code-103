from timewarpy import datasets, preprocess


def test_load_energy_data():
    df = datasets.load_energy_data()
    X, y = preprocess.create_univariate_windows(df, 1680, 240, 'Appliances')
    assert X.shape == (17816, 1680, 1)
