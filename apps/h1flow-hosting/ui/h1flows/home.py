from h1st.core.step import H1StepWithWebUI
from django.http import HttpResponse 

class Home(H1StepWithWebUI):
    def handle_get(self, req):
        print(req)
        return HttpResponse("This is Home")