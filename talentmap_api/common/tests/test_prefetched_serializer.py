import pytest

from talentmap_api.common.serializers import PrefetchedSerializer


@pytest.mark.django_db()
def test_prefetched_child_fields():
    override_fields = [
        "id",
        "long_description",
        "banana",
        "post",
        "post__banana",
        "post__danger_pay",
        "post__randr__description",
        "notpost__butnested"
    ]

    override_exclude = [
        "id",
        "long_description",
        "banana",
        "post",
        "post__banana",
        "post__danger_pay",
        "post__randr__description",
        "notpost__butnested"
    ]

    expected_kwargs = {
        "override_fields": [
            "banana",
            "danger_pay",
            "randr__description"
        ],

        "override_exclude": [
            "banana",
            "danger_pay",
            "randr__description"
        ]
    }

    kwargs = {}

    PrefetchedSerializer.parse_child_overrides(override_fields, override_exclude, "post", {}, kwargs)

    assert expected_kwargs == kwargs
