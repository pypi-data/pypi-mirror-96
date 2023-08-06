import sys

import click


@click.command('me', short_help='Update current user')
@click.option('--name', help='Name of user')
@click.option('--email', help='Email address (login username)')
@click.option('--password', help='Password')
@click.option('--status', help='Status eg. active, inactive')
@click.option('--text', help='Description of user')
@click.pass_obj
def cli(obj, name, email, password, status, text):
    """Update current user details, including password reset."""
    if not any([name, email, password, status, text]):
        click.echo('Nothing to update.')
        sys.exit(1)

    client = obj['client']
    try:
        user = client.update_me(name=name, email=email, password=password, status=status, attributes=None, text=text)
    except Exception as e:
        click.echo('ERROR: {}'.format(e), err=True)
        sys.exit(1)
    click.echo(user.id)
