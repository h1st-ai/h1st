from .h1flows.home import Home
from .h1flows.execute import Execute

H1FLOW_URLS = {
    "": Home,
    # "upload/": Upload,
    "execute/<str:model_id>": Execute,
}