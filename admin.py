from django.contrib import admin

import condottieri_scenarios.models as scenarios

class SetupInline(admin.TabularInline):
	model = scenarios.Setup
	extra = 5
	ordering = ['country']

class HomeInline(admin.TabularInline):
	model = scenarios.Home
	extra = 5
	ordering = ['country']

class TreasuryInline(admin.TabularInline):
	model = scenarios.Treasury
	extra = 1
	ordering = ['country']

class CityIncomeInline(admin.TabularInline):
	model = scenarios.CityIncome
	extra = 1
	ordering = ['city']

class DisabledAreaInline(admin.TabularInline):
	model = scenarios.DisabledArea
	extra = 1
	ordering = ['area', ]

class NeutralInline(admin.TabularInline):
	model = scenarios.Neutral
	extra = 1

class ScenarioAdmin(admin.ModelAdmin):
	list_display = ('name', 'start_year')
	inlines = [HomeInline, SetupInline, TreasuryInline, CityIncomeInline,
				DisabledAreaInline, NeutralInline, ]
	actions = ['make_map',]
	
	def make_map(self, request, queryset):
		for obj in queryset:
			make_scenario_map(obj)
	make_map.short_description = "Make initial map"

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

admin.site.register(scenarios.Scenario, ScenarioAdmin) 
admin.site.register(scenarios.Country, CountryAdmin)
admin.site.register(scenarios.Area, AreaAdmin)
