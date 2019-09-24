from common import *
import json

_api_perms = json.load(lx.open_resource('api.json'))
_field_perms = json.load(lx.open_resource('content_field.json'))
_uri_perms = json.load(lx.open_resource('content_uri.json'))

def get_class_permissions(dex, class_):
    perms = set()
    perm_api_map = {}
    perm_class_map = {}
    for method in class_.methods():
        for m in method.get_invoked_methods():
            perms.update(_api_perms.get(m, [ ]))
            now_perms = _api_perms.get(m, None)
            if now_perms is not None:
                for now_perm in now_perms:
                    if perm_api_map.get(now_perm, None) is None:
                        perm_api_map[now_perm] = set()
                    perm_api_map[now_perm].update([m])

                    if perm_class_map.get(now_perm, None) is None:
                        perm_class_map[now_perm] = set()
                    perm_class_map[now_perm].update([method.name()])

        for f in method.get_read_fields():
            perms.update(_field_perms.get(f.split('-')[0], [ ]))
        for s in method.get_const_strings():
            if s and s.startswith('content://'):
                for uri in _uri_perms:
                    if s.startswith(uri):
                        perms.update(_uri_perms[uri])
    return perms, perm_api_map, perm_class_map
