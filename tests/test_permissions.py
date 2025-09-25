from app import models, crud

def test_permission_levels(db_session):
    # Creamos device y asociaciones
    device = models.Microcontroller(id="dev-1", unique_id="UID123", type="ESP32")
    db_session.add(device)
    db_session.commit()

    assoc_viewer = models.UserMicrocontroller(user_id="user-viewer", microcontroller_id="dev-1", role="viewer")
    assoc_editor = models.UserMicrocontroller(user_id="user-editor", microcontroller_id="dev-1", role="editor")
    assoc_owner = models.UserMicrocontroller(user_id="user-owner", microcontroller_id="dev-1", role="owner")
    db_session.add_all([assoc_viewer, assoc_editor, assoc_owner])
    db_session.commit()

    # Viewer no puede editar
    assert not crud.user_has_permission(db_session, "user-viewer", "dev-1", min_role="editor")
    # Editor sí puede editar
    assert crud.user_has_permission(db_session, "user-editor", "dev-1", min_role="editor")
    # Owner puede editar
    assert crud.user_has_permission(db_session, "user-owner", "dev-1", min_role="editor")
    # Usuario sin asociación no puede ver
    assert not crud.user_has_permission(db_session, "user-x", "dev-1", min_role="viewer")
