"""Replace public gcr image url w/ project gcr.
   Add noAddress to runtimes.
"""
import argparse
import os

parser = argparse.ArgumentParser(description='Migrate broad wdl files to gcp vpc')
parser.add_argument('-d', '--delete', action='store_true', help='Delete local docker pull of image.')
parser.add_argument('project', type=str, help='GCP project')
parser.add_argument('wdl', type=str, help='Input wdl.')
parser.add_argument('wdlout', type=str, help='Output wdl.')

def add_noaddress(line, fout):
    print(line.strip(), file=fout)
    print('noAddress: true', file=fout)

def mk_new_image_line(project, line):
    """ex line
    String picard_docker = "us.gcr.io/broad-gotc-prod/gatk4-joint-genotyping:yf_fire_crosscheck_picard_with_nio_fast_fail_fast_sample_map"
    """
    broad_proj = line.split('/')[1]
    new_line = line.strip().replace(broad_proj, project)
    if 'us.gcr.io' in new_line:
        new_line = new_line.replace('us.gcr.io', 'gcr.io')
    return new_line

def update_gcr(project, line, fout):
    # gcr.io/arcus-jpe-pipe-stage-4f4279cc/gatk:4.1.0.0
    new_line = mk_new_image_line(project, line)
    print(new_line, file=fout)

def parse_image(line):
    image = line.strip().strip('"').split()[-1].lstrip('"')
    return image

def update_wdl(project, wdl, wdlout):
    """Return set of image urls.
       Add noAddress and update gcr paths."""
    images = set()
    with open(wdl) as f, open(wdlout, 'w') as fout:
        for line in f:
            if line.strip().lstrip() == 'runtime {':
                add_noaddress(line, fout)
            elif 'gcr' in line:
                update_gcr(project, line, fout)
                image = parse_image(line)
                images.add(image)
            else:
                print(line.strip(), file=fout)
    return images

def push_image(delete_image, project, image):
    """
    docker pull us.gcr.io/broad-gotc-prod/gnarly_genotyper:fixNegativeRefCount; docker tag us.gcr.io/broad-gotc-prod/gnarly_genotyper:fixNegativeRefCount gcr.io/arcus-jpe-pipe-stage-4f4279cc/gnarly_genotyper:fixNegativeRefCount; docker push gcr.io/arcus-jpe-pipe-stage-4f4279cc/gnarly_genotyper:fixNegativeRefCount;
    """
    new_image = mk_new_image_line(project, image)
    cmd = f'docker pull {image}; docker tag {image} {new_image}; docker push {new_image}'
    if delete_image:
        cmd += f"docker rmi $(docker images --format '{{{{.Repository}}}}:{{{{.Tag}}}}' | grep '{image}'); docker rmi $(docker images --format '{{{{.Repository}}}}:{{{{.Tag}}}}' | grep '{new_image}')"
    os.system(cmd)

def migrate(delete_image, project, wdl, wdlout):
    images = update_wdl(project, wdl, wdlout)
    for image in images:
        push_image(delete_image, project, image)

def main(args=None):
    args = parser.parse_args(args=args)
    migrate(args.delete, args.project, args.wdl, args.wdlout)

if __name__ == "__main__":
    main()
