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

import condottieri_scenarios.models as scenarios

class ScenarioForm(forms.ModelForm):
	designer = forms.CharField(max_length=30, required=False)

	class Meta:
		model = scenarios.Scenario
		fields = ('title_en',
			'description_en',
			'designer',
			'start_year',
			'number_of_players',)
		exclude = ('editor',)

class ScenarioDescriptionsForm(forms.ModelForm):

	class Meta:
		model = scenarios.Scenario
		exclude = ('name', 'designer', 'start_year', 'number_of_players',
			'editor', 'enabled')
