from unittest import TestCase

from orders.parse_product_options import (
    CustomizeProgressCalculator, OptionsCalculator, RangeCalculator, SelectedOption, SingleOptionCalculator,
    TemplateRepresentation, LAYOUT_TYPES, get_product_layout_type, parse_options_from_layout_options,
)


class TestParseOptionsType(TestCase):
    def setUp(self) -> None:
        pass

    def test_parse_option_model(self):
        options = [
            (
                {
                    "id": "nvuu1548hwrjyywmoyw",
                    "addedAt": 1565040373737,
                    "product": {
                        "slug": "glory",
                        "title": "Glory boosting",
                        "squareImage": "https://stage.littlelight.store/api/destiny2/media/uploaded_images/glory-rank51.png",
                    },
                    "layoutType": "range-calculator",
                    "characterId": "2305843009310315583",
                    "membershipId": "4611686018471738848",
                    "layoutOptions": {
                        "price": "100.00",
                        "pointTo": 1000,
                        "oldPrice": "100.00",
                        "dimension": "Point",
                        "lastLabel": "Brave",
                        "pointFrom": 0,
                        "pointValue": 50,
                        "dimensionPlural": "Points",
                    },
                },
                "range-calculator",
            ),
            (
                {
                    "id": "8dn7wfkhzx2k0j4ae6k",
                    "addedAt": 1568439342668,
                    "product": {
                        "slug": "the-recluse",
                        "title": "The Recluse",
                        "squareImage": "/api/destiny2/media/uploaded_images/the_Recluse.jpg",
                    },
                    "layoutType": "customize-progress",
                    "characterId": "2305843009478614754",
                    "membershipId": "4611686018435433552",
                    "layoutOptions": {
                        "price": {"steps": 1, "oldPrice": "179", "totalPrice": "150",},
                        "selectedPreset": {
                            "id": 117,
                            "price": "150",
                            "title": "The Recluse",
                            "service": "the-recluse",
                            "ordering": 0,
                            "old_price": "179",
                            "description": "Full Quest Completion",
                            "extra_configs": {"steps": 1, "isTotal": True},
                        },
                        "customSelectedOptions": [],
                    },
                },
                "customize-progress",
            ),
            (
                {
                    "layoutType": "single",
                    "layoutOptions": {
                        "id": 41,
                        "title": "Start from 10 competitive matches",
                        "description": "full quest",
                        "price": "91",
                        "old_price": "89",
                        "extra_configs": {"steps": 4},
                        "ordering": 0,
                        "service": "the-shattered-throne",
                        "steps": 4,
                    },
                    "product": {
                        "title": "The Shattered Throne",
                        "squareImage": "http://localhost:8000/api/destiny2/media/uploaded_images/Crown_of_Sorrow_pPZ4HpT.jpg",
                        "slug": "the-shattered-throne",
                    },
                    "id": "omqyxmrtzpk8lpk88e",
                    "characterId": "2305843009260984947",
                    "membershipId": "4611686018444234603",
                    "addedAt": 1586010264494,
                },
                "single",
            ),
            (
                {
                    "id": "qoqesr3tvtgk8ky5ynk",
                    "addedAt": 1585964249264,
                    "product": {
                        "slug": "trials-of-osiris",
                        "title": "Trials Of Osiris",
                        "squareImage": "/api/destiny2/media/uploaded_images/MAIN_390-435_4Xw4AWS.jpg",
                    },
                    "layoutType": "check-progress",
                    "characterId": "2305843009271697835",
                    "membershipId": "4611686018469010863",
                    "layoutOptions": {
                        "price": {"oldPrice": 50, "totalPrice": 50},
                        "selectedOptions": {
                            "332": {
                                "id": 332,
                                "price": "50",
                                "title": "Flawless Passage",
                                "service": "trials-of-osiris",
                                "ordering": 1,
                                "old_price": None,
                                "description": "Default Flawless Passage",
                                "extra_configs": {
                                    "isChecked": False,
                                    "skipProgress": True,
                                    "mustBeChecked": False,
                                },
                            }
                        },
                        "isOptionsSelected": True,
                    },
                },
                "check-progress",
            ),
        ]
        for option in options:
            raw_data, result = option
            with self.subTest(i=result):
                self.assertEqual(get_product_layout_type(raw_data), result)


