from django.test import TestCase, override_settings
from unittest import skip, mock 

from django.contrib.auth.models import User

from condottieri_scenarios.models import *

class SettingTestCase(TestCase):

    fixtures = ['users.yaml',]

    def setUp(self):
        self.user = User.objects.first()
        self.setting = Setting.objects.create(title_en = 'dummy setting',
                description_en = 'description',
                editor = self.user)

    def test_get_board_upload_path(self):
        self.assertIn("board-dummy-setting.png", get_board_upload_path(self.setting, ''))

    def test_str(self):
        self.assertEqual(str(self.setting), "dummy setting")

    def test_user_allowed(self):
        self.assertTrue(self.setting.user_allowed(self.user))

    def test_in_play(self):
        self.assertFalse(self.setting.in_play)

    def test_configuration_str(self):
        self.assertEqual(str(self.setting.configuration), "dummy setting")

class ScenarioTestCase(TestCase):

    fixtures = ['users.yaml',]

    def setUp(self):
        self.user = User.objects.first()
        self.setting = Setting.objects.create(title_en = 'dummy setting',
                description_en = 'description',
                editor = self.user)
        self.scenario = Scenario.objects.create(setting = self.setting,
                title_en = "dummy scenario",
                description_en = "description",
                start_year = 0,
                editor = self.user)

    def test_number_of_players(self):
        self.assertEqual(self.scenario.number_of_players, 0)

    def test_get_max_players(self):
        self.assertEqual(self.scenario.get_max_players(), 0)

    def test_str(self):
        self.assertEqual(str(self.scenario), "dummy scenario")

    def test_get_aboslute_url(self):
        self.assertEqual(self.scenario.get_absolute_url(), "/scenarios/detail/dummy-scenario/")

    def test_map_name(self):
        self.assertEqual(self.scenario.map_name, "scenario-dummy-scenario.jpg")

    @override_settings(MEDIA_ROOT="media")
    @override_settings(SCENARIOS_ROOT="scenarios")
    def test_map_path(self):
        self.assertEqual(self.scenario.map_path,
                "media/scenarios/scenario-dummy-scenario.jpg")

    @override_settings(MEDIA_URL="media")
    @override_settings(SCENARIOS_ROOT="scenarios")
    def test_map_url(self):
        self.assertEqual(self.scenario.map_url,
                "media/scenarios/scenario-dummy-scenario.jpg")

    @override_settings(MEDIA_ROOT="media")
    @override_settings(SCENARIOS_ROOT="scenarios")
    def test_thumbnail_path(self):
        self.assertEqual(self.scenario.thumbnail_path,
                "media/scenarios/thumbnails/scenario-dummy-scenario.jpg")

    @override_settings(MEDIA_URL="media")
    @override_settings(SCENARIOS_ROOT="scenarios")
    def test_thumbnail_url(self):
        self.assertEqual(self.scenario.thumbnail_url,
                "media/scenarios/thumbnails/scenario-dummy-scenario.jpg")

    def test_in_use(self):
        self.assertFalse(self.scenario.in_use)
    
    def test_in_play(self):
        self.assertFalse(self.scenario.in_play)

    def test_autonomous(self):
        self.assertQuerysetEqual(self.scenario.autonomous, [])

    def test_major_cities(self):
        self.assertQuerysetEqual(self.scenario.major_cities, [])

    def test_times_played(self):
        self.assertEqual(self.scenario.times_played, 0)

class SpecialUnitTestCase(TestCase):

    def setUp(self):
        self.unit = SpecialUnit.objects.create(static_title="special unit",
                title_en="special unit",
                cost = 0,
                power = 0,
                loyalty = 0)

    def test_str(self):
        self.assertEqual(str(self.unit), "special unit (0d)")

    def test_describe(self):
        self.assertEqual(self.unit.describe(), "Costs 0; Strength 0; Loyalty 0")

class ReligionTestCase(TestCase):

    def setUp(self):
        self.religion = Religion.objects.create(slug="religion", name_en="religion")

    def test_str(self):
        self.assertEqual(str(self.religion), "religion")

class CountryTestCase(TestCase):

    fixtures = ['users.yaml',]
    
    @mock.patch("condottieri_scenarios.graphics.make_country_tokens")
    def setUp(self, make_country_tokens_mock):
        make_country_tokens_mock.return_value = None
        self.user = User.objects.first()
        self.setting = Setting.objects.create(title_en = 'dummy setting',
                description_en = 'description',
                editor = self.user)
        self.country = Country.objects.create(name_en = "Albacete",
                color = "000000",
                coat_of_arms = "",
                editor = self.user)

    def test_get_coat_upload_path(self):
        self.assertEqual(get_coat_upload_path(self.country, ""),
                "scenarios/coats/coat-albacete.png")

    def test_str(self):
        self.assertEqual(str(self.country), "Albacete")

    def test_get_absolute_url(self):
        self.assertEqual(self.country.get_absolute_url(),
                "/scenarios/country/detail/albacete/")

    def test_get_income(self):
        self.assertFalse(self.country.get_income(self.setting))

    def test_get_random_income(self):
        self.assertEqual(self.country.get_random_income(self.setting, 0, False), 0)

    def test_in_play(self):
        self.assertFalse(self.country.in_play)

