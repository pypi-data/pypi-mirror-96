# COPYRIGHT (C) 2020-2021 Nicotine+ Team
# COPYRIGHT (C) 2006-2009 Daelstorm <daelstorm@gmail.com>
# COPYRIGHT (C) 2003-2004 Hyriand <hyriand@thegraveyard.org>
#
# GNU GENERAL PUBLIC LICENSE
#    Version 3, 29 June 2007
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

import os

from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject

from pynicotine import slskmessages
from pynicotine.gtkgui.utils import humanize
from pynicotine.gtkgui.utils import human_speed
from pynicotine.gtkgui.utils import initialise_columns
from pynicotine.gtkgui.utils import load_ui_elements
from pynicotine.gtkgui.utils import PopupMenu
from pynicotine.gtkgui.utils import set_treeview_selected_row
from pynicotine.gtkgui.utils import triggers_context_menu
from pynicotine.gtkgui.utils import update_widget_visuals


class Interests:

    def __init__(self, frame, np):

        self.frame = frame
        self.np = np

        load_ui_elements(self, os.path.join(self.frame.gui_dir, "ui", "interests.ui"))
        self.frame.interestsvbox.add(self.Main)

        self.likes = {}
        self.likes_model = Gtk.ListStore(str)
        self.likes_model.set_sort_column_id(0, Gtk.SortType.ASCENDING)

        cols = initialise_columns(
            None,
            self.LikesList,
            ["i_like", _("I Like"), -1, "text", None]
        )

        cols["i_like"].set_sort_column_id(0)
        self.LikesList.set_model(self.likes_model)

        self.til_popup_menu = popup = PopupMenu(self.frame)

        popup.setup(
            ("#" + _("_Remove Item"), self.on_remove_thing_i_like),
            ("#" + _("Re_commendations For Item"), self.on_recommend_item),
            ("", None),
            ("#" + _("_Search For Item"), self.on_recommend_search)
        )

        self.dislikes = {}
        self.dislikes_model = Gtk.ListStore(str)
        self.dislikes_model.set_sort_column_id(0, Gtk.SortType.ASCENDING)

        cols = initialise_columns(
            None,
            self.DislikesList,
            ["i_dislike", _("I Dislike"), -1, "text", None]
        )

        cols["i_dislike"].set_sort_column_id(0)
        self.DislikesList.set_model(self.dislikes_model)

        self.tidl_popup_menu = popup = PopupMenu(self.frame)

        popup.setup(
            ("#" + _("_Remove Item"), self.on_remove_thing_i_dislike),
            ("", None),
            ("#" + _("_Search For Item"), self.on_recommend_search)
        )

        cols = initialise_columns(
            None,
            self.RecommendationsList,
            ["rating", _("Rating"), 0, "number", None],
            ["item", _("Item"), -1, "text", None]
        )

        cols["rating"].set_sort_column_id(2)
        cols["item"].set_sort_column_id(1)

        self.recommendations_model = Gtk.ListStore(
            str,  # (0) hrating
            str,  # (1) item
            int   # (2) rating
        )
        self.RecommendationsList.set_model(self.recommendations_model)

        self.r_popup_menu = popup = PopupMenu(self.frame)

        popup.setup(
            ("$" + _("I _Like This"), self.on_like_recommendation),
            ("$" + _("I _Dislike This"), self.on_dislike_recommendation),
            ("#" + _("_Recommendations For Item"), self.on_recommend_recommendation),
            ("", None),
            ("#" + _("_Search For Item"), self.on_recommend_search)
        )

        cols = initialise_columns(
            None,
            self.UnrecommendationsList,
            ["rating", _("Rating"), 0, "number", None],
            ["item", _("Item"), -1, "text", None]
        )

        cols["rating"].set_sort_column_id(2)
        cols["item"].set_sort_column_id(1)

        self.unrecommendations_model = Gtk.ListStore(
            str,  # (0) hrating
            str,  # (1) item
            int   # (2) rating
        )
        self.UnrecommendationsList.set_model(self.unrecommendations_model)

        self.ur_popup_menu = popup = PopupMenu(self.frame)

        popup.setup(
            ("$" + _("I _Like This"), self.on_like_recommendation),
            ("$" + _("I _Dislike This"), self.on_dislike_recommendation),
            ("#" + _("_Recommendations For Item"), self.on_recommend_recommendation),
            ("", None),
            ("#" + _("_Search For Item"), self.on_recommend_search)
        )

        cols = initialise_columns(
            None,
            self.RecommendationUsersList,
            ["country", _("Country"), 25, "pixbuf", None],
            ["user", _("User"), 100, "text", None],
            ["speed", _("Speed"), 100, "text", None],
            ["files", _("Files"), 100, "text", None],
        )

        cols["country"].set_sort_column_id(4)
        cols["user"].set_sort_column_id(1)
        cols["speed"].set_sort_column_id(5)
        cols["files"].set_sort_column_id(6)

        cols["country"].get_widget().hide()

        self.recommendation_users = {}
        self.recommendation_users_model = Gtk.ListStore(
            GObject.TYPE_OBJECT,  # (0) status icon
            str,                  # (1) user
            str,                  # (2) hspeed
            str,                  # (3) hfiles
            GObject.TYPE_INT64,   # (4) status
            GObject.TYPE_UINT64,  # (5) speed
            GObject.TYPE_UINT64   # (6) file count
        )
        self.RecommendationUsersList.set_model(self.recommendation_users_model)
        self.recommendation_users_model.set_sort_column_id(1, Gtk.SortType.ASCENDING)

        self.ru_popup_menu = popup = PopupMenu(self.frame)
        popup.setup_user_menu()

        for thing in self.np.config.sections["interests"]["likes"]:
            if thing and isinstance(thing, str):
                self.likes[thing] = self.likes_model.append([thing])

        for thing in self.np.config.sections["interests"]["dislikes"]:
            if thing and isinstance(thing, str):
                self.dislikes[thing] = self.dislikes_model.append([thing])

        self.update_visuals()

    def on_add_thing_i_like(self, widget, *args):
        thing = widget.get_text()
        widget.set_text("")

        if thing and thing.lower() not in self.np.config.sections["interests"]["likes"]:
            thing = thing.lower()
            self.np.config.sections["interests"]["likes"].append(thing)
            self.likes[thing] = self.likes_model.append([thing])
            self.np.config.write_configuration()
            self.np.queue.put(slskmessages.AddThingILike(thing))

    def on_add_thing_i_dislike(self, widget, *args):
        thing = widget.get_text()
        widget.set_text("")

        if thing and thing.lower() not in self.np.config.sections["interests"]["dislikes"]:
            thing = thing.lower()
            self.np.config.sections["interests"]["dislikes"].append(thing)
            self.dislikes[thing] = self.dislikes_model.append([thing])
            self.np.config.write_configuration()
            self.np.queue.put(slskmessages.AddThingIHate(thing))

    def on_remove_thing_i_like(self, widget):
        thing = self.til_popup_menu.get_user()

        if thing not in self.np.config.sections["interests"]["likes"]:
            return

        self.likes_model.remove(self.likes[thing])
        del self.likes[thing]
        self.np.config.sections["interests"]["likes"].remove(thing)

        self.np.config.write_configuration()
        self.np.queue.put(slskmessages.RemoveThingILike(thing))

    def on_remove_thing_i_dislike(self, widget):
        thing = self.tidl_popup_menu.get_user()

        if thing not in self.np.config.sections["interests"]["dislikes"]:
            return

        self.dislikes_model.remove(self.dislikes[thing])
        del self.dislikes[thing]
        self.np.config.sections["interests"]["dislikes"].remove(thing)

        self.np.config.write_configuration()
        self.np.queue.put(slskmessages.RemoveThingIHate(thing))

    def on_like_recommendation(self, widget):
        thing = widget.get_parent().get_user()

        if widget.get_active() and \
                thing and thing not in self.np.config.sections["interests"]["likes"]:
            self.np.config.sections["interests"]["likes"].append(thing)
            self.likes[thing] = self.likes_model.append([thing])

            self.np.config.write_configuration()
            self.np.queue.put(slskmessages.AddThingILike(thing))

        elif not widget.get_active() and \
                thing and thing in self.np.config.sections["interests"]["likes"]:
            self.likes_model.remove(self.likes[thing])
            del self.likes[thing]
            self.np.config.sections["interests"]["likes"].remove(thing)

            self.np.config.write_configuration()
            self.np.queue.put(slskmessages.RemoveThingILike(thing))

    def on_dislike_recommendation(self, widget):
        thing = widget.get_parent().get_user()

        if widget.get_active() and \
                thing and thing not in self.np.config.sections["interests"]["dislikes"]:
            self.np.config.sections["interests"]["dislikes"].append(thing)
            self.dislikes[thing] = self.dislikes_model.append([thing])

            self.np.config.write_configuration()
            self.np.queue.put(slskmessages.AddThingIHate(thing))

        elif not widget.get_active() and \
                thing and thing in self.np.config.sections["interests"]["dislikes"]:
            self.dislikes_model.remove(self.dislikes[thing])
            del self.dislikes[thing]
            self.np.config.sections["interests"]["dislikes"].remove(thing)

            self.np.config.write_configuration()
            self.np.queue.put(slskmessages.RemoveThingIHate(thing))

    def on_recommend_item(self, widget):
        thing = self.til_popup_menu.get_user()
        self.np.queue.put(slskmessages.ItemRecommendations(thing))
        self.np.queue.put(slskmessages.ItemSimilarUsers(thing))

    def on_recommend_recommendation(self, widget):
        thing = self.r_popup_menu.get_user()
        self.np.queue.put(slskmessages.ItemRecommendations(thing))
        self.np.queue.put(slskmessages.ItemSimilarUsers(thing))

    def on_recommend_search(self, widget):
        thing = widget.get_parent().get_user()
        self.frame.SearchEntry.set_text(thing)
        self.frame.change_main_page("search")

    def on_global_recommendations_clicked(self, widget):
        self.np.queue.put(slskmessages.GlobalRecommendations())

    def on_recommendations_clicked(self, widget):
        self.np.queue.put(slskmessages.Recommendations())

    def on_similar_users_clicked(self, widget):
        self.np.queue.put(slskmessages.SimilarUsers())

    def set_recommendations(self, title, recom):
        self.recommendations_model.clear()

        for (thing, rating) in recom.items():
            self.recommendations_model.append([humanize(rating), thing, rating])

        self.recommendations_model.set_sort_column_id(2, Gtk.SortType.DESCENDING)

    def set_unrecommendations(self, title, recom):
        self.unrecommendations_model.clear()

        for (thing, rating) in recom.items():
            self.unrecommendations_model.append([humanize(rating), thing, rating])

        self.unrecommendations_model.set_sort_column_id(2, Gtk.SortType.ASCENDING)

    def global_recommendations(self, msg):
        self.set_recommendations("Global recommendations", msg.recommendations)
        self.set_unrecommendations("Unrecommendations", msg.unrecommendations)

    def recommendations(self, msg):
        self.set_recommendations("Recommendations", msg.recommendations)
        self.set_unrecommendations("Unrecommendations", msg.unrecommendations)

    def item_recommendations(self, msg):
        self.set_recommendations(_("Recommendations for %s") % msg.thing, msg.recommendations)
        self.set_unrecommendations("Unrecommendations", msg.unrecommendations)

    def similar_users(self, msg):
        self.recommendation_users_model.clear()
        self.recommendation_users = {}

        for user in msg.users:
            iterator = self.recommendation_users_model.append([self.frame.images["offline"], user, "0", "0", 0, 0, 0])
            self.recommendation_users[user] = iterator
            self.np.queue.put(slskmessages.AddUser(user))

    def get_user_status(self, msg):
        if msg.user not in self.recommendation_users:
            return

        img = self.frame.get_status_image(msg.status)
        self.recommendation_users_model.set(self.recommendation_users[msg.user], 0, img, 4, msg.status)

    def get_user_stats(self, msg):
        if msg.user not in self.recommendation_users:
            return

        self.recommendation_users_model.set(self.recommendation_users[msg.user], 2, human_speed(msg.avgspeed), 3, humanize(msg.files), 5, msg.avgspeed, 6, msg.files)

    def get_selected_item(self, treeview, column=0):

        model, iterator = treeview.get_selection().get_selected()

        if iterator is None:
            return None

        return model.get_value(iterator, column)

    def on_ru_list_clicked(self, widget, event):

        if triggers_context_menu(event):
            set_treeview_selected_row(widget, event)
            return self.on_popup_ru_menu(widget)

        if event.type == Gdk.EventType._2BUTTON_PRESS:
            user = self.get_selected_item(widget)

            if user is not None:
                self.frame.privatechats.send_message(user)
                self.frame.change_main_page("private")
                return True

        return False

    def on_popup_ru_menu(self, widget):

        user = self.get_selected_item(widget, column=1)
        if user is None:
            return False

        self.ru_popup_menu.set_user(user)
        self.ru_popup_menu.toggle_user_items()

        self.ru_popup_menu.popup()
        return True

    def on_til_list_clicked(self, widget, event):

        if triggers_context_menu(event):
            set_treeview_selected_row(widget, event)
            return self.on_popup_til_menu(widget)

        return False

    def on_popup_til_menu(self, widget):

        item = self.get_selected_item(widget, column=0)
        if item is None:
            return False

        self.til_popup_menu.set_user(item)

        self.til_popup_menu.popup()
        return True

    def on_tidl_list_clicked(self, widget, event):

        if triggers_context_menu(event):
            set_treeview_selected_row(widget, event)
            return self.on_popup_tidl_menu(widget)

        return False

    def on_popup_tidl_menu(self, widget):

        item = self.get_selected_item(widget, column=0)
        if item is None:
            return False

        self.tidl_popup_menu.set_user(item)

        self.tidl_popup_menu.popup()
        return True

    def on_r_list_clicked(self, widget, event):

        if triggers_context_menu(event):
            set_treeview_selected_row(widget, event)
            return self.on_popup_r_menu(widget)

        return False

    def on_popup_r_menu(self, widget):

        item = self.get_selected_item(widget, column=1)
        if item is None:
            return False

        self.r_popup_menu.set_user(item)

        items = self.r_popup_menu.get_items()
        items[_("I _Like This")].set_active(item in self.np.config.sections["interests"]["likes"])
        items[_("I _Dislike This")].set_active(item in self.np.config.sections["interests"]["dislikes"])

        self.r_popup_menu.popup()
        return True

    def on_un_rec_list_clicked(self, widget, event):

        if triggers_context_menu(event):
            set_treeview_selected_row(widget, event)
            return self.on_popup_un_rec_menu(widget)

        return False

    def on_popup_un_rec_menu(self, widget):

        item = self.get_selected_item(widget, column=1)
        if item is None:
            return False

        self.ur_popup_menu.set_user(item)

        items = self.ur_popup_menu.get_items()
        items[_("I _Like This")].set_active(item in self.np.config.sections["interests"]["likes"])
        items[_("I _Dislike This")].set_active(item in self.np.config.sections["interests"]["dislikes"])

        self.ur_popup_menu.popup()
        return True

    def update_visuals(self):

        for widget in self.__dict__.values():
            update_widget_visuals(widget)
