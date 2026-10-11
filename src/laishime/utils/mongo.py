"""MongoDB write compatibility without importing application configuration."""


def update_document(collection, selector, changes, upsert=False):
    """update_document updates one matching document and returns the driver's result.

    The selector, update document and upsert flag are passed through unchanged.
    Class-level lookup avoids mistaking a dynamically named collection for a
    method when running with legacy Motor/PyMongo.
    """
    if callable(getattr(type(collection), 'update_one', None)):
        return collection.update_one(selector, changes, upsert=upsert)
    return collection.update(selector, changes, upsert=upsert)
