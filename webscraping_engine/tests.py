from django.test import TestCase
from .utils import WebscrapingUtils


class TestWebscrapingEngine(TestCase):
    engine = WebscrapingUtils()

    def test_university_picture(self):
        self.engine.get(url="https://www.studentcrowd.com/university-l1000607-s1008573-bournemouth_university-bournemouth")
        # University picture src
        control_src: str = "https://media.studentcrowd.net/w426-h284-q70-cfill/index-data/20181029052048-1008573.jpeg"
        assert control_src == self.engine.get_university_picture()

    def test_university_ucas_points(self):
        self.engine.get(url="https://www.studentcrowd.com/university-l1000607-s1008573-bournemouth_university-bournemouth")
        control_ucas_points = "144-159"
        assert control_ucas_points == self.engine.get_university_ucas_points()

    def test_university_tef_rating(self):
        self.engine.get(url="https://www.studentcrowd.com/university-l1000607-s1008573-bournemouth_university-bournemouth")
        control_tef_rating = "Silver"
        assert control_tef_rating == self.engine.get_tef_rating()

    def test_offer_acceptance_rates(self):
        self.engine.get(url="https://www.studentcrowd.com/university-l1000607-s1008573-bournemouth_university-bournemouth")
        control_offer_rate, control_acceptance_rate = "77.4%", "22.35%"
        scraped_data = self.engine.get_offer_and_acceptance_rate()
        scraped_offer_rate, scraped_acceptance_rate = scraped_data['offer_rate'], scraped_data['acceptance_rate']

        assert control_offer_rate == scraped_offer_rate
        assert control_acceptance_rate == scraped_acceptance_rate
