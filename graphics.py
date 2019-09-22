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

from PIL import Image, ImageDraw
import os
import os.path

from django.conf import settings

TOKENS_DIR=os.path.join(settings.MEDIA_ROOT, 'scenarios', 'tokens')
TEMPLATES_DIR=os.path.join(settings.MEDIA_ROOT, 'scenarios', 'token_templates')
BADGES_DIR=os.path.join(settings.MEDIA_ROOT, 'scenarios', 'badges')

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
        result = base_map.convert("RGB")
        filename = s.map_path
        ensure_dir(filename)
        result.save(filename)
        make_scenario_thumb(s, 187, 267, "thumbnails")
        return True

def make_scenario_thumb(scenario, w, h, dirname):
        """ Make thumbnails of the scenario map image """
        size = w, h
        fd = scenario.map_path
        outfile= scenario.thumbnail_path
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
        flag = Image.new("RGBA", (32, 32))
        draw = ImageDraw.Draw(flag)
        coords = [(5,12), (13,9), (17,12), (30,9), (30,1), (17,4), (13,1), (5,4)]
        draw.polygon(coords, fill=fill, outline="#000000")
        draw.line([(5,3), (5,31)], fill="#000000", width=2)
        del draw
        return flag

def signal_handler_make_country_tokens(sender, instance, created, raw, **kwargs):
    make_country_tokens(sender, instance, created, raw, **kwargs)

def make_country_tokens(sender, instance, created, raw, **kwargs):
        """ Generate all the tokens for a country """
        if raw:
            return
        if instance.protected:
            return
        #try:
        coat = Image.open(instance.coat_of_arms)
        #except:
        #       coat = None
        ## generate 48x48 Badge
        badge_base = Image.open(os.path.join(TEMPLATES_DIR, "badge-base.png"))
        if coat:
                badge_base.paste(coat, (4,4), coat)
        badge_base.save(os.path.join(BADGES_DIR, "badge-%s.png" % instance.static_name))
        ## generate 24x24 icon
        if coat:
                icon = coat.copy()
                icon.thumbnail((24,24), Image.ANTIALIAS)
                icon.save(os.path.join(BADGES_DIR, "icon-%s.png" % instance.static_name))
        ## generate Army token
        army_base = Image.open(os.path.join(TEMPLATES_DIR, "army-base.png"))
        draw = ImageDraw.Draw(army_base)
        draw.ellipse((5, 5, 45, 45), fill="#%s" % instance.color)
        del draw
        if coat:
                a_coat = coat.copy()
                a_coat.thumbnail((26,26), Image.ANTIALIAS)
                army_base.paste(a_coat, (12,12), a_coat)
        army_base.save(os.path.join(TOKENS_DIR, "A-%s.png" % instance.static_name))
        ## generate Garrison token
        garrison_base = Image.open(os.path.join(TEMPLATES_DIR, "garrison-base.png"))
        draw = ImageDraw.Draw(garrison_base)
        draw.ellipse((3, 3, 30, 30), fill="#%s" % instance.color)
        del draw
        if coat:
                g_coat = coat.copy()
                g_coat.thumbnail((19, 19), Image.ANTIALIAS)
                garrison_base.paste(g_coat, (8,8), g_coat)
        garrison_base.save(os.path.join(TOKENS_DIR, "G-%s.png" % instance.static_name))
        ## generate Fleet token
        fleet_base = Image.open(os.path.join(TEMPLATES_DIR, "fleet-base.png"))
        rectangle = round_rectangle((49,24), 7, "#%s" % instance.color)
        fleet_base.paste(rectangle, (2, 2), rectangle)
        ship = Image.open(os.path.join(TEMPLATES_DIR, "ship-icon.png"))
        fleet_base.paste(ship, (0,0), ship)
        if coat:
                fleet_base.paste(g_coat, (6, 5), g_coat)
        fleet_base.save(os.path.join(TOKENS_DIR, "F-%s.png" % instance.static_name))
        ## generate Control token
        control = Image.new("RGBA", (24, 24))
        draw = ImageDraw.Draw(control)
        draw.ellipse((0, 0, 24, 24), fill="#%s" % instance.color, outline="#000000")
        del draw
        control.save(os.path.join(TOKENS_DIR, "control-%s.png" % instance.static_name))
        ## generate Home flag
        flag = make_flag("#%s" % instance.color)
        flag.save(os.path.join(TOKENS_DIR, "flag-%s.png" % instance.static_name))
