#! /usr/bin/env python3
# coding=utf-8

import sys
import json
from enum import Enum, unique
from my_exception import ParamError, FormatError, UndefineError
from google.protobuf.descriptor_pb2 import FieldDescriptorProto
from google.protobuf.descriptor_pb2 import FileDescriptorProto
from google.protobuf import message_factory


# Field Type合法值集合
FieldTypes = {
    'bool',
    'double',
    'float',
    'int32',
    'uint32',
    'int64',
    'uint64',
    'sint32',
    'sint64',
    'fixed32',
    'fixed64',
    'sfixed32',
    'sfixed64',
    'string',
    'bytes',
    'enum',
    'message'
}

# Field Property合法值集合
FieldProperty = {
    'required',
    'optional',
    'repeated'
}

# 定义消息行的首字符串集合
LineStatusMessage = {
    'message',
    'required',
    'optional',
    'repeated',
    '{',
    '}'
}

FieldType2PbType = {
    'bool'      : FieldDescriptorProto.TYPE_BOOL,
    'double'    : FieldDescriptorProto.TYPE_DOUBLE,
    'float'     : FieldDescriptorProto.TYPE_FLOAT,
    'int32'     : FieldDescriptorProto.TYPE_INT32,
    'uint32'    : FieldDescriptorProto.TYPE_UINT32,
    'int64'     : FieldDescriptorProto.TYPE_INT64,
    'uint64'    : FieldDescriptorProto.TYPE_UINT64,
    'sint32'    : FieldDescriptorProto.TYPE_SINT32,
    'sint64'    : FieldDescriptorProto.TYPE_SINT64,
    'fixed32'   : FieldDescriptorProto.TYPE_FIXED32,
    'fixed64'   : FieldDescriptorProto.TYPE_FIXED64,
    'sfixed32'  : FieldDescriptorProto.TYPE_SFIXED32,
    'sfixed64'  : FieldDescriptorProto.TYPE_SFIXED64,
    'string'    : FieldDescriptorProto.TYPE_STRING,
    'bytes'     : FieldDescriptorProto.TYPE_BYTES,
    'enum'      : FieldDescriptorProto.TYPE_ENUM,
    'message'   : FieldDescriptorProto.TYPE_MESSAGE
}

FieldProperty2PbProperty = {
    'required': FieldDescriptorProto.LABEL_REQUIRED,
    'optional': FieldDescriptorProto.LABEL_OPTIONAL,
    'repeated': FieldDescriptorProto.LABEL_REPEATED
}

# 定义行状态枚举
@unique
class LineStatus(Enum):
    line_status_undefine = 0
    line_status_import = 1
    line_status_package = 2
    line_status_message = 3
    line_status_comment = 4
    line_status_empty = 5
    line_status_others = 6
    line_status_eof = 7


