import click
import os
from dotenv import load_dotenv
from InfraWrapper import InfraWrapper

@click.group()
def main():
    pass

@main.command()
@click.argument('address')
@click.option('--infra_key', help='the infra api key, defaults to the INFRA_KEY env')
def approvals(address, infra_key):
    """lists the approved approvals of a given address"""
    if infra_key is None:
        infra_key = os.getenv('INFRA_KEY')
        if not infra_key:
            print("Missing infra API key please pass it via the --infra_key option or define it via the INFRA_KEY env")
            exit(1)
    infra = InfraWrapper(infra_key)
    result_list = infra.get_all_approvals_events(address)
    for result in result_list:
        print(f"approval on {result['name']} on amount of {result['value']}")


if __name__ == '__main__':
    load_dotenv()
    main()