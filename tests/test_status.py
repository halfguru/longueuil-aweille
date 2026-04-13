from longueuil_aweille.status import ActivityStatus, get_status_from_image_src


def test_available_default():
    assert get_status_from_image_src("some-random-image.png") == ActivityStatus.AVAILABLE


def test_available_empty_strings():
    assert get_status_from_image_src("") == ActivityStatus.AVAILABLE


def test_not_yet():
    assert get_status_from_image_src("NotNow.png") == ActivityStatus.NOT_YET


def test_not_yet_case_insensitive():
    assert get_status_from_image_src("notnow_something.gif") == ActivityStatus.NOT_YET


def test_never_available_src():
    assert get_status_from_image_src("JamaisDispo.png") == ActivityStatus.NEVER_AVAILABLE


def test_never_available_alt():
    assert (
        get_status_from_image_src("img.png", "jamais disponible") == ActivityStatus.NEVER_AVAILABLE
    )


def test_never_available_alt_case_insensitive():
    assert get_status_from_image_src("x.png", "Jamais Disponible") == ActivityStatus.NEVER_AVAILABLE


def test_full():
    assert get_status_from_image_src("Complet.png") == ActivityStatus.FULL


def test_full_case_insensitive():
    assert get_status_from_image_src("complet_icon.png") == ActivityStatus.FULL


def test_cancelled():
    assert get_status_from_image_src("Annule.png") == ActivityStatus.CANCELLED


def test_cancelled_case_insensitive():
    assert get_status_from_image_src("annule_badge.png") == ActivityStatus.CANCELLED


def test_alt_text_unused_for_non_never():
    assert get_status_from_image_src("NotNow.png", "complet") == ActivityStatus.NOT_YET


def test_priority_notnow_over_complet_in_alt():
    result = get_status_from_image_src("notnow.png", "complet")
    assert result == ActivityStatus.NOT_YET