class Field:

    def __init__(self, field_name=None, field_type=None, field_property=None, field_sequence=None, field_default=None, field_comment=None, field_value=None, json_string=None):
        """
        :param field_name       字段名，字符串
        :param field_type       见FieldTypes定义
        :param field_property   见FieldProperty定义
        :param field_sequence   字段序列号，整形
        :param field_default    默认值
        :param field_comment    字段说明
        :param json_string      描述字段的json字符串，优先使用json字符串构造字段
        :return
        """
        # 若json_string不为空，直接使用json字符串进行构造
        if json_string is not None:
            self.__parse_from_json(json_string)
            return

        # 检查参数
        if field_name.strip() == '':
            raise ParamError('Invalid Parameter field_name:[%s]' % str(field_name))
        if field_type not in FieldTypes:
            raise ParamError('Invalid Parameter field_type:[%s]' % str(field_type))
        if field_property not in FieldProperty:
            raise ParamError('Invalid Parameter field_property[%s]' % str(field_property))
        if not isinstance(field_sequence, int):
            raise ParamError('Invalid Parameter field_sequence[%s]' % str(field_sequence))
        self.name = field_name
        self.type = field_type
        self.property = field_property
        self.sequence = field_sequence
        self.default = field_default
        self.comment = field_comment
        self.value = field_value

    def __str__(self):
        """
        将内容以字符串形式返回
        """
        return  '  field_name: %s\n  field_type: %s\n  field_property: %s\n  field_sequence: %d\n  filed_default: %s\n  field_comment: %s\n  field_value: %s\n' % (
            self.name, self.type, self.property, self.sequence, self.default, self.comment, str(self.value))

    def __parse_from_json(self, json_string):
        """
        根据json字符串构造
        :param json_string:
        """
        # 检查消息必要字段
        l_dict = json.loads(json_string)
        if 'field_name' not in l_dict or \
            'field_type' not in l_dict or l_dict['field_type'] not in FieldTypes or \
            'field_property' not in l_dict  or l_dict['field_property'] not in FieldProperty or \
            'field_sequence' not in l_dict or not isinstance(l_dict['field_sequence'], int):
            raise FormatError('Invlaid Json string for serialize to Field')

        self.name = l_dict['field_name']
        self.type = l_dict['field_type']
        self.property = l_dict['field_property']
        self.sequence = l_dict['field_sequence']
        self.default = None if ('field_default' not in l_dict) else l_dict['field_default']
        self.comment = '' if ('field_comment' not in l_dict) else l_dict['field_comment']
        self.value = None if ('field_value' not in l_dict) else l_dict['field_value']

    def to_json(self):
        """
        将内容以格式化json字符串
        """
        l_dict = {'field_name': self.name,
                  'field_type': self.type,
                  'field_property': self.property,
                  'field_sequence': self.sequence,
                  'field_default': self.default,
                  'field_comment': self.comment,
                  'field_value': self.value}
        return json.dumps(l_dict, ensure_ascii=False)


