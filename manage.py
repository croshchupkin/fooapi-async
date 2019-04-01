from argparse import ArgumentParser
from os.path import expanduser

from tornado.ioloop import IOLoop
import jwt

from fooapi_async.app import run, create_schema, init_settings, drop_schema

parser = ArgumentParser()
parser.add_argument('--settings-file', type=str, required=True)

subparsers = parser.add_subparsers(dest='subcommand')

run_parser = subparsers.add_parser('run')

init_db_parser = subparsers.add_parser('init-db')

create_jwt_parser = subparsers.add_parser('create-jwt')
create_jwt_parser.add_argument('creator_id', type=int)


if __name__ == '__main__':
    args = parser.parse_args()
    if args.subcommand == 'run':
        run(args.settings_file)
    elif args.subcommand == 'init-db':
        async def run_create_schema():
            init_settings(args.settings_file)
            await drop_schema()
            await create_schema()
        IOLoop.current().run_sync(run_create_schema)
    elif args.subcommand == 'create-jwt':
        init_settings(args.settings_file)
        from fooapi_async.app import settings

        with open(expanduser(settings.priv_key), 'r') as f:
            key = f.read()

        token = jwt.encode({'id': args.creator_id}, key,
                           algorithm='RS256')
        print(token)
