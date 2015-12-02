#
# -*- coding: utf-8 -*-
# Dia Group Resize Plugin
# Copyright (c) 2015, Alexandre Machado <axmachado@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys, dia
import os
import pygtk
pygtk.require("2.0")
import gtk
import locale

class ResizeWindow(object):    
    
    def __init__(self, group, data):
        self.group = group
        self.data = data
        self.initWindow()

    def initWindow(self):
        self.dlg = gtk.Dialog()
        self.dlg.set_title('Group Resize')
        self.dlg.set_border_width(6)
        self.dlg.vbox.pack_start(self.dialogContents(), fill=True, expand=True, padding=5)
        self.dlg.add_button(gtk.STOCK_APPLY, gtk.RESPONSE_APPLY)
        self.dlg.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        self.dlg.set_has_separator(True)
        self.dlg.set_modal(False)
        self.dlg.get_widget_for_response(gtk.RESPONSE_CLOSE).connect("clicked", self.hide, None)
        self.dlg.get_widget_for_response(gtk.RESPONSE_APPLY).connect("clicked", self.clickAplicar, None)

    def dimensionsFrame(self, label):       
        frame = gtk.Frame(label)
        table = gtk.Table(rows=4, columns=2)
        ignore = gtk.RadioButton(group=None, label="do not change")
        ignore.show()
        smallest = gtk.RadioButton(group=ignore, label="shrink to smallest")
        smallest.show()
        largest = gtk.RadioButton(group=ignore, label="enlarge to largest")
        largest.show()
        specify = gtk.RadioButton(group=ignore, label="resize to:")        
        specify.show()
        value = gtk.Entry()
        value.show()
        specify.connect("toggled", self.enableValueEntry, value)
        self.enableValueEntry(specify, value)
        table.attach (ignore, 0, 1, 0, 1)
        table.attach (smallest, 0, 1, 1, 2)
        table.attach (largest, 0, 1, 2, 3)
        table.attach (specify, 0, 1, 3, 4)
        table.attach (value, 1, 2, 3, 4)
        frame.add(table)
        table.show()
        frame.show()

        options = {
            'ignore': ignore,
            'smallest': smallest,
            'largest': largest,
            'specify': specify,
            'value': value
        }        
        return frame, options

    def enableValueEntry(self, radioSpecify, entrySpecify, *args):
        entrySpecify.set_sensitive(radioSpecify.get_active())
    
    def contentsFrameWidth(self):
        frame, self.widthOptions = self.dimensionsFrame('Width')
        return frame

    def contentsFrameHeight(self):
        frame, self.heightOptions = self.dimensionsFrame('Height')
        return frame
    
    def dialogContents(self):        
        contents = gtk.VBox(spacing=5)
        contents.pack_start(self.contentsFrameWidth(), fill=True, expand=True)
        contents.pack_start(self.contentsFrameHeight(), fill=True, expand=True)
        contents.show()
        return contents

    def getSelectedGroupOption(self, options):
        value = options['value'].get_text()
        for opt in 'ignore', 'smallest', 'largest', 'specify':
            if options[opt].get_active():
                return (opt,value)
        return ('ignore',value)

    def getValue(self, opt, value, elProperty):
        if opt == 'specify':
            return self.toFloat(value)
        else:
            values = [ x.properties[elProperty].value for x in self.group if x.properties.has_key(elProperty) ]
            if opt == 'smallest':
                return min(values)
            else:
                return max(values)

    def adjustWidth(self, value):
        for obj in self.group:
            pos = obj.properties['obj_pos'].value
            if obj.properties.has_key("elem_width"):
                difference = value - obj.properties['elem_width'].value
                handleLeft = obj.handles[3]
                handleRight = obj.handles[4]
                amount = difference/2
                obj.move_handle(handleLeft, (handleLeft.pos.x - amount, handleLeft.pos.y), 0, 0)
                obj.move_handle(handleRight, (handleRight.pos.x + amount, handleRight.pos.y), 0, 0)
                obj.move(pos.x, pos.y)

    def adjustHeight(self, value):
        for obj in self.group:
            pos = obj.properties['obj_pos'].value
            if obj.properties.has_key("elem_height"):
                difference = value - obj.properties['elem_height'].value
                handleTop = obj.handles[1]
                handleBottom = obj.handles[6]
                amount = difference/2
                obj.move_handle(handleTop, (handleTop.pos.x, handleTop.pos.y - amount), 0, 0)
                obj.move_handle(handleBottom, (handleBottom.pos.x, handleBottom.pos.y + amount), 0, 0)
                obj.move(pos.x, pos.y)
                

    def toFloat(self, valor):
        return locale.atof(valor)
                
    def clickAplicar(self, *args):
        optWidth = self.getSelectedGroupOption(self.widthOptions)
        optHeight = self.getSelectedGroupOption(self.heightOptions)

        try:
            if optWidth[0] != 'ignore':
                width = self.getValue(optWidth[0], optWidth[1], 'elem_width')
                self.adjustWidth(width)
            if optHeight[0] != 'ignore':
                height = self.getValue(optHeight[0], optHeight[1], 'elem_height')
                self.adjustHeight(height)

            if dia.active_display():
                diagram = dia.active_display().diagram
                for obj in self.group:
                    diagram.update_connections(obj)
                    
        except Exception,e:
            dia.message(gtk.MESSAGE_ERROR, repr(e))

        if dia.active_display():
            dia.active_display().add_update_all()
            dia.active_display().flush()

            
    def show(self):
        self.dlg.show()
        
    def hide(self, *args):
        self.dlg.hide()

    def run(self):
        return self.dlg.run()
        
def dia_group_resize_db (data,flags):
    diagram = dia.active_display().diagram
    group = diagram.get_sorted_selected()
    if len(group) > 0:
        win = ResizeWindow(group, data)
        win.show()
    else:
        dia.message(gtk.MESSAGE_INFO, "Please select a group of objects")

dia.register_action("ObjectGroupResize", "Group Resize",
                    "/DisplayMenu/Objects/ObjectsExtensionStart",
                    dia_group_resize_db)
