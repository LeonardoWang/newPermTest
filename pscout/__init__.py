from . import permdb as db

import subprocess

def get_class_permissions(dex, class_, db = db):
    method_ids = set()
    str_ids = set()
    field_ids = set()

    api_perms = set()
    content_uri_perms = set()
    intent_perms = set()
    content_field_perms = set()

    perm_api_map = {}
    perm_class_map = {}

    for method in class_.methods():
        method_ids = set()
        str_ids = set()
        field_ids = set()
        str_ids.update(method.get_const_string_ids())
        method_ids.update(method.get_invoked_method_ids())
        field_ids.update(method.get_read_field_ids())

    
        for m in method_ids:
            api = dex.get_method_name(m)
            api_perms.update(db.ApiPerms.get(api, [ ]))

            now_perms = db.ApiPerms.get(api, None)
            if now_perms is not None:
                for now_perm in now_perms:
                    if perm_api_map.get(now_perm, None) is None:
                        perm_api_map[now_perm] = set()
                    perm_api_map[now_perm].update([api])

                    if perm_class_map.get(now_perm, None) is None:
                        perm_class_map[now_perm] = set()
                    perm_class_map[now_perm].update([method.name()])
        
        for s in str_ids:
            uri = dex.get_string(s)
            if uri.startswith('content://'):
                content_uri_perms.update(db.ContentUriPerms.get(uri, [ ]))
                now_perms = db.ContentUriPerms.get(uri, None)
            else:
                intent_perms.update(db.IntentPerms.get(uri, [ ]))
                now_perms = db.IntentPerms.get(uri, None)

            if now_perms is not None:
                for now_perm in now_perms:

                    if perm_class_map.get(now_perm, None) is None:
                        perm_class_map[now_perm] = set()
                    perm_class_map[now_perm].update([method.name()])

        
        for f in field_ids:
            field = dex.get_field_name(f)
            for perm in db.ContentFieldPerms.get(field, [ ]):
                content_field_perms.add(perm)

                if perm_class_map.get(perm, None) is None:
                        perm_class_map[perm] = set()
                perm_class_map[perm].update([method.name()])

    return set(list(api_perms) + list(content_uri_perms) + list(content_field_perms) + list(intent_perms)),perm_api_map, perm_class_map


def get_manifest_permissions(apk_path, db = db):
    cmd = ['aapt', 'd', 'xmltree', apk_path, 'AndroidManifest.xml']
    r = subprocess.run(cmd, stdout = subprocess.PIPE)
    if r.returncode != 0: return None
    lines = r.stdout.decode('utf8').split('\n')

    intents = [ ]

    intent_indent = None
    action_indent = None
    for line in lines:
        l = line.lstrip()
        indent = len(line) - len(l)
        if l.startswith('E: intent-filter '):
            intent_indent = indent
        elif intent_indent is not None and intent_indent < indent:
            if l.startswith('E: action '):
                action_indent = indent
            elif action_indent is not None and action_indent < indent:
                if l.startswith('A: android:name'):
                    intents.append(l.split('"')[1])

    perms = sum( (db.IntentPerms.get(intent, [ ]) for intent in intents), [ ])
    return list(set(perms))
