from .h1flows.home import Home
from .h1flows.execute import Execute
from .h1flows.upload import Upload

H1FLOW_URLS = {
    "": Home,
    "upload/": Upload,
    "execute/<str:model_id>": Execute,
}