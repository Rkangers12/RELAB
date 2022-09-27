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

    def get_payroll_value(self, payroll_key, default="unavailable"):
        """get the value of the requested payroll data"""

        return self.get_payroll.get(payroll_key, default)

    def set_payroll_value(self, payroll_key, payroll_value):
        """set the payroll value"""

        db = self._datastore.get()
        payroll = db.get("payrollData", {})
        payroll[payroll_key] = payroll_value
        self._datastore.write_all(db)

    # class methods

    async def set_payroll_data(self, message, payroll_key):
        """store data for payroll within the database"""

        try:
            payroll_value = float(message.content.split(" ")[1])
        except (IndexError, ValueError):
            await message.channel.send(
                "Please provide me some with appropriate payroll information."
            )
            return 404

        if payroll_key == "payDay":
            payroll_value = min(31, payroll_value)

        self.set_payroll_value(payroll_key, payroll_value)

        await message.channel.send(
            "RELAB has updated your **{}** payroll details.".format(payroll_key)
        )

    async def get_payroll_data(self, message, payroll_key, of_type=None):
        """get individual data within payroll stored within database"""

        val = self.get_payroll_value(payroll_key)

        if val != "unavailable":
            if of_type == "date":
                print(int(val))
                val = self._handletimes.format_a_day(int(val), weekday=True).isoformat()
            elif of_type == "currency":
                val = "£" + str(float(val))

        await message.channel.send(
            "RELAB has retrieved your payroll details:\n    - {}: **{}**".format(
                payroll_key,
                val,
            )
        )

    async def toggle_student_loan(self, message, slt_key):
        """toggle student loan setting"""

        loan_setting = self.get_payroll_value(slt_key, default=False)
        setting = "active"

        if loan_setting:
            self.set_payroll_value(slt_key, False)
            setting = "inactive"
        else:
            self.set_payroll_value(slt_key, True)

        await message.channel.send(
            "RELAB has updated your student loan settings - now **{}**.".format(setting)
        )

    async def check_student_loan(self, message, slt_key):
        """check student loan setting"""

        sl = self.get_payroll_value(slt_key, default=False)

        setting = "**inactive**"
        if sl:
            setting = "**active**"

        await message.channel.send(
            "RELAB has retrieved your payroll details:\n    - {}: **{}**".format(
                "Student Loan", setting
            )
        )

    # async def get_takehome_breakdown(self, message):
    #     """retrieve a breakdown of the takehome summary for user"""

    #     self._incomehandle = IncomeHandle()
