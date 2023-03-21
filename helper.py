# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
import math

def show_message_info(message):
    def draw(self, context):
        self.layout.label(text = message)
    bpy.context.window_manager.popup_menu(draw, title = "Message", icon = "INFO")

def show_message_error(message):
    def draw(self, context):
        self.layout.label(text = message)
    bpy.context.window_manager.popup_menu(draw, title = 'Error', icon = 'ERROR')