#! /usr/bin/env python3

# One day i will remove exceptions that cover more than one unique case,
# i promise.

class NotLoggedIn(Exception):
    # Is triggered if user is unauthenticated 
    # Either was not logged in or session timed out
    pass

class Unauthorized(Exception):
    pass

class NotAuthenticated(Exception):
    # Is triggered on occasion when there is a TWS or IBGateway session running
    # Or if the previous session was not properly exited by logging out of the 
    # TWS or calling /logout endpoint.
    pass

class CompetingSessionException(Exception):
    # is raised if there is a competing session running. Only one session
    # is allowed per username
    pass

# Contract related issues

class NoContractsFoundForSymbol(Exception):
    # Is raised when search by symbol returned no results
    pass

class NoContractsFoundForCompany(Exception):
    # Is raised when search by company name returned no results
    pass

# Trading related exceptions:

class NoTradingPermissionError(Exception):
    # is triggered if account is not configured with relevant trading
    # permissions
    pass

class OrderRejectedClosingOnly(Exception):
    # Triggered if positions for the instrument can
    # only be closed, no new positions can be opened
    pass

class OrderRejectedDueToReasons(Exception):
    # Because this is the way
    pass

class InternalServerError(Exception):
    # 500 code returned from the server
    pass

class JavaLangException(Exception):
    # Is triggered when contract is not found
    # Who knows when else...
    pass

class TooManyHistoricalRequests(Exception):
    # Is triggered once the limit of 10 requests per second breached
    pass

class NotAllowedOutsideRTH(Exception):
    # Not all orders can be placed outside regular trading hours
    pass

class InvalidAttributeSyntax(Exception):
    # Raised if one of the JSON fields has invalid formatting
    # For example: Price instead of price or trailingAmount instead ot trailingAmt
    pass

class ReplyIdNotFound(Exception):
    # Raised if order reply failed to find reply id
    pass

class DuplicateOrderReference(Exception):
    # Raised if cOID has already been used in other order
    pass
