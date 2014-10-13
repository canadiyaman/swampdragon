from ..connections.sockjs_connection import SubscriberConnection
from ..route_handler import BaseRouter
from .dragon_test_case import DragonTestCase
from .mock_connection import TestConnection
from .test_subscriber_connection import TestSession
import json


class FooRouter(BaseRouter):
    route_name = 'foo-router'
    valid_verbs = ['write_session', 'read_session']

    def write_session(self, **kwargs):
        self.connection.session_store.set('key', kwargs['value'])

    def read_session(self):
        val = self.connection.session_store.get('key')
        self.send(val)


class TestSessions(DragonTestCase):
    def setUp(self):
        self.session = TestSession()
        self.connection = SubscriberConnection(self.session)
        self.session_store = self.connection.session_store

    def test_read_from_session(self):
        val = 'test val'
        self.session_store.set('a_key', val)
        self.assertEqual(val, self.session_store.get('a_key'))

    def test_overwrite_value(self):
        val = 'test val'
        self.session_store.set('a_key', val)
        self.session_store.set('a_key', 'updated val')
        self.assertEqual('updated val', self.session_store.get('a_key'))

    def test_write_dict(self):
        data = {'a': 'val', 'b': 1}
        key = 'key'
        self.session_store.set(key, data)
        data_from_session = json.loads(self.session_store.get(key))
        self.assertDictEqual(data, data_from_session)

    def test_session_from_router(self):
        """
        Ensure that sessions are unique per connection
        """
        connection_a = TestConnection()
        connection_b = TestConnection()
        foo_router = FooRouter(connection_a)
        foo_router.write_session(**{'value': 'a value'})
        foo_router.read_session()
        self.assertEqual(connection_a.get_last_message()['data'], 'a value')

        foo_router = FooRouter(connection_b)
        foo_router.read_session()
        self.assertNotEqual(connection_b.get_last_message()['data'], 'a value')
