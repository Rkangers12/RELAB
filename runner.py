from util.monitor_bills import BillsMonitor

b = BillsMonitor()

# b.set(".setbill .bill=council Tax.day=16.cost=135")
# print(b.get(".getbill .bill=water"))

# b.set(".setbill .bill=council tax.day=24")
# print(b.get(".getbill .bill=council tax"))

# b.set(".setbill .bill=electricity.day=17")
#
# print(b.get_bill(".getbill .bill=electricitey"))  # return 404


# print(b.get_bill_meta(".getbill .bill=electricity"))  # return 404
print(
    b.format_bill(b.get_bill_meta(".getbilldata .bill=electricity.metadata=debit_day"))
)
# print(b.format_bill(b.get_bill_meta(".getbilldata .bill=electricity.metadata=expense")))
# print(b.get_bill_meta(".getbilldata .bill=electridcity.metadata=debit_day"))

# b.delete(".deletebill .bill=electricity")


# print(b.get_all())

# Commands for testing features of the bill monitor
"""
.setbill .bill=council Tax.day=16.cost=135
.getbill .bill=water
.setbill .bill=council tax.day=24
.getbill .bill=council tax
.setbill .bill=electricity.day=17
.getbilldate .bill=electricity.metadata=debit_day
.deletebill .bill=electricity
"""