class Message:
    """
    pb消息
    """
    # 动态构造PB消息的工厂实例
    _factory = None
    _file_proto = None
    #_file_proto = FileDescriptorProto(name='dummy.proto', package='pkg')

    def __init__(self, message_name=None, message_pkg=None, message_comment=None, message_fields=None, json_string=None):
        """
        :param message_name     消息名
        :param message_fields   消息的字段列表
        :param json_string      描述消息的json字符串，优先使用json字符串构造消息
        """
        # 若json_string不为空，直接使用json字符串进行构造
        if json_string is not None:
            self.__parse_from_json(json_string)
            return

        # 检查参数
        if message_name.strip() == '':
            raise ParamError('Invalid Parameter message_name:[%s]' % str(message_name))
        if not isinstance(message_fields, list):
            raise ParamError('Invalid Parameter message_fields:[%s]' % str(message_fields))
        self.__name = message_name
        self.__fields = [] if (message_fields == None) else message_fields
        self.__pkg = message_pkg
        self.__comment = message_comment


    def __str__(self):
        """
        以字符串形式返回消息内容
        :return:
        """
        string = 'message_name: %s\n' % self.__name
        string += ('message_comment: %s\nmessage_pkg: %s\nfield_list:\n' % (self.__comment, self.__pkg))
        for field in self.__fields:
            string += (str(field) + '\n')
        return string

    def __parse_from_json(self, json_string):
        """
        解析json字符串，构造消息
        """
        # 若json_string不为空，直接使用json字符串进行构造
        l_dict = json.loads(json_string)
        if 'message_name' not in l_dict or \
            'field_list' not in l_dict or \
            len(l_dict['field_list']) == 0:
            raise format('Invlaid Json string for serialize to Messafe')
        self.__name = l_dict['message_name']
        self.__comment = None if ('message_comment' not in l_dict) else l_dict['message_comment']
        self.__pkg = None if ('message_pkg' not in l_dict) else l_dict['message_pkg']
        self.__fields = []
        for field_dict in l_dict['field_list']:
            self.__fields.append(Field(json_string=json.dumps(field_dict, ensure_ascii=False)))

    def __create_dynamic_message(self):
        try:
            # 找到直接返回
            self._factory.pool.FindMessageTypeByName('%s.%s' % (str(self.__pkg), str(self.__name)))
            return
        except KeyError:
            pass
        # 未找到则创建
        message_proto = self._file_proto.message_type.add(name=self.__name)
        for field in self.__fields:
            if field.type == 'enum':
                print('not support yet')
            elif field.type == 'message':
                print('not support yet')
            else:
                message_proto.field.add(name=field.name,
                                        type=FieldType2PbType[field.type],
                                        number=field.sequence,
                                        label=FieldProperty2PbProperty[field.property])
        # 将构造好的虚拟PB文件添加到工厂实例中
        self._factory.pool.Add(self._file_proto)

    def __create_message_object(self):
        try:
            descriptor = self._factory.pool.FindMessageTypeByName('%s.%s' % (str(self.__pkg), str(self.__name)))
            message = self._factory.GetPrototype(descriptor)
            msg = message()
            for field in self.__fields:
                if field.type == 'message':

                    print('not support')
                elif field.type == 'bool':
                    fd = descriptor.fields_by_name[field.name]
                    msg._fields[fd] = (field.value == 'true')
                else:
                    fd = descriptor.fields_by_name[field.name]
                    msg._fields[fd] = field.value
            # 设置消息改动标记，在计算消息的长度是才会正确计算
            msg._Modified()
            return msg
        except KeyError:
            print('not found')
            pass

    def to_json(self):
        """
        将消息转换为json格式字符串
        :return:
        """
        l_dict = {
            'message_name': self.__name,
            'message_comment': self.__comment,
            'message_fields': []
        }
        for field in self.__fields:
            l_dict['message_fields'].append(json.loads(field.to_json()))
        return json.dumps(l_dict, ensure_ascii=False)

    def serialize(self):
        """
        将消息按照PB规则序列化为二进制数据
        :return:
        """
        self._factory = message_factory.MessageFactory()
        # dummy.proto为虚拟文件，若未明确指定pkg，则pkg默认为'None'; package参数不能为空，否则后面找消息类时会出错
        self._file_proto = FileDescriptorProto(name='dummy.proto', package=str(self.__pkg))
        # 创建动态消息
        self.__create_dynamic_message()
        # 创建消息对象
        return self.__create_message_object()

    def add_field(self, message_field):
        """
        增加消息字段
        :param message_field:
        :return:
        """
        if not isinstance(message_field, Field):
            raise ParamError('Invalid Parameter message_field')
        self.__fields.append(message_field)

    def add_comment(self, comment):
        """
        增加消息注释信息
        :param comment:
        :return:
        """
        if self.__comment == None:
            self.__comment = comment
        else:
            self.__comment += ('\n' + comment)

    def name(self):
        """
        返回消息名
        :return:
        """
        return self.__name


