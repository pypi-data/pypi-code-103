import pathlib
import tempfile

import pytest

from rebotics_sdk.advanced.packers import ClassificationDatabasePacker, ZipDatabasePacker, \
    DuplicateFeatureVectorsException, VirtualClassificationDatabasePacker, VirtualClassificationEntry


@pytest.fixture(scope="module")
def script_cwd(request):
    return request.fspath.join("..")


def test_classification_packing(script_cwd):
    db_folder = pathlib.Path(script_cwd.join("db"))
    with tempfile.TemporaryDirectory() as dirname:
        destination_filename = pathlib.Path(dirname, 'test')
        packer = ClassificationDatabasePacker(destination=destination_filename)
        features = db_folder / 'features.txt'
        labels = db_folder / 'labels.txt'
        images_folder = db_folder / 'custom_folder/'

        res = packer.pack(labels, features, images_folder)

        assert 'test.rcdb' in res
        assert len(packer.images) == 2

        packer = ClassificationDatabasePacker(source=res)
        entries = list(packer.unpack())
        assert len(entries) == 2
        entry = entries[0]
        assert entry.label == '123123123'
        assert entry.feature == '123123123123123'
        internal_filename = entry.filename
        assert internal_filename == 'image_1.png'

        # testing if it can be dumped to the FS
        og_file = images_folder / internal_filename
        tmp_file = db_folder / internal_filename

        with open(tmp_file, 'wb') as fout:
            fout.write(entry.image)

        assert og_file.stat().st_size == tmp_file.stat().st_size
        tmp_file.unlink()


def test_classification_packing_check_duplicates(script_cwd):
    db_folder = pathlib.Path(script_cwd.join("db"))
    packer = ClassificationDatabasePacker(destination='test', check_duplicates=True)
    features = db_folder / 'features.txt'
    labels = db_folder / 'labels.txt'
    images_folder = db_folder / 'custom_folder/'

    with pytest.raises(DuplicateFeatureVectorsException) as excinfo:
        packer.pack(labels, features, images_folder)
    assert "duplicate" in str(excinfo.value)


def test_zip_packing():
    packer = ZipDatabasePacker()
    packed = packer.pack(
        labels=[
            '123123123'
        ],
        features=[
            '123123123123123'
        ]
    )
    assert packer.meta_data['count'] == 1

    unpacker = ZipDatabasePacker(source=packed)
    for entry in unpacker.unpack():
        assert entry.label == '123123123'
        assert entry.feature == '123123123123123'

    assert unpacker.meta_data['count'] == 1


def test_virtual_packing():
    packer = VirtualClassificationDatabasePacker()
    packed = packer.pack([
        VirtualClassificationEntry(
            label='{}'.format(i),
            feature='{}'.format(i) * 5,
            image_url='https://example.com/image_{}.jpeg'.format(i)
        ) for i in range(100)
    ])
    assert packer.meta_data['count'] == 100
    assert len(packer.meta_data['batches']) == 1

    unpacker = VirtualClassificationDatabasePacker(source=packed)
    assert unpacker.meta_data['count'] == 100
    for i, entry in enumerate(unpacker.unpack()):
        if i == 0:
            first_entry = entry
            assert first_entry.label == '0'
            assert first_entry.feature == '00000'
            assert first_entry.index == 1
            assert first_entry.image_url == 'https://example.com/image_0.jpeg'
            break
