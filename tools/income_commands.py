class IncomeCommands:

    def __init__(self, datastore):

        self._datastore = datastore

        if self._datastore.get_value('payrollData') is None:
            self._datastore.overwrite(db_key='payrollData', db_value={})
    
    async def set_payroll_data(self, message, payroll_key):
        '''store data for payroll witin the database'''
        
        try:
            payroll_value = int(message.split(' ')[1])
        except IndexError:
            payroll_value = 0
        
        db = self._datastore.get()
        db.get('payrollData', {})[payroll_key] = payroll_value
        self._datastore.write_all(db)
        
    async def get_individual_payroll_data(self, message, payroll_key):
        '''get individual data within payroll stored within database'''

        await message.channel.send(
            self._datastore.get_value('payrollData', {}).get(payroll_key, '')
        )
    
