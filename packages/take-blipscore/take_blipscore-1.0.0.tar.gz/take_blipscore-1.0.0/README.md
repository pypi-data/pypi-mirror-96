# Take Blip Score

This project proposes to _offer a rate named Blip Score and represents a general metric for bot_.

The proposal uses the [satisfaction rate](https://pypi.org/project/take-satisfaction/) and [resolution rate](https://pypi.org/project/take-resolution/) as input to create the BLiP Score rate.
The value of the rate is in interval (0, 1) and it is better as near to 1 (one)

# Installation
Use [pip] to install:

```shell script
pip install take-blipscore
```

# Usage

```python
import take_blipscore as tbs
result = tbs.run(satisfaction_rate=0.67,
                 resolution_rate=0.82)

print(result["rate"])
```

Which will result in `0.7665976833542061`.

# Author
Take Data&Analytics Research - squad XD.
