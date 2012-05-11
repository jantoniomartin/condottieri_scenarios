from django.conf.urls.defaults import *

from condottieri_scenarios.views import ScenarioListView, ScenarioView

urlpatterns = patterns('condottieri_scenarios.views',
	url(r'^$', ScenarioListView.as_view(), name='scenario_list'),
	url(r'^(?P<slug>[-\w]+)/$', ScenarioView.as_view(), name='scenario_detail'),
	url(r'^(?P<slug>[-\w]+)/stats/$',
		ScenarioView.as_view(template_name='condottieri_scenarios/scenario_stats.html'),
		name='scenario_stats'),
)

