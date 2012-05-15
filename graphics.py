## Copyright (c) 2010 by Jose Antonio Martin <jantonio.martin AT gmail DOT com>
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

""" This module defines functions to generate the map. """

import Image
import os
import os.path

from django.conf import settings

TOKENS_DIR=os.path.join(settings.PROJECT_ROOT, 'apps/machiavelli/media/machiavelli/tokens')

BASEMAP='base-map.png'
MAPSDIR=os.path.join(settings.MEDIA_ROOT, 'maps')
SCENARIOSDIR=os.path.join(settings.MEDIA_ROOT, 'scenarios')

def ensure_dir(f):
	d = os.path.dirname(f)
	if not os.path.exists(d):
		os.makedirs(d)

def make_scenario_map(s):
	""" Makes the initial map for an scenario.
	"""
	base_map = Image.open(os.path.join(TOKENS_DIR, BASEMAP))
	## if there are disabled areas, mark them
	marker = Image.open("%s/disabled.png" % TOKENS_DIR)
	for d in  s.disabledarea_set.all():
		base_map.paste(marker, (d.area.aftoken.x, d.area.aftoken.y), marker)
	## mark special city incomes
	marker = Image.open("%s/chest.png" % TOKENS_DIR)
	for i in s.cityincome_set.all():
		base_map.paste(marker, (i.city.gtoken.x + 48, i.city.gtoken.y), marker)
	##
	for c in s.contender_set.filter(country__isnull=False):
		## paste control markers and flags
		marker = Image.open("%s/control-%s.png" % (TOKENS_DIR, c.country.static_name))
		flag = Image.open("%s/flag-%s.png" % (TOKENS_DIR, c.country.static_name))
		for h in c.home_set.all():
			base_map.paste(marker, (h.area.controltoken.x, h.area.controltoken.y), marker)
			if h.is_home:
				base_map.paste(flag, (h.area.controltoken.x, h.area.controltoken.y - 15), flag)
		## paste units
		army = Image.open("%s/A-%s.png" % (TOKENS_DIR, c.country.static_name))
		fleet = Image.open("%s/F-%s.png" % (TOKENS_DIR, c.country.static_name))
		garrison = Image.open("%s/G-%s.png" % (TOKENS_DIR, c.country.static_name))
		for setup in c.setup_set.all():
			if setup.unit_type == 'G':
				coords = (setup.area.gtoken.x, setup.area.gtoken.y)
				base_map.paste(garrison, coords, garrison)
			elif setup.unit_type == 'A':
				coords = (setup.area.aftoken.x, setup.area.aftoken.y)
				base_map.paste(army, coords, army)
			elif setup.unit_type == 'F':
				coords = (setup.area.aftoken.x, setup.area.aftoken.y)
				base_map.paste(fleet, coords, fleet)
			else:
				pass
	for c in s.contender_set.filter(country__isnull=True):
		## paste autonomous garrisons
		garrison = Image.open("%s/G-autonomous.png" % TOKENS_DIR)
		for g in c.setup_set.filter(unit_type='G'):
			coords = (g.area.gtoken.x, g.area.gtoken.y)
			base_map.paste(garrison, coords, garrison)
	## save the map
	result = base_map #.resize((1250, 1780), Image.ANTIALIAS)
	filename = os.path.join(SCENARIOSDIR, s.map_name)
	ensure_dir(filename)
	result.save(filename)
	make_scenario_thumb(s, 187, 267, "thumbnails")
	make_scenario_thumb(s, 625, 890, "625x890")
	return True

def make_scenario_thumb(scenario, w, h, dirname):
	""" Make thumbnails of the scenario map image """
	size = w, h
	fd = os.path.join(SCENARIOSDIR, scenario.map_name)
	ensure_dir(fd)
	filename = os.path.split(fd)[1]
	outfile= os.path.join(SCENARIOSDIR, dirname, filename)
	im = Image.open(fd)
	im.thumbnail(size, Image.ANTIALIAS)
	ensure_dir(outfile)
	im.save(outfile, "JPEG")

