from datetime import datetime

from PyVIDA.database import Mapped, Model, db, mapped_column


class EcuDescription(Model):
    __bind_key__ = "diag"
    __tablename__ = "EcuDescription"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    DisplayText: Mapped[str] = mapped_column(db.NVARCHAR(256))
    fkLanguage: Mapped[int] = mapped_column(db.ForeignKey("Language.Id"))
    fkEcu: Mapped[int] = mapped_column(db.ForeignKey("Ecu.Id"))


class ECU(Model):
    __bind_key__ = "diag"
    __tablename__ = "ECU"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)


class ECUInformationReference(Model):
    __bind_key__ = "diag"
    __tablename__ = "ECUInformationReference"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkIE: Mapped[str] = mapped_column(db.ForeignKey("IE.Id"))
    fkECU: Mapped[int] = mapped_column(db.ForeignKey("ECU.Id"))
    fkInformationQualifier: Mapped[int] = mapped_column(db.Integer)


class ScriptType(Model):
    __bind_key__ = "diag"
    __tablename__ = "ScriptType"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Description: Mapped[str] = mapped_column(db.String(50))


class IE(Model):
    __bind_key__ = "diag"
    __tablename__ = "IE"

    Id: Mapped[str] = mapped_column(db.String(16))
    VCCId: Mapped[str] = mapped_column(db.String(16))
    fkIEType: Mapped[int] = mapped_column(db.ForeignKey("IEType.id"))
    FirstTestgrpId: Mapped[str] = mapped_column(db.String(50), default="")
    fkInformationQualifier: Mapped[int] = mapped_column(
        db.ForeignKey("InformationQualifier.Id")
    )
    ProjectDocumentId: Mapped[str] = mapped_column(db.String(16))
    Version: Mapped[str] = mapped_column(db.String(10))


class IEParentChildMap(Model):
    __bind_key__ = "diag"
    __tablename__ = "IEParentChildMap"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkIEparent: Mapped[str] = mapped_column(db.ForeignKey("IEparent.id"))
    fkIEchild: Mapped[str] = mapped_column(db.ForeignKey("IEchild.id"))


class Script(Model):
    __bind_key__ = "diag"
    __tablename__ = "Script"

    Id: Mapped[str] = mapped_column(db.String, primary_key=True)
    fkScriptType: Mapped[int] = mapped_column(db.ForeignKey("ScriptType.Id"))


class IEProfileMap(Model):
    __bind_key__ = "diag"
    __tablename__ = "IEProfileMap"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkIE: Mapped[str] = mapped_column(db.ForeignKey("IE.Id"))
    fkProfile: Mapped[str] = mapped_column(db.ForeignKey("Profile.id"))


class IETitle(Model):
    __bind_key__ = "diag"
    __tablename__ = "IETitle"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkIE: Mapped[str] = mapped_column(db.ForeignKey("IE.Id"))
    fkLanguage: Mapped[int] = mapped_column(db.ForeignKey("Language.Id"))
    DisplayText: Mapped[str] = mapped_column(db.NVARCHAR(256))


class IEType(Model):
    __bind_key__ = "diag"
    __tablename__ = "IEType"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Name: Mapped[str] = mapped_column(db.String(64))


class Image(Model):
    __bind_key__ = "diag"
    __tablename__ = "Image"

    Id: Mapped[str] = mapped_column(db.String, primary_key=True)
    Path: Mapped[str] = mapped_column(db.String(255))
    Description: Mapped[str] = mapped_column(db.String(50))


class ImageProfileMap(Model):
    __bind_key__ = "diag"
    __tablename__ = "ImageProfileMap"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkImage: Mapped[str] = mapped_column(db.ForeignKey("Image.Id"))
    fkProfile: Mapped[str] = mapped_column(db.ForeignKey("Profile.id"))


class InformationQualifier(Model):
    __bind_key__ = "diag"
    __tablename__ = "InformationQualifier"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Name: Mapped[str] = mapped_column(db.String(64))
    fkInformationQualifier: Mapped[int] = mapped_column(
        db.ForeignKey("InformationQualifier.Id")
    )
    fkLanguage: Mapped[int] = mapped_column(db.ForeignKey("Language.Id"))
    DisplayText: Mapped[str] = mapped_column(db.NVARCHAR(256))


class Language(Model):
    __bind_key__ = "diag"
    __tablename__ = "Language"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Code: Mapped[str] = mapped_column(db.String(10))


class ScriptCarFunction(Model):
    __bind_key__ = "diag"
    __tablename__ = "ScriptCarFunction"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkScript: Mapped[str] = mapped_column(db.ForeignKey("Script.Id"))
    FunctionGroup: Mapped[int] = mapped_column(db.Integer)


class SWProductProfileMap(Model):
    __bind_key__ = "diag"
    __tablename__ = "SWProductProfileMap"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkSoftwareProduct: Mapped[int] = mapped_column(db.ForeignKey("SoftwareProduct.Id"))
    fkVehicleProfile: Mapped[str] = mapped_column(db.ForeignKey("VehicleProfile.id"))


class ScriptProfileMap(Model):
    __bind_key__ = "diag"
    __tablename__ = "ScriptProfileMap"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkScript: Mapped[str] = mapped_column(db.ForeignKey("Script.Id"))
    fkProfile: Mapped[str] = mapped_column(db.ForeignKey("Profile.id"))


class SoftwareProduct(Model):
    __bind_key__ = "diag"
    __tablename__ = "SoftwareProduct"

    Id: Mapped[int] = mapped_column(db.BigInteger)
    Name: Mapped[str] = mapped_column(db.String(64))
    PieId: Mapped[str] = mapped_column(db.String(30))
    EmissionRelated: Mapped[bool] = mapped_column(db.Boolean)


