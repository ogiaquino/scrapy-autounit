import os
from glob import glob
from scrapy_autounit.utils import (
    unpickle_data,
    decompress_data,
    get_project_settings
)


def check_path(parser, path):
    if not os.path.isfile(path):
        parser.error("Fixture '{}' not found".format(path))


def check_args(parser, args):
    if not args.spider or not args.callback or not args.fixture:
        parser.error("If -p is not present, -s, -c and -f are required.")


def parse_fixture_arg(arg):
    try:
        int(arg)
        return 'fixture{}.bin'.format(arg)
    except ValueError:
        pass
    if not arg.endswith('.bin'):
        return '{}.bin'.format(arg)
    return arg


def get_fixture_data(path):
    with open(path, 'rb') as f:
        raw_data = f.read()
    fixture_info = unpickle_data(decompress_data(raw_data), 'utf-8')
    if 'fixture_version' in fixture_info:
        encoding = fixture_info['encoding']
        data = unpickle_data(fixture_info['data'], encoding)
    else:
        data = fixture_info  # legacy tests (not all will work, just utf-8)
    return data


def get_callback_dir(project_dir, spider, callback):
    settings = get_project_settings()
    base_path = settings.get(
        'AUTOUNIT_BASE_PATH',
        default=os.path.join(project_dir, 'autounit')
    )
    tests_dir = os.path.join(base_path, 'tests')
    extra_path = settings.get('AUTOUNIT_EXTRA_PATH') or ''
    return os.path.join(tests_dir, spider, extra_path, callback)


def get_fixture_path(project_dir, spider, callback, fixture):
    callback_dir = get_callback_dir(project_dir, spider, callback)
    fixture = parse_fixture_arg(fixture)
    return os.path.join(callback_dir, fixture)


def discover_fixtures(project_dir, spider, callback):
    callback_dir = get_callback_dir(project_dir, spider, callback)
    target = os.path.join(callback_dir, "*.bin")
    return glob(target)
