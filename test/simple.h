// this is my single line comment
/*
// multi line comment
*/
/* a
// bit
// harder
// this
// time */

#include "myfile.h"
#define BLAH 0

int simple_function()
{
	printf( "hello" );
}

namespace
{
	int namespaced_function()
	{
		printf( "hello" );
	}
}

namespace custom {
int my_global_variable;
}

class my_class: public base_class
{
	public:
		my_class();
		my_class( int );
		virtual ~my_class();

		const int	normal_method();
		static int	static_method();
		virtual const int	virtual_method();
	
	private:
		int		my_variable;
		int*	my_pointer;
}

