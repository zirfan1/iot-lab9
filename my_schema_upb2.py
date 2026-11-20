# Muhammad Zaid Irfan C22499352
# Lut Dunne C23470466
# Amar Jagana c22423526
# Ephraim Kuedituka C23504716
# Mohammad Mujahed C23502209


from uprotobuf import *


@registerMessage
class TimeMessage(Message):
    _proto_fields=[
        dict(name='hour', type=WireType.Varint, subType=VarintSubType.UInt32, fieldType=FieldType.Required, id=1),
        dict(name='minute', type=WireType.Varint, subType=VarintSubType.UInt32, fieldType=FieldType.Required, id=2),
        dict(name='second', type=WireType.Varint, subType=VarintSubType.UInt32, fieldType=FieldType.Required, id=3),
    ]

@registerMessage
class TemperaturemessageMessage(Message):
    _proto_fields=[
        dict(name='publisher_id', type=WireType.Length, subType=LengthSubType.String, fieldType=FieldType.Required, id=1),
        dict(name='temperature', type=WireType.Bit32, subType=FixedSubType.Float, fieldType=FieldType.Required, id=2),
        dict(name='epoch', type=WireType.Varint, subType=VarintSubType.UInt64, fieldType=FieldType.Required, id=3),
    ]