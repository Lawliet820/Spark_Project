import json


def report_decode(hbase_string_data):
    decoded_data = json.loads(
        json.loads(
            hbase_string_data
        )['value'].encode().decode('unicode-escape').encode("raw_unicode_escape").decode()
    )
    return decoded_data