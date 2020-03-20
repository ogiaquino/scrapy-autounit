import re
import os
import sys
import argparse
from scrapy.utils.project import inside_project
from scrapy.utils.reqser import request_from_dict
from scrapy_autounit.utils import (
    add_sample,
    auto_import,
    get_project_dir,
    parse_callback_result,
    prepare_callback_replay,
)
from scrapy_autounit.cli.utils import (
    get_fixture_path,
    check_path,
    check_args,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',
        '--spider',
        help='The spider where to look fixtures for update'
    )
    parser.add_argument(
        '-c',
        '--callback',
        help='The callback where to look fixtures for update (requires spider)'
    )
    parser.add_argument(
        '-f',
        '--fixture',
        help=(
            'The fixture number to update (requires spider and callback).'
            'It can be an integer indicating the fixture number or a string'
            'indicating the fixture name'
        )
    )
    parser.add_argument(
        '-p',
        '--path',
        help='The full path for the fixture to update'
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
            project_dir, args.spider, args.callback, args.fixture
        )

    check_path(parser, path)

    data, _, spider, _ = prepare_callback_replay(path)

    request = request_from_dict(data['request'], spider)

    response_cls = auto_import(
        data['response'].pop('cls', 'scrapy.http.HtmlResponse')
    )
    response = response_cls(request=data["request"], **data['response'])

    data["result"], _ = parse_callback_result(
        request.callback(response), spider
    )

    test_dir, filename = os.path.split(path)
    fixture_index = re.search(r"\d+", filename).group()
    add_sample(fixture_index, test_dir, filename, data)

    print("Fixture '{}' successfully updated.".format(os.path.relpath(path)))
    return 0
