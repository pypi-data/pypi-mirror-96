# bitcoinde

Python wrapper for the bitcoin.de trading API. Currently, only v4 is supported.

## Installation

    pip install bitcoinde

## Tutorial

    from bitcoinde import TradingAPI

    client = TradingAPI(API_KEY, API_SECRET)
    client.show_orderbook('btceur', 'buy', seat_of_bank=['DE', 'IT'])
