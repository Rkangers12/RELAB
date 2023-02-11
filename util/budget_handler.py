from datetime import datetime
from uuid import uuid4

from util.handle_times import HandleTimes
from tools.handler import Handler


class BudgetHandler:
    def __init__(self, datastore=None):

        self._budgetkey = "budgetData"
        self._datastore = datastore or Handler()
        self._handletime = HandleTimes()

    def set_threshold(self, user, threshold=0):
        """set the threshold of the budget alert"""

        self._datastore.overwrite_nested(
            ["users", user, self._budgetkey], "threshold", threshold
        )

    def get_threshold(self, user):
        """get the threshold value for budget alerting"""
        return self._datastore.get_nested_value(
            ["users", user, self._budgetkey, "threshold"]
        )

    def reset_archive(self, user):
        """reset archive store of budgets"""

        self._datastore.overwrite_nested(
            ["users", user, self._budgetkey], "archive", {}
        )

    def create_budget(self, name, expiration, limit, user):
        """store the budget within the database"""

        if not self.check_budget_exists(name, user):
            try:
                budget = {
                    "creation": str(self._handletime.format_a_day(datetime.now().day)),
                    "expiration": str(self._handletime.format_a_day(int(expiration))),
                    "limit": float(limit),
                    "spending": 0.00,
                }
            except (IndexError, ValueError):
                return 404
            else:
                self._datastore.overwrite_nested(
                    ["users", user, self._budgetkey, "budgets"], name, budget
                )
                return 200

        return 201

    def check_budget_exists(self, name, user):
        """check if the budget is already existing"""

        if name in self.get_all_budgets(user):
            return True

    def check_budget_archived(self, name, user):
        """check if the budget exists within the archives"""

        if name in self.get_all_archived(user):
            return True

    def modify_budget_limit(self, name, limit, user):
        """change the budget limit to new value"""

        if self.check_budget_exists(name, user):
            try:
                self._datastore.overwrite_nested(
                    ["users", user, self._budgetkey, "budgets", name],
                    "limit",
                    float(limit),
                )
            except ValueError:
                return 404

            return 200

        return 204

    def modify_budget_expiration(self, name, expiration, user):
        """change the budget expiration to new value"""

        if self.check_budget_exists(name, user):
            try:
                self._datastore.overwrite_nested(
                    ["users", user, self._budgetkey, "budgets", name],
                    "expiration",
                    str(self._handletime.format_a_day(int((expiration)))),
                )
            except ValueError:
                return 404

            return 200

        return 204

    def get_budget(self, name, user):
        """get the data of the provided data"""

        return self._datastore.get_nested_value(
            ["users", user, self._budgetkey, "budgets", name]
        )

    def get_archived(self, name, user):
        """get the budget which has been archived"""

        return self._datastore.get_nested_value(
            ["users", user, self._budgetkey, "archive", name]
        )

    def get_all_budgets(self, user):
        """get all budgets within the database"""

        return self._datastore.get_nested_value(
            ["users", user, self._budgetkey, "budgets"]
        )

    def get_all_archived(self, user):
        """get all archived budgets within the database"""

        return self._datastore.get_nested_value(
            ["users", user, self._budgetkey, "archive"]
        )

    def record_spending(self, name, spending, user):
        """record spending to existing budget"""

        budget = self.get_budget(name, user)
        if self.check_budget_exists(name, user):
            spending = budget["spending"] + spending

            self._datastore.overwrite_nested(
                ["users", user, self._budgetkey, "budgets", name], "spending", spending
            )

            res = 200
            remaining = self.get_remaining(name, user)

            if remaining < 0:
                res = 203
            elif remaining < self.get_threshold(user):
                res = 204

            return res
        else:
            return 201

    def get_remaining(self, name, user):
        """get the spending remaining for a budget"""
        budget = self.get_budget(name, user) or self.get_archived(name, user)

        if self.check_budget_exists(name, user) or self.check_budget_archived(
            name, user
        ):
            return budget.get("limit") - budget.get("spending")
        else:
            None

    def delete_budget(self, name, user):
        """delete a budget within the database"""

        if self.check_budget_exists(name, user):
            self._datastore.delete_nested(
                ["users", user, self._budgetkey, "budgets"], name
            )
            return 200
        else:
            return 201

    def archive_budget(self, name, user):
        """re-locate an existing budget to the archives"""

        if self.check_budget_exists(name, user):
            budget = self.get_budget(name, user)
            budget["og_name"] = name
            idify = f"{name}_{uuid4().hex[:6]}"

            self._datastore.overwrite_nested(
                ["users", user, self._budgetkey, "archive"], idify, budget
            )
            self.delete_budget(name, user)
        else:
            return 201

    def check_expired(self, name, user):
        """compare expiration against today's date"""

        if self.check_budget_exists(name, user):
            # retrieve today's day to compare against expiration
            today = str(self._handletime.format_a_day(datetime.now().day))
            budget = self.get_budget(name, user)

            if today > budget.get("expiration"):
                self.archive_budget(name, user)
                return 201
            else:
                return 202

        return 404

    def budget_spending(self, user):
        """identify spending in all budgets"""

        budgets = self.get_all_budgets(user)

        expenditure = 0
        for budget in budgets:
            expenditure += budgets.get(budget, {}).get("spending", 0)

        return expenditure

    def archive_spending(self, user):
        """identify spending in all archived budgets"""

        budgets = self.get_all_archived(user)

        expenditure = 0
        for budget in budgets:
            expenditure += budgets.get(budget, {}).get("spending", 0)

        return expenditure
