# RandomPhone

![Build Status](https://api.travis-ci.com/rfranks-securenet/RandomPhone.svg?branch=main)

## Overview

RandomPhone is a package for generating random phone numbers.
It currently supports UK phone numbers pulled from the
[Ofcom telephone numbers for use in TV and radio drama](https://www.ofcom.org.uk/phones-telecoms-and-internet/information-for-industry/numbering/numbers-for-drama)

## Install

Easy way:

`pip install RandomPhone`

## Usage

RandomPhone can create landlines, mobiles, freephone, premium, and local rate numbers.

```
from random_phone import RandomUkPhone

rukp = RandomUkPhone()

rukp.random_landline()
rukp.random_mobile()
rukp.random_freephone()
rukp.random_premium()
rukp.random_ukwide()

```

An optional parameter `international` can be passed to place the international dialing prefix on the front (+44)