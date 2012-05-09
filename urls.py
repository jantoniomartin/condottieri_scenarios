from django.conf.urls.defaults import *

from condottieri_scenarios.views import *

urlpatterns = patterns('condottieri_scenarios.views',
	url(r'^$', ScenarioListView.as_view(), name='scenario_list'),
	url(r'^(?P<slug>[-\w]+)/$', ScenarioView.as_view(), name='scenario_detail'),
)

