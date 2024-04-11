### Setting up the code
#### Clone repository
Start by cloning the repository:
```bash
 git clone https://github.com/learnqc/code_plus
```


#### Code Setup

1. Next, **create a virtual environment** where you can run the code.
```bash
python -m venv bqs-env
```

2. **Activate the new environment.**
```bash
source bqs-env/bin/activate
```

3. **Install the dependencies** for the repository in the virtual environment.
```bash
pip install -r requirements.txt
```

## Run the single-qubit UI application

```bash
cd src 
 python -m panel serve experiments/single_qubit.py --show
```

![Single Qubit App](./assets/images/single_qubit_app.png)
