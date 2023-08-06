import grp
import pwd
from unittest import TestCase

from chibi.nix import (
    _parse_passwd, _parse_group, get_passwd, get_group,
    user_exists, group_exists, mem_info
)


class Test_passwd( TestCase ):
    def setUp( self ):
        self.all_passwd = filter(
            lambda x: x.pw_name != "nobody", pwd.getpwall() )

    def test_parse_passwd_should_have_the_same_data_as_the_raw( self ):
        for raw_passwd in self.all_passwd:
            with self.subTest( f"parsing {raw_passwd}" ):
                passwd = _parse_passwd( raw_passwd )

                self.assertEqual( passwd.name, raw_passwd.pw_name )
                self.assertEqual( passwd.passwd, raw_passwd.pw_passwd )
                self.assertEqual( passwd.uid, raw_passwd.pw_uid )
                self.assertEqual( passwd.gid, raw_passwd.pw_gid )
                self.assertEqual( passwd.gecos, raw_passwd.pw_gecos )
                self.assertEqual( passwd.dir, raw_passwd.pw_dir )
                self.assertEqual( passwd.shell, raw_passwd.pw_shell )

    def test_get_passwd_should_raise_a_exeption_if_no_args_are_send( self ):
        with self.assertRaises( ValueError ):
            get_passwd()

    def test_get_passwd_by_uid_should_parse_the_passwd( self ):
        for raw_passwd in self.all_passwd:
            with self.subTest( f"parsing {raw_passwd}" ):
                parse_passwd = _parse_passwd( raw_passwd )
                passwd = get_passwd( uid=raw_passwd.pw_uid )
                self.assertEqual( passwd.keys(), parse_passwd.keys() )

    def test_get_passwd_by_name_should_parse_the_passwd( self ):
        for raw_passwd in self.all_passwd:
            with self.subTest( f"parsing {raw_passwd}" ):
                parse_passwd = _parse_passwd( raw_passwd )
                passwd = get_passwd( name=raw_passwd.pw_name )
                self.assertEqual( passwd.keys(), parse_passwd.keys() )

    def test_get_passwd_by_name_and_uid_should_be_the_same( self ):
        for raw_passwd in self.all_passwd:
            with self.subTest( f"parsing {raw_passwd}" ):
                name_passwd = get_passwd( name=raw_passwd.pw_name )
                uid_passwd = get_passwd( uid=raw_passwd.pw_uid )
                self.assertEqual( name_passwd, uid_passwd )


class Test_group( TestCase ):
    def setUp( self ):
        self.all_group = grp.getgrall()

    def test_parse_group_should_have_the_same_data_as_the_raw( self ):
        for raw_group in self.all_group:
            group = _parse_group( raw_group )

            self.assertEqual( group.name, raw_group.gr_name )
            self.assertEqual( group.passwd, raw_group.gr_passwd )
            self.assertEqual( group.gid, raw_group.gr_gid )
            self.assertEqual( group.mem, raw_group.gr_mem )

    def test_get_group_should_raise_a_exeption_if_no_args_are_send( self ):
        with self.assertRaises( ValueError ):
            get_group()

    def test_get_group_by_gid_should_parse_the_group( self ):
        for raw_group in self.all_group:
            parse_passwd = _parse_group( raw_group )
            group = get_group( gid=raw_group.gr_gid )
            self.assertEqual( group.keys(), parse_passwd.keys() )

    def test_get_group_by_name_should_parse_the_group( self ):
        for raw_group in self.all_group:
            parse_passwd = _parse_group( raw_group )
            group = get_group( name=raw_group.gr_name )
            self.assertEqual( group.keys(), parse_passwd.keys() )

    def test_get_group_by_name_and_gid_should_be_the_same( self ):
        for raw_group in self.all_group:
            name_passwd = get_group( name=raw_group.gr_name )
            gid_passwd = get_group( gid=raw_group.gr_gid )
            self.assertEqual( name_passwd, gid_passwd )


class Test_exists( TestCase ):
    def test_user_exists_only_name( self ):
        self.assertTrue( user_exists( name='root' ) )

    def test_user_exists_only_uid( self ):
        self.assertTrue( user_exists( uid=0 ) )

    def test_user_exists_name_and_uid( self ):
        self.assertTrue( user_exists( uid=0, name='root' ) )

    def test_user_exists_name_and_uid_if_one_no_exits_should_be_false( self ):
        self.assertFalse( user_exists( uid=1, name='root' ) )
        self.assertFalse( user_exists( uid=0, name='toor' ) )

    def test_group_exists_only_name( self ):
        self.assertTrue( group_exists( name='root' ) )

    def test_group_exists_only_uid( self ):
        self.assertTrue( group_exists( gid=0 ) )

    def test_group_exists_name_and_uid( self ):
        self.assertTrue( group_exists( gid=0, name='root' ) )

    def test_group_exists_name_and_uid_if_one_no_exits_should_be_false( self ):
        self.assertFalse( group_exists( gid=1, name='root' ) )
        self.assertFalse( group_exists( gid=0, name='toor' ) )


class Test_mem_info( TestCase ):
    def test_mem_info( self ):
        result = mem_info()
        self.assertIn( 'mem_total', result )
        self.assertGreater( result.mem_total, 1000 )
