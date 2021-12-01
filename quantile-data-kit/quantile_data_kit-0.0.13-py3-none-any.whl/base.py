from typing import Any, Dict, List, Sequence, Set

from dagster import (
    Field,
    InputDefinition,
    OutputDefinition,
    SolidDefinition,
    SolidExecutionContext,
)
from dagster.core.definitions.events import Output


class BaseComponent:
    input_defs: List[InputDefinition] = []
    output_defs: List[OutputDefinition] = []
    config_schema: Dict[str, Field] = {}
    required_resource_keys: Set[str] = set()
    tags: Dict[str, str] = {}

    @classmethod
    def _compute_hook(cls, step_context: SolidExecutionContext, inputs: Dict[str, Any]):
        """The compute hook that runs the actual compute function.
            Needs to overridden by the descendant classes.

        Args:
            step_context (SolidExecutionContext): The Dagster execution context.
            inputs (Dict[str, Any]): The inputs that are supplied to the solid as a dictionary.

        Raises:
            NotImplementedError: The compute hook is not implemented by default.
        """
        # Run the compute function ("cls.compute_function" needs to be defined by the children)
        # The inputs of the previous and solid config are injected into the compute function
        results = getattr(cls, cls.compute_function)(
            **inputs, **step_context.solid_config
        )

        # If the results are not a sequence, wrap it in a list
        if not isinstance(results, Sequence):
            results = [results]

        # Zip the results with the output definitions and yield the results
        for result, output_def in zip(results, cls.output_defs):
            yield Output(result, output_def.name)

    @classmethod
    def to_solid(cls, name: str) -> SolidDefinition:
        """Generates a solid definition for this component.

        Args:
            name (str): The name of the solid.
            input_defs (List[InputDefinition], optional): The list of Dagster input values. Defaults to [].
            output_defs (List[OutputDefinition], optional): The list of Dagster output values. Defaults to [].

        Returns:
            SolidDefinition: The Solid that is used by Dagster to execute this component .
        """
        return SolidDefinition(
            name=name,
            input_defs=cls.input_defs,
            output_defs=cls.output_defs,
            required_resource_keys=cls.required_resource_keys,
            config_schema=cls.config_schema,
            compute_fn=cls._compute_hook,
            tags=cls.tags,
        )
