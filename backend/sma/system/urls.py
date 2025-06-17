from django.urls import path
from rest_framework import routers

from sma.system.views.api_white_list import ApiWhiteListViewSet
from sma.system.views.area import AreaViewSet
from sma.system.views.cppqcp_review_result import ReviewResultViewSet
from sma.system.views.csrfile_review_result import CSRReviewResultViewSet
from sma.system.views.dept import DeptViewSet
from sma.system.views.dictionary import DictionaryViewSet
from sma.system.views.file_list import FileViewSet
from sma.system.views.login_log import LoginLogViewSet
from sma.system.views.menu import MenuViewSet
from sma.system.views.menu_button import MenuButtonViewSet
from sma.system.views.message_center import MessageCenterViewSet
from sma.system.views.operation_log import OperationLogViewSet
from sma.system.views.role import RoleViewSet
from sma.system.views.role_menu import RoleMenuPermissionViewSet
from sma.system.views.role_menu_button_permission import RoleMenuButtonPermissionViewSet
from sma.system.views.system_config import SystemConfigViewSet
from sma.system.views.user import UserViewSet
from sma.system.views.menu_field import MenuFieldViewSet

from sma.system.views.mco_pdf import MCOPdfFileViewSet
from sma.system.views.mco_keywords_search import MCOParagraphViewSet
from sma.system.views.mco_cmp import MCOCMPPairViewSet
from sma.system.views.mco_file_history import MCOFileHistoryViewSet
from sma.system.views.mco_monitor import MonitorViewSet

from sma.system.views.stack_pdf import STACKPdfFileViewSet
from sma.system.views.stack_material import STACKMaterialViewSet

from sma.system.views.cppqcp_pdf import PdfFileViewSet
from sma.system.views.cppqcp_review_version import ReviewVersionViewSet
from sma.system.views.csrfile_pdf import CSRPdfFileViewSet
from sma.system.views.csrfile_review_version import CSRReviewVersionViewSet
from sma.system.views.iqa_data import IqaDataViewSet
from sma.system.views.iqa_dir import IqaDirViewSet
from sma.system.views.mco_monitor import MonitorConfigSerializer

system_url = routers.SimpleRouter()
system_url.register(r'menu', MenuViewSet)
system_url.register(r'menu_button', MenuButtonViewSet)
system_url.register(r'role', RoleViewSet)
system_url.register(r'dept', DeptViewSet)
system_url.register(r'user', UserViewSet)
system_url.register(r'operation_log', OperationLogViewSet)
system_url.register(r'dictionary', DictionaryViewSet)
system_url.register(r'area', AreaViewSet)
system_url.register(r'file', FileViewSet)
system_url.register(r'api_white_list', ApiWhiteListViewSet)
system_url.register(r'system_config', SystemConfigViewSet)
system_url.register(r'message_center', MessageCenterViewSet)
system_url.register(r'role_menu_button_permission', RoleMenuButtonPermissionViewSet)
system_url.register(r'role_menu_permission', RoleMenuPermissionViewSet)
system_url.register(r'column', MenuFieldViewSet)

cppqcp_url = routers.SimpleRouter()
cppqcp_url.register(r'cppqcp_pdf', PdfFileViewSet)
cppqcp_url.register(r'cppqcp_vreview', ReviewVersionViewSet)
cppqcp_url.register(r'cppqcp_reviewrst', ReviewResultViewSet)

csrfile_url = routers.SimpleRouter()
csrfile_url.register(r'csrfile_pdf', CSRPdfFileViewSet)
csrfile_url.register(r'csrfile_vreview', CSRReviewVersionViewSet)
csrfile_url.register(r'csrfile_reviewrst', CSRReviewResultViewSet)

mco_url = routers.SimpleRouter()
mco_url.register(r'mco_pdf', MCOPdfFileViewSet)
mco_url.register(r'mco_para', MCOParagraphViewSet)
mco_url.register(r'mco_cmp', MCOCMPPairViewSet)
mco_url.register(r'mco_file_history', MCOFileHistoryViewSet)
mco_url.register(r'monitor-config', MonitorViewSet)

stack_url = routers.SimpleRouter()
stack_url.register(r'stack_pdf', STACKPdfFileViewSet)
stack_url.register(r'stack_materials', STACKMaterialViewSet)

iqa_url = routers.SimpleRouter()
iqa_url.register(r'iqa_data', IqaDataViewSet)
iqa_url.register(r'iqa_dir', IqaDirViewSet)

urlpatterns = [
    path('user/export/', UserViewSet.as_view({'post': 'export_data', })),
    path('user/import/', UserViewSet.as_view({'get': 'import_data', 'post': 'import_data'})),
    path('system_config/save_content/', SystemConfigViewSet.as_view({'put': 'save_content'})),
    path('system_config/get_association_table/', SystemConfigViewSet.as_view({'get': 'get_association_table'})),
    path('system_config/get_table_data/<int:pk>/', SystemConfigViewSet.as_view({'get': 'get_table_data'})),
    path('system_config/get_relation_info/', SystemConfigViewSet.as_view({'get': 'get_relation_info'})),
    path('login_log/', LoginLogViewSet.as_view({'get': 'list'})),
    path('login_log/<int:pk>/', LoginLogViewSet.as_view({'get': 'retrieve'})),
    path('dept_lazy_tree/', DeptViewSet.as_view({'get': 'dept_lazy_tree'})),
]
urlpatterns += system_url.urls
urlpatterns += cppqcp_url.urls
urlpatterns += csrfile_url.urls
urlpatterns += mco_url.urls
urlpatterns += stack_url.urls
urlpatterns += iqa_url.urls
