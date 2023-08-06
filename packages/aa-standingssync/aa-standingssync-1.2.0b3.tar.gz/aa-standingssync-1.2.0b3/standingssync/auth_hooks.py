from django.utils.translation import ugettext_lazy as _

from allianceauth.services.hooks import MenuItemHook, UrlHook
from allianceauth import hooks

from . import urls, __title__


class standingssyncMenuItem(MenuItemHook):
    """ This class ensures only authorized users will see the menu entry """

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _(__title__),
            "fas fa-sync-alt",
            "standingssync:index",
            navactive=["standingssync:index"],
        )

    def render(self, request):
        if request.user.has_perm("standingssync.add_syncedcharacter"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return standingssyncMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "standingssync", r"^standingssync/")
