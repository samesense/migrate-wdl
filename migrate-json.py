"""Replace public gs image url w/ project gs.
   Cp data to my project.
   (data cannot be copied directly between buckets)
"""
import subprocess
import argparse
import os
import json

parser = argparse.ArgumentParser(description="Migrate broad json files to gcp vpc")
parser.add_argument("-d", "--delete", action="store_true", help="Delete local gs data.")
parser.add_argument("bucket", type=str, help="GCP project")
parser.add_argument("sa", type=str, help="Service account json")
parser.add_argument("json", type=str, help="Input json.")
parser.add_argument("json_out", type=str, help="Output json.")


def strip_gs(gs_url):
    print('debug url', gs_url)
    return gs_url[5:]


def mk_new_gs(project, gs_url):
    """
    gs://gatk-test-data/intervals/hg38_wgs_scattered_calling_intervals.txt
    """
    path = strip_gs(gs_url)
    return f"gs://{project}/data/ref-data/{path}"


def update_json(project, jsn, json_out):
    """Return set of gcs urls."""
    urls = set()
    with open(jsn) as f:
        j = json.load(f)
        for field in j:
            val = j[field]
            if isinstance(val, str):
                if val[:5].startswith("gs://"):
                    gs_url = val
                    new_gs = mk_new_gs(project, gs_url)
                    j[field] = new_gs
                    urls.add((gs_url, new_gs))

    with open(json_out, "w") as fout:
        json.dump(j, fout)

    return urls

def mk_auth_cmd(sa):
    cmd = f'gcloud auth activate-service-account --key-file={sa}'
    return cmd

def cp_data(delete, project, url, auth):
    """
    """
    src, dest = url
    src_set = set()
    local = strip_gs(src)
    have_file = subprocess.run([f'{auth}; gsutil -q stat "{dest}" || echo "no"'], shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(have_file, dest)
    if 'no\n' == have_file:
        src_set.add(local)
        os.system(f"gsutil cp {src} {local}")
        print(local)
        os.system(f"{auth}; gsutil cp {local} {dest}")

    # recursive cp data
    # if dest.endswith('.txt'):

    if delete:
        for local in src_set:
            os.system(f"rm {local}")


def migrate(delete_data, bucket, sa, jsn, json_out):
    urls = update_json(bucket, jsn, json_out)
    auth = mk_auth_cmd(sa)
    for url in urls:
        print(url)
        cp_data(delete_data, bucket, url, auth)


def main(args=None):
    args = parser.parse_args(args=args)
    migrate(args.delete, args.bucket, args.sa, args.json, args.json_out)


if __name__ == "__main__":
    main()
