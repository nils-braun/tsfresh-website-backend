# tsfresh-website backend

This repo contains everything needed for the tsfresh website backend.

To start developing, run

	conda create -n tsfresh-website
	conda activate tsfresh-website
	conda install --file requirements.txt -c conda-forge

And for starting the server

	uvicorn backend.main:app --reload

## Deployment

To deploy to the GCP cloud:

	gcloud builds submit --tag gcr.io/tsfresh-website/backend
	gcloud run deploy --image gcr.io/tsfresh-website/backend --platform managed 

