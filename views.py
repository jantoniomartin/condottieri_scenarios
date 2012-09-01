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

from datetime import datetime

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.shortcuts import redirect
from django import http
from django.utils.functional import lazy
from django.core.urlresolvers import reverse
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

import condottieri_scenarios.models as models
import condottieri_scenarios.forms as forms
from condottieri_scenarios.graphics import make_scenario_map

reverse_lazy = lambda name=None, *args : lazy(reverse, str)(name, args=args)

class CreationAllowedMixin(object):
	""" A mixin requiring a user to be authenticated and being editor or admin """
	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated() or \
		not request.user.get_profile().is_editor:
			raise http.Http404
		return super(CreationAllowedMixin, self).dispatch(request, *args, **kwargs)

class EditionAllowedMixin(CreationAllowedMixin):
	""" A mixin requiring a user to be the creator of the scenario """
	def get(self, request, *args, **kwargs):
		obj = self.get_object()
		try:
			editor = obj.editor
		except AttributeError:
			print "No editor"
			editor = None
		if not editor == self.request.user and not self.request.user.is_staff:
			raise http.Http404
		return super(EditionAllowedMixin, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(EditionAllowedMixin, self).get_context_data(**kwargs)
		context.update({'user_can_edit': True,})
		return context

class CountryCreateView(CreationAllowedMixin, CreateView):
	model = models.Country
	form_class = forms.CountryForm
	
	def get_context_data(self, **kwargs):
		context = super(CountryCreateView, self).get_context_data(**kwargs)
		user_is_editor = self.request.user.get_profile().is_editor
		context.update({'user_can_create': user_is_editor,
						'mode': 'create',})
		return context
	
	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.editor = self.request.user
		self.object.save()
		return super(CountryCreateView, self).form_valid(form)

class CountryUpdateView(EditionAllowedMixin, UpdateView):
	model = models.Country
	slug_field = 'static_name'
	context_object_name = 'country'
	form_class = forms.CountryForm

	def get_context_data(self, **kwargs):
		context = super(CountryUpdateView, self).get_context_data(**kwargs)
		if self.object.protected:
			messages.error(self.request, _("This country is read only."))
			return redirect(self.object)
		formset = forms.CountryRandomIncomeFormSet
		if self.request.POST:
			context['formset'] = formset(instance=self.object, data=self.request.POST)
		else:
			context['formset'] = formset()
		return context
	
	def form_valid(self, form):
		context = self.get_context_data()
		formset = context['formset']
		if formset.is_valid():
			try:
				formset.save()
			except Exception, v:
				messages.error(self.request, v)
			else:
				form.save()
				return http.HttpResponseRedirect(self.get_success_url())
		return self.render_to_response(self.get_context_data(form=form))

class CountryRandomIncomeDeleteView(EditionAllowedMixin, DeleteView):
	model = models.CountryRandomIncome
	context_object_name = "income"
	success_msg = _("The random income table has been deleted")

	def get_success_url(self):
		return reverse_lazy('country_detail', self.country_slug)

	def delete(self, request, *args, **kwargs):
		country = self.get_object().country
		self.country_slug = country.static_name
		if country.in_play:
			messages.error(request, _("You cannot change the random income for a country that is currently being used in a game."))
			return redirect(self.get_success_url())
		else:
			messages.success(request, self.success_msg)
			return super(CountryRandomIncomeDeleteView, self).delete(request, *args, **kwargs)

class CountryView(DetailView):
	model = models.Country
	slug_field = "static_name"
	context_object_name = "country"

	def get_context_data(self, **kwargs):
		context = super(CountryView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			user_can_edit = self.request.user.get_profile().is_editor
			context.update({'user_can_edit': user_can_edit})
		return context

class CountryListView(ListView):
	model = models.Country
	
	def get_queryset(self):
		if not self.request.user.is_authenticated():
			return models.Country.objects.filter(enabled=True)
		if self.request.user.is_staff:
			return models.Country.objects.all()
		else:
			return models.Country.objects.filter(Q(enabled=True)|Q(editor=self.request.user))
	
class SettingView(DetailView):
	model = models.Setting
	context_object_name = 'setting'

class SettingListView(ListView):
	model = models.Setting

	def get_queryset(self):
		if not self.request.user.is_authenticated():
			return models.Setting.objects.filter(enabled=True)
		if self.request.user.is_staff:
			return models.Setting.objects.all()
		else:
			return models.Setting.objects.filter(Q(enabled=True)|Q(editor=self.request.user))
	
class ScenarioListView(ListView):
	model = models.Scenario
	
	def get_queryset(self):
		if not self.request.user.is_authenticated():
			return models.Scenario.objects.filter(enabled=True)
		if self.request.user.is_staff:
			return models.Scenario.objects.all()
		else:
			return models.Scenario.objects.filter(Q(enabled=True)|Q(editor=self.request.user))
	
class ScenarioView(DetailView):
	model = models.Scenario
	slug_field = 'name'
	context_object_name = 'scenario'

	def get_context_data(self, **kwargs):
		context = super(ScenarioView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			user_can_edit = self.request.user.get_profile().is_editor
			context.update({'user_can_edit': user_can_edit})
		return context

class ScenarioToggleView(EditionAllowedMixin, UpdateView):
	model = models.Scenario
	slug_field = 'name'
	context_object_name = 'scenario'
	form_class = forms.ScenarioForm	
	template_name = 'condottieri_scenarios/scenario_toggle.html'

	def post(self, request, *args, **kwargs):
		obj = self.get_object()
		if not obj.enabled:
			## check that all scenario parts have been edited
			if obj.contender_set.count() < 2:
				messages.error(request, _("First you must define at least two countries"))
				return redirect(obj)
			for c in obj.contender_set.filter(country__isnull=False):
				if c.home_set.count() < 1:
					messages.error(request, _("At least one country doesn't have home areas"))
					return redirect(obj)
				if c.setup_set.count() < 1:
					messages.error(request, _("At least one country doesn't have initial units"))
					return redirect(obj)
				try:
					c.treasury
				except:
					messages.error(request, _("At least one country doesn't have an initial treasury"))
					return redirect(obj)
		return super(ScenarioToggleView, self).post(request, *args, **kwargs)
	
	def form_valid(self, form):
		if form.is_valid():
			scenario = form.save(commit=False)
			scenario.enabled = not scenario.enabled
			if scenario.enabled:
				messages.success(self.request, _("The scenario has been enabled"))
				if scenario.published is None:
					scenario.published = datetime.now()
			else:
				messages.success(self.request, _("The scenario has been disabled"))
			scenario.save()
		return super(ScenarioToggleView, self).form_valid(form=form)

class ScenarioRedrawMapView(EditionAllowedMixin, ScenarioView):
	def get(self, request, **kwargs):
		obj = self.get_object()
		make_scenario_map(obj)
		return super(ScenarioRedrawMapView, self).get(request, **kwargs)

class ScenarioCreateView(CreationAllowedMixin, CreateView):
	model = models.Scenario
	form_class = forms.CreateScenarioForm
	
	def get_context_data(self, **kwargs):
		context = super(ScenarioCreateView, self).get_context_data(**kwargs)
		user_is_editor = self.request.user.get_profile().is_editor
		context.update({'user_can_create': user_is_editor,
						'mode': 'create',})
		return context
	
	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.editor = self.request.user
		self.object.save()
		return super(ScenarioCreateView, self).form_valid(form)

class ScenarioDescriptionsEditView(EditionAllowedMixin, UpdateView):
	model = models.Scenario
	slug_field = 'name'
	form_class = forms.ScenarioDescriptionsForm

class ScenarioUpdateView(EditionAllowedMixin, UpdateView):
	model = models.Scenario
	slug_field = 'name'
	context_object_name = 'scenario'
	form_class = forms.ScenarioForm
	
	def form_valid(self, form):
		context = self.get_context_data()
		formset = context['formset']
		if formset.is_valid():
			try:
				formset.save()
			except Exception, v:
				messages.error(self.request, v)
			else:
				return http.HttpResponseRedirect(self.get_success_url())
		return self.render_to_response(self.get_context_data(form=form))

	def get_context_data(self, formset=None, **kwargs):
		context = super(ScenarioUpdateView, self).get_context_data(**kwargs)
		if formset is None:
			return context
		if self.request.POST:
			context['formset'] = formset(instance=self.object, data=self.request.POST)
		else:
			context['formset'] = formset()
		return context

class ContenderEditView(ScenarioUpdateView):
	template_name = 'condottieri_scenarios/contender_form.html'

	def get_context_data(self, **kwargs):
		return super(ContenderEditView, self).get_context_data(formset=forms.ContenderFormSet, **kwargs)

class DisabledAreasEditView(ScenarioUpdateView):
	template_name = 'condottieri_scenarios/disabled_form.html'

	def get_context_data(self, **kwargs):
		formset = forms.disabledareaformset_factory(self.object.setting)
		return super(DisabledAreasEditView, self).get_context_data(formset=formset, **kwargs)

class CityIncomeEditView(ScenarioUpdateView):
	template_name = 'condottieri_scenarios/cityincome_form.html'

	def get_context_data(self, formset=None, **kwargs):
		formset = forms.cityincomeformset_factory(self.object.setting)
		return super(CityIncomeEditView, self).get_context_data(formset=formset, **kwargs)

class ScenarioItemDeleteView(EditionAllowedMixin, DeleteView):
	def delete(self, request, *args, **kwargs):
		scenario = self.get_object().scenario
		self.scenario_name = scenario.name
		if scenario.in_play:
			messages.error(request, _("You cannot make this change in a scenario that is being played played"))
			return redirect(self.get_success_url())
		else:
			messages.success(request, _("The object has been deleted"))
			return super(ScenarioItemDeleteView, self).delete(request, *args, **kwargs)

class CityIncomeDeleteView(ScenarioItemDeleteView):
	def get_success_url(self, **kwargs):
		return reverse_lazy('scenario_detail', self.scenario_name)

	model = models.CityIncome
	context_object_name = "cityincome"

class DisabledAreaDeleteView(ScenarioItemDeleteView):
	def get_success_url(self, **kwargs):
		return reverse_lazy('scenario_detail', self.scenario_name)

	model = models.DisabledArea
	context_object_name = "disabledarea"
	
class ContenderDeleteView(EditionAllowedMixin, DeleteView):
	model = models.Contender
	context_object_name = "contender"
	
	def get_success_url(self, **kwargs):
		return reverse_lazy('scenario_detail', self.scenario_name)

	def delete(self, request, *args, **kwargs):
		scenario = self.get_object().scenario
		self.scenario_name = scenario.name
		if scenario.in_use:
			messages.error(request, _("You cannot change the countries in a scenario that has been already played."))
			return redirect(self.get_success_url())
		else:
			messages.success(request, _("The country has been deleted"))
			return super(ContenderDeleteView, self).delete(request, *args, **kwargs)

class ContenderUpdateView(EditionAllowedMixin, UpdateView):
	model = models.Contender
	context_object_name = 'contender'
	form_class =forms.ContenderEditForm
	
	def form_valid(self, form):
		context = self.get_context_data()
		formset = context['formset']
		if formset.is_valid():
			try:
				formset.save()
			except Exception, v:
				messages.error(self.request, v)
			else:
				return http.HttpResponseRedirect(self.get_success_url())
		return self.render_to_response(self.get_context_data(form=form))

	def get_context_data(self, formset=None, **kwargs):
		context = super(ContenderUpdateView, self).get_context_data(**kwargs)
		if formset is None:
			return context
		if self.request.POST:
			context['formset'] = formset(instance=self.object, data=self.request.POST)
		else:
			context['formset'] = formset()
		return context

class ContenderHomeView(ContenderUpdateView):
	template_name = 'condottieri_scenarios/homes_form.html'
	
	def get_success_url(self, **kwargs):
		return reverse_lazy('scenario_contender_homes', self.object.pk)
	
	def get_context_data(self, **kwargs):
		formset = forms.homeformset_factory(self.object.scenario.setting)
		return super(ContenderHomeView, self).get_context_data(formset=formset, **kwargs)

class ContenderSetupView(ContenderUpdateView):
	template_name = 'condottieri_scenarios/setup_form.html'
	
	def get_success_url(self, **kwargs):
		return reverse_lazy('scenario_contender_setup', self.object.pk)
	
	def get_context_data(self, **kwargs):
		formset = forms.setupformset_factory(self.object.scenario.setting)
		return super(ContenderSetupView, self).get_context_data(formset=formset, **kwargs)

class ContenderTreasuryView(ContenderUpdateView):
	template_name = 'condottieri_scenarios/treasury_form.html'
	
	def get_success_url(self, **kwargs):
		return reverse_lazy('scenario_detail', self.object.scenario.name)
	
	def get_context_data(self, **kwargs):
		context = super(ContenderUpdateView, self).get_context_data(**kwargs)
		if self.request.POST:
			context['formset'] = forms.TreasuryFormSet(instance=self.object, data=self.request.POST)
		else:
			context['formset'] = forms.TreasuryFormSet(instance=self.object)
		return context

class ContenderItemDeleteView(EditionAllowedMixin, DeleteView):
	def delete(self, request, *args, **kwargs):
		contender = self.get_object().contender
		self.contender_pk = contender.pk
		if contender.scenario.in_play:
			messages.error(request, _("You cannot change the initial setup in a scenario that is currently being played."))
			return redirect(self.get_success_url())
		else:
			messages.success(request, self.success_msg)
			return super(ContenderItemDeleteView, self).delete(request, *args, **kwargs)

class HomeDeleteView(ContenderItemDeleteView):
	model = models.Home
	context_object_name = "home"
	success_msg = _("The initial area has been deleted")

	def get_success_url(self):
		return reverse_lazy('scenario_contender_homes', self.contender_pk)

class SetupDeleteView(ContenderItemDeleteView):
	model = models.Setup
	context_object_name = "setup"
	success_msg = _("The initial unit has been deleted")

	def get_success_url(self):
		return reverse_lazy('scenario_contender_setup', self.contender_pk)

