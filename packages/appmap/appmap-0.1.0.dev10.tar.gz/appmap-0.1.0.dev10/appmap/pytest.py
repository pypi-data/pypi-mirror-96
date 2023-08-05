import logging
import pytest
import os
import os.path
import re

import inflection

from appmap._implementation import configuration, env, generation, recording
from appmap._implementation.utils import fqname

logger = logging.getLogger(__name__)

try:
    # Make sure we have hooks installed if we're testing a django app.
    # pylint: disable=unused-import
    import appmap.django  # noqa: F401
except ImportError:
    pass  # probably no django


class FuncItem:
    def __init__(self, pyfuncitem):
        self.item = pyfuncitem

    @property
    def class_name(self):
        return self.item.cls.__name__

    @property
    def defined_class(self):
        return fqname(self.item.cls)

    @property
    def method_id(self):
        return self.item.originalname

    def is_in_class(self):
        return self.item.cls is not None
    has_feature_group = is_in_class

    @property
    def feature_group(self):
        test_name = self.class_name
        if test_name.startswith('Test'):
            test_name = test_name[4:]
        return inflection.humanize(inflection.titleize(test_name))

    @property
    def feature(self):
        return inflection.humanize(self.test_name)

    @property
    def scenario_name(self):
        name = '%s%s' %(self.feature[0].lower(), self.feature[1:])
        if self.has_feature_group():
            name = ' '.join([self.feature_group, name])
        return name

    @property
    def test_name(self):
        ret = self.item.name
        return re.sub('^test.?_', '', ret)

    @property
    def filename(self):
        fname = self.item.name
        if self.item.cls:
            fname = '%s_%s' % (self.defined_class, fname)
        fname = re.sub('[^a-zA-Z0-9-_]', '_', fname)
        if fname.endswith('_'):
            fname = fname[:-1]
        return fname

    @property
    def metadata(self):
        ret = {}
        if self.is_in_class():
            ret['feature_group'] = self.feature_group
            ret['recording'] = {
                'defined_class': self.defined_class,
                'method_id': self.method_id
            }
        ret.update({
            'name': self.scenario_name,
            'feature': self.feature
        })
        return ret


@pytest.hookimpl(hookwrapper=True)
def pytest_runtestloop(session):
    if not env.enabled():
        yield
        return

    session.appmap_path = os.path.join(
        configuration.Config().output_dir, 'pytest'
    )
    logger.debug('pytest_runtestloop, creating %s', session.appmap_path)
    os.makedirs(session.appmap_path, exist_ok=True)
    session.appmap_metadata = {
        'app': configuration.Config().name,
        'frameworks': [{
            'name': 'pytest',
            'version': pytest.__version__

        }],
        'recorder': {
            'name': 'pytest'
        }
    }
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    if not env.enabled():
        yield
        return

    session = item.session
    item = FuncItem(item)
    metadata = dict(session.appmap_metadata)
    metadata.update(item.metadata)
    logger.debug('pytest_pyfunc_call, metadata %s', repr(metadata))
    fname = item.filename + '.appmap.json'
    path = os.path.join(session.appmap_path, fname)

    def write_recording(r):
        with open(path, 'w') as appmap_file:
            appmap_file.write(generation.dump(r, metadata))
        logger.info('wrote recording %s', path)

    logger.info('starting recording %s', path)
    r = recording.Recording(exit_hook=write_recording)
    with r:
        yield
