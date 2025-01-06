from datetime import datetime

from PyVIDA.database import Mapped, Model, db, mapped_column


class VINDecodeVariant(Model):
    __bind_key__ = "basedata"
    __tablename__ = "VINDecodeVariant"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    VinStartPos: Mapped[int] = mapped_column(db.SmallInteger)
    VinEndPos: Mapped[int] = mapped_column(db.SmallInteger)
    VinCompare: Mapped[str] = mapped_column(db.String(8))
    fkVehicleModel: Mapped[int] = mapped_column(db.ForeignKey("VehicleModel.Id"))
    fkModelYear: Mapped[int] = mapped_column(db.ForeignKey("ModelYear.Id"))
    fkPartnerGroup: Mapped[int] = mapped_column(db.ForeignKey("PartnerGroup.Id"))
    fkEngine: Mapped[int] = mapped_column(db.ForeignKey("Engine.Id"))
    fkTransmission: Mapped[int] = mapped_column(db.ForeignKey("Transmission.Id"))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class VehicleModel(Model):
    __bind_key__ = "basedata"
    __tablename__ = "VehicleModel"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[int] = mapped_column(db.Integer)
    Description: Mapped[str] = mapped_column(db.String(255))
    ImagePath: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class VINVariantCodes(Model):
    __bind_key__ = "basedata"
    __tablename__ = "VINVariantCodes"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    VINVariantCode: Mapped[str] = mapped_column(db.String(8))
    fkEngine: Mapped[int] = mapped_column(db.ForeignKey("Engine.Id"))
    fkBodyStyle: Mapped[int] = mapped_column(db.ForeignKey("BodyStyle.Id"))
    fkTransmission: Mapped[int] = mapped_column(db.ForeignKey("Transmission.Id"))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class VehicleProfilePartnerGroup(Model):
    __bind_key__ = "basedata"
    __tablename__ = "VehicleProfilePartnerGroup"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkVehicleProfile: Mapped[str] = mapped_column(db.ForeignKey("VehicleProfile.Id"))
    PartnerGroupCID: Mapped[str] = mapped_column(db.String(10))


class SpecialVehicle(Model):
    __bind_key__ = "basedata"
    __tablename__ = "SpecialVehicle"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[int] = mapped_column(db.Integer)
    Description: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class VehicleProfileDescriptions(Model):
    __bind_key__ = "basedata"
    __tablename__ = "VehicleProfileDescriptions"

    Id: Mapped[str] = mapped_column(db.String(1), primary_key=True)
    FullTitle: Mapped[str] = mapped_column(db.String(2337))
    NavTitle: Mapped[str] = mapped_column(db.String(1823))
    VehicleModelDesc: Mapped[str] = mapped_column(db.String(255))
    ModelYearDesc: Mapped[str] = mapped_column(db.String(255))
    EngineDesc: Mapped[str] = mapped_column(db.String(255))
    TransmissionDesc: Mapped[str] = mapped_column(db.String(255))
    BodyStyleDesc: Mapped[str] = mapped_column(db.String(255))
    SteeringDesc: Mapped[str] = mapped_column(db.String(255))
    PartnerGroupDesc: Mapped[str] = mapped_column(db.String(255))
    BrakesSystemDesc: Mapped[str] = mapped_column(db.String(255))
    StructureWeekDesc: Mapped[str] = mapped_column(db.String(255))
    SpecialVehicleDesc: Mapped[str] = mapped_column(db.String(255))
    ChassiNoFrom: Mapped[int] = mapped_column(db.Integer)
    ChassiNoTo: Mapped[int] = mapped_column(db.Integer)


class VehicleProfile(Model):
    __bind_key__ = "basedata"
    __tablename__ = "VehicleProfile"

    Id: Mapped[str] = mapped_column(db.String(1), primary_key=True)
    FolderLevel: Mapped[int] = mapped_column(db.SmallInteger)
    Description: Mapped[str] = mapped_column(db.String(255))
    Title: Mapped[str] = mapped_column(db.String(255))
    ChassisNoFrom: Mapped[int] = mapped_column(db.Integer)
    ChassisNoTo: Mapped[int] = mapped_column(db.Integer)
    fkNodeECU: Mapped[int] = mapped_column(db.ForeignKey("NodeECU.Id"))
    fkVehicleModel: Mapped[int] = mapped_column(db.ForeignKey("VehicleModel.Id"))
    fkBodyStyle: Mapped[int] = mapped_column(db.ForeignKey("BodyStyle.Id"))
    fkSteering: Mapped[int] = mapped_column(db.ForeignKey("Steering.Id"))
    fkTransmission: Mapped[int] = mapped_column(db.ForeignKey("Transmission.Id"))
    fkSuspension: Mapped[int] = mapped_column(db.ForeignKey("Suspension.Id"))
    fkEngine: Mapped[int] = mapped_column(db.ForeignKey("Engine.Id"))
    fkStructureWeek: Mapped[int] = mapped_column(db.ForeignKey("StructureWeek.Id"))
    fkBrakeSystem: Mapped[int] = mapped_column(db.ForeignKey("BrakeSystem.Id"))
    fkPartnerGroup: Mapped[int] = mapped_column(db.ForeignKey("PartnerGroup.Id"))
    fkModelYear: Mapped[int] = mapped_column(db.ForeignKey("ModelYear.Id"))
    fkSpecialVehicle: Mapped[int] = mapped_column(db.ForeignKey("SpecialVehicle.Id"))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class SelectedProfiles(Model):
    __bind_key__ = "basedata"
    __tablename__ = "SelectedProfiles"

    ID: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    SelectedProfiles: Mapped[str] = mapped_column(db.String(255))


