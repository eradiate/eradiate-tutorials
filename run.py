from __future__ import annotations

import glob
import subprocess
from pathlib import Path

import click

import eradiate
from eradiate.typing import PathLike


def list_tutorials(root_dir: PathLike | None, globs: list[str] | None) -> list[Path]:
    result = set()

    for g in globs:
        for tutorial_file in glob.glob(f"{root_dir}/{g}"):
            if tutorial_file.endswith(".ipynb"):
                result.add(Path(tutorial_file))

    return sorted(result)


@click.group()
@click.option(
    "--root-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Root directory of the tutorial collection "
    "(default: '$ERADIATE_SOURCE_DIR/tutorials').",
)
@click.option(
    "--globs",
    type=str,
    help="A list of globs used to filter tutorials, relative to the root directory.",
)
@click.pass_context
def main(ctx, root_dir: str, globs: str):
    """
    Run Eradiate tutorials.
    """
    ctx.obj = {}

    if root_dir is None:
        root_dir = eradiate.config.source_dir / "tutorials"
    else:
        root_dir = Path(root_dir)
    ctx.obj["root_dir"] = root_dir

    if globs is None:
        globs = globs = ["**/*"]
    else:
        globs = [x.strip() for x in globs.split(",")]
    ctx.obj["globs"] = globs


@click.command()
@click.option("--relative", is_flag=True)
@click.pass_context
def ls(ctx, relative):
    """
    List available tutorials.
    """
    root_dir = ctx.obj["root_dir"]
    globs = ctx.obj["globs"]

    print(f"Looking up '{root_dir}'")

    filenames = list_tutorials(root_dir, globs)
    for filename in filenames:
        if relative:
            print(filename.relative_to(root_dir))
        else:
            print(filename)


@click.command()
@click.argument("filenames", nargs=-1)
@click.pass_context
def run(ctx, filenames):
    """
    Render tutorial files specified as FILENAMES. If none is specified, all
    tutorials will be rendered.
    """
    root_dir = ctx.obj["root_dir"]
    globs = ctx.obj["globs"]

    if not filenames:
        filenames = list_tutorials(root_dir, globs)

    errors = []

    for filename in filenames:
        cmd = [
            "jupyter",
            "nbconvert",
            str(filename),
            "--to",
            "notebook",
            "--inplace",
            "--execute",
        ]
        print(" ".join(cmd))
        output = subprocess.run(cmd)

        if output.returncode != 0:
            errors.append(filename)

    if errors:
        print()
        print("The following tutorials did not run without error:")
        for error in errors:
            print(error)

        exit(1)


main.add_command(ls)
main.add_command(run)


if __name__ == "__main__":
    main()
