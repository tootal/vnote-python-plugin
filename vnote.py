import re
import os
import time
import json
import string
import configparser

import color

VERSION='0.1a'
conf=configparser.ConfigParser()
current_path=''
current_vpath=['~']
notebooks={}
hide_files=['_vnote.json']
hide_folders=['_v_images','_v_attachments','_v_recycle_bin']
def v_welcome():
	print('Welcome to vnote-python-plugin '+VERSION)
	print(r'''VNote is a note-taking application that knows programmers and Markdown better.
For more information, please visit https://tamlok.github.io/vnote''')
def get_disks():
	disks=""
	for i in string.ascii_uppercase:
		if os.path.isdir(i+':'):
			disks+=i
	return disks

def v_help(cmd):
	print('This is vnote help.')
	if cmd:
		print('info about: ',cmd)

def v_path(path):
	temp_path=current_path.copy()
	temp_vpath=current_vpath.copy()
	status='ok'
	path=path.strip()
	if path[0]=='/':
		temp_path=[]
		temp_vpath=['/']
	elif path[0]=='~':
		temp_path=[]
		temp_vpath=['~']
	rels=path.strip('/~ ').split('/')
	for rel in rels:
		if rel=='':
			pass
		elif rel=='.':
			pass
		elif rel=='..':
			if len(temp_vpath)>1:
				temp_vpath.pop()
				temp_path.pop()
			else:
				pass
		else:
			if temp_vpath[0]=='~':
				if len(temp_vpath)==1:
					try:
						temp_path=notebooks[rel].split('/')
						temp_vpath.append(rel)
					except KeyError:
						status='No such notebook: "'+rel+'".'
				else:
					if os.path.isdir('/'.join(temp_path)+'/'+rel):
						temp_path.append(rel)
						temp_vpath.append(rel)
					else:
						status='No such directory: "'+rel+'".'
			elif temp_vpath[0]=='/':
				if len(temp_vpath)==1:
					if rel in get_disks():
						temp_path=[rel+':']
						temp_vpath.append(rel)
					else:
						status='No such device: "'+rel+'".'
				else:
					if os.path.isdir('/'.join(temp_path)+'/'+rel):
						temp_path.append(rel)
						temp_vpath.append(rel)
					else:
						status='No such directory: "'+rel+'".'
			else:
				pass
	return temp_path,temp_vpath,status

def v_path_show(path):
	if path[0]=='/' and len(path)>1:
		return '/'+'/'.join(path[1:])
	else:
		return '/'.join(path)

def v_get_path_status(path):
	try:
		with open(path+'/_vnote.json',encoding='utf-8') as f:
			v_json=json.load(f)
			v_files={x['name'] for x in v_json['files']}
			v_folders={x['name'] for x in v_json['sub_directories']}
			folders={x for x in os.listdir(path) 
				if os.path.isdir(path+'/'+x)}
			files={x for x in os.listdir(path)
				if os.path.isfile(path+'/'+x)}
			return {
				'status': 'yes',
				'files': files,
				'v_files': v_files,
				'folders': folders,
				'v_folders': v_folders,
				'v_json': v_json
			}
	except FileNotFoundError:
		return {
			'status': 'no'
		}

def v_print_files(path):
	ret=v_get_path_status(path)
	if ret['status']=='no':
		for file in os.listdir(path):
			if os.path.isdir('/'.join(current_path)+'/'+file):
				print(file+'/')
			else:
				print(file)
	else:
		files=ret['files']
		v_files=ret['v_files']
		folders=ret['folders']
		v_folders=ret['v_folders']
		a_files=files.union(v_files)
		a_folders=folders.union(v_folders)
		for i in a_folders:
			if i in v_folders and i in folders:
				print(i+'/')
			elif i in v_folders and i not in folders:
				color.print(i+'/','red')
			elif i not in v_folders and i in folders and i not in hide_folders:
				color.print(i+'/','green')
			else:
				pass
		for i in a_files:
			if i in v_files and i in files:
				print(i)
			elif i in v_files and i not in files:
				color.print(i,'red')
			elif i not in v_files and i in files and i not in hide_files and i.endswith('.md'):
				color.print(i,'green')
			else:
				pass
	
