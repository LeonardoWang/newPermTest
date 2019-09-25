import pscout
import axplorer

from common import Apk

import os
import zipfile
import sys

#import library
total_permission_list = []
usage_perm_list = []
lib_perm_list = []
over_perm_list = []
perm_map = {}
lib_map = []
library_list = []
find_list = []

api_maps = {}
class_map = {}

def get_permission(content):
    perm_list = content.split('\n')
    for perm_value in perm_list:
        if perm_value.find('uses-permission') >= 0:
            perm_list = perm_value.split(' ')
            for now_perm in perm_list:
                if now_perm.find("name=")>=0:
                    now_perm = now_perm.replace('name=','')
                    now_perm = now_perm.replace('\'','')
                    total_permission_list.append(now_perm)
        elif perm_value.find('permission:') >= 0:
            now_perm = perm_value.replace('permission:','')
            total_permission_list.append(now_perm)

def get_method_perm(file_path):
    f = open(file_path)
    for lines in f.readlines():
        now_line = lines.strip().split('  ::  ')
        if len(now_line)==2:
            end = now_line[0].index('(')
            perm_map[now_line[0][0:end]] = now_line[1]

def get_library_map(file_path):
    f = open(file_path)
    for lines in f.readlines():
        now_line = lines.strip()[1:]
        lib_map.append(now_line)

def get_dex_file(file_path):
    permission_content = os.popen('./tools/aapt dump permissions {}'.format(file_path)).read()
    #print(permission_content)
    get_permission(permission_content)
    for dex in list(Apk(file_path)):
        for class_ in dex.classes:
            pscout_perms, pscout_api_maps, pscout_class_maps = pscout.get_class_permissions(dex, class_)
            axplorer_perms, axplorer_api_maps, axplorer_class_maps = axplorer.get_class_permissions(dex, class_)

   
            #print(class_.name())
            tag = False
            tmp_class_name = class_.name()[1:-1]
            for lib in lib_map:
                if tmp_class_name.startswith(lib):
                    tag = True
                    lib = lib.replace('/','.')
                    if lib not in library_list:
                        library_list.append(lib)
                    break
                    new_class_name = tmp_class_name.replace('/','.')

            for perm in pscout_perms:
            	if perm in total_permission_list and perm not in usage_perm_list:
            		usage_perm_list.append(perm)
            	if tag and perm in total_permission_list and perm not in lib_perm_list:
            		lib_perm_list.append(perm)
            for perm in axplorer_perms:
            	if perm in total_permission_list and perm not in usage_perm_list:
            		usage_perm_list.append(perm)
            	if tag and perm in total_permission_list and perm not in lib_perm_list:
            		lib_perm_list.append(perm)

            for perm in axplorer_api_maps:
                if api_maps.get(perm, None) is None:
                    api_maps[perm] = set()
                api_maps[perm].update(axplorer_api_maps[perm])

            for perm in pscout_api_maps:
                if api_maps.get(perm, None) is None:
                    api_maps[perm] = set()
                api_maps[perm].update(pscout_api_maps[perm])

            for perm in axplorer_class_maps:
                if class_map.get(perm, None) is None:
                    class_map[perm] = set()
                class_map[perm].update(axplorer_class_maps[perm])

            for perm in pscout_class_maps:
                if class_map.get(perm, None) is None:
                    class_map[perm] = set()
                class_map[perm].update(pscout_class_maps[perm])

    for perm in total_permission_list:
        if perm not in usage_perm_list:
            over_perm_list.append(perm)
    print('total_permission_list',total_permission_list)
    print('')
    print('true use permission',usage_perm_list)
    print('')
    print('library',library_list)
    print('')
    print('library permissiom usage',lib_perm_list)
    print('')
    print('overprilege permission', over_perm_list)

    for perm in usage_perm_list:
        print(perm)
        if api_maps.get(perm, None) is not None:
            for i in api_maps[perm]:
                print('     api call ',i)
        if class_map.get(perm, None) is not None:
            for i in class_map[perm]:
                print('     method call ',i)

get_method_perm('./tools/framework-map-25.txt')
get_method_perm('./tools/sdk-map-25.txt')
get_library_map('./tools/libs.txt')
#print(lib_map)

get_dex_file(sys.argv[1])
