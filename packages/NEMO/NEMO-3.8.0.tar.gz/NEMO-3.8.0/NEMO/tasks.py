import inspect
from logging import getLogger
from threading import Thread, Lock, RLock

from django.utils.text import slugify

postponed_tasks_logger = getLogger("NEMO.PostponedTasks")

# Use this decorator on a function to make a call to said function asynchronous
# The function will be run in a separate thread, and the current execution will continue
def postpone(function):
	def decorator(*arguments, **named_arguments):
		t = Thread(target=function, args=arguments, kwargs=named_arguments)
		t.daemon = True
		t.start()

	return decorator


# Use this decorator annotation to prevent concurrent execution of a function
# Passing a method argument will only lock a function being called with that same argument
# For example, @synchronized('tool_id') on a do_this(tool_id) function will only prevent do_this from being called
# at the same time with the same tool_id. If do_this is called twice with different tool_id, it won't be locked
def synchronized(method_argument=""):
	def inner(function):
		def decorator(*args, **kwargs):
			func_args = inspect.signature(function).bind(*args, **kwargs).arguments
			attribute_value = slugify(str(func_args.get(method_argument, ""))).replace("-", "_")
			lock_name = "__" + function.__name__ + "_lock_" + attribute_value + "__"
			lock: RLock = vars(function).get(lock_name, None)
			if lock is None:
				meta_lock = vars(decorator).setdefault("_synchronized_meta_lock", Lock())
				with meta_lock:
					lock = vars(function).get(lock_name, None)
					if lock is None:
						lock = RLock()
						setattr(function, lock_name, lock)
			with lock:
				return function(*args, **kwargs)

		return decorator

	return inner
