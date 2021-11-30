import uuid

from monite.services.comments.schemas import CommentSchema, CreateUpdateCommentSchema


def test_cread_comment_schemas():
    scheme = CreateUpdateCommentSchema.validate({"text": "fewfewfw"})
    assert isinstance(scheme.dict(), dict)


def test_comment_schema():
    scheme = CommentSchema.validate(
        {
            "id": uuid.uuid4(),
            "entity_id": uuid.uuid4(),
            "status": "active",
            "entity_user_id": uuid.uuid4(),
            "api_user_id": None,
            "object_id": "string",
            "object_type": "string",
            "text": "string",
            "mentions": [{"visible_name": "string", "group": "string", "recipient": "string"}],
            "replies_to": None,
            "attachments": [
                {
                    "file_type": "string",
                    "name": "string",
                    "region": "string",
                    "md5": "string",
                    "mimetype": "string",
                    "url": "string",
                    "size": 0,
                    "previews": [{"url": "string", "width": 0, "height": 0}],
                }
            ],
            "edited_at": "2021-10-19T17:52:05.456Z",
        }
    )

    assert isinstance(scheme.dict(), dict)
