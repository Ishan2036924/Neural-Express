"""CLI entrypoint for Neural Express."""

import sys
import asyncio
from pathlib import Path
import click

from .config.settings import Settings
from .main import NeuralExpress


@click.command()
@click.argument("command", type=click.Choice(["run"]))
@click.option(
    "--mode",
    type=click.Choice(["daily", "weekly"]),
    default="daily",
    help="Newsletter mode (daily or weekly)"
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Custom configuration file"
)
@click.option(
    "--mock",
    is_flag=True,
    help="Use mock data (no API calls)"
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Custom output directory"
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose logging"
)
@click.option(
    "--email",
    is_flag=True,
    help="Send newsletter via email after generation"
)
def main(
    command: str,
    mode: str,
    config: Path,
    mock: bool,
    output: Path,
    verbose: bool,
    email: bool
):
    """
    NEURAL EXPRESS - AI News Newsletter Generator

    Commands:
        run     Run the newsletter generation pipeline
    """
    if command == "run":
        asyncio.run(run_pipeline(mode, config, mock, output, verbose, email))


async def run_pipeline(
    mode: str,
    config_path: Path,
    use_mock: bool,
    output_dir: Path,
    verbose: bool,
    send_email: bool
):
    """Run the newsletter generation pipeline."""
    try:
        # Load settings
        settings = Settings(config_path=config_path)

        # Override output directory if specified
        if output_dir:
            settings.output_dir = output_dir
            settings.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize pipeline
        pipeline = NeuralExpress(settings, verbose=verbose, send_email=send_email)

        # Run
        output_path = await pipeline.run(mode=mode, use_mock=use_mock)

        # Success
        click.echo(click.style("\n✓ Newsletter generated successfully!", fg="green"))
        click.echo(f"\nOutput: {output_path}")

    except Exception as e:
        click.echo(click.style(f"\n✗ Error: {e}", fg="red"), err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
