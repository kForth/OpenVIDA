class ProfileViewModel extends VidaBaseModel {
    constructor() {
        super();
        var self = this;

        self.imagePath = ko.observable("");
        self.vinNumber = ko.observable("");
        self.partnerGroup = ko.observable(null);
        self.vehicleModel = ko.observable(null);
        self.modelYear = ko.observable(null);
        self.engine = ko.observable(null);
        self.transmission = ko.observable(null);
        self.steering = ko.observable(null);
        self.bodyStyle = ko.observable(null);
        self.specialVehicle = ko.observable(null);

        self.partnerGroupOptions = ko.observableArray([]);
        self.vehicleModelOptions = ko.observableArray([{ id: null, text: "" }]);
        self.modelYearOptions = ko.observableArray([{ id: null, text: "" }]);
        self.engineOptions = ko.observableArray([{ id: null, text: "" }]);
        self.transmissionOptions = ko.observableArray([{ id: null, text: "" }]);
        self.steeringOptions = ko.observableArray([{ id: null, text: "" }]);
        self.bodyStyleOptions = ko.observableArray([{ id: null, text: "" }]);
        self.specialVehicleOptions = ko.observableArray([
            { id: null, text: "" },
        ]);

        self.pushAll = function (arr1, arr2) {
            for (let e of arr2) {
                arr1.push(e);
            }
        };
        $.get("/Vida/partnerGroups", (resp) =>
            self.pushAll(self.partnerGroupOptions, resp)
        );
        $.get("/Vida/vehicleModels", (resp) =>
            self.pushAll(self.vehicleModelOptions, resp)
        );
        $.get("/Vida/modelYears", (resp) =>
            self.pushAll(self.modelYearOptions, resp)
        );
        $.get("/Vida/engines", (resp) =>
            self.pushAll(self.engineOptions, resp)
        );
        $.get("/Vida/transmissions", (resp) =>
            self.pushAll(self.transmissionOptions, resp)
        );
        $.get("/Vida/steerings", (resp) =>
            self.pushAll(self.steeringOptions, resp)
        );
        $.get("/Vida/bodyStyles", (resp) =>
            self.pushAll(self.bodyStyleOptions, resp)
        );
        $.get("/Vida/specialVehicles", (resp) =>
            self.pushAll(self.specialVehicleOptions, resp)
        );

        self.vinNumber.subscribe(function () {
            var match = self
                .vinNumber()
                .match(
                    /^[\d\w][\d\w][\d\w][\d\w][\d\w][\d\w][\d\w][\d\w][\d\w][\d\w][\d\w](\d{6})$/
                );
            $("#vin").toggleClass(
                "is-invalid",
                !match && self.vinNumber().length > 0
            );
        });

        self.loadProfileFromVin = function () {
            $.ajax({
                url: "/Vida/decode_vin/",
                contentType: "application/x-www-form-urlencoded; charset=UTF-8",
                data: {
                    vinNumber: self.vinNumber(),
                    partnerGroup: self.partnerGroup(),
                },
                success: (resp) => {
                    self.imagePath(`/Vida/DataImages/${resp.image}`);

                    self.modelYear(
                        resp.year ||
                            self
                                .modelYearOptions()
                                .find((e) => e.id == resp.year).id
                    );
                    self.vehicleModel(
                        resp.model ||
                            self
                                .vehicleModelOptions()
                                .find((e) => e.id == resp.model).id
                    );
                    self.transmission(
                        resp.transmission ||
                            self
                                .transmissionOptions()
                                .find((e) => e.id == resp.transmission).id
                    );
                    self.engine(
                        resp.engine ||
                            self
                                .engineOptions()
                                .find((e) => e.id == resp.engine).id
                    );
                    self.bodyStyle(
                        resp.body ||
                            self
                                .bodyStyleOptions()
                                .find((e) => e.id == resp.body).id
                    );
                    self.submitProfile();
                },
            });
        };

        self.clearProfile = function () {
            self.partnerGroup("");
            self.vehicleModel("");
            self.modelYear("");
            self.engine("");
            self.transmission("");
            self.steering("");
            self.bodyStyle("");
            self.specialVehicle("");
        };

        self.submitProfile = function () {
            let data = {
                fkPartnerGroup: self.partnerGroup(),
                fkVehicleModel: self.vehicleModel(),
                fkModelYear: self.modelYear(),
                fkEngine: self.engine(),
                fkTransmission: self.transmission(),
                fkSteering: self.steering(),
                fkBodyStyle: self.bodyStyle(),
                fkSpecialVehicle: self.specialVehicle(),
            };
            $.ajax({
                url: "/Vida/profile",
                data: data,
                success: (resp) => self.selectedProfile(resp.Id),
            });
        };

        self.profileInfo.subscribe(() => {
            if (self.profileInfo()) {
                self.partnerGroup(self.profileInfo().fkPartnerGroup);
                self.vehicleModel(self.profileInfo().fkVehicleModel);
                self.modelYear(self.profileInfo().fkModelYear);
                self.engine(self.profileInfo().fkEngine);
                self.transmission(self.profileInfo().fkTransmission);
                self.steering(self.profileInfo().fkSteering);
                self.bodyStyle(self.profileInfo().fkBodyStyle);
                self.specialVehicle(self.profileInfo().fkSpecialVehicle);
            }
        });
    }
}

ko.applyBindings(new ProfileViewModel());

// Show autocomplete options on focus
$(".ui-autocomplete-input").on("focus", (e1) => {
    if (!$(e1.currentTarget).val())
        $(e1.currentTarget).autocomplete("search", "");
});
