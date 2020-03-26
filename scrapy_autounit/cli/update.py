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
    check_path,
    get_fixture_path,
    discover_fixtures,
)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('spider', help="The spider to update.")
    parser.add_argument('callback', help="The callback to update.")
    parser.add_argument(
        '-f',
        '--fixture',
        help=(
            "The fixture number to update.\n"
            "Can be the fixture number or the fixture name.\n"
            "If not specified, all fixtures will be updated."
        )
    )

    args = parser.parse_args()

    if not inside_project():
        print("No active Scrapy project")
        sys.exit(1)

    project_dir = get_project_dir()
    sys.path.append(project_dir)

    spider = args.spider
    callback = args.callback
    fixture = args.fixture

    to_update = []
    if fixture:
        path = get_fixture_path(project_dir, spider, callback, fixture)
        check_path(parser, path)
        to_update.append(path)
    else:
        to_update = discover_fixtures(project_dir, spider, callback)

    for path in to_update:
        data, _, spider, _ = prepare_callback_replay(path)

        request = request_from_dict(data['request'], spider)

        response_cls = auto_import(
            data['response'].pop('cls', 'scrapy.http.HtmlResponse')
        )
        response = response_cls(request=data["request"], **data['response'])

        data["result"], _ = parse_callback_result(
            request.callback(response), spider
        )

        fixture_dir, filename = os.path.split(path)
        fixture_index = re.search(r"\d+", filename).group()
        add_sample(fixture_index, fixture_dir, filename, data)

        print("Fixture '{}' successfully updated.".format(
            os.path.relpath(path)))

    return 0
