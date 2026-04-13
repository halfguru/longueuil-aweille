from longueuil_aweille.browse import Activity, ActivityScraper
from longueuil_aweille.status import ActivityStatus


def _make_activity(
    name: str = "Test Activity",
    days: str = "Lundi",
    age_min: int = 5,
    age_max: int = 12,
    location: str = "Centre A",
) -> Activity:
    return Activity(
        name=name,
        code="ABC123",
        domain="Test Domain",
        age_min=age_min,
        age_max=age_max,
        start_date="1 jan",
        end_date="31 mar",
        promoter="Prom",
        spots=10,
        price="50$",
        days=days,
        times="18:00",
        location=location,
        status=ActivityStatus.AVAILABLE,
    )


def test_filter_by_name():
    scraper = ActivityScraper()
    scraper.activities = [
        _make_activity(name="Parent-bébé natation"),
        _make_activity(name="Adulte yoga"),
        _make_activity(name="Parent-bébé gym"),
    ]
    result = scraper.filter_activities(name_contains="parent-bébé")
    assert len(result) == 2
    assert all("parent-bébé" in a.name.lower() for a in result)


def test_filter_by_name_case_insensitive():
    scraper = ActivityScraper()
    scraper.activities = [_make_activity(name="Yoga Avancé")]
    result = scraper.filter_activities(name_contains="yoga avancé")
    assert len(result) == 1


def test_filter_by_name_no_match():
    scraper = ActivityScraper()
    scraper.activities = [_make_activity(name="Yoga")]
    result = scraper.filter_activities(name_contains="pilate")
    assert len(result) == 0


def test_filter_by_location():
    scraper = ActivityScraper()
    scraper.activities = [
        _make_activity(location="Centre Vieux-Longueuil"),
        _make_activity(location="Parc Boucherville"),
        _make_activity(location="Centre Vieux-Longueuil Est"),
    ]
    result = scraper.filter_activities(location_contains="Vieux-Longueuil")
    assert len(result) == 2


def test_filter_by_day_french():
    scraper = ActivityScraper()
    scraper.activities = [
        _make_activity(days="Lundi et Mercredi"),
        _make_activity(days="Mardi"),
        _make_activity(days="lun. et jeu."),
    ]
    result = scraper.filter_activities(day="lundi")
    assert len(result) == 2


def test_filter_by_day_english():
    scraper = ActivityScraper()
    scraper.activities = [
        _make_activity(days="Monday"),
        _make_activity(days="Tuesday"),
    ]
    result = scraper.filter_activities(day="mon")
    assert len(result) == 1


def test_filter_by_day_short_abbreviation():
    scraper = ActivityScraper()
    scraper.activities = [
        _make_activity(days="Mercredi"),
        _make_activity(days="Vendredi"),
    ]
    result = scraper.filter_activities(day="mer")
    assert len(result) == 1
    assert result[0].days == "Mercredi"


def test_filter_by_age_in_range():
    scraper = ActivityScraper()
    scraper.activities = [
        _make_activity(age_min=5, age_max=12),
        _make_activity(age_min=13, age_max=17),
    ]
    result = scraper.filter_activities(age=8)
    assert len(result) == 1
    assert result[0].age_min == 5


def test_filter_by_age_at_boundary():
    scraper = ActivityScraper()
    scraper.activities = [_make_activity(age_min=5, age_max=12)]
    assert len(scraper.filter_activities(age=5)) == 1
    assert len(scraper.filter_activities(age=12)) == 1


def test_filter_by_age_out_of_range():
    scraper = ActivityScraper()
    scraper.activities = [_make_activity(age_min=5, age_max=12)]
    result = scraper.filter_activities(age=4)
    assert len(result) == 0
    result = scraper.filter_activities(age=13)
    assert len(result) == 0


def test_filter_age_zero_skips_filter():
    scraper = ActivityScraper()
    scraper.activities = [
        _make_activity(age_min=5, age_max=12),
        _make_activity(age_min=13, age_max=17),
    ]
    result = scraper.filter_activities(age=0)
    assert len(result) == 2


def test_filter_combined():
    scraper = ActivityScraper()
    scraper.activities = [
        _make_activity(name="Swim Kids", days="Lundi", age_min=5, age_max=12, location="Pool"),
        _make_activity(name="Swim Adults", days="Lundi", age_min=18, age_max=99, location="Pool"),
        _make_activity(name="Swim Kids", days="Mardi", age_min=5, age_max=12, location="Pool"),
    ]
    result = scraper.filter_activities(name_contains="swim", day="lun", age=8)
    assert len(result) == 1
    assert result[0].name == "Swim Kids"


def test_filter_no_filters_returns_all():
    scraper = ActivityScraper()
    scraper.activities = [_make_activity(), _make_activity()]
    result = scraper.filter_activities()
    assert len(result) == 2
