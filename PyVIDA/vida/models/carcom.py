from datetime import datetime

from PyVIDA.database import Mapped, Model, db, mapped_column


class T143_BlockDataType(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T143_BlockDataType"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(200))


class T154_SymptomType(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T154_SymptomType"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT190_Text: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))


class T155_Scaling(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T155_Scaling"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    definition: Mapped[str] = mapped_column(db.String(254))
    type: Mapped[int] = mapped_column(db.Integer)


class T163_ProfileValueType(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T163_ProfileValueType"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(db.String(100))


class T172_SecurityCodeType(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T172_SecurityCodeType"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(db.String(200))
    description: Mapped[str] = mapped_column(db.String(250))


class T192_TextCategory(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T192_TextCategory"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(db.String(5))
    description: Mapped[str] = mapped_column(db.String(200))


class T193_Language(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T193_Language"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(db.String(200))
    description: Mapped[str] = mapped_column(db.String(80))


class T199_ControlTable(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T199_ControlTable"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    controlId: Mapped[str] = mapped_column(db.String(20))
    controlValue: Mapped[str] = mapped_column(db.String(200))
    controlDescription: Mapped[str] = mapped_column(db.String(200))
    modified: Mapped[datetime] = mapped_column(db.DateTime())
    modifiedBy: Mapped[str] = mapped_column(db.String(12))


class T101_Ecu(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T101_Ecu"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT102_EcuType: Mapped[int] = mapped_column(db.ForeignKey("T102_EcuType.id"))
    identifier: Mapped[str] = mapped_column(db.String(200))
    name: Mapped[str] = mapped_column(db.String(200))


class T111_Service(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T111_Service"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT122_Protocol: Mapped[int] = mapped_column(db.ForeignKey("T122_Protocol.id"))
    service: Mapped[str] = mapped_column(db.String(10))
    mode: Mapped[str] = mapped_column(db.String(10))
    serviceName: Mapped[str] = mapped_column(db.String(200))
    modeName: Mapped[str] = mapped_column(db.String(200))
    description: Mapped[str] = mapped_column(db.String(200))
    definition: Mapped[bytes] = mapped_column(db.BINARY(2147483647))
    type: Mapped[int] = mapped_column(db.Integer)
    status: Mapped[int] = mapped_column(db.Integer)
    fkt130_Init_Timing_Service_Default: Mapped[int] = mapped_column(db.ForeignKey("T130_Init.id"))


class T130_Init(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T130_Init"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT133_InitCategory: Mapped[int] = mapped_column(db.ForeignKey("T133_InitCategory.id"))


class T134_InitCategory_Type(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T134_InitCategory_Type"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT133_InitCategory: Mapped[int] = mapped_column(db.ForeignKey("T133_InitCategory.id"))
    fkT132_InitValueType: Mapped[int] = mapped_column(db.ForeignKey("T132_InitValueType.id"))


class T162_ProfileValue(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T162_ProfileValue"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(db.String(100))
    description: Mapped[str] = mapped_column(db.String(200))
    fkT163_ProfileValueType: Mapped[int] = mapped_column(
        db.ForeignKey("T163_ProfileValueType.id")
    )


class T171_SecurityCode(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T171_SecurityCode"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT172_SecurityCodeType: Mapped[int] = mapped_column(
        db.ForeignKey("T172_SecurityCodeType.id")
    )
    code: Mapped[str] = mapped_column(db.String(200))
    description: Mapped[str] = mapped_column(db.String(250))


class T190_Text(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T190_Text"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT192_TextCategory: Mapped[int] = mapped_column(db.ForeignKey("T192_TextCategory.id"))
    status: Mapped[int] = mapped_column(db.Integer)


class dtproperties(Model):
    __bind_key__ = "carcom"
    __tablename__ = "dtproperties"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    objectid: Mapped[int] = mapped_column(db.Integer)
    property: Mapped[str] = mapped_column(db.String(64))
    value: Mapped[str] = mapped_column(db.String(255))
    uvalue: Mapped[str] = mapped_column(db.NVARCHAR(255))
    lvalue: Mapped[list] = mapped_column(db.BINARY(2147483647))
    version: Mapped[int] = mapped_column(db.Integer, default=0)


class T100_EcuVariant(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T100_EcuVariant"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT101_Ecu: Mapped[int] = mapped_column(db.ForeignKey("T101_Ecu.id"))
    fkT101_Ecu_Gateway: Mapped[int] = mapped_column(db.ForeignKey("T101_Ecu.id"))
    identifier: Mapped[str] = mapped_column(db.String(200))
    status: Mapped[int] = mapped_column(db.Integer)
    inheritance: Mapped[str] = mapped_column(db.String(1))


class T123_Bus(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T123_Bus"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT124_Net: Mapped[int] = mapped_column(db.ForeignKey("T124_Net.id"))
    fkT190_Text: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    identifier: Mapped[int] = mapped_column(db.Integer)
    name: Mapped[str] = mapped_column(db.String(200))
    description: Mapped[str] = mapped_column(db.String(200))
    version: Mapped[int] = mapped_column(db.Integer)


class T131_InitValue(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T131_InitValue"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT130_Init: Mapped[int] = mapped_column(db.ForeignKey("T130_Init.id"))
    fkT132_InitValueType: Mapped[int] = mapped_column(db.ForeignKey("T132_InitValueType.id"))
    initValue: Mapped[str] = mapped_column(db.String(80))
    sortOrder: Mapped[int] = mapped_column(db.Integer)


class T141_Block(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T141_Block"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT142_BlockType: Mapped[int] = mapped_column(db.ForeignKey("T142_BlockType.id"))
    fkT143_BlockDataType: Mapped[int] = mapped_column(db.ForeignKey("T143_BlockDataType.id"))
    name: Mapped[str] = mapped_column(db.String(500))
    fkT190_Text: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    offset: Mapped[int] = mapped_column(db.Integer)
    length: Mapped[int] = mapped_column(db.Integer)
    exclude: Mapped[int] = mapped_column(db.Integer, default=0)
    composite: Mapped[bool] = mapped_column(db.Boolean)


class T156_SymptomSection(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T156_SymptomSection"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT190_Text: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))


class T161_Profile(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T161_Profile"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(db.String(100))
    folderLevel: Mapped[int] = mapped_column(db.Integer)
    description: Mapped[str] = mapped_column(db.String(500))
    title: Mapped[str] = mapped_column(db.String(500))
    fkT162_ProfileValue_Model: Mapped[int] = mapped_column(
        db.ForeignKey("T162_ProfileValue.id")
    )
    fkT162_ProfileValue_Year: Mapped[int] = mapped_column(
        db.ForeignKey("T162_ProfileValue.id")
    )
    fkT162_ProfileValue_Engine: Mapped[int] = mapped_column(
        db.ForeignKey("T162_ProfileValue.id")
    )
    fkT162_ProfileValue_Transmission: Mapped[int] = mapped_column(
        db.ForeignKey("T162_ProfileValue.id")
    )
    fkT162_ProfileValue_Body: Mapped[int] = mapped_column(
        db.ForeignKey("T162_ProfileValue.id")
    )
    fkT162_ProfileValue_Steering: Mapped[int] = mapped_column(
        db.ForeignKey("T162_ProfileValue.id")
    )
    fkT162_ProfileValue_Market: Mapped[int] = mapped_column(
        db.ForeignKey("T162_ProfileValue.id")
    )
    fkT162_ProfileValue_ControlUnit: Mapped[int] = mapped_column(
        db.ForeignKey("T162_ProfileValue.id")
    )
    fkT162_ProfileValue_ChassisFrom: Mapped[int] = mapped_column(
        db.ForeignKey("T162_ProfileValue.id")
    )
    fkT162_ProfileValue_ChassisTo: Mapped[int] = mapped_column(
        db.ForeignKey("T162_ProfileValue.id")
    )


class T191_TextData(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T191_TextData"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT193_Language: Mapped[int] = mapped_column(db.ForeignKey("T193_Language.id"))
    fkT190_Text: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    status: Mapped[int] = mapped_column(db.Integer)
    data: Mapped[str] = mapped_column(db.NVARCHAR(500))


class T194_FunctionGroup_1(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T194_FunctionGroup_1"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT190_Text: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))


class T103_EcuVariant_Project(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T103_EcuVariant_Project"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT100_EcuVariant: Mapped[int] = mapped_column(db.ForeignKey("T100_EcuVariant.id"))
    fkT104_Project: Mapped[int] = mapped_column(db.ForeignKey("T104_Project.id"))


class T110_Service_EcuVariant(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T110_Service_EcuVariant"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT111_Service: Mapped[int] = mapped_column(db.ForeignKey("T111_Service.id"))
    fkT100_EcuVariant: Mapped[int] = mapped_column(db.ForeignKey("T100_EcuVariant.id"))
    fkt130_Init_Timing_Service: Mapped[int] = mapped_column(db.ForeignKey("T130_Init.id"))


class T121_Config(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T121_Config"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT123_Bus: Mapped[int] = mapped_column(db.ForeignKey("T123_Bus.id"))
    fkT122_Protocol: Mapped[int] = mapped_column(db.ForeignKey("T122_Protocol.id"))
    fkT130_Init_Diag: Mapped[int] = mapped_column(db.ForeignKey("T130_Init.id"))
    fkT130_Init_Timing: Mapped[int] = mapped_column(db.ForeignKey("T130_Init.id"))
    physicalAddress: Mapped[str] = mapped_column(db.String(100))
    functionalAddress: Mapped[str] = mapped_column(db.String(100))
    canAddress: Mapped[str] = mapped_column(db.String(100))
    commAddress: Mapped[str] = mapped_column(db.String(100))
    priority: Mapped[int] = mapped_column(db.Integer)
    canIdTX: Mapped[str] = mapped_column(db.String(3))
    canIdRX: Mapped[str] = mapped_column(db.String(3))
    canIdFunc: Mapped[str] = mapped_column(db.String(7))
    canIdUUDT: Mapped[str] = mapped_column(db.String(508))
    busRate: Mapped[str] = mapped_column(db.String(10))
    addressSize: Mapped[str] = mapped_column(db.String(10))
    fkT121_Config_Gateway: Mapped[int] = mapped_column(db.ForeignKey("T121_Config.id"))


class T136_InitHw_Profile(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T136_InitHw_Profile"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT130_Init: Mapped[int] = mapped_column(db.ForeignKey("T130_Init.id"))
    fkT161_Profile: Mapped[int] = mapped_column(db.ForeignKey("T161_Profile.id"))


class T137_InitSwdl_Profile(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T137_InitSwdl_Profile"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT130_Init: Mapped[int] = mapped_column(db.ForeignKey("T130_Init.id"))
    fkT161_Profile: Mapped[int] = mapped_column(db.ForeignKey("T161_Profile.id"))
    ecuAddress: Mapped[str] = mapped_column(db.String(100))


class T144_BlockChild(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T144_BlockChild"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT100_EcuVariant: Mapped[int] = mapped_column(db.ForeignKey("T100_EcuVariant.id"))
    fkT141_Block_Child: Mapped[int] = mapped_column(db.ForeignKey("T141_Block.id"))
    fkT141_Block_Parent: Mapped[int] = mapped_column(db.ForeignKey("T141_Block.id"))
    SortOrder: Mapped[int] = mapped_column(db.Integer)


class T150_BlockValue(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T150_BlockValue"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT141_Block: Mapped[int] = mapped_column(db.ForeignKey("T141_Block.id"))
    SortOrder: Mapped[int] = mapped_column(db.Integer)
    CompareValue: Mapped[str] = mapped_column(db.String(50))
    Operator: Mapped[int] = mapped_column(db.Integer)
    fkT190_Text_Value: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    fkT190_Text_Unit: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    fkT155_Scaling: Mapped[int] = mapped_column(db.ForeignKey("T155_Scaling.id"))
    altDisplayValue: Mapped[str] = mapped_column(db.String(10))
    fkT190_Text_ppeValue: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    fkT190_Text_ppeUnit: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    fkT155_ppeScaling: Mapped[int] = mapped_column(db.ForeignKey("T155_Scaling.id"))


class T153_SymptomCategory(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T153_SymptomCategory"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT190_Text: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    fkT156_SymptomSection: Mapped[int] = mapped_column(
        db.ForeignKey("T156_SymptomSection.id")
    )
    fkT154_SymptomType: Mapped[int] = mapped_column(db.ForeignKey("T154_SymptomType.Id"))


class T160_DefaultEcuVariant(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T160_DefaultEcuVariant"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT161_Profile: Mapped[int] = mapped_column(db.ForeignKey("T161_Profile.id"))
    fkT100_EcuVariant: Mapped[int] = mapped_column(db.ForeignKey("T100_EcuVariant.id"))


class T170_SecurityCode_EcuVariant(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T170_SecurityCode_EcuVariant"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT171_SecurityCode: Mapped[int] = mapped_column(db.ForeignKey("T171_SecurityCode.id"))
    fkT100_EcuVariant: Mapped[int] = mapped_column(db.ForeignKey("T100_EcuVariant.id"))


class T196_FunctionGroup_2(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T196_FunctionGroup_2"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT194_FunctionGroup_1: Mapped[int] = mapped_column(
        db.ForeignKey("T194_FunctionGroup_1.id")
    )
    fkT190_Text: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))


class T120_Config_EcuVariant(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T120_Config_EcuVariant"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT121_Config: Mapped[int] = mapped_column(db.ForeignKey("T121_Config.id"))
    fkT100_EcuVariant: Mapped[int] = mapped_column(db.ForeignKey("T100_EcuVariant.id"))


class T152_Symptom(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T152_Symptom"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT153_SymptomCategory: Mapped[int] = mapped_column(
        db.ForeignKey("T153_SymptomCategory.id")
    )
    fkT190_Text: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    type: Mapped[str] = mapped_column(db.String(1))


class T158_Symptom_CSC(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T158_Symptom_CSC"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    CSC: Mapped[str] = mapped_column(db.String(2))
    status: Mapped[str] = mapped_column(db.String(10))
    fkT190_Text_SymptomType: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    fkT194_FunctionGroup_1: Mapped[int] = mapped_column(
        db.ForeignKey("T194_FunctionGroup_1.id")
    )
    fkT196_FunctionGroup_2: Mapped[int] = mapped_column(
        db.ForeignKey("T196_FunctionGroup_2.id")
    )
    fkT190_Text_CompFunc: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    fkT190_Text_Deviation: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    fkT190_Text_Condition_1: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    fkT190_Text_Condition_2: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    validFromDate: Mapped[datetime] = mapped_column(db.)


class T157_SymptomConnection(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T157_SymptomConnection"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT152_Symptom: Mapped[int] = mapped_column(db.ForeignKey("T152_Symptom.id"))
    fkT100_EcuVariant: Mapped[int] = mapped_column(db.ForeignKey("T100_EcuVariant.id"))


class T159_SymptomCSC_SymptomDTC(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T159_SymptomCSC_SymptomDTC"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT158_Symptom_CSC: Mapped[int] = mapped_column(db.ForeignKey("T158_Symptom_CSC.id"))
    fkT152_Symptom: Mapped[int] = mapped_column(db.ForeignKey("T152_Symptom.id"))


class T151_BlockValue_Symptom(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T151_BlockValue_Symptom"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT150_BlockValue: Mapped[int] = mapped_column(db.ForeignKey("T150_BlockValue.Id"))
    fkT157_SymptomConnection: Mapped[int] = mapped_column(
        db.ForeignKey("T157_SymptomConnection.id")
    )
    SortOrder: Mapped[int] = mapped_column(db.Integer)


class DBSchema(Model):
    __bind_key__ = "carcom"
    __tablename__ = "DBSchema"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Version: Mapped[str] = mapped_column(db.String(50))
    Release: Mapped[str] = mapped_column(db.String(50))
    ObjVersion: Mapped[datetime] = mapped_column(db.)


class DBContent(Model):
    __bind_key__ = "carcom"
    __tablename__ = "DBContent"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Release: Mapped[str] = mapped_column(db.String(50))
    ScriptName: Mapped[str] = mapped_column(db.String(50))
    ObjVersion: Mapped[datetime] = mapped_column(db.)


class T148_BlockMetaPARA(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T148_BlockMetaPARA"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT141_Block: Mapped[int] = mapped_column(db.ForeignKey("T141_Block.id"))
    fkT100_EcuVariant: Mapped[int] = mapped_column(db.ForeignKey("T100_EcuVariant.id"))
    asMinRange: Mapped[float] = mapped_column(db.DECIMAL, default=30)
    asMaxRange: Mapped[float] = mapped_column(db.DECIMAL, default=30)
    showAsFreezeFrame: Mapped[bool] = mapped_column(db.Boolean)


class DBStageVersion(Model):
    __bind_key__ = "carcom"
    __tablename__ = "DBStageVersion"

    ID: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    StageTag: Mapped[str] = mapped_column(db.String(30))
    StageDate: Mapped[datetime] = mapped_column(db.)


class T102_EcuType(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T102_EcuType"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    identifier: Mapped[int] = mapped_column(db.Integer)
    fkt190_Text: Mapped[int] = mapped_column(db.ForeignKey("T190_Text.id"))
    description: Mapped[str] = mapped_column(db.String(100))


class T104_Project(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T104_Project"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(200))
    modelYear: Mapped[int] = mapped_column(db.Integer)
    startOfProd: Mapped[str] = mapped_column(db.String(10))
    serie: Mapped[str] = mapped_column(db.String(50))
    isProdData: Mapped[bool] = mapped_column(db.Boolean)
    prodDataFrom: Mapped[datetime] = mapped_column(db.)


class T122_Protocol(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T122_Protocol"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(db.String(200))
    version: Mapped[int] = mapped_column(db.Integer)
    description: Mapped[str] = mapped_column(db.String(200))


class T124_Net(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T124_Net"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    identifier: Mapped[str] = mapped_column(db.String(200))
    name: Mapped[str] = mapped_column(db.String(200))


class T132_InitValueType(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T132_InitValueType"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(200))


class T133_InitCategory(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T133_InitCategory"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(200))


class T142_BlockType(Model):
    __bind_key__ = "carcom"
    __tablename__ = "T142_BlockType"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkT142_BlockType_Parent: Mapped[int] = mapped_column(db.ForeignKey("T142_BlockType.id"))
    identifier: Mapped[str] = mapped_column(db.String(200))
    metaTable: Mapped[str] = mapped_column(db.String(200))
