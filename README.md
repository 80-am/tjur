# tjur
[![Build Status](https://travis-ci.org/80-am/tjur.svg?branch=master)](https://travis-ci.org/80-am/tjur)
[![Python Version](https://img.shields.io/badge/python-%3E%3D%203.6-blue)](https://www.python.org/)
[![License: GPL-3.0](https://img.shields.io/github/license/80-am/kreepr)](https://opensource.org/licenses/GPL-3.0)

Binance momentum bot

## Getting Started
Copy [tjur/config.sample](tjur/config.sample) into tjur/config.yaml and fill in your API secrets.

```yaml
# Live trading or paper trading
live_trading: False

# Whether to use Terminal UI
ui: True

binance:
  api_key: 'YOUR_API_KEY'
  api_secret: 'YOUR_API_SECRET'

log:
  level: 'INFO'

symbols:
  one: 'ETH'
  two: 'USDT'

position_percentage: 4
```

Install dependencies with pip.
```bash
pip install -r requirements.txt
```
