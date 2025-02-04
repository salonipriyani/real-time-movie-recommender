# Evaluation

## Online Eval

### Environment
To run the code, you will need to have Python 3.6 or higher and the following packages installed:

- numpy
- kafka-python
- scikit-learn

You can install these packages using pip:

```bash
pip install numpy kafka-python scikit-learn
```

### Usage

To monitor the online metric in evaluation, run the `online_personalization.py` script in `online/`:

```bash
python online_personalization.py
```

Logs will be automatically recorded every 1000 recommendation requests get handled. Find logs at `logs/`


## Offline Eval

### Environment
To run the code, you will need to have Python 3.6 or higher and the following packages installed:

- numpy
- pandas
- surprise

You can install these packages using pip:

```bash
pip install numpy pandas surprise
```

### Usage

To run the offline evaluation, run the `svd_train.py` script in `offline/`:

```bash
python svd_train.py
```

Test RMSE value and the hyperparameters that are used for the final model will be printed on terminal.
Trained svd model will be saved as `SVD_model_2.0.dump`.
