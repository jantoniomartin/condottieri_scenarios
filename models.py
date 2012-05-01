## Copyright (c) 2012 by Jose Antonio Martin <jantonio.martin AT gmail DOT com>
## This program is free software: you can redistribute it and/or modify it
## under the terms of the GNU Affero General Public License as published by the
## Free Software Foundation, either version 3 of the License, or (at your option
## any later version.
##
## This program is distributed in the hope that it will be useful, but WITHOUT
## ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
## FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
## for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/agpl.txt>.
##
## This license is also included in the file COPYING
##
## AUTHOR: Jose Antonio Martin <jantonio.martin AT gmail DOT com>

from django.db import models

from transmeta import TransMeta

import condottieri_scenarios.managers as managers

class Scenario(models.Model):
	""" This class defines a Condottieri scenario. """

	__metaclass__ = TransMeta
	
	name = models.SlugField(_("slug"), max_length=20, unique=True)
	title = models.CharField(max_length=128, verbose_name=_("title"))
	description = models.TextField(verbose_name=_("description"))
	start_year = models.PositiveIntegerField(_("start year"))
	number_of_players = models.PositiveIntegerField(_("number of players"), default=0)
	enabled = models.BooleanField(_("enabled"), default=False)

	class Meta:
		verbose_name = _("scenario")
		verbose_name_plural = _("scenarios")
		ordering = ["title",]
		translate = ('title', 'description',)

	def get_max_players(self):
		return self.number_of_players

	def get_min_players(self):
		max_players = self.get_max_players()
		neutrals = self.neutral_set.count()
		return max_players - neutrals

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return "scenario/%s" % self.slug

	def _get_countries(self):
		return Country.objects.filter(home__scenario=self).distinct()

	countries = property(_get_countries)

class Country(models.Model):
	__metaclass__ = TransMeta
	name = models.CharField(_("name"), max_length=20, unique=True)
	can_excommunicate = models.BooleanField(_("can excommunicate"), default=False)
	static_name = models.CharField(_("static name"), max_length=20, default="")
	special_units = models.ManyToManyField(SpecialUnit, verbose_name="special units")
	
	objects = managers.CountryManager()

	class Meta:
		verbose_name = _("country")
		verbose_name_plural = _("countries")
		ordering = ["name", ]
		translate = ("name",)

	def __unicode__(self):
		return self.name

