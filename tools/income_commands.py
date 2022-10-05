from email.policy import default
from util.handle_times import HandleTimes
from util.income_handler import IncomeHandle


class IncomeCommands:
    def __init__(self, datastore):

        self._handletimes = HandleTimes()
        self._datastore = datastore

        if self._datastore.get_value("payrollData") is None:
            self._datastore.overwrite(db_key="payrollData", db_value={})

    # class getters and setters
    @property
    def get_payroll(self):
        """get the payroll data from database"""

        return self._datastore.get_value("payrollData", {})

    def get_payroll_value(self, payroll_key, default=None):
        """get the value of the requested payroll data"""

        return self.get_payroll.get(payroll_key, default)

    def set_payroll_value(self, payroll_key, payroll_value):
        """set the payroll value"""

        db = self._datastore.get()
        payroll = db.get("payrollData", {})
        payroll[payroll_key] = payroll_value
        self._datastore.write_all(db)

    # class methods
    def set_payroll(self, content, payroll_key):
        """store the data for the payroll within the database"""

        try:
            payroll_value = float(content.split(" ")[1])
        except (IndexError, ValueError):
            return 404

        if payroll_key == "payDay":
            payroll_value = min(31, payroll_value)

        self.set_payroll_value(payroll_key, payroll_value)

        return 200

    def get(self, payroll_key):
        """get individual data within payroll from database"""

        val = self.get_payroll_value(payroll_key, default=0)

        return val

    def sl_toggle(self, slt_key):
        """toggle student loan setting"""

        loan_setting = self.get_payroll_value(slt_key, default=False)
        setting = "active"

        if loan_setting:
            self.set_payroll_value(slt_key, False)
            setting = "inactive"
        else:
            self.set_payroll_value(slt_key, True)

        return setting

    def sl_check(self, slt_key):
        """check student loan setting"""

        return self.get_payroll_value(slt_key, default=False)

    def get_takehome(self):
        """retrieve a breakdow n of the take home pay for the user"""

        self._incomehandle = IncomeHandle(
            self.get("grossSalary"), notionals=self.get("notionals")
        )

        return self._incomehandle.get_take_home(student_loan=self.sl_check("activeSL"))

    def get_payslip(self):
        """retrieve payslip details including gross, nic, tax, slt, takehome"""

        gross = self.get("grossSalary")
        self._inc_hand = IncomeHandle(gross, notionals=self.get("notionals"))

        payslip = {
            "gross": gross,
            "tax": self._inc_hand.get_tax,
            "nic": self._inc_hand.get_nic,
            "takehome": self._inc_hand.get_take_home(
                student_loan=self.sl_check("activeSL")
            ),
        }

        if self.sl_check("activeSL"):
            payslip["slt"] = self._inc_hand.get_slt

        return payslip
