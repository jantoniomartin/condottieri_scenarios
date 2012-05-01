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

class SpecialUnit(models.Model):
	""" A SpecialUnit describes the attributes of a unit that costs more ducats
	than usual and can be more powerful or more loyal """
	__metaclass__ = TransMeta
	static_title = models.CharField(_("static title"), max_length=50)
	title = CharField(_("title"), max_length=50)
	cost = models.PositiveIntegerField(_("cost"))
	power = models.PositiveIntegerField(_("power"))
	loyalty = models.PositiveIntegerField(_("loyalty"))

	class Meta:
		verbose_name = _("special unit")
		verbose_name_plural = _("special units")
		translate = ("title",)

	def __unicode__(self):
		return _("%(title)s (%(cost)sd)") % {'title': self.title,
											'cost': self.cost}

	def describe(self):
		return _("Costs %(cost)s; Strength %(power)s; Loyalty %(loyalty)s") % {
			'cost': self.cost,
			'power': self.power,
			'loyalty': self.loyalty}

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

class Neutral(models.Model):
	""" Defines a country that will not be used when a game has less players
	than the default. """
	scenario = models.ForeignKey(Scenario, verbose_name=_("scenario"))
	country = models.ForeignKey(Country, verbose_name=_("country"))
	priority = models.PositiveIntegerField(_("priority"), default=0)

	class Meta:
		verbose_name = _("neutral country")
		verbose_name_plural = _("neutral countries")
		ordering = ['scenario', 'priority',]
		unique_together = (('scenario', 'country'), ('scenario', 'priority'),)

	def __unicode__(self):
		return "(%s) %s" % (self.priority, self.country)

class Treasury(models.Model):
	"""
	This class represents the initial amount of ducats that a Country starts
	each Scenario with
	"""
	scenario = models.ForeignKey(Scenario, verbose_name=_("scenario"))
	country = models.ForeignKey(Country, verbose_name=_("country"))
	ducats = models.PositiveIntegerField(_("ducats"), default=0)
	double = models.BooleanField(_("double income"), default=False)

	def __unicode__(self):
		return "%s starts %s with %s ducats" % (self.country, self.scenario,
			self.ducats)

	class Meta:
		verbose_name = _("treasury")
		verbose_name_plural = _("treasuries")
		unique_together = (("scenario", "country"),)

class Area(models.Model):
	""" This class describes **only** the area features in the board. The game is
	actually played in GameArea objects.
	"""
	__metaclass__ = TransMeta

	name = CharField(max_length=25, unique=True, verbose_name=_("name"))
	code = models.CharField(_("code"), max_length=5 ,unique=True)
	is_sea = models.BooleanField(_("is sea"), default=False)
	is_coast = models.BooleanField(_("is coast"), default=False)
	has_city = models.BooleanField(_("has city"), default=False)
	is_fortified = models.BooleanField(_("is fortified"), default=False)
	has_port = models.BooleanField(_("has port"), default=False)
	borders = models.ManyToManyField("self", editable=False, verbose_name=_("borders"))
	## control_income is the number of ducats that the area gives to the player
	## that controls it, including the city (seas give 0)
	control_income = models.PositiveIntegerField(_("control income"),
		null=False, default=0)
	## garrison_income is the number of ducats given by an unbesieged
	## garrison in the area's city, if any (no fortified city, 0)
	garrison_income = models.PositiveIntegerField(_("garrison income"),
		null=False, default=0)

	def is_adjacent(self, area, fleet=False):
		""" Two areas can be adjacent through land, but not through a coast. 
		
		The list ``only_armies`` shows the areas that are adjacent but their
		coasts are not, so a Fleet can move between them.
		"""
		##TODO: Move this to a table in the database
		only_armies = [
			('AVI', 'PRO'),
			('PISA', 'SIE'),
			('CAP', 'AQU'),
			('NAP', 'AQU'),
			('SAL', 'AQU'),
			('SAL', 'BARI'),
			('HER', 'ALB'),
			('BOL', 'MOD'),
			('BOL', 'LUC'),
			('CAR', 'CRO'),
		]
		if fleet:
			if (self.code, area.code) in only_armies or (area.code, self.code) in only_armies:
				return False
		return area in self.borders.all()

	def accepts_type(self, type):
		""" Returns True if an given type of Unit can be in the Area. """

		assert type in ('A', 'F', 'G'), 'Wrong unit type'
		if type=='A':
			if self.is_sea or self.code=='VEN':
				return False
		elif type=='F':
			if not self.has_port:
				return False
		else:
			if not self.is_fortified:
				return False
		return True

	def __unicode__(self):
		return "%(code)s - %(name)s" % {'name': self.name, 'code': self.code}
	
	class Meta:
		verbose_name = _("area")
		verbose_name_plural = _("areas")
		ordering = ('code',)
		translate = ('name', )

class DisabledArea(models.Model):
	""" A DisabledArea is an Area that is not used in a given Scenario. """
	scenario = models.ForeignKey(Scenario, verbose_name=_("scenario"))
	area = models.ForeignKey(Area, verbose_name=_("area"))

	def __unicode__(self):
		return "%(area)s disabled in %(scenario)s" % {'area': self.area,
													'scenario': self.scenario}
	
	class Meta:
		verbose_name = _("disabled area")
		verbose_name_plural = _("disabled areas")
		unique_together = (('scenario', 'area'),) 

