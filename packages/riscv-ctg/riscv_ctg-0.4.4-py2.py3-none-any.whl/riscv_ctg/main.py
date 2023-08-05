# See LICENSE.incore for details
"""Console script for riscv_ctg."""

import click,os,shutil

from riscv_ctg.log import logger
from riscv_ctg.ctg import ctg
from riscv_ctg.__init__ import __version__
from riscv_ctg.constants import env,gen_sign_dataset,gen_usign_dataset
from riscv_isac.cgf_normalize import expand_cgf
@click.command()
@click.version_option(prog_name="RISC-V Compliance Test Generator",version=__version__)
@click.option('--verbose', '-v', default='error', help='Set verbose level', type=click.Choice(['info','error','debug'],case_sensitive=False))
@click.option('--out-dir', '-d', default='./', type=click.Path(resolve_path=True,writable=True), help='Output directory path')
@click.option('--randomize','-r', default=False , is_flag='True', help='Randomize Outputs.')
@click.option('--cgf','-cf',multiple=True,type=click.Path(exists=True,resolve_path=True,readable=True),help="Path to the cgf file(s). Multiple allowed.")
@click.option('--procs','-p',type=int,default=1,help='Max number of processes to spawn')
@click.option('--base-isa','-bi',type=click.Choice(['rv32e','rv32i','rv64i']),help="Base ISA string for the tests.")
def cli(verbose, out_dir, randomize , cgf,procs,base_isa):
    logger.level(verbose)
    logger.info('****** RISC-V Compliance Test Generator {0} *******'.format(__version__ ))
    logger.info('Copyright (c) 2020, InCore Semiconductors Pvt. Ltd.')
    logger.info('All Rights Reserved.')
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    logger.info("Copying env folder to Output directory.")
    env_dir = os.path.join(out_dir,"env")
    if not os.path.exists(env_dir):
        shutil.copytree(env,env_dir)
    if '32' in base_isa:
        xlen = 32
    elif '64' in base_isa:
        xlen = 64
    ctg(verbose, out_dir, randomize ,xlen, cgf,procs,base_isa)
