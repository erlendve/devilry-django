from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from abstract_is_admin import AbstractIsAdmin
from save_interface import SaveInterface

class BaseNode(AbstractIsAdmin, SaveInterface):
    """
    The base class of the Devilry hierarchy. Implements basic functionality
    used by the other Node classes. This is an abstract datamodel, so it
    is never used directly.


    .. attribute:: short_name

        A django.db.models.SlugField_ with max 20 characters. Only numbers,
        letters, '_' and '-'.

    .. attribute:: long_name

        A django.db.models.CharField_ with max 100 characters. Gives a longer
        description than :attr:`short_name`.
    """

    def __unicode__(self):
        return self.get_path()

    def get_path(self):
        """ Get the unique path to this node.

        :return:
            A ``'.'`` separated list containing the short_name of this
            node and every parentnode required to make this path unique. For
            everything from Subject and down, this is up to subject, and for Node,
            this is up to a Node with ``parentnode==None``.
        """
        return self.parentnode.get_path() + "." + self.short_name
    get_path.short_description = _('Path')

    def get_admins(self):
        """ Get a string with the username of all administrators on this node
        separated by comma and a space like: ``"uioadmin, superuser"``.

        Note that admins on parentnode(s) is not included.
        """
        return u', '.join([u.username for u in self.admins.all()])
    get_admins.short_description = _('Administrators')

    def is_admin(self, user_obj):
        """ Check if the given user is admin on this node or any parentnode.

        :param user_obj: A django.contrib.auth.models.User_ object.
        :rtype: bool
        """
        try:
            self.admins.get(pk=user_obj.pk)
        except User.DoesNotExist, e:
            if self.parentnode:
                return self.parentnode.is_admin(user_obj)
        else:
            return True
        return False

    def _can_save_id_none(self, user_obj):
        """ Used by all except Node, which overrides. """
        return self.parentnode.is_admin(user_obj)

    def can_save(self, user_obj):
        """
        Check if the current user can save the current object. Unlike is_admin,
        this method returns true for superusers, and if this is a new object (id=None),
        we check if the user is admin on any parent.
        """
        if user_obj.is_superuser:
            return True
        if self.id == None:
            return self._can_save_id_none(user_obj)
        elif self.is_admin(user_obj):
            return True
        else:
            return False