class LineFsm:
    """
    行解析状态机
    :param line: 行内容
    :param number: 行号
    """

    words = []
    line_number = 0

    def __init__(self, line, number, line_status=LineStatus.line_status_undefine):
        self.__line = line
        self.__line_status = line_status
        LineFsm.line_number = number

    def __str__(self):
        return self.__line

    def parse(self):
        """
        解析行
        :return:
        """
        # 对行做分割
        LineFsm.words = self.__line.split()
        # 空行不作处理
        if 0 == len(LineFsm.words):
            self.__line_status = LineStatus.line_status_empty
            return
        # 根据行第一个字符串判断行的性质
        if LineFsm.words[0] in LineStatusMessage:
            # 新消息头
            self.__line_status = LineStatus.line_status_message
        elif "import" == LineFsm.words[0]:
            self.__line_status = LineStatus.line_status_import
        elif "package" == LineFsm.words[0]:
            self.__line_status = LineStatus.line_status_package
        elif '//' == LineFsm.words[0][0:2]:
            self.__line_status = LineStatus.line_status_comment
        else:
            self.__line_status = LineStatus.line_status_others

    def parse_message_new(self):
        # 确定行为新消息声明行时，做进一步解析
        w = []
        for word in LineFsm.words:
            for i in word.split("{"):
                if "" != i:
                    w.append(i)
        self.words = w

    def parse_message_element(self):
        """
        确定行为消息字段是，做进一步解析
        解析后的字段列表为["optional", "bool", "name", "1", "comment"]
        :return:
        """
        w = []
        word_pos_s = 0
        word_pos_e = 0
        pure_line = self.__line.replace('\t', ' ')
        pure_line = pure_line.replace('=', ' ')
        pure_line = pure_line.replace(';', ' ')
        for ch in pure_line:
            if "/" == ch:
                w.append(pure_line[word_pos_s + 2:].strip('\n'))
                break
                # return
            elif ch.isalnum() or '_' == ch:
                word_pos_e += 1
            elif ' ' == ch:
                if word_pos_s == word_pos_e:
                    word_pos_s += 1
                    word_pos_e += 1
                    continue
                w.append(pure_line[word_pos_s:word_pos_e])
                word_pos_s = word_pos_e = word_pos_e + 1
        # 检查解析后的字符串列表
        if (len(w) != 4 and len(w) != 5) or \
            w[0] not in FieldProperty or \
            w[1] not in FieldTypes or \
            not w[3].isdigit():
            raise FormatError('invalid syntax. line:%d' % self.line_number + ', Message element format invalid')
        # 若无注释信息，需手动补齐空字符串
        if len(w) == 4:
            w.append("")
        # 保存结果
        LineFsm.words = w

    def line_status(self):
        """
        获取行状态
        :return:
        """
        return self.__line_status

    def line_content(self):
        """
        返回行原内容
        :return:
        """
        return self.__line


