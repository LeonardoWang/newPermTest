from common import *

from collections import defaultdict


ApiPerms = None
ContentUriPerms = None
ContentFieldPerms = None
IntentPerms = None


class _ContentUriPatterns:
    def __init__(self):
        self.patterns = [ ]

    def add_pattern(self, pattern, perms):
        exact, prefix, suffix = pattern.split('|')
        self.patterns.append( (exact, prefix, suffix, perms) )

    def get(self, string, default = None):
        ret = set()
        for exact, prefix, suffix, perms in self.patterns:
            if exact and string != exact: continue
            if prefix and not string.startswith(prefix): continue
            # We are testing string constants instead of final function arguments,
            # the suffix may be concatenated later
            #if suffix and not string.endswith(suffix): continue
            ret = ret.union(perms)
        return list(ret)


def init():
    global ApiPerms, ContentUriPerms, ContentFieldPerms, IntentPerms

    api_file = lx.open_resource('mapping_5.1.1.csv')
    content_uri_file = lx.open_resource('jellybean_contentproviderpermission.txt')
    content_field_file = lx.open_resource('jellybean_contentproviderfieldpermission.txt')
    intent_file = lx.open_resource('jellybean_intentpermissions.txt')

    ApiPerms = defaultdict(set)
    api_file.readline()
    for line in api_file:
        class_, method, proto, perm, ver = line.split(',')
        method_name = 'L%s;->%s' % (class_, method)
        ApiPerms[method_name].add(perm)
    ApiPerms = { k : list(v) for k, v in ApiPerms.items() }

    tmp_uri_perms = defaultdict(set)
    for line in content_uri_file:
        parts = line.strip().split(' ')
        if len(parts) == 3: parts.append(None)
        uri, rw, perm, type_ = parts
        if type_ is None:
            pattern = uri + '||'
        elif type_ == 'path':
            pattern = '|' + uri + '|'
        elif type_ == 'pathPrefix':
            pattern = '|' + uri + '|'
        elif type_ == 'pathPattern':
            prefix, suffix = uri.split('*')
            uri = '|' + prefix + '|' + suffix
        else:
            assert False
        tmp_uri_perms[pattern].add(perm)
    ContentUriPerms = _ContentUriPatterns()
    for pattern, perms in tmp_uri_perms.items():
        ContentUriPerms.add_pattern(pattern, list(perms))

    ContentFieldPerms = defaultdict(set)
    cur_perm = None
    for line in content_field_file:
        line = line.strip()
        if line[0] != '<':
            assert line.startswith('PERMISSION:')
            cur_perm = line[11:]
            continue
        class_, type_, field = line[1:-1].split(' ')
        class_ = class_[:-1].replace('.', '/')
        field_name = 'L%s;->%s' % (class_, field)
        ContentFieldPerms[field_name].add(cur_perm)
    ContentFieldPerms = { k : list(v) for k, v in ContentFieldPerms.items() }

    IntentPerms = defaultdict(set)
    for line in intent_file:
        intent, perm, rw = line.split(' ')
        IntentPerms[intent].add(perm)
    IntentPerms = { k : list(v) for k, v in IntentPerms.items() }

init()