class TestRangeCalculatorParsing(TestCase):
    layout_option = "range-calculator"

    layout_options = [
        {
            "price": "100.00",
            "pointTo": 1000,
            "oldPrice": "100.00",
            "dimension": "Point",
            "lastLabel": "Brave",
            "pointFrom": 0,
            "pointValue": 50,
            "dimensionPlural": "Points",
        },
        {
            "pointFrom": 0,
            "pointTo": 44,
            "pointValue": 1,
            "price": "352",
            "oldPrice": "352",
            "lastLabel": "40",
            "respectManual": False,
            "dimension": "Win",
            "dimensionPlural": "Wins",
        },
    ]

    parsed_result = [
        "From 0 points to 1000 points",
        "44 wins",
    ]

    def test_parsing_from_json(self):
        for option in self.layout_options:
            with self.subTest(i=option):
                parsed = RangeCalculator.from_json(option)  # type: RangeCalculator

                self.assertEqual(parsed.point_to, option["pointTo"])
                self.assertEqual(parsed.point_from, option["pointFrom"])
                self.assertEqual(parsed.old_price, option["oldPrice"])
                self.assertEqual(parsed.dimension, option["dimension"])
                self.assertEqual(parsed.dimension_plural, option["dimensionPlural"])
                self.assertEqual(parsed.last_label, option["lastLabel"])

    def test_representation(self):
        for i, option in enumerate(self.layout_options):
            with self.subTest(i=option):
                result = self.parsed_result[i]

                parsed = RangeCalculator.from_json(option)  # type: RangeCalculator

                representation = parsed.get_template_representation()
                rep = representation[0]
                self.assertEqual(rep.description, result)
                self.assertEqual(rep.price, parsed.price)


class TestOptionsCalculatorRepresentation(TestCase):
    layout_option = "customize-progress"

    layout_options = [
        {
            "price": {"steps": 1, "oldPrice": "179", "totalPrice": "150"},
            "selectedPreset": {
                "id": 117,
                "price": "150",
                "title": "The Recluse",
                "service": "the-recluse",
                "ordering": 0,
                "old_price": "179",
                "description": "Full Quest Completion",
                "extra_configs": {"steps": 1, "isTotal": True},
            },
            "customSelectedOptions": [],
        },
        {
            "price": {"steps": 1, "oldPrice": "179", "totalPrice": "150"},
            "selectedPreset": None,
            "customSelectedOptions": [
                {
                    "id": 293,
                    "title": "125 Linear Fusion Rifle Final Blows",
                    "description": "",
                    "price": "80",
                    "old_price": None,
                    "extra_configs": {
                        "isChecked": True,
                        "skipProgress": False,
                        "mustBeChecked": True,
                    },
                    "ordering": 1,
                    "service": "komodo-4fr",
                },
                {
                    "id": 294,
                    "title": "15 Linear Fusion Rifle Precision Final Blows",
                    "description": "",
                    "price": "30",
                    "old_price": None,
                    "extra_configs": {
                        "isChecked": True,
                        "skipProgress": False,
                        "mustBeChecked": False,
                    },
                    "ordering": 2,
                    "service": "komodo-4fr",
                },
                {
                    "id": 295,
                    "title": "Reach Glory Rank Heroic",
                    "description": "",
                    "price": "30",
                    "old_price": None,
                    "extra_configs": {
                        "isChecked": True,
                        "skipProgress": True,
                        "mustBeChecked": False,
                    },
                    "ordering": 3,
                    "service": "komodo-4fr",
                },
            ],
        },
    ]

    def test_parsing_json(self):
        parsed_options = [
            [],
            [
                SelectedOption(title="125 Linear Fusion Rifle Final Blows", price="80"),
                SelectedOption(
                    title="15 Linear Fusion Rifle Precision Final Blows", price="30"
                ),
                SelectedOption(title="Reach Glory Rank Heroic", price="30"),
            ],
        ]
        for option, parsed_options in zip(self.layout_options, parsed_options):
            with self.subTest(i=option):
                parsed = CustomizeProgressCalculator.from_json(
                    option
                )  # type: CustomizeProgressCalculator

                self.assertEqual(parsed.price, option["price"]["totalPrice"])
                self.assertEqual(
                    parsed.selected_preset,
                    option["selectedPreset"]["description"]
                    if option["selectedPreset"]
                    else None,
                )
                self.assertEqual(parsed.selected_options, parsed_options)

    def test_layout_repr(self):
        repr_result = [
            [
                TemplateRepresentation(description="Full Quest Completion", price="150"),
            ],
            [
                TemplateRepresentation(
                    description="125 Linear Fusion Rifle Final Blows", price="80"
                ),
                TemplateRepresentation(
                    description="15 Linear Fusion Rifle Precision Final Blows",
                    price="30",
                ),
                TemplateRepresentation(
                    description="Reach Glory Rank Heroic", price="30"
                ),
            ],
        ]
        for i, option in enumerate(self.layout_options):
            result = repr_result[i]
            with self.subTest(i=result):
                parsed = CustomizeProgressCalculator.from_json(option)
                _repr = parsed.get_template_representation()
                self.assertListEqual(_repr, result)


