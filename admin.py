from django.contrib import admin

import condottieri_scenarios.models as scenarios
from condottieri_scenarios.graphics import make_scenario_map

class ContenderInline(admin.TabularInline):
	model = scenarios.Contender
	extra = 1
	ordering = ['country']

class SetupInline(admin.TabularInline):
	model = scenarios.Setup
	extra = 5
	ordering = ['contender']

class HomeInline(admin.TabularInline):
	model = scenarios.Home
	extra = 5
	ordering = ['contender']

class TreasuryInline(admin.TabularInline):
	model = scenarios.Treasury
	extra = 1
	ordering = ['contender']

class CityIncomeInline(admin.TabularInline):
	model = scenarios.CityIncome
	extra = 1
	ordering = ['city']

class DisabledAreaInline(admin.TabularInline):
	model = scenarios.DisabledArea
	extra = 1
	ordering = ['area', ]

class ScenarioAdmin(admin.ModelAdmin):
	list_display = ('name', 'start_year', 'setting',)
	inlines = [ContenderInline, CityIncomeInline, DisabledAreaInline, ]
	actions = ['make_map',]
	
	def make_map(self, request, queryset):
		for obj in queryset:
			make_scenario_map(obj)
	make_map.short_description = "Make initial map"

class ContenderAdmin(admin.ModelAdmin):
	inlines = [HomeInline, SetupInline, TreasuryInline,]
	
class CountryAdmin(admin.ModelAdmin):
	list_display = ('name', 'static_name')

class ControlTokenInline(admin.TabularInline):
	model = scenarios.ControlToken
	extra = 1

class GTokenInline(admin.TabularInline):
	model = scenarios.GToken
	extra = 1

class AFTokenInline(admin.TabularInline):
	model = scenarios.AFToken
	extra = 1

class AreaAdmin(admin.ModelAdmin):
	list_display = ('name', 'code', 'is_sea', 'is_coast', 'has_city', 'is_fortified', 'has_port', 'control_income', 'garrison_income')
	inlines = [ ControlTokenInline,
		GTokenInline,
		AFTokenInline ]

admin.site.register(scenarios.Setting) 
admin.site.register(scenarios.Scenario, ScenarioAdmin) 
admin.site.register(scenarios.Contender, ContenderAdmin) 
admin.site.register(scenarios.Country, CountryAdmin)
admin.site.register(scenarios.Area, AreaAdmin)
admin.site.register(scenarios.CountryRandomIncome) 
admin.site.register(scenarios.CityRandomIncome) 
