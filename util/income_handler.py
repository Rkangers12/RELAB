class IncomeHandle:
    """class to handle the gross income and convert to payouts"""

    def __init__(self, gross_salary, notionals=None):

        self._gross = gross_salary / 12
        self._notionals = notionals / 12 or 0

    @property
    def get_nic(self):
        """calculate national insurance contribution"""

        thres_u = {"figure": 4189, "rate": 0.0325}
        thres_l = {"figure": 1048, "rate": 0.1325}

        u_bracket = max(self._gross - thres_u["figure"], 0) * thres_u["rate"]
        l_bracket = min(
            thres_u["figure"] - thres_l["figure"], self._gross - thres_l["figure"]
        ) * thres_l.get("rate")

        return round(u_bracket + l_bracket, 0)

    @property
    def get_tax(self):
        """calculate the tax paid"""

        salary = (self._gross + self._notionals) * 12
        thresholds = {
            "allowance": 12570,
            "basic": 50270,
            "higher": 150000,
            "additional": 150000,
            "extra": 0,
        }

        if salary >= 100000:
            thresholds["extra"] = thresholds["allowance"] - max(
                0, thresholds["allowance"] - (salary - 100000) / 2
            )

        basic = max(
            0,
            min(
                salary - thresholds["allowance"],
                thresholds["basic"] - thresholds["allowance"],
            ),
        )
        higher = max(
            0,
            min(
                salary - thresholds["basic"], thresholds["higher"] - thresholds["basic"]
            ),
        )
        additional = max(0, salary - thresholds["additional"])

        return round(
            (basic * 0.2 + (higher + thresholds["extra"]) * 0.4 + additional * 0.45)
            / 12,
            0,
        )

    @property
    def get_slt(self):
        """calculate the student loan repayment"""

        repayment = {"threshold": 2274, "rate": 0.09}

        return round(
            max(0, (self._gross - repayment["threshold"]) * repayment["rate"], 0)
        )

    def get_take_home(self, student_loan=0):
        "provide the take home wage"

        return self._gross - (
            self.get_nic + (self.get_slt * student_loan) + self.get_tax
        )
