from .h1flows.api import Api
from .h1flows.home import Home

REST_URLS = {
#    "api/users/": Api,
    "api/users/": Api.users,
#    "api/users/": Home,
}
