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

import django.forms as forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

import condottieri_scenarios.models as scenarios

class CreateScenarioForm(forms.ModelForm):
	designer = forms.CharField(max_length=30, required=False, help_text=_("leave it blank if you are the designer"))

	class Meta:
		model = scenarios.Scenario
		fields = (
			'setting',
			'title_en',
			'description_en',
			'designer',
			'start_year',)
		exclude = ('editor', 'published')

class ScenarioDescriptionsForm(forms.ModelForm):

	class Meta:
		model = scenarios.Scenario
		exclude = ('name', 'editor', 'enabled', 'countries', 'published')

class ScenarioForm(forms.ModelForm):
	class Meta:
		model = scenarios.Scenario
		fields = ( )

class CountryForm(forms.ModelForm):
	class Meta:
		model = scenarios.Country
		exclude = ('editor', 'static_name', 'protected',)

class CreateContenderForm(forms.ModelForm):
	country = forms.ModelChoiceField(queryset=scenarios.Country.objects.filter(enabled=True),
		label=_("Country"))

	class Meta:
		model = scenarios.Contender
		fields = ('country',)

class ContenderEditForm(forms.ModelForm):
	class Meta:
		model = scenarios.Contender
		fields = ( )

def homeformset_factory(setting):
	class HomeForm(forms.ModelForm):
		area = forms.ModelChoiceField(queryset=scenarios.Area.objects.filter(
			setting=setting))
	
		class Meta:
			model = scenarios.Home
	
	return inlineformset_factory(scenarios.Contender, scenarios.Home, form=HomeForm, extra=5)

def setupformset_factory(setting):
	class SetupForm(forms.ModelForm):
		area = forms.ModelChoiceField(queryset=scenarios.Area.objects.filter(
			setting=setting))
	
		class Meta:
			model = scenarios.Setup
	
	return inlineformset_factory(scenarios.Contender, scenarios.Setup, form=SetupForm, extra=5)

def cityincomeformset_factory(setting):
	class CityIncomeForm(forms.ModelForm):
		city = forms.ModelChoiceField(queryset=scenarios.Area.objects.major().filter(setting=setting))
	
		class Meta:
			model = scenarios.CityIncome

	return inlineformset_factory(scenarios.Scenario, scenarios.CityIncome, form=CityIncomeForm, extra=3)

def disabledareaformset_factory(setting):
	class DisabledAreaForm(forms.ModelForm):
		area = forms.ModelChoiceField(queryset=scenarios.Area.objects.filter(setting=setting))
	
		class Meta:
			model = scenarios.DisabledArea

	return inlineformset_factory(scenarios.Scenario, scenarios.DisabledArea, form=DisabledAreaForm, extra=5)

TreasuryFormSet = inlineformset_factory(scenarios.Contender, scenarios.Treasury, extra=1)

ContenderFormSet = inlineformset_factory(scenarios.Scenario, scenarios.Contender,
	form=CreateContenderForm, extra=1)

CountryRandomIncomeFormSet = inlineformset_factory(scenarios.Country,
	scenarios.CountryRandomIncome,
	extra=1)

