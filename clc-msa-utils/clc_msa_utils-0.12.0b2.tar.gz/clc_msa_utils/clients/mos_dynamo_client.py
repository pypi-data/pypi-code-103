import boto3
from boto3.dynamodb.conditions import Key
import logging
import os
import sys
import traceback
from clc_msa_utils.utils import authorized_machine, log_exception
from clc_msa_utils.kv_store import KVStore


class MOSDynamoClient:
    kv_store = KVStore(
        kv_prefix=os.getenv('DYNAMO_ETCD_PREFIX', '/config/dynamodb')
    )
    def __init__(self):
        self._kv_store = KVStore(
            kv_prefix=os.getenv('DYNAMO_ETCD_PREFIX', '/config/dynamodb')
        )
        self._dynamodb = boto3.resource('dynamodb',
                                  region_name=self._kv_store.get('db-region'),
                                  aws_access_key_id=self._kv_store.get('aws-key'),
                                  aws_secret_access_key=self._kv_store.get('aws-secret')
                                  )
        self._tables = {}
        self._tables['managed_servers_table'] = self._dynamodb.Table(self._kv_store.get('managed_servers_table'))
        self._tables['managed_applications_table'] = self._dynamodb.Table(self._kv_store.get('managed_applications_table'))
        self._tables['ad_servers_table'] = self._dynamodb.Table(self._kv_store.get('active-directory-server-table'))
        self._tables['events_table'] = self._dynamodb.Table(self._kv_store.get('events-table'))
        self._tables['networks_table'] = self._dynamodb.Table(self._kv_store.get('network-table'))
        self._tables['vpn_hubs_table'] = self._dynamodb.Table(self._kv_store.get('vpn_hubs_table'))
        self._tables['vpn_tenants_table'] = self._dynamodb.Table(self._kv_store.get('vpn_tenants_table'))
        self._tables['tickets-table'] = self._dynamodb.Table(self._kv_store.get('tickets-table'))
        self._logger = logging.getLogger("default")


    def _get_item(self, table, key):
        item = None
        try:
            response = table.get_item(Key=key)
            self._logger.debug("Response getting item by Key={}:\n{}".format(key, response))

            if "Item" in response:
                item = response['Item']

            return item
        except Exception as exception:
            self._logger.error(
                "Unexpected error occurred retrieving document from database:\n%s" % traceback.format_exc())
            self._logger.error("Exception:\n%s" % exception)
            raise exception

    def _put_item(self, table, item ):
        response = table.put_item(Item=item)
        return response['ResponseMetadata']['HTTPStatusCode']

    def _query(self, table, db_args):
        items = []
        try:
            response = table.query(**db_args)
            self._logger.debug("Response querying {}:\n{}".format(table.table_name, response))
            if response['Count'] > 0:
                items = response['Items']
        except Exception as exception:
            self._logger.error(
                "Unexpected error occurred retrieving data from {} :\n{}".format(table.table_name, traceback.format_exc()))
            self._logger.error("Exception:\n%s" % exception)
            raise exception
        return items


    def get_managed_server(self, managed_server_id, instance_info):
        self._logger.debug("Getting managed server details for server with ID = " + managed_server_id + "...")
        managed_server = self.get_managed_server_by_support_id(managed_server_id)

        if not managed_server:
            managed_server = self.get_managed_server_by_machine_name(managed_server_id, instance_info)

        self._logger.debug("Returning Managed Server:\n" + managed_server)
        return managed_server

    def get_managed_server_by_support_id(self, support_id):
        self._logger.debug("Getting managed server details for server with support ID = " + support_id)
        return self._get_item(self._tables['managed_servers_table'], {'name': support_id})

    def get_managed_server_by_machine_name(self, machine_name, instance_info):
        managed_server = None
        self._logger.debug("Getting managed server details for server with machine name = " + machine_name + "...")
        db_args = {
            "KeyConditionExpression": Key('mcmInstanceId').eq(machine_name),
            "IndexName": "mcmInstanceId-index"
        }
        servers = self._query(self._tables['managed_servers_table'], db_args)
        self._logger.debug("Response getting server by machine_name:\n%s" % servers)
        if servers > 0:
            for server in servers:
                machine = authorized_machine(instance_info, 'support_id', server.get('name'))
                if machine:
                    managed_server = server
                    break

        return managed_server


    def get_appliances_by_network(self, vpc_id):
        db_args = {
            "KeyConditionExpression": Key('network').eq(vpc_id) & Key('isAppliance').eq('true'),
            "IndexName": "network-isAppliance-index"
        }
        return self._query(self._tables['managed_servers_table'], db_args)


    def get_managed_servers_by_gateway_name(self, gateway_name):
        db_args = {
            "KeyConditionExpression": Key('gatewayName').eq(gateway_name) & Key('status').eq('active'),
            "IndexName": "gatewayName-status-index"
        }
        return self._query(self._tables['managed_servers_table'], db_args)


    def get_managed_application(self, application_id):
        self._logger.debug("Getting managed application details for ID = " + application_id)
        return self._get_item(self.self._tables['managed_applications_table'], {'}mcmInstanceId': application_id})

    def scan_managed_servers(self, db_args):
        return self._tables['managed_servers_table'].scan(**db_args)


    def update_managed_application(self, db_args):
        return self._tables['managed_applications_table'].update_item(**db_args)


    def update_managed_server(self, db_args):
        return self._tables['managed_servers_table'].update_item(**db_args)


    def scan_ad_servers(self, db_args):
        return self._tables['ad_servers_table'].scan(**db_args)

    def put_ad_server(self, ad_server):
        self._logger.info("PUT Payload : " + str(ad_server))
        return self._put_item(self._tables['ad_servers_table'], ad_server)


    def delete_ad_server(self, gateway_name):
        try:
            response =  self._tables['ad_servers_table'].update_item(Key={'gatewayName': gateway_name},
                                                UpdateExpression="SET #status = :status",
                                                ExpressionAttributeValues={
                                                    ':status': "terminated"
                                                },
                                                ExpressionAttributeNames={
                                                    '#status': 'status'
                                                })
            return response['ResponseMetadata']['HTTPStatusCode']

        except Exception as e:
            self._logger.error("Error occurred deleting ad server with vpcId '{0}': \n{1}".format(id, str(e)))
            log_exception(sys.exc_info())
            raise e


    def get_ad_server_by_gateway_name(self, gateway_name):
        ad_server = None
        response = self._tables['ad_servers_table'].get_item(Key={'gatewayName': gateway_name})
        if "Item" in response:
            ad_server = response['Item']

        return ad_server

    def get_ad_servers_by_account(self, account):
        db_args = {
            "KeyConditionExpression": Key('status').eq('active') & Key('account').eq(account),
            "IndexName": "status-account-index"
        }
        return self._query(self._tables['ad_servers_table'], db_args)

    def get_ad_server_dynamo_health(self, json_data):
        table_info = {}
        table_monitor = {"name": "DynamoDB Monitor"}
        try:
            table_info["tableName"] = self._tables['ad_servers_table'].table_name
            table_info["tableStatus"] = self._tables['ad_servers_table'].table_status
            if table_info["tableStatus"] in ["CREATING", "UPDATING", "ACTIVE"]:
                table_monitor["status"] = "UP"
            else:
                table_monitor["status"] = "DOWN"
                json_data["status"] = "DOWN"
            table_monitor["tableInfo"] = table_info
        except:
            e = sys.exc_info()
            log_exception(traceback.format_exc())
            table_monitor["info"] = str(e)
            table_monitor["status"] = "DOWN"
            json_data["status"] = "DOWN"
        return table_monitor


    """
    This method is used by the network-services in two endpoints;
    PUT /network-services/public/networks which creates/updates entries in the networks table. This function is called
    and if a document is returned, it updates it, if not it creates a new one. Theoretically, only one entry should
    ever be created with a single combination of vpcId and provider_id
    
    POST /network-services/admin/networks Which actually just GETS returns the network in question
    
    Since there should only ever be a single document with the same vpcId and provider_id we throw an exception if
    there is more than one document. This may create a race condition with multiple pods of network services running
    in prod. But I would argue throw the exception will at least make us aware of an issue. But if that happens we
    will probably need to find a better way to deal with network identification.
    """
    def find_network(self, provider_network_id, provider_id):
        networks = []
        if provider_network_id and provider_id:
            self._logger.debug("Getting network details in '%s' and with provider '%s'", provider_network_id, provider_id)
            db_args = {
                "KeyConditionExpression": Key('vpcId').eq(provider_network_id) & Key('provider_id').eq(provider_id),
                "IndexName": "vpcId-provider_id-index"
            }
            networks = self._query(self._tables['networks_table'], db_args)
            if len(networks) > 1:
                raise Exception("Found more than one network for vpcId %s and provider_id %s", provider_network_id, provider_id)
        else:
            self._logger.debug("Provider network id is not given, cannot fetch details.")

        return networks[0] if networks else None

    def read_network(self, network_id):
        self._logger.debug("Getting network details in " + network_id + "...")
        network = self._get_item(self._tables['networks_table'], {'network_id': network_id})
        return network

    def get_networks_by_provider_id(self, provider_id):
        db_args = {
            "KeyConditionExpression": Key('provider_id').eq(provider_id),
            "IndexName": "provider_id-index"
        }

        return self._query(self._tables['networks_table'], db_args)



    def put_network(self, network):
        return self._put_item(self._tables['networks_table'], network)

    def check_table(self, table_key):
        table_info = {}
        table_monitor = {"name": "DynamoDB monitor"}
        try:
            table_info["tableName"] = self._tables[table_key].table_name
            table_info["tableStatus"] = self._tables[table_key].table_status
            if table_info["tableStatus"] in ["CREATING", "UPDATING", "ACTIVE"]:
                table_monitor["status"] = "UP"
            else:
                table_monitor["status"] = "DOWN"
            table_monitor["tableInfo"] = table_info
        except:
            log_exception(sys.exc_info())
            table_monitor["status"] = "DOWN"

        return table_monitor


    def get_first_managed_server_event(self, support_id):
        event = None
        db_args = {
            "KeyConditionExpression": Key('eventId').eq(support_id),
            "ProjectionExpression": "eventId,eventTime",
            "Limit": 1
        }
        events = self._query(self._tables['events_table'], db_args)
        if len(events) > 0:
            event = events[0]
            self._logger.debug("Event found: {}".format(event))

        return event

    def put_event(self, event):
        self._put_item(self._tables['events_table'], event)


    def get_vpn_hubs(self):
        db_args = {
            "KeyConditionExpression": Key('enabled').eq('true'),
            "IndexName": "enabled-index"
        }

        return self._query(self._tables['vpn_hubs_table'], db_args)


    def get_active_vpn_tenant_by_ipv6_subnet(self, subnet):
        db_args = {
            "KeyConditionExpression": Key('ipv6_prefix').eq(subnet) & Key('status').eq('active'),
            "IndexName": "ipv6_prefix-status-index",
            "Limit": 1
        }

        tenants = self._query(self._tables['vpn_tenants_table'], db_args)
        if len(tenants) > 1:
            """
            When assigning a /96 subnet to a management appliance, the subnet is chosen randomly. This query is to
            determine in the subnet chosen is already in use. There should only be a single tenant for any given /96
            subnet. We do not want to throw an exception here because returning anything but an empty array will cause
            vpn-tenant-api to chose a different subnet. We log an error though because we definitely need to know if
            there are multiple management appliances assigned the same /96 CIDR block.
            """
            self._logger.error("Multiple tenants found for {}:\n{}".format(subnet, tenants))

        return self._query(self._tables['vpn_tenants_table'], db_args)

    def get_vpn_tenant(self, vpn_tenant_id):
        return self._get_item(self._tables['vpn_tenants_table'], {'vpn_tenant_id': vpn_tenant_id})

    def put_vpn_tenant(self, vpn_tenant):
        return self._put_item(self._tables['vpn_tenants_table'], vpn_tenant)


    def get_ticket(self, support_id, correlation_id):
        key = {
            'support_id': support_id,
            'correlation_id': correlation_id
        }

        return self._get_item(self._tables['tickets-table'], key)

    def update_ticket(self, db_args):
        return self._tables['tickets-table'].update_item(**db_args)


    def put_ticket(self, ticket):
        return self._put_item(self._tables['tickets-table'], ticket)

    def scan_tickets(self, db_args):
        return self.self._tables['tickets-table'].scan(**db_args)


    def query_tickets(self, db_args):
        return self._query(self._tables['tickets-table'], db_args)
