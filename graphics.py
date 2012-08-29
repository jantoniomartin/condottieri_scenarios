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

import Image, ImageDraw
import os
import os.path

from django.conf import settings

TOKENS_DIR=os.path.join(settings.MEDIA_ROOT, 'scenarios', 'tokens')
TEMPLATES_DIR=os.path.join(settings.PROJECT_ROOT, 'apps/condottieri_scenarios/media/condottieri_scenarios/token_templates')
BADGES_DIR=os.path.join(settings.MEDIA_ROOT, 'scenarios', 'badges')

MAPSDIR=os.path.join(settings.MEDIA_ROOT, 'maps')
SCENARIOSDIR=os.path.join(settings.MEDIA_ROOT, 'scenarios')
COATSDIR=os.path.join(settings.MEDIA_ROOT, 'scenarios', 'coats')

def ensure_dir(f):
	d = os.path.dirname(f)
	if not os.path.exists(d):
		os.makedirs(d)

def make_scenario_map(s):
	""" Makes the initial map for an scenario.
	"""
	base_map = Image.open(s.setting.board)
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

def round_corner(radius, fill):
	""" Draw a round corner
	Taken from http://nadiana.com/pil-tutorial-basic-advanced-drawing
	"""
	corner = Image.new("RGBA", (radius, radius), (0,0,0,0))
	draw = ImageDraw.Draw(corner)
	draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
	del draw
	return corner

def round_rectangle(size, radius, fill):
	""" Draw a rounded rectangle
	Taken from http://nadiana.com/pil-tutorial-basic-advanced-drawing
	"""
	width, height = size
	rectangle = Image.new("RGBA", size, fill)
	corner = round_corner(radius, fill)
	rectangle.paste(corner, (0, 0))
	rectangle.paste(corner.rotate(90), (0, height - radius))
	rectangle.paste(corner.rotate(180), (width - radius, height - radius))
	rectangle.paste(corner.rotate(270), (width - radius, 0))
	return rectangle

def make_flag(fill):
	""" Draw a simple, colored flag """
	flag = Image.new("RGBA", (48, 48))
	draw = ImageDraw.Draw(flag)
	coords = [(7,18), (20,13), (25,18), (45,13), (45,1), (25,6), (20,1), (7,6)]
	draw.polygon(coords, fill=fill, outline="#000000")
	draw.line([(7,5), (7,46)], fill="#000000", width=2)
	del draw
	return flag

def make_country_tokens(instance, **kwargs):
	""" Generate all the tokens for a country """
	try:
		coat = Image.open("%s/%s" % (settings.MEDIA_ROOT, instance.coat_of_arms))
	except:
		coat = None
	## generate 48x48 Badge
	badge_base = Image.open("%s/badge-base.png" % TEMPLATES_DIR)
	if coat:
		badge_base.paste(coat, (4,4), coat)
	badge_base.save("%s/badge-%s.png" % (BADGES_DIR, instance.static_name))
	## generate 24x24 icon
	if coat:
		icon = coat.copy()
		icon.thumbnail((24,24), Image.ANTIALIAS)
		icon.save("%s/icon-%s.png" % (BADGES_DIR, instance.static_name))
	## generate Army token
	army_base = Image.open("%s/army-base.png" % TEMPLATES_DIR)
	draw = ImageDraw.Draw(army_base)
	draw.ellipse((8, 8, 68, 68), fill="#%s" % instance.color)
	del draw
	if coat:
		army_base.paste(coat, (18,18), coat)
	army_base.save("%s/A-%s.png" % (TOKENS_DIR, instance.static_name))
	## generate Garrison token
	garrison_base = Image.open("%s/garrison-base.png" % TEMPLATES_DIR)
	draw = ImageDraw.Draw(garrison_base)
	draw.ellipse((4, 4, 44, 44), fill="#%s" % instance.color)
	del draw
	if coat:
		g_coat = coat.copy()
		g_coat.thumbnail((28, 28), Image.ANTIALIAS)
		garrison_base.paste(g_coat, (12,12), g_coat)
	garrison_base.save("%s/G-%s.png" % (TOKENS_DIR, instance.static_name))
	## generate Fleet token
	fleet_base = Image.open("%s/fleet-base.png" % TEMPLATES_DIR)
	rectangle = round_rectangle((74,36), 10, "#%s" % instance.color)
	fleet_base.paste(rectangle, (3, 3), rectangle)
	ship = Image.open("%s/ship-icon.png" % TEMPLATES_DIR)
	fleet_base.paste(ship, (0,0), ship)
	if coat:
		fleet_base.paste(g_coat, (9, 7), g_coat)
	fleet_base.save("%s/F-%s.png" % (TOKENS_DIR, instance.static_name))
	## generate Control token
	control = Image.new("RGBA", (36, 36))
	draw = ImageDraw.Draw(control)
	draw.ellipse((0, 0, 36, 36), fill="#%s" % instance.color, outline="#000000")
	del draw
	control.save("%s/control-%s.png" % (TOKENS_DIR, instance.static_name))
	## generate Home flag
	flag = make_flag("#%s" % instance.color)
	flag.save("%s/flag-%s.png" % (TOKENS_DIR, instance.static_name))
