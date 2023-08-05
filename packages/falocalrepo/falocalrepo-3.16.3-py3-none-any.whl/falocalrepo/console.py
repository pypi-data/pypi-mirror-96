from datetime import datetime
from inspect import cleandoc
from os import environ
from os.path import abspath
from os.path import getsize
from os.path import isfile
from os.path import join
from re import match
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Tuple
from typing import Union

from faapi import __version__ as __faapi_version__
from falocalrepo_database import FADatabase
from falocalrepo_database import __version__ as __database_version__
from falocalrepo_server import __version__ as __server_version__
from falocalrepo_server import server

from .__version__ import __version__
from .commands import check_process
from .commands import latest_version
from .commands import make_journal
from .commands import make_submission
from .commands import move_files_folder
from .commands import print_items
from .commands import print_users
from .commands import search
from .download import clean_username
from .download import download_journals as download_journals_
from .download import download_submissions as download_submissions_
from .download import download_users as download_users_
from .download import download_users_update
from .download import read_cookies
from .download import save_journal
from .download import save_submission
from .download import write_cookies


class MalformedCommand(Exception):
    pass


class UnknownCommand(Exception):
    pass


class MultipleInstances(Exception):
    pass


def raiser(e: Exception) -> Callable[[], None]:
    def inner(*_):
        raise e

    return inner


def docstring_parameter(*args, **kwargs):
    def inner(obj: {__doc__}) -> {__doc__}:
        obj.__doc__ = obj.__doc__.format(*args, **kwargs)
        return obj

    return inner


def parameters_multi(args: Iterable[str]) -> Dict[str, List[str]]:
    params: Dict[str, List[str]] = {}
    for param, value in map(lambda p: p.split("=", 1), args):
        param = param.strip()
        params[param] = [*params.get(param, []), value]

    return params


def parameters(args: Iterable[str]) -> Dict[str, str]:
    return {p: v for p, v in map(lambda p: p.split("=", 1), args)}


def parse_args(args_raw: Iterable[str]) -> Tuple[Dict[str, str], List[str]]:
    opts: List[str] = []
    args: List[str] = []

    for i, arg in enumerate(args_raw):
        if match(r"\w+=\w+", arg):
            opts.append(arg)
        elif arg == "--":
            args.extend(args_raw[i + 1:])
            break
        else:
            args.extend(args_raw[i:])
            break

    return parameters(opts), args


def check_update(version: str, package: str) -> bool:
    if (latest := latest_version(package)) and latest != version:
        print(f"New {package} version available: {version} > {latest}")
        return True
    return False


def help_(comm: str = "", op: str = "", *_rest) -> str:
    """
    USAGE
        falocalrepo help [<command> [<operation>]]

    ARGUMENTS
        <command>       Command to get the help of
        <operation>     Command operation to get the help of

    AVAILABLE COMMANDS
        help            Display the manual of help
        init            Display the manual of init
        config          Display the manual of config
        download        Display the manual of download
        database        Display the manual of database
    """

    f = {
        "": console,
        "help": help_,
        "init": init,
        "config": config,
        "config_list": config_list,
        "config_cookies": config_cookies,
        "config_files-folder": config_files_folder,
        "download": download,
        "download_users": download_users,
        "download_update": download_update,
        "download_submissions": download_submissions,
        "download_journals": download_journals,
        "database": database,
        "database_info": database_info,
        "database_history": database_history,
        "database_search-users": database_search_users,
        "database_search-submissions": database_search_submissions,
        "database_search-journals": database_search_journals,
        "database_add-submission": database_add_submission,
        "database_add-journal": database_add_journal,
        "database_remove-users": database_remove_users,
        "database_remove-submissions": database_remove_submissions,
        "database_remove-journals": database_remove_journals,
        "database_server": database_server,
        "database_merge": database_merge,
        "database_clean": database_clean,
    }.get(f"{comm}_{op}" if op else comm, None)

    if f is None:
        raise UnknownCommand(f"{comm} {op}".strip())

    return cleandoc(f.__doc__)


def init():
    """
    USAGE
        falocalrepo init

    DESCRIPTION
        The init command initialises the database or, if one is already present,
        updates to a new version - if available - and then exits.

        It can be used to create the database and then manually edit it, or to
        update it to a new version without calling other commands.
    """

    print("Database ready")


