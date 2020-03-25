# migrate-wdl
 
Take [broad wdl](https://github.com/gatk-workflows) and make usable in VPC. For wdl, add noAddress to runtime, mv images to quay, and update docker paths. For json, mv gcs data inside project, and update json. This requires a GCP service account to mv the gcs data.

### Running

```
# mk service account json
gcloud auth login
gcloud config set project arcus-jpe-pipe-stage-4f4279cc
gcloud iam service-accounts keys create sa-upload.json --iam-account you@project.iam.gserviceaccount.com

# clone broad repo
git clone https://github.com/gatk-workflows/broad-prod-wgs-germline-snps-indels

# enter image
sh src/scripts/start-docker.sh

# sh src/scripts/json-ex.sh has ex migrate-json usage or 
# migrate json/data
python src/scripts/migrate-json.py arcus-jpe-pipe-stage-storage sa-upload.json /mnt/isilon/dbhi_bfx/perry/projects/asif/gatk4-germline-snps-indels/JointGenotyping.hg19.wgs.inputs.json JointGenotyping.hg19.wgs.inputs.chop.json

# migrate wdl
python ~/chop/migrate-wdl/migrate-wdl.py arcus-jpe-pipe-stage-4f4279cc JointGenotypingTasks.wdl new.wdl
```

### Building image
```
#docker build -t quay.research.chop.edu/evansj/migrate-wdl:dev -f Dockerfile .
sh build.sh
```
