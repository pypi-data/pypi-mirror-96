# Take Satisfaction
This package proposes to offer a rate that represents the customer satisfaction research from the bot.

The proposal converts the Customer Satifaction Survey (CSS) to a normalized rate between 0 to 1. The normalized value alow the comparasion of CSS from differents bot that have differents scales types and ranges.

# Installation
Use [pip](https://pypi.org/project/take-satisfaction/) to install:

```shell script
pip install take-satisfaction
```

# Usage

## Using a **numeric scale** Consumer Satisfaction Survey:

```python
import pandas as pd
import take_satisfaction as ts

pdf = pd.DataFrame({"Action": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    "amount": [0, 1, 2, 0, 0, 10, 0, 35, 200, 360, 3330]})

result = ts.run(dataframe=pdf,
                scale_column="Action",
                amount_column="amount")

print(result["rate"])
```

Which will result in `0.9761300152361605`.

## Using a **textual scale** Consumer Satisfaction Survey:

```python
import pandas as pd
import take_satisfaction as ts

pdf = pd.DataFrame(
    {"Action": ["Péssimo", "Ruim", "OK", "Ótimo", "Excelente"],
    "amount": [0, 1, 35, 350, 3330]})
css_column = "Action"
amount = "amount"

result = ts.run(dataframe=pdf,
                scale_column=css_column,
                amount_column=amount)

print(result["rate"])
```

Which will result in `0.9715419806243273`.


# Author
Take Data&Analytics Research - squad XD.
