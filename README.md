# migrate-wdl
 
Take [broad wdl](https://github.com/gatk-workflows) and make usable in VPC. For wdl, add noAddress to runtime, mv images to quay, and update docker paths. For json, mv gcs data inside project, and update json. This requires a GCP service account to mv the gcs data.

### Running

```
# mk service account json
gcloud iam service-accounts keys create sa-upload.json --iam-account you@project.iam.gserviceaccount.com
# enter image
start-docker.sh
# test.sh has ex migrate-json usage
# migrate wdl
python ~/chop/migrate-wdl/migrate-wdl.py arcus-jpe-pipe-stage-4f4279cc JointGenotypingTasks.wdl new.wdl
```