class ContenderTestCase(TestCase):

    fixtures = ['users.yaml',]
    
    @mock.patch("condottieri_scenarios.graphics.make_country_tokens")
    def setUp(self, make_country_tokens_mock):
        make_country_tokens_mock.return_value = None
        self.user = User.objects.first()
        self.setting = Setting.objects.create(title_en = 'dummy setting',
                description_en = 'description',
                editor = self.user)
        self.country = Country.objects.create(name_en = "Albacete",
                color = "000000",
                coat_of_arms = "",
                editor = self.user)
        self.scenario = Scenario.objects.create(setting = self.setting,
                title_en = "dummy scenario",
                description_en = "description",
                start_year = 0,
                editor = self.user)
        self.contender = Contender.objects.create(country=self.country,
                scenario=self.scenario)
        self.treasury = Treasury.objects.create(contender=self.contender)

    def test_str(self):
        self.assertEqual(str(self.contender), "Albacete")

    def test_editor(self):
        self.assertEqual(self.contender.editor, self.user)

    def test_treasury_str(self):
        self.assertEqual(str(self.treasury), "Albacete starts with 0 ducats")

    def test_treasury_editor(self):
        self.assertEqual(self.treasury.editor, self.user)

class AreaTestCase(TestCase):

    fixtures = ['users.yaml',]
    
    def setUp(self):
        self.user = User.objects.first()
        self.setting = Setting.objects.create(title_en = 'dummy setting',
                description_en = 'description',
                editor = self.user)
        self.area_1 = Area.objects.create(setting=self.setting,
                name_en="Alicante",
                code="ALI",
                is_coast=True,
                has_city=True,
                is_fortified=True,
                has_port=True)
        self.area_2 = Area.objects.create(setting=self.setting,
                name_en="Murcia",
                code="MUR",
                is_coast=True)
        self.area_3 = Area.objects.create(setting=self.setting,
                name_en="Albacete",
                code="ALB",
                has_city=True)
        Border.objects.create(from_area=self.area_1, to_area=self.area_2, only_land=False)
        Border.objects.create(from_area=self.area_1, to_area=self.area_3, only_land=True)
        Border.objects.create(from_area=self.area_2, to_area=self.area_3, only_land=True)

    def test_is_adjacent_no_fleet(self):
        self.assertTrue(self.area_1.is_adjacent(self.area_2))
        self.assertTrue(self.area_2.is_adjacent(self.area_1))
        self.assertTrue(self.area_2.is_adjacent(self.area_3))
        self.assertTrue(self.area_3.is_adjacent(self.area_2))
        self.assertTrue(self.area_1.is_adjacent(self.area_3))
        self.assertTrue(self.area_3.is_adjacent(self.area_1))

    def test_is_adjacent_fleet(self):
        self.assertTrue(self.area_1.is_adjacent(self.area_2, fleet=True))
        self.assertTrue(self.area_2.is_adjacent(self.area_1, fleet=True))
        self.assertFalse(self.area_2.is_adjacent(self.area_3, fleet=True))
        self.assertFalse(self.area_3.is_adjacent(self.area_2, fleet=True))
        self.assertFalse(self.area_1.is_adjacent(self.area_3, fleet=True))
        self.assertFalse(self.area_3.is_adjacent(self.area_1, fleet=True))

    def test_build_possible(self):
        self.assertTrue(self.area_1.build_possible('A'))
        self.assertTrue(self.area_1.build_possible('F'))
        self.assertTrue(self.area_1.build_possible('G'))
        self.assertTrue(self.area_2.build_possible('A'))
        self.assertFalse(self.area_2.build_possible('F'))
        self.assertFalse(self.area_2.build_possible('G'))
        self.assertTrue(self.area_3.build_possible('A'))
        self.assertFalse(self.area_3.build_possible('F'))
        self.assertFalse(self.area_3.build_possible('G'))
    
    def test_accepts_type(self):
        self.assertTrue(self.area_1.accepts_type('A'))
        self.assertTrue(self.area_1.accepts_type('F'))
        self.assertTrue(self.area_1.accepts_type('G'))
        self.assertTrue(self.area_2.accepts_type('A'))
        self.assertTrue(self.area_2.accepts_type('F'))
        self.assertFalse(self.area_2.accepts_type('G'))
        self.assertTrue(self.area_3.accepts_type('A'))
        self.assertFalse(self.area_3.accepts_type('F'))
        self.assertFalse(self.area_3.accepts_type('G'))

    def test_str(self):
        self.assertEqual(str(self.area_1),
                "ALI - Alicante")

    def test_get_random_income(self):
        self.assertEqual(self.area_1.get_random_income(0), 0)