def v_print_disks():
	for c in get_disks():
		print(c)

def v_print_notebooks():
	for c in notebooks:
		color.print(c)

def v_list(paths):
	if paths==None or len(paths)==0:
		paths=['.']
	for path in paths:
		if len(paths)>1:
			print(path+':')
		temp_path,temp_vpath,status=v_path(path)
		if status=='ok':
			if len(temp_vpath)==1:
				if temp_vpath[0]=='/':
					v_print_disks()
				elif temp_vpath[0]=='~':
					v_print_notebooks()
				else:
					pass
			elif len(temp_vpath)==2 and temp_vpath[0]=='/':
				v_print_files(temp_vpath[1]+':/')
			else:
				v_print_files('/'.join(temp_path))
		else:
			print(status)

def v_chdir(path):
	if path==None:
		return 
	elif len(path)==0:
		return 
	elif len(path)==1:
		global current_path
		global current_vpath
		temp_path,temp_vpath,status=v_path(path[0])
		if status=='ok':
			current_path,current_vpath=temp_path,temp_vpath
		else:
			print(status)
	else:
		print('cd: too many arguments')
		return 

def v_init_path(path):
	color.print('[Init] working on '+path,'yellow')
	v_json=v_get_json()
	for i in os.listdir(path):
		if os.path.isdir(path+'/'+i):
			v_json['sub_directories'].append(v_get_folder_json(i))
		elif i.endswith('.md'):
			v_json['files'].append(v_get_file_json(path+'/'+i))
	with open(path+'/_vnote.json','w',encoding='utf-8') as f:
		json.dump(v_json,f)

def v_init_path_r(path):
	v_init_path(path)
	for i in os.listdir(path):
		if os.path.isdir(path+'/'+i):
			v_init_path_r(path+'/'+i)

def v_sync_path(path):
	print('[Sync] working on '+path)
	ret=v_get_path_status(path)
	if ret['status']=='no':
		v_init_path_r(path)
	else:
		v_json=ret['v_json']
		files=ret['files']
		v_files=ret['v_files']
		folders=ret['folders']
		v_folders=ret['v_folders']
		a_files=files.union(v_files)
		a_folders=folders.union(v_folders)
		# print(v_folders,folders)
		# print(v_files,files)
		for i in a_folders:
			if i in v_folders and i in folders:
				pass
			elif i in v_folders and i not in folders:
				for x in v_json['sub_directories']:
					if x['name']==i:
						v_json['sub_directories'].remove(x)
				color.print('[Sync] remove folder: '+path+'/'+i+'/','red')
			elif i not in v_folders and i in folders and i not in hide_folders:
				v_json['sub_directories'].append(v_get_folder_json(i))
				color.print('[Sync] add folder: '+path+'/'+i+'/','green')
			else:
				pass
		for i in a_files:
			if i in v_files and i in files:
				pass
			elif i in v_files and i not in files:
				for x in v_json['files']:
					if x['name']==i:
						v_json['files'].remove(x)
				color.print('[Sync] remove file: '+path+'/'+i,'red')
			elif i not in v_files and i in files and i not in hide_files and i.endswith('.md'):
				v_json['files'].append(v_get_file_json(path+'/'+i))
				color.print('[Sync] add file: '+path+'/'+i,'green')
			else:
				pass
		with open(path+'/_vnote.json','w',encoding='utf-8') as f:
			json.dump(v_json,f)

def v_sync_path_r(path):
	v_sync_path(path)
	for file in os.listdir(path):
		if os.path.isdir(path+'/'+file) and file not in hide_folders:
			v_sync_path_r(path+'/'+file)

