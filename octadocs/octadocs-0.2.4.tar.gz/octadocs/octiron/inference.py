import logging
import textwrap
from pathlib import Path

import owlrl
from owlrl import OWLRL_Extension
from rdflib import ConjunctiveGraph

logger = logging.getLogger(__name__)


def apply_inference_owlrl(graph: ConjunctiveGraph) -> None:
    """Apply OWL RL inference rules."""
    logger.info('Inference: OWL RL started...')
    owlrl.DeductiveClosure(OWLRL_Extension).expand(graph)
    logger.info('Inference: OWL RL complete.')


def apply_inference_sparql(
    inference_directory: Path,
    graph: ConjunctiveGraph,
) -> bool:
    """Apply custom SPARQL inference rules."""
    if inference_directory.is_dir():
        query_files = list(sorted(   # noqa: C413
            inference_directory.glob('**/*.sparql'),
        ))
    else:
        query_files = []

    if not query_files:
        logger.info(
            'No SPARQL inference files found at %s directory.',
            inference_directory,
        )
        return False

    logger.warning(
        'SPARQL inference queries are an outdated feature. Files: %s',
        query_files,
    )
    for query_file in query_files:
        logger.info(
            'Inference: %s',
            query_file.relative_to(inference_directory),
        )

        query_text = query_file.read_text()
        logger.debug('  Query text: %s', textwrap.indent(
            query_text,
            prefix='  ',
        ))

        graph.update(query_text)

    return True
