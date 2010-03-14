from django.utils.translation import ugettext as _
from devilry.addons.dashboard.dashboardplugin_registry import register

register('add_delivery_key', 
         'Add Delivery', 
         '/student/choose-assignment/', 
         description = _('Add delivery.'),
         icon='ikon.png',
         student_access=True,
         )


register('show_history_key', 
         'Show History', 
         '/student/show-history/', 
         description = _('Show History.'),
         icon='ikon.png', 
         student_access=True,
         )