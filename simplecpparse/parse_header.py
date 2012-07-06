import re

""" A simple C / C++ header parser using standard Python.

This code doesn't make use of any lexical parsers, so we can't handle everything. But what we sacrificed in functionality, we made up for with simplicity and lack of dependencies (which is always good).

Caveats:
This code:
-Doesn't handle multiple statements on a single line. Ie, a = 1; b = 2;
-Doesn't process includes.
-Doesn't process macros.
-Doesn't process templates.
"""

class state_machine( object ):
    
    def __init__( self ):
        super( state_machine, self ).__init__()

        self.state = []

        # state with an empty scope state
        self.push_state( empty_scope_state( self ) )

    def run( self, f, line ):
        # while we have valid states
        # run them
        while len( self.state ) > 0:
            if line == '':
                print 'Reached EOF, but state machine still running'
                return
            line = self.state[ -1 ].parse( f, line )

    def push_state( self, state ):
        # add the state to the end of our list
        self.state.append( state )

    def pop_state( self ):
        # pop the state from our list
        self.state.pop()
    

class state( object ):
    
    def __init__( self, sm ):
        super( state, self ).__init__()
        self.sm = sm
        self.substates = []

    def parse( self, f, line ):
        pass

    @staticmethod
    def matches( line ):
        return False

    def add_substate( self, substate ):
        self.substates.append( substate )

    def run_substates( self, f, line ):
        state = self.match_substates( line )
        if state != None:
            new_state = state( self.sm )
            self.sm.push_state( new_state )
            return True
        return False

    def match_substates( self, line ):
        for state in self.substates:
            if state.matches( line ):
                return state
        return None

    def remove_comments( self, line ):
        # tokenise and return the first token
        line_list = line.split( line, '//', 1 )
        return line_list[ 0 ]

    def concatenate_continuations( self, f, line ):
        assert line != None

        # detect a line ending with a \
        # which means we should concatenate the line with the
        # next line
        while line.endswith( '\\' ):
            line = line[ : -1 ]
            line += f.readline()
        return line


class empty_scope_state( state ):
    
    def __init__( self, sm ):
        super( empty_scope_state, self ).__init__( sm )

        # add our substates
        self.add_substate( multi_line_comment_state )
        self.add_substate( function_state )
        self.add_substate( class_state )
        self.add_substate( variable_state )
        self.add_substate( namespace_state )
        # is this valid?
        #self.add_substate( sub_scope_state )

    def parse( self, f, line ):
        assert line != None

        while line != '':
            # handle continuations
            line = self.concatenate_continuations( f, line )

            print "empty_scope_state"
            print line

            # don't remove any commented lines or we
            # may miss the beginning of a multi-line comment

            # check if any substates can run yet
            if self.run_substates( f, line ) == True:
                break

            # nothing happened
            # just keep reading
            line = f.readline()
        return line

class multi_line_comment_state( state ):

    def __init__( self, sm ):
        super( multi_line_comment_state, self ).__init__( sm )

        # no sub states
        pass

    @staticmethod
    def matches( line ):
        if re.search( r'/\*', line ) != None:
            return True
        return False

    def parse( self, f, line ):
        assert line != None

        while line != '':
            # handle continuations
            line = self.concatenate_continuations( f, line )

            # don't trim comments or we may miss the /*
            print "multi_line_comment_state"
            print line

            # parse until we hit a */
            if re.search( line, r'\*/' ) != None:
                # we found the end of the comment
                # remove up to the */
                # TODO:
                break

            line = f.readline()
        return line

class variable_state( state ):

    def __init__( self, sm ):
        super( variable_state, self ).__init__( sm )

        # no sub states
        pass

    @staticmethod
    def matches( line ):
        # we're looking for something like:
        # abc::def   my_var;
        # or
        # const abc::def    my_var;
        # or
        # const abc:def * a, b, c;
        if line.startswith( r'/' ):
            return False
        if re.search( r'(\s+)?(\w+)?(\W+)\w+(\W+\w*)*', line ) != None:
            return True
        return False

    def parse( self, f, line ):
        assert line != None

        # parse the variable name
        # TODO
        print "variable_state"
        print line
        line = f.readline()
        return line

