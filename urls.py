from django.conf.urls.defaults import *

import condottieri_scenarios.views as views

urlpatterns = patterns('condottieri_scenarios.views',
	url(r'^$', views.ScenarioListView.as_view(), name='scenario_list'),
	url(r'^(?P<slug>[-\w]+)/setup/$', views.ScenarioView.as_view(), name='scenario_detail'),
	url(r'^(?P<slug>[-\w]+)/stats/$',
		views.ScenarioView.as_view(template_name='condottieri_scenarios/scenario_stats.html'),
		name='scenario_stats'),
	url(r'^(?P<slug>[-\w]+)/description/$', views.ScenarioDescriptionsEditView.as_view(), name='scenario_descriptions_edit'),
	url(r'^(?P<slug>[-\w]+)/edit/$', views.ScenarioDisabledEditView.as_view(), name='scenario_edit'),
	url(r'^create/$', views.ScenarioCreateView.as_view(), name='scenario_create'),
)

