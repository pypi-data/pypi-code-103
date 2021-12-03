from py_eth_sig_utils.signing import sign_typed_data, v_r_s_to_signature
from swivel.constants import DOMAIN_NAME, DOMAIN_VERSION, HEX_PREFIX

class Signer:
    def sign_order(self, o, i, a, k):
        """Sign an order, producing an EIP712 compliant signature

        Parameters:
            o (dict) Swivel Order object
            i (int) ChainId
            a (string) Address of the deployed verifying contract
            k (bytes) Private key as bytes

        Returns:
            The signature hex with 0x prefix normalized
        """
        
        data = self.prepare_data()
        self.prepare_message(data, o)
        self.prepare_domain(data, i, a)

        sig = v_r_s_to_signature(*sign_typed_data(data, k)).hex()

        if sig.startswith(HEX_PREFIX):
            return sig
        else:
            return HEX_PREFIX + sig

    def prepare_message(self, d, o):
        """Update the data dictionary with the 'message' entry (Order)"""

        msg = { 'message': o }

        d.update(msg)

    def prepare_domain(self, d, i, a):
        """Update the data dictionary with the 'domain' entry"""

        domain = {
            'domain': {
                'name': DOMAIN_NAME,
                'version': DOMAIN_VERSION,
                'chainId': i,
                'verifyingContract': a,
            }
        }

        d.update(domain)

    def prepare_data(self):
        """Get the initial EIP712 compliant data dictionary to sign"""

        return {
            'types': {
                'EIP712Domain': [
                    { 'name': 'name', 'type': 'string' },
                    { 'name': 'version', 'type': 'string' },
                    { 'name': 'chainId', 'type': 'uint256' },
                    { 'name': 'verifyingContract', 'type': 'address' },
                ],
                'Order': [
                    { 'name': 'key', 'type': 'bytes32' },
                    { 'name': 'maker', 'type': 'address' },
                    { 'name': 'underlying', 'type': 'address' },
                    { 'name': 'vault', 'type': 'bool' },
                    { 'name': 'exit', 'type': 'bool' },
                    { 'name': 'principal', 'type': 'uint256' },
                    { 'name': 'premium', 'type': 'uint256' },
                    { 'name': 'maturity', 'type': 'uint256' },
                    { 'name': 'expiry', 'type': 'uint256' },
                ]
            },
            'primaryType': 'Order'
        }
