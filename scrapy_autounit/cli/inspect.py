import sys
import json
import scrapy
import argparse
from datetime import datetime
from scrapy.utils.project import inside_project
from scrapy.utils.python import to_unicode
from scrapy_autounit.utils import get_project_dir
from scrapy_autounit.cli.utils import (
    get_fixture_data,
    get_fixture_path,
    check_path,
    check_args,
)


def parse_data(data):
    if isinstance(data, (dict, scrapy.Item)):
        return {parse_data(k): parse_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [parse_data(x) for x in data]
    elif isinstance(data, bytes):
        return to_unicode(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, (int, float)):
        return data
    return str(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--path',
        help='The full path for the fixture to inspect'
    )
    parser.add_argument(
        '-s',
        '--spider',
        help='The spider where to look fixtures for'
    )
    parser.add_argument(
        '-c',
        '--callback',
        help='The callback where to look fixtures for (requires spider)'
    )
    parser.add_argument(
        '-f',
        '--fixture',
        help=(
            'The fixture number to inspect (requires spider and callback).'
            'It can be an integer indicating the fixture number or a string'
            'indicating the fixture name'
        )
    )

    args = parser.parse_args()

    if not inside_project():
        print('No active Scrapy project')
        sys.exit(1)

    project_dir = get_project_dir()
    sys.path.append(project_dir)

    path = args.path
    if not path:
        check_args(parser, args)
        path = get_fixture_path(
            project_dir, args.spider, args.callback, args.fixture)

    check_path(parser, path)

    data = parse_data(get_fixture_data(path))
    print(json.dumps(data))

    return 0
