from argparse import ArgumentParser

from tornado.ioloop import IOLoop
import jwt

from fooapi_async.app import run, create_schema, init_settings, settings

parser = ArgumentParser()

subparsers = parser.add_subparsers(dest='subcommand')

run_parser = subparsers.add_parser('run')
run_parser.add_argument('--settings-file', type=str, required=True)

init_db_parser = subparsers.add_parser('init-db')
init_db_parser.add_argument('--settings-file', type=str, required=True)

create_jwt_parser = subparsers.add_parser('create-jwt')
create_jwt_parser.add_argument('private_key', type=str)
create_jwt_parser.add_argument('creator_id', type=int)


if __name__ == '__main__':
    args = parser.parse_args()
    if args.subcommand == 'run':
        run(args.settings_file)
    elif args.subcommand == 'init-db':
        async def run_create_schema():
            init_settings(args.settings_file)
            await create_schema(settings)
        IOLoop.current().run_sync(run_create_schema)
    elif args.subcommand == 'create-jwt':
        with open(args.private_key, 'r') as f:
            key = f.read()

        token = jwt.encode({'id': args.creator_id}, key,
                           algorithm='RS256')
        print(token)
