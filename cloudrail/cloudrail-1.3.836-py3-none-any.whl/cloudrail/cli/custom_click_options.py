import click


class OptionRequiredIf(click.Option):
    """
    Option is required if the context has `option` set to `value`
    """

    def __init__(self, *a, **k):
        try:
            option = k.pop('option')
            value  = k.pop('value')
            depends_on_flag = k.pop('depends_on_flag', None)
        except KeyError:
            raise(KeyError('OptionRequiredIf needs the option and value keywords arguments'))

        click.Option.__init__(self, *a, **k)
        self._option: str = option
        self._value = value
        self._depends_on_flag = depends_on_flag

    def full_process_value(self, ctx, value):
        value = super().full_process_value(ctx, value)
        if value is None and ctx.params[self._option.replace('-', '_')] == self._value:
            if self._depends_on_flag:
                if self._value:
                    msg = f'Required if {self._option} is set.'
                else:
                    msg = f'Required if {self._option} is not set.'
            else:
                msg = f'Required if --{self._option}={self._value}.'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        return value
