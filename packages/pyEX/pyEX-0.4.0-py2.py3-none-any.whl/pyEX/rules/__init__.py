# *****************************************************************************
#
# Copyright (c) 2020, the pyEX authors.
#
# This file is part of the pyEX library, distributed under the terms of
# the Apache License 2.0.  The full license can be found in the LICENSE file.
#
from functools import wraps

from ..common import PyEXception, _delete, _get, _post, _raiseIfNotStr
from .engine import Rule  # noqa: F401


def lookup(lookup="", token="", version="stable", format="json"):
    """Pull the latest schema for data points, notification types, and operators used to construct rules.

    https://iexcloud.io/docs/api/#rules-schema

    Args:
        lookup (str): If a schema object has “isLookup”: true, pass the value key to /stable/rules/lookup/{value}. This returns all valid values for the rightValue of a condition.
        token (str): Access token
        version (str): API version
        format (str): return format, defaults to json

    Returns:
        dict: result
    """
    _raiseIfNotStr(lookup)
    if lookup:
        return _get(
            "rules/lookup/{}".format(lookup),
            token=token,
            version=version,
            format=format,
        )
    return _get("rules/schema", token=token, version=version, format=format)


@wraps(lookup)
def schema(token="", version="stable", format="json"):
    return lookup(token=token, version=version, format=format)


def create(
    rule,
    ruleName,
    ruleSet,
    type="any",
    existingId=None,
    token="",
    version="stable",
    format="json",
):
    """This endpoint is used to both create and edit rules. Note that rules run be default after being created.

    Args:
        rule (Rule or dict): rule object to create
        ruleName (str): name for rule
        ruleSet (str): Valid US symbol or the string ANYEVENT. If the string ANYEVENT is passed, the rule will be triggered for any symbol in the system. The cool down period for alerts (frequency) is applied on a per symbol basis.
        type (str): Specify either any, where if any condition is true you get an alert, or all, where all conditions must be true to trigger an alert. any is the default value
        existingId (Optional[str]): The id of an existing rule only if you are editing the existing rule
        token (str): Access token
        version (str): API version
        format (str): return format, defaults to json
    """
    if type not in ("any", "all"):
        raise PyEXception("type must be in (any, all). got: {}".format(type))

    if isinstance(rule, Rule):
        rule = rule.toJson()

    rule["token"] = token
    rule["ruleSet"] = ruleSet
    rule["type"] = type
    rule["ruleName"] = ruleName

    # Conditions, outputs, and additionalKeys handled by rule object
    if "conditions" not in rule:
        raise PyEXception("rule is missing `conditions` key!")
    if "outputs" not in rule:
        raise PyEXception("rule is missing `outputs` key!")

    if existingId is not None:
        rule["id"] = existingId
    return _post(
        "rules/create",
        json=rule,
        token=token,
        version=version,
        token_in_params=False,
        format=format,
    )


def pause(ruleId, token="", version="stable", format="json"):
    """You can control the output of rules by pausing and resume per rule id.

    Args:
        ruleId (str): The id of an existing rule to puase
        token (str): Access token
        version (str): API version
        format (str): return format, defaults to json
    """
    return _post(
        "rules/pause",
        json={"ruleId": ruleId, "token": token},
        token=token,
        version=version,
        token_in_params=False,
        format=format,
    )


def resume(ruleId, token="", version="stable", format="json"):
    """You can control the output of rules by pausing and resume per rule id.

    Args:
        ruleId (str): The id of an existing rule to puase
        token (str): Access token
        version (str): API version
        format (str): return format, defaults to json
    """
    return _post(
        "rules/resume",
        json={"ruleId": ruleId, "token": token},
        token=token,
        version=version,
        token_in_params=False,
        format=format,
    )


def delete(ruleId, token="", version="stable", format="json"):
    """You can delete a rule by using an __HTTP DELETE__ request. This will stop rule executions and delete the rule from your dashboard. If you only want to temporarily stop a rule, use the pause/resume functionality instead.

    Args:
        ruleId (str): The id of an existing rule to puase
        token (str): Access token
        version (str): API version
        format (str): return format, defaults to json
    """
    return _delete(
        "rules/{}".format(ruleId), token=token, version=version, format=format
    )


def rule(ruleId, token="", version="stable", format="json"):
    """Rule information such as the current rule status and execution statistics.

    Args:
        ruleId (str): The id of an existing rule to puase
        token (str): Access token
        version (str): API version
        format (str): return format, defaults to json
    """
    return _get(
        "rules/info/{}".format(ruleId), token=token, version=version, format=format
    )


def rules(token="", version="stable", format="json"):
    """List all rules that are currently on your account. Each rule object returned will include the current rule status and execution statistics."""
    return _get("rules", token=token, version=version, format=format)


def output(ruleId, token="", version="stable", format="json"):
    """If you choose `logs` as your rule output method, IEX Cloud will save the output objects on our server. You can use this method to retrieve those data objects.

    Args:
        ruleId (str): The id of an existing rule to puase
        token (str): Access token
        version (str): API version
        format (str): return format, defaults to json
    """
    return _get(
        "rules/output/{}".format(ruleId), token=token, version=version, format=format
    )
