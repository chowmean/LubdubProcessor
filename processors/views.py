from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import json

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def submit(request):
	if request.method == "POST":
		data =  json.loads(request.body.decode('utf-8'))
		content_json = process_process_stat(data["content"])
		content_json["hostname"] = data["hostname"]
		content_json["id"] = data["id"]
		print(content_json)
		return HttpResponse("This method is allowed")
	else:
		return HttpResponse("This method not allowed")


def process_process_stat(content):
	data = {}
	for line in content.splitlines():
		line = line.strip()
		if not line:continue
		data[line.split(":")[0]] = line.split(":")[1].strip()
	return data
