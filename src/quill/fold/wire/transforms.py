def basic_transform(doc):
    """
    Simple transform of a MMD document to HTML (string).
    """
    transformed_str = "\n".join(repr(n) for b in doc.blocks for n in b.nodes)
    return transformed_str
