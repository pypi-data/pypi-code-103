import numpy as np

from shared.external.constants import AnnotationGroups
from shared.external.models.annotation import (BoundingBox, Polygon, Point, Line,
                                               BoundingBoxAnnotation, PolygonAnnotation, PointAnnotation, LineAnnotation,
                                               ClassificationAnnotation, Label)


def test_create_mrcnn_annotation():
    annotation_id = "dd0f5995-ec1d-43fa-bfc8-f8a1f9c7b9fe_frame_0.ann"
    media_asset_id = "dd0f5995-ec1d-43fa-bfc8-f8a1f9c7b9fe_frame_0.png"
    destination_set = None

    annotation = BoundingBoxAnnotation(
        id=annotation_id,
        asset_id=media_asset_id,
        bounding_boxes=[BoundingBox(x_min=448, x_max=485, y_min=467, y_max=487, label='car', confidence=0.99512035)],
        set_id=destination_set,
        annotation_group=AnnotationGroups.MODEL_GENERATED
    )

    assert annotation.id == annotation_id
    assert annotation.annotation_type == 'two_d_bounding_box'
    assert annotation.annotation_group == AnnotationGroups.MODEL_GENERATED
    annotation_dict = annotation.to_dic()
    annotation_entities = annotation_dict['annotation_entities']
    annotation_entities[0].pop("uid")
    assert annotation_entities == \
           [
               {
                   'annotation_type': 'two_d_bounding_box',
                   'attributes': {},
                   'category_id': None,
                   'confidence': 0.99512035,
                   'coordinates': [{'x': 448.0, 'y': 467.0},
                                   {'x': 485.0, 'y': 467.0},
                                   {'x': 485.0, 'y': 487.0},
                                   {'x': 448.0, 'y': 487.0}],
                   'label': 'car',
                   'related_annotations': []
               }
           ]


def test_create_bbox_annotation():
    media_asset_id = "test_bbox_asset_id"

    bboxes = []
    x_min = 10.0
    y_min = 11.0
    for i in range(3):
        bboxes.append(
            BoundingBox(x_min=x_min,
                        y_min=y_min,
                        x_max=x_min + 20 * (i + 1),
                        y_max=y_min + 25 * (i + 1),
                        label="test_label_{}".format(i),
                        confidence=0.7 + 0.1 * i,
                        category_id=i,
                        attributes={"track_id": i}
                        )
        )

    annotation = BoundingBoxAnnotation(
        image_id=media_asset_id,
        bounding_boxes=bboxes,
        provider="my_model",
        annotation_group=AnnotationGroups.MODEL_GENERATED,
        version="my_model_version",
        id="test_bbox_ann_id"

    )

    assert annotation.id == "test_bbox_ann_id"
    assert annotation.asset_id == media_asset_id
    assert annotation.annotation_type == "two_d_bounding_box"
    assert annotation.annotation_group == "false"
    assert annotation.provider == "my_model"
    assert annotation.version == "my_model_version"
    annotation_dict = annotation.to_dic()
    annotation_entities = annotation_dict['annotation_entities']
    assert len(annotation_entities) == 3
    assert annotation_entities[0]["attributes"]["track_id"] == 0


def test_create_point_annotation():
    media_asset_id = "test_point_asset_id"

    points = []
    left = 5.0
    top = 5.0
    for i in range(3):
        points.append(
            Point(
                left=left + 20 * (i + 1),
                top=top + 20 * (i + 1),
                label="test_label_{}".format(i),
                confidence=0.7 + 0.1 * i,
                category_id=i,
                attributes={"geometry": "point.geometry"}
            )
        )

    annotation = PointAnnotation(
        image_id=media_asset_id,
        points=points,
        provider="my_model",
        annotation_group=AnnotationGroups.MODEL_GENERATED,
        version="my_model_version",
        id="test_point_ann_id"

    )

    assert annotation.id == "test_point_ann_id"
    assert annotation.asset_id == media_asset_id
    assert annotation.annotation_type == "point"
    assert annotation.annotation_group == AnnotationGroups.MODEL_GENERATED
    assert annotation.provider == "my_model"
    assert annotation.version == "my_model_version"
    annotation_dict = annotation.to_dic()
    annotation_entities = annotation_dict['annotation_entities']
    assert len(annotation_entities) == 3
    assert annotation_entities[0]["attributes"]["geometry"] == "point.geometry"


