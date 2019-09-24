__all__ = [
    'connect_db',
    'query',
    'commit',
    'commit_multi',
]


from .importtypes import *
from .logins import *


def _try_import_sql_engine(name):
    try:
        return __import__(name)
    except ModuleNotFoundError:
        return None

def _import_sql_engine(*engines):
    for name in engines:
        module = _try_import_sql_engine(name)
        if module is not None: return module
    raise ModuleNotFoundError()

SqlEngine = _import_sql_engine('MySQLdb', 'pymysql')
SqlConn = Any


_conns: Dict[str, SqlConn] = { }


def connect_db(db: str) -> SqlConn:
    if db not in _conns:
        _conns[db] = SqlEngine.connect(
            host = SqlHost,
            user = SqlUser,
            password = SqlPassword,
            db = db,
            charset = 'utf8'
        )
    return _conns[db]


def query(db: str, sql: str, args: Any = None, multi: bool = False) -> Any:
    args_ = args

    if '{ARGS}' in sql:
        assert '%' not in sql
        args_ = list(cast(Iterable, args_))
        s = '(' + ','.join('%s' for a in args_) + ')'
        sql = sql.replace('{ARGS}', s)
        multi = True

    cursor = connect_db(db).cursor()
    if args_ is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, args_)
    ret = cursor.fetchall()

    if len(ret) == 0:
        return [ ] if multi else None
    if len(ret[0]) == 1:
        ret = [ row[0] for row in ret ]
    if len(ret) == 1 and not multi:
        ret = ret[0]
    return ret


def commit(db: str, sql: str, args: Any) -> None:
    db_ = connect_db(db)
    db_.cursor().execute(sql, args)
    db_.commit()


def commit_multi(db: str, sql: str, arg_list: Iterable[Any]) -> None:
    db_ = connect_db(db)
    db_.cursor().executemany(sql, list(arg_list))
    db_.commit()


# Check whether this is an OrangeAPK database
try:
    query('main', 'select apk_id from apk limit 1')
except Exception:
    raise ModuleNotFoundError()
