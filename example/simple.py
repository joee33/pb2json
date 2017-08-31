#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
sys.path.append('../src')
from pb_parser import FileFsm
from pb_parser import Message
import json


def pb_to_json():
    print('\n---translate pb to json---')
    file_fms = FileFsm('test.proto')
    file_fms.parse()
    json_msg = file_fms.message_to_json('Test1')
    print(json_msg)

def json_to_pb():
    print('\n---translate json to pb---')
    test_string = json.dumps(
        {
        'message_name': 'Test3',
        'message_comment': '测试消息3',
        'field_list': [
            {
                'field_name': 'first_field',
                'field_type': 'string',
                'field_property': 'required',
                'field_sequence': 1,
                'field_comment': '第一个字段',
                'field_value': 'hello,world'
             },
            {
                'field_name': 'second_field',
                'field_type': 'int32',
                'field_property': 'optional',
                'field_sequence': 2,
                'field_comment': '第二个字段',
                'field_value': 10086
            }
        ]},
        ensure_ascii = False
    )
    msg = Message(json_string=test_string)
    pb_msg = msg.serialize()
    print('[protobuf message]:\n', pb_msg)
    print('[protobuf message length]: ', pb_msg.ByteSize())
    print('[protobuf message serialize binary data]: ', pb_msg.SerializeToString())

test_function = {
    pb_to_json,
    json_to_pb
}

if __name__ == '__main__':
    for f in test_function:
        f()

