from chibi.file.snippets import cd
from chibi.file import Chibi_path
from tests.snippet.files import Test_moving_dir


class Test_current_dir( Test_moving_dir ):
    def move_root( self ):
        cd( '/' )

    def move_home( self ):
        cd( '~' )

    def test_current_dir_should_return_a_string( self ):
        result = Chibi_path.current_dir()
        self.assertIsInstance( result, str )

    def test_current_dir_should_no_return_empty( self ):
        result = Chibi_path.current_dir()
        self.assertTrue( result )

    def test_current_dir_is_different_when_move_to_home( self ):
        first_current_dir = Chibi_path.current_dir()
        self.move_home()
        home_dir = Chibi_path.current_dir()
        self.assertNotEqual( first_current_dir, home_dir )

    def test_current_dir_is_different_when_move_to_root( self ):
        first_current_dir = Chibi_path.current_dir()
        self.move_root()
        root_dir = Chibi_path.current_dir()
        self.assertNotEqual( first_current_dir, root_dir )

    def test_should_no_be_root( self ):
        directory = Chibi_path.current_dir()
        self.assertNotEqual( directory, '/' )
