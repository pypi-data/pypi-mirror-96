import click

from alertaclient.utils import build_query


@click.command('note', short_help='Add note')
@click.option('--ids', '-i', metavar='UUID', multiple=True, help='List of note IDs')
@click.option('--alert-ids', '-i', metavar='UUID', multiple=True, help='List of alert IDs (can use short 8-char id)')
@click.option('--query', '-q', 'query', metavar='QUERY', help='severity:"warning" AND resource:web')
@click.option('--filter', '-f', 'filters', metavar='FILTER', multiple=True, help='KEY=VALUE eg. serverity=warning resource=web')
@click.option('--text', help='Note or message')
@click.option('--delete', '-D', metavar='ID', nargs=2, help='Delete note parent ID and note ID')
@click.pass_obj
def cli(obj, ids, alert_ids, query, filters, text, delete):
    """Add or delete note to alerts."""
    client = obj['client']
    if delete:
        client.delete_alert_note(*delete)
    else:
        if alert_ids:
            total = len(alert_ids)
        else:
            if query:
                query = [('q', query)]
            else:
                query = build_query(filters)
            total, _, _ = client.get_count(query)
            alert_ids = [a.id for a in client.get_alerts(query)]

        with click.progressbar(alert_ids, label='Add note to {} alerts'.format(total)) as bar:
            for id in bar:
                client.alert_note(id, text=text)
