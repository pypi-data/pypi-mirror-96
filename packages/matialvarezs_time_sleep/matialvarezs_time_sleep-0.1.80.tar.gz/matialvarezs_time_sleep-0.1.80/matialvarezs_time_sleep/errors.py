from django.utils.translation import ugettext as _

BASE_ERROR_CODE = 204672

ERROR_NAME = {
	"code" : BASE_ERROR_CODE | 1, "message" : _("Base error"),
}