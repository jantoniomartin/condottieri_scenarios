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
from django.core.exceptions import ObjectDoesNotExist
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
		not request.user.profile.is_editor:
			raise http.Http404
		return super(CreationAllowedMixin, self).dispatch(request, *args, **kwargs)

class EditionAllowedMixin(CreationAllowedMixin):
	""" A mixin requiring a user to be the creator of the scenario """
	def get(self, request, *args, **kwargs):
		obj = self.get_object()
		try:
			editor = obj.editor
		except AttributeError:
			print("No editor")
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
		user_is_editor = self.request.user.profile.is_editor
		context.update({'user_can_create': user_is_editor,
						'mode': 'create',})
		return context
	
	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.editor = self.request.user
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
			except Exception as v:
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
			user_can_edit = self.request.user.profile.is_editor
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

	def get_context_data(self, **kwargs):
		context = super(SettingView, self).get_context_data(**kwargs)
		if self.object.user_allowed(self.request.user):
			context['editable'] = True
		return context

class DisasterTableView(SettingView):
	template_name = 'condottieri_scenarios/disaster_table.html'

	def get_context_data(self, **kwargs):
		context = super(DisasterTableView, self).get_context_data(**kwargs)
		context.update({
			'famine': models.FamineCell.objects.filter(area__setting=self.object).order_by('row', 'column'),
			'plague': models.PlagueCell.objects.filter(area__setting=self.object).order_by('row', 'column'),
			'storm': models.StormCell.objects.filter(area__setting=self.object).order_by('row', 'column'),
		})
		return context

class SettingAreasView(DetailView):
	model = models.Setting
	context_object_name = 'setting'
	template_name = 'condottieri_scenarios/area_list.html'

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
			user_can_edit = self.request.user.profile.is_editor
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
		user_is_editor = self.request.user.profile.is_editor
		context.update({'user_can_create': user_is_editor,
						'mode': 'create',})
		return context
	
	def form_valid(self, form):
		self.object = form.save(commit=False)
		if not self.object.setting.user_allowed(self.request.user):
			messages.error(self.request, _("You are not allowed to create new scenarios in this setting"))
			return redirect("scenario_list")
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
			except Exception as v:
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
			except Exception as v:
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

class AreaEditMixin(CreationAllowedMixin):
	model = models.Area
	form_class = forms.AreaForm

	def get_context_data(self, formset, **kwargs):
		context = super(AreaEditMixin, self).get_context_data(**kwargs)
		if self.object:
			setting = self.object.setting
		else:
			setting = self.setting
		if setting.user_allowed(self.request.user):
			if setting.in_play:					
				context['protected'] = True
				return context
		else:
			raise http.Http404
		if self.request.POST:
			context['border_formset'] = formset(instance=self.object, data=self.request.POST)
			context['ct_formset'] = forms.ControlTokenFormSet(instance=self.object, data=self.request.POST)
			context['gt_formset'] = forms.GTokenFormSet(instance=self.object, data=self.request.POST)
			context['aft_formset'] = forms.AFTokenFormSet(instance=self.object, data=self.request.POST)
			context['famine_formset'] = forms.FamineCellFormSet(instance=self.object, data=self.request.POST)
			context['plague_formset'] = forms.PlagueCellFormSet(instance=self.object, data=self.request.POST)
			context['storm_formset'] = forms.StormCellFormSet(instance=self.object, data=self.request.POST)
		else:
			if self.object:
				context['border_formset'] = formset(instance=self.object)
				context['ct_formset'] = forms.ControlTokenFormSet(instance=self.object)
				context['gt_formset'] = forms.GTokenFormSet(instance=self.object)
				context['aft_formset'] = forms.AFTokenFormSet(instance=self.object)
				context['famine_formset'] = forms.FamineCellFormSet(instance=self.object)
				context['plague_formset'] = forms.PlagueCellFormSet(instance=self.object)
				context['storm_formset'] = forms.StormCellFormSet(instance=self.object)
			else:
				context['border_formset'] = formset()
				context['ct_formset'] = forms.ControlTokenFormSet()
				context['gt_formset'] = forms.GTokenFormSet()
				context['aft_formset'] = forms.AFTokenFormSet()
				context['famine_formset'] = forms.FamineCellFormSet()
				context['plague_formset'] = forms.PlagueCellFormSet()
				context['storm_formset'] = forms.StormCellFormSet()
		return context

	def form_valid(self, form):
		if not self.object:
			self.object = form.save(commit=False)
			self.object.setting = self.setting
			self.object.save()
			messages.success(self.request, _("The area was successfully created"))
		context = self.get_context_data()
		border_formset = context['border_formset']
		ct_formset = context['ct_formset']
		gt_formset = context['gt_formset']
		aft_formset = context['aft_formset']
		famine_formset = context['famine_formset']
		plague_formset = context['plague_formset']
		storm_formset = context['storm_formset']
		if border_formset.is_valid():
			border_formset.save()
		else:
			messages.error(self.request, _("Borders could not be saved")) 
		if ct_formset.is_valid():
			ct_formset.save()
		else:
			messages.error(self.request, _("Control token position could not be saved")) 
		if gt_formset.is_valid():
			gt_formset.save()
		else:
			messages.error(self.request, _("Garrison token position could not be saved")) 
		if aft_formset.is_valid():
			aft_formset.save()
		else:
			messages.error(self.request, _("Army/Fleet token position could not be saved")) 
		if famine_formset.is_valid() and not self.object.is_sea:
			famine_formset.save()
		else:
			messages.error(self.request, _("Famine table cell could not be saved")) 
		if plague_formset.is_valid() and not self.object.is_sea:
			plague_formset.save()
		else:
			messages.error(self.request, _("Plague table cell could not be saved")) 
		if storm_formset.is_valid() and self.object.is_sea:
			storm_formset.save()
		else:
			messages.error(self.request, _("Storm table cell could not be saved")) 
		return super(AreaEditMixin, self).form_valid(form)

class AreaCreateView(AreaEditMixin, CreateView):
	def dispatch(self, request, *args, **kwargs):
		slug = kwargs['slug']
		try:
			self.setting = models.Setting.objects.get(slug=slug)
		except ObjectDoesNotExist:
			raise http.Http404
		return super(AreaCreateView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		formset = forms.areaborderformset_factory(self.setting)
		context = super(AreaCreateView, self).get_context_data(formset, **kwargs)
		context['setting'] = self.setting
		return context

	def get_success_url(self, **kwargs):
		return reverse_lazy('setting_areas', self.setting.slug)

class AreaUpdateView(AreaEditMixin, UpdateView):
	context_object_name = 'area'
	
	def get_context_data(self, **kwargs):
		formset = forms.areaborderformset_factory(self.object.setting)
		context = super(AreaUpdateView, self).get_context_data(formset, **kwargs)
		context['setting'] = self.object.setting
		return context

	def get_success_url(self, **kwargs):
		return reverse_lazy('setting_areas', self.object.setting.slug)