class function_state( state ):

    def __init__( self, sm ):
        super( function_state, self ).__init__( sm )

        # add our substates
        self.add_substate( multi_line_comment_state )
        # TODO: use a special scope that doesn't look for variables, etc
        self.add_substate( sub_scope_state )

    @staticmethod
    def matches( line ):
        # we're looking for something like:
        # abc::def   my_func( abc * xyz, abc< def > & uvw )
        if re.search( r'(\W+)\w+(\W+)\((.+)\)', line ) != None:
            return True
        return False

    def parse( self, f, line ):
        assert line != None

        # parse the function name, return type and arguments
        # check for an opening brace

        # parse until we hit a }
        # TODO:
        print "function_state"
        print line
        line = f.readline()
        return line

class sub_scope_state( state ):

    def __init__( self, sm ):
        super( sub_scope_state, self ).__init__( sm )

        # subscope is used for anything with { }'s
        # this includes namespaces, classes, functions, etc
        # so we support anything they support
        self.add_substate( multi_line_comment_state )
        self.add_substate( function_state )
        self.add_substate( class_state )
        self.add_substate( variable_state )

    @staticmethod
    def matches( line ):
        if re.search( r'\{', line ) != None:
            return True
        return False

    def parse( self, f, line ):
        assert line != None

        # remove the first { from the line and then
        # keep on parsing
        # otherwise we could hit an infinite loop
        # TODO:

        # parse until we hit a }
        # TODO:
        print "sub_scope_state"
        print line
        line = f.readline()
        return line

class namespace_state( state ):

    def __init__( self, sm ):
        super( namespace_state, self ).__init__( sm )

        # add our substates
        self.add_substate( multi_line_comment_state )
        self.add_substate( sub_scope_state )

    @staticmethod
    def matches( line ):
        # we want something in the format
        # namespace
        # {
        # or
        # namespace ABC
        # {
        if re.search( r'\s*namespace\s*(\w+)?', line ) != None:
            return True
        return False

    def parse( self, f, line ):
        assert line != None

        # parse the namespace name, if any
        # TODO:

        # remove the 'namespace' part of our line
        # otherwise we could get in an infinite loop
        # TODO:

        while line != '':
            # handle continuations
            line = self.concatenate_continuations( f, line )

            # don't remove any commented lines or we
            # may miss the beginning of a multi-line comment
            print "namespace_state"
            print line

            # check if any substates can run yet
            if self.run_substates( f, line ) == True:
                break

            # nothing happened
            # just keep reading
            line = f.readline()
        return line
    

class class_state( state ):

    def __init__( self, sm ):
        super( class_state, self ).__init__( sm )

        # add our substates
        self.add_substate( multi_line_comment_state )
        self.add_substate( sub_scope_state )

    @staticmethod
    def matches( line ):
        # we want something in the format
        # class XYZ:
        if re.search( r'\s*class\s+(\w+):', line ) != None:
            return True
        return False

    def parse( self, f, line ):
        assert line != None

        # parse the class name
        # parse the classes we inherit from
        # we should hit a sub-scope change
        print "class_state"
        print line
        line = f.readline()
        return line



def parse_header( path ):
    """Open the file and read the contents
    Convenience function that just opens the file
    and calls process_file with the appropriate parameters
    """
    with open( path, 'r') as f:
        process_file( f )

def process_file( f ):
    """Processes the header file
    Creates the state machine and begins parsing the file
    """
    sm = state_machine()

    line = f.readline()
    sm.run( f, line )


if __name__ == '__main__':
    import sys
    if len( sys.argv ) > 1:
        parse_header( sys.argv[ 1 ] )

