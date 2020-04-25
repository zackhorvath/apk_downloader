#!/usr/bin/env python3
# coding: utf-8
import asyncio
from aiohttp import ClientSession
import os
import argparse
import lib.apkpure_download as apkpure

# Configures script parameters
about = "This script asynchronously downloads APKs from APKPure."
parser = argparse.ArgumentParser(description=about)
parser.add_argument(
    "-a",
    "--app",
    nargs='+',
    help="App Package name(s). ex: 'com.appname.android', or 'com.appname1.android com.appname2.android'",
    required=True,
    type=str,
)
parser.add_argument(
    "-v",
    "--version",
    help="App Package version. ex: '12.0.34', or 'latest'",
    default="latest",
    type=str,
)
parser.add_argument(
    "-o",
    "--output",
    help="The output directory. Default: './apks'",
    default="apks/",
    type=str,
)
parser.add_argument(
    "-t",
    "--timeout",
    help="Customizes the download timeout in seconds. Default: '300' (5 Minutes)",
    default=300,
    type=int,
)
args = parser.parse_args()
app_dir = os.path.join(args.output, "")

# Creates multiple download threads per app argument
async def main(loop):
    async with ClientSession() as session:
        await asyncio.gather(
            *[
                apkpure.get_apk(session, args.app, args.version, app_dir, args.timeout)
                for args.app in args.app
            ]
        )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
