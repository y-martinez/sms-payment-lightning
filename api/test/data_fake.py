data_of_webhook = {
    "block_hash": "0000000000000012db3eb9d21199f801e43be828817d6f6d60681c7979c5bbb3",
    "block_height": 1902015,
    "block_index": 4,
    "hash": "d1b6fb7ba9e638c1c243c14a2adde0f34f04ab9b2e0e6c0a94b0ec43a4a3a5ca",
    "addresses": [
        "2NGAaoZc59jss3WkjfarS8oM5MLvcpkxC9e",
        "tb1qwatu5c240fnuk5yryqx3cxmzmaj7c7eydzwred",
        "tb1qxmjhkm8lnyp52yr4d02k8ta0928h4650agntfv",
    ],
    "total": 5820758368,
    "fees": 16691,
    "size": 136,
    "preference": "low",
    "relayed_by": "46.101.165.206:18333",
    "confirmed": "2021-01-02T20:14:21Z",
    "received": "2021-01-02T20:09:04.164Z",
    "ver": 2,
    "lock_time": 1902014,
    "double_spend": False,
    "vin_sz": 1,
    "vout_sz": 2,
    "confirmations": 1,
    "inputs": [
        {
            "prev_hash": "ea928b5090058fd2d2a55a22c5fc068ae8a56c5c39738192647675aaa4bace62",
            "output_index": 0,
            "script": "1600146647bd94f69ab58dde2333276c80dd9cdcac7693",
            "output_value": 5820775059,
            "sequence": 4294967294,
            "addresses": ["2NGAaoZc59jss3WkjfarS8oM5MLvcpkxC9e"],
            "script_type": "pay-to-script-hash",
            "age": 1902014,
        }
    ],
    "outputs": [
        {
            "value": 1601786,
            "script": "00147757ca61557a67cb5083200d1c1b62df65ec7b24",
            "addresses": [],
            "script_type": "pay-to-witness-pubkey-hash",
        },
        {
            "value": 5819156582,
            "script": "001436e57b6cff99034510756bd563afaf2a8f7aea8f",
            "addresses": ["tb1qwatu5c240fnuk5yryqx3cxmzmaj7c7eydzwred"],
            "script_type": "pay-to-witness-pubkey-hash",
        },
    ],
}

data_list_webhooks = [
    {
        "address": "15qx9ug952GWGTNn7Uiv6vode4RcGrRemh",
        "callback_errors": 0,
        "confirmations": 6,
        "event": "confirmed-tx",
        "filter": "event=confirmed-tx&addr=15qx9ug952GWGTNn7Uiv6vode4RcGrRemh",
        "id": "bcaf7c39-9a7f-4e8b-8ba4-23b3c1806039",
        "token": "TOKEN",
        "url": "https://example.com/callbacks/new-tx",
    }
]

data_rate = {
    "time": {
        "updated": "Dec 31, 2020 21:00:00 UTC",
        "updatedISO": "2020-12-31T21:00:00+00:00",
        "updateduk": "Dec 31, 2020 at 21:00 GMT",
    },
    "disclaimer": "This data was produced from the CoinDesk Bitcoin Price\
        Index (USD). Non-USD currency data converted using hourly conversion\
            rate from openexchangerates.org",
    "bpi": {
        "USD": {
            "code": "USD",
            "rate": "21,306.29",
            "description": "United States Dollar",
            "rate_float": 21306.29,
        }
    },
}

data_balance_wallet_errors = {
    "error": "Unable to connect www.apibtc.com",
    "status_code": 500,
}

data_wallet_errors = [
    {
        "error": "Unable to connect www.example.com:9876",
        "status_code": 500,
    },
    {"error": "Not found", "status_code": 404},
]


