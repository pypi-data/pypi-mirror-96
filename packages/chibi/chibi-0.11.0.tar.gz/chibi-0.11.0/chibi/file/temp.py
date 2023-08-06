import tempfile

from .path import Chibi_path


class Chibi_temp_path( Chibi_path ):
    def __new__( cls, *args, **kw ):
        args_2 = []
        args_2.append( tempfile.mkdtemp() )
        return str.__new__( cls, *args_2, **kw )

    def __del__( self ):
        self.delete()

    def __add__( self, other ):
        return Chibi_path( str( self ) ) + other

    def temp_file( self, extension='' ):
        subffix = f'.{extension}' if extension else extension
        file_name = tempfile.mkstemp( suffix=subffix, dir=str( self ) )[1]
        return Chibi_path( file_name )

    def temp_dir( self ):
        return Chibi_path( tempfile.mkdtemp( dir=str( self ) ) )
