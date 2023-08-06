from unittest import TestCase

from chibi.snippet.xml import guaranteed_list, compress_dummy_list


class test_guaranteed_list(TestCase):

    def setUp( self ):
        self.example = {
            'args': 'nmap -oX - -sn 200.200.200.200/24',
            'debugging': {'level': '0'},
            'host': {
                'address': {'addr': '200.200.200.200', 'addrtype': 'ipv4'},
                'hostnames': None,
                'status': {'reason': 'conn-refused', 'reason_ttl': '0',
                           'state': 'up'},
                'times': {'rttvar': '3768', 'srtt': '204', 'to': '100000'}},
            'runstats': {
                'finished': {
                    'elapsed': '6.82', 'exit': 'success',
                    'summary': (
                        'Nmap done at Thu May  2 15:24:38 '
                        '2019; 256 IP addresses (1 host up) '
                        'scanned in 6.82 seconds' ),
                    'time': '1556828678',
                    'timestr': 'Thu May  2 15:24:38 2019'},
                'hosts': {'down': '255', 'total': '256', 'up': '1'}},
            'scanner': 'nmap', 'start': '1556828671',
            'startstr': 'Thu May  2 15:24:31 2019', 'verbose': {'level': '0'},
            'version': '7.70', 'xmloutputversion': '1.04'}

        self.expected = {
            'args': 'nmap -oX - -sn 200.200.200.200/24',
            'debugging': {'level': '0'},
            'host': [ {
                'address': {'addr': '200.200.200.200', 'addrtype': 'ipv4'},
                'hostnames': None,
                'status': {'reason': 'conn-refused', 'reason_ttl': '0',
                           'state': 'up'},
                'times': {'rttvar': '3768', 'srtt': '204', 'to': '100000'}} ],
            'runstats': {
                'finished': {
                    'elapsed': '6.82', 'exit': 'success',
                    'summary': (
                        'Nmap done at Thu May  2 15:24:38 '
                        '2019; 256 IP addresses (1 host up) '
                        'scanned in 6.82 seconds' ),
                    'time': '1556828678',
                    'timestr': 'Thu May  2 15:24:38 2019'},
                'hosts': {'down': '255', 'total': '256', 'up': '1'}},
            'scanner': 'nmap', 'start': '1556828671',
            'startstr': 'Thu May  2 15:24:31 2019', 'verbose': {'level': '0'},
            'version': '7.70', 'xmloutputversion': '1.04'}

    def test_should_convert_host_in_list( self ):
        result = guaranteed_list( self.example, 'host' )
        self.assertEqual( self.expected, result )


class test_compress_dummy_list(TestCase):

    def setUp( self ):
        self.example = {
            'regions': { 'region': 'asdf' },
            'attrs': { 'attr': { 'asdf': 'asdf' } },
            'lists': [ '', [], [ { 'regions': { 'region': 'qq' } } ] ],
            'list': [
                '',
                [ { 'regions': { 'region': 'qq' } } ],
                [
                    {
                        'regions': {
                            'region': [ { 'asdfs': { 'asdf': 1 } } ]
                        }
                    },
                ],
            ],
        }

        self.expected = {
            'attrs': {'asdf': 'asdf'},
            'list': [
                '',
                [ { 'regions': 'qq' } ],
                [ { 'regions': [ { 'asdfs': 1 } ] } ] ],
            'lists': [ '', [], [ { 'regions': 'qq' } ] ],
            'regions': 'asdf', }

    def test_should_convert_host_in_list( self ):
        result = compress_dummy_list( self.example )
        self.assertEqual( self.expected, result )
