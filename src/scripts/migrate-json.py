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
    #print("debug url", gs_url)
    return gs_url[5:]


def mk_new_gs(project, gs_url):
    """
    gs://gatk-test-data/intervals/hg38_wgs_scattered_calling_intervals.txt
    """
    path = strip_gs(gs_url)
    return f"gs://{project}/data/ref-data/{path}"

def udate_url(field, project, gs_url, json_obj, url_ls):
    new_gs = mk_new_gs(project, gs_url)
    json_obj[field] = new_gs
    if gs_url != new_gs:
        url_ls.add((gs_url, new_gs))


def update_json(project, jsn, json_out):
    """Return set of gcs urls."""
    urls = set()
    with open(jsn) as f:
        j = json.load(f)
        for field in j:
            val = j[field]
            if isinstance(val, str):
                if val[:5].startswith("gs://"):
                    udate_url(field, project, val, j, urls)
            elif isinstance(val, dict):
                for field2 in j[field]:
                    val2 = j[field][field2] 
                    if isinstance(val2, str):
                        if val2[:5].startswith("gs://"):
                            print('debug1', j[field][field2])
                            udate_url(field2, project, val2, j[field], urls)
                            print('debug2', j[field][field2])
                    elif isinstance(val2, list):
                        for idx, item in enumerate(val2):
                            if item[:5].startswith("gs://"):
                                new_gs = mk_new_gs(project, item)
                                j[field][field2][idx] = new_gs
                                if item != new_gs:
                                    urls.add((item, new_gs))
                    elif isinstance(val2, dict):
                        for field3 in j[field][field2]:
                            val3 = j[field][field2][field3] 
                            if isinstance(val3, str):
                                if val3[:5].startswith("gs://"):
                                    udate_url(field3, project, val3, j[field][field2], urls)

    with open(json_out, "w") as fout:
        json.dump(j, fout)

    return urls


def mk_auth_cmd(sa):
    cmd = f"gcloud auth activate-service-account --key-file={sa}"
    return cmd


def cp_data(delete, project, url, auth):
    """
    """
    src, dest = url
    src_set = set()
    local = strip_gs(src)
    have_file = subprocess.run(
        [f'{auth}; gsutil -q stat "{dest}" || echo "no"'],
        shell=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")
    print(have_file, dest)
    if "no\n" == have_file:
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
