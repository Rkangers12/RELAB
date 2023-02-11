from util.handle_times import HandleTimes
from util.income_handler import IncomeHandle


class IncomeCommands:
    def __init__(self, datastore):

        self._handletimes = HandleTimes()
        self._datastore = datastore
        self._key = "payrollData"

    # class methods
    def set_payroll(self, content, key, user):
        """store the data for the payroll within the database"""

        try:
            val = float(content.split(" ")[1])
        except (IndexError, ValueError):
            return 404

        if key == "payDay":
            val = int(min(31, val))

        self._datastore.overwrite_nested(["users", user, self._key], key, val)

        return 200

    def get(self, key, user):
        """get individual data within payroll from database"""

        val = self._datastore.get_nested_value(["users", user, self._key, key])

        return val

    def sl_toggle(self, slt_key, user):
        """toggle student loan setting"""

        loan_setting = self._datastore.get_nested_value(
            ["users", user, self._key, slt_key]
        )
        setting = "active"

        if loan_setting:
            self._datastore.overwrite_nested(["users", user, self._key], slt_key, False)
            setting = "inactive"
        else:
            self._datastore.overwrite_nested(["users", user, self._key], slt_key, True)

        return setting

    def sl_check(self, slt_key, user):
        """check student loan setting"""

        return self._datastore.get_nested_value(["users", user, self._key, slt_key])

    def get_takehome(self, user):
        """retrieve a breakdow n of the take home pay for the user"""

        self._incomehandle = IncomeHandle(
            self.get("grossSalary", user), notionals=self.get("notionals", user)
        )

        return self._incomehandle.get_take_home(
            student_loan=self.sl_check("activeSL", user)
        )

    def get_payslip(self, user):
        """retrieve payslip details including gross, nic, tax, slt, takehome"""

        gross = self.get("grossSalary", user)
        self._inc_hand = IncomeHandle(gross, notionals=self.get("notionals", user))

        student = self.sl_check("activeSL", user)
        payslip = {
            "gross": gross,
            "tax": self._inc_hand.get_tax,
            "nic": self._inc_hand.get_nic,
            "takehome": self._inc_hand.get_take_home(student_loan=student),
        }

        if student:
            payslip["slt"] = self._inc_hand.get_slt

        return payslip
