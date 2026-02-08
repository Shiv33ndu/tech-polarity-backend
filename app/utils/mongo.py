from bson import ObjectId


def serialize_mongo_doc(doc: dict) -> dict:
    if not doc:
        return doc

    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc
