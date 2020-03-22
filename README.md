# Sagemill: Run SageMaker jobs like papermill
Sagemill lets you to execute your notebook as [SageMaker](https://aws.amazon.com/sagemaker/) jobs in the similar way to [papermill](https://papermill.readthedocs.io/en/latest/)

## Overall features
- parameterize notebooks
- execute notebooks as SageMaker Trainig/Processing Job

## Installatioin
```
$ pip install sagemill
```

## Prerequsites
- Python>=3.5

### Required IAM policy
- ecr
  - create-repository
  - get-authorization-token
- sts
  - get-caller-identity
- permission to run Sagemaker jobs
  - write to cloudwatch logs
  - access to some S3 buckets
  - start training/proceessing jobs
  - etc.

## Example notebooks
These notebook are assumed to be `conda_python3` in SageMaker Notebook instance<br>
If you run it on different environments, install `conda` and run `pip install sagemaker`<br>
(You cannot see tags in Github. Download and run the notebooks to see tags)

- [Training job with tensorflow](./example/train_tf.ipynb)
- [Training job with your own docker image](./example/train_custom.ipynb)
- [Processing job with SKLearnProcessor](./example/process_sklearn.ipynb)
- [Processing job with your own docker image](./example/process_custom.ipynb)
