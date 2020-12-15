import click

from lib import ImportService, PackageBucket, PackageDirectory

@click.group()
def cli():
    pass

@click.command()
@click.option('-s', '--s3-mount-point', required=True, help='Amazon Web Services S3 mount point')
def sync(s3_mount_point):
    aws_bucket = PackageBucket(s3_mount_point)
    aws_bucket.download()

@click.command()
@click.option('-s', '--s3-mount-point', required=True, help='Amazon Web Services S3 mount point')
@click.option('-u', '--dspace-submitter', required=True, help='user account for the DSpace installation')
@click.option('-d', '--dspace-home', default='/dspace', help='directory path for the DSpace installation')
def ingest(s3_mount_point, dspace_submitter, dspace_home):
    aws_bucket = PackageBucket(s3_mount_point)

    import_service = ImportService(dspace_home, dspace_submitter, aws_bucket)
    import_service.configure_logging()

    package_dir = PackageDirectory(aws_bucket.mount_point, import_service)
    package_dir.ingest()

cli.add_command(sync)
cli.add_command(ingest)

if __name__ == '__main__':
    cli()
