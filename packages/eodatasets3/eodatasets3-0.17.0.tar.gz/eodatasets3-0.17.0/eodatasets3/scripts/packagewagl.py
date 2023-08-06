"""
Package WAGL HDF5 Outputs

This will convert the HDF5 file (and sibling fmask/gqa files) into
GeoTIFFS (COGs) with datacube metadata using the DEA naming conventions
for files.
"""
from pathlib import Path
from typing import Sequence

import click
import rasterio
from click import secho

from eodatasets3 import wagl
from eodatasets3.ui import PathPath


@click.command(help=__doc__)
@click.option(
    "--level1",
    help="Optional path to the input level1 metadata doc "
    "(otherwise it will be loaded from the level1 path in the HDF5)",
    required=False,
    type=PathPath(exists=True, readable=True, dir_okay=False, file_okay=True),
)
@click.option(
    "--output",
    help="Put the output package into this directory",
    required=True,
    type=PathPath(exists=True, writable=True, dir_okay=True, file_okay=False),
)
@click.option(
    "-p",
    "--product",
    "products",
    help="Package only the given products (can specify multiple times)",
    type=click.Choice(wagl.POSSIBLE_PRODUCTS, case_sensitive=False),
    multiple=True,
)
@click.option(
    "--with-oa/--no-oa",
    "with_oa",
    help="Include observation attributes (default: true)",
    is_flag=True,
    default=True,
)
@click.argument("h5_file", type=PathPath(exists=True, readable=True, writable=False))
def run(
    level1: Path, output: Path, h5_file: Path, products: Sequence[str], with_oa: bool
):
    if products:
        products = set(p.lower() for p in products)
    else:
        products = wagl.DEFAULT_PRODUCTS
    with rasterio.Env():
        for granule in wagl.Granule.for_path(h5_file, level1_metadata_path=level1):
            with wagl.do(
                f"Packaging {granule.name}. (products: {', '.join(products)})",
                heading=True,
                fmask=bool(granule.fmask_image),
                fmask_doc=bool(granule.fmask_doc),
                gqa=bool(granule.gqa_doc),
                oa=with_oa,
            ):
                dataset_id, dataset_path = wagl.package(
                    out_directory=output,
                    granule=granule,
                    included_products=products,
                    include_oa=with_oa,
                )
                secho(f"Created folder {click.style(str(dataset_path), fg='green')}")


if __name__ == "__main__":
    run()