def test_create_polygon_annotation():
    media_asset_id = "test_polygon_asset_id"

    polygons = []
    for i in range(3):
        polygons.append(
            Polygon(coordinates=[(100.0 + 10.0 * i, 200.0 - 10.0 * i),
                                 (150.0 + 10.0 * i, 250.0 - 10.0 * i),
                                 (300.0 + 10.0 * i, 100.0 - 10.0 * i),
                                 (100.0 + 10.0 * i, 200.0 - 10.0 * i)],
                    label="test_label_{}".format(i),
                    confidence=0.7 + 0.1 * i,
                    category_id=i,
                    attributes={"track_id": 0}
                    )
        )

    annotation = PolygonAnnotation(
        image_id=media_asset_id,
        polygons=polygons,
        provider="my_model",
        annotation_group=AnnotationGroups.MODEL_GENERATED,
        version="my_model_version",
        id="test_polygon_ann_id"

    )

    assert annotation.id == "test_polygon_ann_id"
    assert annotation.asset_id == media_asset_id
    assert annotation.annotation_type == "polygon"
    assert annotation.annotation_group == AnnotationGroups.MODEL_GENERATED
    assert annotation.provider == "my_model"
    assert annotation.version == "my_model_version"
    annotation_dict = annotation.to_dic()
    annotation_entities = annotation_dict['annotation_entities']
    assert len(annotation_entities) == 3
    assert annotation_entities[0]["attributes"]["track_id"] == 0


def test_create_line_annotation():
    media_asset_id = "test_line_asset_id"

    lines = []
    for i in range(3):
        lines.append(
            Line(coordinates=[(100.0 + 10.0 * i, 200.0 - 10.0 * i),
                                 (150.0 + 10.0 * i, 250.0 - 10.0 * i),
                                 (300.0 + 10.0 * i, 100.0 - 10.0 * i),
                                 (100.0 + 10.0 * i, 200.0 - 10.0 * i)],
                 label="test_label_{}".format(i),
                 confidence=0.7 + 0.1 * i,
                 category_id=i,
                 attributes={"complete": False}
            )
        )

    annotation = LineAnnotation(
        image_id=media_asset_id,
        lines=lines,
        provider="my_model",
        annotation_group=AnnotationGroups.MODEL_GENERATED,
        version="my_model_version",
        id="test_line_ann_id"

    )

    assert annotation.id == "test_line_ann_id"
    assert annotation.asset_id == media_asset_id
    assert annotation.annotation_type == "line"
    assert annotation.annotation_group == AnnotationGroups.MODEL_GENERATED
    assert annotation.provider == "my_model"
    assert annotation.version == "my_model_version"
    annotation_dict = annotation.to_dic()
    annotation_entities = annotation_dict['annotation_entities']
    assert len(annotation_entities) == 3
    assert annotation_entities[0]["attributes"]["complete"] is False


def test_create_classification_annotation():
    media_asset_id = "test_cls_asset_id"
    annotation = ClassificationAnnotation(
        asset_id=media_asset_id,
        labels=[Label(
            label="my_label",
            confidence=0.98,
            category_id=1,
            class_name="my_class_name"
        )],
        provider="my_model",
        annotation_group=AnnotationGroups.MODEL_GENERATED,
        version="my_model_version",
        id="test_cls_ann_id"
    )

    assert annotation.id == "test_cls_ann_id"
    assert annotation.asset_id == media_asset_id
    assert annotation.annotation_type == "classification"
    assert annotation.annotation_group == AnnotationGroups.MODEL_GENERATED
    assert annotation.provider == "my_model"
    assert annotation.version == "my_model_version"
    annotation_dict = annotation.to_dic()
    annotation_entities = annotation_dict['annotation_entities']
    assert len(annotation_entities) == 1
    assert annotation_entities[0]["label"] == "my_label"
    assert annotation_entities[0]["class_name"] == "my_class_name"
    assert annotation_entities[0]["confidence"] == 0.98
    assert annotation_entities[0]["category_id"] == 1