class ValidProfiles(Model):
    __bind_key__ = "basedata"
    __tablename__ = "ValidProfiles"

    ID: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    ValidProfile: Mapped[str] = mapped_column(db.String(255))


class dtproperties(Model):
    __bind_key__ = "basedata"
    __tablename__ = "dtproperties"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    objectid: Mapped[int] = mapped_column(db.Integer)
    property: Mapped[str] = mapped_column(db.String(64))
    value: Mapped[str] = mapped_column(db.String(255))
    uvalue: Mapped[str] = mapped_column(db.NVARCHAR(255))
    lvalue: Mapped[bytes] = mapped_column(db.BINARY(2147483647))
    version: Mapped[int] = mapped_column(db.Integer, default=0)


class DBContent(Model):
    __bind_key__ = "basedata"
    __tablename__ = "DBContent"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Release: Mapped[str] = mapped_column(db.String(50))
    ScriptName: Mapped[str] = mapped_column(db.String(50))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class DBSchema(Model):
    __bind_key__ = "basedata"
    __tablename__ = "DBSchema"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Version: Mapped[str] = mapped_column(db.String(50))
    Release: Mapped[str] = mapped_column(db.String(50))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class AMYProfileMap(Model):
    __bind_key__ = "basedata"
    __tablename__ = "AMYProfileMap"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkSourceProfile: Mapped[str] = mapped_column(db.ForeignKey("VehicleProfile.Id"))
    fkTargetProfile: Mapped[str] = mapped_column(db.ForeignKey("VehicleProfile.Id"))


class DBStageVersion(Model):
    __bind_key__ = "basedata"
    __tablename__ = "DBStageVersion"

    ID: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    StageTag: Mapped[str] = mapped_column(db.String(30))
    StageDate: Mapped[datetime] = mapped_column(db.DateTime)


class BodyStyle(Model):
    __bind_key__ = "basedata"
    __tablename__ = "BodyStyle"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[int] = mapped_column(db.Integer)
    Description: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class BrakeSystem(Model):
    __bind_key__ = "basedata"
    __tablename__ = "BrakeSystem"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[int] = mapped_column(db.Integer)
    Description: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class Engine(Model):
    __bind_key__ = "basedata"
    __tablename__ = "Engine"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[int] = mapped_column(db.Integer)
    Description: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class ModelYear(Model):
    __bind_key__ = "basedata"
    __tablename__ = "ModelYear"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[int] = mapped_column(db.Integer)
    Description: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class StructureWeek(Model):
    __bind_key__ = "basedata"
    __tablename__ = "StructureWeek"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[str] = mapped_column(db.String(50))
    Description: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class NodeECU(Model):
    __bind_key__ = "basedata"
    __tablename__ = "NodeECU"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[int] = mapped_column(db.Integer)
    Description: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class PartnerGroup(Model):
    __bind_key__ = "basedata"
    __tablename__ = "PartnerGroup"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[str] = mapped_column(db.String(10))
    Description: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class Steering(Model):
    __bind_key__ = "basedata"
    __tablename__ = "Steering"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[int] = mapped_column(db.Integer)
    Description: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class Suspension(Model):
    __bind_key__ = "basedata"
    __tablename__ = "Suspension"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[int] = mapped_column(db.Integer)
    Description: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class Transmission(Model):
    __bind_key__ = "basedata"
    __tablename__ = "Transmission"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Cid: Mapped[int] = mapped_column(db.Integer)
    Description: Mapped[str] = mapped_column(db.String(255))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class VINDecodeModel(Model):
    __bind_key__ = "basedata"
    __tablename__ = "VINDecodeModel"

    ID: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    VinStartPos: Mapped[int] = mapped_column(db.SmallInteger)
    VinEndPos: Mapped[int] = mapped_column(db.SmallInteger)
    VinCompare: Mapped[str] = mapped_column(db.String(8))
    fkVehicleModel: Mapped[int] = mapped_column(db.ForeignKey("VehicleModel.Id"))
    fkModelYear: Mapped[int] = mapped_column(db.ForeignKey("ModelYear.Id"))
    fkBodyStyle: Mapped[int] = mapped_column(db.ForeignKey("BodyStyle.Id"))
    fkPartnerGroup: Mapped[int] = mapped_column(db.ForeignKey("PartnerGroup.Id"))
    ChassisNoFrom: Mapped[int] = mapped_column(db.Integer)
    ChassisNoTo: Mapped[int] = mapped_column(db.Integer)
    YearCodePos: Mapped[int] = mapped_column(db.SmallInteger)
    YearCode: Mapped[str] = mapped_column(db.String(1))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)
