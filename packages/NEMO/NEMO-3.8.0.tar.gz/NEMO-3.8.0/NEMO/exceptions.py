from typing import List, Any

from NEMO.models import User, Area, Resource, Interlock, PhysicalAccessException


class NEMOException(Exception):
	""" Basic NEMO exception """

	default_msg = "A {} error occurred"

	def __init__(self, msg=None):
		if msg is None:
			from NEMO.views.customization import get_customization
			site_title = get_customization('site_title')
			msg = self.default_msg.format(site_title)
		self.msg = msg
		super(NEMOException, self).__init__(msg)


class InvalidCustomizationException(NEMOException):
	def __init__(self, name: str, value: str = None):
		msg = f"Invalid customization ({name})"
		if value is not None:
			msg += f" for value: [{value}]"
		super(InvalidCustomizationException, self).__init__(msg)


class InterlockError(NEMOException):
	""" Interlock related errors """

	def __init__(self, interlock: Interlock, msg=None):
		self.message = msg
		error_message = f"An Error occurred with interlock [{interlock}]"
		if msg is not None:
			error_message += f": {msg}"
		self.interlock = interlock
		super(InterlockError, self).__init__(error_message)


class UserAccessError(NEMOException):
	""" User access related errors """

	detailed_msg = ""

	def __init__(self, user: Any, msg=None):
		message = f"An Error occurred with user access [{user}]"
		if msg is not None:
			message += f": {msg}"
		elif self.detailed_msg:
			message += f": {self.detailed_msg}"
		self.user = user
		super(UserAccessError, self).__init__(message)


class InactiveUserError(UserAccessError):
	detailed_msg = "This user is not active"


class NoActiveProjectsForUserError(UserAccessError):
	detailed_msg = "This user does not have any active projects"


class PhysicalAccessExpiredUserError(UserAccessError):
	detailed_msg = "This user's physical access has expired"


class NoPhysicalAccessUserError(UserAccessError):
	detailed_msg = "This user has not been granted physical access to any area"


class NoAccessiblePhysicalAccessUserError(UserAccessError):
	def __init__(self, user: User, area: Area, access_exception: PhysicalAccessException=None):
		self.area = area
		self.access_exception = access_exception
		details = f"This user is not assigned to a physical access that allow access to this area [{area}] at this time"
		if self.access_exception:
			details = f"This user was denied access to this area [{area}] due to the following exception: {access_exception.name}"
		super(NoAccessiblePhysicalAccessUserError, self).__init__(user=user, msg=details)


class UnavailableResourcesUserError(UserAccessError):
	def __init__(self, user: User, area: Area, resources: List[Resource]):
		self.area = area
		self.resources = resources
		details = f"This user was denied access to this area [{area}] because a required resource was unavailable [{resources}"
		super(UnavailableResourcesUserError, self).__init__(user=user, msg=details)

class MaximumCapacityReachedError(UserAccessError):
	def __init__(self, user: User, area: Area):
		self.area = area
		details = f"This user was denied access to this area [{area}] because the area's maximum capacity of [{area.maximum_capacity}] has been reached"
		super(MaximumCapacityReachedError, self).__init__(user=user, msg=details)

class ScheduledOutageInProgressError(UserAccessError):
	def __init__(self, user: User, area: Area):
		self.area = area
		details = f"This user was denied access to this area [{area}] because there is a scheduled outage in progress"
		super(ScheduledOutageInProgressError, self).__init__(user=user, msg=details)

class ReservationRequiredUserError(UserAccessError):
	def __init__(self, user: User, area: Area):
		self.area = area
		details = f"This user was denied access to this area [{area}] because the user doesn't have a current reservation for that area"
		super(ReservationRequiredUserError, self).__init__(user=user, msg=details)
