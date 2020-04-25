from bs4 import BeautifulSoup
import asyncio
import progressbar
import os
import aiofiles
import re
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

# APK Download Site (do not change this)
SITE = "https://apkpure.com"

# These functions download APK files from the SITE variable.
# The package_version variable ( default = latest ) determines if additional url construction is required. There is an additional assumption that package_name will yield the first result in the search function of the SITE variable.
async def get_apk(session, package_name, package_version, app_dir, timeout):
    url = f"{SITE}/search?q={package_name}"
    output_dir = os.path.join(app_dir, package_name, package_version)
    output_file = os.path.join(output_dir, f"{package_name}.apk")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    async with session.get(url) as html:
        parse = BeautifulSoup(await html.text(), "html.parser")
        for i in parse.find("p"):
            try:
                a_url = i["href"]
                app_url = SITE + a_url
                app_download_url = app_url + "/download?from=details"
                # Looks for "versioned" APKs...
                if package_version != "latest":
                    async with session.get(app_url) as html2:
                        parse2 = BeautifulSoup(await html2.text(), "html.parser")
                        regex = re.compile(package_version)
                        download_landing_url = (
                            SITE + parse2.find("a", title=regex)["href"]
                        )
                        # If a "versioned" APK has a "variant", find and download the first one - architecture does not matter...
                        if "variant" in download_landing_url:
                            async with session.get(download_landing_url) as html3:
                                parse3 = BeautifulSoup(
                                    await html3.text(), "html.parser"
                                )
                                download_link = (
                                    SITE + parse3.find("a", text="Download")["href"]
                                )
                        else:
                            async with session.get(download_landing_url) as html3:
                                parse3 = BeautifulSoup(
                                    await html3.text(), "html.parser"
                                )
                                for link in parse3.find_all("a", id="download_link"):
                                    download_link = link["href"]
                                # Targets the last download link on the page
                elif package_version == "latest":
                    async with session.get(app_download_url) as html2:
                        parse2 = BeautifulSoup(await html2.text(), "html.parser")
                        for link in parse2.find_all("a", id="download_link"):
                            download_link = link["href"]
                        # Targets the last download link on the page
            except TypeError as e:
                print(
                    f"ERROR: Unable to get 'href' attribute in <p> tag for {package_name} {package_version}!"
                )
            try:
                await asyncio.wait_for(
                    download_apk(session, download_link, output_file), timeout
                )
            except UnboundLocalError as error:
                print(
                    f"ERROR: Unable to generate download URL for {package_name} {package_version}!"
                )
                return None
    return (package_name, package_version)


# Progress Bar
async def make_progress_bar():
    return progressbar.ProgressBar(
        redirect_stdout=True,
        redirect_stderr=True,
        widgets=[
            progressbar.Percentage(),
            progressbar.Bar(),
            " (",
            progressbar.AdaptiveTransferSpeed(),
            " ",
            progressbar.ETA(),
            ") ",
        ],
    )


async def download_apk(session, download_link, output_file):
    if "xapk" in download_link:
        output_file = re.sub(r".apk", ".xapk", output_file)
    async with session.get(download_link) as response:
        print(f"INFO: Downloading to {output_file}")
        async with aiofiles.open(output_file, "wb") as fd:
            total_length = int(response.headers.get("content-length"))
            bar = await make_progress_bar()
            bar_progress = 0
            bar.start(total_length)
            while True:
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                bar_progress += len(chunk)
                bar.update(bar_progress)
                await fd.write(chunk)
            bar.finish()
        return await response.release()
