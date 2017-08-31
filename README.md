# pb2json
a python script used to translate Protobuf to Son

# patch说明
目前处于开发状态，仅支持字段为简单类型的消息，如bool，string等；暂不支持message、enum。

# 使用说明
## protobuf消息转为json字符串
proto_file.proto文件内容如下：
`
package test.pkg;

//测试消息
message Test{
    required bool   first_field     = 1; //第一个字段
    optional double second_filed    = 2; //第二个地段
    optional float  third_field     = 3; //第三个字段
    optional int32  forth_field     = 4; //第四个字段
    optional uint32 fifth_field     = 5; //第五个字段
}

`
新建一个FileFsm实例：
`file_fsm = FileFsm('proto_file.proto')  
 file_fsm.parse()
 result = file_fsm.message_to_json('Test')
 print(result)`  
 结果打印：
 `"message_name": "Test", "message_comment": "测试消息", "message_fields": [{"field_name": "first_field", "field_type": "bool", "field_property": "required", "field_sequence": 1, "field_default": "", "field_comment": "第一个字段", "field_value": null}, {"field_name": "second_filed", "field_type": "double", "field_property": "optional", "field_sequence": 2, "field_default": "", "field_comment": "第二个地段", "field_value": null}, {"field_name": "third_field", "field_type": "float", "field_property": "optional", "field_sequence": 3, "field_default": "", "field_comment": "第三个字段", "field_value": null}, {"field_name": "forth_field", "field_type": "int32", "field_property": "optional", "field_sequence": 4, "field_default": "", "field_comment": "第四个字段", "field_value": null}, {"field_name": "fifth_field", "field_type": "uint32", "field_property": "optional", "field_sequence": 5, "field_default": "", "field_comment": "第五个字段", "field_value": null}]}`
 
 ## json字符串转为PB消息
 json字符串如下：
 `
 test_string = '''{"message_name": "Test3", "message_comment": "测试消息3", "field_list": [{"field_name": "first_field", "field_type": "string", "field_property": "required", "field_sequence": 1, "field_comment": "第一个字段", "field_value": "hello,world"}, {"field_name": "second_field", "field_type": "int32", "field_property": "optional", "field_sequence": 2, "field_comment": "第二个字段", "field_value": 10086}]}'''
 `
以json字符串新建一个Message实例
`msg = Message(json_string=test_string)
pb_msg = msg.serialize()
print(pb_msg)
print(pb_msg.ByteSize())
print(pb_msg.pb_msg.SerializeToString())
`
打印结果如下：
`
first_field: "hello,world"
second_field: 10086
16
b'\n\x0bhello,world\x10\xe6N'
`
