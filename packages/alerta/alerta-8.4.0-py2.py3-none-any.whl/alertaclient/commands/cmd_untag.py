import click

from alertaclient.utils import build_query


@click.command('untag', short_help='Untag alerts')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--query', '-q', 'query', metavar='QUERY', help='severity:"warning" AND resource:web')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--tag', '-T', 'tags', required=True, multiple=True, help='List of tags')
@click.pass_obj
def cli(obj, ids, query, filters, tags):
    """Remove tags from alerts."""
    client = obj['client']
    if ids:
        total = len(ids)
    else:
        if query:
            query = [('q', query)]
        else:
            query = build_query(filters)
        total, _, _ = client.get_count(query)
        ids = [a.id for a in client.get_alerts(query)]

    with click.progressbar(ids, label='Untagging {} alerts'.format(total)) as bar:
        for id in bar:
            client.untag_alert(id, tags)
