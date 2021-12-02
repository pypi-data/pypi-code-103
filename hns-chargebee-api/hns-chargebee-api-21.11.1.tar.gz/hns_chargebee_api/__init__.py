from chargebee import Customer, Subscription, configure
from chargebee.result import Result
from datetime import datetime, timedelta
from typing import Union


class ChargebeeAPI:

    def __init__(self, api_key: str, site: str, first20_trial_days: int = 90, base_trial_days: int = 14):
        """
        Perform common tasks on chargebee like activation of subscription etc, etc

        :param api_key: Chargebee API key
        :param site:  Chargebee site
        :param first20_trial_days: How many days of trial to give to first 20 users
        :param base_trial_days:  How many days of trial to give to everyone
        """

        self.api_key = api_key
        self.site = site
        self.first20_trial_days = first20_trial_days
        self.base_trial_days = base_trial_days
        configure(self.api_key, self.site)

    def calculate_trial_end(self, first20_flag: bool, sales_office_flag: bool) -> int:
        """ Calculates amount of trial to give """

        if sales_office_flag or first20_flag:
            trial_end = datetime.now() + timedelta(days=self.first20_trial_days)
        else:
            trial_end = datetime.now() + timedelta(days=self.base_trial_days)
        return int(trial_end.timestamp())

    def activate_subs(self, subs: Result, cid: str) -> bool:
        """ Activates service on chargebee """

        sales_office = subs.subscription.cf_sales_office
        if sales_office is None or sales_office.lower() != 'true':
            sales_office_flag = False
        else:
            sales_office_flag = True

        first20 = subs.customer.cf_first20reservation
        if first20 is None or first20.lower() == 'true':
            first20_flag = True
        else:
            first20_flag = False

        activate = Subscription.update(
            subs.subscription.id,
            {
                'start_date': 0,
                'trial_end': self.calculate_trial_end(first20_flag, sales_office_flag),
                'cf_service_live_date': int(datetime.now().timestamp()),
                'cf_cid': cid
            }
        )

        if activate.subscription.status == 'active' \
                or activate.subscription.status == 'in_trial':
            return True
        return False

    @staticmethod
    def retrieve(id: str) -> Result:
        return Subscription.retrieve(id)

    def retrieve_sub(self, id: str) -> Result:
        return self.retrieve(id)

    @staticmethod
    def retrieve_cust(id: str) -> Result:
        return Customer.retrieve(id)

    @staticmethod
    def clear_ucr(cust_id) -> Result:
        return Customer.update(cust_id, {'cf_ucr': None})

    def clear_pii(self, cust_id: str) -> Result:
        self.clear_ucr(cust_id)
        return Customer.clear_personal_data(cust_id)

    @staticmethod
    def set_purged_from_db_and_remove_cid(subs_id: str) -> Union[Result, ValueError]:
        """ Sets purged from db flag for a subscription and removes cid from subscription """

        subs = Subscription.retrieve(subs_id)
        if subs.subscription.status != 'cancelled':
            raise ValueError('Cannot set purged from db flag and removed cid for non cancelled subscription')
        else:
            update = Subscription.update(subs.subscription.id, {
                'cf_purged_from_db': True,
                'cf_cid': None
            })
            return update

    @staticmethod
    def update_cid(subs_id: str, cid: str) -> Result:
        """ Updates cid of a subscription """

        subs = Subscription.retrieve(subs_id)
        if subs.subscription.cf_cid == cid:
            return subs
        elif subs.subscription.status == 'in_trial':
            update = Subscription.update(subs.subscription.id, {
                'cf_cid': cid,
                'trial_end': subs.subscription.trial_end
            })
            return update
        else:
            update = Subscription.update(subs.subscription.id, {
                'cf_cid': cid
            })
            return update
