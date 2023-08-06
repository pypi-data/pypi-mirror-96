# nteu_translation_engine_fake


## Usage
```python
from nteu_translation_engine_fake.nteu_translation_engine_fake import NTEUTranslationEngineFake


NTEUTranslationEngineFake.run(
    host='0.0.0.0',
    port=5000
)
```

## Upload package to Pypi

### Install dependencies
```BASH
pip install wheel
pip install twine
```

### Create package
```
python setup.py sdist bdist_wheel
```

## Upload package
```
python -m twine upload dist/*
```