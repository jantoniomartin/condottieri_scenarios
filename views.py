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

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import redirect

from condottieri_scenarios.models import Scenario
import condottieri_scenarios.forms as forms


class ScenarioListView(ListView):
	model = Scenario
	
class ScenarioView(DetailView):
	model = Scenario
	slug_field = 'name'
	context_object_name = 'scenario'

	def get_context_data(self, **kwargs):
		context = super(ScenarioView, self).get_context_data(**kwargs)
		user_can_edit = self.request.user.get_profile().is_editor or \
			self.request.user.is_admin
		context.update({'user_can_edit': user_can_edit})
		return context
	

class ScenarioCreateView(CreateView):
	model = Scenario
	form_class = forms.CreateScenarioForm
	
	def get_context_data(self, **kwargs):
		context = super(ScenarioCreateView, self).get_context_data(**kwargs)
		user_is_editor = self.request.user.get_profile().is_editor
		context.update({'user_can_create': user_is_editor})
		return context
	
	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.editor = self.request.user
		self.object.save()
		return super(ScenarioCreateView, self).form_valid(form)

class ScenarioUpdateView(UpdateView):
	model = Scenario
	slug_field = 'name'
	
	def get_context_data(self, **kwargs):
		context = super(ScenarioUpdateView, self).get_context_data(**kwargs)
		user_can_edit = self.request.user.get_profile().is_editor or \
			self.request.user.is_admin
		context.update({'user_can_edit': user_can_edit})
		return context

class ScenarioDescriptionsEditView(ScenarioUpdateView):
	form_class = forms.ScenarioDescriptionsForm

class ScenarioDisabledEditView(ScenarioUpdateView):
	form_class = forms.ScenarioForm
	template_name = 'condottieri_scenarios/scenario_areas_form.html'

	def form_valid(self, form):
		context = self.get_context_data()
		disabledarea_formset = context['disabledarea_formset']
		if disabledarea_formset.is_valid():
			self.object = form.save()
			disabledarea_formset.instance = self.object
			disabledarea_formset.save()
			return redirect(self.object)

	def get_context_data(self, **kwargs):
		context = super(ScenarioDisabledEditView, self).get_context_data(**kwargs)
		if self.request.POST:
			context['disabledarea_formset'] = forms.DisabledAreaFormSet(self.request.POST)
		else:
			context['disabledarea_formset'] = forms.DisabledAreaFormSet()
		return context
