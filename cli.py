import click
import os
from dotenv import load_dotenv
from services.web3service import web3service
import asyncio

@click.group()
def main():
    pass

@main.command()
@click.argument('address')
@click.option('--infra_key', help='the infra api key, defaults to the INFRA_KEY env')
def approvals(address, infra_key):
    """lists the approved approvals of a given address"""
    if not infra_key:
        infra_key = os.getenv('INFRA_KEY')
        if not infra_key:
            print("Missing infra API key please pass it via the --infra_key option or define it via the INFRA_KEY env")
            exit(1)
    infra = web3service(infra_key)
    result_list = asyncio.run(infra.get_all_approvals_events(address))
    for result in result_list:
        display_name = result.address
        if result.symbol:
            display_name = result.symbol
        elif result.name:
            display_name = result.name 
        print(f"approval on {display_name} on amount of {result.value}")


if __name__ == '__main__':
    load_dotenv()
    main()