class TestOptions(TestCase):
    layout_types = ["check-progress", "options"]
    layout_options = [
        {
            "price": {"oldPrice": 30, "totalPrice": 30},
            "selectedOptions": {
                "133": {
                    "id": 133,
                    "price": "30",
                    "title": "Normal Leviathan",
                    "old_price": None,
                    "description": "",
                }
            },
            "isOptionsSelected": True,
        },
        {
            "price": {"oldPrice": 50, "totalPrice": 50},
            "selectedOptions": {
                "332": {
                    "id": 332,
                    "price": "50",
                    "title": "Flawless Passage",
                    "service": "trials-of-osiris",
                    "ordering": 1,
                    "old_price": None,
                    "description": "Default Flawless Passage",
                    "extra_configs": {
                        "isChecked": False,
                        "skipProgress": True,
                        "mustBeChecked": False,
                    },
                }
            },
            "isOptionsSelected": True,
        },
    ]

    def test_parsing_json(self):
        parsed_options = [
            [SelectedOption(title="Normal Leviathan", price="30")],
            [SelectedOption(title="Flawless Passage", price="50")],
        ]

        for option, parsed_options in zip(self.layout_options, parsed_options):
            with self.subTest(i=option):
                parsed = OptionsCalculator.from_json(option)  # type: OptionsCalculator

                self.assertEqual(parsed.price, str(option["price"]["totalPrice"]))
                self.assertEqual(parsed.selected_options, parsed_options)

    def test_layout_repr(self):
        repr_result = [
            [
                TemplateRepresentation(description="Normal Leviathan", price="30"),
            ],
            [
                TemplateRepresentation(description="Flawless Passage", price="50"),
            ]
        ]
        for i, option in enumerate(self.layout_options):
            result = repr_result[i]
            for layout_type in self.layout_types:  # type: LAYOUT_TYPES
                with self.subTest(i=(result, layout_type)):
                    parsed = parse_options_from_layout_options(option, layout_type)
                    self.assertListEqual(parsed, result)


class TestSingle(TestCase):
    layout_options = [
        {
            "id": 41,
            "title": "Start from 10 competitive matches",
            "description": "full quest",
            "price": "91",
            "old_price": "89",
            "extra_configs": {"steps": 4},
            "ordering": 0,
            "service": "the-shattered-throne",
            "steps": 4,
        }
    ]

    def test_parsing_json(self):

        for option in self.layout_options:
            with self.subTest(i=option):
                parsed = SingleOptionCalculator.from_json(
                    option
                )  # type: SingleOptionCalculator

                self.assertEqual(parsed.price, str(option["price"]))
                self.assertEqual(parsed.description, str(option["title"]))

    def test_layout_repr(self):
        repr_result = [
            [
                TemplateRepresentation(
                    description="Start from 10 competitive matches", price="91"
                ),
            ]
        ]
        for i, option in enumerate(self.layout_options):
            result = repr_result[i]
            with self.subTest(i=result):
                parsed = SingleOptionCalculator.from_json(option)
                _repr = parsed.get_template_representation()
                self.assertListEqual(_repr, result)