def config_list(db: FADatabase, *_rest):
    """
    USAGE
        falocalrepo config list

    DESCRIPTION
        Prints a list of stored settings.
    """

    cookie_a, cookie_b = read_cookies(db)
    folder: str = db.settings["FILESFOLDER"]
    print("cookie a:", cookie_a)
    print("cookie b:", cookie_b)
    print("folder  :", folder)


def config_cookies(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo config cookies [<cookie1 name>=<cookie1 value>] ...
                    [<cookieN name>=<cookieN value>]

    ARGUMENTS
        <cookie name>   The name of the cookie (e.g. a)
        <cookie value>  The value of the cookie

    DESCRIPTION
        Read or modify stored cookies.

    EXAMPLES
        falocalrepo config cookies a=a1b2c3d4-1234 b=e5f6g7h8-5678
    """

    if not args:
        for c in read_cookies(db):
            print(f"cookie {c['name']}:", c['value'])
    elif len(args) == 2:
        write_cookies(db, **parse_args(args)[0])
    else:
        raise MalformedCommand("cookies needs two arguments")


def config_files_folder(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo config files-folder [<new folder>]

    ARGUMENTS
        <new folder>    Path to new files folder

    DESCRIPTION
        Read or modify the folder used to store submission files. This can be any
        path relative to the folder of the database. If a new value is given, the
        program will move any files to the new location.
    """

    if not args:
        print("files folder:", db.settings["FILESFOLDER"])
    elif len(args) == 1:
        move_files_folder(db.settings["FILESFOLDER"], args[0])
        db.settings["FILESFOLDER"] = args[0]
    else:
        raise MalformedCommand("files-folder needs one argument")


def config(db: FADatabase, comm: str = "", *args: str):
    """
    USAGE
        falocalrepo config [<setting> [<value1>] ... [<valueN>]]

    ARGUMENTS
        <setting>       Setting to read/edit
        <value>         New setting value

    AVAILABLE SETTINGS
        list            List settings
        cookies         Cookies for the API
        files-folder    Files download folder

    DESCRIPTION
        The config command allows to change the settings used by the program.
    """

    {
        "": config_list,
        "list": config_list,
        "cookies": config_cookies,
        "files_folder": config_files_folder,
    }.get(comm, raiser(UnknownCommand(f"config {comm}")))(db, *args)


def download_users(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo download users <user1>[,...,<userN>] <folder1>[,...,<folderN>]

    ARGUMENTS
        <user>      Username
        <folder>    One of gallery, scraps, favorites, journals

    DESCRIPTION
        Download specific user folders. Requires two arguments with comma separated
        users and folders. Prepending 'list-' to a folder allows to list all remote
        items in a user folder without downloading them. Supported folders are:
            * gallery
            * scraps
            * favorites
            * journals

    EXAMPLES
        falocalrepo download users tom,jerry gallery,scraps,journals
        falocalrepo download users tom,jerry list-favorites
    """

    if len(args) != 2:
        raise MalformedCommand("users needs two arguments")

    users_tmp: List[str] = list(filter(bool, map(clean_username, args[0].split(","))))
    users: List[str] = sorted(set(users_tmp), key=users_tmp.index)
    folders_tmp: List[str] = list(filter(bool, map(str.strip, args[1].split(","))))
    folders: List[str] = sorted(set(folders_tmp), key=folders_tmp.index)
    download_users_(db, users, folders)


def download_update(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo download update [stop=<stop n>] [<user1>,...,<userN>]
                    [<folder1>,...,<folderN>]

    ARGUMENTS
        <stop n>    Number of submissions to find in database before stopping,
                    defaults to 1
        <user>      Username
        <folder>    One of gallery, scraps, favorites, journals

    DESCRIPTION
        Update the repository by checking the previously downloaded folders
        (gallery, scraps, favorites or journals) of each user and stopping when it
        finds a submission that is already present in the repository. Can pass a
        list of users and/or folders that will be updated if in the database. To
        skip users, use '@' as argument. The 'stop=<n>' option allows to stop
        updating after finding n submissions in a user's database entry, defaults
        to 1. If a user is deactivated, the folders in the database will be
        prepended with a '!' and the user will be skipped when update is called
        again.

    EXAMPLES
        falocalrepo download update stop=5
        falocalrepo download update @ gallery,scraps
        falocalrepo download update tom,jerry
    """

    users: List[str] = []
    folders: List[str] = []
    opts, args = parse_args(args)
    if args and args[0] != "@":
        users_tmp: List[str] = list(filter(bool, map(clean_username, args[0].split(","))))
        users = sorted(set(users_tmp), key=users_tmp.index)
    if args[1:] and args[1] != "@":
        folders_tmp: List[str] = list(filter(bool, map(str.strip, args[1].split(","))))
        folders = sorted(set(folders_tmp), key=folders_tmp.index)
    download_users_update(db, users, folders, int(opts.get("stop", 1)))


def download_submissions(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo download submissions <id1> ... [<idN>]

    ARGUMENTS
        <id>    Submission ID

    DESCRIPTION
        Download specific submissions. Requires submission ID's provided as separate
        arguments.

    EXAMPLES
        falocalrepo download submissions 12345678 13572468 87651234
    """

    if not args:
        raise MalformedCommand("submissions needs at least one argument")
    sub_ids_tmp: List[str] = list(filter(str.isdigit, args))
    sub_ids: List[str] = sorted(set(sub_ids_tmp), key=sub_ids_tmp.index)
    download_submissions_(db, sub_ids)


def download_journals(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo download journals <id1> ... [<idN>]

    ARGUMENTS
        <id>    Journal ID

    DESCRIPTION
        Download specific journals. Requires journal ID's provided as separate
        arguments.

    EXAMPLES
        falocalrepo download journals 123456 135724 876512
    """

    if not args:
        raise MalformedCommand("journals needs at least one argument")
    journal_ids_tmp: List[str] = list(filter(str.isdigit, args))
    journal_ids: List[str] = sorted(set(journal_ids_tmp), key=journal_ids_tmp.index)
    download_journals_(db, journal_ids)


def download(db: FADatabase, comm: str = "", *args: str):
    """
    USAGE
        falocalrepo download <operation> [<option>=<value>] [<arg1>] ... [<argN>]

    ARGUMENTS
        <operation>     The download operation to execute
        <option>        Option for the download command
        <value>         Value of an option
        <arg>           Argument for the download command

    AVAILABLE COMMANDS
        users           Download users
        update          Update database using the users and folders already saved
        submissions     Download single submissions
        journals        Download single journals

    DESCRIPTION
        The download command performs all download operations get and update users,
        submissions, and journals.
    """

    if not comm:
        raise MalformedCommand("download needs a command")

    {
        "users": download_users,
        "update": download_update,
        "submissions": download_submissions,
        "journals": download_journals,
    }.get(comm, raiser(UnknownCommand(f"download {comm}")))(db, *args)


def database_info(db: FADatabase, *_rest):
    """
    USAGE
        falocalrepo database info

    DESCRIPTION
        Show database information, statistics and version.
    """

    print("Size        :", f"{getsize(db.database_path) / 1e6:.1f}MB")
    print("Users       :", len(db.users))
    print("Submissions :", len(db.submissions))
    print("Journals    :", len(db.journals))
    print("History     :", len(db.settings.read_history()) - 1)
    print("Version     :", db.settings["VERSION"])


def database_history(db: FADatabase):
    """
    USAGE
        falocalrepo database history

    DESCRIPTION
        Show commands history.
    """

    for time, command in db.settings.read_history():
        print(str(datetime.fromtimestamp(time)), command)


def database_search_users(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database search-users [<param1>=<value1>] ...
                    [<paramN>=<valueN>]

    ARGUMENTS
        <param>     Search parameter
        <value>     Value of the parameter

    DESCRIPTION
        Search the users entries using metadata fields. Search parameters can be
        passed multiple times to act as OR values. All columns of the users table
        are supported. Parameters can be lowercase. If no parameters are supplied, a
        list of all users will be returned instead.

    EXAMPLES
        falocalrepo database search-users folders=%gallery% gallery=%0012345678%
    """

    results: List[Dict[str, str]] = search(db.users, parameters_multi(args))
    print_users(results)
    print(f"Found {len(results)} results")


def database_search_submissions(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database search-submissions [<param1>=<value1>] ...
                    [<paramN>=<valueN>]

    ARGUMENTS
        <param>     Search parameter
        <value>     Value of the parameter

    DESCRIPTION
        Search the submissions entries using metadata fields. Search parameters can
        be passed multiple times to act as OR values. All columns of the submissions
        table are supported. Parameters can be lowercase. If no parameters are
        supplied, a list of all submissions will be returned instead.

    EXAMPLES
        falocalrepo database search-submissions tags=%cat,%mouse% date=2020-% \\
            category=%artwork% order="AUTHOR" order="ID"
        falocalrepo database search-submissions tags=%cat% tags=%mouse% \\
            date=2020-% category=%artwork%
    """

    results: List[Dict[str, Union[int, str]]] = search(db.submissions, parameters_multi(args))
    print_items(results)
    print(f"Found {len(results)} results")


def database_search_journals(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database search-journals [<param1>=<value1>] ...
                    [<paramN>=<valueN>]

    ARGUMENTS
        <param>     Search parameter
        <value>     Value of the parameter

    DESCRIPTION
        Search the journals entries using metadata fields. Search parameters can
        be passed multiple times to act as OR values. All columns of the journals
        table are supported. Parameters can be lowercase. If no parameters are
        supplied, a list of all submissions will be returned instead.

    EXAMPLES
        falocalrepo database search-journals date=2020-% author=CatArtist \\
            order="ID DESC"
        falocalrepo database search-journals date=2020-% date=2019-% \\
            content=%commission%
    """

    results: List[Dict[str, Union[int, str]]] = search(db.journals, parameters_multi(args))
    print_items(results)
    print(f"Found {len(results)} results")


def database_add_user(db: FADatabase, *args):
    """
    USAGE
        falocalrepo database add-user <param1>=<value1> ... <paramN>=<valueN>

    ARGUMENTS
        <param>     Make parameter
        <value>     Value of the parameter

    DESCRIPTION
        Add a user to the database manually. If the user is already present, the
        folders parameter will overwrite the existing value if given. The following
        parameters are necessary for a user entry to be accepted:
            * 'username'
        The following parameters are optional:
            * 'folders'

    EXAMPLES
        falocalrepo database add-user username=tom folders=gallery,scraps
    """

    make_params: Dict[str, str] = parameters(args)
    db.users.new_user(username) if (username := make_params["username"]) not in db.users else None
    if make_params.get("folders", None) is not None:
        folders: List[str] = db.users[username]["FOLDERS"].split(",")
        folders_new: List[str] = make_params["folders"].split(",")
        for f in folders:
            db.users.remove_user_folder(username, f) if f not in folders_new else None
        for f in folders_new:
            db.users.add_user_folder(username, f) if f not in folders else None
    db.commit()


def database_add_submission(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database add-submissions <param1>=<value1> ... <paramN>=<valueN>

    ARGUMENTS
        <param>     Make parameter
        <value>     Value of the parameter

    DESCRIPTION
        Add a submission to the database manually. The submission file is not
        downloaded and can instead be provided with the extra parameter
        'file_local_url'. The following parameters are necessary for a submission
        entry to be accepted:
            * 'id'
            * 'title'
            * 'author'
            * 'date' date in the format YYYY-MM-DD
            * 'category'
            * 'species'
            * 'gender'
            * 'rating'
            * 'folder' gallery or scraps
        The following parameters are optional:
            * 'tags' comma-separated tags
            * 'description'
            * 'file_url' the url of the submission file
            * 'file_local_url' if provided, take the submission file from this path
                and put it into the database

    EXAMPLES
        falocalrepo database add-submission id=12345678 title='cat & mouse' \\
            author=CartoonArtist date=2020-08-09 category=Artwork \\
            species='Unspecified / Any' gender=Any rating=General \\
            tags=cat,mouse,cartoon description="$(cat description.html)" \\
            file_url='http://remote.url/to/submission.file' \\
            file_local_url='path/to/submission.file' folder=gallery
    """

    make_params = parameters(args)
    make_params["id_"] = make_params.get("id", "")
    if "id" in make_params:
        del make_params["id"]
    save_submission(db, *make_submission(**make_params), user_update=False)


def database_add_journal(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database add-journal <param1>=<value1> ... <paramN>=<valueN>

    ARGUMENTS
        <param>     Make parameter
        <value>     Value of the parameter

    DESCRIPTION
        Add a journal to the database manually. The following parameters are
        necessary for a journal entry to be accepted:
            * 'id'
            * 'title'
            * 'author'
            * 'date' date in the format YYYY-MM-DD
        The following parameters are optional:
            * 'content' the body of the journal

    EXAMPLES
        falocalrepo database add-journal id=12345678 title="An Update" \\
            author=CartoonArtist date=2020-08-09 content="$(cat journal.html)"
    """

    make_params = parameters(args)
    make_params["id_"] = make_params.get("id", "")
    if "id" in make_params:
        del make_params["id"]
    save_journal(db, make_journal(**make_params), user_update=False)


def database_remove_users(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database remove-users <user1> ... [<userN>]

    ARGUMENTS
        <user>  Username

    DESCRIPTION
        Remove specific users from the database.
    """

    for user in map(clean_username, args):
        print("Deleting", user)
        del db.users[user]
        db.commit()


def database_remove_submissions(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database remove-submissions <id1> ... [<idN>]

    ARGUMENTS
        <id>    Submission ID

    DESCRIPTION
        Remove specific submissions from the database.
    """

    for sub in args:
        print("Deleting", sub)
        del db.submissions[int(sub)]
        db.commit()


def database_remove_journals(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database remove-journals <id1> ... [<idN>]

    ARGUMENTS
        <id>    Journal ID

    DESCRIPTION
        Remove specific journals from the database.
    """

    for jrn in args:
        print("Deleting", jrn)
        del db.journals[int(jrn)]
    db.commit()


@docstring_parameter(f"https://pypi.org/project/falocalrepo-server/{__server_version__}")
def database_server(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database server [host=<host>] [port=<port>]

    ARGUMENTS
        <host>  Host address
        <port>  Port

    DESCRIPTION
        Starts a server at <host>:<port> to navigate the database, defaults to
        0.0.0.0:8080. For more details on usage see
        {0}.

    EXAMPLES
        falocalrepo database server host=127.0.0.1 port=5000
    """

    opts, _ = parse_args(args)
    server(db.database_path, **opts)
    print()


def database_merge(db: FADatabase, *args: str):
    """
    USAGE
        falocalrepo database merge <path>

    ARGUMENTS
        <path>  Path to second database file

    DESCRIPTION
        Merge (or create) the database in the current folder with a second database
        located at 'path'.

    EXAMPLES
        falocalrepo database merge ~/Documents/FA/FA.db
    """

    if len(args) != 1:
        raise MalformedCommand("merge needs one argument")
    elif not isfile(args[0]):
        raise FileNotFoundError(f"No such file or directory: '{args[0]}'")
    with FADatabase(args[0]) as db2:
        print(f"Merging with database {db2.database_path}...")
        db.update(db2)
        db.commit()
        print("Done")


def database_clean(db: FADatabase, *_rest):
    """
    USAGE
        falocalrepo database clean

    DESCRIPTION
        Clean the database using the SQLite VACUUM function.
    """

    db.vacuum()


@docstring_parameter(f"https://pypi.org/project/falocalrepo-database/{__database_version__}")
def database(db: FADatabase, comm: str = "", *args: str):
    """
    USAGE
        falocalrepo database [<operation> [<param1>=<value1> ... <paramN>=<valueN>]]

    ARGUMENTS
        <operation>         The database operation to execute
        <param>             Parameter for the database operation
        <value>             Value of the parameter

    AVAILABLE COMMANDS
        info                Show database information
        history             Show commands history
        search-users        Search users
        search-submissions  Search submissions
        search-journals     Search journals
        add-user            Add a user to the database manually
        add-submission      Add a submission to the database manually
        add-journal         Add a journal to the database manually
        remove-users        Remove users from database
        remove-submissions  Remove submissions from database
        remove-journals     Remove submissions from database
        server              Start local server to browse database
        merge               Merge with a second database
        clean               Clean the database with the VACUUM function

    DESCRIPTION
        The database command allows to operate on the database. Used without an
        operation command shows the database information, statistics (number of
        users and submissions and time of last update), and version. For more
        details on tables see {0}.

        All search operations are conducted case-insensitively using the SQLite like
        expression which allows for limited pattern matching. For example this
        expression can be used to search two words together separated by an unknown
        amount of characters '%cat%mouse%'. Fields missing wildcards will only match
        an exact result, i.e. 'cat' will only match a field equal to 'cat' tag
        whereas '%cat%' wil match a field that has contains 'cat'.

        All search operations support the extra 'order', 'limit', and 'offset'
        parameters with values in SQLite 'ORDER BY' clause, 'LIMIT' clause format,
        and 'OFFSET' clause. The 'order' parameter supports all fields of the
        specific search command.
    """

    {
        "": database_info,
        "info": database_info,
        "history": database_history,
        "search-users": database_search_users,
        "search-submissions": database_search_submissions,
        "search-journals": database_search_journals,
        "add-user": database_add_user,
        "add-submission": database_add_submission,
        "add-journal": database_add_journal,
        "remove-users": database_remove_users,
        "remove-submissions": database_remove_submissions,
        "remove-journals": database_remove_journals,
        "server": database_server,
        "merge": database_merge,
        "clean": database_clean,
    }.get(comm, raiser(UnknownCommand(f"database {comm}")))(db, *args)


@docstring_parameter(__version__, __database_version__, __server_version__, __faapi_version__)
def console(comm: str = "", *args: str) -> None:
    """
    falocalrepo: {0}
    falocalrepo-database: {1}
    falocalrepo-server: {2}
    faapi: {3}

    USAGE
        falocalrepo [-h | -v | -d | -s | -u] [<command> [<operation>] [<arg1> ...
                    <argN>]]

    ARGUMENTS
        <command>       The command to execute
        <operation>     The operation to execute for the given command
        <arg>           The arguments of the command or operation

    GLOBAL OPTIONS
        -h, --help      Display this help message
        -v, --version   Display version
        -d, --database  Display database version
        -s, --server    Display server version
        -u, --updates   Check for updates on PyPi

    AVAILABLE COMMANDS
        help            Display the manual of a command
        init            Create/update the database and exit
        config          Manage settings
        download        Perform downloads
        database        Operate on the database
    """

    if not comm:
        print(help_())
        return
    elif comm in ("-h", "--help"):
        print(help_())
        return
    elif comm == "help":
        print(help_(*args))
        return
    elif comm in ("-v", "--version"):
        print(__version__)
        return
    elif comm in ("-d", "--database"):
        print(__database_version__)
        return
    elif comm in ("-s", "--server"):
        print(__server_version__)
        return
    elif comm in ("-u", "--updates"):
        v = check_update(__version__, "falocalrepo")
        v += check_update(__database_version__, "falocalrepo-database")
        v += check_update(__server_version__, "falocalrepo-server")
        v += check_update(__faapi_version__, "faapi")
        if not v:
            print("No updates available")
        return
    elif comm not in (init.__name__, config.__name__, download.__name__, database.__name__):
        raise UnknownCommand(comm)
    elif check_process(p := "falocalrepo") > 1:
        raise MultipleInstances(f"Another instance of {p} was detected")

    if environ.get("FALOCALREPO_DEBUG", None) is not None:
        print(f"Using FALOCALREPO_DEBUG")

    # Initialise and prepare database
    database_path = "FA.db"

    if db_path := environ.get("FALOCALREPO_DATABASE", None):
        print(f"Using FALOCALREPO_DATABASE: {db_path}")
        database_path = db_path if db_path.endswith(".db") else join(db_path, database_path)

    db: FADatabase = FADatabase(abspath(database_path))

    try:
        db.upgrade()
        db.settings.add_history(f"{comm} {' '.join(args)}".strip())
        db.commit()

        if comm == init.__name__:
            init()
        elif comm == config.__name__:
            config(db, *args)
        elif comm == download.__name__:
            download(db, *args)
        elif comm == database.__name__:
            database(db, *args)
    finally:
        # Close database and update totals
        if db is not None:
            db.commit()
            db.close()
