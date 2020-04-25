# apk_downloader
This is a utility for bulk downloading APK packages from various APK download sites, leveraging asyncrhonous downloads using `asyncio`. It currently downloads from apkpure.com but there is planned functionality to support multiple download sites that don't use Captcha. The original idea for using beautifulsoup to parse html for the download links was sourced from [0x27](https://github.com/0x27/apkpure_get), with rewrites done by me to make it asyncrhonous, to improve URL construction logic, and make it a little more robust.

```
usage: apk_download.py [-h] -a APP [APP ...] [-v VERSION] [-o OUTPUT]
                       [-t TIMEOUT]

This script asynchronously downloads APKs.

Arguments:
  -h, --help            show this help message and exit
  -a APP [APP ...], --app APP [APP ...]
                        App Package name(s). ex: 'com.appname.android', or 'com.appname1.android com.appname2.android'
  -v VERSION, --version VERSION
                        App Package version. ex: '12.0.34', or 'latest'
  -o OUTPUT, --output OUTPUT
                        The output directory. Default: './apks'
  -t TIMEOUT, --timeout TIMEOUT
                        Customizes the download timeout in seconds. Default: '300' (5 Minutes)
```

## Installation & Running
1) Clone the repo to your machine.
2) Run `pip3 install -r requirements.txt` from inside the cloned directory to install dependencies.
3) Run `apk_download.py -a com.appname.android` to download your desired APKs!

### Tips
* The `-a` argument is required, but can accept multiple package names, e.g. "com.appname1.android com.appname2.android". When you are downloading multiple packages it is recommended to leave `-v` unset.
* The `-v` argument sets what version of the app you would like to download. This defaults to `latest` for ease of use, but you can, for example, specify `267.1.0.46.120` to target `V267.1.0.46.120` that appears in the "previous versions" section of apkpure.
* The folder structure for downloaded files is: `apks/com.appname.android/version/com.appname.android.apk`. A real life example of this would be `apks/me.lyft.android/latest/me.lyft.android.apk`.

### A note about XAPK files
Some files exist as `.xapks` on apkpure - these are apk bundles using some kind of proprietary bundling mechanism. This script will rename these files to have a `.xapk` file extension if it detects the original filename had `.xapk` in it. Inside these `.xapk` bundles there are several `.apk` files, one of which will be the main `.apk` you are probably looking for. Therefore, to properly decompile a `.xapk` you will likely need to run your decompiler *twice*. Below is some bash I have written to achieve that...
```
# Where $JADX_DIR is where JADX resides. Substitute with whatever your decompiler workflow is.
xapk_decompile () {
    for package in apks/**/*.xapk; do
        package_dir=$(dirname "${package}")
        package_name=$(basename "${package}" .xapk)
        package_version=$(basename "${package_dir}")
        echo "INFO: Decompiling $package."
        $JADX_DIR/bin/jadx $package -dr $package_dir
        # Remove the extra .apk files
        find $package_dir ! -name $package_name.apk -type f -exec rm -f {} +
        echo "INFO: Re-decompiling $package_name."
        $JADX_DIR/bin/jadx $package_dir/$package_name.apk -dr $package_dir/resources
    done
```

## Troubleshooting
---
There are a few assumptions that are made in the code. This section outlines some of the 'gotchas' you may run into.  
  
* **Packages Aren't Being Downloaded**
  * There are a few culprits with this, but the design of the apkpure_downloader web scraper makes an assumption that the first result using `"https://apkpure.com/search?q=%s" % package_name` will contain the wanted package name. You can manually check using that URL to determine if your package is properly named in the database, or if the correct listing is first.
  * Another potential issue is some packages are DMCA'd from the APKPure platform, meaning that when the link constructor does its thing it will generate a null download link. In this case, the script will generate an exception and move on.