# cryptoforecast.io scraper

## Introduction

CryptoForecast.io scraper

Allows simple interface for automating downloading of data from https://www.cryptoforecast.io API.

## Table of contens

- [Installation](#installation)

- [API](#api)

  - [API Methods](#api-methods)

- [Credits](#credits)

## Installation

    pip install cryptoforecast_io_scraper

## Requirements

- Requires Requests

## API

### Get data from CryptoForecast

    from cryptoforecast_io_scraper.request import DataReq

    data_req = DataReq()

    print(data_req._get_data())

## API Methods

The following API methods are available:

- [Get data]: returns recent data

# Credits

- https://github.com/Drakkar-Software/pytrends
