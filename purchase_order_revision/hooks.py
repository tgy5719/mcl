
def post_init_hook(cr, registry):
    """ Fill unrevisioned name of all existent purchases """
    query = """
        UPDATE purchase_order SET unrevisioned_name=name
        WHERE unrevisioned_name IS NULL;
    """
    cr.execute(query)