def v_time(t):
	return time.strftime("%Y-%m-%dT%H:%M:%ST")

def v_get_file_json(path):
	return {
		'attachment_folder': "",
		'attachments': [],
		'created_time': v_time(os.path.getctime(path)),
		'modified_time': v_time(os.path.getmtime(path)),
		'name': os.path.basename(path),
		'tags': []
	}

def v_get_folder_json(name):
	return {
		'name': name
	}

def v_get_json():
	return {
		'created_time': v_time(time.time()),
		'files': [],
		'sub_directories': [],
		'version': "1"
	}

def v_sync(paths):
	if paths==None or len(paths)==0:
		paths=['.']
	for path in paths:
		if len(paths)>1:
			print(path+':')
		temp_path,temp_vpath,status=v_path(path)
		# print(temp_path,temp_vpath,status)
		if status=='ok':
			if len(temp_vpath)==1:
				if temp_vpath[0]=='/':
					print('Can not sync "/".')
					continue
				elif temp_vpath[0]=='~':
					for x in notebooks:
						v_sync_path_r(notebooks[x])
				else:
					pass
			elif len(temp_vpath)==2 and temp_vpath[0]=='/':
				print('Can not sync "'+temp_vpath[1]+':/"')
				continue
			else:
				v_sync_path_r('/'.join(temp_path))
		else:
			print(status)

def v_read_ini():
	session_path=os.path.expanduser('~')+'\\AppData\\Roaming\\vnote\\session.ini'
	conf.read(session_path,encoding='utf-8')
	global notebooks
	global current_path
	global current_vpath
	size=int(conf['notebooks']['size'])
	current_notebook=int(conf['global']['current_notebook'])
	for i in range(1,size+1):
		name=str(conf['notebooks'][str(i)+'\\name'])
		path=str(conf['notebooks'][str(i)+'\\path'])
		notebooks[name]=path
		if i-1==current_notebook:
			current_vpath.append(name)
			current_path=path.split('/')

def v_version():
	print('this is version information')

def v_cmds(cmds):
	args=re.findall(r"""(".+?"|'.+?'|\S+)""",cmds)
	# print(args)
	argv=len(args)

	if argv==1:
		if args[0][-1]=='?':
			v_help(args[0][:-1])
			return 'ok'
		elif args[0][-2:]=='/?':
			v_help(args[0][:-2])
			return 'ok'
		elif args[0] in ('exit','quit','q'):
			return 'exit'
		elif args[0] in ('version','ver','v'):
			v_version()
			return 'ok'
		elif args[0] == 'pwd':
			print('/'.join(current_vpath))
			return 'ok'
		elif args[0] == 'disk':
			print('\n'.join(get_disks()))
			return 'ok'

	if args[0] in ('help','h','?'):
		v_help(args[1:])
	elif args[0] in ('ls','dir','l'):
		v_list(args[1:])
	elif args[0] in ('cd'):
		v_chdir(args[1:])
	elif args[0] in ('sync','s'):
		v_sync(args[1:])
	# elif args[0] in ('init','i'):
		# v_init(args[1:])
	else:
		return 'undefined'

def main():
	v_welcome()
	color.print('ATTENTION: YOU MUST BACKUP FILES BEFORE ANY OPERATION.','red')
	v_read_ini()
	print('Last start: '+conf['global']['last_start_time'])
	while True:
		cmd_str=input('vnote:'+v_path_show(current_vpath)+'> ')
		if cmd_str.strip()=="":
			continue
		if cmd_str.lstrip()[0]==':':
			os.system(cmd_str.lstrip()[1:])
			continue
		signal=v_cmds(cmd_str)
		if signal=='exit':
			print('Bye')
			break
		elif signal=='undefined':
			print('Undefined command: "'+cmd_str+'". Try "help".')
		elif signal=='ok':
			continue
		else:
			pass


if __name__ == '__main__':
	main()