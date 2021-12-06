#!/usr/bin/env python3
import argparse
import os.path
import shutil
import subprocess
import sys
import zipfile


def report_bitbucket_status(auth, commit, status):
    import requests
    endpoint = ("https://api.bitbucket.org/2.0/repositories/suprocktech/"
                "asphodel/commit/{}/statuses/build").format(commit)
    requests.post(endpoint, auth=auth, data=status)


def run_cmake(args):
    path = os.environ["PATH"]
    path += os.pathsep + r"C:\Program Files\CMake\bin"
    path += os.pathsep + r"C:\Program Files (x86)\CMake\bin"
    cmake = shutil.which("cmake", path=path)
    cmake_args = [cmake]
    cmake_args.extend(args)
    subprocess.check_call(cmake_args)


def create_zip(zip_name, directory):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(directory):
            for file in files:
                fullpath = os.path.join(root, file)
                relpath = os.path.relpath(fullpath, start=directory)
                zip.write(fullpath, arcname=relpath)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="build_dir", required=True,
                        help="build directory")
    parser.add_argument("-G", dest="generator", required=True,
                        help="CMake generator")
    parser.add_argument("-z", dest="zip", help="Zip file name")
    parser.add_argument("-t", dest="type", default="RelWithDebInfo",
                        help='CMake build type')
    parser.add_argument("-c", dest="commit", metavar="HASH",
                        help='commit id to send to bitbucket')
    parser.add_argument("-k", dest="status_key", metavar="KEY",
                        help='key sent to bitbucket (e.g. "win32")')
    parser.add_argument("-n", dest="status_name", metavar="NAME",
                        help='name sent to bitbucket (e.g. "Win32 Binaries")')
    parser.add_argument("-u", dest="status_url", metavar="URL",
                        help='INPROGRESS and FAILED url passed to bitbucket')
    parser.add_argument("-s", dest="s3_bucket", metavar="S3_BUCKET",
                        help='S3 bucket for uploading',
                        default='suprock-public-software')
    parser.add_argument("-p", dest="s3_prefix", metavar="S3_PREFIX",
                        help='S3 prefix when uploading', default='')
    parser.add_argument("cmake_args", nargs="*",
                        help="Extra arguments passed to CMake")
    args = parser.parse_args()
    
    bb_args = ['commit', 'status_key', 'status_name', 'status_url']
    bb_args_defined = [getattr(args, k) is not None for k in bb_args]
    if any(bb_args_defined):
        if not all(bb_args_defined):
            parser.error('all bitbucket arguments must be given together')

        if 'BB_AUTH_STRING' not in os.environ:
            raise Exception("BB_AUTH_STRING environment var must be defined")
        auth = tuple(os.environ['BB_AUTH_STRING'].split(":", 1))
        status = {"state": "INPROGRESS",
                  "key": args.status_key,
                  "name": args.status_name,
                  "url": args.status_url}
        report_status = True
    else:
        report_status = False

    if report_status:
        report_bitbucket_status(auth, args.commit, status)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))
    build_dir = os.path.join(root_dir, args.build_dir)
    output_dir = os.path.join(build_dir, "output")

    # make the build dir
    os.makedirs(build_dir, exist_ok=True)

    # cd to the build dir
    os.chdir(build_dir)

    try:
        # configure
        configure_args = ["-G", args.generator,
                          "-DCMAKE_BUILD_TYPE=" + args.type,
                          "-DCMAKE_INSTALL_PREFIX=" + output_dir]
        configure_args.extend(sys.argv[1:])
        configure_args.append(root_dir)
        run_cmake(configure_args)

        # build
        run_cmake(["--build", ".", "--config", args.type,
                   "--target", "install"])

        # create zip file
        if args.zip:
            create_zip(args.zip, output_dir)

            if report_status:
                # try uploading to S3
                import boto3
                s3 = boto3.client('s3')
                key = "{}{}".format(args.s3_prefix, args.zip)
                s3.upload_file(args.zip, args.s3_bucket, key)
                zip_url = 'https://{}.s3.amazonaws.com/{}'
                status['url'] = zip_url.format(args.s3_bucket, key)

        if report_status:
            status['state'] = "SUCCESSFUL"
            report_bitbucket_status(auth, args.commit, status)
    except:
        if report_status:
            status['state'] = "FAILED"
            report_bitbucket_status(auth, args.commit, status)
        raise


if __name__ == "__main__":
    main()
