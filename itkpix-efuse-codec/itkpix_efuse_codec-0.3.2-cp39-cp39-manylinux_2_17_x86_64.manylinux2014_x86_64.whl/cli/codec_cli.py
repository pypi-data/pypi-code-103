"""itkpix-efuse-codec CLI"""

import click
import sys

import itkpix_efuse_codec
from itkpix_efuse_codec import EfuseData

@click.group(name="codec")
def cli():
    """The efuse codec CLI group."""

@cli.command()
@click.pass_context
@click.argument("probe-location", type=str)
@click.argument("chip-sn", type=str)
def encode(ctx, probe_location, chip_sn):
    """
    Construct the encoded E-fuse data
    """

    chip_sn = int(chip_sn, 16)
    encoded_binary_string = itkpix_efuse_codec.encode(probe_location, chip_sn)
    encoded_int = int(encoded_binary_string, 2)

    if ctx.obj["VERBOSE"] :
        print(f"Input:")
        print(f"   probe_location name  : {probe_location}")
        print(f"   chip serial number   : {chip_sn} (bin: {bin(chip_sn)}, hex: {hex(chip_sn)})")
        print(f"Encoded:")
        print(f"   encoded e-fuse (bin) : {encoded_binary_string} ({len(encoded_binary_string)} bits)")
        print(f"                  (hex) : 0x{hex(encoded_int)[2:]}")
    else :
        print(f"0x{hex(encoded_int)[2:]}")

@cli.command()
@click.pass_context
@click.argument("efuse-data", type = str)
def decode(ctx, efuse_data) :
    """
    Decode a retrieved e-fuse data word.
    """

    
    efuse_data = int(efuse_data, 16)
    decoded_binary_string = itkpix_efuse_codec.decode(efuse_data)
    decoded_int = int(decoded_binary_string, 2)

    if ctx.obj["VERBOSE"] :
        efuse_data = EfuseData(decoded_binary_string)
        print(f"Input:")
        print(f"    e-fuse data   (bin): {bin(decoded_int)}")
        print(f"                  (hex): {hex(decoded_int)}")
        print(f"Decoded:")
        print(f"    chip serial number : {hex(efuse_data.chip_sn())}")
        print(f"    probe location     : {efuse_data.probe_location_name()} (id: {hex(efuse_data.probe_location_id())})")
    else :
        print(f"0x{hex(decoded_int)[2:]}")
