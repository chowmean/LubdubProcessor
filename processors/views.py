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
		if data["type"] == "CPU PROCESS":
			content_json = process_process_stat(data["content"])
		if data["type"] == "CPU":
			content_json = process_cpu_stat(data["content"])
		if data["type"] == "MEMORY":
                        content_json = process_memory_info(data["content"])	
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
		client = MongoClient()
		db = client['lubdub']
		cpu_procs = db.cpu_procs
		cpu_stats = cpu_procs.find({"service":SERVICE_NAME,"type":"CPU"})
		data=[]
		for stats in cpu_stats:
			stats.pop('_id')
			stats["datetime"]=stats["datetime"].strftime('%H:%M:%S %m/%d/%Y')
			data.append(stats)
		return HttpResponse(json.dumps({"data":data}))


def get_proc_info(request):
	return "hello"

def process_process_stat(content):
	data = {}
	for line in content.splitlines():
		line = line.strip()
		if not line:continue
		data[line.split(":")[0]] = line.split(":")[1].strip()
	return data

def process_memory_info(content):
	data = {}
	for line in content.splitlines():
		line = line.strip()
		if not line:continue
		data[line.split(":")[0]] = line.split(":")[1].strip()
	return data

def process_cpu_stat(content):
	data = {}
	i=-1
	for line in content.splitlines():
		if line.startswith('cpu'):
			index = ""
			cpu = line.split(" ")
			if i>=0:
				index = "cpu"+str(i)
			else:
				index = "cpu"
			data[index] = {}
			data[index]["user_process"] = cpu[1].strip()
			data[index]["niced_process"] = cpu[2].strip()
			data[index]["system_process"] = cpu[3].strip()
			data[index]["idle"] = cpu[4].strip()
			data[index]["io_wait"] = cpu[5].strip()
			data[index]["process_hard_intr"] = cpu[6].strip()
			data[index]["process_soft_intr"] = cpu[7].strip()
			i=i+1
			
		elif line.startswith('intr'):
			pass
		elif line.startswith('ctxt'):
			data["context_switch"] = line.split(" ")[1].strip()
		elif line.startswith('btime'):
			data["uptime_epoch"] = line.split(" ")[1].strip()
		elif line.startswith('processes'):
			data["process_threads"] = line.split(" ")[1].strip()
		elif line.startswith('procs_running'):
			data["running_process"] = line.split(" ")[1].strip()
		elif line.startswith('procs_blocked'):
			data["blocked_process"] = line.split(" ")[1].strip()
	return data
