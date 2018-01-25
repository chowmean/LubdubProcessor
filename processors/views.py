from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from pymongo import MongoClient
from config import CLIENT_ACCESS_TOKEN,SERVICE_NAME
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def submit(request):
	if request.method == "POST":
		data =  json.loads(request.body.decode('utf-8'))
		if "api_access_token" not in data:
			return HttpResponseForbidden(json.dumps({"message":"permissions error"}))
		else:
			if data["api_access_token"]!=CLIENT_ACCESS_TOKEN[SERVICE_NAME]:
				return HttpResponseForbidden(json.dumps({"message":"permissions error"}))
		content_json = process_process_stat(data["content"])
		content_json["hostname"] = data["hostname"]
		content_json["id"] = data["id"]
		content_json["service"] = SERVICE_NAME
		content_json["type"] = data["type"]
		content_json["datetime"] = datetime.datetime.now()	
		client = MongoClient()
		db = client['lubdub']
		cpu_procs = db.cpu_procs
		content_id = cpu_procs.insert_one(content_json).inserted_id
		return HttpResponse({"insert_id":content_id})
	else:
		return HttpResponseForbidden("This method not allowed")

def get_cpu_info(request):
	if request.method != "GET":
		return HttpResponseForbidden(json.dumps({"message":"method not allowed"}))
	else:
		return "hello"
		

def process_process_stat(content):
	data = {}
	for line in content.splitlines():
		line = line.strip()
		if not line:continue
		data[line.split(":")[0]] = line.split(":")[1].strip()
	return data
