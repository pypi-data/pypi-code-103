"""

sample data

test_data = [
    ["TPb..8y...L1rTo..Qsw", 1000000],
    ["TN8..H...dyMm...4CynM", 1000000],
    ["TJ1..L...dNy...TA6i", 1000000],
    ["TH...NZ...U878...2", 1000000],
    ["TPvf...8q....mT", 1000000],
]


    sendOb = BulkManager(test_data, ws.tron)
    print("total {}".format(sendOb.getSENDTotal()))
    print("address {}".format(sendOb.getSENDAddresses()))

    ws.getContactBS().bulk_send_trx(
        sendOb.getSENDAddresses(),
        sendOb.getSENDAmountBalances(),
        sendOb.getSENDTotal()
    )

"""


class BulkManager:
    def __init__(self, dat, tron):
        self.datlist = dat
        self.tron = tron

    def getSENDAddresses(self) -> list:
        list_address = list()
        for c in self.datlist:
            list_address.append(c[0])
        return list_address

    def getSENDAmountBalances(self) -> list:
        list_address = list()
        for c in self.datlist:
            list_address.append(c[1])

        return list_address

    def getSENDTotal(self) -> int:
        total = 0
        for c in self.datlist:
            total += int(c[1])
        return total
