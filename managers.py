from django.db import models
from django.db.models import Avg

class CountryManager(models.Manager):
	def scenario_stats(self, scenario):
		return self.filter(score__game__scenario=scenario).distinct().annotate(
			avg_points=Avg('score__points'),
			avg_position=Avg('score__position')).order_by('avg_position')

class AreaManager(models.Manager):
	def major(self):
		return self.filter(garrison_income__gt=1)
