import logging.config
import unittest
from unittest import mock

from . import configure


class TestEnvconf(unittest.TestCase):

  dev = None
  prd = None

  devSeq = None
  prdSeq = None

  def setUp(self):
    base = {
      'global' : {
        'server.socket_host' : '127.0.0.1',
        'server.socket_port' : 8080,
        'server.thread_pool' : 8,
      },
      'logging' : {
        'version'    : 1,
        'formatters' : {
          'print' : {
            'format' : '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'
          },
        },
        'handlers' : {
          'console' : {
            'level'     : 'DEBUG',
            'class'     : 'logging.StreamHandler',
            'formatter' : 'print'
          },
        },
        'loggers' : {
          'app' : {
            'handlers'  : ['console'],
            'level'     : 'INFO',
            'propagate' : False
          },
        }
      },
      'app' : {
        'api' : {
          '/' : {
            'request.dispatch' : {
              '()'       : 'xml.parsers.expat.ParserCreate',
              'encoding' : 'utf-8'
            }
          }
        },
      }
    }

    self.prdSeq = (base, {
      'global' : {
        'server.socket_host' : '0.0.0.0',
        'server.thread_pool' : 16,
      },
      '/' : {
        # compression
        'tools.gzip.on'         : True,
        'tools.gzip.mime_types' : ['application/json', 'application/javascript'],
        # authentication
        'tools.auth_basic.on'            : True,
        'tools.auth_basic.realm'         : 'App',
        'tools.auth_basic.checkpassword' : 'ext://clor.test.TestEnvconf'
      }
    })

    self.devSeq = (base, {
      'global' : {
        'server.thread_pool' : None,
      },
      'data' : {
        'a' : 'alpha',
        'b' : 'beta'
      },
      'instances' : {
        'test' : {
          '()' : 'types.SimpleNamespace',
          'a'  : 'cfg://data.a',
          'b'  : 'cfg://data.b',
          'c'  : {
            '()' : 'types.SimpleNamespace',
            'a'  : 'cfg://data.a',
            'b'  : 'cfg://data.b',
          }
        },
      },
      'logging' : {
        'loggers' : {
          'app' : {
            'level' : 'DEBUG'
          }
        },
        'handlers' : {
          'console2': 'cfg://logging.handlers.console',
        }
      },
      'app' : {
        'api' : {
          '/' : {
            'tools.response_headers.on'      : True,
            'tools.response_headers.headers' : [('Access-Control-Allow-Origin', '*')]
          }
        },
        'api2' : 'cfg://app.api'
      }
    })

    self.prd = configure(*self.prdSeq)
    self.dev = configure(*self.devSeq)

  def testInherit(self):
    self.assertEqual('127.0.0.1', self.dev['global']['server.socket_host'])
    self.assertEqual('127.0.0.1', self.dev['global'].get('server.socket_host'))

    self.assertEqual(['console'], self.dev['logging']['loggers']['app']['handlers'])

  def testSet(self):
    self.assertEqual(True, self.prd['/']['tools.gzip.on'])

  def testOverride(self):
    self.assertEqual('0.0.0.0', self.prd['global']['server.socket_host'])
    self.assertEqual('DEBUG', self.dev['logging']['loggers']['app']['level'])

  def testRemove(self):
    self.assertEqual({
      'server.socket_host': '127.0.0.1',
      'server.socket_port': 8080
    }, self.dev['global'])

  def testExternal(self):
    self.assertIs(self.__class__, self.prd['/']['tools.auth_basic.checkpassword'])

  def testFactory(self):
    obj = self.dev['app']['api']['/']['request.dispatch']
    self.assertTrue(repr(obj).startswith('<pyexpat.xmlparser object'))

  def testFactoryManual(self):
    self.dev = configure(*self.devSeq, auto_factory = False)

    obj = self.dev['app']['api']['/']['request.dispatch']
    self.assertTrue(isinstance(obj, logging.config.ConvertingDict))
    self.assertEqual({'encoding': 'utf-8', '()': 'xml.parsers.expat.ParserCreate'}, dict(obj))

  def testFactoryItems(self):
    for _, v in self.dev['app']['api'].items():
      obj = v['request.dispatch']
      self.assertTrue(repr(obj).startswith('<pyexpat.xmlparser object'))

  def testUpdate(self):
    target = {}
    target.update(self.prd['/'])
    self.assertIs(self.__class__, target['tools.auth_basic.checkpassword'])

  def testCfg(self):
    self.assertEqual(
      self.dev['logging']['handlers']['console'],
      self.dev['logging']['handlers']['console2'])
    self.assertIs(
      self.dev['app']['api']['/']['request.dispatch'],
      self.dev['app']['api2']['/']['request.dispatch'])

    # there must be only one resolution of "ext" pseudo-protocol
    with mock.patch('xml.parsers.expat.ParserCreate') as m:
      self.dev = configure(*self.devSeq)
      self.dev['app']['api2']['/']['request.dispatch']
      self.assertEqual(1, len(m.call_args_list))

  def testCfgFromFactory(self):
    actual = self.dev['instances']['test']
    self.assertEqual('alpha', actual.a)
    self.assertEqual('beta', actual.b)
    self.assertEqual('alpha', actual.c.a)
    self.assertEqual('beta', actual.c.b)
