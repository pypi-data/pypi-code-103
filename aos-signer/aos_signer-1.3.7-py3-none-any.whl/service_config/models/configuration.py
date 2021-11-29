from uuid import UUID

from jsonschema import ValidationError

from .config_chapter import ConfigChapter


class Configuration(ConfigChapter):

    def __init__(self,
                 state,
                 layers,
                 env,
                 cmd,
                 working_dir,
                 quotas,
                 alert,
                 hostname,
                 exposed_ports,
                 allowed_connections,
                 devices,
                 resources):
        self._state = state
        self._layers = layers
        self._env = env
        self._cmd = cmd
        self._working_dir = working_dir
        self._quotas = quotas
        self._alert = alert
        self._hostname = hostname
        self._exposed_ports = exposed_ports
        self._allowed_connections = allowed_connections
        self._devices = devices
        self._resources = resources

    @property
    def state(self):
        return self._state

    @property
    def layers(self):
        return self._layers

    @property
    def env(self):
        return self._env

    @property
    def cmd(self):
        return self._cmd

    @property
    def working_dir(self):
        return self._working_dir

    @property
    def quotas(self):
        return self._quotas

    @property
    def hostname(self):
        return self._hostname

    @property
    def exposed_ports(self):
        return self._exposed_ports

    @property
    def allowed_connections(self):
        return self._allowed_connections

    @property
    def devices(self):
        return self._devices

    @property
    def resources(self):
        return self._resources

    @staticmethod
    def from_yaml(input_dict):
        p = Configuration(
            input_dict.get('state'),
            input_dict.get('layers'),
            input_dict.get('env'),
            input_dict.get('cmd'),
            input_dict.get('workingDir'),
            input_dict.get('quotas'),
            input_dict.get('alert'),
            input_dict.get('hostname'),
            input_dict.get('exposedPorts'),
            input_dict.get('allowedConnections'),
            input_dict.get('devices'),
            input_dict.get('resources'),
        )
        ConfigChapter.validate(input_dict, validation_file='configuration_schema.json')
        p.validate_exposed_ports()
        p.validate_allowed_connections()
        return p

    def validate_allowed_connections(self):
        if not self._allowed_connections:
            return

        for con in self._allowed_connections:
            data = con.split('/')

            if len(data) != 3:
                raise ValidationError(
                    f'Wrong format in "{con}". '
                    f'\n Supported formats are: '
                    f'\n  - "service-guid/port/protocol"'
                    f'\n  - "service-guid/port-port/protocol" '
                )
            Configuration._validate_uuid(data[0])
            Configuration._validate_port_range(data[1])
            Configuration._validate_protocol(data[2])

    def validate_exposed_ports(self):
        if not self._exposed_ports:
            return

        for port in self._exposed_ports:
            if isinstance(port, int):
                continue

            parts = port.split('/')
            if len(parts) > 2:
                raise ValidationError(
                    f'Wrong format in "{port}". '
                    f'\n Supported formats are: '
                    f'\n  - "port-port/protocol"'
                    f'\n  - "port/protocol" '
                    f'\n  - "port".'
                )
            if parts[1]:
                Configuration._validate_protocol(parts[1])
            Configuration._validate_port_range(parts[0])

    @staticmethod
    def _validate_protocol(protocol_str: str):
        if protocol_str not in ['tcp', 'udp']:
            raise ValidationError(
                f'Unknown protocol "{protocol_str}". '
                f'\n Known protocols are : "tcp", "udp"'
            )

    @staticmethod
    def _validate_port_range(port_range_config: str):
        ports = port_range_config.split('-')
        if len(ports) > 2:
            raise ValidationError(
                f'Unsupported port range config in "{port_range_config}"'
            )

        for p in ports:
            if not p.isdigit():
                raise ValidationError(f'Port "{p}" is not a valid port number.')

        if len(ports) == 2 and int(ports[0]) >= int(ports[1]):
            raise ValidationError(f'Start port "{ports[0]}" is bigger or same than the last "{ports[1]}"')

    @staticmethod
    def _validate_uuid(uuid_to_test):
        try:
            UUID(uuid_to_test, version=4)
        except ValueError:
            raise ValidationError(f'Service GUID "{uuid_to_test}" is not valid')