class FileFsm:
    """
    文件解析状态机
    """

    # 缓存遇到行内容
    line_cache = []
    # 正在处理中的消息
    message_cache = None

    def __init__(self, path):
        self.__path = path
        self.__pkg = ''
        self.__message = dict()
        self.__line_rotine = {
            LineStatus.line_status_undefine: self.__rt_undefine,
            LineStatus.line_status_import: self.__rt_import,
            LineStatus.line_status_package: self.__rt_package,
            LineStatus.line_status_message: self.__rt_message,
            LineStatus.line_status_comment: self.__rt_comment,
            LineStatus.line_status_empty: self.__rt_empty,
            LineStatus.line_status_others: self.__rt_other,
            LineStatus.line_status_eof: self.__rt_eof
        }

    def __str__(self):
        string = 'proto package: %s\n' % self.__pkg
        for k, v in self.__message.items():
            string += (str(v) + '\n')
        return string

    def message_to_json(self, message_name):
        """
        获取指定消息的json描述
        :return:
        """
        return self.__message[message_name].to_json()

    def parse(self):
        """
        解析文件
        :return:
        """
        # 格式化文件内容
        self.__format()
        # 按行解析文件
        line_number = 1
        #for line_string in open(self.__path):
        for line_string in self.__format().split('\n'):
            line = LineFsm(line_string, line_number)
            line.parse()
            # 根据行属性分别处理
            self.__line_rotine[line.line_status()](line)
            line_number += 1

    def __format(self):
        """
        对文件内容做格式化处理
        :return:
        """
        file_data = ''
        for line_string in open(self.__path):
            line_cur_s = line_cur_e = 0
            new_line_flag = False
            comment_flag = False
            for ch in line_string:
                # 若被标记为注释，则不判断内容
                if True == comment_flag and '\n' != ch:
                    line_cur_e += 1
                    continue

                if ch.isalnum() or ch in {'_', '='}:
                    # 新行标志为真，若不是comment，且下一个为字符，需换行
                    if new_line_flag == True:
                        word = line_string[line_cur_s:line_cur_e]
                        file_data += (word + '\n')
                        # 重新开始计算位置
                        line_cur_s = line_cur_e
                        line_cur_e += 1
                        new_line_flag = False
                        comment_flag = False
                    else:
                        line_cur_e += 1

                elif ch in  {' ', '\t'}:
                    if new_line_flag == True:
                        line_cur_e += 1
                    elif line_cur_e == line_cur_s:
                        line_cur_e += 1
                        line_cur_s += 1
                    else:
                        word = line_string[line_cur_s:line_cur_e]
                        file_data += (word + ' ')
                        line_cur_s = line_cur_e = (line_cur_e + 1)

                elif ch == '{':
                    word = line_string[line_cur_s:line_cur_e]
                    file_data += (word + '\n')
                    file_data += (ch + '\n')
                    line_cur_s = line_cur_e = (line_cur_e + 1)

                elif ch == ';':
                    new_line_flag = True
                    line_cur_e += 1

                elif ch == '\n':
                    word = line_string[line_cur_s:line_cur_e]
                    file_data += (word + '\n')

                elif ch == '}':
                    # 若已置换行，需要先把当前行的内容输出
                    if new_line_flag == True:
                        word = line_string[line_cur_s:line_cur_e]
                        file_data += word
                    file_data += ('\n' + ch)
                    line_cur_s = line_cur_e = (line_cur_e + 1)

                elif ch == '/':
                    comment_flag = True
                    line_cur_e += 1
        return file_data

    def __rt_import(self, line):
        """
        处理import行
        :param line:
        :return:
        """
        print('import not support')
        sys.exit(-1)
        path = line.words[1].split("\"")[1]
        file_fms = FileFsm(path)
        file_fms.parse()

    def __rt_package(self, line):
        self.__pkg = line.words[1]

    def __rt_message(self, line):
        # 消息开始
        if "message" == line.words[0]:
            # 判断是否正在解析上一个消息
            if FileFsm.message_cache != None:
                raise FormatError("invalid syntax. line: " + str(line) + ". Parsing message have not finish")
            # 新建一个消息进行解析
            line.parse_message_new()
            FileFsm.message_cache = Message(message_name=line.words[1], message_pkg=self.__pkg, message_fields=[])
            # 处理缓存行
            for l in FileFsm.line_cache:
                if self.is_comment(l):
                    FileFsm.message_cache.add_comment(l[2:])
                else:
                    raise FormatError("invalid syntax. line" + str(l.line_number))
        # 消息结束
        elif "}" == line.words[0][0:1]:
            # 保存消息
            self.__message[FileFsm.message_cache.name()] = FileFsm.message_cache
            # 清空缓存
            FileFsm.message_cache = None
            FileFsm.line_cache.clear()
        # 消息开始
        elif '{' == line.words[0]:
            # do nothing
            return
        # 消息内容
        else:
            if line.words[0] not in FieldProperty:
                raise FormatError("invalid syntax. line:" + str(line))
            if None == FileFsm.message_cache:
                raise FormatError("invalid syntax. line:" + str(line))
            # 进一步解析行
            line.parse_message_element()
            # 向消息添加字段
            FileFsm.message_cache.add_field(Field(line.words[2], line.words[1], line.words[0], int(line.words[3]), "", line.words[4]))

    def __rt_comment(self, line):
        self.line_cache.append(line.words[0])

    def __rt_undefine(self, line):
        raise UndefineError('undefine line status: %s' % line)

    def __rt_empty(self, line):
        # do nothing
        return

    def __rt_other(self, line):
        raise UndefineError('unsupport format, line:%s' % line)

    def __rt_eof(self, line):
        print('end of file')

    def is_comment(self, line):
        return "//" == line[0:2]

if __name__ == '__main__':
    file_fsm = FileFsm(sys.argv[1])
    file_fsm.parse()
    print(file_fsm)
    # 获取Test1消息
    print(file_fsm.message_to_json('Test1'))

    # 根据json字符串构造对象
    test_string = {
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
        ]
    }
    msg = Message(json_string=json.dumps(test_string, ensure_ascii=False))
    pb_msg = msg.serialize()
    print(pb_msg)
    print(pb_msg.ByteSize())
    print(pb_msg.SerializeToString())


