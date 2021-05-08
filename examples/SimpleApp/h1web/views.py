from django.http import HttpResponse

def default(request):
	return HttpResponse("<HTML><BODY><CENTER><H1></H1></CENTER></BODY></HTML>")
