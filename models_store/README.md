# Model Store

This directory is intended to store the serialized machine learning model files. 

## Adding Models

To add a new model, simply place the `.pkl` file in this directory. The application is configured to look for `autorest_model.pkl` by default. If you use a different filename, be sure to update the `MODEL_PATH` environment variable.