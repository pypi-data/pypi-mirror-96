# Basic binary classification supervised auto-ml library

This lib is intended to automate supervised binary classification

Usage is as simple as

```python
from automl_pn.binary_classifier import BinaryClassifier

cls = BinaryClassifier()
cls.fit(X_train, y_train)
pred = cls.predict(X_test)
```