class SoftwareProductTitle(Model):
    __bind_key__ = "diag"
    __tablename__ = "SoftwareProductTitle"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkSoftwareProduct: Mapped[int] = mapped_column(db.ForeignKey("SoftwareProduct.Id"))
    fkLanguage: Mapped[int] = mapped_column(db.ForeignKey("Language.Id"))
    DisplayText: Mapped[str] = mapped_column(db.NVARCHAR(256))


class ScriptContent(Model):
    __bind_key__ = "diag"
    __tablename__ = "ScriptContent"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkScript: Mapped[str] = mapped_column(db.ForeignKey("Script.Id"))
    fkLanguage: Mapped[int] = mapped_column(db.ForeignKey("Language.Id"))
    DisplayText: Mapped[str] = mapped_column(db.NVARCHAR(256))
    XmlDataCompressed: Mapped[bytes] = mapped_column(db.BINARY(2147483647))
    checksum: Mapped[str] = mapped_column(db.NVARCHAR(256))


class DBContent(Model):
    __bind_key__ = "diag"
    __tablename__ = "DBContent"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Release: Mapped[str] = mapped_column(db.String(50))
    ScriptName: Mapped[str] = mapped_column(db.String(50))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class DBSchema(Model):
    __bind_key__ = "diag"
    __tablename__ = "DBSchema"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Version: Mapped[str] = mapped_column(db.String(50))
    Release: Mapped[str] = mapped_column(db.String(50))
    ObjVersion: Mapped[datetime] = mapped_column(db.DateTime)


class DBStageVersion(Model):
    __bind_key__ = "diag"
    __tablename__ = "DBStageVersion"

    ID: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    StageTag: Mapped[str] = mapped_column(db.String(30))
    StageDate: Mapped[datetime] = mapped_column(db.DateTime)


class IEGenericComponent(Model):
    __bind_key__ = "diag"
    __tablename__ = "IEGenericComponent"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkIE: Mapped[str] = mapped_column(db.ForeignKey("IE.Id"))
    GCID: Mapped[str] = mapped_column(db.String, primary_key=True)
    GLID: Mapped[str] = mapped_column(db.String, primary_key=True)


class dtproperties(Model):
    __bind_key__ = "diag"
    __tablename__ = "dtproperties"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    objectid: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    property: Mapped[str] = mapped_column(db.String(64))
    value: Mapped[str] = mapped_column(db.String(255))
    uvalue: Mapped[str] = mapped_column(db.NVARCHAR(256))
    lvalue: Mapped[bytes] = mapped_column(db.BINARY(2147483647))
    version: Mapped[int] = mapped_column(db.Integer, default=0)


class SoftwareProductNote(Model):
    __bind_key__ = "diag"
    __tablename__ = "SoftwareProductNote"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    NoteText: Mapped[str] = mapped_column(db.String(2000))
    fkSoftwareProduct: Mapped[int] = mapped_column(db.ForeignKey("SoftwareProduct.Id"))


class IECustomerFunction(Model):
    __bind_key__ = "diag"
    __tablename__ = "IECustomerFunction"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkIE: Mapped[str] = mapped_column(db.ForeignKey("IE.Id"))
    CF: Mapped[int] = mapped_column(db.Integer)


class SmartToolScript(Model):
    __bind_key__ = "diag"
    __tablename__ = "SmartToolScript"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    SmartToolId: Mapped[str] = mapped_column(db.String, primary_key=True)
    ScriptId: Mapped[str] = mapped_column(db.String, primary_key=True)
    SmartToolName: Mapped[str] = mapped_column(db.String(255))


class SymptomIEMap(Model):
    __bind_key__ = "diag"
    __tablename__ = "SymptomIEMap"

    Id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    fkSymptom: Mapped[int] = mapped_column(db.ForeignKey("Symptom.id"))
    fkIE: Mapped[str] = mapped_column(db.ForeignKey("IE.Id"))
    Type: Mapped[str] = mapped_column(db.String(1))
    fkProfile: Mapped[str] = mapped_column(db.ForeignKey("Profile.id"))
    CarFunction: Mapped[int] = mapped_column(db.Integer)
    DTCId: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    DTCComponentNameId: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    DFCId: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    DFSId: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Probability: Mapped[int] = mapped_column(db.Integer)
    Periods: Mapped[int] = mapped_column(db.Integer)
    Qualified: Mapped[bool] = mapped_column(db.Boolean)
    Order: Mapped[bool] = mapped_column(db.Boolean)


class ProfileDescription(Model):
    __bind_key__ = "diag"
    __tablename__ = "ProfileDescription"

    Id: Mapped[str] = mapped_column(db.String, primary_key=True)
    NavTitle: Mapped[str] = mapped_column(db.String(1309))


class DBVersion(Model):
    __bind_key__ = "diag"
    __tablename__ = "DBVersion"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Version: Mapped[str] = mapped_column(db.String(10), default="")
    VersionDate: Mapped[datetime] = mapped_column(db.DateTime)


class diagnostic_ImageWithProfile(Model):
    __bind_key__ = "diag"
    __tablename__ = "diagnostic_ImageWithProfile"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    Expr1: Mapped[str] = mapped_column(db.String(1))
    FullTitle: Mapped[str] = mapped_column(db.String(2337))


class ScriptVariant(Model):
    __bind_key__ = "diag"
    __tablename__ = "ScriptVariant"

    Id: Mapped[str] = mapped_column(db.String, primary_key=True)
    fkScript: Mapped[str] = mapped_column(db.ForeignKey("Script.Id"))