data_info_payreq = {
    "destination": "030f1784fafe1b5b143e4e4545e6c2f612943c60e6a5b770b35e324c60b6ae9516",
    "payment_hash": "024f6669fb36ce15536e0d2a8249cfa3a94778c6469ab07c212437d43b755684",
    "num_satoshis": "1000",
    "timestamp": "1610325941",
    "expiry": "86400",
    "cltv_expiry": "40",
    "payment_addr": "QxUaTHrldiDJG/F3kP8pOa8iH4WXaX2vwXIRSZO7eBg=",
    "num_msat": "1000000",
    "features": {
        "9": {"name": "tlv-onion", "is_known": True},
        "14": {"name": "payment-addr", "is_required": True, "is_known": True},
        "17": {"name": "multi-path-payments", "is_known": True},
    },
}

data_invoice_paid = {
    "payment_preimage": "9X7IYxn6UFWERsGvUCAJJLXklfoaHmtcPJIpFGstT+k=",
    "payment_route": {
        "total_time_lock": 1903449,
        "total_fees": "1",
        "total_amt": "1001",
        "hops": [
            {
                "chan_id": "2092769750382477313",
                "chan_capacity": "2250000",
                "amt_to_forward": "1000",
                "fee": "1",
                "expiry": 1903409,
                "amt_to_forward_msat": "1000000",
                "fee_msat": "1005",
                "pub_key": "038863cf8ab91046230f561cd5b386cbff8309fa02e3f0c3ed161a3aeb64a643b9",
                "tlv_payload": True,
            },
            {
                "chan_id": "2011864386272559104",
                "chan_capacity": "20000000",
                "amt_to_forward": "1000",
                "expiry": 1903409,
                "amt_to_forward_msat": "1000000",
                "pub_key": "030f1784fafe1b5b143e4e4545e6c2f612943c60e6a5b770b35e324c60b6ae9516",
                "tlv_payload": True,
                "mpp_record": {
                    "payment_addr": "3pyqbkuNrAldKCtW5ghJKealtdSyXm5P/OQ6LAw1Tvk=",
                    "total_amt_msat": "1000000",
                },
            },
        ],
        "total_fees_msat": "1005",
        "total_amt_msat": "1001005",
    },
    "payment_hash": "d3HOkjDiuYERcCMdpds+2bG8jQEn8u4HqdPyiLVHH5w=",
}


data_invoice_not_paid = {
    "error_invoice_payreq_malformatted": {
        "error": "string not all lowercase or all uppercase",
        "message": "string not all lowercase or all uppercase",
        "code": 2,
    },
    "error_invoice_checksum": {
        "error": "checksum failed. Expected 40jxz5, got c3de33.",
        "code": 2,
        "message": "checksum failed. Expected 40jxz5, got c3de33.",
        "details": [],
    },
    "error_invoice_expired": {
        "error": "invoice expired. Valid until 2020-12-18 06:15:24 +0000 UTC",
        "code": 2,
        "message": "invoice expired. Valid until 2020-12-18 06:15:24 +0000 UTC",
        "details": [],
    },
    "error_invoice_paid": {
        "payment_error": "invoice is already paid",
        "payment_preimage": None,
        "payment_route": None,
        "payment_hash": "K+UyZ2hP7ekVb5w4q3IxyZD2EyujsJ9QZemK009OLzk=",
    },
    "error_invoice_incorrect": {
        "payment_error": "IncorrectOrUnknownPaymentDetails(amt=50000000 mSAT, height=1903394)@3",
        "payment_hash": "dFZv1l9akc9gWgJi6wKwD5r7yCLyH9fNAUDMJNpJCI8=",
    },
    "error_invoice_in_transition": {
        "payment_error": "payment is in transition",
        "payment_hash": "dFZv1l9akc9gWgJi6wKwD5r7yCLyH9fNAUDMJNpJCI8=",
    },
    "error_invoice_no_route": {
        "payment_error": "unable to find a path to destination",
        "payment_hash": "FKFqrav204kRKrjUqzLfNJrMUL1zh+7rAFkkOzizsBQ=",
    },
}
