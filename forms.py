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
		fields = ('title_en',
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

class CreateContenderForm(forms.ModelForm):
	country = forms.ModelChoiceField(queryset=scenarios.Country.objects.all(),
		cache_choices=True,
		label=_("Country"))

	class Meta:
		model = scenarios.Contender
		fields = ('country',)

class ContenderEditForm(forms.ModelForm):
	class Meta:
		model = scenarios.Contender
		fields = ( )

class CityIncomeForm(forms.ModelForm):
	city = forms.ModelChoiceField(queryset=scenarios.Area.objects.major())

	class Meta:
		model = scenarios.CityIncome

HomeAreaFormSet = inlineformset_factory(scenarios.Contender, scenarios.Home, extra=5)

SetupFormSet = inlineformset_factory(scenarios.Contender, scenarios.Setup, extra=5)

TreasuryFormSet = inlineformset_factory(scenarios.Contender, scenarios.Treasury, extra=1)

CityIncomeFormSet = inlineformset_factory(scenarios.Scenario, scenarios.CityIncome,
	form=CityIncomeForm, extra=3)

DisabledAreaFormSet = inlineformset_factory(scenarios.Scenario, scenarios.DisabledArea, extra=5)

ContenderFormSet = inlineformset_factory(scenarios.Scenario, scenarios.Contender,
	form=CreateContenderForm, extra=1)
